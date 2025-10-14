#!/bin/bash

# Test manuale integrazione completa Onboarding + CGS
# Questo script esegue il flusso completo con risposte corrette

set -e

BASE_URL="http://localhost:8001/api/v1/onboarding"
CGS_URL="http://localhost:8000"

echo "======================================================================"
echo "  🧪 TEST INTEGRAZIONE COMPLETA: ONBOARDING + CGS"
echo "======================================================================"
echo ""

# Colori
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Health Check
echo -e "${BLUE}Step 1: Health Check${NC}"
echo "Verifico che entrambi i servizi siano attivi..."
echo ""

echo "Onboarding Service (porta 8001):"
curl -s http://localhost:8001/health | python3 -m json.tool
echo ""

echo "CGS Backend (porta 8000):"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

read -p "Premi ENTER per continuare..."

# Step 2: Start Onboarding
echo ""
echo -e "${BLUE}Step 2: Start Onboarding${NC}"
echo "Avvio onboarding per Fylle..."
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/start" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "Fylle",
    "website": "https://fylle.ai",
    "goal": "linkedin_post",
    "user_email": "test@fylle.ai"
  }')

echo "$RESPONSE" | python3 -m json.tool

SESSION_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

echo ""
echo -e "${GREEN}✅ Session creata: $SESSION_ID${NC}"
echo ""

echo "⏳ Attendo 30 secondi per completamento research + synthesis..."
sleep 30

# Step 3: Get Snapshot
echo ""
echo -e "${BLUE}Step 3: Recupero Snapshot e Domande${NC}"
echo ""

SNAPSHOT=$(curl -s "$BASE_URL/$SESSION_ID")
echo "$SNAPSHOT" | python3 -m json.tool

echo ""
echo -e "${YELLOW}📋 DOMANDE GENERATE:${NC}"
echo "$SNAPSHOT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'snapshot' in data and 'clarifying_questions' in data['snapshot']:
    for q in data['snapshot']['clarifying_questions']:
        print(f\"\\n{q['id']}: {q['question']}\")
        print(f\"  Tipo: {q.get('expected_response_type', 'string')}\")
        if 'options' in q and q['options']:
            print(f\"  Opzioni: {', '.join(q['options'])}\")
"

echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE: Guarda le domande sopra e le loro opzioni!${NC}"
echo ""

read -p "Premi ENTER quando sei pronto a rispondere..."

# Step 4: Submit Answers (interattivo)
echo ""
echo -e "${BLUE}Step 4: Invia Risposte${NC}"
echo ""
echo "Inserisci le risposte alle domande:"
echo ""

# Estrai le domande
QUESTIONS=$(echo "$SNAPSHOT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'snapshot' in data and 'clarifying_questions' in data['snapshot']:
    for q in data['snapshot']['clarifying_questions']:
        print(f\"{q['id']}|||{q['question']}|||{q.get('expected_response_type', 'string')}|||{','.join(q.get('options', []))}\")
")

# Costruisci JSON risposte
ANSWERS_JSON="{"

FIRST=true
while IFS='|||' read -r qid question qtype options; do
    echo ""
    echo "Domanda: $question"
    
    if [ "$qtype" = "enum" ] && [ -n "$options" ]; then
        echo "Opzioni disponibili:"
        IFS=',' read -ra OPTS <<< "$options"
        for i in "${!OPTS[@]}"; do
            echo "  $((i+1)). ${OPTS[$i]}"
        done
        echo -n "Scegli numero (1-${#OPTS[@]}): "
        read choice
        ANSWER="${OPTS[$((choice-1))]}"
    else
        echo -n "Risposta: "
        read ANSWER
    fi
    
    if [ "$FIRST" = true ]; then
        ANSWERS_JSON="$ANSWERS_JSON\"$qid\": \"$ANSWER\""
        FIRST=false
    else
        ANSWERS_JSON="$ANSWERS_JSON, \"$qid\": \"$ANSWER\""
    fi
done <<< "$QUESTIONS"

ANSWERS_JSON="$ANSWERS_JSON}"

echo ""
echo "Risposte da inviare:"
echo "{\"answers\": $ANSWERS_JSON}" | python3 -m json.tool
echo ""

read -p "Confermi l'invio? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Test annullato."
    exit 0
fi

echo ""
echo "⏳ Invio risposte..."

ANSWER_RESPONSE=$(curl -s -X POST "$BASE_URL/$SESSION_ID/answers" \
  -H "Content-Type: application/json" \
  -d "{\"answers\": $ANSWERS_JSON}")

echo "$ANSWER_RESPONSE" | python3 -m json.tool

echo ""
echo -e "${GREEN}✅ Risposte inviate!${NC}"
echo ""

read -p "Premi ENTER per procedere con l'esecuzione..."

# Step 5: Execute (chiamata a CGS)
echo ""
echo -e "${BLUE}Step 5: Execute - Generazione Contenuto con CGS${NC}"
echo ""
echo "⏳ Avvio generazione contenuto (questo può richiedere 1-2 minuti)..."
echo ""

EXECUTE_RESPONSE=$(curl -s -X POST "$BASE_URL/$SESSION_ID/execute")

echo "$EXECUTE_RESPONSE" | python3 -m json.tool

echo ""
echo -e "${GREEN}✅ Esecuzione completata!${NC}"
echo ""

# Step 6: Verifica risultato finale
echo ""
echo -e "${BLUE}Step 6: Verifica Risultato Finale${NC}"
echo ""

sleep 5

FINAL=$(curl -s "$BASE_URL/$SESSION_ID")
echo "$FINAL" | python3 -m json.tool

echo ""
echo "======================================================================"
echo -e "${GREEN}  🎉 TEST COMPLETATO!${NC}"
echo "======================================================================"
echo ""
echo "Session ID: $SESSION_ID"
echo ""
echo "Puoi verificare i dati in Supabase:"
echo "https://app.supabase.com/project/iimymnlepgilbuoxnkqa/editor/onboarding_sessions"
echo ""

