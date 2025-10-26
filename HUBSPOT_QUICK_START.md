# 🚀 HubSpot Integration - Quick Start Guide

**TL;DR**: Pubblicazione nativa contenuti su HubSpot con architettura ibrida MCP + Direct API

---

## 📊 OVERVIEW

### Cosa Stiamo Costruendo

Sistema per pubblicare contenuti generati (blog posts, social media) direttamente su HubSpot con:
- ✅ **MCP Integration** per context-aware content generation
- ✅ **Direct API** per pubblicazione (write operations)
- ✅ Multi-tenant aware
- ✅ Scheduling & retry logic
- ✅ Performance tracking

### Timeline & Effort

| Fase | Durata | Story Points | Deliverables |
|------|--------|--------------|--------------|
| **MVP** (Phase 1-2) | 4-5 settimane | 65 points | Blog publishing, basic UI, MCP read |
| **Production-Ready** (Phase 1-4) | 7-8 settimane | 99 points | OAuth, multi-tenant, scheduling |
| **Complete** (All phases) | 8-10 settimane | 144 points | Social, analytics, MCP full integration |

### MVP Scope (4-5 settimane, 65 points)

**Must Have**:
- ✅ Database schema (credentials, publications, metadata)
- ✅ HubSpot MCP client (read-only CRM access)
- ✅ HubSpot Direct API adapter (blog publishing)
- ✅ Markdown → HTML converter
- ✅ Basic UI (publish button, status tracking)
- ✅ Private App authentication (simple)

**Nice to Have** (defer to Phase 2):
- ⏳ OAuth 2.0 flow
- ⏳ Scheduling
- ⏳ Social media publishing
- ⏳ Performance analytics

---

## 🏗️ ARCHITETTURA

### Approccio Ibrido: MCP + Direct API

**Perché Ibrido?**
- HubSpot MCP Server è **read-only** al momento
- Direct API necessaria per **write operations** (pubblicazione)
- MCP ottimo per **context-aware generation** e validation

**Componenti**:

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  - Publish button  - Status tracking  - Preview             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                            │
│  - PublishToHubSpotUseCase                                   │
│  - ContentPublicationRepository                              │
└─────────┬──────────────────────────────────┬────────────────┘
          │                                  │
┌─────────▼──────────────┐      ┌───────────▼────────────────┐
│  HubSpot MCP Client    │      │  HubSpot Direct API        │
│  (Read Operations)     │      │  (Write Operations)        │
│  - Get contacts        │      │  - Publish blog post       │
│  - Get companies       │      │  - Publish social post     │
│  - Get deals           │      │  - Schedule publication    │
│  - Context enrichment  │      │  - Get analytics           │
└────────────────────────┘      └────────────────────────────┘
          │                                  │
          │                                  │
┌─────────▼──────────────────────────────────▼────────────────┐
│                    HubSpot Platform                          │
│  - CRM (contacts, companies, deals)                          │
│  - Content (blog posts, social media)                        │
│  - Analytics                                                 │
└──────────────────────────────────────────────────────────────┘
```

**Workflow**:
1. User clicks "Publish to HubSpot"
2. **MCP Client** fetches context (target company, contact, deal)
3. Content enriched with CRM context
4. **Direct API** publishes blog post
5. Publication tracked in database
6. **MCP Client** fetches analytics (post-publication)

---

## 🛠️ TECH STACK

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL (Supabase)
- **MCP Client**: `mcp` Python SDK
- **HTTP Client**: `httpx` (async)
- **Markdown**: `markdown` + `bleach` (sanitization)

### Frontend
- **Framework**: React 18 + TypeScript
- **UI**: Material-UI (MUI)
- **State**: React Query
- **Build**: Vite

### HubSpot
- **MCP Server**: `mcp.hubspot.com` (read-only)
- **Direct API**: `api.hubapi.com` (write operations)
- **Auth**: OAuth 2.0 (migrerà a OAuth 2.1 con PKCE)
- **Platform**: Developer Platform v2025.2+

### DevOps
- **CLI**: HubSpot CLI v7.60.0+ (Developer MCP)
- **Deployment**: Docker
- **Monitoring**: Sentry (error tracking)

---

## 📋 GETTING STARTED

### Phase 1: Setup HubSpot MCP (Week 1)

#### 1.1 Create HubSpot Developer Account
```bash
# 1. Go to https://developers.hubspot.com/
# 2. Create developer account
# 3. Create test account (sandbox)
```

#### 1.2 Create User-Level App
```bash
# 1. Go to HubSpot Developer Platform
# 2. Create new app (User-level)
# 3. Add OAuth scopes:
#    - crm.objects.contacts.read
#    - crm.objects.companies.read
#    - crm.objects.deals.read
#    - crm.objects.tickets.read
#    - content (for blog posts - write)
# 4. Get Client ID and Client Secret
```

#### 1.3 Install HubSpot CLI & Setup Developer MCP
```bash
# Install HubSpot CLI
npm install -g @hubspot/cli@latest

# Verify version (must be 7.60.0+)
hs --version

# Setup Developer MCP Server
hs mcp setup

# Select tools:
# - Scaffolding
# - Deploy
# - Documentation access

# Test Developer MCP
# (use with Claude Desktop, Cursor, or other MCP client)
```

#### 1.4 Install MCP Python SDK
```bash
# Install MCP client library
pip install mcp

# Install HubSpot MCP server (Node.js)
npx -y @hubspot/mcp-server --version
```

#### 1.5 Test MCP Connection
```python
# test_mcp_connection.py

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp():
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@hubspot/mcp-server"],
        env={
            "HUBSPOT_ACCESS_TOKEN": "your_access_token",
            "HUBSPOT_PORTAL_ID": "your_portal_id",
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test: Get contact
            result = await session.call_tool("get_contact", {"id": "123"})
            print(f"Contact: {result}")

asyncio.run(test_mcp())
```

---

### Phase 2: Database Setup (Week 1)

#### 2.1 Create Migration Script
```bash
# Create migration file
touch onboarding/infrastructure/database/migrations/004_create_hubspot_integration.sql

# Copy schema from DATABASE_SCHEMA_HUBSPOT_INTEGRATION.sql
```

#### 2.2 Run Migration
```bash
# Connect to Supabase
psql $DATABASE_URL

# Run migration
\i onboarding/infrastructure/database/migrations/004_create_hubspot_integration.sql

# Verify tables
\dt hubspot_*
```

---

### Phase 3: Implement MCP Client (Week 2)

#### 3.1 Create MCP Client Wrapper
```bash
# Create file
touch onboarding/infrastructure/mcp/hubspot_mcp_client.py

# Implement HubSpotMCPClient class
# See EXAMPLES_HUBSPOT_INTEGRATION.md for code
```

#### 3.2 Test MCP Client
```python
# test_mcp_client.py

from onboarding.infrastructure.mcp.hubspot_mcp_client import HubSpotMCPClient

async def test():
    client = HubSpotMCPClient()
    session = await client.connect(access_token, portal_id)
    
    # Get company
    company = await client.get_company(session, "123")
    print(f"Company: {company}")

asyncio.run(test())
```

---

### Phase 4: Implement Direct API Adapter (Week 2-3)

#### 4.1 Create HubSpot Adapter
```bash
# Create file
touch onboarding/infrastructure/adapters/hubspot_adapter.py

# Implement HubSpotAdapter class
# See EXAMPLES_HUBSPOT_INTEGRATION.md for code
```

#### 4.2 Test Blog Publishing
```python
# test_publish_blog.py

from onboarding.infrastructure.adapters.hubspot_adapter import HubSpotAdapter

async def test():
    adapter = HubSpotAdapter(access_token, portal_id)
    
    result = await adapter.publish_blog_post(
        title="Test Blog Post",
        body_html="<p>Hello World</p>",
        blog_author_id="123",
        content_group_id="456",
    )
    
    print(f"Published: {result['url']}")

asyncio.run(test())
```

---

## 🎯 SUCCESS METRICS

### MVP (Phase 1-2)
- ✅ MCP connection success rate >95%
- ✅ Blog post publish success rate >90%
- ✅ Average publish time <10 seconds
- ✅ Zero credential leaks

### Production-Ready (Phase 1-4)
- ✅ OAuth flow completion rate >80%
- ✅ Token refresh success rate >99%
- ✅ Multi-tenant isolation 100%
- ✅ Scheduled publish accuracy >95%

### Complete (All Phases)
- ✅ Social media publish success >85%
- ✅ Analytics fetch success >90%
- ✅ System uptime >99.5%

---

## 🚨 RISKS & MITIGATIONS

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| MCP write operations non disponibili | High | High | Usa Direct API (già pianificato) |
| OAuth 2.1 migration breaking changes | Medium | Medium | Monitor HubSpot changelog, test early |
| Rate limiting (100 req/10s) | Medium | Medium | Implement rate limiter, queue system |
| Token expiration (6h) | Low | High | Background refresh job |
| HubSpot API changes | Medium | Low | Version pinning, integration tests |

---

## 📚 RESOURCES

### Documentation
- [HubSpot MCP Server](https://developers.hubspot.com/mcp)
- [HubSpot API Docs](https://developers.hubspot.com/docs/api/overview)
- [MCP Protocol Spec](https://modelcontextprotocol.io/)
- [OAuth 2.1 Spec](https://oauth.net/2.1/)

### Internal Docs
- `HUBSPOT_INTEGRATION_ANALYSIS.md` - Complete analysis
- `LINEAR_ROADMAP_HUBSPOT_INTEGRATION.md` - Detailed roadmap
- `DATABASE_SCHEMA_HUBSPOT_INTEGRATION.sql` - Database schema
- `EXAMPLES_HUBSPOT_INTEGRATION.md` - Code examples

---

**Last Updated**: 2025-10-25  
**Version**: 2.0 (Updated with MCP)  
**Status**: Ready for Implementation

