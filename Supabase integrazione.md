ISTRUZIONI COMPLETE DI IMPLEMENTAZIONE
1. INSTALLA DIPENDENZE
pip install supabase>=2.0.0
2. AGGIORNA .ENV
# Aggiungi queste righe 
SUPABASE_URL=https://iimymnlepgilbuoxnkqa.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlpbXltbmxlcGdpbGJ1b3hua3FhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYzMDc5NTMsImV4cCI6MjA3MTg4Mzk1M30.fl0wf8TVZv7OcIxL-dAlpuT6u6Y1oVx7N8hu9uvyvFo
USE_SUPABASE=true
3. AGGIORNA SETTINGS

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Supabase Configuration
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_anon_key: Optional[str] = Field(default=None, env="SUPABASE_ANON_KEY")
    use_supabase: bool = Field(default=False, env="USE_SUPABASE") 4. CREA SUPABASE TRACKER

from supabase import create_client, Client
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from core.infrastructure.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)

class SupabaseTracker:
    def __init__(self):
        settings = get_settings()
        if not settings.supabase_url or not settings.supabase_anon_key:
            raise ValueError("Supabase credentials not configured")
        
        self.client: Client = create_client(
            settings.supabase_url, 
            settings.supabase_anon_key
        )
    
    def start_workflow_run(self, client_name: str, workflow_name: str, topic: str) -> str:
        """Inizia tracking di una nuova workflow run"""
        try:
            result = self.client.table('workflow_runs').insert({
                'client_name': client_name,
                'workflow_name': workflow_name,
                'topic': topic,
                'status': 'running'
            }).execute()
            
            run_id = result.data[0]['id']
            logger.info(f"✅ Started tracking run: {run_id}")
            return run_id
            
        except Exception as e:
            logger.error(f"❌ Error starting workflow run: {e}")
            raise
    
    def complete_workflow_run(self, run_id: str, status: str = "completed", 
                             error: str = None, cost: float = None, tokens: int = None):
        """Completa una workflow run"""
        try:
            update_data = {
                'status': status,
                'completed_at': datetime.now().isoformat()
            }
            
            if error:
                update_data['error_message'] = error
            if cost is not None:
                update_data['total_cost_usd'] = cost
            if tokens is not None:
                update_data['total_tokens'] = tokens
                
            self.client.table('workflow_runs').update(update_data).eq('id', run_id).execute()
            logger.info(f"✅ Completed run {run_id} with status: {status}")
            
        except Exception as e:
            logger.error(f"❌ Error completing workflow run: {e}")
    
    def log_agent_execution(self, run_id: str, agent_name: str, step: int, 
                           input_data: Dict = None, output_data: Dict = None, 
                           thoughts: str = None, tokens: int = None, cost: float = None):
        """Log esecuzione di un agente"""
        try:
            data = {
                'run_id': run_id,
                'agent_name': agent_name,
                'step_number': step,
                'status': 'completed',
                'completed_at': datetime.now().isoformat()
            }
            
            if input_data:
                data['input_data'] = input_data
            if output_data:
                data['output_data'] = output_data
            if thoughts:
                data['thoughts'] = thoughts
            if tokens is not None:
                data['tokens_used'] = tokens
            if cost is not None:
                data['cost_usd'] = cost
                
            self.client.table('agent_executions').insert(data).execute()
            logger.info(f"✅ Logged agent {agent_name} execution for run {run_id}")
            
        except Exception as e:
            logger.error(f"❌ Error logging agent execution: {e}")
    
    def add_log(self, run_id: str, level: str, message: str, 
               agent_name: str = None, metadata: Dict = None):
        """Aggiungi un log entry"""
        try:
            data = {
                'run_id': run_id,
                'level': level.upper(),
                'message': message
            }
            
            if agent_name:
                data['agent_name'] = agent_name
            if metadata:
                data['metadata'] = metadata
                
            self.client.table('run_logs').insert(data).execute()
            
        except Exception as e:
            logger.error(f"❌ Error adding log: {e}")
    
    def get_run_history(self, client_name: str = None, limit: int = 50) -> List[Dict]:
        """Ottieni storico delle run"""
        try:
            query = self.client.table('workflow_runs').select('*').order('started_at', desc=True).limit(limit)
            
            if client_name:
                query = query.eq('client_name', client_name)
                
            result = query.execute()
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Error getting run history: {e}")
            return []
    
    def get_run_details(self, run_id: str) -> Optional[Dict]:
        """Ottieni dettagli completi di una run"""
        try:
            # Run info
            run_result = self.client.table('workflow_runs').select('*').eq('id', run_id).execute()
            if not run_result.data:
                return None
            
            # Agent executions
            agents_result = self.client.table('agent_executions').select('*').eq('run_id', run_id).order('step_number').execute()
            
            # Logs
            logs_result = self.client.table('run_logs').select('*').eq('run_id', run_id).order('timestamp').execute()
            
            return {
                'run': run_result.data[0],
                'agents': agents_result.data,
                'logs': logs_result.data
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting run details: {e}")
            return None

# Factory function
def get_tracker() -> Optional[SupabaseTracker]:
    """Get tracker instance"""
    try:
        settings = get_settings()
        if settings.use_supabase:
            return SupabaseTracker()
        return None
    except Exception as e:
        logger.warning(f"Tracker not available: {e}")
        return None  5. AGGIORNA USE CASE GENERATE CONTENT

from core.infrastructure.database.supabase_tracker import get_tracker

class GenerateContentUseCase:
    def __init__(self, workflow_factory, task_orchestrator, agent_executor, agent_repository):
        # ... existing init ...
        self.tracker = get_tracker()
    
    async def execute(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
        """Execute content generation with tracking"""
        
        # Start tracking
        run_id = None
        if self.tracker:
            try:
                run_id = self.tracker.start_workflow_run(
                    client_name=request.client_profile or "unknown",
                    workflow_name=request.workflow_type or "content_generation",
                    topic=request.topic
                )
                self.tracker.add_log(run_id, "INFO", f"Started content generation for topic: {request.topic}")
            except Exception as e:
                logger.warning(f"Tracking initialization failed: {e}")
        
        try:
            start_time = time.time()
            
            # Log request details
            if self.tracker and run_id:
                self.tracker.add_log(run_id, "INFO", f"Provider: {request.provider_config.provider.value if request.provider_config else 'default'}")
                self.tracker.add_log(run_id, "INFO", f"Model: {request.provider_config.model if request.provider_config else 'default'}")
            
            # ... existing workflow execution code ...
            
            # Execute workflow through orchestrator
            result = await self.task_orchestrator.execute_workflow(
                workflow=workflow,
                context=context,
                verbose=True,
                run_id=run_id,  # Pass run_id to orchestrator
                tracker=self.tracker
            )
            
            execution_time = time.time() - start_time
            
            if result['success']:
                # ... existing success handling ...
                
                # Complete tracking
                if self.tracker and run_id:
                    self.tracker.complete_workflow_run(
                        run_id=run_id,
                        status="completed",
                        cost=result.get('total_cost', 0),
                        tokens=result.get('total_tokens', 0)
                    )
                    self.tracker.add_log(run_id, "INFO", f"Content generation completed successfully in {execution_time:.2f}s")
                
                # ... existing response creation ...
                
            else:
                # Handle failure
                error_msg = result.get('error', 'Workflow execution failed')
                
                if self.tracker and run_id:
                    self.tracker.complete_workflow_run(
                        run_id=run_id,
                        status="failed",
                        error=error_msg
                    )
                    self.tracker.add_log(run_id, "ERROR", f"Workflow execution failed: {error_msg}")
                
                raise Exception(error_msg)
                
        except Exception as e:
            # Handle any exception
            if self.tracker and run_id:
                self.tracker.complete_workflow_run(
                    run_id=run_id,
                    status="failed",
                    error=str(e)
                )
                self.tracker.add_log(run_id, "ERROR", f"Content generation failed: {str(e)}")
            
            logger.error(f"Content generation failed: {str(e)}")
            return ContentGenerationResponse(
                content_id=uuid4(),
                title="",
                body="",
                content_type=request.content_type,
                content_format=request.content_format,
                success=False,
                error_message=str(e)
            )  6. AGGIORNA TASK ORCHESTRATOR

class TaskOrchestrator:
    async def execute_workflow(self, workflow, context, verbose=False, run_id=None, tracker=None):
        """Execute workflow with tracking"""
        
        try:
            # ... existing setup code ...
            
            step_number = 1
            for task in workflow.tasks:
                if tracker and run_id:
                    tracker.add_log(run_id, "INFO", f"Starting task: {task.name}", task.agent_name)
                
                try:
                    # Execute task
                    task_start_time = time.time()
                    
                    # ... existing task execution code ...
                    
                    task_execution_time = time.time() - task_start_time
                    
                    # Log agent execution
                    if tracker and run_id:
                        tracker.log_agent_execution(
                            run_id=run_id,
                            agent_name=task.agent_name,
                            step=step_number,
                            input_data={"task_name": task.name, "input": str(task_input)[:500]},
                            output_data={"output": str(task_output)[:500]},
                            thoughts=getattr(task_output, 'thoughts', None),
                            tokens=getattr(task_output, 'tokens_used', None),
                            cost=getattr(task_output, 'cost', None)
                        )
                        tracker.add_log(run_id, "INFO", f"Completed task: {task.name} in {task_execution_time:.2f}s", task.agent_name)
                    
                    step_number += 1
                    
                except Exception as task_error:
                    if tracker and run_id:
                        tracker.add_log(run_id, "ERROR", f"Task {task.name} failed: {str(task_error)}", task.agent_name)
                    raise
            
            # ... existing completion code ...
            
        except Exception as e:
            if tracker and run_id:
                tracker.add_log(run_id, "ERROR", f"Workflow execution failed: {str(e)}")
            raise 7. CREA CLI PER VISUALIZZARE TRACKING

#!/usr/bin/env python3
"""CLI per visualizzare tracking data"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from datetime import datetime
import json

from core.infrastructure.database.supabase_tracker import get_tracker

app = typer.Typer(help="CGSRef Tracking Commands")
console = Console()

@app.command("history")
def show_history(
    client: str = typer.Option(None, "--client", "-c", help="Filter by client"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of runs to show")
):
    """Show workflow run history"""
    
    tracker = get_tracker()
    if not tracker:
        console.print("[red]❌ Tracking not available[/red]")
        return
    
    try:
        runs = tracker.get_run_history(client_name=client, limit=limit)
        
        if not runs:
            console.print("[yellow]No runs found[/yellow]")
            return
        
        table = Table(title=f"Workflow Run History{f' - {client}' if client else ''}")
        table.add_column("ID", style="cyan", width=8)
        table.add_column("Client", style="green")
        table.add_column("Workflow", style="blue")
        table.add_column("Topic", style="white", width=30)
        table.add_column("Status", style="bold")
        table.add_column("Started", style="dim")
        table.add_column("Duration", style="magenta")
        table.add_column("Cost", style="yellow")
        
        for run in runs:
            status_style = {
                'completed': '[green]✅ Completed[/green]',
                'failed': '[red]❌ Failed[/red]',
                'running': '[yellow]🔄 Running[/yellow]'
            }.get(run['status'], run['status'])
            
            started = datetime.fromisoformat(run['started_at'].replace('Z', '+00:00'))
            started_str = started.strftime('%m/%d %H:%M')
            
            duration = f"{run['duration_seconds']}s" if run['duration_seconds'] else "-"
            cost = f"${run['total_cost_usd']:.4f}" if run['total_cost_usd'] else "-"
            
            table.add_row(
                run['id'][:8],
                run['client_name'],
                run['workflow_name'],
                run['topic'][:30] + "..." if len(run['topic']) > 30 else run['topic'],
                status_style,
                started_str,
                duration,
                cost
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")

@app.command("details")
def show_details(run_id: str):
    """Show detailed information for a specific run"""
    
    tracker = get_tracker()
    if not tracker:
        console.print("[red]❌ Tracking not available[/red]")
        return
    
    try:
        details = tracker.get_run_details(run_id)
        
        if not details:
            console.print(f"[red]❌ Run {run_id} not found[/red]")
            return
        
        run = details['run']
        agents = details['agents']
        logs = details['logs']
        
        # Run info panel
        run_info = f"""
[bold]Client:[/bold] {run['client_name']}
[bold]Workflow:[/bold] {run['workflow_name']}
[bold]Topic:[/bold] {run['topic']}
[bold]Status:[/bold] {run['status']}
[bold]Started:[/bold] {run['started_at']}
[bold]Duration:[/bold] {run['duration_seconds']}s
[bold]Cost:[/bold] ${run['total_cost_usd']:.4f}
[bold]Tokens:[/bold] {run['total_tokens']}
        """
        
        if run['error_message']:
            run_info += f"\n[bold red]Error:[/bold red] {run['error_message']}"
        
        console.print(Panel(run_info, title=f"Run Details - {run_id[:8]}", border_style="blue"))
        
        # Agents table
        if agents:
            agents_table = Table(title="Agent Executions")
            agents_table.add_column("Step", style="cyan")
            agents_table.add_column("Agent", style="green")
            agents_table.add_column("Status", style="bold")
            agents_table.add_column("Duration", style="magenta")
            agents_table.add_column("Tokens", style="yellow")
            agents_table.add_column("Thoughts", style="white", width=40)
            
            for agent in agents:
                thoughts = agent.get('thoughts', '')
                if thoughts and len(thoughts) > 40:
                    thoughts = thoughts[:37] + "..."
                
                agents_table.add_row(
                    str(agent['step_number']),
                    agent['agent_name'],
                    agent['status'],
                    f"{agent['duration_seconds']}s" if agent['duration_seconds'] else "-",
                    str(agent['tokens_used']) if agent['tokens_used'] else "-",
                    thoughts
                )
            
            console.print(agents_table)
        
        # Recent logs
        if logs:
            console.print(f"\n[bold]Recent Logs ({len(logs)} total):[/bold]")
            for log in logs[-10:]:  # Show last 10 logs
                timestamp = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                time_str = timestamp.strftime('%H:%M:%S')
                
                level_style = {
                    'ERROR': '[red]ERROR[/red]',
                    'WARNING': '[yellow]WARN[/yellow]',
                    'INFO': '[blue]INFO[/blue]',
                    'DEBUG': '[dim]DEBUG[/dim]'
                }.get(log['level'], log['level'])
                
                agent_str = f"[{log['agent_name']}] " if log['agent_name'] else ""
                console.print(f"  {time_str} {level_style} {agent_str}{log['message']}")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")

@app.command("stats")
def show_stats(
    client: str = typer.Option(None, "--client", "-c", help="Filter by client"),
    days: int = typer.Option(7, "--days", "-d", help="Number of days to analyze")
):
    """Show tracking statistics"""
    
    tracker = get_tracker()
    if not tracker:
        console.print("[red]❌ Tracking not available[/red]")
        return
    
    try:
        runs = tracker.get_run_history(client_name=client, limit=1000)
        
        if not runs:
            console.print("[yellow]No runs found[/yellow]")
            return
        
        # Calculate stats
        total_runs = len(runs)
        completed = len([r for r in runs if r['status'] == 'completed'])
        failed = len([r for r in runs if r['status'] == 'failed'])
        running = len([r for r in runs if r['status'] == 'running'])
        
        total_cost = sum(r['total_cost_usd'] or 0 for r in runs)
        total_tokens = sum(r['total_tokens'] or 0 for r in runs)
        
        avg_duration = sum(r['duration_seconds'] or 0 for r in runs if r['duration_seconds']) / max(1, len([r for r in runs if r['duration_seconds']]))
        
        stats_text = f"""
[bold]Total Runs:[/bold] {total_runs}
[bold]Completed:[/bold] [green]{completed}[/green]
[bold]Failed:[/bold] [red]{failed}[/red]
[bold]Running:[/bold] [yellow]{running}[/yellow]
[bold]Success Rate:[/bold] {(completed/max(1,total_runs)*100):.1f}%

[bold]Total Cost:[/bold] ${total_cost:.4f}
[bold]Total Tokens:[/bold] {total_tokens:,}
[bold]Avg Duration:[/bold] {avg_duration:.1f}s
        """
        
        console.print(Panel(stats_text, title=f"Statistics{f' - {client}' if client else ''}", border_style="green"))
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")

if __name__ == "__main__":
    app()  8. AGGIORNA MAIN CLI

 import typer
from api.cli.tracking import app as tracking_app

app = typer.Typer()

# Add tracking commands
app.add_typer(tracking_app, name="tracking", help="Workflow tracking commands")

# ... existing commands ...  9. CREA TEST SCRIPT

#!/usr/bin/env python3
"""Test tracking integration"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.application.use_cases.generate_content import get_use_case
from core.domain.models.content_generation import ContentGenerationRequest, ContentType, ContentFormat
from core.domain.models.provider_config import ProviderConfig, LLMProvider

async def test_tracking_integration():
    """Test complete tracking integration"""
    
    print("🧪 Testing tracking integration...")
    
    try:
        # Create request
        request = ContentGenerationRequest(
            topic="Test AI Article for Tracking",
            content_type=ContentType.ARTICLE,
            content_format=ContentFormat.MARKDOWN,
            client_profile="siebert",
            workflow_type="enhanced_article",
            provider_config=ProviderConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4o-mini",
                temperature=0.7
            )
        )
        
        # Execute with tracking
        use_case = get_use_case()
        response = await use_case.execute(request)
        
        if response.success:
            print(f"✅ Content generated successfully!")
            print(f"   Content ID: {response.content_id}")
            print(f"   Word count: {response.word_count}")
            print(f"   Generation time: {response.generation_time_seconds:.2f}s")
            print(f"\n📊 Check tracking with: python -m api.cli.main tracking history")
            return True
        else:
            print(f"❌ Generation failed: {response.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_tracking_integration())
    sys.exit(0 if success else 1) 🎯 COMANDI PER ESEGUIRE L'INTEGRAZIONE

# 1. Installa dipendenze
pip install supabase>=2.0.0

# 2. Configura .env con i tuoi valori Supabase

# 3. Testa l'integrazione
python test_tracking_integration.py

# 4. Visualizza tracking
python -m api.cli.main tracking history
python -m api.cli.main tracking stats
python -m api.cli.main tracking details <run-id>

# 5. Genera contenuto con tracking
python -m api.cli.main generate "AI in Finance" --type article --client siebert

# 6. Verifica nel dashboard Supabase
# Vai su https://your-project.supabase.co/editor  ✅ RISULTATO FINALE
Dopo questa implementazione avrai:
1. Tracking automatico di ogni workflow run
2. Dashboard web su Supabase per visualizzare i dati
3. CLI commands per analizzare le performance
4. Log dettagliati di ogni step degli agenti
5. Statistiche su costi, tempi, successi/fallimenti
6. Storico completo di tutte le generazioni