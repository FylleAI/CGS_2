# 🔧 CGS Knowledge Base Fix - Caricamento da Supabase

**Data**: 2025-10-15  
**Problema**: Frontend CGS non caricava knowledge base da Supabase quando si selezionava un cliente

---

## 🐛 **Problema Identificato**

### **Sintomo**
- Selezionando un cliente nel frontend CGS, la knowledge base non si caricava
- Console browser mostrava errori di caricamento documenti

### **Causa Root**
1. **Frontend usava dati mock hardcoded** invece di caricare da Supabase
2. **Client "reopla" non esisteva** in Supabase (solo "siebert" presente)
3. **Nessun endpoint API** per recuperare client profiles completi

### **Errore Backend**
```
2025-10-15 21:59:11 - api.rest.v1.endpoints.knowledge_base - INFO - 🎨 Getting frontend documents for client: reopla
HTTP/2 406 Not Acceptable
proxy-status: PostgREST; error=PGRST116
```

**Significato**: Client "reopla" non trovato nella tabella `clients` di Supabase

---

## ✅ **Soluzione Implementata**

### **1. Creato Nuovo Endpoint API**

**File**: `api/rest/v1/endpoints/knowledge_base.py`

**Endpoint**: `GET /api/v1/knowledge-base/profiles`

**Codice**:
```python
class ClientProfile(BaseModel):
    """Client profile model for frontend."""
    
    id: str
    name: str
    displayName: str
    description: Optional[str] = None
    brandVoice: Optional[str] = None
    targetAudience: Optional[str] = None
    industry: Optional[str] = None
    ragEnabled: bool = True
    knowledgeBasePath: Optional[str] = None


@router.get("/profiles", response_model=List[ClientProfile])
async def get_client_profiles(supabase=Depends(get_supabase_client)) -> List[ClientProfile]:
    """Get list of client profiles with full details."""
    logger.info("📋 Getting client profiles from Supabase")

    try:
        res = supabase.table("clients").select("*").execute()
        profiles = []
        for client in (res.data or []):
            profiles.append(ClientProfile(
                id=client["name"],
                name=client["name"],
                displayName=client.get("display_name", client["name"]),
                description=client.get("description"),
                brandVoice=client.get("brand_voice"),
                targetAudience=client.get("target_audience"),
                industry=client.get("industry"),
                ragEnabled=client.get("rag_enabled", True),
                knowledgeBasePath=client.get("knowledge_base_path")
            ))
        logger.info(f"✅ Found {len(profiles)} client profiles from Supabase")
        return sorted(profiles, key=lambda x: x.name)
    except Exception as e:
        logger.error(f"Error getting client profiles from Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving client profiles: {e}")
```

---

### **2. Aggiornato Frontend per Usare API Reale**

**File**: `web/react-app/src/services/api.ts`

**Prima** (dati mock):
```typescript
async getClientProfiles(): Promise<ClientProfile[]> {
  // For now, return mock data - will be replaced with real API
  return [
    {
      id: 'siebert',
      name: 'siebert',
      displayName: 'Siebert Financial',
      // ... hardcoded data
    },
    {
      id: 'reopla',  // ❌ Non esiste in Supabase!
      name: 'reopla',
      // ... hardcoded data
    }
  ];
}
```

**Dopo** (caricamento da Supabase):
```typescript
async getClientProfiles(): Promise<ClientProfile[]> {
  try {
    console.log('📋 Fetching client profiles from knowledge base API');
    
    const response = await api.get('/api/v1/knowledge-base/profiles');
    
    console.log(`✅ Received ${response.data.length} client profiles from Supabase`);
    
    return response.data;
  } catch (error) {
    console.error('❌ Error fetching client profiles:', error);
    throw new Error('Failed to fetch client profiles from Supabase');
  }
}
```

---

## 🧪 **Test e Verifica**

### **Test Endpoint**
```bash
curl http://localhost:8000/api/v1/knowledge-base/profiles
```

**Risposta**:
```json
[
  {
    "id": "siebert",
    "name": "siebert",
    "displayName": "Siebert Financial",
    "description": "Financial services company focused on empowering individual investors",
    "brandVoice": "Professional yet accessible, empowering, educational, trustworthy",
    "targetAudience": "Gen Z and young professionals interested in financial literacy",
    "industry": "Financial Services",
    "ragEnabled": true,
    "knowledgeBasePath": "knowledge_base/siebert"
  }
]
```

### **Verifica Supabase**
```bash
curl http://localhost:8000/api/v1/knowledge-base/clients
```

**Risposta**:
```json
["siebert"]
```

---

## 📊 **Architettura Aggiornata**

### **Prima**
```
Frontend CGS
    │
    └─► Dati Mock Hardcoded
        ├─ siebert ✅
        ├─ reopla ❌ (non esiste in Supabase)
        └─ default
```

### **Dopo**
```
Frontend CGS
    │
    └─► GET /api/v1/knowledge-base/profiles
        │
        └─► Supabase.table("clients").select("*")
            │
            └─► Restituisce solo client reali:
                └─ siebert ✅
```

---

## 🎯 **Benefici**

### **1. Sincronizzazione Automatica**
- ✅ Frontend mostra sempre i client realmente presenti in Supabase
- ✅ Nessun disallineamento tra frontend e database
- ✅ Nessun errore 406 quando si seleziona un client

### **2. Gestione Dinamica**
- ✅ Aggiungendo un client in Supabase, appare automaticamente nel frontend
- ✅ Rimuovendo un client da Supabase, scompare dal frontend
- ✅ Nessuna modifica al codice necessaria

### **3. Dati Completi**
- ✅ Frontend riceve tutti i dettagli del client (brand voice, target audience, etc.)
- ✅ Informazioni sempre aggiornate
- ✅ Single source of truth (Supabase)

---

## 📝 **Schema Supabase**

### **Tabella `clients`**
```sql
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    brand_voice TEXT,
    target_audience TEXT,
    industry VARCHAR(100),
    rag_enabled BOOLEAN DEFAULT true,
    knowledge_base_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **Client Esistente**
```sql
SELECT * FROM clients WHERE name = 'siebert';
```

| Campo | Valore |
|-------|--------|
| name | siebert |
| display_name | Siebert Financial |
| description | Financial services company... |
| brand_voice | Professional yet accessible... |
| target_audience | Gen Z and young professionals... |
| industry | Financial Services |
| rag_enabled | true |
| knowledge_base_path | knowledge_base/siebert |

---

## 🚀 **Prossimi Step**

### **Per Aggiungere Nuovi Client**

1. **Inserisci in Supabase**:
```sql
INSERT INTO clients (name, display_name, description, brand_voice, target_audience, industry, rag_enabled, knowledge_base_path)
VALUES (
    'nuovo_cliente',
    'Nuovo Cliente S.p.A.',
    'Descrizione del cliente',
    'Tono di voce del brand',
    'Target audience',
    'Industria',
    true,
    'knowledge_base/nuovo_cliente'
);
```

2. **Ricarica Frontend**: Il nuovo client apparirà automaticamente!

---

## 🔍 **Troubleshooting**

### **Problema**: Frontend non mostra nessun client
**Soluzione**: Verifica che Supabase sia configurato correttamente nel `.env`:
```bash
SUPABASE_URL=https://iimymnlepgilbuoxnkqa.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
USE_SUPABASE=true
```

### **Problema**: Errore 500 dall'endpoint `/profiles`
**Soluzione**: Verifica che la tabella `clients` esista in Supabase:
```bash
curl http://localhost:8000/api/v1/knowledge-base/clients
```

### **Problema**: Knowledge base non si carica per un client
**Soluzione**: Verifica che il client abbia documenti nella tabella `documents`:
```bash
curl http://localhost:8000/api/v1/knowledge-base/frontend/clients/siebert/documents
```

---

## ✅ **Status Finale**

- ✅ Backend CGS riavviato con nuovo endpoint
- ✅ Frontend CGS aggiornato per usare API reale
- ✅ Caricamento client profiles da Supabase funzionante
- ✅ Knowledge base si carica correttamente per client "siebert"
- ✅ Nessun errore 406 o client inesistenti

---

**Ultimo aggiornamento**: 2025-10-15 22:05

