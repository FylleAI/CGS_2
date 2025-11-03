# 🚀 Onboarding → Cards Service Redirect

**Data**: 2025-11-03  
**Obiettivo**: Implementare redirect automatico da Onboarding Service a Cards Service dopo il completamento dell'onboarding

---

## 📋 Architettura

### **Flusso Completo**

```
┌─────────────────────────────────────────────────────────────┐
│ ONBOARDING SERVICE                                          │
│ 1. User inserisce nome azienda                              │
│ 2. Perplexity ricerca informazioni                          │
│ 3. Gemini sintetizza Company Snapshot                       │
│ 4. User risponde a domande personalizzate                   │
│ 5. Backend arricchisce snapshot con risposte                │
│ 6. Backend → POST snapshot a Cards Service API              │
│ 7. Frontend → REDIRECT automatico a Cards Service           │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ POST /api/v1/cards/batch
                          │ (Company Snapshot)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ CARDS SERVICE (Microservizio separato)                      │
│ 1. Riceve Company Snapshot                                  │
│ 2. Normalizza dati                                          │
│ 3. Fa ricerche aggiuntive (se necessario)                   │
│ 4. Crea 4 Cards (Company, Audience, Voice, Insights)        │
│ 5. Salva Cards in DB                                        │
│ 6. Ritorna card_ids                                         │
│                                                              │
│ Frontend Cards Service:                                     │
│ - Visualizza le Cards create                                │
│ - Permette editing e gestione                               │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Modifiche Implementate

### **1. Backend - Response Model**

**File**: `onboarding/api/models.py`

```python
class SubmitAnswersResponse(BaseModel):
    """Response from submitting answers."""
    
    session_id: UUID
    state: SessionState
    message: str
    snapshot: Optional[CompanySnapshot] = None
    card_ids: Optional[List[str]] = None
    cards_created: Optional[int] = None
    partial: Optional[bool] = None
    
    # ✨ NEW: URL for automatic redirect
    cards_service_url: Optional[str] = None
```

---

### **2. Backend - Settings**

**File**: `onboarding/config/settings.py`

```python
# Cards API integration
cards_api_url: str = Field(default="http://localhost:8002", env="CARDS_API_URL")
cards_frontend_url: str = Field(default="http://localhost:3002", env="CARDS_FRONTEND_URL")
```

---

### **3. Backend - Endpoint**

**File**: `onboarding/api/endpoints.py`

```python
# Cards API configuration
CARDS_API_URL = os.getenv("CARDS_API_URL", "http://localhost:8002")
CARDS_FRONTEND_URL = os.getenv("CARDS_FRONTEND_URL", "http://localhost:3002")

@router.post("/{session_id}/answers", response_model=SubmitAnswersResponse)
async def submit_answers(...):
    # ... existing code ...
    
    # Build Cards Service frontend URL for redirect
    cards_service_url = f"{CARDS_FRONTEND_URL}/cards?session_id={session_id}&tenant_id={tenant_id}"
    
    response = SubmitAnswersResponse(
        session_id=session.session_id,
        state=session.state,
        message=f"Cards created successfully! Created {created_count} cards.",
        snapshot=session.snapshot,
        card_ids=[str(cid) for cid in card_ids],
        cards_created=created_count,
        partial=partial,
        cards_service_url=cards_service_url,  # ✨ NEW
    )
    
    return response
```

---

### **4. Frontend - TypeScript Types**

**File**: `onboarding-frontend/src/types/onboarding.ts`

```typescript
export interface SubmitAnswersResponse {
  session_id: string;
  state: SessionState;
  snapshot?: CompanySnapshot;
  card_ids?: string[];
  cards_created?: number;
  partial?: boolean;
  cards_service_url?: string;  // ✨ NEW
  // ... other fields
}
```

---

### **5. Frontend - Redirect Logic**

**File**: `onboarding-frontend/src/hooks/useOnboarding.ts`

```typescript
onSuccess: async (data) => {
  // Update snapshot
  if (data.snapshot) {
    setSnapshot(data.snapshot);
    console.log('✅ Snapshot updated with user answers:', data.snapshot);
  }

  // ✨ NEW: Automatic redirect to Cards Service
  if (data.cards_service_url) {
    console.log('🚀 Redirecting to Cards Service:', data.cards_service_url);
    
    toast.success('Onboarding complete! Redirecting to your cards...', {
      duration: 2000,
    });

    // Wait 2 seconds for user to see the success message, then redirect
    setTimeout(() => {
      window.location.href = data.cards_service_url!;
    }, 2000);

    setLoading(false);
    return;
  }

  // ✨ LEGACY PATH: If no cards_service_url, show results in Onboarding frontend
  console.warn('⚠️ No cards_service_url in response - using legacy results view');
  // ... existing code for backward compatibility ...
}
```

---

### **6. Environment Variables**

**File**: `.env`

```bash
# Cards Service Integration
# Backend API URL (for creating cards)
CARDS_API_URL=http://localhost:8002
# Frontend URL (for redirecting users to view cards)
CARDS_FRONTEND_URL=http://localhost:3002
```

**File**: `onboarding/.env.example`

```bash
# =============================================================================
# CARDS SERVICE INTEGRATION
# =============================================================================
CARDS_API_URL=http://localhost:8002
CARDS_FRONTEND_URL=http://localhost:3002
```

---

## 🎯 Comportamento

### **Scenario 1: Cards Service Disponibile (Produzione)**

1. User completa onboarding
2. Backend crea snapshot arricchito
3. Backend → POST a Cards Service API
4. Cards Service crea 4 cards
5. Backend ritorna `cards_service_url`
6. Frontend mostra toast "Redirecting to your cards..."
7. **Dopo 2 secondi → Redirect automatico a Cards Service frontend**
8. User vede le Cards nel frontend del Cards Service

### **Scenario 2: Cards Service NON Disponibile (Development)**

1. User completa onboarding
2. Backend crea snapshot arricchito
3. Backend **NON chiama** Cards Service (client non disponibile)
4. Backend ritorna `cards_service_url = null`
5. Frontend **NON fa redirect**
6. Frontend mostra **legacy results view** (OnboardingResultsGrid)
7. User vede le card legacy nel frontend di Onboarding

---

## 🔧 Testing

### **Test 1: Verifica Backend Response**

```bash
# Completa un onboarding e verifica la response
curl -X POST http://localhost:8001/api/v1/onboarding/{session_id}/answers \
  -H "Content-Type: application/json" \
  -d '{"answers": {...}}'

# Verifica che la response contenga:
# - cards_service_url: "http://localhost:3002/cards?session_id=xxx&tenant_id=yyy"
```

### **Test 2: Verifica Redirect Frontend**

1. Apri http://localhost:3001
2. Completa onboarding
3. Verifica console browser:
   - `✅ Snapshot updated with user answers:`
   - `🚀 Redirecting to Cards Service: http://localhost:3002/cards?...`
4. Verifica toast: "Onboarding complete! Redirecting to your cards..."
5. Verifica redirect dopo 2 secondi

### **Test 3: Verifica Fallback (Cards Service Down)**

1. Ferma Cards Service (se in esecuzione)
2. Completa onboarding
3. Verifica console browser:
   - `⚠️ No cards_service_url in response - using legacy results view`
4. Verifica che venga mostrato `OnboardingResultsGrid` (legacy)

---

## 📝 Note Importanti

### **1. Componenti Legacy NON Rimossi**

I componenti legacy (`OnboardingResultsGrid`, card renderers) **NON sono stati rimossi** perché:
- Servono come **fallback** quando Cards Service non è disponibile
- Utili per **development** e **testing**
- Permettono **backward compatibility**

### **2. Idempotency**

Il backend usa `idempotency_key` per evitare duplicati:
```python
idem_key = idempotency_key or f"onboarding-{session_id}-batch"
```

### **3. Query Parameters**

L'URL di redirect include:
- `session_id`: Per recuperare i dati della sessione
- `tenant_id`: Per multi-tenancy

Esempio:
```
http://localhost:3002/cards?session_id=7e678a52-724a-445e-9f74-cfd35760d73d&tenant_id=7e678a52-724a-445e-9f74-cfd35760d73d
```

---

## 🚀 Prossimi Passi

1. **Implementare Cards Service Frontend**
   - Creare route `/cards` che accetta `session_id` e `tenant_id`
   - Recuperare cards dal backend usando i query params
   - Visualizzare le 4 cards (Company, Audience, Voice, Insights)

2. **Testing End-to-End**
   - Testare flusso completo con Cards Service in esecuzione
   - Verificare che il redirect funzioni correttamente
   - Testare fallback quando Cards Service è down

3. **Monitoring**
   - Aggiungere metriche per redirect success/failure
   - Log per debugging del flusso

---

## ✅ Checklist

- [x] Backend ritorna `cards_service_url` in response
- [x] Frontend fa redirect automatico quando `cards_service_url` è presente
- [x] Frontend mostra legacy view quando `cards_service_url` è assente
- [x] Environment variables configurate
- [x] Backward compatibility mantenuta
- [ ] Cards Service frontend implementato
- [ ] Test end-to-end completati
- [ ] Documentazione aggiornata

---

**Status**: ✅ **READY FOR TESTING**

Il codice è pronto. Quando il Cards Service frontend sarà disponibile su `http://localhost:3002/cards`, il redirect funzionerà automaticamente.

