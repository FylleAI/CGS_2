# 🎯 ESEMPI PRATICI: Implementazione Profili Dinamici

**Versione**: 1.0  
**Data**: 2025-10-14  
**Riferimento**: [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)

---

## 📋 INDICE

1. [Priorità 1: Comandi Pratici](#priorità-1-comandi-pratici)
2. [Priorità 2: Test Profili Dinamici](#priorità-2-test-profili-dinamici)
3. [Priorità 3: Test Performance](#priorità-3-test-performance)
4. [Troubleshooting](#troubleshooting)
5. [Script Utility](#script-utility)

---

## 🔥 PRIORITÀ 1: COMANDI PRATICI

### Step 1: Attivare Agent Profilo Default

```bash
# 1. Navigare nella directory agent
cd data/profiles/default/agents/

# 2. Backup configurazione corrente
mkdir -p ../../../backups/default_agents_$(date +%Y%m%d)
cp *.yaml ../../../backups/default_agents_$(date +%Y%m%d)/

# 3. Attivare tutti gli agent (metodo rapido)
for file in *.yaml; do
  sed -i '' 's/is_active: false/is_active: true/g' "$file"
  echo "✅ Activated: $file"
done

# 4. Verificare modifiche
grep "is_active:" *.yaml

# Output atteso:
# analyst.yaml:is_active: true
# copywriter.yaml:is_active: true
# enhanced_article_writer.yaml:is_active: true
# ...

# 5. Validare sintassi YAML
for file in *.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$file'))" && echo "✅ $file valid" || echo "❌ $file invalid"
done

# 6. Tornare alla root
cd ../../../../
```

### Step 2: Creare Entry "default" in Supabase

```bash
# 1. Aprire Supabase Dashboard
open "https://app.supabase.com/project/iimymnlepgilbuoxnkqa/editor"

# 2. Aprire SQL Editor (menu laterale)
# 3. Copiare e eseguire questo SQL:
```

```sql
-- Verificare se entry esiste già
SELECT * FROM clients WHERE name = 'default';

-- Se non esiste, creare entry
INSERT INTO clients (
  name,
  display_name,
  description,
  brand_voice,
  style_guidelines,
  target_audience,
  industry,
  company_background,
  key_messages,
  terminology,
  content_preferences,
  rag_enabled,
  knowledge_base_path,
  created_at,
  updated_at
) VALUES (
  'default',
  'Default Profile',
  'Generic profile for onboarding clients without specific configuration',
  'professional, clear, informative',
  'Use clear language, avoid jargon, focus on value proposition',
  'Business professionals and decision makers',
  'Technology and Business Services',
  'Multi-industry platform serving diverse clients',
  ARRAY['Innovation', 'Efficiency', 'Results-driven'],
  '{}',
  '{"tone": "professional", "style": "informative"}',
  true,
  'data/knowledge_base/default',
  NOW(),
  NOW()
)
ON CONFLICT (name) DO NOTHING;

-- Verificare inserimento
SELECT id, name, display_name, rag_enabled, created_at
FROM clients 
WHERE name = 'default';
```

### Step 3: Riavviare CGS Backend

```bash
# 1. Terminare processo corrente (se in esecuzione)
# CTRL+C nel terminal dove gira CGS

# 2. Riavviare con reload
cd /path/to/CGS_2
python3 -m uvicorn api.rest.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Verificare startup nei log
# Cercare:
# ✅ "Loaded client-specific agent: rag_specialist for profile: default"
# ✅ "Loaded client-specific agent: copywriter for profile: default"
# ❌ NO "Client-specific agent 'X' is inactive"
```

### Step 4: Test Completo

```bash
# Test 1: Health Check
curl http://localhost:8000/health

# Test 2: Workflow con profilo default
curl -X POST http://localhost:8000/api/v1/content/generate \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "enhanced_article",
    "client_profile": "default",
    "topic": "The Future of AI in Marketing",
    "target_audience": "Marketing professionals",
    "target_word_count": 500
  }'

# Test 3: Verificare log CGS
# Cercare:
# ✅ "Using client-specific agent 'rag_specialist'"
# ✅ "RAG RETRIEVAL: Accessing knowledge base for client 'default'" → SUCCESS
# ❌ NO "Using global agent"
# ❌ NO "RAG ERROR: Failed to retrieve content"
```

---

## 🚀 PRIORITÀ 2: TEST PROFILI DINAMICI

### Scenario 1: Onboarding Nuovo Brand "TestBrand"

```bash
# 1. Avviare onboarding service (se non già in esecuzione)
cd /path/to/CGS_2/onboarding
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

# 2. Avviare CGS backend (se non già in esecuzione)
cd /path/to/CGS_2
python3 -m uvicorn api.rest.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Start onboarding
SESSION_ID=$(curl -s -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "TestBrand",
    "website": "https://testbrand.com",
    "goal": "article",
    "user_email": "test@testbrand.com"
  }' | jq -r '.session_id')

echo "Session ID: $SESSION_ID"

# 4. Aspettare completamento research + synthesis (30-40s)
sleep 40

# 5. Verificare snapshot
curl -s "http://localhost:8001/api/v1/onboarding/$SESSION_ID" | jq '.snapshot'

# 6. Rispondere alle domande (esempio)
curl -X POST "http://localhost:8001/api/v1/onboarding/$SESSION_ID/answers" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "q1": "LinkedIn, email newsletters, and blog content",
      "q2": "Increase brand awareness",
      "q3": true
    }
  }'

# 7. Eseguire workflow CGS
curl -X POST "http://localhost:8001/api/v1/onboarding/$SESSION_ID/execute"

# 8. Aspettare completamento (20-30s)
sleep 30

# 9. Verificare risultato
curl -s "http://localhost:8001/api/v1/onboarding/$SESSION_ID" | jq '{
  state: .state,
  profile_created: .profile_name,
  content_title: .content_title,
  word_count: .word_count
}'
```

### Scenario 2: Verificare Profilo Creato

```bash
# 1. Verificare directory profilo
ls -la data/profiles/testbrand/

# Output atteso:
# drwxr-xr-x  agents/
# -rw-r--r--  profile.yaml

# 2. Verificare agent creati
ls -la data/profiles/testbrand/agents/

# Output atteso:
# -rw-r--r--  rag_specialist.yaml
# -rw-r--r--  copywriter.yaml
# -rw-r--r--  enhanced_article_writer.yaml
# -rw-r--r--  perplexity_researcher.yaml
# -rw-r--r--  enhanced_article_compliance_specialist.yaml

# 3. Verificare personalizzazione agent
cat data/profiles/testbrand/agents/copywriter.yaml | grep -A 10 "BRAND CONTEXT"

# Output atteso:
# BRAND CONTEXT (from onboarding):
# - Company: TestBrand
# - Industry: ...
# - Voice: ...

# 4. Verificare metadata profilo
cat data/profiles/testbrand/profile.yaml

# 5. Verificare entry Supabase
# SQL Editor:
SELECT * FROM clients WHERE name = 'testbrand';

# 6. Verificare knowledge base
ls -la data/knowledge_base/testbrand/

# Output atteso:
# -rw-r--r--  company_overview.md
# -rw-r--r--  brand_voice.md
# -rw-r--r--  target_audience.md
# -rw-r--r--  key_messages.md
# -rw-r--r--  offerings.md (se presenti)

# 7. Leggere documento KB
cat data/knowledge_base/testbrand/brand_voice.md
```

### Scenario 3: Test Riuso Profilo Esistente

```bash
# 1. Secondo onboarding stesso brand
SESSION_ID_2=$(curl -s -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "TestBrand",
    "website": "https://testbrand.com",
    "goal": "linkedin_post",
    "user_email": "test2@testbrand.com"
  }' | jq -r '.session_id')

# 2. Verificare log onboarding service
# Cercare:
# ✅ "Cache HIT for profile: testbrand"
# ✅ "Reusing existing profile: testbrand"
# ❌ NO "Creating new profile for: TestBrand"

# 3. Completare workflow
sleep 40
curl -X POST "http://localhost:8001/api/v1/onboarding/$SESSION_ID_2/answers" \
  -d '{"answers": {"q1": "...", "q2": "...", "q3": true}}'
curl -X POST "http://localhost:8001/api/v1/onboarding/$SESSION_ID_2/execute"
```

---

## ⚡ PRIORITÀ 3: TEST PERFORMANCE

### Test 1: Cache Hit Rate

```bash
# Script per testare cache
for i in {1..10}; do
  echo "=== Test $i ==="
  
  SESSION_ID=$(curl -s -X POST http://localhost:8001/api/v1/onboarding/start \
    -H "Content-Type: application/json" \
    -d '{
      "brand_name": "TestBrand",
      "website": "https://testbrand.com",
      "goal": "linkedin_post",
      "user_email": "test'$i'@testbrand.com"
    }' | jq -r '.session_id')
  
  echo "Session: $SESSION_ID"
  
  # Aspettare completamento
  sleep 40
  
  # Verificare se cache hit
  curl -s "http://localhost:8001/api/v1/onboarding/$SESSION_ID" | \
    jq '{session_id, profile_name, cache_hit: .metadata.cache_hit}'
done

# Calcolare hit rate dai log
grep "Cache HIT" onboarding.log | wc -l
grep "Cache MISS" onboarding.log | wc -l
```

### Test 2: Tempo Lookup Profilo

```bash
# Script per misurare performance
python3 << 'EOF'
import asyncio
import httpx
import time
from statistics import mean, median

async def test_profile_lookup():
    times = []
    
    for i in range(100):
        start = time.time()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/api/v1/onboarding/start",
                json={
                    "brand_name": "TestBrand",
                    "website": "https://testbrand.com",
                    "goal": "linkedin_post",
                    "user_email": f"test{i}@testbrand.com"
                }
            )
        
        elapsed = (time.time() - start) * 1000  # ms
        times.append(elapsed)
        
        if i % 10 == 0:
            print(f"Progress: {i}/100")
    
    print(f"\n=== RESULTS ===")
    print(f"Mean: {mean(times):.2f}ms")
    print(f"Median: {median(times):.2f}ms")
    print(f"Min: {min(times):.2f}ms")
    print(f"Max: {max(times):.2f}ms")
    
    # Target: < 100ms
    if mean(times) < 100:
        print("✅ PASS: Mean lookup time < 100ms")
    else:
        print("❌ FAIL: Mean lookup time >= 100ms")

asyncio.run(test_profile_lookup())
EOF
```

### Test 3: Load Test

```bash
# Installare hey (load testing tool)
# macOS: brew install hey
# Linux: go install github.com/rakyll/hey@latest

# Test 1: 100 richieste, 10 concurrent
hey -n 100 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"brand_name":"TestBrand","website":"https://testbrand.com","goal":"linkedin_post","user_email":"test@test.com"}' \
  http://localhost:8001/api/v1/onboarding/start

# Verificare:
# - Success rate: 100%
# - Average response time: < 200ms
# - No errors

# Test 2: CGS workflow
hey -n 50 -c 5 -m POST \
  -H "Content-Type: application/json" \
  -d '{"workflow_type":"enhanced_article","client_profile":"testbrand","topic":"Test","target_audience":"general"}' \
  http://localhost:8000/api/v1/content/generate
```

---

## 🔧 TROUBLESHOOTING

### Problema 1: Agent Non Attivati

**Sintomo**:
```
WARNING: Client-specific agent 'rag_specialist' is inactive (is_active=false); skipping
WARNING: Using global agent 'rag_specialist' instead
```

**Soluzione**:
```bash
# Verificare configurazione
grep "is_active:" data/profiles/default/agents/*.yaml

# Se ancora false, riattivare
cd data/profiles/default/agents/
sed -i '' 's/is_active: false/is_active: true/g' *.yaml

# Riavviare CGS
# CTRL+C e poi:
python3 -m uvicorn api.rest.main:app --host 0.0.0.0 --port 8000 --reload
```

### Problema 2: RAG Error

**Sintomo**:
```
ERROR: RAG ERROR: Failed to retrieve content for default: 
{'message': 'Cannot coerce the result to a single JSON object', 
 'code': 'PGRST116', 
 'details': 'The result contains 0 rows'}
```

**Soluzione**:
```sql
-- Verificare entry clients
SELECT * FROM clients WHERE name = 'default';

-- Se non esiste, creare (vedi Step 2 sopra)
INSERT INTO clients (...) VALUES (...);
```

### Problema 3: Profilo Non Creato

**Sintomo**:
```bash
ls data/profiles/testbrand/
# ls: data/profiles/testbrand/: No such file or directory
```

**Soluzione**:
```bash
# 1. Verificare log onboarding service
tail -f onboarding.log | grep "Creating CGS profile"

# 2. Verificare permessi directory
ls -la data/profiles/
chmod 755 data/profiles/

# 3. Verificare implementazione
# Assicurarsi che create_client_profile.py sia implementato
ls -la onboarding/application/use_cases/create_client_profile.py

# 4. Verificare integrazione in execute_onboarding.py
grep "CreateClientProfileUseCase" onboarding/application/use_cases/execute_onboarding.py
```

### Problema 4: Knowledge Base Vuota

**Sintomo**:
```bash
ls data/knowledge_base/testbrand/
# (nessun file)
```

**Soluzione**:
```bash
# 1. Verificare log
tail -f onboarding.log | grep "Populating knowledge base"

# 2. Verificare implementazione
ls -la onboarding/application/use_cases/populate_knowledge_base.py

# 3. Verificare permessi
chmod 755 data/knowledge_base/
mkdir -p data/knowledge_base/testbrand

# 4. Test manuale
python3 << 'EOF'
import asyncio
from onboarding.application.use_cases.populate_knowledge_base import PopulateKnowledgeBaseUseCase
from onboarding.config.settings import OnboardingSettings

async def test():
    settings = OnboardingSettings()
    uc = PopulateKnowledgeBaseUseCase(settings)
    # ... test con snapshot mock
    
asyncio.run(test())
EOF
```

### Problema 5: Cache Non Funziona

**Sintomo**:
```
Cache MISS for profile: testbrand
Cache MISS for profile: testbrand  # Dovrebbe essere HIT
```

**Soluzione**:
```bash
# 1. Verificare implementazione cache
ls -la onboarding/infrastructure/cache/profile_cache.py

# 2. Verificare integrazione
grep "ProfileCache" onboarding/application/use_cases/execute_onboarding.py

# 3. Test manuale cache
python3 << 'EOF'
import asyncio
from onboarding.infrastructure.cache.profile_cache import ProfileCache
from onboarding.config.settings import OnboardingSettings

async def test():
    settings = OnboardingSettings()
    cache = ProfileCache(settings)
    
    # Test set/get
    await cache.set_profile("TestBrand", {"name": "testbrand"})
    result = await cache.get_profile("TestBrand")
    
    print(f"Cache test: {result}")
    print(f"Stats: {cache.get_stats()}")

asyncio.run(test())
EOF
```

---

## 🛠️ SCRIPT UTILITY

### Script 1: Attivazione Batch Agent

```bash
#!/bin/bash
# File: scripts/activate_agents.sh

PROFILE=${1:-default}

echo "Activating agents for profile: $PROFILE"

cd "data/profiles/$PROFILE/agents/" || exit 1

# Backup
BACKUP_DIR="../../../backups/${PROFILE}_agents_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp *.yaml "$BACKUP_DIR/"
echo "✅ Backup created: $BACKUP_DIR"

# Activate
for file in *.yaml; do
  sed -i '' 's/is_active: false/is_active: true/g' "$file"
  echo "✅ Activated: $file"
done

# Verify
echo ""
echo "=== VERIFICATION ==="
grep "is_active:" *.yaml

cd - > /dev/null
```

**Uso**:
```bash
chmod +x scripts/activate_agents.sh
./scripts/activate_agents.sh default
./scripts/activate_agents.sh testbrand
```

### Script 2: Cleanup Profili Vecchi

```bash
#!/bin/bash
# File: scripts/cleanup_old_profiles.sh

DAYS=${1:-90}

echo "Cleaning up profiles older than $DAYS days..."

# Find e rimuovi directory profili vecchie
find data/profiles -type d -mtime +$DAYS -maxdepth 1 | while read dir; do
  if [ "$dir" != "data/profiles/default" ]; then
    echo "Removing: $dir"
    rm -rf "$dir"
  fi
done

# Cleanup knowledge base
find data/knowledge_base -type d -mtime +$DAYS -maxdepth 1 | while read dir; do
  if [ "$dir" != "data/knowledge_base/default" ]; then
    echo "Removing: $dir"
    rm -rf "$dir"
  fi
done

echo "✅ Cleanup completed"
```

**Uso**:
```bash
chmod +x scripts/cleanup_old_profiles.sh
./scripts/cleanup_old_profiles.sh 90  # Rimuovi profili > 90 giorni
```

### Script 3: Test End-to-End Completo

```bash
#!/bin/bash
# File: scripts/test_e2e.sh

BRAND_NAME=${1:-TestBrand}
WEBSITE=${2:-https://testbrand.com}

echo "=== E2E TEST: $BRAND_NAME ==="

# 1. Start onboarding
echo "1. Starting onboarding..."
SESSION_ID=$(curl -s -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d "{
    \"brand_name\": \"$BRAND_NAME\",
    \"website\": \"$WEBSITE\",
    \"goal\": \"article\",
    \"user_email\": \"test@test.com\"
  }" | jq -r '.session_id')

echo "Session ID: $SESSION_ID"

# 2. Wait for snapshot
echo "2. Waiting for snapshot (40s)..."
sleep 40

# 3. Get snapshot
echo "3. Fetching snapshot..."
curl -s "http://localhost:8001/api/v1/onboarding/$SESSION_ID" | jq '.snapshot.company.name'

# 4. Submit answers
echo "4. Submitting answers..."
curl -s -X POST "http://localhost:8001/api/v1/onboarding/$SESSION_ID/answers" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "q1": "LinkedIn, email, blog",
      "q2": "Increase brand awareness",
      "q3": true
    }
  }' | jq '.state'

# 5. Execute workflow
echo "5. Executing CGS workflow..."
curl -s -X POST "http://localhost:8001/api/v1/onboarding/$SESSION_ID/execute" | jq '.state'

# 6. Wait for completion
echo "6. Waiting for completion (30s)..."
sleep 30

# 7. Get result
echo "7. Fetching result..."
curl -s "http://localhost:8001/api/v1/onboarding/$SESSION_ID" | jq '{
  state,
  profile_name,
  content_title,
  word_count,
  workflow_metrics
}'

# 8. Verify profile created
echo "8. Verifying profile..."
PROFILE_NAME=$(echo "$BRAND_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
ls -la "data/profiles/$PROFILE_NAME/"
ls -la "data/knowledge_base/$PROFILE_NAME/"

echo "=== TEST COMPLETED ==="
```

**Uso**:
```bash
chmod +x scripts/test_e2e.sh
./scripts/test_e2e.sh "MyBrand" "https://mybrand.com"
```

---

**Fine Esempi Pratici**

Per riferimenti completi, vedi:
- [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) - Piano completo
- [IMPLEMENTATION_CODE.md](IMPLEMENTATION_CODE.md) - Codice dettagliato

