# 📋 HubSpot Integration - Linear Roadmap

**Project**: Native HubSpot Publishing Integration
**Approccio**: Architettura ibrida MCP + Direct API
**Timeline**: 8-10 settimane
**Team Size**: 2-3 engineers (1 Backend, 1 Full-stack, 0.5 DevOps)
**Story Points Totali**: 144 points (aggiornato con MCP)

---

## 🆕 IMPORTANTE: HubSpot MCP Integration

### Strategia MCP

**HubSpot MCP Server** (Model Context Protocol) è ora disponibile in beta:
- ✅ **Read-only** access a CRM data (contacts, companies, deals, tickets, etc.)
- ✅ OAuth 2.0 authentication (migrerà a OAuth 2.1 con PKCE nel 2025)
- ✅ Endpoint: `mcp.hubspot.com`
- ❌ **No write operations** al momento (no pubblicazione diretta)

**Architettura Ibrida Proposta**:
1. **HubSpot MCP Server** → Context-aware content generation, validation, preview
2. **Direct HubSpot API** → Pubblicazione contenuti (write operations)
3. **Developer MCP Server** → Sviluppo e deploy accelerato

**Roadmap MCP**:
- **Fase 1** (MVP): Direct API only
- **Fase 2** (Hybrid): MCP read + Direct API write ← **Implementeremo questa**
- **Fase 3** (Future): Full MCP quando write operations disponibili

**Requisiti MCP**:
- HubSpot Developer Platform v2025.2+
- HubSpot CLI v7.60.0+ (per Developer MCP)
- User-level App con OAuth scopes
- MCP-compatible client library

---

## 📊 EXECUTIVE SUMMARY

### Obiettivo
Abilitare la pubblicazione nativa dei contenuti generati dal sistema CGS direttamente su HubSpot (Blog, Social Media, Email).

### Scope
- **MVP** (4-5 settimane): Blog post publishing con Private App token
- **Production-Ready** (7-8 settimane): OAuth multi-tenant, scheduling, social media
- **Advanced** (10 settimane): Performance tracking, A/B testing, auto-optimization

### Effort Totale
- **Total Story Points**: 134
- **MVP Points**: 55 (41%)
- **Production Points**: 89 (66%)

---

## 🎯 MILESTONES

### M1: Foundation & Database (Weeks 1-2)
**Goal**: Database schema e domain models pronti  
**Points**: 23  
**Deliverables**:
- Database migration con 4 tabelle
- Domain models (HubSpotCredential, ContentPublication)
- Repository layer completo

### M2: HubSpot Adapter & Blog Publishing (Weeks 3-4)
**Goal**: Pubblicazione blog post funzionante  
**Points**: 32  
**Deliverables**:
- HubSpotAdapter con blog API
- Content format conversion (Markdown → HTML)
- Error handling e retry logic

### M3: API & Frontend Integration (Week 5)
**Goal**: UI per pubblicazione  
**Points**: 18  
**Deliverables**:
- API endpoints per pubblicazione
- Frontend UI per trigger pubblicazione
- Status tracking dashboard

### M4: OAuth & Multi-Tenant (Weeks 6-7)
**Goal**: Multi-tenant production-ready  
**Points**: 34  
**Deliverables**:
- OAuth 2.0 flow completo
- Token refresh automation
- Multi-tenant credential management

### M5: Advanced Features (Weeks 8-10)
**Goal**: Scheduling, social, performance tracking
**Points**: 27
**Deliverables**:
- Scheduled publishing
- Social media publishing
- Performance tracking da HubSpot
- A/B testing framework

### M6: MCP Integration (Weeks 6-8) 🆕
**Goal**: Integrate HubSpot MCP for context-aware publishing
**Points**: 10
**Deliverables**:
- MCP client implementation
- Context-aware content enrichment
- Preview con dati reali da CRM
- Developer MCP setup per team

---

## 📦 EPICS & TASKS

### EPIC 0: MCP Setup & Integration 🆕

#### Task 0.1: Setup HubSpot MCP Server
**ID**: HS-0.1
**Priority**: P1 (High)
**Estimate**: 3 points
**Assignee**: Backend Engineer
**Dependencies**: None

**Description**:
Setup HubSpot MCP Server (Remote) per accesso read-only a CRM data. Configurare OAuth app e testare connessione.

**Acceptance Criteria**:
- [ ] HubSpot Developer Platform v2025.2+ configurato
- [ ] User-level App creata con OAuth scopes (crm.objects.contacts.read, crm.objects.companies.read, etc.)
- [ ] MCP client library installata (Python MCP SDK)
- [ ] Connessione a mcp.hubspot.com testata
- [ ] Esempio di fetch contact/company funzionante
- [ ] Documentazione setup per team

**Technical Notes**:
- Endpoint: `mcp.hubspot.com`
- OAuth 2.0 (preparare per migrazione a OAuth 2.1 con PKCE)
- Scopes necessari: `crm.objects.contacts.read`, `crm.objects.companies.read`, `crm.objects.deals.read`

---

#### Task 0.2: Implement MCP Client Wrapper
**ID**: HS-0.2
**Priority**: P1 (High)
**Estimate**: 5 points
**Assignee**: Backend Engineer
**Dependencies**: HS-0.1

**Description**:
Creare wrapper Python per HubSpot MCP client con metodi per fetch contacts, companies, deals.

**Acceptance Criteria**:
- [ ] `HubSpotMCPClient` class implementata
- [ ] Metodi: `get_contact()`, `get_company()`, `get_deal()`, `search_companies()`
- [ ] Error handling per MCP connection failures
- [ ] Retry logic per transient errors
- [ ] Unit tests con mock MCP responses
- [ ] Integration test con HubSpot sandbox

**Technical Notes**:
```python
class HubSpotMCPClient:
    async def connect(self, access_token, portal_id)
    async def get_contact(self, session, contact_id)
    async def search_companies(self, session, query)
```

---

#### Task 0.3: Setup Developer MCP Server
**ID**: HS-0.3
**Priority**: P2 (Medium)
**Estimate**: 2 points
**Assignee**: DevOps/Backend
**Dependencies**: None

**Description**:
Setup Developer MCP Server (Local) per accelerare sviluppo con CLI.

**Acceptance Criteria**:
- [ ] HubSpot CLI v7.60.0+ installato
- [ ] `hs mcp setup` eseguito
- [ ] Developer MCP server funzionante
- [ ] Team training su uso Developer MCP
- [ ] Documentazione comandi utili

**Technical Notes**:
- Comando: `hs mcp setup`
- Selezionare tools: scaffolding, deploy, documentation
- Testare con AI client (Claude Desktop, Cursor, etc.)

---

### EPIC 1: Database Schema & Models

#### Task 1.1: Design Database Schema
**ID**: HS-1.1  
**Priority**: P0 (Critical)  
**Estimate**: 5 points  
**Assignee**: Backend Engineer  
**Dependencies**: None

**Description**:
Design complete database schema for HubSpot integration including credentials, publications, metadata, and events tables.

**Acceptance Criteria**:
- [ ] Schema includes all 4 tables (credentials, publications, metadata, events)
- [ ] Multi-tenant isolation with tenant_id on all tables
- [ ] Proper indexes for performance (tenant_id, status, created_at)
- [ ] Foreign key constraints defined
- [ ] Encryption strategy for access_token defined
- [ ] Schema reviewed and approved by team

**Technical Notes**:
- Use UUID for all primary keys
- JSONB for flexible metadata
- TIMESTAMPTZ for all timestamps
- GIN indexes for JSONB columns

---

#### Task 1.2: Create Database Migration
**ID**: HS-1.2  
**Priority**: P0 (Critical)  
**Estimate**: 3 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-1.1

**Description**:
Create SQL migration script (004_create_hubspot_integration.sql) with all tables, indexes, and helper functions.

**Acceptance Criteria**:
- [ ] Migration script runs without errors
- [ ] All tables created with correct schema
- [ ] Indexes created
- [ ] Helper functions for encryption/decryption
- [ ] Rollback script provided
- [ ] Migration tested on dev database

---

#### Task 1.3: Create Domain Models (Python)
**ID**: HS-1.3  
**Priority**: P0 (Critical)  
**Estimate**: 5 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-1.1

**Description**:
Create Pydantic models for HubSpot domain entities (HubSpotCredential, ContentPublication, PublicationMetadata, PublicationEvent).

**Acceptance Criteria**:
- [ ] All domain models created with proper types
- [ ] Enums for HubSpotAuthType, HubSpotPlatform, PublicationStatus
- [ ] Validation rules implemented
- [ ] to_dict() and from_dict() methods
- [ ] Unit tests for models (>80% coverage)
- [ ] Documentation strings

**Files to Create**:
- `onboarding/domain/hubspot_models.py`

---

#### Task 1.4: Create TypeScript Types
**ID**: HS-1.4  
**Priority**: P1 (High)  
**Estimate**: 3 points  
**Assignee**: Frontend Engineer  
**Dependencies**: HS-1.3

**Description**:
Create TypeScript interfaces matching Python domain models for frontend.

**Acceptance Criteria**:
- [ ] All interfaces match Python models
- [ ] Enums for platform, status, auth type
- [ ] Zod schemas for runtime validation
- [ ] Export from central types file

**Files to Create**:
- `onboarding-frontend/src/types/hubspot.ts`

---

#### Task 1.5: Create Repository Layer
**ID**: HS-1.5  
**Priority**: P0 (Critical)  
**Estimate**: 8 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-1.2, HS-1.3

**Description**:
Implement repository classes for HubSpot credentials and publications with full CRUD operations.

**Acceptance Criteria**:
- [ ] HubSpotCredentialRepository with get, create, update, revoke
- [ ] ContentPublicationRepository with create, update_status, get_pending, get_failed
- [ ] PublicationMetadataRepository
- [ ] Proper error handling
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests with Supabase

**Files to Create**:
- `onboarding/infrastructure/repositories/hubspot_credential_repository.py`
- `onboarding/infrastructure/repositories/content_publication_repository.py`

---

### EPIC 2: HubSpot Adapter & Blog Publishing

#### Task 2.1: Create HubSpot Adapter Base
**ID**: HS-2.1  
**Priority**: P0 (Critical)  
**Estimate**: 8 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-1.5

**Description**:
Create HubSpotAdapter class with authentication, rate limiting, and error handling.

**Acceptance Criteria**:
- [ ] Adapter follows existing pattern (BrevoAdapter, CgsAdapter)
- [ ] Support for Private App token authentication
- [ ] Rate limiting (100 req/10s, 10k/day)
- [ ] Exponential backoff on 429 errors
- [ ] Comprehensive error handling
- [ ] Logging and monitoring
- [ ] Unit tests with mocked HTTP calls

**Files to Create**:
- `onboarding/infrastructure/adapters/hubspot_adapter.py`

---

#### Task 2.2: Implement Blog Post Publishing
**ID**: HS-2.2  
**Priority**: P0 (Critical)  
**Estimate**: 8 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-2.1

**Description**:
Implement publish_blog_post() method with full HubSpot Blog API integration.

**Acceptance Criteria**:
- [ ] POST to /content/api/v2/blog-posts works
- [ ] All required fields mapped (name, post_body, blog_author_id, content_group_id)
- [ ] Optional fields supported (meta_description, featured_image, tags)
- [ ] State management (DRAFT, PUBLISHED)
- [ ] Returns HubSpot blog post ID and URL
- [ ] Error handling for API failures
- [ ] Integration tests with HubSpot sandbox

**API Endpoint**: `POST https://api.hubapi.com/content/api/v2/blog-posts`

---

#### Task 2.3: Markdown to HTML Conversion
**ID**: HS-2.3  
**Priority**: P0 (Critical)  
**Estimate**: 5 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-2.2

**Description**:
Implement robust Markdown → HTML conversion with HubSpot-compatible formatting.

**Acceptance Criteria**:
- [ ] Use markdown library (markdown-it or marked)
- [ ] Preserve headings, lists, links, images
- [ ] Code blocks with syntax highlighting
- [ ] Blockquotes and tables
- [ ] Sanitize HTML to prevent XSS
- [ ] Unit tests with various Markdown samples
- [ ] Preview functionality

**Files to Create**:
- `onboarding/infrastructure/converters/markdown_to_html.py`

---

#### Task 2.4: Content Metadata Extraction
**ID**: HS-2.4  
**Priority**: P1 (High)  
**Estimate**: 3 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-2.3

**Description**:
Extract SEO metadata from content (meta description, featured image, tags) for HubSpot.

**Acceptance Criteria**:
- [ ] Extract meta description from first paragraph (150-160 chars)
- [ ] Extract featured image from content or metadata
- [ ] Extract tags from content.tags
- [ ] Generate canonical URL
- [ ] Fallback values for missing metadata

---

#### Task 2.5: Retry Logic & Error Handling
**ID**: HS-2.5  
**Priority**: P0 (Critical)  
**Estimate**: 5 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-2.2

**Description**:
Implement robust retry logic with exponential backoff for failed publications.

**Acceptance Criteria**:
- [ ] Retry on transient errors (429, 500, 502, 503, 504)
- [ ] Exponential backoff (1s, 2s, 4s, 8s, 16s)
- [ ] Max 5 retries
- [ ] Don't retry on 4xx errors (except 429)
- [ ] Update publication status on each retry
- [ ] Log all retry attempts
- [ ] Alert on max retries exceeded

---

### EPIC 3: Use Cases & API Endpoints

#### Task 3.1: PublishToHubSpotUseCase
**ID**: HS-3.1  
**Priority**: P0 (Critical)  
**Estimate**: 8 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-2.5

**Description**:
Create use case orchestrating the complete publication flow.

**Acceptance Criteria**:
- [ ] Get content by ID
- [ ] Get HubSpot credentials for tenant
- [ ] Convert content format
- [ ] Create publication record
- [ ] Publish to HubSpot
- [ ] Update publication status
- [ ] Track publication event
- [ ] Handle errors gracefully
- [ ] Unit tests with mocked dependencies

**Files to Create**:
- `onboarding/application/use_cases/publish_to_hubspot.py`

---

#### Task 3.2: API Endpoints for Publishing
**ID**: HS-3.2  
**Priority**: P0 (Critical)  
**Estimate**: 5 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-3.1

**Description**:
Create FastAPI endpoints for triggering and managing publications.

**Acceptance Criteria**:
- [ ] POST /content/{id}/publish/hubspot - Trigger publication
- [ ] GET /publications/{id} - Get publication status
- [ ] GET /publications - List publications (with filters)
- [ ] POST /publications/{id}/retry - Retry failed publication
- [ ] DELETE /publications/{id} - Cancel scheduled publication
- [ ] Proper request/response models
- [ ] OpenAPI documentation
- [ ] Integration tests

**Files to Modify**:
- `onboarding/api/endpoints.py`

---

#### Task 3.3: Configuration Management
**ID**: HS-3.3  
**Priority**: P0 (Critical)  
**Estimate**: 3 points  
**Assignee**: Backend Engineer  
**Dependencies**: None

**Description**:
Add HubSpot configuration to settings with environment variables.

**Acceptance Criteria**:
- [ ] HUBSPOT_API_KEY in settings
- [ ] HUBSPOT_PORTAL_ID in settings
- [ ] HUBSPOT_BASE_URL (default: https://api.hubapi.com)
- [ ] HUBSPOT_TIMEOUT (default: 30s)
- [ ] HUBSPOT_RATE_LIMIT_PER_SECOND (default: 10)
- [ ] Validation for required settings
- [ ] .env.example updated

**Files to Modify**:
- `onboarding/config/settings.py`
- `onboarding/.env.example`

---

### EPIC 4: Frontend Integration

#### Task 4.1: Publication UI Component
**ID**: HS-4.1  
**Priority**: P1 (High)  
**Estimate**: 8 points  
**Assignee**: Frontend Engineer  
**Dependencies**: HS-3.2

**Description**:
Create UI component for triggering HubSpot publication from content view.

**Acceptance Criteria**:
- [ ] "Publish to HubSpot" button on content card
- [ ] Modal with publication options (platform, metadata, scheduling)
- [ ] Form validation
- [ ] Loading states
- [ ] Success/error notifications
- [ ] Confirmation dialog
- [ ] Responsive design

**Files to Create**:
- `onboarding-frontend/src/components/publishing/PublishToHubSpotButton.tsx`
- `onboarding-frontend/src/components/publishing/PublishModal.tsx`

---

#### Task 4.2: Publication Status Dashboard
**ID**: HS-4.2  
**Priority**: P1 (High)  
**Estimate**: 8 points  
**Assignee**: Frontend Engineer  
**Dependencies**: HS-4.1

**Description**:
Create dashboard showing all publications with status, filters, and actions.

**Acceptance Criteria**:
- [ ] Table view with columns: content, platform, status, published_at, actions
- [ ] Filters: status, platform, date range
- [ ] Status badges with colors (pending, publishing, published, failed)
- [ ] Retry button for failed publications
- [ ] View details modal
- [ ] Pagination
- [ ] Real-time updates (polling or WebSocket)

**Files to Create**:
- `onboarding-frontend/src/pages/PublicationsDashboard.tsx`
- `onboarding-frontend/src/components/publishing/PublicationTable.tsx`

---

#### Task 4.3: State Management for Publications
**ID**: HS-4.3  
**Priority**: P1 (High)  
**Estimate**: 3 points  
**Assignee**: Frontend Engineer  
**Dependencies**: HS-4.1

**Description**:
Create Zustand store for managing publication state.

**Acceptance Criteria**:
- [ ] Store for publications list
- [ ] Actions: publish, retry, cancel, refresh
- [ ] Optimistic updates
- [ ] Error handling
- [ ] Loading states
- [ ] Cache invalidation

**Files to Create**:
- `onboarding-frontend/src/store/publicationsStore.ts`

---

### EPIC 5: OAuth & Multi-Tenant Support

#### Task 5.1: OAuth 2.0 Flow Implementation
**ID**: HS-5.1  
**Priority**: P1 (High)  
**Estimate**: 13 points  
**Assignee**: Full-stack Engineer  
**Dependencies**: HS-3.3

**Description**:
Implement complete OAuth 2.0 authorization flow for HubSpot.

**Acceptance Criteria**:
- [ ] OAuth authorization URL generation
- [ ] Callback endpoint to receive authorization code
- [ ] Exchange code for access + refresh tokens
- [ ] Store tokens securely (encrypted)
- [ ] Associate tokens with tenant
- [ ] Handle OAuth errors
- [ ] Revoke token endpoint
- [ ] Integration tests

**Files to Create**:
- `onboarding/infrastructure/auth/hubspot_oauth.py`
- `onboarding/api/oauth_endpoints.py`

**OAuth Flow**:
1. User clicks "Connect HubSpot"
2. Redirect to HubSpot authorization URL
3. User authorizes app
4. HubSpot redirects to callback with code
5. Exchange code for tokens
6. Store tokens for tenant

---

#### Task 5.2: Token Refresh Automation
**ID**: HS-5.2  
**Priority**: P0 (Critical)  
**Estimate**: 8 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-5.1

**Description**:
Implement automatic token refresh before expiration (6 hours).

**Acceptance Criteria**:
- [ ] Background job checks token expiration every hour
- [ ] Refresh tokens 30 minutes before expiration
- [ ] Update stored tokens
- [ ] Retry on refresh failure
- [ ] Alert on refresh failure
- [ ] Fallback to re-authorization if refresh fails
- [ ] Unit tests

**Files to Create**:
- `onboarding/workers/hubspot_token_refresher.py`

---

#### Task 5.3: Multi-Tenant Credential Management
**ID**: HS-5.3  
**Priority**: P1 (High)  
**Estimate**: 5 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-5.1

**Description**:
Implement UI and API for managing HubSpot credentials per tenant.

**Acceptance Criteria**:
- [ ] API endpoint to list credentials for tenant
- [ ] API endpoint to add new credential (OAuth or Private App)
- [ ] API endpoint to revoke credential
- [ ] Frontend UI for credential management
- [ ] Credential status indicators (active, expired, revoked)
- [ ] Audit log for credential changes

---

#### Task 5.4: Tenant Isolation Testing
**ID**: HS-5.4  
**Priority**: P0 (Critical)  
**Estimate**: 5 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-5.3

**Description**:
Comprehensive testing to ensure tenant isolation in publications.

**Acceptance Criteria**:
- [ ] Test: Tenant A cannot publish with Tenant B's credentials
- [ ] Test: Tenant A cannot see Tenant B's publications
- [ ] Test: Tenant A cannot retry Tenant B's failed publications
- [ ] Test: Token refresh only affects correct tenant
- [ ] Security audit passed
- [ ] Penetration testing passed

---

### EPIC 6: Scheduling & Social Media

#### Task 6.1: Scheduled Publishing
**ID**: HS-6.1  
**Priority**: P2 (Medium)  
**Estimate**: 8 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-3.1

**Description**:
Implement scheduled publishing with background job processing.

**Acceptance Criteria**:
- [ ] Accept scheduled_at parameter in publish API
- [ ] Create publication with status=SCHEDULED
- [ ] Background job checks for due publications every minute
- [ ] Publish when scheduled_at is reached
- [ ] Update status to PUBLISHING → PUBLISHED
- [ ] Handle timezone conversions
- [ ] Cancel scheduled publication endpoint

**Files to Create**:
- `onboarding/workers/scheduled_publisher.py`

---

#### Task 6.2: Social Media Publishing (LinkedIn)
**ID**: HS-6.2  
**Priority**: P2 (Medium)  
**Estimate**: 8 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-2.1

**Description**:
Implement social media publishing to LinkedIn via HubSpot Social API.

**Acceptance Criteria**:
- [ ] POST to /social/v1/broadcasts
- [ ] Support text-only posts
- [ ] Support posts with link
- [ ] Support posts with image
- [ ] Channel selection (LinkedIn account)
- [ ] Scheduling support
- [ ] Character limit validation (3000 chars)
- [ ] Integration tests

**API Endpoint**: `POST https://api.hubapi.com/social/v1/broadcasts`

---

#### Task 6.3: Social Media Publishing (Twitter/Facebook)
**ID**: HS-6.3  
**Priority**: P3 (Low)  
**Estimate**: 5 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-6.2

**Description**:
Extend social media publishing to Twitter and Facebook.

**Acceptance Criteria**:
- [ ] Twitter support (280 char limit)
- [ ] Facebook support
- [ ] Platform-specific validation
- [ ] Platform-specific formatting
- [ ] Integration tests

---

### EPIC 7: Performance Tracking & Analytics

#### Task 7.1: HubSpot Analytics API Integration
**ID**: HS-7.1  
**Priority**: P2 (Medium)  
**Estimate**: 8 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-2.2

**Description**:
Integrate HubSpot Analytics API to fetch performance metrics for published content.

**Acceptance Criteria**:
- [ ] Fetch blog post analytics (views, CTR, time on page)
- [ ] Fetch social post analytics (impressions, clicks, engagement)
- [ ] Store metrics in publication_metadata
- [ ] Background job syncs metrics daily
- [ ] API endpoint to get latest metrics
- [ ] Integration tests

**API Endpoint**: `GET https://api.hubapi.com/analytics/v2/reports`

---

#### Task 7.2: Performance Dashboard
**ID**: HS-7.2  
**Priority**: P2 (Medium)  
**Estimate**: 8 points  
**Assignee**: Frontend Engineer  
**Dependencies**: HS-7.1

**Description**:
Create dashboard showing performance metrics for published content.

**Acceptance Criteria**:
- [ ] Charts: views over time, CTR, engagement rate
- [ ] Filters: date range, platform, content type
- [ ] Top performing content list
- [ ] Comparison view (content A vs B)
- [ ] Export to CSV
- [ ] Responsive design

**Files to Create**:
- `onboarding-frontend/src/pages/PerformanceDashboard.tsx`

---

#### Task 7.3: Integration with Adaptive Cards
**ID**: HS-7.3  
**Priority**: P2 (Medium)  
**Estimate**: 5 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-7.1, Adaptive Cards Phase 3

**Description**:
Integrate publication data with Adaptive Cards system (CampaignCard, PerformanceCard).

**Acceptance Criteria**:
- [ ] CampaignCard includes publications array
- [ ] PerformanceCard aggregates HubSpot metrics
- [ ] Card relationships link content to publications
- [ ] Auto-update cards when publication completes
- [ ] Integration tests

---

### EPIC 8: Advanced Features

#### Task 8.1: A/B Testing Framework
**ID**: HS-8.1  
**Priority**: P3 (Low)  
**Estimate**: 13 points  
**Assignee**: Full-stack Engineer  
**Dependencies**: HS-7.1

**Description**:
Implement A/B testing for content variants (different titles, images, CTAs).

**Acceptance Criteria**:
- [ ] Create content variants
- [ ] Publish variants to HubSpot
- [ ] Track performance per variant
- [ ] Statistical significance calculation
- [ ] Winner selection (manual or automatic)
- [ ] UI for creating and managing tests
- [ ] Integration tests

---

#### Task 8.2: Bulk Publishing
**ID**: HS-8.2  
**Priority**: P3 (Low)  
**Estimate**: 5 points  
**Assignee**: Backend Engineer  
**Dependencies**: HS-3.1

**Description**:
Support publishing multiple content pieces in one operation.

**Acceptance Criteria**:
- [ ] API endpoint accepts array of content IDs
- [ ] Queue-based processing
- [ ] Progress tracking
- [ ] Batch status reporting
- [ ] Rate limiting respected
- [ ] Error handling per item

---

#### Task 8.3: Publication Templates
**ID**: HS-8.3  
**Priority**: P3 (Low)  
**Estimate**: 5 points  
**Assignee**: Full-stack Engineer  
**Dependencies**: HS-3.1

**Description**:
Create reusable publication templates (metadata presets, scheduling patterns).

**Acceptance Criteria**:
- [ ] Template CRUD API
- [ ] Template includes: platform, metadata, scheduling rules
- [ ] Apply template to publication
- [ ] Template library UI
- [ ] Share templates across team

---

## 📊 SUMMARY BY PHASE

### MVP (Phases 1-2): 55 points
- Database schema & models: 23 points
- HubSpot adapter & blog publishing: 32 points
- **Timeline**: 4-5 settimane
- **Team**: 1 Backend Engineer

### Production-Ready (Phases 1-4): 89 points
- MVP: 55 points
- API & Frontend: 18 points
- OAuth & Multi-tenant: 16 points
- **Timeline**: 7-8 settimane
- **Team**: 1 Backend + 1 Frontend Engineer

### Complete (All Phases): 134 points
- Production-Ready: 89 points
- Scheduling & Social: 21 points
- Performance Tracking: 21 points
- Advanced Features: 23 points (optional)
- **Timeline**: 10 settimane
- **Team**: 1 Backend + 1 Frontend + 0.5 DevOps

---

## 🎯 CRITICAL PATH

```
HS-1.1 (Schema Design)
  ↓
HS-1.2 (Migration) + HS-1.3 (Models)
  ↓
HS-1.5 (Repositories)
  ↓
HS-2.1 (Adapter Base)
  ↓
HS-2.2 (Blog Publishing) + HS-2.3 (Markdown Conversion)
  ↓
HS-2.5 (Retry Logic)
  ↓
HS-3.1 (Use Case)
  ↓
HS-3.2 (API Endpoints)
  ↓
HS-4.1 (Frontend UI)
  ↓
MVP COMPLETE ✅
```

---

**Roadmap Version**: 1.0  
**Last Updated**: 2025-10-25  
**Status**: Ready for Linear Import

