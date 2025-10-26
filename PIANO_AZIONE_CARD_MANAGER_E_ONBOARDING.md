# Piano d'Azione: Risolvere Card Manager e Onboarding

## 🎯 Obiettivo Finale

Creare un flusso completo e funzionante:
```
Onboarding → CompanySnapshot → Card Service → Card Manager (Frontend) → Content Workflow
```

---

## 📍 PROBLEMA 1: Card Manager non vede le card

### Causa Root
- Card Service crea card in Supabase ✅
- Card Manager (frontend) non sa come leggerle
- Mismatch tra vecchio schema (PostgreSQL) e nuovo (Supabase)

### Soluzione

#### Step 1: Verificare Card Service API
```bash
# Test endpoint
curl http://localhost:8001/api/v1/cards?tenant_id=test-user@example.com

# Dovrebbe ritornare:
{
  "items": [
    {
      "id": "...",
      "card_type": "product",
      "title": "...",
      "content": {...}
    }
  ]
}
```

#### Step 2: Aggiornare Card Manager Frontend
**File**: `frontends/card-explorer/src/hooks/useCards.ts`

```typescript
// OLD: Legge da API locale
const response = await fetch(`/api/cards?tenant_id=${tenantId}`);

// NEW: Legge da Card Service
const response = await fetch(
  `http://localhost:8001/api/v1/cards?tenant_id=${tenantId}`
);
```

#### Step 3: Aggiornare API Config
**File**: `frontends/card-explorer/src/config/api.ts`

```typescript
export const API_BASE_URL = process.env.REACT_APP_API_URL || 
  'http://localhost:8001/api/v1';
```

#### Step 4: Aggiornare .env.example
```env
REACT_APP_API_URL=http://localhost:8001/api/v1
REACT_APP_TENANT_ID=test-user@example.com
```

---

## 📍 PROBLEMA 2: Onboarding mostra card vecchie

### Causa Root
- Onboarding non invia snapshot a Card Service
- Card Service non viene chiamato dopo onboarding
- Vecchio flusso ancora in uso

### Soluzione: Implementare CardExportPipeline

#### Step 1: Creare CardExportPipeline
**File**: `services/onboarding/application/card_export_pipeline.py`

```python
class CardExportPipeline:
    """Pipeline per esportare snapshot a Card Service"""
    
    def __init__(self, card_service_client: CardServiceClient):
        self.card_service = card_service_client
    
    async def export_snapshot(
        self, 
        tenant_id: str, 
        snapshot: CompanySnapshot
    ) -> List[CardSummary]:
        """
        Esporta snapshot a Card Service e riceve card create
        """
        # 1. Normalizza snapshot
        normalized = self._normalize_snapshot(snapshot)
        
        # 2. Invia a Card Service
        response = await self.card_service.create_cards_from_snapshot(
            tenant_id=tenant_id,
            snapshot=normalized
        )
        
        # 3. Ritorna CardSummary list
        return response.cards
    
    def _normalize_snapshot(self, snapshot: CompanySnapshot) -> dict:
        """Normalizza snapshot per Card Service"""
        return {
            "company": snapshot.company.dict(),
            "audience": snapshot.audience.dict(),
            "voice": snapshot.voice.dict(),
            "insights": snapshot.insights.dict(),
        }
```

#### Step 2: Integrare in Onboarding Flow
**File**: `services/onboarding/api/endpoints/onboarding.py`

```python
@router.post("/complete")
async def complete_onboarding(
    request: OnboardingCompleteRequest,
    pipeline: CardExportPipeline = Depends(get_card_export_pipeline),
):
    """Completa onboarding e esporta snapshot a Card Service"""
    
    # 1. Salva snapshot
    snapshot = await save_snapshot(request.snapshot)
    
    # 2. Esporta a Card Service
    cards = await pipeline.export_snapshot(
        tenant_id=request.tenant_id,
        snapshot=snapshot
    )
    
    # 3. Ritorna cards create
    return {
        "status": "completed",
        "snapshot_id": snapshot.id,
        "cards": cards,
    }
```

#### Step 3: Creare CardServiceClient
**File**: `services/onboarding/infrastructure/card_service_client.py`

```python
class CardServiceClient:
    """Client per comunicare con Card Service"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def create_cards_from_snapshot(
        self,
        tenant_id: str,
        snapshot: dict
    ) -> CardServiceResponse:
        """Crea card da snapshot"""
        response = await self.client.post(
            f"{self.base_url}/cards/onboarding/create-from-snapshot",
            params={"tenant_id": tenant_id},
            json=snapshot,
        )
        return CardServiceResponse(**response.json())
```

---

## 🔄 Flusso Completo Dopo Fix

```
1. User completa Onboarding
   ↓
2. Onboarding salva CompanySnapshot
   ↓
3. CardExportPipeline.export_snapshot()
   ↓
4. Card Service crea 4 card atomiche
   ↓
5. Card Manager legge card da Card Service API
   ↓
6. Frontend mostra card create
   ↓
7. User può editare card
   ↓
8. Content Workflow usa card come RAG context
```

---

## ✅ Checklist Implementazione

### FASE 1: Card Manager (Frontend)
- [ ] Aggiornare `useCards.ts` per leggere da Card Service
- [ ] Aggiornare `api.ts` con nuovo base URL
- [ ] Aggiornare `.env.example`
- [ ] Testare lettura card da Supabase

### FASE 2: CardExportPipeline (Backend)
- [ ] Creare `card_export_pipeline.py`
- [ ] Creare `card_service_client.py`
- [ ] Integrare in onboarding endpoint
- [ ] Aggiungere test

### FASE 3: Testing
- [ ] Test end-to-end: Onboarding → Card Service → Card Manager
- [ ] Verificare card visibili nel frontend
- [ ] Verificare card usate in Content Workflow

### FASE 4: Documentation
- [ ] Aggiornare README con nuovo flusso
- [ ] Aggiornare API documentation
- [ ] Aggiornare architecture guide

