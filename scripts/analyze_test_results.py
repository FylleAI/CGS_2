"""
Analyze test results from Supabase after end-to-end test.

This script checks:
1. company_contexts table - RAG context saved
2. onboarding_sessions table - Session completed
3. Validates rich context was passed to CGS
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client
from dotenv import load_dotenv

def main():
    """Analyze test results."""

    # Load environment from root .env
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)

    # Initialize Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        print(f"   URL: {supabase_url}")
        print(f"   Key: {'***' if supabase_key else 'None'}")
        return
    
    client = create_client(supabase_url, supabase_key)
    
    print("=" * 80)
    print("📊 ANALISI RISULTATI TEST END-TO-END")
    print("=" * 80)
    print()
    
    # 1. Check company_contexts
    print("🔍 1. COMPANY CONTEXTS (RAG)")
    print("-" * 80)
    
    # Get latest context (last 10 minutes)
    cutoff = (datetime.utcnow() - timedelta(minutes=10)).isoformat()
    
    contexts_response = client.table("company_contexts").select("*").gte("created_at", cutoff).order("created_at", desc=True).execute()
    
    if contexts_response.data:
        print(f"✅ Trovati {len(contexts_response.data)} context creati negli ultimi 10 minuti\n")
        
        for ctx in contexts_response.data:
            print(f"📦 Context ID: {ctx['context_id']}")
            print(f"   Company: {ctx['company_display_name']} ({ctx['company_name']})")
            print(f"   Version: v{ctx['version']}")
            print(f"   Industry: {ctx['industry']}")
            print(f"   Active: {'✅' if ctx['is_active'] else '❌'}")
            print(f"   Usage Count: {ctx['usage_count']}")
            print(f"   Created: {ctx['created_at']}")
            print(f"   Last Used: {ctx['last_used_at']}")
            
            # Check snapshot data
            snapshot = ctx.get('snapshot_data', {})
            if snapshot:
                company = snapshot.get('company', {})
                print(f"   Differentiators: {len(company.get('differentiators', []))}")
                print(f"   Key Offerings: {len(company.get('key_offerings', []))}")
                
                voice = snapshot.get('voice', {})
                print(f"   Tone: {voice.get('tone', 'N/A')}")
                print(f"   Style Guidelines: {len(voice.get('style_guidelines', []))}")
                print(f"   Forbidden Phrases: {len(voice.get('forbidden_phrases', []))}")
                
                insights = snapshot.get('insights', {})
                print(f"   Key Messages: {len(insights.get('key_messages', []))}")
            
            print()
    else:
        print("❌ Nessun context trovato negli ultimi 10 minuti")
        print()
    
    # 2. Check onboarding_sessions
    print("🔍 2. ONBOARDING SESSIONS")
    print("-" * 80)
    
    sessions_response = client.table("onboarding_sessions").select("*").gte("created_at", cutoff).order("created_at", desc=True).execute()
    
    if sessions_response.data:
        print(f"✅ Trovate {len(sessions_response.data)} sessioni create negli ultimi 10 minuti\n")
        
        for session in sessions_response.data:
            print(f"📝 Session ID: {session['session_id']}")
            print(f"   Brand: {session.get('brand_name', 'N/A')}")
            print(f"   Goal: {session.get('goal', 'N/A')}")
            print(f"   State: {session.get('state', 'N/A')}")
            print(f"   Company Context ID: {session.get('company_context_id', 'N/A')}")
            print(f"   Created: {session['created_at']}")
            print(f"   Updated: {session['updated_at']}")
            
            # Check CGS response
            cgs_response = session.get('cgs_response', {})
            if cgs_response:
                print(f"   CGS Status: {cgs_response.get('status', 'N/A')}")
                print(f"   CGS Run ID: {cgs_response.get('cgs_run_id', 'N/A')}")
                
                content = cgs_response.get('content', {})
                if content:
                    print(f"   Content Title: {content.get('title', 'N/A')}")
                    print(f"   Content Word Count: {content.get('word_count', 0)}")
            
            # Check CGS payload
            cgs_payload = session.get('cgs_payload', {})
            if cgs_payload:
                print(f"   Workflow: {cgs_payload.get('workflow', 'N/A')}")
                
                # Check if rich context was included
                company_snapshot = cgs_payload.get('company_snapshot')
                clarifying_answers = cgs_payload.get('clarifying_answers')
                
                if company_snapshot:
                    print(f"   ✅ Rich Context: company_snapshot PRESENTE")
                else:
                    print(f"   ❌ Rich Context: company_snapshot MANCANTE")
                
                if clarifying_answers:
                    print(f"   ✅ Rich Context: clarifying_answers PRESENTE ({len(clarifying_answers)} answers)")
                else:
                    print(f"   ❌ Rich Context: clarifying_answers MANCANTE")
            
            print()
    else:
        print("❌ Nessuna sessione trovata negli ultimi 10 minuti")
        print()
    
    # 3. Summary
    print("=" * 80)
    print("📊 RIEPILOGO")
    print("=" * 80)
    
    if contexts_response.data and sessions_response.data:
        context = contexts_response.data[0]
        session = sessions_response.data[0]
        
        # Check if session is linked to context
        if session.get('company_context_id') == context['context_id']:
            print("✅ Sessione collegata al context RAG")
        else:
            print("⚠️ Sessione NON collegata al context RAG")
        
        # Check if context was used
        if context['usage_count'] > 0:
            print(f"✅ Context utilizzato {context['usage_count']} volte")
        else:
            print("⚠️ Context non ancora utilizzato")
        
        # Check if rich context was passed
        cgs_payload = session.get('cgs_payload', {})
        if cgs_payload.get('company_snapshot') and cgs_payload.get('clarifying_answers'):
            print("✅ Rich context passato a CGS")
        else:
            print("❌ Rich context NON passato a CGS")
        
        # Check if session completed
        if session.get('state') == 'done':
            print("✅ Sessione completata con successo")
        else:
            print(f"⚠️ Sessione in stato: {session.get('state')}")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()

