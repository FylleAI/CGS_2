# 🗺️ ROADMAP IMPLEMENTAZIONE: Ottimizzazione Profili CGS per Onboarding

**Versione**: 1.0  
**Data**: 2025-10-14  
**Autore**: CGS Team  
**Status**: 📋 Planning

---

## 📋 INDICE

1. [Obiettivo](#obiettivo)
2. [Analisi Situazione Attuale](#analisi-situazione-attuale)
3. [Priorità 1: Essenziale](#priorità-1-essenziale-2-3-ore)
4. [Priorità 2: Miglioramento](#priorità-2-miglioramento-1-2-giorni)
5. [Priorità 3: Ottimizzazione](#priorità-3-ottimizzazione-3-5-giorni)
6. [Timeline](#timeline-implementazione)
7. [Testing](#strategia-di-test)
8. [Metriche](#metriche-di-successo)
9. [Rischi](#rischi-e-mitigazioni)

---

## 🎯 OBIETTIVO

Trasformare il sistema da **"agent generici"** a **"agent brand-specific"** per garantire contenuti perfettamente allineati al brand di ogni cliente onboardato.

### Problema Attuale

```
Onboarding → CGS Payload ✅
  ↓
CGS riceve payload ✅
  ↓
Cerca agent "default" ⚠️
  ↓
Agent disattivati → Usa fallback generici ⚠️
  ↓
Agent generici senza brand context ⚠️
  ↓
Contenuto generato ma generico ⚠️
```

### Obiettivo Finale

```
Onboarding → CGS Payload + Snapshot ✅
  ↓
CGS riceve payload ✅
  ↓
Crea/usa profilo brand-specific ✅
  ↓
Agent attivi con brand context ✅
  ↓
Agent accedono knowledge base ✅
  ↓
Contenuto brand-aligned e personalizzato ✅
```

---

## 📊 ANALISI SITUAZIONE ATTUALE

### ✅ Cosa Funziona

- Integrazione Onboarding → CGS: **100% funzionante**
- Payload construction: **Tutte le info passate correttamente**
- Workflow execution: **4 agent, 4 task, 100% success rate**
- Snapshot generation: **Perplexity + Gemini/Vertex AI operativi**

### ⚠️ Problemi Identificati

1. **Agent Disattivati**: Profilo "default" ha 7/8 agent con `is_active: false`
2. **Fallback Generici**: Sistema usa agent globali senza brand context
3. **RAG Non Funziona**: Nessun client "default" in tabella Supabase `clients`
4. **Brand Alignment Mancante**: Contenuto generico invece che brand-specific

### 📈 Evidenze dai Log

```
WARNING: Client-specific agent 'rag_specialist' is inactive (is_active=false); skipping
WARNING: Using global agent 'rag_specialist' instead of client-specific for profile 'default'

ERROR: RAG ERROR: Failed to retrieve content for default: 
{'message': 'Cannot coerce the result to a single JSON object', 
 'code': 'PGRST116', 
 'details': 'The result contains 0 rows'}
```

---

## 🔥 PRIORITÀ 1: ESSENZIALE (2-3 ore)

**Obiettivo**: Far funzionare il sistema base con agent attivi e RAG operativo.

### Task 1.1: Attivare Agent nel Profilo "default"

**Tempo stimato**: 2 ore  
**Complessità**: 🟢 Bassa  
**Impatto**: 🔴 Alto

#### File da Modificare

```
data/profiles/default/agents/
├── rag_specialist.yaml                    → is_active: false → true
├── copywriter.yaml                        → is_active: false → true  
├── enhanced_article_writer.yaml           → is_active: false → true
├── perplexity_researcher.yaml             → is_active: false → true
├── enhanced_article_compliance_specialist → is_active: false → true
└── web_searcher.yaml                      → is_active: false → true
```

#### Procedura

1. **Aprire ogni file YAML**:
   ```bash
   cd data/profiles/default/agents/
   ```

2. **Modificare il campo `is_active`**:
   ```yaml
   # Prima
   is_active: false
   
   # Dopo
   is_active: true
   ```

3. **Verificare sintassi YAML**:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('rag_specialist.yaml'))"
   ```

4. **Riavviare CGS backend**:
   ```bash
   # Terminare processo corrente (CTRL+C)
   python3 -m uvicorn api.rest.main:app --host 0.0.0.0 --port 8000 --reload
   ```

#### Test di Verifica

```bash
# Test 1: Verificare agent caricati
curl -X POST http://localhost:8000/api/v1/content/generate \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "enhanced_article",
    "client_profile": "default",
    "topic": "Test topic",
    "target_audience": "general"
  }'

# Verificare nei log CGS:
# ✅ "Using client-specific agent 'rag_specialist'"
# ❌ "Using global agent" (non dovrebbe più apparire)
```

#### Risultato Atteso

- ✅ 0 warning "Using global agent"
- ✅ Agent specifici attivi e utilizzati
- ✅ Workflow usa configurazione profilo default

---

### Task 1.2: Creare Entry "default" in Tabella `clients` Supabase

**Tempo stimato**: 1 ora  
**Complessità**: 🟢 Bassa  
**Impatto**: 🔴 Alto

#### Prerequisiti

- Accesso a Supabase dashboard
- Credenziali admin database

#### Procedura

1. **Accedere a Supabase**:
   ```
   https://app.supabase.com/project/iimymnlepgilbuoxnkqa
   ```

2. **Aprire SQL Editor**:
   - Menu laterale → SQL Editor
   - New Query

3. **Verificare struttura tabella** (opzionale):
   ```sql
   SELECT column_name, data_type, is_nullable
   FROM information_schema.columns 
   WHERE table_name = 'clients'
   ORDER BY ordinal_position;
   ```

4. **Inserire entry "default"**:
   ```sql
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
   );
   ```

5. **Verificare inserimento**:
   ```sql
   SELECT id, name, display_name, rag_enabled, created_at
   FROM clients 
   WHERE name = 'default';
   ```

#### Test di Verifica

```bash
# Test 1: RAG retrieval
curl -X GET "http://localhost:8000/api/v1/knowledge-base/clients/default/documents"

# Test 2: Verificare log CGS durante workflow
# ✅ "RAG RETRIEVAL: Accessing knowledge base for client 'default'" → SUCCESS
# ❌ "RAG ERROR: Failed to retrieve content" (non dovrebbe più apparire)
```

#### Risultato Atteso

- ✅ Entry "default" presente in tabella clients
- ✅ RAG tool funzionante (no errori "Cannot coerce result")
- ✅ Agent possono recuperare brand info dal database

---

### Checklist Priorità 1

- [ ] Tutti gli agent in `data/profiles/default/agents/` hanno `is_active: true`
- [ ] CGS backend riavviato
- [ ] Entry "default" creata in Supabase `clients` table
- [ ] Test workflow completato senza warning
- [ ] Test RAG completato senza errori
- [ ] Log verificati: agent specifici utilizzati

---

## 🚀 PRIORITÀ 2: MIGLIORAMENTO (1-2 giorni)

**Obiettivo**: Creare profili dinamici per ogni brand e popolare knowledge base.

### Task 2.1: Creare Profili Dinamici per Ogni Brand

**Tempo stimato**: 8 ore  
**Complessità**: 🟡 Media  
**Impatto**: 🔴 Alto

#### Architettura

```
onboarding/application/use_cases/
└── create_client_profile.py  (NUOVO)

Flusso:
1. Onboarding completa snapshot
2. Crea profilo CGS dinamico da snapshot
3. Popola tabella clients in Supabase
4. Copia agent template da "default" a nuovo profilo
5. Personalizza agent con brand info
6. Usa nuovo profilo per generazione contenuto
```

#### File da Creare

**File 1**: `onboarding/application/use_cases/create_client_profile.py`

Vedi sezione [Implementazione Dettagliata - Task 2.1](#implementazione-dettagliata-task-21) per il codice completo.

**File 2**: Modificare `onboarding/application/use_cases/execute_onboarding.py`

Aggiungere dopo synthesis snapshot:

```python
# Crea profilo CGS dinamico
from onboarding.application.use_cases.create_client_profile import CreateClientProfileUseCase

create_profile_uc = CreateClientProfileUseCase(self.settings)
profile_result = await create_profile_uc.execute(
    snapshot=snapshot,
    brand_name=session.brand_name,
)

# Usa il nuovo profilo invece di "default"
payload = self.payload_builder.build_payload(
    session_id=session_id,
    trace_id=session.trace_id,
    snapshot=snapshot,
    goal=session.goal,
    client_profile=profile_result["profile_name"],  # ← Profilo dinamico
)
```

#### Test di Verifica

```bash
# Test 1: Creare nuova sessione onboarding
curl -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "TestBrand",
    "website": "https://testbrand.com",
    "goal": "linkedin_post",
    "user_email": "test@testbrand.com"
  }'

# Aspettare completamento (30s)

# Test 2: Verificare directory profilo creata
ls -la data/profiles/testbrand/
ls -la data/profiles/testbrand/agents/

# Test 3: Verificare entry Supabase
# SQL Editor:
SELECT * FROM clients WHERE name = 'testbrand';

# Test 4: Verificare agent personalizzati
cat data/profiles/testbrand/agents/copywriter.yaml
# Cercare: "BRAND CONTEXT" nel system_message
```

#### Risultato Atteso

- ✅ Directory `data/profiles/{brand_name}/` creata
- ✅ 5+ agent YAML copiati e personalizzati
- ✅ Entry in Supabase `clients` table
- ✅ Payload CGS usa `client_profile="{brand_name}"`
- ✅ Agent contengono brand context nel system_message

---

### Task 2.2: Popolare Knowledge Base con Snapshot Info

**Tempo stimato**: 4 ore  
**Complessità**: 🟡 Media  
**Impatto**: 🟡 Medio

#### File da Creare

**File**: `onboarding/application/use_cases/populate_knowledge_base.py`

Vedi sezione [Implementazione Dettagliata - Task 2.2](#implementazione-dettagliata-task-22) per il codice completo.

#### Documenti Creati

Per ogni brand, vengono creati 5 documenti markdown:

1. **company_overview.md** - Info azienda, industry, differentiators
2. **brand_voice.md** - Tone, style guidelines, CTA preferences
3. **target_audience.md** - Primary/secondary audience, pain points
4. **key_messages.md** - Core messages, positioning
5. **offerings.md** - Prodotti e servizi chiave

#### Integrazione

```python
# In execute_onboarding.py, dopo create_client_profile:

from onboarding.application.use_cases.populate_knowledge_base import PopulateKnowledgeBaseUseCase

populate_kb_uc = PopulateKnowledgeBaseUseCase(self.settings)
kb_result = await populate_kb_uc.execute(
    profile_name=profile_result["profile_name"],
    snapshot=snapshot,
)
```

#### Test di Verifica

```bash
# Test 1: Verificare documenti creati
ls -la data/knowledge_base/testbrand/

# Dovrebbe mostrare:
# - company_overview.md
# - brand_voice.md
# - target_audience.md
# - key_messages.md
# - offerings.md

# Test 2: Verificare contenuto documento
cat data/knowledge_base/testbrand/brand_voice.md

# Test 3: Test RAG retrieval
curl -X GET "http://localhost:8000/api/v1/knowledge-base/clients/testbrand/documents"
```

#### Risultato Atteso

- ✅ 4-5 documenti markdown creati per brand
- ✅ Contenuto accurato da snapshot
- ✅ RAG tool può recuperare documenti
- ✅ Agent hanno accesso a brand knowledge

---

### Checklist Priorità 2

- [ ] `create_client_profile.py` implementato
- [ ] `populate_knowledge_base.py` implementato
- [ ] `execute_onboarding.py` modificato per usare nuovi use case
- [ ] Test creazione profilo dinamico completato
- [ ] Test population KB completato
- [ ] Documentazione aggiornata in README.md

---

## ⚡ PRIORITÀ 3: OTTIMIZZAZIONE (3-5 giorni)

**Obiettivo**: Context injection runtime e caching per performance.

### Task 3.1: Configurare Agent con Context Specifico dal Snapshot

**Tempo stimato**: 8 ore  
**Complessità**: 🟡 Media  
**Impatto**: 🟡 Medio

#### Approccio

Context Injection Runtime - invece di modificare file YAML, inietta context dinamicamente a runtime.

#### File da Modificare

**File**: `core/infrastructure/factories/agent_factory.py`

Aggiungere metodo:

```python
def inject_snapshot_context(
    self,
    agent: Agent,
    snapshot: CompanySnapshot,
) -> Agent:
    """Inietta context snapshot nell'agent runtime."""
    
    # Costruisci context string
    context = f"""
BRAND CONTEXT (from onboarding):
Company: {snapshot.company.name}
Industry: {snapshot.company.industry}
Voice Tone: {snapshot.voice.tone}
Target Audience: {snapshot.audience.primary}

Key Messages:
{chr(10).join(f'- {m}' for m in snapshot.insights.key_messages[:3])}

Style Guidelines:
{chr(10).join(f'- {g}' for g in snapshot.voice.style_guidelines[:3])}

Differentiators:
{chr(10).join(f'- {d}' for d in snapshot.company.differentiators[:3])}
"""
    
    # Inietta nel system_message
    enhanced_system_message = f"{agent.system_message}\n\n{context}"
    
    # Crea nuovo agent con context
    return Agent(
        name=agent.name,
        role=agent.role,
        goal=agent.goal,
        backstory=agent.backstory,
        system_message=enhanced_system_message,
        tools=agent.tools,
        examples=agent.examples,
        metadata={**agent.metadata, "snapshot_context_injected": True},
        is_active=agent.is_active,
    )
```

#### Integrazione in Workflow

Modificare workflow handler per iniettare context prima di eseguire agent:

```python
# In workflow handler, prima di eseguire agent:

if "company_snapshot" in context:
    snapshot = context["company_snapshot"]
    agent = agent_factory.inject_snapshot_context(agent, snapshot)
```

#### Risultato Atteso

- ✅ Agent ricevono context brand dinamicamente
- ✅ No bisogno di ricreare agent per ogni brand
- ✅ Flessibilità massima per A/B testing

---

### Task 3.2: Implementare Caching Profili per Performance

**Tempo stimato**: 4 ore  
**Complessità**: 🟡 Media  
**Impatto**: 🟢 Basso (ma importante per scala)

#### File da Creare

**File**: `onboarding/infrastructure/cache/profile_cache.py`

Vedi sezione [Implementazione Dettagliata - Task 3.2](#implementazione-dettagliata-task-32) per il codice completo.

#### Strategia

- **In-memory cache** con TTL (24 ore default)
- **Fallback a Supabase** se cache miss
- **Invalidazione automatica** su TTL expiry

#### Integrazione

```python
# In execute_onboarding.py:

from onboarding.infrastructure.cache.profile_cache import ProfileCache

# Check se profilo esiste già
profile_cache = ProfileCache(self.settings)
existing_profile = await profile_cache.get_profile(session.brand_name)

if existing_profile:
    # Riusa profilo esistente
    profile_name = existing_profile["name"]
else:
    # Crea nuovo profilo
    create_profile_uc = CreateClientProfileUseCase(self.settings)
    profile_result = await create_profile_uc.execute(...)
    
    # Cache it
    await profile_cache.set_profile(
        session.brand_name,
        profile_result,
    )
    profile_name = profile_result["profile_name"]
```

#### Risultato Atteso

- ✅ Cache hit rate > 80% per brand ricorrenti
- ✅ Tempo lookup profilo < 100ms
- ✅ Riduzione chiamate Supabase del 70-80%

---

### Checklist Priorità 3

- [ ] Context injection implementato in `agent_factory.py`
- [ ] `profile_cache.py` implementato
- [ ] Integrazione cache in `execute_onboarding.py`
- [ ] Performance test completati
- [ ] Monitoring configurato (opzionale)

---

## 📅 TIMELINE IMPLEMENTAZIONE

### Settimana 1: Priorità 1 (Essenziale)

**Giorno 1** (5 ore totali)
- ⏰ 09:00-11:00: Task 1.1 - Attivare agent profilo default
- ⏰ 11:00-12:00: Task 1.2 - Creare entry Supabase
- ⏰ 14:00-16:00: Test integrazione completa
- ⏰ 16:00-17:00: Documentazione e commit

**Deliverable**: Sistema base funzionante con agent attivi e RAG operativo

---

### Settimana 2: Priorità 2 (Miglioramento)

**Giorno 1-2** (16 ore totali)
- Task 2.1 - Implementazione profili dinamici
  - Giorno 1: Creazione `create_client_profile.py` (8h)
  - Giorno 2: Integrazione e testing (8h)

**Giorno 3** (8 ore)
- Task 2.2 - Knowledge base population
  - Mattina: Implementazione `populate_knowledge_base.py` (4h)
  - Pomeriggio: Testing e debugging (4h)

**Giorno 4** (8 ore)
- Test end-to-end completo
- Bug fixing
- Performance tuning

**Giorno 5** (8 ore)
- Documentazione completa
- Code review
- Deployment su staging

**Deliverable**: Profili dinamici funzionanti con KB popolata

---

### Settimana 3: Priorità 3 (Ottimizzazione)

**Giorno 1-2** (16 ore)
- Task 3.1 - Context injection
  - Giorno 1: Implementazione (8h)
  - Giorno 2: Testing e refinement (8h)

**Giorno 3** (8 ore)
- Task 3.2 - Profile caching
  - Implementazione e testing

**Giorno 4-5** (16 ore)
- Performance testing
- Load testing
- Optimization
- Final documentation

**Deliverable**: Sistema ottimizzato production-ready

---

## 🧪 STRATEGIA DI TEST

### Test Priorità 1

```bash
# Test Suite 1: Agent Attivi
curl -X POST http://localhost:8000/api/v1/content/generate \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "enhanced_article",
    "client_profile": "default",
    "topic": "AI in Marketing",
    "target_audience": "Marketing professionals"
  }'

# Verificare log:
# ✅ "Using client-specific agent 'rag_specialist'"
# ✅ "Using client-specific agent 'copywriter'"
# ❌ NO "Using global agent"

# Test Suite 2: RAG Funzionante
# Verificare log durante workflow:
# ✅ "RAG RETRIEVAL: Accessing knowledge base for client 'default'" → SUCCESS
# ❌ NO "RAG ERROR: Failed to retrieve content"
```

### Test Priorità 2

```bash
# Test Suite 1: Profilo Dinamico Creato
SESSION_ID=$(curl -s -X POST http://localhost:8001/api/v1/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "TestBrand",
    "website": "https://testbrand.com",
    "goal": "linkedin_post",
    "user_email": "test@testbrand.com"
  }' | jq -r '.session_id')

# Aspettare 30s per completamento
sleep 30

# Verificare directory
ls -la data/profiles/testbrand/agents/
# Aspettato: 5+ file YAML

# Test Suite 2: Entry Supabase
# SQL:
SELECT * FROM clients WHERE name = 'testbrand';
# Aspettato: 1 row

# Test Suite 3: Knowledge Base Popolata
ls -la data/knowledge_base/testbrand/
# Aspettato: 4-5 file .md
```

### Test Priorità 3

```bash
# Test Suite 1: Context Injection
# Verificare log agent durante esecuzione:
# Cercare nel system_message: "BRAND CONTEXT (from onboarding)"

# Test Suite 2: Cache Hit
# Primo onboarding brand "TestBrand2"
curl -X POST http://localhost:8001/api/v1/onboarding/start \
  -d '{"brand_name": "TestBrand2", ...}'

# Secondo onboarding stesso brand
curl -X POST http://localhost:8001/api/v1/onboarding/start \
  -d '{"brand_name": "TestBrand2", ...}'

# Verificare log:
# ✅ "Profile found in cache for TestBrand2"
```

---

## 📊 METRICHE DI SUCCESSO

### Priorità 1: Baseline Funzionante

| Metrica | Target | Misurazione |
|---------|--------|-------------|
| Errori RAG | 0 | Log grep "RAG ERROR" |
| Warning fallback agent | 0 | Log grep "Using global agent" |
| Agent attivi profilo default | 100% (7/7) | YAML files check |
| Workflow success rate | 100% | Test execution |

### Priorità 2: Profili Dinamici

| Metrica | Target | Misurazione |
|---------|--------|-------------|
| Profili creati per brand | 1:1 | Directory count |
| Documenti KB per brand | 5+ | File count |
| Tempo creazione profilo | < 5s | Performance log |
| Entry Supabase per brand | 1 | SQL count |

### Priorità 3: Performance

| Metrica | Target | Misurazione |
|---------|--------|-------------|
| Context injection rate | 100% | Log verification |
| Cache hit rate | > 80% | Cache metrics |
| Tempo lookup profilo | < 100ms | Performance log |
| Riduzione chiamate Supabase | > 70% | API metrics |

---

## 🚨 RISCHI E MITIGAZIONI

### Rischio 1: Conflitti Agent Multipli

**Problema**: Più profili con stesso agent name causano conflitti  
**Probabilità**: 🟡 Media  
**Impatto**: 🔴 Alto  

**Mitigazione**:
- Namespace agent per profilo: `{profile_name}_{agent_name}`
- Metadata agent include `client_profile`
- Agent factory risolve per profilo specifico

### Rischio 2: Esplosione Storage KB

**Problema**: Troppi documenti KB occupano storage  
**Probabilità**: 🟢 Bassa  
**Impatto**: 🟡 Medio  

**Mitigazione**:
- Cleanup automatico profili inattivi > 90 giorni
- Compressione documenti vecchi
- Monitoring storage usage

### Rischio 3: Cache Stale Data

**Problema**: Cache con dati obsoleti dopo update profilo  
**Probabilità**: 🟡 Media  
**Impatto**: 🟡 Medio  

**Mitigazione**:
- TTL 24h per auto-refresh
- Invalidazione manuale su update profilo
- Versioning profili

### Rischio 4: Performance Degradation

**Problema**: Creazione profili rallenta onboarding  
**Probabilità**: 🟢 Bassa  
**Impatto**: 🟡 Medio  

**Mitigazione**:
- Creazione profilo asincrona (background task)
- Cache aggressiva
- Profili pre-creati per brand comuni

---

## 📝 CHECKLIST PRE-DEPLOYMENT

### Priorità 1: Baseline

- [ ] Tutti gli agent in `data/profiles/default/agents/` hanno `is_active: true`
- [ ] Entry "default" creata in Supabase `clients` table
- [ ] CGS backend riavviato e funzionante
- [ ] Test workflow completato senza warning
- [ ] Test RAG completato senza errori
- [ ] Log verificati: agent specifici utilizzati
- [ ] Documentazione aggiornata

### Priorità 2: Profili Dinamici

- [ ] `create_client_profile.py` implementato e testato
- [ ] `populate_knowledge_base.py` implementato e testato
- [ ] `execute_onboarding.py` modificato e testato
- [ ] Test creazione profilo dinamico: PASS
- [ ] Test KB population: PASS
- [ ] Test end-to-end con nuovo brand: PASS
- [ ] Code review completata
- [ ] Documentazione API aggiornata

### Priorità 3: Ottimizzazione

- [ ] Context injection implementato in `agent_factory.py`
- [ ] `profile_cache.py` implementato
- [ ] Integrazione cache in `execute_onboarding.py`
- [ ] Performance test: cache hit rate > 80%
- [ ] Performance test: lookup time < 100ms
- [ ] Load test: 100 concurrent requests
- [ ] Monitoring configurato (opzionale)
- [ ] Documentazione performance tuning

---

## 🔗 RIFERIMENTI

### Documentazione Correlata

- [README.md](README.md) - Setup e quickstart
- [QUICKSTART.md](QUICKSTART.md) - Guida rapida
- [INTEGRATION_TEST_GUIDE.md](INTEGRATION_TEST_GUIDE.md) - Test integrazione
- [API_REFERENCE.md](API_REFERENCE.md) - Riferimento API (da creare)

### File Chiave

- `onboarding/application/use_cases/execute_onboarding.py` - Orchestrazione workflow
- `onboarding/application/builders/payload_builder.py` - Costruzione payload CGS
- `core/infrastructure/factories/agent_factory.py` - Factory agent CGS
- `data/profiles/default/agents/*.yaml` - Configurazione agent

### Risorse Esterne

- [Supabase Dashboard](https://app.supabase.com/project/iimymnlepgilbuoxnkqa)
- [GitHub Repository](https://github.com/FylleAI/CGS_2)
- [Clean Architecture Guide](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

**Ultimo aggiornamento**: 2025-10-14  
**Prossima revisione**: Dopo completamento Priorità 1


