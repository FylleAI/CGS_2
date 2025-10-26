# Analisi PR #30 e Flusso Attuale del Sistema

## 📋 Sommario della PR #30

**Titolo**: Fix onboarding compatibility and update tests  
**Autore**: MutenAI  
**Stato**: OPEN  
**Cambiamenti**: 396 file, +1558 -945 linee

### Obiettivi della PR:
1. **Compatibility shim** per tradurre payload legacy in nuovi domain models
2. **Relax contracts** per snapshot e card (legacy fixtures senza UUID)
3. **Align tests** con nuovi adapter e HTML validation

---

## 🏗️ Nuova Struttura Proposta (PR #30)

La PR propone una **riorganizzazione da `core/` a `services/`**:

```
OLD STRUCTURE:
├── core/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── card_service/
├── onboarding/
└── api/

NEW STRUCTURE (PR #30):
├── services/
│   ├── content_workflow/  (ex core/)
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── prompts/
│   ├── card_service/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── api/
│   └── onboarding/
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── api/
├── packages/
│   └── contracts/  (shared models)
└── api/
    └── rest/
```

### Vantaggi della nuova struttura:
- ✅ **Microservices-ready**: Ogni servizio è indipendente
- ✅ **Shared contracts**: `packages/contracts/` per modelli comuni
- ✅ **Clear boundaries**: Separazione netta tra servizi
- ✅ **Scalability**: Facile aggiungere nuovi servizi

---

## 🔄 Flusso End-to-End Proposto

```
1. USER COMPLETES ONBOARDING
   ↓
2. ONBOARDING SERVICE
   - Ricerca & sintesi snapshot
   - Genera CompanySnapshot (shared contract)
   ↓
3. CARD SERVICE (CardExportPipeline)
   - Riceve CompanySnapshot
   - CreateCardsFromSnapshotUseCase
   - Crea 4 card atomiche (Product, Persona, Campaign, Topic)
   - Ritorna CardSummary list + WorkflowContext
   ↓
4. CONTENT WORKFLOW SERVICE
   - Riceve WorkflowContext (snapshot + card + metadata)
   - AgentExecutor + Registry
   - Esegue workflow dinamico
   ↓
5. USER RECEIVES CONTENT
   - Contenuto generato + analytics
```

---

## ⚠️ PROBLEMI ATTUALI

### 1. **Card Manager non vede le card**
- ❌ Card create in Supabase ma non visibili nel frontend
- **Causa**: Mismatch tra vecchio e nuovo schema
- **Soluzione**: Aggiornare CardManager per leggere da Supabase REST API

### 2. **Onboarding mostra card vecchie**
- ❌ Onboarding non aggiornato per leggere nuove card
- **Causa**: Onboarding ancora usa vecchio flusso
- **Soluzione**: Implementare CardExportPipeline in Onboarding

### 3. **Struttura ancora mista**
- ❌ PR #30 non è stata mergiata
- ❌ Codice ancora in `core/` e `onboarding/` separati
- **Soluzione**: Completare migrazione a `services/`

---

## 📊 Stato Attuale vs Proposto

| Aspetto | ATTUALE | PROPOSTO (PR #30) |
|---------|---------|-------------------|
| Struttura | `core/` + `onboarding/` | `services/` |
| Card Service | Usa PostgreSQL diretto | Usa Supabase REST API ✅ |
| Shared Models | Nessuno | `packages/contracts/` |
| Onboarding → Card | Manuale | CardExportPipeline |
| Card → Workflow | Manuale | WorkflowContext |
| Frontend | Legge da API | Legge da Supabase |

---

## 🎯 Prossimi Passi Consigliati

### FASE 1: Completare migrazione Card Service (FATTO ✅)
- ✅ Migrare da PostgreSQL a Supabase REST API
- ✅ Implementare SupabaseCardRepository
- ✅ Aggiornare data access patterns
- ✅ Tutti i test passano

### FASE 2: Implementare CardExportPipeline (TODO)
- [ ] Creare CardExportPipeline in Onboarding
- [ ] Normalizzare CompanySnapshot
- [ ] Inviare snapshot a Card Service
- [ ] Ricevere CardSummary list

### FASE 3: Aggiornare Card Manager (TODO)
- [ ] Leggere card da Supabase REST API
- [ ] Mostrare card create da Onboarding
- [ ] Implementare card editing
- [ ] Sync con backend

### FASE 4: Completare PR #30 (TODO)
- [ ] Merge della PR #30
- [ ] Completare migrazione a `services/`
- [ ] Aggiornare tutti gli import
- [ ] Eseguire test suite completa

---

## 🔗 Contratti Condivisi (PR #30)

```python
# packages/contracts/

# Onboarding → Card Service
class CompanySnapshot(BaseModel):
    company: CompanyInfo
    audience: AudienceInfo
    voice: VoiceInfo
    insights: InsightsInfo

# Card Service → Frontend/Workflow
class CardSummary(BaseModel):
    id: UUID
    card_type: CardType
    title: str
    content: Dict[str, Any]

# Workflow Context
class WorkflowContext(BaseModel):
    snapshot: CompanySnapshot
    cards: List[CardSummary]
    metadata: Dict[str, Any]
```

---

## 📝 Raccomandazioni

1. **Priorità**: Completare FASE 2 (CardExportPipeline)
2. **Testing**: Aggiungere test per CardExportPipeline
3. **Documentation**: Aggiornare README con nuovo flusso
4. **Merge**: Preparare PR #30 per merge dopo FASE 2

