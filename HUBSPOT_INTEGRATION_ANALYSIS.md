# 🔍 HubSpot Integration - Analisi Completa

**Data**: 2025-10-25
**Obiettivo**: Pubblicazione nativa dei contenuti generati direttamente su HubSpot
**Approccio**: Utilizzo del **HubSpot MCP Server** (Model Context Protocol)

---

## 🆕 IMPORTANTE: HubSpot MCP Server

### Cos'è MCP (Model Context Protocol)?

**MCP** è un protocollo standardizzato che permette agli agenti AI (LLM) di:
- ✅ Richiedere e ricevere informazioni da sistemi esterni (come HubSpot)
- ✅ Eseguire azioni in modo sicuro e controllato
- ✅ Operare con contesto real-time dal CRM

### HubSpot MCP Server (Remote)

**Funzionalità**:
- 🔗 Bridge tra LLM e HubSpot account specifico
- 📊 Accesso real-time a dati CRM (contacts, companies, deals, tickets, etc.)
- 🔒 Autenticazione OAuth 2.0 (migrerà a OAuth 2.1 con PKCE)
- 📖 **Read-only** al momento (contacts, companies, deals, tickets, invoices, products, line items, quotes, subscriptions, orders, carts, users)

**Requisiti Tecnici**:
- HubSpot Developer Platform v2025.2+
- User-level App con OAuth scopes per CRM objects
- Endpoint: `mcp.hubspot.com`
- MCP-compatible client

**Limitazioni Attuali**:
- ❌ Solo **read-only** (nessuna scrittura/pubblicazione ancora)
- ❌ No accesso a Sensitive Data Properties
- ❌ No accesso a custom Sensitive Data

### Developer MCP Server (Local)

**Funzionalità**:
- 🛠️ CLI-based per sviluppo locale
- 📦 Scaffolding progetti HubSpot
- 📚 Accesso a documentazione developer
- 🚀 Deploy automatico

**Requisiti**:
- HubSpot CLI v7.60.0+
- Developer Platform v2025.2+
- Comando: `hs mcp setup`

---

## 📊 STATO ATTUALE DEL SISTEMA

### ✅ Cosa Abbiamo Già

#### 1. **Content Generation System**
- **Workflow Engine**: `onboarding_content_handler.py` con supporto per:
  - LinkedIn Post (200-400 parole)
  - LinkedIn Article (800-1500 parole)
  - Newsletter (1000-1500 parole)
  - Blog Post (1200-2000 parole, SEO-optimized)
- **Content Entity**: `core/domain/entities/content.py`
  - ContentType enum (article, newsletter, blog_post, social_media, email)
  - ContentStatus enum (draft, review, approved, published, archived)
  - ContentFormat enum (markdown, html, plain_text, json)
  - Metadata tracking (word_count, reading_time, tags, etc.)
- **Storage**: FileContentRepository salva contenuti in `data/output/`

#### 2. **External Service Integration Pattern**
- **Adapter Pattern**: Già implementato per:
  - `BrevoAdapter` (email delivery)
  - `CgsAdapter` (CGS API)
  - `PerplexityAdapter` (research)
  - `GeminiAdapter` (synthesis)
- **Pattern Comune**:
  ```python
  class ServiceAdapter:
      def __init__(self, api_key, base_url, timeout)
      def _build_headers(self) -> Dict[str, str]
      async def execute(self, payload) -> Dict[str, Any]
  ```

#### 3. **Configuration Management**
- **Settings Pattern**: Pydantic BaseSettings con env vars
- **Existing Integrations**:
  - `BREVO_API_KEY` (email)
  - `PERPLEXITY_API_KEY` (research)
  - `GEMINI_API_KEY` (LLM)
  - `SUPABASE_URL` + `SUPABASE_ANON_KEY` (database)

#### 4. **Multi-Tenant Awareness**
- **Supabase Schema**: Tabelle con `tenant_id` (in progress con Adaptive Cards)
- **Session Management**: `onboarding_sessions` table con tenant isolation
- **Company Context**: `company_contexts` table (da migrare a multi-tenant)

#### 5. **Workflow Orchestration**
- **Dynamic Workflows**: Registry pattern con `@register_workflow`
- **Task Orchestration**: `TaskOrchestrator` gestisce dipendenze e output
- **Agent System**: Multi-agent con RAG, research, copywriting

---

## ❌ COSA MANCA PER HUBSPOT

### 1. **HubSpot API Integration**
- ❌ Nessun adapter HubSpot esistente
- ❌ Nessuna configurazione HubSpot in settings
- ❌ Nessun credential management per HubSpot

### 2. **Publishing Workflow**
- ❌ Nessun workflow di pubblicazione
- ❌ Nessun tracking dello stato di pubblicazione
- ❌ Nessun error handling per pubblicazione fallita

### 3. **Content Mapping**
- ❌ Nessun mapping da Content entity a HubSpot objects
- ❌ Nessuna gestione metadati HubSpot (featured image, SEO, tags)
- ❌ Nessuna conversione formato (Markdown → HTML per HubSpot)

### 4. **Multi-Tenant Publishing**
- ❌ Nessun mapping tenant → HubSpot portal
- ❌ Nessuna gestione credenziali per-tenant
- ❌ Nessun isolation delle pubblicazioni

---

## 🎯 ARCHITETTURA PROPOSTA

### Approccio Ibrido: MCP + Direct API

Dato che **HubSpot MCP Server è attualmente read-only**, proponiamo un'architettura ibrida:

**Componenti**:

1. **HubSpot MCP Server (Remote)** → Per lettura dati CRM
   - Context-aware content generation
   - Validation dati pre-pubblicazione
   - Preview con dati reali
   - Fetch analytics post-pubblicazione

2. **Direct HubSpot API** → Per pubblicazione contenuti
   - Write operations (blog posts, social media)
   - Fino a quando MCP supporterà write operations

3. **Developer MCP Server (Local)** → Per sviluppo
   - Scaffolding progetti
   - Deploy automatico
   - Accesso documentazione

**Vantaggi**:
- ✅ Sfrutta MCP per context-aware generation
- ✅ Usa Direct API per pubblicazione (necessario al momento)
- ✅ Preparato per migrazione completa a MCP quando disponibile
- ✅ Developer MCP accelera sviluppo

**Roadmap MCP**:
- **Fase 1** (MVP): Direct API per tutto
- **Fase 2** (Hybrid): MCP read + Direct API write
- **Fase 3** (Future): Full MCP quando write operations disponibili

---

## 🎯 REQUISITI TECNICI

### HubSpot API Endpoints Necessari

#### 1. **Blog Posts API**
- **Endpoint**: `POST /content/api/v2/blog-posts`
- **Autenticazione**: OAuth 2.0 o Private App Access Token
- **Campi Richiesti**:
  - `name` (title)
  - `post_body` (HTML content)
  - `blog_author_id`
  - `content_group_id` (blog ID)
- **Campi Opzionali**:
  - `meta_description` (SEO)
  - `featured_image` (URL)
  - `tag_ids` (array)
  - `publish_date` (timestamp)
  - `state` (DRAFT, PUBLISHED, SCHEDULED)

#### 2. **Social Media API** (LinkedIn, Facebook, Twitter)
- **Endpoint**: `POST /social/v1/broadcasts`
- **Campi**:
  - `channelGuid` (social account ID)
  - `message` (post text)
  - `linkUrl` (optional)
  - `photoUrl` (optional)
  - `triggerAt` (scheduling)

#### 3. **Email API** (Marketing Emails)
- **Endpoint**: `POST /marketing-emails/v1/emails`
- **Campi**:
  - `name`
  - `subject`
  - `emailBody` (HTML)
  - `from_name`
  - `reply_to`

#### 4. **Landing Pages API**
- **Endpoint**: `POST /content/api/v2/pages`
- **Campi**: Simili a blog posts

### Autenticazione

#### Opzione 1: Private App Access Token (Raccomandato per MVP)
- **Pro**: Semplice, nessun OAuth flow
- **Con**: Un token per portal, scope limitati
- **Setup**: HubSpot Settings → Integrations → Private Apps
- **Scopes Necessari**:
  - `content` (read/write)
  - `social` (read/write)
  - `marketing-email` (read/write)

#### Opzione 2: OAuth 2.0 (Production-Ready)
- **Pro**: Multi-tenant, user-level permissions, refresh tokens
- **Con**: Più complesso, richiede OAuth flow
- **Setup**: HubSpot Developer Account → Create App
- **Flow**:
  1. User authorizes app
  2. Get authorization code
  3. Exchange for access token + refresh token
  4. Store tokens per tenant
  5. Refresh when expired (6 hours)

---

## 🏗️ ARCHITETTURA DETTAGLIATA

### Integrazione MCP nel Sistema

**MCP Client Integration**:

```python
# onboarding/infrastructure/mcp/hubspot_mcp_client.py

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class HubSpotMCPClient:
    """Client per HubSpot MCP Server."""

    async def connect(self, access_token: str, portal_id: str):
        """Connect to HubSpot MCP server."""
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@hubspot/mcp-server"],
            env={
                "HUBSPOT_ACCESS_TOKEN": access_token,
                "HUBSPOT_PORTAL_ID": portal_id,
            }
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return session

    async def get_contact(self, session, contact_id: str):
        """Get contact via MCP."""
        result = await session.call_tool("get_contact", {"id": contact_id})
        return result

    async def search_companies(self, session, query: str):
        """Search companies via MCP."""
        result = await session.call_tool("search_companies", {"query": query})
        return result
```

**Use Case con MCP**:

```python
# onboarding/application/use_cases/publish_with_mcp_context.py

class PublishWithMCPContextUseCase:
    """Publish content using MCP for context."""

    async def execute(self, content_id: UUID, target_company_id: str):
        # 1. Get company context via MCP
        mcp_session = await self.mcp_client.connect(token, portal)
        company_data = await self.mcp_client.get_company(mcp_session, target_company_id)

        # 2. Enrich content with context
        enriched_content = await self.enrich_content(content, company_data)

        # 3. Publish via Direct API (MCP read-only al momento)
        result = await self.hubspot_adapter.publish_blog_post(enriched_content)

        # 4. Track publication
        await self.publication_repo.create(publication)

        return result
```

---

### Layer 1: Database Schema

```sql
-- HubSpot credentials per tenant
CREATE TABLE hubspot_credentials (
    credential_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    portal_id TEXT NOT NULL,
    auth_type TEXT NOT NULL, -- 'private_app' or 'oauth'
    access_token TEXT NOT NULL, -- Encrypted
    refresh_token TEXT, -- For OAuth
    token_expires_at TIMESTAMPTZ,
    scopes TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, portal_id)
);

-- Publication tracking
CREATE TABLE content_publications (
    publication_id UUID PRIMARY KEY,
    content_id UUID NOT NULL, -- FK to content
    tenant_id UUID NOT NULL,
    platform TEXT NOT NULL, -- 'hubspot_blog', 'hubspot_social', 'hubspot_email'
    platform_content_id TEXT, -- HubSpot blog post ID, broadcast ID, etc.
    platform_url TEXT, -- Published URL
    status TEXT NOT NULL, -- 'pending', 'publishing', 'published', 'failed', 'scheduled'
    scheduled_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Publication metadata (SEO, images, tags)
CREATE TABLE publication_metadata (
    metadata_id UUID PRIMARY KEY,
    publication_id UUID NOT NULL REFERENCES content_publications(publication_id),
    meta_description TEXT,
    featured_image_url TEXT,
    tags TEXT[],
    canonical_url TEXT,
    author_id TEXT, -- HubSpot author ID
    blog_id TEXT, -- HubSpot blog/content group ID
    custom_fields JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Publication events (audit log)
CREATE TABLE publication_events (
    event_id UUID PRIMARY KEY,
    publication_id UUID NOT NULL REFERENCES content_publications(publication_id),
    event_type TEXT NOT NULL, -- 'created', 'publishing', 'published', 'failed', 'retrying'
    event_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Layer 2: Domain Models

```python
# onboarding/domain/hubspot_models.py

class HubSpotAuthType(Enum):
    PRIVATE_APP = "private_app"
    OAUTH = "oauth"

class HubSpotPlatform(Enum):
    BLOG = "hubspot_blog"
    SOCIAL = "hubspot_social"
    EMAIL = "hubspot_email"
    LANDING_PAGE = "hubspot_landing_page"

class PublicationStatus(Enum):
    PENDING = "pending"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"

@dataclass
class HubSpotCredential:
    credential_id: UUID
    tenant_id: UUID
    portal_id: str
    auth_type: HubSpotAuthType
    access_token: str  # Encrypted
    refresh_token: Optional[str]
    token_expires_at: Optional[datetime]
    scopes: List[str]
    is_active: bool

@dataclass
class ContentPublication:
    publication_id: UUID
    content_id: UUID
    tenant_id: UUID
    platform: HubSpotPlatform
    platform_content_id: Optional[str]
    platform_url: Optional[str]
    status: PublicationStatus
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    metadata: Dict[str, Any]

@dataclass
class PublicationMetadata:
    meta_description: Optional[str]
    featured_image_url: Optional[str]
    tags: List[str]
    canonical_url: Optional[str]
    author_id: Optional[str]
    blog_id: Optional[str]
    custom_fields: Dict[str, Any]
```

### Layer 3: HubSpot Adapter (Direct API)

**Note**: Usa Direct API per write operations (MCP read-only al momento)

```python
# onboarding/infrastructure/adapters/hubspot_adapter.py

class HubSpotAdapter:
    """Adapter for HubSpot Direct API (write operations)."""

    def __init__(self, access_token: str, portal_id: str):
        self.access_token = access_token
        self.portal_id = portal_id
        self.base_url = "https://api.hubapi.com"
        self.rate_limiter = HubSpotRateLimiter()

    async def publish_blog_post(
        self,
        title: str,
        body_html: str,
        metadata: PublicationMetadata,
    ) -> Dict[str, Any]:
        """Publish blog post to HubSpot via Direct API."""
        # Rate limiting
        await self.rate_limiter.acquire()

        # Make request
        response = await self._make_request(
            "POST",
            "/content/api/v2/blog-posts",
            data={
                "name": title,
                "post_body": body_html,
                "blog_author_id": metadata.author_id,
                "content_group_id": metadata.blog_id,
                "meta_description": metadata.meta_description,
                "featured_image": metadata.featured_image_url,
                "tag_ids": metadata.tags,
            }
        )

        return response

    async def publish_social_post(
        self,
        channel_guid: str,
        message: str,
        link_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Publish social media post via Direct API."""
        pass

    async def schedule_publication(
        self,
        content_type: str,
        payload: Dict[str, Any],
        publish_at: datetime,
    ) -> Dict[str, Any]:
        """Schedule content for future publication."""
        pass
```

### Layer 4: Repository Layer

```python
# onboarding/infrastructure/repositories/hubspot_repository.py

class HubSpotCredentialRepository:
    async def get_by_tenant(self, tenant_id: UUID) -> Optional[HubSpotCredential]
    async def create(self, credential: HubSpotCredential) -> HubSpotCredential
    async def update_token(self, credential_id: UUID, access_token: str, expires_at: datetime)
    async def revoke(self, credential_id: UUID)

class ContentPublicationRepository:
    async def create(self, publication: ContentPublication) -> ContentPublication
    async def get_by_id(self, publication_id: UUID) -> Optional[ContentPublication]
    async def get_by_content_id(self, content_id: UUID) -> List[ContentPublication]
    async def update_status(self, publication_id: UUID, status: PublicationStatus, ...)
    async def get_pending(self, limit: int = 100) -> List[ContentPublication]
    async def get_failed(self, max_retries: int = 3) -> List[ContentPublication]
```

### Layer 5: Use Cases

```python
# onboarding/application/use_cases/publish_to_hubspot.py

class PublishToHubSpotUseCase:
    async def execute(
        self,
        content_id: UUID,
        tenant_id: UUID,
        platform: HubSpotPlatform,
        metadata: PublicationMetadata,
        schedule_at: Optional[datetime] = None,
    ) -> ContentPublication:
        """Publish content to HubSpot."""
        
        # 1. Get content
        # 2. Get HubSpot credentials
        # 3. Convert content format (Markdown → HTML)
        # 4. Create publication record
        # 5. Publish to HubSpot
        # 6. Update publication status
        # 7. Track event
        pass
```

### Layer 6: API Endpoints

```python
# onboarding/api/endpoints.py

@router.post("/content/{content_id}/publish/hubspot")
async def publish_to_hubspot(
    content_id: UUID,
    request: PublishToHubSpotRequest,
    tenant_id: UUID = Depends(get_current_tenant),
):
    """Publish content to HubSpot."""
    pass

@router.get("/publications/{publication_id}")
async def get_publication_status(publication_id: UUID):
    """Get publication status."""
    pass

@router.post("/publications/{publication_id}/retry")
async def retry_publication(publication_id: UUID):
    """Retry failed publication."""
    pass
```

---

## 🔄 INTEGRATION CON ADAPTIVE CARDS

### Come si Integra

1. **CampaignCard** → Traccia pubblicazioni
   ```json
   {
     "card_type": "campaign",
     "content": {
       "publications": [
         {
           "platform": "hubspot_blog",
           "url": "https://blog.company.com/post",
           "published_at": "2025-10-25T10:00:00Z",
           "performance": {"views": 1500, "ctr": 0.05}
         }
       ]
     }
   }
   ```

2. **PerformanceCard** → Aggrega metriche da HubSpot
   ```json
   {
     "card_type": "performance",
     "content": {
       "hubspot_blog": {
         "total_posts": 25,
         "avg_views": 1200,
         "avg_ctr": 0.04
       }
     }
   }
   ```

3. **Card Relationships** → Collega contenuto a pubblicazione
   ```
   ContentCard --derived_from--> CampaignCard
   PublicationEvent --references--> ContentCard
   ```

---

## 📈 SUCCESS METRICS

### MVP (Phase 1-2)
- ✅ Publish blog post to HubSpot (manual trigger)
- ✅ Track publication status
- ✅ Handle errors with retry
- ✅ Support single tenant (Private App token)

### Production-Ready (Phase 3)
- ✅ OAuth 2.0 multi-tenant support
- ✅ Schedule publications
- ✅ Publish to social media
- ✅ Automatic retry with exponential backoff
- ✅ Webhook integration for status updates

### Advanced (Phase 4-5)
- ✅ A/B testing (publish variants)
- ✅ Performance tracking from HubSpot
- ✅ Auto-optimization based on performance
- ✅ Bulk publishing
- ✅ Template library

---

## 🚨 RISCHI E MITIGAZIONI

### Rischio 1: Rate Limiting
- **HubSpot Limits**: 100 requests/10 seconds (burst), 10,000/day
- **Mitigazione**: 
  - Implement rate limiter
  - Queue system for bulk operations
  - Exponential backoff on 429 errors

### Rischio 2: Token Expiration
- **OAuth tokens**: Expire after 6 hours
- **Mitigazione**:
  - Automatic refresh before expiration
  - Fallback to refresh token
  - Alert on refresh failure

### Rischio 3: Content Format Mismatch
- **Problema**: Markdown → HTML conversion può perdere formattazione
- **Mitigazione**:
  - Use robust Markdown parser (markdown-it, marked)
  - Preview before publishing
  - Support custom HTML injection

### Rischio 4: Multi-Tenant Credential Leakage
- **Problema**: Credenziali di un tenant usate per altro tenant
- **Mitigazione**:
  - Strict tenant isolation in queries
  - Encrypt tokens at rest
  - Audit log per publication

---

## 🎯 PROSSIMI PASSI

1. ✅ **Analisi completata** (questo documento)
2. ⏭️ **Creare roadmap Linear** (prossimo step)
3. ⏭️ **Design database schema** (SQL migration)
4. ⏭️ **Implementare HubSpotAdapter** (MVP)
5. ⏭️ **Testing end-to-end**

---

**Documento creato**: 2025-10-25  
**Versione**: 1.0  
**Status**: ✅ Analisi Completa

