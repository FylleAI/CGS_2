# Fylle Onboarding v3

A modular onboarding microservice for content generation with support for multiple LLM providers.

## Features

- **Multi-Provider LLM Support**: OpenAI, Anthropic, Gemini, DeepSeek, Perplexity
- **Configurable Prompts**: YAML defaults with Supabase dynamic overrides
- **Cards System**: 8 card types for company context
- **Packs**: Newsletter Pack, Blog Post Pack for brief generation
- **Full Tracking**: All data stored in Supabase

## Architecture

```
User Flow:
Email Input → Onboarding → Cards Generation → Pack Selection → Brief Generation
```

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
# Edit .env with your credentials
uvicorn app.main:app --reload --port 8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker (Recommended)

```bash
docker-compose up -d
```

## Project Structure

```
fylle-onboarding-v3/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config/              # Settings and provider configs
│   │   ├── api/routes/          # REST endpoints
│   │   ├── core/
│   │   │   ├── llm/             # LLM provider implementations
│   │   │   ├── prompts/         # Prompt engine
│   │   │   └── context/         # Context aggregation
│   │   ├── domain/              # Business entities and services
│   │   └── infrastructure/      # Database and repositories
│   └── prompts/                 # Default YAML prompts
├── frontend/                    # React/Vite application
└── supabase/migrations/         # Database schema
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Create user by email |
| `/api/v1/onboarding/start` | POST | Start onboarding flow |
| `/api/v1/onboarding/{id}/answers` | POST | Submit answers |
| `/api/v1/cards` | GET | Get user's cards |
| `/api/v1/cards/{id}` | PUT | Update card |
| `/api/v1/packs` | GET | List available packs |
| `/api/v1/briefs/generate` | POST | Generate brief |
| `/api/v1/briefs` | GET | List user's briefs |

## Environment Variables

See `backend/env.example` for all required variables.

## License

Proprietary - Fylle AI
