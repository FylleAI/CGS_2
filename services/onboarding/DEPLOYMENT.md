# 🚀 Deployment Guide - Onboarding Service

Guida completa per il deployment del servizio di onboarding.

---

## 📋 Prerequisiti

### Servizi Esterni Richiesti

1. **CGS Backend** (Content Generation System)
   - URL: Configurabile via `CGS_BASE_URL`
   - Deve essere accessibile dal servizio onboarding
   - Endpoint richiesto: `POST /api/v1/content/generate`

2. **Supabase** (Database)
   - Account Supabase attivo
   - Progetto creato
   - Credenziali: URL + Service Role Key

3. **Perplexity AI** (Research)
   - API Key da https://www.perplexity.ai/
   - Modello: `sonar` o `sonar-pro`

4. **Google Gemini** (Synthesis)
   - API Key da Google AI Studio
   - Modello: `gemini-2.0-flash-exp` o `gemini-1.5-pro`

5. **Brevo** (Email Delivery) - Opzionale
   - Account Brevo (ex-Sendinblue)
   - API Key da dashboard Brevo
   - Email mittente verificata

---

## 🔧 Setup Locale

### 1. Clone e Installazione

```bash
# Naviga nella directory onboarding
cd onboarding

# Crea virtual environment (opzionale ma consigliato)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate  # Windows

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Configurazione Environment

```bash
# Copia template
cp .env.example .env

# Modifica .env con le tue credenziali
nano .env  # o usa il tuo editor preferito
```

**Variabili richieste**:

```bash
# Service
SERVICE_NAME=onboarding-service
SERVICE_VERSION=1.0.0
LOG_LEVEL=INFO

# API
ONBOARDING_API_HOST=0.0.0.0
ONBOARDING_API_PORT=8001

# CGS Backend
CGS_BASE_URL=http://localhost:8000
CGS_API_KEY=your-cgs-api-key  # Se richiesto

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Perplexity
PERPLEXITY_API_KEY=your-perplexity-api-key
PERPLEXITY_MODEL=sonar

# Gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash-exp

# Brevo (opzionale)
BREVO_API_KEY=your-brevo-api-key
BREVO_SENDER_EMAIL=noreply@yourdomain.com
BREVO_SENDER_NAME=Your Company
ENABLE_AUTO_DELIVERY=true
```

### 3. Setup Database

```bash
# 1. Accedi a Supabase Dashboard
# 2. Vai su SQL Editor
# 3. Copia il contenuto di infrastructure/database/supabase_schema.sql
# 4. Esegui lo script SQL

# Verifica creazione tabella
# SELECT * FROM onboarding_sessions LIMIT 1;
```

### 4. Avvio Servizio

```bash
# Opzione 1: Uvicorn con reload (development)
uvicorn onboarding.api.main:app --reload --port 8001

# Opzione 2: Python module
python -m onboarding.api.main

# Opzione 3: Uvicorn production
uvicorn onboarding.api.main:app --host 0.0.0.0 --port 8001 --workers 4
```

### 5. Verifica

```bash
# Health check
curl http://localhost:8001/health

# API Docs
open http://localhost:8001/docs

# Root endpoint
curl http://localhost:8001/
```

---

## 🐳 Deployment con Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copia dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia codice
COPY . .

# Esponi porta
EXPOSE 8001

# Comando di avvio
CMD ["uvicorn", "onboarding.api.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  onboarding:
    build: .
    ports:
      - "8001:8001"
    env_file:
      - .env
    environment:
      - ONBOARDING_API_HOST=0.0.0.0
      - ONBOARDING_API_PORT=8001
    restart: unless-stopped
    depends_on:
      - cgs
    networks:
      - app-network

  cgs:
    image: your-cgs-image:latest
    ports:
      - "8000:8000"
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### Build e Run

```bash
# Build
docker build -t onboarding-service:latest .

# Run
docker run -d \
  --name onboarding \
  -p 8001:8001 \
  --env-file .env \
  onboarding-service:latest

# Con docker-compose
docker-compose up -d
```

---

## ☁️ Deployment Cloud

### Railway / Render / Fly.io

1. **Crea nuovo servizio**
2. **Connetti repository Git**
3. **Configura environment variables** (copia da .env)
4. **Imposta build command**: `pip install -r requirements.txt`
5. **Imposta start command**: `uvicorn onboarding.api.main:app --host 0.0.0.0 --port $PORT`
6. **Deploy**

### AWS / GCP / Azure

Usa Docker deployment con:
- **AWS**: ECS/Fargate o App Runner
- **GCP**: Cloud Run o GKE
- **Azure**: Container Instances o AKS

---

## 🔒 Sicurezza

### Best Practices

1. **API Keys**: Mai committare nel repository
2. **CORS**: Configura `allow_origins` in produzione
3. **Rate Limiting**: Aggiungi middleware per rate limiting
4. **HTTPS**: Usa sempre HTTPS in produzione
5. **Secrets**: Usa secret manager (AWS Secrets, GCP Secret Manager, etc.)

### Esempio Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/onboarding/start")
@limiter.limit("5/minute")
async def start_onboarding(...):
    ...
```

---

## 📊 Monitoring

### Logs

```bash
# Tail logs
tail -f logs/onboarding.log

# Docker logs
docker logs -f onboarding

# Structured logging
# Logs sono in formato: timestamp - name - level - message
```

### Metrics

Monitora:
- **Request rate**: Richieste al minuto
- **Error rate**: Errori 4xx/5xx
- **Latency**: Tempo risposta API
- **CGS health**: Status CGS backend
- **Database**: Query performance Supabase

### Health Checks

```bash
# Health endpoint
curl http://localhost:8001/health

# Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "perplexity": true,
    "gemini": true,
    "supabase": true,
    "brevo": true
  },
  "cgs_healthy": true
}
```

---

## 🐛 Troubleshooting

### Problema: CGS non raggiungibile

```bash
# Verifica connettività
curl http://localhost:8000/health

# Controlla CGS_BASE_URL in .env
echo $CGS_BASE_URL
```

### Problema: Supabase connection error

```bash
# Verifica credenziali
# Controlla SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY

# Test connessione
python -c "from supabase import create_client; client = create_client('URL', 'KEY'); print('OK')"
```

### Problema: API Key invalida

```bash
# Verifica API keys
# Controlla che non ci siano spazi o caratteri nascosti

# Test Perplexity
curl https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY"

# Test Gemini
curl "https://generativelanguage.googleapis.com/v1/models?key=$GEMINI_API_KEY"
```

---

## 📚 Risorse

- **API Docs**: http://localhost:8001/docs
- **Supabase Dashboard**: https://app.supabase.com
- **CGS Repository**: [Link al repo CGS]
- **Support**: [Email o Slack channel]

---

**Deployment completato!** 🎉

Per domande o problemi, consulta la documentazione o contatta il team di sviluppo.

