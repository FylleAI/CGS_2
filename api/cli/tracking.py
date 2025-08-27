"""CLI per visualizzare tracking data su Supabase (opzionale).

Comandi:
- history: lista run recenti
- details: dettagli di una run specifica
- stats: statistiche aggregate
"""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

from core.infrastructure.database.supabase_tracker import get_tracker

app = typer.Typer(help="CGSRef Tracking Commands")
console = Console()


@app.command("history")
def show_history(
    client: str = typer.Option(None, "--client", "-c", help="Filter by client"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of runs to show"),
):
    tracker = get_tracker()
    if not tracker:
        console.print("[red]❌ Tracking not available[/red]")
        raise typer.Exit(code=1)

    runs = tracker.get_run_history(client_name=client, limit=limit)
    if not runs:
        console.print("[yellow]No runs found[/yellow]")
        return

    table = Table(title=f"Workflow Run History{' - ' + client if client else ''}")
    table.add_column("ID", style="cyan", width=8)
    table.add_column("Client", style="green")
    table.add_column("Workflow", style="blue")
    table.add_column("Topic", style="white", width=30)
    table.add_column("Status", style="bold")
    table.add_column("Started", style="dim")
    table.add_column("Duration", style="magenta")
    table.add_column("Cost", style="yellow")

    for run in runs:
        status = run.get("status", "-")
        status_style = {
            "completed": "[green]✅ Completed[/green]",
            "failed": "[red]❌ Failed[/red]",
            "running": "[yellow]🔄 Running[/yellow]",
        }.get(status, status)

        started_raw = run.get("started_at") or run.get("created_at")
        if started_raw:
            try:
                started = datetime.fromisoformat(str(started_raw).replace("Z", "+00:00"))
                started_str = started.strftime("%m/%d %H:%M")
            except Exception:
                started_str = str(started_raw)
        else:
            started_str = "-"

        duration = run.get("duration_seconds")
        duration_str = f"{duration}s" if duration else "-"
        cost = run.get("total_cost_usd")
        cost_str = f"${cost:.4f}" if cost else "-"

        topic = run.get("topic", "-")
        short_topic = topic[:30] + "..." if len(topic) > 30 else topic

        table.add_row(
            str(run.get("id", "-") )[:8],
            str(run.get("client_name", "-")),
            str(run.get("workflow_name", "-")),
            short_topic,
            status_style,
            started_str,
            duration_str,
            cost_str,
        )

    console.print(table)


@app.command("details")
def show_details(run_id: str):
    tracker = get_tracker()
    if not tracker:
        console.print("[red]❌ Tracking not available[/red]")
        raise typer.Exit(code=1)

    details = tracker.get_run_details(run_id)
    if not details:
        console.print(f"[red]❌ Run {run_id} not found[/red]")
        raise typer.Exit(code=1)

    run = details["run"]
    agents = details["agents"]
    logs = details["logs"]

    run_info = f"""
[bold]Client:[/bold] {run.get('client_name','-')}
[bold]Workflow:[/bold] {run.get('workflow_name','-')}
[bold]Topic:[/bold] {run.get('topic','-')}
[bold]Status:[/bold] {run.get('status','-')}
[bold]Started:[/bold] {run.get('started_at','-')}
[bold]Duration:[/bold] {run.get('duration_seconds','-')}s
[bold]Cost:[/bold] ${run.get('total_cost_usd',0) or 0:.4f}
[bold]Tokens:[/bold] {run.get('total_tokens','-')}
"""
    if run.get("error_message"):
        run_info += f"\n[bold red]Error:[/bold red] {run.get('error_message')}"

    console.print(Panel(run_info, title=f"Run Details - {str(run.get('id',''))[:8]}", border_style="blue"))

    if agents:
        table = Table(title="Agent Executions")
        table.add_column("Step", style="cyan")
        table.add_column("Agent", style="green")
        table.add_column("Status", style="bold")
        table.add_column("Duration", style="magenta")
        table.add_column("Tokens", style="yellow")
        table.add_column("Thoughts", style="white", width=40)
        for a in agents:
            thoughts = a.get("thoughts") or ""
            if len(thoughts) > 40:
                thoughts = thoughts[:37] + "..."
            table.add_row(
                str(a.get("step_number", "-")),
                str(a.get("agent_name", "-")),
                str(a.get("status", "-")),
                f"{a.get('duration_seconds') or '-'}s",
                str(a.get("tokens_used") or "-"),
                thoughts,
            )
        console.print(table)

    if logs:
        console.print(f"\n[bold]Recent Logs ({len(logs)} total):[/bold]")
        for log in logs[-10:]:
            ts_raw = log.get("timestamp") or log.get("created_at")
            try:
                ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
                ts_str = ts.strftime("%H:%M:%S")
            except Exception:
                ts_str = str(ts_raw)
            level = log.get("level", "INFO")
            level_style = {
                "ERROR": "[red]ERROR[/red]",
                "WARNING": "[yellow]WARN[/yellow]",
                "INFO": "[blue]INFO[/blue]",
                "DEBUG": "[dim]DEBUG[/dim]",
            }.get(level, level)
            agent_str = f"[{log.get('agent_name')}] " if log.get("agent_name") else ""
            console.print(f"  {ts_str} {level_style} {agent_str}{log.get('message','')}")


@app.command("stats")
def show_stats(
    client: str = typer.Option(None, "--client", "-c", help="Filter by client"),
    days: int = typer.Option(7, "--days", "-d", help="Days window (not enforced here, filtered client-side)"),
):
    tracker = get_tracker()
    if not tracker:
        console.print("[red]❌ Tracking not available[/red]")
        raise typer.Exit(code=1)

    runs = tracker.get_run_history(client_name=client, limit=1000)
    if not runs:
        console.print("[yellow]No runs found[/yellow]")
        return

    total_runs = len(runs)
    completed = len([r for r in runs if r.get("status") == "completed"])
    failed = len([r for r in runs if r.get("status") == "failed"])
    running = len([r for r in runs if r.get("status") == "running"])
    total_cost = sum(r.get("total_cost_usd") or 0 for r in runs)
    total_tokens = sum(r.get("total_tokens") or 0 for r in runs)
    durs = [r.get("duration_seconds") for r in runs if r.get("duration_seconds")]
    avg_duration = sum(durs) / max(1, len(durs))

    stats_text = f"""
[bold]Total Runs:[/bold] {total_runs}
[bold]Completed:[/bold] [green]{completed}[/green]
[bold]Failed:[/bold] [red]{failed}[/red]
[bold]Running:[/bold] [yellow]{running}[/yellow]
[bold]Success Rate:[/bold] {(completed/max(1,total_runs)*100):.1f}%

[bold]Total Cost:[/bold] ${total_cost:.4f}
[bold]Total Tokens:[/bold] {total_tokens}
[bold]Avg Duration:[/bold] {avg_duration:.1f}s
"""
    console.print(Panel(stats_text, title=f"Statistics{' - ' + client if client else ''}", border_style="green"))


if __name__ == "__main__":
    app()

