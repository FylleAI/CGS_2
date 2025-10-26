# 🔵 LinkedIn Integration - Linear Roadmap

**Project**: LinkedIn Direct Publishing  
**Timeline**: 6-8 settimane  
**Total Story Points**: 89  
**Team Size**: 2-3 developers

---

## 📊 OVERVIEW

### Milestones

| Milestone | Descrizione | Story Points | Duration | Dependencies |
|-----------|-------------|--------------|----------|--------------|
| **M1: Foundation** | OAuth + Database | 18 pts | 1-2 weeks | None |
| **M2: Core Publishing** | Text & Image posts | 21 pts | 2 weeks | M1 |
| **M3: Production Ready** | Error handling + Monitoring | 20 pts | 1-2 weeks | M2 |
| **M4: Advanced Features** | Scheduling + Multi-media | 15 pts | 1-2 weeks | M3 |
| **M5: Organization Support** | Company page publishing | 10 pts | 1 week | M2 |
| **M6: Analytics & Optimization** | Performance tracking | 5 pts | 1 week | M3 |

**Total**: 89 story points

---

## 🎯 EPICS

### EPIC 1: OAuth & Authentication (18 pts)
**Goal**: Implementare OAuth 2.0 flow per connettere account LinkedIn

**Tasks**:
- LI-1.1: Setup LinkedIn App & Credentials
- LI-1.2: Implement OAuth Authorization Flow
- LI-1.3: Implement Token Exchange & Storage
- LI-1.4: Implement Token Refresh Logic
- LI-1.5: Create Database Schema for Credentials

---

### EPIC 2: Core Publishing (21 pts)
**Goal**: Pubblicare post text e image su LinkedIn

**Tasks**:
- LI-2.1: Create LinkedIn API Client
- LI-2.2: Implement Text Post Publishing
- LI-2.3: Implement Image Upload
- LI-2.4: Implement Image Post Publishing
- LI-2.5: Create Publication Tracking System

---

### EPIC 3: Error Handling & Resilience (20 pts)
**Goal**: Sistema robusto con retry logic e monitoring

**Tasks**:
- LI-3.1: Implement Rate Limiting
- LI-3.2: Implement Retry Logic with Exponential Backoff
- LI-3.3: Implement Error Handling & Logging
- LI-3.4: Create Background Job for Token Refresh
- LI-3.5: Setup Monitoring & Alerts

---

### EPIC 4: Advanced Publishing (15 pts)
**Goal**: Scheduling, video, multi-image support

**Tasks**:
- LI-4.1: Implement Scheduled Publishing
- LI-4.2: Implement Video Upload & Publishing
- LI-4.3: Implement Multi-Image Posts
- LI-4.4: Implement Article/Link Posts

---

### EPIC 5: Organization Publishing (10 pts)
**Goal**: Pubblicare su company pages

**Tasks**:
- LI-5.1: Implement Organization OAuth Flow
- LI-5.2: Implement Organization Post Publishing
- LI-5.3: Add Organization Selector UI

---

### EPIC 6: Analytics & Performance (5 pts)
**Goal**: Tracking performance e analytics

**Tasks**:
- LI-6.1: Implement Publication Performance Tracking
- LI-6.2: Create Analytics Dashboard

---

## 📋 DETAILED TASKS

### MILESTONE 1: Foundation (18 pts)

#### **LI-1.1: Setup LinkedIn App & Credentials**
- **Priority**: P0 (Critical)
- **Estimate**: 2 points
- **Assignee**: Backend Lead
- **Epic**: EPIC 1
- **Dependencies**: None

**Description**:
Setup LinkedIn Developer App e configurare credenziali OAuth.

**Acceptance Criteria**:
- [ ] LinkedIn Developer App creata
- [ ] Client ID e Client Secret ottenuti
- [ ] Redirect URI configurato
- [ ] Scopes configurati: `profile`, `email`, `w_member_social`
- [ ] Credenziali salvate in environment variables (`.env`)
- [ ] Documentazione setup completata

**Technical Notes**:
```bash
# .env
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_REDIRECT_URI=https://yourdomain.com/api/auth/linkedin/callback
```

---

#### **LI-1.2: Implement OAuth Authorization Flow**
- **Priority**: P0 (Critical)
- **Estimate**: 5 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 1
- **Dependencies**: LI-1.1

**Description**:
Implementare OAuth 2.0 authorization flow per ottenere authorization code.

**Acceptance Criteria**:
- [ ] Endpoint `/api/auth/linkedin/authorize` creato
- [ ] Genera authorization URL con state parameter
- [ ] Redirect user a LinkedIn authorization page
- [ ] State parameter validato per CSRF protection
- [ ] Error handling per authorization failures
- [ ] Unit tests scritti (coverage >80%)

**Technical Notes**:
```python
# core/infrastructure/adapters/linkedin_oauth_service.py
class LinkedInOAuthService:
    def get_authorization_url(self, tenant_id: str, user_id: str) -> str:
        state = self._generate_state(tenant_id, user_id)
        params = {
            'response_type': 'code',
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'redirect_uri': settings.LINKEDIN_REDIRECT_URI,
            'scope': 'profile email w_member_social',
            'state': state
        }
        return f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
```

---

#### **LI-1.3: Implement Token Exchange & Storage**
- **Priority**: P0 (Critical)
- **Estimate**: 5 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 1
- **Dependencies**: LI-1.2, LI-1.5

**Description**:
Implementare token exchange e storage sicuro dei token.

**Acceptance Criteria**:
- [ ] Endpoint `/api/auth/linkedin/callback` creato
- [ ] Exchange authorization code per access token
- [ ] Decrypt e store access_token e refresh_token
- [ ] Store token expiration timestamps
- [ ] Get LinkedIn user profile (person URN)
- [ ] Save to `linkedin_credentials` table
- [ ] Encryption at rest per tokens
- [ ] Unit tests + integration tests

**Technical Notes**:
```python
async def exchange_code_for_token(self, code: str) -> LinkedInTokenResponse:
    response = await self.http_client.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'client_secret': settings.LINKEDIN_CLIENT_SECRET,
            'redirect_uri': settings.LINKEDIN_REDIRECT_URI
        }
    )
    return LinkedInTokenResponse(**response.json())
```

---

#### **LI-1.4: Implement Token Refresh Logic**
- **Priority**: P0 (Critical)
- **Estimate**: 3 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 1
- **Dependencies**: LI-1.3

**Description**:
Implementare automatic token refresh prima della scadenza.

**Acceptance Criteria**:
- [ ] Metodo `refresh_access_token()` implementato
- [ ] Refresh automatico 7 giorni prima della scadenza
- [ ] Update `linkedin_credentials` con nuovi token
- [ ] Handle refresh token expiration (re-auth required)
- [ ] Logging per refresh successes/failures
- [ ] Unit tests per refresh logic

**Technical Notes**:
```python
async def refresh_access_token(self, credential_id: UUID) -> None:
    credential = await self.repo.get_credential(credential_id)
    
    response = await self.http_client.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        data={
            'grant_type': 'refresh_token',
            'refresh_token': credential.refresh_token,
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'client_secret': settings.LINKEDIN_CLIENT_SECRET
        }
    )
    
    await self.repo.update_tokens(credential_id, response.json())
```

---

#### **LI-1.5: Create Database Schema for Credentials**
- **Priority**: P0 (Critical)
- **Estimate**: 3 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 1
- **Dependencies**: None

**Description**:
Creare database schema per LinkedIn credentials e publications.

**Acceptance Criteria**:
- [ ] Migration creata per `linkedin_credentials` table
- [ ] Migration creata per `linkedin_publications` table
- [ ] Indexes creati per performance
- [ ] Constraints e validations aggiunti
- [ ] Encryption configurata per sensitive fields
- [ ] Rollback script testato
- [ ] Documentation aggiornata

**Technical Notes**:
See `DATABASE_SCHEMA_LINKEDIN_INTEGRATION.sql` (to be created)

---

### MILESTONE 2: Core Publishing (21 pts)

#### **LI-2.1: Create LinkedIn API Client**
- **Priority**: P0 (Critical)
- **Estimate**: 5 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 2
- **Dependencies**: LI-1.3

**Description**:
Creare HTTP client per LinkedIn REST API con authentication.

**Acceptance Criteria**:
- [ ] `LinkedInAPIClient` class creata
- [ ] Automatic token injection in headers
- [ ] Handle 401 (token expired) → trigger refresh
- [ ] Handle 429 (rate limit) → exponential backoff
- [ ] Request/response logging
- [ ] Timeout configuration
- [ ] Unit tests con mocked responses

**Technical Notes**:
```python
class LinkedInAPIClient:
    BASE_URL = "https://api.linkedin.com/rest"
    
    def __init__(self, credential: LinkedInCredential):
        self.credential = credential
        self.session = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                'X-Restli-Protocol-Version': '2.0.0',
                'Linkedin-Version': '202501'
            },
            timeout=30.0
        )
    
    async def _request(self, method: str, path: str, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.credential.access_token}'
        
        response = await self.session.request(method, path, headers=headers, **kwargs)
        
        if response.status_code == 401:
            # Token expired, refresh needed
            raise TokenExpiredError()
        elif response.status_code == 429:
            # Rate limited
            raise RateLimitError()
        
        response.raise_for_status()
        return response.json()
```

---

#### **LI-2.2: Implement Text Post Publishing**
- **Priority**: P0 (Critical)
- **Estimate**: 5 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 2
- **Dependencies**: LI-2.1

**Description**:
Implementare pubblicazione di text-only posts su LinkedIn.

**Acceptance Criteria**:
- [ ] `publish_text_post()` method implementato
- [ ] POST request a `/rest/posts` funzionante
- [ ] Get author URN from `/rest/me`
- [ ] Handle visibility settings (PUBLIC, CONNECTIONS)
- [ ] Return post URN e URL
- [ ] Error handling per API failures
- [ ] Integration tests con LinkedIn sandbox

**Technical Notes**:
```python
async def publish_text_post(
    self,
    commentary: str,
    visibility: str = "PUBLIC"
) -> LinkedInPost:
    # Get author URN
    me = await self._request('GET', '/me')
    author_urn = f"urn:li:person:{me['id']}"
    
    # Create post
    payload = {
        "author": author_urn,
        "commentary": commentary,
        "visibility": visibility,
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED"
    }
    
    response = await self._request('POST', '/posts', json=payload)
    return LinkedInPost.from_api_response(response)
```

---

#### **LI-2.3: Implement Image Upload**
- **Priority**: P0 (Critical)
- **Estimate**: 5 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 2
- **Dependencies**: LI-2.1

**Description**:
Implementare upload di immagini su LinkedIn.

**Acceptance Criteria**:
- [ ] `upload_image()` method implementato
- [ ] Initialize upload via `/rest/images?action=initializeUpload`
- [ ] Upload image binary to upload URL
- [ ] Return image URN
- [ ] Support JPEG, PNG formats
- [ ] Validate image size (<5MB)
- [ ] Error handling per upload failures
- [ ] Integration tests

**Technical Notes**:
```python
async def upload_image(self, image_data: bytes, filename: str) -> str:
    # Step 1: Initialize upload
    init_response = await self._request(
        'POST',
        '/images?action=initializeUpload',
        json={
            "initializeUploadRequest": {
                "owner": self.author_urn
            }
        }
    )
    
    upload_url = init_response['value']['uploadUrl']
    image_urn = init_response['value']['image']
    
    # Step 2: Upload binary
    async with httpx.AsyncClient() as client:
        await client.put(
            upload_url,
            content=image_data,
            headers={'Content-Type': 'application/octet-stream'}
        )
    
    return image_urn
```

---

#### **LI-2.4: Implement Image Post Publishing**
- **Priority**: P0 (Critical)
- **Estimate**: 3 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 2
- **Dependencies**: LI-2.2, LI-2.3

**Description**:
Implementare pubblicazione di post con immagini.

**Acceptance Criteria**:
- [ ] `publish_image_post()` method implementato
- [ ] Upload image first, then create post
- [ ] Include image URN in post payload
- [ ] Support image title/description
- [ ] Return post URN e URL
- [ ] Integration tests

**Technical Notes**:
```python
async def publish_image_post(
    self,
    commentary: str,
    image_data: bytes,
    image_title: str = None,
    visibility: str = "PUBLIC"
) -> LinkedInPost:
    # Upload image
    image_urn = await self.upload_image(image_data, "image.jpg")
    
    # Create post with image
    payload = {
        "author": self.author_urn,
        "commentary": commentary,
        "visibility": visibility,
        "distribution": {
            "feedDistribution": "MAIN_FEED"
        },
        "content": {
            "media": {
                "title": image_title or "Image",
                "id": image_urn
            }
        },
        "lifecycleState": "PUBLISHED"
    }
    
    response = await self._request('POST', '/posts', json=payload)
    return LinkedInPost.from_api_response(response)
```

---

#### **LI-2.5: Create Publication Tracking System**
- **Priority**: P0 (Critical)
- **Estimate**: 3 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 2
- **Dependencies**: LI-1.5, LI-2.2

**Description**:
Implementare tracking di tutte le pubblicazioni LinkedIn.

**Acceptance Criteria**:
- [ ] Save publication to `linkedin_publications` table
- [ ] Track status: pending → publishing → published/failed
- [ ] Store post URN, URL, content
- [ ] Track retry attempts
- [ ] Query methods per tenant/user
- [ ] Unit tests per repository

**Technical Notes**:
```python
class LinkedInPublicationRepository:
    async def create_publication(
        self,
        tenant_id: UUID,
        credential_id: UUID,
        content_id: UUID,
        post_type: str,
        commentary: str
    ) -> LinkedInPublication:
        # Insert with status='pending'
        pass
    
    async def update_status(
        self,
        publication_id: UUID,
        status: str,
        linkedin_post_urn: str = None,
        error_message: str = None
    ) -> None:
        # Update status and metadata
        pass
```

---

### MILESTONE 3: Production Ready (20 pts)

#### **LI-3.1: Implement Rate Limiting**
- **Priority**: P0 (Critical)
- **Estimate**: 5 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 3
- **Dependencies**: LI-2.1

**Description**:
Implementare rate limiting per rispettare LinkedIn API limits.

**Acceptance Criteria**:
- [ ] `LinkedInRateLimiter` class implementata
- [ ] Token bucket algorithm
- [ ] Conservative limit: 100 req/10 sec
- [ ] Per-tenant rate limiting
- [ ] Monitor `X-RateLimit-*` headers
- [ ] Adjust limits dynamically
- [ ] Unit tests

---

#### **LI-3.2: Implement Retry Logic with Exponential Backoff**
- **Priority**: P0 (Critical)
- **Estimate**: 5 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 3
- **Dependencies**: LI-2.5

**Description**:
Implementare retry logic per transient failures.

**Acceptance Criteria**:
- [ ] Exponential backoff implementato
- [ ] Max 3 retries per publication
- [ ] Retry on: 429, 500, 502, 503, 504
- [ ] NO retry on: 400, 401, 403
- [ ] Track retry_count in database
- [ ] Unit tests

---

#### **LI-3.3: Implement Error Handling & Logging**
- **Priority**: P1 (High)
- **Estimate**: 3 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 3
- **Dependencies**: LI-2.1

**Description**:
Comprehensive error handling e structured logging.

**Acceptance Criteria**:
- [ ] Custom exceptions per error types
- [ ] Structured logging (JSON format)
- [ ] Log all API requests/responses
- [ ] Sensitive data masking (tokens)
- [ ] Error messages user-friendly
- [ ] Unit tests

---

#### **LI-3.4: Create Background Job for Token Refresh**
- **Priority**: P0 (Critical)
- **Estimate**: 5 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 3
- **Dependencies**: LI-1.4

**Description**:
Background job per refresh automatico dei token.

**Acceptance Criteria**:
- [ ] Celery/Temporal task creato
- [ ] Run daily, check tokens expiring in 7 days
- [ ] Refresh tokens proattivamente
- [ ] Handle refresh failures (notify user)
- [ ] Logging per ogni refresh
- [ ] Integration tests

---

#### **LI-3.5: Setup Monitoring & Alerts**
- **Priority**: P1 (High)
- **Estimate**: 2 points
- **Assignee**: DevOps
- **Epic**: EPIC 3
- **Dependencies**: LI-3.3

**Description**:
Setup monitoring e alerting per LinkedIn integration.

**Acceptance Criteria**:
- [ ] Metrics: publish success rate, latency, errors
- [ ] Alerts: high error rate, token refresh failures
- [ ] Dashboard in Grafana/Datadog
- [ ] Log aggregation in ELK/Splunk
- [ ] On-call runbook creato

---

### MILESTONE 4: Advanced Features (15 pts)

#### **LI-4.1: Implement Scheduled Publishing**
- **Priority**: P1 (High)
- **Estimate**: 5 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 4
- **Dependencies**: LI-2.5, LI-3.4

**Description**:
Permettere scheduling di post per pubblicazione futura.

**Acceptance Criteria**:
- [ ] `scheduled_for` field utilizzato
- [ ] Background job checks pending scheduled posts
- [ ] Publish at scheduled time
- [ ] Timezone handling
- [ ] UI per selezionare data/ora
- [ ] Integration tests

---

#### **LI-4.2: Implement Video Upload & Publishing**
- **Priority**: P2 (Medium)
- **Estimate**: 5 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 4
- **Dependencies**: LI-2.3

**Description**:
Support per upload e pubblicazione video.

**Acceptance Criteria**:
- [ ] `upload_video()` method implementato
- [ ] Support MP4, MOV formats
- [ ] Validate video size (<200MB)
- [ ] `publish_video_post()` method
- [ ] Integration tests

---

#### **LI-4.3: Implement Multi-Image Posts**
- **Priority**: P2 (Medium)
- **Estimate**: 3 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 4
- **Dependencies**: LI-2.4

**Description**:
Support per post con multiple immagini (carousel).

**Acceptance Criteria**:
- [ ] Upload multiple images
- [ ] `publish_multi_image_post()` method
- [ ] Max 9 images per post
- [ ] Integration tests

---

#### **LI-4.4: Implement Article/Link Posts**
- **Priority**: P2 (Medium)
- **Estimate**: 2 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 4
- **Dependencies**: LI-2.2

**Description**:
Support per post con link esterni (article preview).

**Acceptance Criteria**:
- [ ] `publish_article_post()` method
- [ ] Include article URL, title, description
- [ ] LinkedIn generates preview automatically
- [ ] Integration tests

---

### MILESTONE 5: Organization Publishing (10 pts)

#### **LI-5.1: Implement Organization OAuth Flow**
- **Priority**: P2 (Medium)
- **Estimate**: 5 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 5
- **Dependencies**: LI-1.2

**Description**:
OAuth flow per ottenere `w_organization_social` scope.

**Acceptance Criteria**:
- [ ] Request `w_organization_social` scope
- [ ] Get organization URNs user can manage
- [ ] Store organization credentials separately
- [ ] Handle admin role requirement
- [ ] Integration tests

---

#### **LI-5.2: Implement Organization Post Publishing**
- **Priority**: P2 (Medium)
- **Estimate**: 3 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 5
- **Dependencies**: LI-5.1, LI-2.2

**Description**:
Pubblicare post su company pages.

**Acceptance Criteria**:
- [ ] Use organization URN as author
- [ ] `publish_organization_post()` method
- [ ] Support text, image, video
- [ ] Integration tests

---

#### **LI-5.3: Add Organization Selector UI**
- **Priority**: P2 (Medium)
- **Estimate**: 2 points
- **Assignee**: Frontend Developer
- **Epic**: EPIC 5
- **Dependencies**: LI-5.1

**Description**:
UI per selezionare tra profilo personale e company pages.

**Acceptance Criteria**:
- [ ] Dropdown con organizzazioni disponibili
- [ ] Default: profilo personale
- [ ] Save selection preference
- [ ] UI tests

---

### MILESTONE 6: Analytics & Optimization (5 pts)

#### **LI-6.1: Implement Publication Performance Tracking**
- **Priority**: P2 (Medium)
- **Estimate**: 3 points
- **Assignee**: Backend Developer
- **Epic**: EPIC 6
- **Dependencies**: LI-2.5

**Description**:
Track performance metrics per ogni pubblicazione.

**Acceptance Criteria**:
- [ ] Table `linkedin_publication_performance`
- [ ] Track: impressions, likes, comments, shares
- [ ] Periodic fetch from LinkedIn API (if available)
- [ ] Update Adaptive Cards performance
- [ ] Unit tests

---

#### **LI-6.2: Create Analytics Dashboard**
- **Priority**: P2 (Medium)
- **Estimate**: 2 points
- **Assignee**: Frontend Developer
- **Epic**: EPIC 6
- **Dependencies**: LI-6.1

**Description**:
Dashboard per visualizzare analytics LinkedIn.

**Acceptance Criteria**:
- [ ] Chart: publications over time
- [ ] Chart: success rate
- [ ] Table: top performing posts
- [ ] Filter by date range
- [ ] UI tests

---

## 📅 SPRINT PLANNING

### Sprint 1 (Week 1-2): Foundation
- LI-1.1, LI-1.2, LI-1.3, LI-1.4, LI-1.5
- **Goal**: OAuth funzionante, credentials stored
- **Demo**: User può connettere LinkedIn account

### Sprint 2 (Week 3-4): Core Publishing
- LI-2.1, LI-2.2, LI-2.3, LI-2.4, LI-2.5
- **Goal**: Pubblicare text e image posts
- **Demo**: User può pubblicare post su LinkedIn

### Sprint 3 (Week 5-6): Production Ready
- LI-3.1, LI-3.2, LI-3.3, LI-3.4, LI-3.5
- **Goal**: Sistema robusto e monitorato
- **Demo**: Error handling, retry, monitoring funzionanti

### Sprint 4 (Week 7): Advanced Features
- LI-4.1, LI-4.2, LI-4.3, LI-4.4
- **Goal**: Scheduling, video, multi-image
- **Demo**: User può schedulare post e pubblicare video

### Sprint 5 (Week 8): Organization & Analytics
- LI-5.1, LI-5.2, LI-5.3, LI-6.1, LI-6.2
- **Goal**: Company pages + analytics
- **Demo**: User può pubblicare su company page e vedere analytics

---

## ✅ DEFINITION OF DONE

Per ogni task:
- [ ] Code implementato e reviewed
- [ ] Unit tests scritti (coverage >80%)
- [ ] Integration tests scritti (se applicabile)
- [ ] Documentation aggiornata
- [ ] PR approved e merged
- [ ] Deployed to staging
- [ ] QA testing completato
- [ ] Deployed to production

---

**Next**: See `LINEAR_IMPORT_LINKEDIN_TASKS.csv` for importable task list.

