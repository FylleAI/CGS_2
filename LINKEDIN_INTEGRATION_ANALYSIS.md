# 🔵 LinkedIn Integration - Technical Analysis

**Data**: 2025-10-25  
**Versione**: 1.0  
**Status**: Planning Phase

---

## 📋 EXECUTIVE SUMMARY

### Obiettivo
Implementare la **pubblicazione nativa** dei contenuti generati direttamente sui profili **LinkedIn dei clienti** (membri e organizzazioni).

### Approccio
**Direct API** - LinkedIn non ha MCP server, quindi utilizziamo direttamente le LinkedIn REST APIs.

### Complessità
**MEDIA** - Più semplice di HubSpot:
- ✅ NO approvazione partner program necessaria
- ✅ Token più longevi (60 giorni vs 6 ore HubSpot)
- ✅ API ben documentata
- ⚠️ Rate limits non documentati

### Timeline
- **MVP**: 3-4 settimane (39 points)
- **Production-Ready**: 5-6 settimane (59 points)
- **Complete**: 6-8 settimane (89 points)

---

## 🔍 STATO ATTUALE

### Cosa Abbiamo

#### 1. Content Generation System
- ✅ CGS agents generano contenuti (blog posts, social media)
- ✅ Output in formato Markdown
- ✅ Metadata (title, description, tags)

#### 2. Database Infrastructure
- ✅ PostgreSQL (Supabase)
- ✅ Multi-tenant architecture
- ✅ Credential storage (encrypted)

#### 3. Publishing Capabilities
- ✅ HubSpot integration (in planning)
- ❌ LinkedIn integration (da implementare)

### Cosa Manca

#### 1. LinkedIn OAuth Integration
- ❌ OAuth 2.0 flow (3-legged)
- ❌ Token storage & refresh
- ❌ Multi-tenant credential management

#### 2. LinkedIn API Adapter
- ❌ REST API client
- ❌ Media upload (images, videos)
- ❌ Post publishing
- ❌ Rate limiting

#### 3. UI Components
- ❌ "Connect LinkedIn" button
- ❌ OAuth callback handler
- ❌ Publication status tracking

---

## 🎯 REQUISITI TECNICI

### 1. LinkedIn API Access

#### A. Permissions (OAuth Scopes)

**Per Pubblicazione Organica** (✅ Self-service - NO approvazione):

| Scope | Descrizione | Tipo | Approvazione |
|-------|-------------|------|--------------|
| `w_member_social` | Pubblicare post per conto di un **membro** | 3-legged OAuth | ✅ Self-service |
| `r_member_social` | Leggere post di un membro | 3-legged OAuth | ❌ Restricted |
| `profile` | Nome, headline, foto del membro | 3-legged OAuth | ✅ Self-service |
| `email` | Email primaria del membro | 3-legged OAuth | ✅ Self-service |

**Per Pubblicazione Organization** (⚠️ Richiede ruolo admin):

| Scope | Descrizione | Tipo | Approvazione |
|-------|-------------|------|--------------|
| `w_organization_social` | Pubblicare post per conto di un'**organizzazione** | 3-legged OAuth | ⚠️ Ruolo admin richiesto |
| `r_organization_social` | Leggere post di un'organizzazione | 3-legged OAuth | ⚠️ Ruolo admin richiesto |

**✅ DECISIONE**: Iniziamo con `w_member_social` (self-service), aggiungiamo `w_organization_social` in Phase 2.

#### B. API Endpoints

**Base URL**: `https://api.linkedin.com/rest`

**Endpoints Principali**:

1. **OAuth**:
   - `GET https://www.linkedin.com/oauth/v2/authorization` - Authorization
   - `POST https://www.linkedin.com/oauth/v2/accessToken` - Token exchange
   - `POST https://www.linkedin.com/oauth/v2/accessToken` - Token refresh

2. **Posts**:
   - `POST /posts` - Create post
   - `GET /posts/{id}` - Get post
   - `GET /posts?author={urn}&q=author` - Find posts by author
   - `POST /posts/{id}` - Update post (PARTIAL_UPDATE)
   - `DELETE /posts/{id}` - Delete post

3. **Media**:
   - `POST /images` - Upload image
   - `POST /videos` - Upload video
   - `POST /documents` - Upload document

4. **Profile** (per ottenere author URN):
   - `GET /me` - Get authenticated user profile

#### C. Headers Richiesti

```http
Authorization: Bearer {ACCESS_TOKEN}
X-Restli-Protocol-Version: 2.0.0
Linkedin-Version: 202501  # Formato YYYYMM
Content-Type: application/json
```

---

### 2. OAuth 2.0 Flow

#### A. Authorization Flow (3-legged)

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Authorization Request                              │
│  GET https://www.linkedin.com/oauth/v2/authorization        │
│  ?response_type=code                                        │
│  &client_id={CLIENT_ID}                                     │
│  &redirect_uri={REDIRECT_URI}                               │
│  &scope=profile%20email%20w_member_social                   │
│  &state={RANDOM_STATE}                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  STEP 2: User Authorization                                 │
│  - User logs in to LinkedIn                                 │
│  - User approves permissions                                │
│  - LinkedIn redirects to REDIRECT_URI with code             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  STEP 3: Token Exchange                                     │
│  POST https://www.linkedin.com/oauth/v2/accessToken         │
│  grant_type=authorization_code                              │
│  code={AUTHORIZATION_CODE}                                  │
│  client_id={CLIENT_ID}                                      │
│  client_secret={CLIENT_SECRET}                              │
│  redirect_uri={REDIRECT_URI}                                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  STEP 4: Token Response                                     │
│  {                                                          │
│    "access_token": "...",                                   │
│    "expires_in": 5184000,  // 60 days                       │
│    "refresh_token": "...",                                  │
│    "refresh_token_expires_in": 31536000  // 365 days        │
│  }                                                          │
└──────────────────────────────────────────────────────────────┘
```

#### B. Token Refresh

```http
POST https://www.linkedin.com/oauth/v2/accessToken
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&refresh_token={REFRESH_TOKEN}
&client_id={CLIENT_ID}
&client_secret={CLIENT_SECRET}
```

**⚠️ IMPORTANTE**: LinkedIn sta migrando a **OAuth 2.1 con PKCE** (come HubSpot).

---

### 3. Content Types Supportati

| Tipo | Organic | Sponsored | Endpoint | Note |
|------|---------|-----------|----------|------|
| **Text only** | ✅ | ✅ | `/posts` | Semplice testo |
| **Single Image** | ✅ | ✅ | `/images` + `/posts` | Upload image prima |
| **Single Video** | ✅ | ✅ | `/videos` + `/posts` | Upload video prima |
| **Document** | ✅ | ✅ | `/documents` + `/posts` | PDF, PPT, DOCX |
| **Article** | ✅ | ✅ | `/posts` | Link esterno con preview |
| **Multi-Image** | ✅ | ❌ | `/posts` | Solo organic |
| **Poll** | ✅ | ❌ | `/posts` | Solo organic |
| **Carousel** | ❌ | ✅ | `/posts` | Solo sponsored |

**✅ MVP SCOPE**: Text, Single Image, Article

---

### 4. Rate Limits

**⚠️ PROBLEMA CRITICO**: LinkedIn **NON pubblica** i rate limits ufficiali!

**Cosa Sappiamo**:
- Rate limits variano per endpoint
- Dipendono dal tipo di app
- **Non documentati pubblicamente**
- Monitorare response headers: `X-RateLimit-*`

**Best Practices**:
- Implementa **exponential backoff**
- Queue system per gestire burst
- Considera **100 requests/10 seconds** come limite conservativo

**Mitigation**:
```python
class LinkedInRateLimiter:
    def __init__(self):
        self.requests = []
        self.max_requests = 100
        self.time_window = 10  # seconds
    
    async def acquire(self):
        now = time.time()
        # Remove old requests
        self.requests = [r for r in self.requests if now - r < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            wait_time = self.time_window - (now - self.requests[0])
            await asyncio.sleep(wait_time)
        
        self.requests.append(now)
```

---

## 🏗️ ARCHITETTURA PROPOSTA

### Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  - React Components (ConnectLinkedInButton, StatusTracker)  │
│  - OAuth Callback Handler                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  - PublishToLinkedInUseCase                                 │
│  - RefreshLinkedInTokenUseCase                              │
│  - ConnectLinkedInAccountUseCase                            │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     DOMAIN LAYER                             │
│  - LinkedInCredential (entity)                              │
│  - LinkedInPublication (entity)                             │
│  - LinkedInPublicationRepository (interface)                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│  - LinkedInAdapter (API client)                             │
│  - LinkedInOAuthService                                     │
│  - LinkedInRateLimiter                                      │
│  - PostgresLinkedInPublicationRepository                    │
└──────────────────────────────────────────────────────────────┘
```

---

### Database Schema

#### Table: `linkedin_credentials`

```sql
CREATE TABLE linkedin_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- LinkedIn Identity
    linkedin_person_urn VARCHAR(255) NOT NULL,  -- urn:li:person:ABC123
    linkedin_email VARCHAR(255),
    linkedin_name VARCHAR(255),
    
    -- OAuth Tokens (encrypted)
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_type VARCHAR(50) DEFAULT 'Bearer',
    
    -- Token Expiration
    access_token_expires_at TIMESTAMP NOT NULL,
    refresh_token_expires_at TIMESTAMP NOT NULL,
    
    -- Scopes
    scopes TEXT[] NOT NULL,  -- ['profile', 'email', 'w_member_social']
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(tenant_id, linkedin_person_urn),
    CHECK (access_token_expires_at > NOW()),
    CHECK (array_length(scopes, 1) > 0)
);

CREATE INDEX idx_linkedin_credentials_tenant ON linkedin_credentials(tenant_id);
CREATE INDEX idx_linkedin_credentials_user ON linkedin_credentials(user_id);
CREATE INDEX idx_linkedin_credentials_expires ON linkedin_credentials(access_token_expires_at);
```

#### Table: `linkedin_publications`

```sql
CREATE TABLE linkedin_publications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    credential_id UUID NOT NULL REFERENCES linkedin_credentials(id) ON DELETE CASCADE,
    
    -- Content Reference
    content_id UUID REFERENCES contents(id) ON DELETE SET NULL,
    
    -- LinkedIn Post Info
    linkedin_post_urn VARCHAR(255),  -- urn:li:share:123 or urn:li:ugcPost:123
    linkedin_post_url TEXT,
    
    -- Post Content
    post_type VARCHAR(50) NOT NULL,  -- 'text', 'image', 'video', 'article', 'multi_image'
    commentary TEXT NOT NULL,
    visibility VARCHAR(50) DEFAULT 'PUBLIC',  -- 'PUBLIC', 'CONNECTIONS'
    
    -- Media
    media_urns TEXT[],  -- ['urn:li:image:123', 'urn:li:video:456']
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  
    -- 'pending', 'publishing', 'published', 'failed', 'deleted'
    
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- Timestamps
    published_at TIMESTAMP,
    scheduled_for TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CHECK (status IN ('pending', 'publishing', 'published', 'failed', 'deleted')),
    CHECK (post_type IN ('text', 'image', 'video', 'article', 'multi_image', 'document')),
    CHECK (retry_count <= max_retries)
);

CREATE INDEX idx_linkedin_publications_tenant ON linkedin_publications(tenant_id);
CREATE INDEX idx_linkedin_publications_credential ON linkedin_publications(credential_id);
CREATE INDEX idx_linkedin_publications_status ON linkedin_publications(status);
CREATE INDEX idx_linkedin_publications_scheduled ON linkedin_publications(scheduled_for) 
    WHERE status = 'pending' AND scheduled_for IS NOT NULL;
```

---

## 📊 INTEGRATION WITH ADAPTIVE CARDS

### Card-Driven Publishing

```
┌─────────────────────────────────────────────────────────────┐
│              ADAPTIVE CARD: SocialMediaCard                  │
│  {                                                          │
│    "type": "SocialMediaCard",                               │
│    "platform": "linkedin",                                  │
│    "content": {                                             │
│      "text": "...",                                         │
│      "media": [...],                                        │
│      "hashtags": ["#AI", "#Tech"]                           │
│    },                                                       │
│    "targeting": {                                           │
│      "audience": "professionals",                           │
│      "tone": "professional"                                 │
│    },                                                       │
│    "performance": {                                         │
│      "engagement_rate": 0.0,                                │
│      "impressions": 0                                       │
│    }                                                        │
│  }                                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│         PublishToLinkedInUseCase                            │
│  - Read card content                                        │
│  - Format for LinkedIn API                                  │
│  - Publish via LinkedInAdapter                              │
│  - Update card performance                                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 PUBLISHING WORKFLOW

### Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: User Initiates Publishing                          │
│  - User clicks "Publish to LinkedIn"                        │
│  - Check if LinkedIn connected                              │
│  - If not: OAuth flow                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  STEP 2: Prepare Content                                    │
│  - Get content from Adaptive Card                           │
│  - Format commentary (text + hashtags + mentions)           │
│  - Identify media (images, videos)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  STEP 3: Upload Media (if needed)                           │
│  - Upload images via /rest/images                           │
│  - Upload videos via /rest/videos                           │
│  - Get media URNs                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  STEP 4: Publish Post                                       │
│  - POST /rest/posts                                         │
│  - Include media URNs                                       │
│  - Get post URN from response                               │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  STEP 5: Track Publication                                  │
│  - Save to linkedin_publications table                      │
│  - Update Adaptive Card performance                         │
│  - Notify user of success                                   │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚨 RISKS & MITIGATIONS

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Rate limiting** (non documentato) | High | Medium | Queue system + exponential backoff + monitoring |
| **Token expiration** (60 giorni) | Medium | High | Background refresh job (7 giorni prima) |
| **OAuth 2.1 migration** | Medium | Medium | Monitor changelog, prepare PKCE |
| **User revoca permessi** | Low | Medium | Handle 401, re-auth flow |
| **Media upload failures** | Medium | Medium | Retry logic, validation pre-upload |
| **API changes** | Medium | Low | Version pinning, integration tests |

---

## 📈 SUCCESS METRICS

### MVP (Phase 1-2)
- ✅ OAuth connection success rate >90%
- ✅ Text post publish success rate >95%
- ✅ Image post publish success rate >90%
- ✅ Average publish time <15 seconds

### Production-Ready (Phase 1-3)
- ✅ Token refresh success rate >99%
- ✅ Multi-tenant isolation 100%
- ✅ Error recovery rate >85%
- ✅ Zero credential leaks

### Complete (All Phases)
- ✅ Scheduled publish accuracy >95%
- ✅ Video publish success >85%
- ✅ System uptime >99.5%
- ✅ User satisfaction >4.5/5

---

**Next**: See `LINEAR_ROADMAP_LINKEDIN_INTEGRATION.md` for detailed implementation plan.

