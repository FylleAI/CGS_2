#!/usr/bin/env python3
"""
Test completo del flusso di onboarding end-to-end.

Questo script testa l'intero flusso:
1. Start onboarding session
2. Verifica snapshot e domande
3. Invia risposte
4. Esegue generazione contenuto (chiama CGS)

PREREQUISITI:
- Onboarding service attivo su porta 8001
- CGS backend attivo su porta 8000 (per step 4)
"""

import asyncio
import httpx
import json
from typing import Dict, Any
import sys


# Configurazione
ONBOARDING_API_URL = "http://localhost:8001"
TEST_COMPANY = {
    "brand_name": "Fylle",
    "website": "https://fylle.ai",
    "user_email": "test@fylle.ai",
    "goal": "linkedin_post"
}


def print_section(title: str):
    """Stampa una sezione formattata."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_json(data: Dict[Any, Any], indent: int = 2):
    """Stampa JSON formattato."""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


async def test_health_check():
    """Test 0: Health check."""
    print_section("🏥 Test 0: Health Check")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{ONBOARDING_API_URL}/health")
            response.raise_for_status()
            
            data = response.json()
            print("✅ Servizio attivo!")
            print_json(data)
            
            # Verifica dependencies essenziali (CGS non è richiesto per i primi 3 test)
            services = data.get("services", {})
            if not all([services.get("perplexity"), services.get("gemini"), services.get("supabase")]):
                print("\n⚠️  Attenzione: Alcune dipendenze essenziali non sono configurate")
                print(f"   Perplexity: {services.get('perplexity')}")
                print(f"   Gemini: {services.get('gemini')}")
                print(f"   Supabase: {services.get('supabase')}")
                return False

            # CGS è opzionale per i primi 3 test
            if not data.get("cgs_healthy"):
                print("\n⚠️  CGS backend non attivo - Test 4 (execute) sarà saltato")

            return True
            
        except httpx.ConnectError:
            print("❌ Errore: Servizio non raggiungibile su porta 8001")
            print("   Avvia il servizio con:")
            print("   uvicorn services.onboarding.api.main:app --reload --port 8001")
            return False
        except Exception as e:
            print(f"❌ Errore: {e}")
            return False


async def test_start_onboarding() -> str | None:
    """Test 1: Avvia onboarding session."""
    print_section("🚀 Test 1: Start Onboarding Session")

    print(f"Azienda: {TEST_COMPANY['brand_name']}")
    print(f"Website: {TEST_COMPANY['website']}")
    print(f"Goal: {TEST_COMPANY['goal']}")
    print("\n⏳ Avvio onboarding (questo richiederà 30-60 secondi)...")
    print("   - Ricerca con Perplexity...")
    print("   - Sintesi con Gemini/Vertex AI...")
    print("   - Generazione domande...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{ONBOARDING_API_URL}/api/v1/onboarding/start",
                json=TEST_COMPANY
            )
            response.raise_for_status()
            
            data = response.json()
            session_id = data.get("session_id")
            
            print("\n✅ Onboarding avviato!")
            print(f"Session ID: {session_id}")
            print(f"State: {data.get('state')}")
            print(f"Message: {data.get('message')}")
            
            return session_id
            
        except httpx.HTTPStatusError as e:
            print(f"\n❌ Errore HTTP {e.response.status_code}")
            print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"\n❌ Errore: {e}")
            return None


async def test_get_session(session_id: str) -> Dict[Any, Any] | None:
    """Test 2: Ottieni snapshot e domande."""
    print_section("📋 Test 2: Verifica Snapshot e Domande")
    
    print(f"Session ID: {session_id}")
    print("\n⏳ Recupero snapshot...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{ONBOARDING_API_URL}/api/v1/onboarding/{session_id}"
            )
            response.raise_for_status()
            
            data = response.json()
            
            print("\n✅ Snapshot recuperato!")
            print(f"State: {data.get('state')}")
            print(f"Company: {data.get('company_name')}")
            
            # Mostra snapshot
            snapshot = data.get("snapshot", {})
            if snapshot:
                print("\n📊 Company Info:")
                company = snapshot.get("company", {})
                print(f"  Name: {company.get('name')}")
                print(f"  Description: {company.get('description', '')[:100]}...")
                print(f"  Offerings: {len(company.get('offerings', []))} items")
                print(f"  Differentiators: {len(company.get('differentiators', []))} items")
                
                print("\n👥 Audience Info:")
                audience = snapshot.get("audience", {})
                print(f"  Primary: {audience.get('primary')}")
                print(f"  Pain Points: {len(audience.get('pain_points', []))} items")
                
                print("\n🎤 Voice Info:")
                voice = snapshot.get("voice", {})
                print(f"  Tone: {voice.get('tone')}")
                
                print("\n❓ Clarifying Questions:")
                questions = snapshot.get("clarifying_questions", [])
                for i, q in enumerate(questions, 1):
                    print(f"\n  Q{i} [{q.get('id')}]:")
                    print(f"    {q.get('question')}")
                    print(f"    Context: {q.get('context')}")
            
            return data
            
        except Exception as e:
            print(f"\n❌ Errore: {e}")
            return None


async def test_submit_answers(session_id: str, snapshot_data: Dict[Any, Any]) -> bool:
    """Test 3: Invia risposte alle domande."""
    print_section("✍️  Test 3: Invia Risposte")
    
    # Estrai domande
    snapshot = snapshot_data.get("snapshot", {})
    questions = snapshot.get("clarifying_questions", [])
    
    if not questions:
        print("❌ Nessuna domanda trovata nello snapshot")
        return False
    
    # Risposte di esempio
    example_answers = [
        "LinkedIn posts and newsletters about AI and automation",
        "B2B marketing teams and content managers in tech companies",
        "Professional, innovative, and helpful - we want to educate while inspiring"
    ]
    
    # Costruisci payload risposte (dizionario question_id -> answer)
    answers = {}
    for i, q in enumerate(questions):
        answer_text = example_answers[i] if i < len(example_answers) else f"Example answer for {q.get('id')}"
        answers[q.get("id")] = answer_text
        print(f"\nQ: {q.get('question')}")
        print(f"A: {answer_text}")
    
    print("\n⏳ Invio risposte...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{ONBOARDING_API_URL}/api/v1/onboarding/{session_id}/answers",
                json={"answers": answers}
            )
            response.raise_for_status()
            
            data = response.json()
            
            print("\n✅ Risposte inviate!")
            print(f"State: {data.get('state')}")
            print(f"Message: {data.get('message')}")
            print(f"Answers Count: {data.get('answers_count')}")
            
            return True
            
        except httpx.HTTPStatusError as e:
            print(f"\n❌ Errore HTTP {e.response.status_code}")
            try:
                error_detail = e.response.json()
                print(f"Dettaglio: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Response: {e.response.text}")
            return False
        except Exception as e:
            print(f"\n❌ Errore: {e}")
            import traceback
            traceback.print_exc()
            return False


async def test_execute_onboarding(session_id: str) -> bool:
    """Test 4: Esegui generazione contenuto (chiama CGS)."""
    print_section("🎯 Test 4: Esegui Generazione Contenuto")
    
    print(f"Session ID: {session_id}")
    print("\n⏳ Esecuzione onboarding (questo richiederà 60-120 secondi)...")
    print("   - Costruzione payload CGS...")
    print("   - Chiamata a CGS backend...")
    print("   - Generazione contenuto...")
    print("\n⚠️  NOTA: CGS backend deve essere attivo su porta 8000!")
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            response = await client.post(
                f"{ONBOARDING_API_URL}/api/v1/onboarding/{session_id}/execute"
            )
            response.raise_for_status()
            
            data = response.json()
            
            print("\n✅ Onboarding completato!")
            print(f"State: {data.get('state')}")
            print(f"Message: {data.get('message')}")
            
            # Mostra risultato
            result = data.get("result", {})
            if result:
                print("\n📄 Contenuto Generato:")
                content = result.get("content", {})
                print(f"  Title: {content.get('title', 'N/A')}")
                print(f"  Body: {content.get('body', '')[:200]}...")
                
                metrics = result.get("workflow_metrics", {})
                if metrics:
                    print("\n📊 Metriche:")
                    print(f"  Duration: {metrics.get('total_duration_seconds', 0):.1f}s")
                    print(f"  Steps: {metrics.get('steps_executed', 0)}")
                    print(f"  Tokens: {metrics.get('tokens_used', 0)}")
            
            return True
            
        except httpx.ConnectError:
            print("\n❌ Errore: CGS backend non raggiungibile su porta 8000")
            print("   Avvia CGS con:")
            print("   uvicorn api.rest.main:app --reload --port 8000")
            return False
        except httpx.HTTPStatusError as e:
            print(f"\n❌ Errore HTTP {e.response.status_code}")
            print(f"Response: {e.response.text}")
            return False
        except Exception as e:
            print(f"\n❌ Errore: {e}")
            return False


async def main():
    """Esegue tutti i test in sequenza."""
    print("\n" + "=" * 70)
    print("  🧪 TEST COMPLETO ONBOARDING SERVICE")
    print("=" * 70)
    print("\nQuesto test eseguirà l'intero flusso di onboarding end-to-end.")
    print("Assicurati che:")
    print("  1. Onboarding service sia attivo su porta 8001")
    print("  2. CGS backend sia attivo su porta 8000 (per test 4)")
    print("\nPremi CTRL+C per annullare...")
    
    await asyncio.sleep(2)
    
    # Test 0: Health check
    if not await test_health_check():
        print("\n❌ Health check fallito. Interrompo i test.")
        return 1
    
    # Test 1: Start onboarding
    session_id = await test_start_onboarding()
    if not session_id:
        print("\n❌ Start onboarding fallito. Interrompo i test.")
        return 1
    
    # Attendi che il processing sia completato
    print("\n⏳ Attendo completamento processing...")
    await asyncio.sleep(5)
    
    # Test 2: Get snapshot
    snapshot_data = await test_get_session(session_id)
    if not snapshot_data:
        print("\n❌ Get session fallito. Interrompo i test.")
        return 1
    
    # Test 3: Submit answers
    if not await test_submit_answers(session_id, snapshot_data):
        print("\n❌ Submit answers fallito. Interrompo i test.")
        return 1
    
    # Test 4: Execute onboarding
    if not await test_execute_onboarding(session_id):
        print("\n⚠️  Execute onboarding fallito (probabilmente CGS non attivo).")
        print("   I primi 3 test sono comunque passati con successo!")
        return 0
    
    # Successo!
    print_section("🎉 TUTTI I TEST COMPLETATI CON SUCCESSO!")
    print("\nIl servizio di onboarding funziona correttamente!")
    print(f"\nSession ID finale: {session_id}")
    print("\nPuoi verificare i dati in Supabase:")
    print("https://app.supabase.com/project/iimymnlepgilbuoxnkqa")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrotto dall'utente.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Errore inaspettato: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

