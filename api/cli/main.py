"""CLI main application using Typer."""

import asyncio
import logging
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from core.application.use_cases.generate_content import GenerateContentUseCase
from core.application.dto.content_request import ContentGenerationRequest
from core.domain.entities.content import ContentType, ContentFormat
from core.domain.value_objects.provider_config import ProviderConfig, LLMProvider
from core.domain.value_objects.generation_params import GenerationParams
from core.infrastructure.repositories.file_content_repository import (
    FileContentRepository,
)
from core.infrastructure.repositories.yaml_agent_repository import YamlAgentRepository
from core.infrastructure.repositories.file_workflow_repository import (
    FileWorkflowRepository,
)
from core.infrastructure.factories.provider_factory import LLMProviderFactory
from core.infrastructure.config.settings import get_settings
from .tracking import app as tracking_app

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise in CLI
logger = logging.getLogger(__name__)

# Create Typer app
app = typer.Typer(
    name="cgsref",
    help="CGSRef - Clean Content Generation System CLI",
    add_completion=False,
)

# Rich console for pretty output
console = Console()

# Register sub-commands
app.add_typer(tracking_app, name="tracking", help="Workflow tracking commands")


def get_use_case(provider: LLMProvider, model: str) -> GenerateContentUseCase:
    """Get configured use case instance."""
    settings = get_settings()

    content_repo = FileContentRepository(settings.output_dir)
    agent_repo = YamlAgentRepository(settings.profiles_dir)
    workflow_repo = FileWorkflowRepository(settings.workflows_dir)

    llm_provider = LLMProviderFactory.create_provider(provider, settings)
    provider_config = ProviderConfig(
        provider=provider,
        model=model,
        api_key=settings.get_provider_api_key(provider.value),
    )

    return GenerateContentUseCase(
        content_repository=content_repo,
        workflow_repository=workflow_repo,
        agent_repository=agent_repo,
        llm_provider=llm_provider,
        provider_config=provider_config,
        rag_service=None,
        serper_api_key=settings.serper_api_key,
    )


@app.command()
def generate(
    topic: str = typer.Argument(..., help="Topic for content generation"),
    content_type: str = typer.Option(
        "article", "--type", "-t", help="Content type (article, newsletter, blog_post)"
    ),
    content_format: str = typer.Option(
        "markdown", "--format", "-f", help="Output format (markdown, html, plain_text)"
    ),
    provider: str = typer.Option(
        "openai", "--provider", "-p", help="AI provider (openai, anthropic, deepseek)"
    ),
    model: str = typer.Option("gpt-4o", "--model", "-m", help="Model name"),
    temperature: float = typer.Option(
        0.7, "--temperature", help="Generation temperature (0.0-2.0)"
    ),
    client_profile: Optional[str] = typer.Option(
        None, "--client", "-c", help="Client profile name"
    ),
    workflow_type: Optional[str] = typer.Option(
        None, "--workflow", "-w", help="Workflow type"
    ),
    target_words: Optional[int] = typer.Option(
        None, "--words", help="Target word count"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Generate content using the specified parameters."""

    if verbose:
        logging.getLogger().setLevel(logging.INFO)

    try:
        # Validate inputs
        try:
            content_type_enum = ContentType(content_type)
            content_format_enum = ContentFormat(content_format)
            provider_enum = LLMProvider(provider)
        except ValueError as e:
            console.print(f"[red]Error: Invalid parameter - {e}[/red]")
            raise typer.Exit(1)

        # Create configuration
        provider_config = ProviderConfig(
            provider=provider_enum, model=model, temperature=temperature
        )

        generation_params = GenerationParams(
            topic=topic,
            content_type=content_type_enum,
            content_format=content_format_enum,
            target_word_count=target_words,
        )

        request = ContentGenerationRequest(
            topic=topic,
            content_type=content_type_enum,
            content_format=content_format_enum,
            client_profile=client_profile,
            workflow_type=workflow_type,
            provider_config=provider_config,
            generation_params=generation_params,
        )

        # Show generation info
        console.print(
            Panel.fit(
                f"[bold]Generating {content_type} about:[/bold] {topic}\n"
                f"[dim]Provider:[/dim] {provider} ({model})\n"
                f"[dim]Format:[/dim] {content_format}\n"
                f"[dim]Client:[/dim] {client_profile or 'default'}",
                title="Content Generation",
                border_style="blue",
            )
        )

        # Execute generation with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating content...", total=None)

            use_case = get_use_case(provider_enum, model)
            response = asyncio.run(use_case.execute(request))

        if response.success:
            # Show success message
            console.print(f"[green]✓[/green] Content generated successfully!")
            console.print(f"[dim]Content ID:[/dim] {response.content_id}")
            console.print(f"[dim]Word count:[/dim] {response.word_count}")
            console.print(
                f"[dim]Generation time:[/dim] {response.generation_time_seconds:.2f}s"
            )

            # Save to file if specified
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(response.body, encoding="utf-8")
                console.print(f"[green]✓[/green] Saved to: {output_path}")
            else:
                # Display content
                console.print("\n" + "=" * 50)
                console.print(response.body)
                console.print("=" * 50)
        else:
            console.print(f"[red]✗[/red] Generation failed: {response.error_message}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def list_content(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of items to show"),
    content_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Filter by content type"
    ),
    client_profile: Optional[str] = typer.Option(
        None, "--client", "-c", help="Filter by client profile"
    ),
):
    """List generated content."""
    try:
        settings = get_settings()
        default_provider = LLMProvider(settings.default_provider)
        use_case = get_use_case(default_provider, settings.default_model)
        # This would need to be implemented in the use case
        console.print("[yellow]Content listing not yet implemented[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def config():
    """Show current configuration."""
    settings = get_settings()

    table = Table(title="CGSRef Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Environment", settings.environment)
    table.add_row("Data Directory", settings.data_dir)
    table.add_row("Output Directory", settings.output_dir)
    table.add_row("Default Provider", settings.default_provider)
    table.add_row("Default Model", settings.default_model)

    # Show available providers
    providers = settings.get_available_providers()
    for provider, available in providers.items():
        status = "✓ Available" if available else "✗ Not configured"
        table.add_row(f"{provider.title()} API", status)

    console.print(table)


@app.command()
def version():
    """Show version information."""
    console.print("CGSRef CLI v1.0.0")
    console.print("Clean Content Generation System")


if __name__ == "__main__":
    app()
