# 🎯 Cards Service - Requisiti di Implementazione

**Data**: 2025-11-03  
**Versione**: 1.0  
**Scopo**: Documentazione completa per implementare il Cards Service che riceve dati da Onboarding Service

---

## 📦 API Backend da Implementare

### **Endpoint**
```
POST /api/v1/cards/batch
```

### **Descrizione**
Riceve il Company Snapshot dall'Onboarding Service e crea 4 cards (Company, Audience Intelligence, Voice DNA, Strategic Insights).

---

## 📥 Request Format

### **Headers**
```http
Content-Type: application/json
X-Tenant-ID: 7e678a52-724a-445e-9f74-cfd35760d73d
X-Trace-ID: 7e678a52-724a-445e-9f74-cfd35760d73d
```

### **Request Body**
```json
{
  "company_snapshot": {
    "brand_name": "One Piece Products",
    "industry": "Anime Merchandise & Collectibles",
    "target_audience": "Anime fans, collectors, cosplayers aged 15-35",
    "pain_points": [
      "Finding authentic merchandise",
      "High shipping costs",
      "Limited edition availability"
    ],
    "key_offerings": [
      "Official licensed products",
      "Exclusive collectibles",
      "Pre-order system"
    ],
    "differentiators": [
      "Direct partnerships with licensors",
      "Global shipping network",
      "Authenticity guarantee"
    ],
    "clarifying_questions": [
      {
        "id": "q1",
        "question": "What is your primary product category?",
        "context": "To understand focus area"
      },
      {
        "id": "q2", 
        "question": "What is your average order value?",
        "context": "To tailor pricing strategy"
      },
      {
        "id": "q3",
        "question": "Do you offer international shipping?",
        "context": "To understand market reach"
      }
    ],
    "user_answers": {
      "q1": "Action figures and statues",
      "q2": "$50-150",
      "q3": "Yes, worldwide"
    }
  },
  "source_session_id": "7e678a52-724a-445e-9f74-cfd35760d73d",
  "created_by": "onboarding-service",
  "idempotency_key": "onboarding-7e678a52-724a-445e-9f74-cfd35760d73d-batch"
}
```

### **Campi Obbligatori**
- `company_snapshot` (object): Snapshot completo dell'azienda
  - `brand_name` (string): Nome dell'azienda
  - `industry` (string): Settore di appartenenza
  - `target_audience` (string): Pubblico target
  - `pain_points` (array): Problemi del pubblico target
  - `key_offerings` (array): Offerte principali
  - `differentiators` (array): Differenziatori competitivi
  - `clarifying_questions` (array): Domande personalizzate
  - `user_answers` (object): Risposte dell'utente alle domande
- `source_session_id` (UUID): ID della sessione di onboarding
- `created_by` (string): Identificatore del servizio chiamante
- `idempotency_key` (string): Chiave per evitare duplicati

---

## 📤 Response Format

### **Success Response (201 Created)**
```json
{
  "card_ids": [
    "card-company-uuid",
    "card-audience-uuid", 
    "card-voice-uuid",
    "card-insights-uuid"
  ],
  "created_count": 4,
  "partial": false,
  "trace_id": "7e678a52-724a-445e-9f74-cfd35760d73d"
}
```

### **Campi Response**
- `card_ids` (array): Lista degli UUID delle cards create
- `created_count` (integer): Numero di cards create (normalmente 4)
- `partial` (boolean): `true` se alcune cards non sono state create
- `trace_id` (string): ID per tracciamento

### **Error Responses**

#### **400 Bad Request**
```json
{
  "error": "BadRequest",
  "detail": "Invalid company_snapshot format",
  "trace_id": "7e678a52-724a-445e-9f74-cfd35760d73d"
}
```

#### **409 Conflict (Idempotency)**
```json
{
  "card_ids": ["existing-card-1", "existing-card-2", "existing-card-3", "existing-card-4"],
  "created_count": 4,
  "partial": false,
  "trace_id": "7e678a52-724a-445e-9f74-cfd35760d73d",
  "message": "Cards already exist for this idempotency key"
}
```

#### **500 Internal Server Error**
```json
{
  "error": "InternalServerError",
  "detail": "Failed to create cards",
  "trace_id": "7e678a52-724a-445e-9f74-cfd35760d73d"
}
```

---

## 🌐 Frontend da Implementare

### **Route**
```
GET /cards?session_id={session_id}&tenant_id={tenant_id}
```

### **Esempio URL**
```
http://localhost:3002/cards?session_id=7e678a52-724a-445e-9f74-cfd35760d73d&tenant_id=7e678a52-724a-445e-9f74-cfd35760d73d
```

### **Query Parameters**
- `session_id` (UUID): ID della sessione di onboarding
- `tenant_id` (UUID): ID del tenant (per multi-tenancy)

### **Comportamento Atteso**
1. Ricevere `session_id` e `tenant_id` dai query params
2. Chiamare il backend Cards Service per recuperare le cards
3. Visualizzare le 4 cards create:
   - Company Card
   - Audience Intelligence Card
   - Voice DNA Card
   - Strategic Insights Card
4. Permettere editing e gestione delle cards

---

## 📋 Le 4 Cards da Creare

### **1. Company Card**
**Contenuto da generare dal `company_snapshot`:**
- Descrizione dell'azienda (da `brand_name`, `industry`)
- Key offerings (da `key_offerings`)
- Differenziatori competitivi (da `differentiators`)

**Esempio Output:**
```
Company: One Piece Products
Industry: Anime Merchandise & Collectibles

Key Offerings:
• Official licensed products
• Exclusive collectibles
• Pre-order system

Differentiators:
• Direct partnerships with licensors
• Global shipping network
• Authenticity guarantee
```

---

### **2. Audience Intelligence Card**
**Contenuto da generare dal `company_snapshot`:**
- Target audience (da `target_audience`)
- Pain points (da `pain_points`)
- Insights dalle risposte utente (da `user_answers`)

**Esempio Output:**
```
Target Audience: Anime fans, collectors, cosplayers aged 15-35

Pain Points:
• Finding authentic merchandise
• High shipping costs
• Limited edition availability

Customer Insights:
• Primary focus: Action figures and statues
• Average order value: $50-150
• Market reach: Worldwide shipping
```

---

### **3. Voice DNA Card**
**Contenuto da generare:**
- Tone of voice (inferito da industry e target audience)
- Brand personality
- Communication style
- Esempi di messaging

**Nota**: Questa card richiede elaborazione AI aggiuntiva per inferire il tone of voice appropriato basato su industry e target audience.

**Esempio Output:**
```
Tone of Voice: Enthusiastic, Authentic, Community-driven

Brand Personality:
• Passionate about anime culture
• Trustworthy and transparent
• Collector-focused

Communication Style:
• Use anime/manga terminology
• Emphasize authenticity and quality
• Build community engagement
```

---

### **4. Strategic Insights Card**
**Contenuto da generare:**
- Market positioning
- Competitive advantages
- Growth opportunities
- Raccomandazioni strategiche

**Nota**: Questa card richiede ricerca aggiuntiva e analisi di mercato.

**Esempio Output:**
```
Market Positioning: Premium anime merchandise provider

Competitive Advantages:
• Direct licensor partnerships
• Authenticity guarantee
• Global distribution network

Growth Opportunities:
• Expand pre-order exclusive items
• Build collector community platform
• Partner with anime conventions

Strategic Recommendations:
• Focus on limited edition releases
• Leverage social proof from collectors
• Implement loyalty program for repeat customers
```

---

## 🔧 Configurazione Richiesta

### **Porte**
```bash
# Backend API
PORT=8002
HOST=0.0.0.0

# Frontend
PORT=3002
HOST=0.0.0.0
```

### **Environment Variables**
```bash
# Cards Service Backend
CARDS_API_PORT=8002
CARDS_API_HOST=0.0.0.0
DATABASE_URL=postgresql://user:pass@localhost:5432/cards_db

# Cards Service Frontend
VITE_CARDS_API_URL=http://localhost:8002
VITE_CARDS_FRONTEND_PORT=3002
```

### **Database Schema (Suggerito)**
```sql
CREATE TABLE cards (
    card_id UUID PRIMARY KEY,
    session_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    card_type VARCHAR(50) NOT NULL, -- 'company', 'audience', 'voice', 'insights'
    content JSONB NOT NULL,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    idempotency_key VARCHAR(255) UNIQUE,
    CONSTRAINT fk_session FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE INDEX idx_cards_session ON cards(session_id);
CREATE INDEX idx_cards_idempotency ON cards(idempotency_key);
```

---

## 🔑 Idempotency - IMPORTANTE

### **Perché è Importante**
L'Onboarding Service potrebbe inviare la stessa richiesta più volte (retry, errori di rete, etc.). Devi evitare di creare cards duplicate.

### **Implementazione**
1. Quando ricevi una richiesta, controlla se esiste già un record con lo stesso `idempotency_key`
2. Se esiste:
   - **NON creare nuove cards**
   - Ritorna le `card_ids` esistenti con status `200 OK` o `409 Conflict`
3. Se non esiste:
   - Crea le cards
   - Salva l'`idempotency_key` nel database
   - Ritorna le nuove `card_ids` con status `201 Created`

### **Esempio Pseudocodice**
```python
def create_cards_batch(request):
    idempotency_key = request.idempotency_key
    
    # Check if cards already exist
    existing_cards = db.query(Card).filter(
        Card.idempotency_key == idempotency_key
    ).all()
    
    if existing_cards:
        # Return existing cards (idempotent)
        return {
            "card_ids": [card.card_id for card in existing_cards],
            "created_count": len(existing_cards),
            "partial": False,
            "trace_id": request.trace_id
        }
    
    # Create new cards
    cards = create_four_cards(request.company_snapshot)
    
    # Save with idempotency key
    for card in cards:
        card.idempotency_key = idempotency_key
        db.add(card)
    
    db.commit()
    
    return {
        "card_ids": [card.card_id for card in cards],
        "created_count": len(cards),
        "partial": False,
        "trace_id": request.trace_id
    }
```

---

## ✅ Checklist Implementazione

### **Backend**
- [ ] API su porta 8002
- [ ] Endpoint `POST /api/v1/cards/batch` implementato
- [ ] Parsing del `company_snapshot`
- [ ] Generazione delle 4 cards
- [ ] Gestione idempotency key
- [ ] Salvataggio cards in database
- [ ] Response con `card_ids`
- [ ] Error handling (400, 409, 500)
- [ ] Logging e tracing

### **Frontend**
- [ ] App su porta 3002
- [ ] Route `/cards` implementata
- [ ] Parsing query params (`session_id`, `tenant_id`)
- [ ] Chiamata API per recuperare cards
- [ ] Visualizzazione delle 4 cards
- [ ] UI per editing cards (opzionale)
- [ ] Error handling

### **Testing**
- [ ] Test endpoint con payload di esempio
- [ ] Test idempotency (stessa richiesta 2 volte)
- [ ] Test error cases (payload invalido)
- [ ] Test frontend redirect da Onboarding

---

## 🧪 Testing

### **Test 1: Creare Cards**
```bash
curl -X POST http://localhost:8002/api/v1/cards/batch \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: test-tenant-123" \
  -H "X-Trace-ID: test-trace-123" \
  -d '{
    "company_snapshot": {
      "brand_name": "Test Company",
      "industry": "Technology",
      "target_audience": "Developers",
      "pain_points": ["Complexity", "Cost"],
      "key_offerings": ["API", "SDK"],
      "differentiators": ["Speed", "Reliability"],
      "clarifying_questions": [],
      "user_answers": {}
    },
    "source_session_id": "test-session-123",
    "created_by": "test",
    "idempotency_key": "test-idem-123"
  }'
```

### **Test 2: Idempotency**
```bash
# Esegui la stessa richiesta 2 volte
# La seconda volta deve ritornare gli stessi card_ids senza creare duplicati
```

### **Test 3: Frontend Redirect**
1. Completa un onboarding su `http://localhost:3001`
2. Verifica che il browser venga reindirizzato a `http://localhost:3002/cards?session_id=...`
3. Verifica che le cards vengano visualizzate correttamente

---

## 📞 Integrazione con Onboarding Service

### **Quando Viene Chiamato**
Il Cards Service viene chiamato automaticamente dall'Onboarding Service quando:
1. L'utente completa le domande personalizzate
2. L'Onboarding Service arricchisce il Company Snapshot con le risposte
3. L'Onboarding Service chiama `POST /api/v1/cards/batch`

### **Flusso Completo**
```
User → Onboarding Frontend → Onboarding Backend → Cards Backend
                                                         ↓
User ← Cards Frontend ←────────────────────────────────┘
```

---

## 🚀 Quick Start

1. **Clona/Crea il progetto Cards Service**
2. **Configura le porte**: 8002 (backend), 3002 (frontend)
3. **Implementa l'endpoint** `POST /api/v1/cards/batch`
4. **Implementa la route** `/cards` nel frontend
5. **Testa con curl** usando il payload di esempio
6. **Testa il redirect** completando un onboarding

---

**Questo documento contiene TUTTE le informazioni necessarie per implementare il Cards Service!** 🎉

