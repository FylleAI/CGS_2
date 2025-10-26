# 🚀 CGS Services Startup Guide

## Quick Start

### Windows
```bash
START_ALL_SERVICES.bat
```

### Linux/Mac
```bash
bash START_ALL_SERVICES.sh
```

---

## Services Overview

### Backend Services

| Service | Port | URL | Docs |
|---------|------|-----|------|
| **Main API** | 8000 | http://127.0.0.1:8000 | http://127.0.0.1:8000/docs |
| **Card Service** | 8001 | http://127.0.0.1:8001 | http://127.0.0.1:8001/docs |
| **Onboarding Service** | 8002 | http://127.0.0.1:8002 | http://127.0.0.1:8002/docs |

### Frontend Applications

| App | Port | URL |
|-----|------|-----|
| **Card Manager** | 5173 | http://127.0.0.1:5173 |
| **Onboarding Frontend** | 5174 | http://127.0.0.1:5174 |

---

## Manual Startup

### 1. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Start Backend Services

#### Card Service
```bash
cd services/card_service
python -m uvicorn api.card_routes:app --host 127.0.0.1 --port 8001 --reload
```

#### Onboarding Service
```bash
cd services/onboarding
python -m uvicorn api.main:app --host 127.0.0.1 --port 8002 --reload
```

#### Main API
```bash
cd api/rest
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Start Frontend Applications

#### Card Manager
```bash
cd frontends/card-explorer
npm run dev
```

#### Onboarding Frontend
```bash
cd onboarding-frontend
npm run dev -- --port 5174
```

---

## Checking Service Status

### Quick Check
```bash
bash CHECK_SERVICES_STATUS.sh
```

### Manual Check
```bash
# Check if services are running
curl http://127.0.0.1:8000/docs
curl http://127.0.0.1:8001/docs
curl http://127.0.0.1:8002/docs
```

---

## Stopping Services

### Windows
```bash
STOP_ALL_SERVICES.bat
```

### Linux/Mac
```bash
bash STOP_ALL_SERVICES.sh
```

Or manually close the terminal windows.

---

## Environment Setup

### Required Environment Variables

Create `.env` file in the root directory:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# LLM Providers
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
PERPLEXITY_API_KEY=your-perplexity-key

# Brevo (Email)
BREVO_API_KEY=your-brevo-key

# Application
ENVIRONMENT=development
DEBUG=true
```

### Frontend Environment Variables

Create `.env.local` in `frontends/card-explorer/`:

```env
VITE_API_URL=http://127.0.0.1:8001
VITE_TENANT_ID=test-user@example.com
```

Create `.env.local` in `onboarding-frontend/`:

```env
VITE_API_URL=http://127.0.0.1:8002
```

---

## Troubleshooting

### Port Already in Use

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -i :8000
kill -9 <PID>
```

### Dependencies Not Installed

```bash
pip install -r requirements.txt
cd frontends/card-explorer && npm install
cd onboarding-frontend && npm install
```

### Virtual Environment Issues

```bash
# Remove old venv
rm -rf venv

# Create new venv
python -m venv venv

# Activate and install
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Service Not Starting

Check logs:
```bash
tail -f logs/main_api.log
tail -f logs/card_service.log
tail -f logs/onboarding_service.log
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
├──────────────────────┬──────────────────────────────────┤
│  Card Manager        │  Onboarding Frontend             │
│  (port 5173)         │  (port 5174)                     │
└──────────────────────┴──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    API Gateway                           │
├──────────────────────────────────────────────────────────┤
│  Main API (port 8000)                                    │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────┬──────────────────┬───────────────┐
│  Card Service        │  Onboarding      │  Content      │
│  (port 8001)         │  Service         │  Workflow     │
│                      │  (port 8002)     │               │
└──────────────────────┴──────────────────┴───────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│                    Supabase Database                      │
└──────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
1. User completes Onboarding
   ↓
2. Onboarding Service generates CompanySnapshot
   ↓
3. CardExportPipeline creates 4 atomic cards
   ↓
4. Cards stored in Supabase
   ↓
5. Card Manager displays cards
   ↓
6. Content Workflow generates content
```

---

## Next Steps

1. ✅ Start all services
2. ✅ Check service status
3. ✅ Test API endpoints
4. ✅ Run end-to-end tests
5. ✅ Deploy to production

---

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review service documentation
3. Check GitHub issues
4. Contact development team

---

**Last Updated**: 2025-10-26
**Status**: ✅ All Services Ready

