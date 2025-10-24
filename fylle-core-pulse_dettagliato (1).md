# 🧭 Progetto: Fylle Core Pulse

## Panoramica Generale
- **Totale issue:** 83
- **Team:** Fylle
- **Milestone principale:** M2: Core Architecture
- **Creatore principale:** fulvio@fylle.ai
- **Priorità predominante:** Urgent
- **Stato attuale:** Prevalentemente *Backlog*, in fase di pianificazione.

## 📋 Elenco completo delle Issue

### 🧩 [MIGRATE-01] Audit Funzionalità Legacy Esistenti
**ID:** FYL-43

**Status:** Backlog  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Audit completo di TUTTE le funzionalità esistenti in gloria-backend da migrare o deprecare.

## Context

Prima di migrare, serve inventario completo di cosa esiste e cosa va mantenuto.

## Tasks

- [ ] Audit completo endpoints API (tramite OpenAPI spec)
- [ ] Audit completo servizi business logic
- [ ] Audit completo modelli database
- [ ] Identificare funzionalità **CORE** (da migrare priorità alta):
  - Authentication & Authorization
  - Organizations/Tenant management
  - User management
  - Configuration management
- [ ] Identificare funzionalità **DEPRECATED** (non migrare):
  - Tutti i moduli financial-specific (già in cleanup issues)
- [ ] Identificare funzionalità **NICE-TO-HAVE** (migrare dopo MVP):
  - Admin utilities
  - Cache management
  - Monitoring endpoints esistenti
- [ ] Creare documento `LEGACY_AUDIT.md` con inventario completo
- [ ] Prioritize migration roadmap

## Acceptance Criteria

* ✅ Documento `LEGACY_AUDIT.md` completo
* ✅ Ogni funzionalità classificata (CORE/DEPRECATED/NICE-TO-HAVE)
* ✅ Migration roadmap definito
* ✅ Issue dedicato per ogni funzionalità CORE da migrare

## Estimate

4 ore

## Output

* `LEGACY_AUDIT.md` (inventario completo)
* Migration roadmap (priorità e timeline)

---

### 🧩 [ARCH-01] Implementare Tenant Context & Multi-tenancy Core
**ID:** FYL-33

**Status:** Backlog  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Implementare sistema di tenant context per isolare completamente i dati tra clienti.

## Context

Multi-tenancy è REQUISITO ARCHITETTURALE FONDAMENTALE. Ogni client deve avere dati completamente isolati.

## Tasks

- [ ] Implementare `TenantContext` (thread-safe, async-safe)
- [ ] Middleware tenant extraction da API Key
- [ ] Implementare Row-Level Security (RLS) in PostgreSQL
- [ ] Creare tabella `tenants` (id, name, settings, created_at)
- [ ] Tenant-aware queries (tutti i servizi devono filtrare per tenant_id)
- [ ] Audit logging per tenant isolation
- [ ] Test tenant isolation (unit + integration)
- [ ] Documentation tenant onboarding

## Acceptance Criteria

* ✅ Ogni API key associata a un tenant_id
* ✅ Middleware automatico estrae tenant da API key
* ✅ Tutte le query database filtrano per tenant_id
* ✅ RLS policies attive in PostgreSQL
* ✅ Test completi isolation (client A non vede dati client B)
* ✅ Zero possibilità di data leakage tra tenant

## Business Value

Security foundation, compliance (GDPR), production-ready multi-tenancy

## Estimate

5 ore

## Riferimenti

* `app/services/organizations.py` (base esistente)
* Pattern: Tenant-aware context manager

---

### 🧩 [CRITICAL] Implementare JWT Authentication per Frontend Users
**ID:** FYL-6

**Status:** Backlog  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Implementare JWT authentication per utenti frontend con supporto per refresh tokens.

## Context

Dal documento `01-authentication-security-analysis.md`: necessario JWT per autenticazione utenti frontend Fylle, separato da API Key authentication (che è per client-to-server).

## Tasks

- [ ] Creare tabella `users` (id, email, password_hash, role, created_at)
- [ ] Endpoint `/api/v1/auth/login` (email/password → JWT access + refresh token)
- [ ] Endpoint `/api/v1/auth/refresh` (refresh token → new access token)
- [ ] Endpoint `/api/v1/auth/logout` (invalidate refresh token)
- [ ] Middleware JWT validation per protected endpoints
- [ ] JWT configuration (secret, expiration, algorithm RS256)
- [ ] Password hashing con bcrypt
- [ ] Role-based access control (RBAC) base

## Acceptance Criteria

* ✅ Login returns JWT access token (15min) + refresh token (7 days)
* ✅ Protected endpoints validate JWT in Authorization header
* ✅ Refresh token rotation implementato
* ✅ Password policy enforced (min 8 chars, complexity)
* ✅ RBAC ready (admin, user roles)

## Riferimenti

* Documento: `MigrationAnalysis/01-authentication-security-analysis.md`
* Repository: `gloria-backend/`

---

### 🧩 [CRITICAL] Implementare API Key Authentication Layer
**ID:** FYL-5

**Status:** Backlog  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Implementare sistema di autenticazione basato su API Key per proteggere gli endpoint dell'Application Server.

## Context

Dal documento `01-authentication-security-analysis.md`: attualmente NON esiste nessun sistema di autenticazione, questo è un **BLOCKER CRITICO** per production.

## Tasks

- [ ] Creare tabella `api_keys` nel database (id, key, client_id, permissions, active, created_at, expires_at)
- [ ] Implementare middleware FastAPI per validazione API key
- [ ] Generare API keys sicure (hashing con bcrypt)
- [ ] Endpoint per gestione API keys (/api/v1/admin/api-keys)
- [ ] Rate limiting per API key
- [ ] Logging accessi per audit trail

## Acceptance Criteria

* ✅ Tutti gli endpoint API richiedono X-API-Key header
* ✅ API keys stored con hash sicuro (bcrypt)
* ✅ Client isolation garantito (ogni key identifica un client)
* ✅ Audit log per tutti gli accessi
* ✅ Rate limiting configurabile per key

## Riferimenti

* Documento: `MigrationAnalysis/01-authentication-security-analysis.md`
* Repository base: `gloria-backend/`

---

### 🧩 [CRITICAL] Database Migration: Supabase → Neon PostgreSQL
**ID:** FYL-7

**Status:** Backlog  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Migrare database da Supabase a Neon PostgreSQL puro per controllo completo e performance ottimali.

## Context

Dal documento `06-database-strategy-analysis.md`: PostgreSQL puro (Neon) offre controllo completo, pgvector ottimizzato (HNSW index), zero vendor lock-in, observability completa.

## Tasks

- [ ] Setup account Neon Pro ($19/month)
- [ ] Creare database branches (main, staging, dev)
- [ ] pg_dump da Supabase
- [ ] pg_restore su Neon main branch
- [ ] Verificare pgvector extension + match_documents() function
- [ ] Data integrity check (10 tabelle)
- [ ] Setup AWS S3 bucket per storage (replace Supabase Storage)
- [ ] Implementare PostgresClient wrapper (asyncpg connection pool)
- [ ] Replace Supabase Storage → AWS S3 in rag_tool.py
- [ ] Replace Supabase RPC → direct SQL queries
- [ ] Refactor 28 files (supabase client → asyncpg)
- [ ] Setup keep-alive cron (mitigate Neon cold start)

## Acceptance Criteria

* ✅ Database migrato completamente su Neon
* ✅ pgvector funzionante con HNSW index
* ✅ Storage migrato su S3
* ✅ Zero dipendenze da Supabase client library
* ✅ Performance query <= 5ms (match_documents)
* ✅ Cold start < 500ms (keep-alive attivo)

## Effort Estimate

1-2 giorni developer time

## Riferimenti

* Documento: `MigrationAnalysis/06-database-strategy-analysis.md`
* Migration cost: $2,000 one-time

---

### 🧩 [FYL-35.5] Documentare Error Codes e Best Practices
**ID:** FYL-78

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Creare documentazione completa per error codes e best practices per error handling.

## Tasks

- [ ] Creare docs/error-codes.md con tutti i codici
- [ ] Documentare ogni error code con:
  - Codice e categoria
  - HTTP status code
  - Descrizione
  - Quando usarlo
  - Esempio di utilizzo
- [ ] Creare docs/patterns/error-handling-guide.md
- [ ] Documentare best practices:
  - Quando usare retry vs circuit breaker
  - Come scegliere error code appropriato
  - Come loggare errori correttamente
  - Esempi pratici per ogni tipo di errore
- [ ] Aggiungere esempi di response JSON
- [ ] Aggiornare README con link a documentazione

## Struttura Documentazione

### docs/error-codes.md

```markdown
# Error Codes Reference

## Authentication Errors (401)

| Code | Description | When to Use |
|------|-------------|-------------|
| AUTH_001 | Invalid token | JWT token invalid or malformed |
| AUTH_002 | Expired token | JWT token expired |
| AUTH_003 | Missing credentials | No auth header provided |

...
```

### docs/patterns/error-handling-guide.md

```markdown
# Error Handling Best Practices

## 1. Choosing the Right Exception

## 2. Using Retry Logic

## 3. Circuit Breaker Pattern

## 4. Logging Errors

## 5. Client-Friendly Error Messages
```

## Acceptance Criteria

* ✅ docs/error-codes.md completo con tutti i codici
* ✅ Ogni error code documentato con esempio
* ✅ docs/patterns/error-handling-guide.md creato
* ✅ Best practices documentate
* ✅ Esempi di utilizzo per retry e circuit breaker
* ✅ README aggiornato con link

## Estimate

1.5 ore

## Dipendenze

Dipende da: FYL-74, FYL-75, FYL-76, FYL-77 (tutte le implementazioni)

---

### 🧩 [API-03] Implementare RFC 7807 Problem Details per Error Response
**ID:** FYL-56

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Standardizzare error responses secondo RFC 7807 Problem Details.

## Context

Dal documento `02-api-architecture-analysis.md`: Error responses attuali sono basic HTTPException, serve standardizzazione.

## Tasks

- [ ] Creare model `ProblemDetail`:

  ```python
  class ProblemDetail(BaseModel):
      type: str          # URI reference (es. "/errors/validation")
      title: str         # Short human-readable
      status: int        # HTTP status code
      detail: str        # Detailed explanation
      instance: str      # Request URI
      request_id: str    # Trace ID
      timestamp: str     # ISO timestamp
      errors: Optional[List[Dict]]  # Validation errors
  ```
- [ ] Custom exception classes:
  - `ValidationException` → 422
  - `AuthenticationException` → 401
  - `AuthorizationException` → 403
  - `NotFoundException` → 404
  - `RateLimitException` → 429
  - `ProviderException` → 502/503
- [ ] Exception handler middleware
- [ ] Error response examples in OpenAPI
- [ ] Client SDK compatibility test
- [ ] Documentation error codes

## Acceptance Criteria

* ✅ Tutte le exceptions usano ProblemDetail
* ✅ Error responses RFC 7807 compliant
* ✅ Request ID tracing in errors
* ✅ Validation errors structured
* ✅ OpenAPI schema aggiornato

## Estimate

2 giorni

## Riferimenti

* Documento: `MigrationAnalysis/02-api-architecture-analysis.md` (sezione 13.3)
* Standard: RFC 7807 Problem Details for HTTP APIs

---

### 🧩 [ARCH-08] Implementare Health Check System
**ID:** FYL-40

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Sistema di health checks completo per monitoring e readiness probes.

## Context

Health checks sono necessari per:

* Kubernetes readiness/liveness probes
* Load balancer health checks
* Monitoring alerts
* Dependency status

## Tasks

- [ ] Implementare `/health` endpoint (basic health)
- [ ] Implementare `/health/ready` (readiness probe)
- [ ] Implementare `/health/live` (liveness probe)
- [ ] Health checks dependencies:
  - PostgreSQL connection
  - Redis connection (se usato)
  - S3 connectivity (se usato)
  - Provider APIs reachability (optional)
- [ ] Response format:

  ```json
  {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 3600,
    "dependencies": {
      "database": "healthy",
      "redis": "healthy",
      "s3": "healthy"
    }
  }
  ```
- [ ] Caching health check results (5s TTL)
- [ ] Timeout per health check dependencies (2s max)

## Acceptance Criteria

* ✅ `/health` endpoint funzionante
* ✅ Readiness/liveness probes separati
* ✅ Dependency checks implementati
* ✅ Response format standard
* ✅ Timeout configurabile
* ✅ Caching per performance

## Business Value

Production-ready, Kubernetes compatibility, monitoring

## Estimate

2 ore

---

### 🧩 [ARCH-07] Implementare Request ID Tracing
**ID:** FYL-39

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Sistema di request ID tracing per tracciare richieste end-to-end.

## Context

Request tracing è essenziale per debugging distributed systems e workflow complessi.

## Tasks

- [ ] Middleware injection `X-Request-ID` header
- [ ] Generare UUID per ogni request (se non presente)
- [ ] Propagare request_id in tutti i log
- [ ] Propagare request_id in chiamate LLM (metadata)
- [ ] Propagare request_id in database queries (commento SQL)
- [ ] Propagare request_id in background jobs
- [ ] Response header `X-Request-ID` (echo back)
- [ ] Documentation request tracing

## Acceptance Criteria

* ✅ Ogni request ha UUID univoco
* ✅ Request ID in tutti i log
* ✅ Request ID in LLM calls metadata
* ✅ Request ID in response headers
* ✅ Request ID in background jobs
* ✅ Facile tracciare request end-to-end

## Business Value

Debugging power, observability, troubleshooting facile

## Estimate

2 ore

---

### 🧩 [ARCH-05] Implementare Background Job System
**ID:** FYL-37

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Sistema di background jobs per task asincroni (long-running workflows, batch processing).

## Context

Workflow complessi possono richiedere minuti. Necessario sistema async job processing.

## Tasks

- [ ] Scegliere job queue (Celery + Redis, oppure ARQ, oppure RQ)
- [ ] Setup Redis come broker
- [ ] Implementare job worker
- [ ] Creare tabella `jobs`:
  - id
  - tenant_id
  - job_type
  - status (pending, running, completed, failed)
  - input_data (JSON)
  - result_data (JSON)
  - error_message
  - created_at, started_at, completed_at
- [ ] API endpoints:
  - `POST /api/v1/jobs` (submit job)
  - `GET /api/v1/jobs/{id}` (status)
  - `GET /api/v1/jobs/{id}/result` (result)
  - `DELETE /api/v1/jobs/{id}` (cancel)
- [ ] Job retry logic (max 3 attempts)
- [ ] Job timeout configuration
- [ ] Job priority queue
- [ ] Monitoring job queue size

## Acceptance Criteria

* ✅ Job submission API funzionante
* ✅ Job status tracking real-time
* ✅ Worker processing jobs correttamente
* ✅ Retry logic su failures
* ✅ Timeout handling
* ✅ Metrics job queue (Prometheus)

## Business Value

Scalability, async workflows, better UX (no timeout 30s)

## Estimate

6 ore

## Riferimenti

* Celery best practices
* Documento: `MigrationAnalysis/09-gloria-backend-integration-plan.md`

---

### 🧩 [ARCH-04] Implementare Audit Logging System
**ID:** FYL-36

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Sistema di audit logging completo per compliance e troubleshooting.

## Context

Audit logging è necessario per:

* Compliance (GDPR, SOC2)
* Troubleshooting (chi ha fatto cosa quando)
* Security (detect anomalie)
* Cost attribution (chi ha consumato cosa)

## Tasks

- [ ] Creare tabella `audit_logs`:
  - org_id ? (slug) ? 
  - user_id
  - action (enum: CREATE, UPDATE, DELETE, EXECUTE, etc.)
  - resource_type (workflow, document, config, etc.)
  - resource_id
  - metadata (JSON)
  - ip_address
  - user_agent
  - timestamp
- [ ] Implementare `AuditLogger` service
- [ ] Decorator `@audit_log` per automatic logging
- [ ] Middleware audit logging HTTP requests
- [ ] Async logging (non-blocking)
- [ ] Retention policy (30 giorni hot, 1 anno archive)
- [ ] API endpoints audit query:
  - `GET /api/v1/audit/logs` (query logs)
  - `GET /api/v1/audit/export` (export CSV)
- [ ] Index database per query performance

## Acceptance Criteria

* ✅ Ogni azione API loggata automaticamente
* ✅ Decorator `@audit_log` funzionante
* ✅ Async logging (non-blocking)
* ✅ Query performance <100ms
* ✅ Retention policy configurabile
* ✅ Export CSV funzionante

## Business Value

Compliance-ready, security, troubleshooting power

## Estimate

5 ore

---

### 🧩 [ARCH-02] Implementare Configuration Management per Tenant
**ID:** FYL-34

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Sistema di configuration management per tenant-specific e global settings.

## Context

Ogni tenant deve poter configurare:

* Provider LLM preferito
* API keys proprie (OpenAI, Anthropic, etc.)
* Workflow customization
* Cost limits
* Rate limits custom

## Tasks

- [ ] Creare tabella `tenant_configs` (tenant_id, config_key, config_value, encrypted)
- [ ] Implementare `ConfigurationService`
- [ ] Encryption per secrets (API keys tenant)
- [ ] Hierarchical config (global defaults → tenant overrides)
- [ ] Config caching (Redis)
- [ ] API endpoints config management:
  - `GET /api/v1/config` (tenant config)
  - `PUT /api/v1/config/{key}` (update config)
- [ ] Config validation (schema validation)
- [ ] Audit log config changes

## Acceptance Criteria

* ✅ Tenant può configurare provider LLM preferito
* ✅ Tenant può usare proprie API keys (encrypted storage)
* ✅ Config hierarchical (defaults + overrides)
* ✅ Config caching funzionante
* ✅ Secrets encrypted at rest
* ✅ Audit log completo

## Business Value

Customization per client, flessibilità, bring-your-own-key model

## Estimate

4 ore

## Riferimenti

* `app/services/types.py` (configuration types esistenti)

---

### 🧩 [API-KEY] Implementare API Key Authentication per Client Esterni
**ID:** FYL-82

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Implementare sistema di autenticazione tramite API Key per permettere a client esterni (machine-to-machine) di utilizzare l'Application Server.

## Context

Dal documento `01-authentication-security-analysis.md`: necessario sistema API Key per client esterni (separato da JWT [Clerk.com](http://Clerk.com) per frontend users).

## Sub-Tasks

### 1\. Database Schema ✅

- [X] File SQL migration creato: `database/migrations/001_api_keys_schema.sql`
- [X] Tabelle: `api_keys`, `api_key_usage`, `api_key_events`, `api_key_rate_limits`
- [X] Helper functions e triggers implementati

### 2\. API Key Generator Service

- [ ] Implementare `APIKeyService` usando DatabaseManager pattern
- [ ] Generazione key format: `fylle_{env}_sk_{random}` (256-bit entropy)
- [ ] SHA256 hashing per storage sicuro
- [ ] Key rotation mechanism
- [ ] Key revocation logic

### 3\. Middleware Validazione

- [ ] Implementare `APIKeyMiddleware`
- [ ] Integrazione con `AuthMiddleware` esistente (JWT + API Key detection)
- [ ] Validazione key hash da database
- [ ] Tenant extraction da API key
- [ ] Permission checking per API key

### 4\. Admin Endpoints

- [ ] `POST /api/v1/admin/api-keys` - Generate new key
- [ ] `GET /api/v1/admin/api-keys` - List keys
- [ ] `POST /api/v1/admin/api-keys/{key_id}/revoke` - Revoke key
- [ ] `POST /api/v1/admin/api-keys/{key_id}/rotate` - Rotate key
- [ ] `GET /api/v1/admin/api-keys/{key_id}/usage` - Usage stats

### 5\. Rate Limiting

- [ ] Redis-based rate limiter per API key
- [ ] Configurabile per key (requests/day, requests/hour)
- [ ] Cost-based rate limiting (optional)
- [ ] Rate limit exceeded response (429)

### 6\. Usage Tracking & Analytics

- [ ] Log ogni request con API key in `api_key_usage`
- [ ] Track cost per request (LLM + tools)
- [ ] Aggregate usage stats per key
- [ ] Cost analytics dashboard endpoint

## Acceptance Criteria

* ✅ Database schema deployed
* ✅ API key generation returns key SOLO una volta (security)
* ✅ API key validation middleware integrato con JWT middleware
* ✅ Admin può creare/list/revoke keys via API
* ✅ Rate limiting funzionante (per-key)
* ✅ Usage tracking granulare in database
* ✅ Multi-tenant isolation enforced (key → tenant_id)
* ✅ Permissions per key configurabili

## Technical Notes

**Database Access Pattern** (IMPORTANTE):

* Usare `DatabaseManager` da `app/core/database.py`
* Usare `get_database_manager()` per singleton
* Usare `get_connection_context(schema_name)` per operations
* Helper methods: `fetch_one()`, `fetch_all()`, `execute_command()`

**Security Requirements**:

* NEVER store plaintext keys (SHA256 hash only)
* Key prefix per identificazione (primi 30 char)
* Audit logging per tutte le operazioni (create/revoke/rotate)
* Invalid key attempts logged

## Riferimenti

* Documento: `MigrationAnalysis/01-authentication-security-analysis.md`
* SQL Migration: `database/migrations/001_api_keys_schema.sql`
* Pattern: `app/core/database.py` (asyncpg con connection pooling)
* Repository: `fylle-core-pulse/`

---

### 🧩 [FYL-35.4] Implementare Circuit Breaker Pattern
**ID:** FYL-77

**Status:** Done  |  **Priorità:** High  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Implementare circuit breaker per proteggere il sistema da servizi esterni down.

## Tasks

- [ ] Installare pybreaker (pip install pybreaker)
- [ ] Creare CircuitBreakerManager in app/utils/circuit_breaker.py
- [ ] Configurare circuit breakers per servizi esterni
- [ ] Implementare @circuit decorator
- [ ] Aggiungere monitoring/metrics per circuit breaker states
- [ ] Configurare failure_threshold e recovery_timeout
- [ ] Gestire CircuitBreakerOpen exception
- [ ] Documentare utilizzo

## Circuit Breaker States

```
CLOSED (normale)
  ↓ Troppi errori (failure_threshold raggiunto)
OPEN (blocca tutte le chiamate - fail-fast)
  ↓ Attendi recovery_timeout
HALF-OPEN (test se servizio è tornato online)
  ↓ Se chiamata succede
CLOSED (torna normale)
```

## Configurazione

```python
# app/utils/circuit_breaker.py
from pybreaker import CircuitBreaker

openai_circuit = CircuitBreaker(
    failure_threshold=5,      # apri dopo 5 errori
    recovery_timeout=60,      # aspetta 60s prima di riprovare
    expected_exception=ProviderError
)
```

## Utilizzo

```python
@openai_circuit
@retry(max_attempts=3, delay=1.0)
async def call_openai(prompt: str):
    response = await openai_client.create(...)
    return response
```

## Servizi da Proteggere

* OpenAI API (LLM calls)
* Database connections
* Altri servizi esterni (future)

## Acceptance Criteria

* ✅ pybreaker installato e configurato
* ✅ Circuit breaker per OpenAI
* ✅ Circuit breaker per database
* ✅ @circuit decorator funzionante
* ✅ Gestione CircuitBreakerOpen con fallback
* ✅ Logging per cambio stato (CLOSED → OPEN → HALF-OPEN)
* ✅ Documentazione utilizzo

## Estimate

2 ore

## Dipendenze

Dipende da: FYL-76 (retry logic)

---

### 🧩 [FYL-35.3] Implementare Retry Logic con Exponential Backoff
**ID:** FYL-76

**Status:** Done  |  **Priorità:** High  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Creare decorator @retry per gestire errori transienti con exponential backoff.

## Tasks

- [ ] Creare @retry decorator in app/utils/retry.py
- [ ] Implementare exponential backoff strategy
- [ ] Supportare max_attempts, delay, backoff factor
- [ ] Filtrare eccezioni ritentabili (solo ServerError)
- [ ] Logging per ogni tentativo
- [ ] Aggiungere jitter per evitare thundering herd
- [ ] Unit tests per retry logic

## Decorator Signature

```python
@retry(
    max_attempts=3,           # massimo 3 tentativi
    delay=1.0,                # attesa iniziale 1 secondo
    backoff=2.0,              # raddoppia delay ogni volta
    exceptions=(ProviderError, DatabaseError, TimeoutError),
    jitter=True               # aggiungi randomness
)
async def call_external_service():
    ...
```

## Sequenza di Retry

```
Tentativo 1: Fallisce
  ↓ Attendi 1.0s (+ jitter 0-0.1s)
Tentativo 2: Fallisce
  ↓ Attendi 2.0s (1.0 × 2 + jitter)
Tentativo 3: Successo ✓
```

## Regole di Retry

**✅ RETRY (errori transienti):**

* DatabaseError (connection pool exhausted)
* ProviderError (503 Service Unavailable)
* TimeoutError
* NetworkError

**❌ NO RETRY (errori permanenti):**

* ValidationError (422)
* AuthenticationError (401)
* NotFoundError (404)
* InternalError (bug nel codice)

## Acceptance Criteria

* ✅ @retry decorator funzionante
* ✅ Exponential backoff implementato
* ✅ Jitter per evitare thundering herd
* ✅ Logging per ogni tentativo
* ✅ Solo ServerError sono ritentabili
* ✅ Unit tests con almeno 5 casi

## Estimate

2.5 ore

## Dipendenze

Dipende da: FYL-74 (error hierarchy)

---

### 🧩 [FYL-35.2] Aggiungere Request ID e Logging Automatico
**ID:** FYL-75

**Status:** Done  |  **Priorità:** High  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Implementare request_id tracking e logging automatico con stack trace per tutte le eccezioni.

## Tasks

- [ ] Creare middleware per generare request_id unico (UUID)
- [ ] Aggiungere request_id a request.state
- [ ] Aggiornare exception handlers per includere request_id nel response
- [ ] Implementare auto-logging con stack trace per errori 5xx
- [ ] Aggiungere request_id ai log entries
- [ ] Aggiornare create_error_response per includere request_id

## Request ID Format

`req_{uuid}` - es. req_7f8a9b2c-1234-5678-9abc-def012345678

## Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "AUTH_001",
    "message": "Authentication failed",
    "details": {...}
  },
  "request_id": "req_7f8a9b2c",
  "timestamp": "2025-10-17T12:30:45Z"
}
```

## Logging Format

```
[2025-10-17 12:30:45] ERROR [req_7f8a9b2c] DB_001: Database connection failed
Traceback:
  File "app/services/database.py", line 45, in connect
    ...
```

## Acceptance Criteria

* ✅ Middleware genera request_id per ogni richiesta
* ✅ request_id incluso in tutti gli error response
* ✅ Logging automatico con stack trace per errori 5xx
* ✅ request_id incluso nei log
* ✅ Formato timestamp ISO 8601

## Estimate

1.5 ore

## Dipendenze

Dipende da: FYL-74 (error codes)

---

### 🧩 [FYL-35.1] Implementare Exception Hierarchy con Error Codes
**ID:** FYL-74

**Status:** Done  |  **Priorità:** High  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Creare hierarchy di eccezioni con ClientError/ServerError e error codes standardizzati.

## Tasks

- [ ] Creare ClientError base class (4xx errors)
- [ ] Creare ServerError base class (5xx errors)
- [ ] Aggiungere InternalError per errori interni (500)
- [ ] Definire ErrorCode class con tutti i codici standardizzati
- [ ] Aggiornare tutte le exception esistenti con error_code parameter
- [ ] Aggiungere request_id support a tutte le eccezioni

## Error Code Format

{CATEGORY}\_{NUMBER} - es. AUTH_001, VAL_002, DB_005

## Categorie:

**Client Errors (4xx):**

* AUTH_xxx - Authentication (401)
* AUTHZ_xxx - Authorization (403)
* VAL_xxx - Validation (422)
* NOT_FOUND_xxx - Not Found (404)
* CONFLICT_xxx - Duplicate/Conflict (409)
* RATE_xxx - Rate Limiting (429)

**Server Errors (5xx):**

* INTERNAL_xxx - Internal errors (500)
* DB_xxx - Database errors (500)
* PROV_xxx - Provider/External (502/503)
* CONFIG_xxx - Configuration (500)

## Acceptance Criteria

* ✅ Exception hierarchy: BaseApplicationError → ClientError/ServerError
* ✅ ErrorCode class con \~20 codici definiti
* ✅ Tutte le exception supportano error_code parameter
* ✅ request_id supportato in tutte le exception

## Estimate

2 ore

## Dipendenze

Parent: FYL-35

---

### 🧩 [ARCH-03] Implementare Error Handling & Exception Framework
**ID:** FYL-35

**Status:** Done  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Framework unificato per error handling con exception hierarchy e error codes.

## Context

Error handling consistente è essenziale per debugging, client experience, monitoring.

Utilizza l'envelope standard del server.

## Tasks Completati

- [X] **Creare exception hierarchy** ✅ **Completato in FYL-74**
  * `BaseApplicationError` (base)
  * `ClientError` (4xx) / `ServerError` (5xx)
  * `AuthenticationError` (401)
  * `AuthorizationError` (403)
  * `ValidationError` (422)
  * `ResourceNotFoundError` (404)
  * `DuplicateResourceError` (409)
  * `RateLimitError` (429)
  * `BusinessLogicError` (400)
  * `DatabaseError` (500)
  * `ExternalServiceError` (503)
  * `InternalError` (500)
  * `ConfigurationError` (500)
- [X] **Error codes standardizzati** ✅ **Completato in FYL-74**
  * AUTH_xxx, AUTHZ_xxx, VAL_xxx, NOT_FOUND_xxx, CONFLICT_xxx
  * RATE_xxx, DB_xxx, PROV_xxx, INTERNAL_xxx, BUSINESS_xxx, CONFIG_xxx
- [X] **Error Response Format con Envelope** ✅ **Completato in FYL-80**
  * ErrorDetail e ErrorResponseData schemas
  * Structured error format: error_code, message, details, request_id, timestamp
  * Integration con envelope system
- [X] **Exception Handler Middleware** ✅ **Completato in FYL-79**
  * ExceptionHandlerMiddleware per FastAPI
  * Automatic exception → HTTP response conversion
  * Logging automatico (ClientError=WARNING, ServerError=ERROR con stack trace)
  * Request ID tracking
  * Integrated in main application
- [X] **Logging automatico errori** ✅ **Implementato in exception base class + middleware**
  * Stack trace capture in BaseApplicationError
  * Automatic logging via ExceptionHandlerMiddleware
- [X] **Retry logic per errori transienti** ✅ **Completato in FYL-76**
  * @retry_async decorator
  * Exponential backoff
  * ServerError-only retries
- [X] **Circuit breaker per provider failures** ✅ **Completato in FYL-77**
  * @circuit_breaker decorator
  * Failure threshold tracking
  * Half-open state recovery
- [X] **Documentation Error Codes e Exception Handling** ✅ **Completato in FYL-81**
  * ERROR_CODES.md - Complete catalog with 40+ error codes
  * EXCEPTION_HANDLING.md - Developer guide with examples
  * API_ERROR_RESPONSES.md - Client integration guide

## Risultati

**182 tests passing** ✅

### Created Files:

* `app/exceptions.py` - Complete exception hierarchy
* `app/middleware/exception_handler.py` - Exception handler middleware
* `app/schemas/error_response.py` - Error response schemas
* `docs/ERROR_CODES.md` - Error codes reference
* `docs/EXCEPTION_HANDLING.md` - Developer guide
* `docs/API_ERROR_RESPONSES.md` - Client guide

### Test Coverage:

* 18 unit tests for exception handler middleware
* 15 unit tests for error response format
* 30+ integration tests for error handling flow
* All exception hierarchy tests passing

## Acceptance Criteria

* ✅ Exception hierarchy completa con ClientError/ServerError
* ✅ 40+ error codes standardizzati e documentati
* ✅ JSON error responses consistenti con envelope format
* ✅ Logging automatico con stack trace per ServerError
* ✅ Retry logic implementato (max 3 tentativi con exponential backoff)
* ✅ Circuit breaker per provider failures
* ✅ Exception handler middleware integrated
* ✅ Error response format standardization
* ✅ Documentation completa (3 comprehensive guides)
* ✅ Request ID tracking in all error responses

## Business Value

* **Developer Experience**: Clear exception hierarchy, comprehensive documentation
* **Debugging**: Request ID tracking, automatic logging, stack traces
* **Client Experience**: Consistent error format, machine-readable codes
* **Monitoring**: Structured logging, error categorization
* **Reliability**: Retry logic, circuit breaker for resilience

## Estimate

4 ore (100% completato)

---

### 🧩 [API-KEY] Implement api_keys_analytics_recent PostgreSQL function
**ID:** FYL-97

**Status:** Done  |  **Priorità:** No priority  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Creare PostgreSQL function `settings.api_keys_analytics_recent` per log attività recente seguendo il pattern ISTRE.

## Tasks

- [ ] Creare function `settings.api_keys_analytics_recent(p_tenant_id UUID, p_limit INT, p_key_id TEXT)`
- [ ] Function deve ordinare per timestamp DESC
- [ ] Function deve validare tenant_id per security
- [ ] Function supporta filtro opzionale per key_id
- [ ] Return JSONB con array di recent requests
- [ ] Aggiornare endpoint `GET /analytics/recent-activity` per usare TenantContext e function
- [ ] Rimuovere tutte le query SQL dirette dall'endpoint
- [ ] Testing

## Recent Activity Include

* usage_id, key_id, key_name
* timestamp, endpoint, method
* status_code, response_time_ms
* ip_address, request_id
* Limit default: 100, max: 500
* Optional filter by specific key_id

---

### 🧩 [API-KEY] Implement api_keys_analytics_by_endpoint PostgreSQL function
**ID:** FYL-96

**Status:** Done  |  **Priorità:** No priority  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Creare PostgreSQL function `settings.api_keys_analytics_by_endpoint` per analytics breakdown per endpoint seguendo il pattern ISTRE.

## Tasks

- [ ] Creare function `settings.api_keys_analytics_by_endpoint(p_tenant_id UUID, p_start_date TIMESTAMP, p_end_date TIMESTAMP, p_limit INT)`
- [ ] Function deve raggruppare per (endpoint, method)
- [ ] Function deve validare tenant_id per security
- [ ] Return JSONB con array di endpoint stats
- [ ] Aggiornare endpoint `GET /analytics/by-endpoint` per usare TenantContext e function
- [ ] Rimuovere tutte le query SQL dirette dall'endpoint
- [ ] Testing

## Endpoint Stats Include

* Endpoint path + HTTP method
* Request count
* Success/failure counts and rates
* Avg/min/max response times
* Total costs
* Sorted by request count DESC
* Limited to top N endpoints (default 20, max 100)

---

### 🧩 [API-KEY] Implement api_keys_analytics_overview PostgreSQL function
**ID:** FYL-95

**Status:** Done  |  **Priorità:** No priority  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Creare PostgreSQL function `settings.api_keys_analytics_overview` per analytics aggregate organization-wide seguendo il pattern ISTRE.

## Tasks

- [ ] Creare function `settings.api_keys_analytics_overview(p_tenant_id UUID, p_start_date TIMESTAMP, p_end_date TIMESTAMP)`
- [ ] Function deve aggregare tutte le keys dell'organization
- [ ] Function deve validare tenant_id per security
- [ ] Return JSONB con: aggregate stats, top keys, daily trends
- [ ] Aggiornare endpoint `GET /analytics/overview` per usare TenantContext e function
- [ ] Rimuovere tutte le query SQL dirette dall'endpoint
- [ ] Testing

## Analytics Include

* Total requests (all keys)
* Success/failure rates
* Total costs and LLM costs
* Avg response times
* Active keys count
* Top 10 keys by usage
* Daily trends (requests, success rate, performance)

---

### 🧩 [API-KEY] Implement api_keys_usage_stats PostgreSQL function
**ID:** FYL-94

**Status:** Done  |  **Priorità:** No priority  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Creare PostgreSQL function `settings.api_keys_usage_stats` per statistiche di utilizzo singola key seguendo il pattern ISTRE.

## Tasks

- [ ] Creare function `settings.api_keys_usage_stats(p_key_id TEXT, p_tenant_id UUID, p_start_date TIMESTAMP, p_end_date TIMESTAMP)`
- [ ] Function deve aggregare da `settings.api_key_usage`
- [ ] Function deve validare tenant_id per security
- [ ] Return JSONB con: total_requests, successful/failed, costs, tokens, response times, breakdown per endpoint/status
- [ ] Aggiornare `APIKeyService.get_usage_stats()` per usare la function
- [ ] Aggiornare endpoint `GET /admin/api-keys/{key_id}/usage` per usare TenantContext
- [ ] Rimuovere query SQL dirette dal endpoint
- [ ] Testing

## Metrics

* Total requests, success/failure counts
* Total cost, LLM cost
* Token usage (input/output)
* Avg/min/max response time
* Breakdown by endpoint, status code

---

### 🧩 [API-KEY] Implement api_keys_delete PostgreSQL function
**ID:** FYL-93

**Status:** Done  |  **Priorità:** No priority  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Creare PostgreSQL function `settings.api_keys_delete` per eliminazione permanente (hard delete) seguendo il pattern ISTRE.

## Tasks

- [ ] Creare function `settings.api_keys_delete(p_context JSONB, p_key_id TEXT)`
- [ ] Function deve loggare evento BEFORE delete in `settings.api_key_events`
- [ ] Function deve eseguire DELETE fisico (NOT soft delete)
- [ ] Function deve validare tenant_id per security
- [ ] Function deve CASCADE delete usage/events/rate_limits (verificare FK constraints)
- [ ] Aggiornare `APIKeyService.delete_api_key()` per usare la function
- [ ] Aggiornare endpoint `DELETE /admin/api-keys/{key_id}` per usare TenantContext
- [ ] Rimuovere SQL diretto dal service
- [ ] Testing

## Pattern

⚠️ WARNING: Irreversible operation!

* Log audit event BEFORE deletion
* Return status code (1 = deleted, 0 = not found)
* Recommend using revoke instead for audit trail

---

### 🧩 [API-KEY] Implement api_keys_rotate PostgreSQL function
**ID:** FYL-92

**Status:** Done  |  **Priorità:** No priority  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Creare PostgreSQL function `settings.api_keys_rotate` per ruotare API keys con grace period seguendo il pattern ISTRE.

## Tasks

- [ ] Creare function `settings.api_keys_rotate(p_context JSONB, p_old_key_id TEXT, p_grace_period_days INT)`
- [ ] Function deve generare nuova key con stessa configurazione
- [ ] Function deve schedulare revoke della vecchia key (expires_at = NOW() + grace_period)
- [ ] Function deve loggare entrambi gli eventi (rotate old, create new)
- [ ] Function deve validare tenant_id per security
- [ ] Aggiornare `APIKeyService.rotate_api_key()` per usare la function
- [ ] Aggiornare endpoint `POST /admin/api-keys/{key_id}/rotate` per usare TenantContext
- [ ] Rimuovere SQL diretto dal service
- [ ] Testing

## Pattern

* Return JSONB con old_key_id, new_key (plaintext), new_key_id
* Grace period default: 7 days
* Audit logging completo

---

### 🧩 [API-KEY] Implement api_keys_revoke PostgreSQL function
**ID:** FYL-91

**Status:** Done  |  **Priorità:** No priority  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Creare PostgreSQL function `settings.api_keys_revoke` per revocare API keys (soft delete) seguendo il pattern ISTRE.

## Tasks

- [ ] Creare function `settings.api_keys_revoke(p_context JSONB, p_key_id TEXT, p_reason TEXT)`
- [ ] Function deve impostare `is_revoked = TRUE, revoked_at = NOW()`
- [ ] Function deve loggare evento in `settings.api_key_events`
- [ ] Function deve validare tenant_id per security
- [ ] Aggiornare `APIKeyService.revoke_api_key()` per usare la function
- [ ] Aggiornare endpoint `POST /admin/api-keys/{key_id}/revoke` per usare TenantContext
- [ ] Rimuovere SQL diretto dal service
- [ ] Testing

## Pattern

Seguire `settings.organizations_del` pattern:

* Context JSONB per audit trail
* Soft delete (NOT physical delete)
* Return status code (1 = success, 0 = not found)

---

### 🧩 [API-KEY] Implement api_keys_get PostgreSQL function
**ID:** FYL-90

**Status:** Done  |  **Priorità:** No priority  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Creare PostgreSQL function `settings.api_keys_get` per recuperare singola API key seguendo il pattern ISTRE.

## Tasks

- [ ] Creare function `settings.api_keys_get(p_key_id TEXT, p_tenant_id UUID)`
- [ ] Function deve filtrare per tenant_id (multi-tenant isolation)
- [ ] Return JSONB con tutti i campi (NO plaintext key)
- [ ] Aggiornare `APIKeyService.get_api_key()` per usare la function
- [ ] Aggiornare endpoint `GET /admin/api-keys/{key_id}` per usare TenantContext
- [ ] Rimuovere SQL diretto dal service
- [ ] Testing

## Pattern

Seguire pattern read operations con:

* Tenant isolation enforcement
* JSONB return format
* Connection pooling via context manager

---

### 🧩 [API-KEY] Implement api_keys_create PostgreSQL function
**ID:** FYL-89

**Status:** Done  |  **Priorità:** No priority  |  **Assegnato a:** nan

**Milestone:** M2: Core Architecture

**Descrizione:**

# Obiettivo

Creare PostgreSQL function `settings.api_keys_create` per generare nuove API keys seguendo il pattern ISTRE.

## Tasks

- [ ] Creare migration con function `settings.api_keys_create`
- [ ] Function deve generare key con formato `fylle_{env}_sk_{random}` (256-bit entropy)
- [ ] Function deve hashare con SHA256 prima dello storage
- [ ] Function deve loggare evento in `settings.api_key_events`
- [ ] Aggiornare `APIKeyService.generate_api_key()` per usare la function
- [ ] Aggiornare endpoint `POST /admin/api-keys` per usare TenantContext
- [ ] Rimuovere SQL diretto dal service
- [ ] Testing

## Pattern

Seguire `settings.organizations_upd` pattern:

* Parametri individuali (non JSONB)
* Context JSONB per audit
* Return JSONB con dati completi

## Security

* NEVER store plaintext keys
* SHA256 hash only
* Return plaintext key ONLY once

---

### 🧩 [MIGRATE-03] Migrare User Management (Auth Framework)
**ID:** FYL-45

**Status:** Backlog  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M3: Migration & Integration

**Descrizione:**

# Obiettivo

Migrare framework di autenticazione utenti da gloria-backend (sostituendo Clerk).

## Context

gloria-backend usa [Clerk.com](http://Clerk.com) per auth. Dobbiamo sostituire con JWT auth interno.

## Tasks

- [ ] Analizzare `app/services/clerk_service.py` (da ELIMINARE)
- [ ] Analizzare `app/services/auth_service.py` (framework base OK)
- [ ] Implementare JWT authentication (sostituzione Clerk):
  - User registration (email + password)
  - Login (email + password → JWT)
  - Refresh token
  - Password reset flow
- [ ] User profile management:
  - `GET /api/v1/users/me` (current user)
  - `PUT /api/v1/users/me` (update profile)
  - `PUT /api/v1/users/me/password` (change password)
- [ ] Admin user management:
  - `GET /api/v1/users` (admin - list all)
  - `POST /api/v1/users` (admin - create user)
  - `PUT /api/v1/users/{id}` (admin - update)
  - `DELETE /api/v1/users/{id}` (admin - delete)
- [ ] Role-based access control (RBAC)
- [ ] Email verification flow (optional MVP+1)
- [ ] Test suite completo

## Acceptance Criteria

* ✅ [Clerk.com](http://Clerk.com) completamente rimosso
* ✅ JWT authentication funzionante
* ✅ User CRUD completo
* ✅ RBAC implementato
* ✅ Test suite passed

## Estimate

6 ore

## Dipendenze

* FYL-6 (JWT Authentication issue già creato)

## Riferimenti

* `gloria-backend/app/services/auth_service.py`
* `gloria-backend/app/services/clerk_service.py` (eliminare)

---

### 🧩 [MIGRATE-02] Migrare Organizations Service (Multi-tenancy Base)
**ID:** FYL-44

**Status:** Backlog  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M3: Migration & Integration

**Descrizione:**

# Obiettivo

Migrare e migliorare il servizio Organizations da gloria-backend.

## Context

Organizations è il cuore del multi-tenancy. Esiste già in gloria-backend, ma serve refactoring per nuovo backend.

## Tasks

- [ ] Analizzare `app/services/organizations.py` esistente
- [ ] Analizzare `app/models/organizations.py` esistente
- [ ] Refactoring per nuovo schema (tenant_id standard)
- [ ] Aggiungere tenant settings (JSON config)
- [ ] Aggiungere tenant status (active/suspended/trial)
- [ ] Aggiungere tenant limits (API calls, storage, etc.)
- [ ] API endpoints:
  - `GET /api/v1/tenants` (admin only - list all)
  - `GET /api/v1/tenants/{id}` (get tenant)
  - `POST /api/v1/tenants` (admin - create tenant)
  - `PUT /api/v1/tenants/{id}` (admin - update tenant)
  - `DELETE /api/v1/tenants/{id}` (admin - suspend tenant)
- [ ] Integration con API Key authentication
- [ ] Test tenant isolation

## Acceptance Criteria

* ✅ Organizations service migrato e refactorato
* ✅ Tenant settings configurabili
* ✅ Tenant limits implementati
* ✅ Admin API completa
* ✅ Test isolation passed

## Estimate

4 ore

## Riferimenti

* `gloria-backend/app/services/organizations.py`
* `gloria-backend/app/models/organizations.py`

---

### 🧩 [INTEGRATE-02] Integrazione Infrastructure Layer da CGS_2
**ID:** FYL-48

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M3: Migration & Integration

**Descrizione:**

# Obiettivo

Integrare Infrastructure Layer (adapters, factories, repositories) da CGS_2.

## Context

Infrastructure layer contiene LLM adapters, factories, tool implementations.

## Tasks

- [ ] Analizzare `CGS_2/core/infrastructure/`
- [ ] Portare LLM adapters:
  - `OpenAIAdapter`
  - `AnthropicAdapter`
  - `GeminiAdapter`
  - `DeepSeekAdapter`
- [ ] Portare `LLMProviderFactory`
- [ ] Portare tool implementations:
  - `RAGTool`
  - `PerplexityTool`
  - `SerperTool`
  - `ImageGenerationTool`
- [ ] Portare orchestration:
  - `PromptBuilder` (Jinja2)
  - `WorkflowOrchestrator`
- [ ] Adattare per asyncpg + Neon
- [ ] Test adapters

## Acceptance Criteria

* ✅ LLM adapters funzionanti (tutti i 4 provider)
* ✅ Factory pattern implementato
* ✅ Tool implementations portate
* ✅ Orchestration funzionante
* ✅ Test passed

## Estimate

8 ore

## Riferimenti

* `CGS_2/core/infrastructure/`
* FYL-11 (Multi-Provider LLM issue già creato)

---

### 🧩 [INTEGRATE-01] Integrazione Domain Layer da CGS_2
**ID:** FYL-47

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M3: Migration & Integration

**Descrizione:**

# Obiettivo

Integrare il Domain Layer (entities, value objects) da CGS_2 in gloria-backend-cgs.

## Context

CGS_2 ha DDD clean architecture. Serve integrare domain entities nel nuovo backend.

## Tasks

- [ ] Analizzare `CGS_2/core/domain/entities/`
- [ ] Portare domain entities:
  - `Agent` (specialist agents)
  - `Workflow` (workflow definition)
  - `Document` (knowledge base)
  - `CostEvent` (cost tracking)
- [ ] Portare value objects:
  - `Provider` (LLM provider enum)
  - `ModelConfig` (model configuration)
  - `ToolResult` (tool execution result)
- [ ] Adattare per nuovo database schema (asyncpg)
- [ ] Validation con Pydantic V2
- [ ] Test entities

## Acceptance Criteria

* ✅ Domain entities portate completamente
* ✅ Value objects portati
* ✅ Pydantic V2 validation
* ✅ Test passed

## Estimate

4 ore

## Riferimenti

* `CGS_2/core/domain/`
* Documento: `MigrationAnalysis/09-gloria-backend-integration-plan.md`

---

### 🧩 Portare Agent System (Specialist Agents)
**ID:** FYL-14

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M3: Migration & Integration

**Descrizione:**

# Obiettivo

Integrare il sistema di agent specialist da CGS_2 (copywriter, research_specialist, rag_specialist, compliance_specialist).

## Context

Agents sono componenti riutilizzabili con system prompts specifici per ruoli diversi.

## Tasks

- [ ] Portare `core/domain/entities/agent.py`
- [ ] Portare agent configurations:
  * Copywriter agent
  * Research specialist agent
  * RAG specialist agent
  * Compliance specialist agent
- [ ] Agent executor (orchestration)
- [ ] Agent system prompt templates
- [ ] Agent configuration per client (custom system prompts)
- [ ] Tabella database `agents` (client_id, name, system_prompt, config)
- [ ] API endpoints:
  * `GET /api/v1/agents` (list available agents)
  * `POST /api/v1/agents/configure` (customize agent per client)
  * `POST /api/v1/agents/execute` (execute single agent)

## Acceptance Criteria

* ✅ Agent system funzionante
* ✅ 4 specialist agents disponibili
* ✅ Agent customization per client
* ✅ Agent execution tracking (cost, tokens, latency)
* ✅ Integration con workflow engine

## Riferimenti

* Documento: `MigrationAnalysis/09-gloria-backend-integration-plan.md` (Week 5-6)

---

### 🧩 Portare RAG Tool (Knowledge Base + pgvector)
**ID:** FYL-13

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M3: Migration & Integration

**Descrizione:**

# Obiettivo

Integrare il RAG tool da CGS_2 per semantic search su knowledge base clienti.

## Context

RAG (Retrieval-Augmented Generation) è feature core per content personalizzato basato su knowledge base clienti.

## Tasks

- [ ] Portare `core/infrastructure/tools/rag_tool.py`
- [ ] Implementare embedding generation (OpenAI, Vertex AI)
- [ ] Implementare document upload + chunking
- [ ] Implementare semantic search (pgvector match_documents)
- [ ] Tabelle database:
  - `documents` (id, client_id, title, content, embedding, metadata)
  - `document_chunks` (per chunking strategy)
- [ ] API endpoints:
  - `POST /api/v1/knowledge/upload` (upload document)
  - `POST /api/v1/knowledge/search` (semantic search)
  - `GET /api/v1/knowledge/documents` (list per client)
  - `DELETE /api/v1/knowledge/documents/{id}`
- [ ] Storage S3 per file originali
- [ ] Chunking strategies (fixed size, semantic, sentence-based)

## Acceptance Criteria

* ✅ Upload document → chunking → embedding → store pgvector
* ✅ Semantic search con similarity threshold
* ✅ Multi-tenant (client isolation garantito)
* ✅ Storage S3 per file originali
* ✅ Performance search < 50ms

## Riferimenti

* Documento: `MigrationAnalysis/06-database-strategy-analysis.md` (pgvector)

---

### 🧩 Portare Workflow Engine (Template-Based)
**ID:** FYL-12

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M3: Migration & Integration

**Descrizione:**

# Obiettivo

Integrare il workflow engine configurabile da CGS_2 basato su template JSON.

## Context

Dal documento `04-current-strengths-detailed.md`: Workflow Engine Configurabile (⭐⭐⭐⭐) - template JSON + Jinja2 prompts, dependency graph dichiarativo.

## Tasks

- [ ] Portare `core/infrastructure/workflows/` (handlers, registry)
- [ ] Portare workflow templates JSON:
  - `enhanced_article.json`
  - `premium_newsletter.json`
  - `enhanced_article_with_image.json`
  - Altri workflow esistenti
- [ ] Portare `core/infrastructure/orchestration/prompt_builder.py` (Jinja2)
- [ ] Portare `core/prompts/` directory (Markdown templates)
- [ ] Implementare WorkflowRegistry con caching
- [ ] Dynamic workflow execution (da template JSON)
- [ ] Dependency resolution (topological sort)
- [ ] API endpoint `/api/v1/workflows/list` (available workflows)
- [ ] API endpoint `/api/v1/workflows/execute` (run workflow)

## Acceptance Criteria

* ✅ Workflow definiti via JSON template (no code)
* ✅ Prompt templates con Jinja2 (separati da logica)
* ✅ Task dependency graph resolution
* ✅ Registry con caching (performance)
* ✅ API per list + execute workflows
* ✅ Workflow customization per client

## Business Value

Configuration over code, customization facile, non-technical user friendly

## Riferimenti

* Documento: `MigrationAnalysis/04-current-strengths-detailed.md` (sezione 4)

---

### 🧩 Portare Multi-Provider LLM Orchestration (Adapters)
**ID:** FYL-11

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M3: Migration & Integration

**Descrizione:**

# Obiettivo

Integrare il sistema multi-provider LLM da CGS_2 con Factory pattern e Adapters.

## Context

Dal documento `04-current-strengths-detailed.md`: Multi-Provider Orchestration (⭐⭐⭐⭐⭐) - supporto OpenAI, Anthropic, Gemini, DeepSeek con interfaccia uniforme.

## Tasks

- [ ] Portare `core/infrastructure/factories/provider_factory.py`
- [ ] Portare adapters:
  - `OpenAIAdapter` (GPT-4o, GPT-4-turbo)
  - `AnthropicAdapter` (Claude 3.5 Sonnet)
  - `GeminiAdapter` (Gemini 2.0 Flash, Vertex AI support)
  - `DeepSeekAdapter` (DeepSeek Chat)
- [ ] Portare `BaseLLMAdapter` interface
- [ ] Config management per API keys (environment variables)
- [ ] Provider selection runtime (client può scegliere provider)
- [ ] Fallback automatico se provider è down
- [ ] Test adapters per ogni provider

## Acceptance Criteria

* ✅ Factory pattern funzionante (LLMProviderFactory.create_provider)
* ✅ Tutti i 4 provider supportati
* ✅ Interfaccia uniforme (generate, generate_streaming, calculate_cost)
* ✅ Provider switching in 1 linea di codice
* ✅ Config per default provider + API keys
* ✅ Fallback automatico implementato

## Business Value

Vendor independence, client choice, cost optimization per use case

## Riferimenti

* Documento: `MigrationAnalysis/04-current-strengths-detailed.md` (sezione 3)

---

### 🧩 Portare Cost Tracking System da CGS_2
**ID:** FYL-10

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M3: Migration & Integration

**Descrizione:**

# Obiettivo

Integrare il sistema di cost tracking granulare da CGS_2 in gloria-backend-cgs.

## Context

Dal documento `04-current-strengths-detailed.md`: il cost tracking è un **DIFFERENZIATORE COMPETITIVO UNICO** (⭐⭐⭐⭐⭐). Tracking multi-dimensionale: per provider, per agent, per tool, per workflow.

## Tasks

- [ ] Portare `core/infrastructure/logging/cost_calculator.py` da CGS_2
- [ ] Portare `core/infrastructure/logging/tool_cost_calculator.py`
- [ ] Portare `core/infrastructure/logging/workflow_reporter.py`
- [ ] Creare tabelle database per cost tracking:
  - `run_cost_events` (event_type, provider, agent, tool, cost_usd, tokens, metadata)
  - `cost_pricing` (provider, model, input_rate, output_rate)
- [ ] Integrare cost tracking in LLM adapters
- [ ] Integrare cost tracking in tool calls (Perplexity, Serper, Image gen)
- [ ] API endpoint `/api/v1/costs/report` (breakdown multi-dimensionale)
- [ ] API endpoint `/api/v1/costs/workflow/{run_id}` (cost per singolo run)

## Acceptance Criteria

* ✅ Ogni chiamata LLM traccia cost (input/output tokens separati)
* ✅ Ogni tool call traccia cost
* ✅ Cost breakdown per provider, agent, tool, workflow
* ✅ Report JSON con percentages e totals
* ✅ Database ledger completo (audit-ready)

## Business Value

Marketing differentiator: "Transparent cost breakdown - vedi dove vanno i soldi"

## Riferimenti

* Documento: `MigrationAnalysis/04-current-strengths-detailed.md` (sezione 1)
* Documento: `MigrationAnalysis/08-cost-tracking-and-framework-strategy.md`

---

### 🧩 [MIGRATE-04] Migrare Admin Utilities (Cache, Config)
**ID:** FYL-46

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M3: Migration & Integration

**Descrizione:**

# Obiettivo

Migrare utility admin esistenti da gloria-backend.

## Context

gloria-backend ha alcuni endpoint admin utili (cache management, config, etc.).

## Tasks

- [ ] Analizzare `app/api/routes/admin_cache.py`
- [ ] Migrare cache management endpoints:
  - `DELETE /api/v1/admin/cache` (clear all cache)
  - `DELETE /api/v1/admin/cache/{key}` (clear specific key)
  - `GET /api/v1/admin/cache/stats` (cache statistics)
- [ ] Admin config endpoints:
  - `GET /api/v1/admin/config` (view all config)
  - `PUT /api/v1/admin/config/{key}` (update config)
- [ ] Admin health endpoints:
  - `GET /api/v1/admin/health/detailed` (detailed status)
  - `GET /api/v1/admin/metrics` (Prometheus metrics export)
- [ ] Admin authentication (admin role required)
- [ ] Audit log per admin actions

## Acceptance Criteria

* ✅ Cache management API migrato
* ✅ Config management API migrato
* ✅ Admin authentication enforced
* ✅ Audit log completo

## Estimate

3 ore

## Riferimenti

* `gloria-backend/app/api/routes/admin_cache.py`

---

### 🧩 [ARCH-06] Implementare Webhook System
**ID:** FYL-38

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M3: Migration & Integration

**Descrizione:**

# Obiettivo

Sistema di webhooks per notifiche event-driven ai client.

## Context

Client devono poter ricevere notifiche asincrone:

* Workflow completato
* Job completed/failed
* Cost threshold raggiunto
* Error alert

## Tasks

- [ ] Creare tabella `webhooks`:
  - tenant_id
  - url
  - secret (per HMAC signature)
  - events (array: workflow.completed, job.failed, etc.)
  - active (boolean)
  - retry_policy
- [ ] Implementare `WebhookService`
- [ ] HMAC signature per security (header `X-Webhook-Signature`)
- [ ] Retry logic (exponential backoff, max 5 attempts)
- [ ] Webhook delivery queue (async)
- [ ] Webhook delivery logs
- [ ] API endpoints:
  - `POST /api/v1/webhooks` (create)
  - `GET /api/v1/webhooks` (list)
  - `PUT /api/v1/webhooks/{id}` (update)
  - `DELETE /api/v1/webhooks/{id}` (delete)
  - `POST /api/v1/webhooks/{id}/test` (test delivery)
- [ ] Monitoring webhook delivery success rate

## Acceptance Criteria

* ✅ Webhook registration API funzionante
* ✅ HMAC signature per security
* ✅ Retry logic con exponential backoff
* ✅ Delivery logs completi
* ✅ Test endpoint funzionante
* ✅ Metrics delivery success rate

## Business Value

Event-driven architecture, client integration facile, real-time notifications

## Estimate

5 ore

---

### 🧩 Portare External Tools (Perplexity, Serper, Image Gen)
**ID:** FYL-15

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M3: Migration & Integration

**Descrizione:**

# Obiettivo

Integrare i tool esterni da CGS_2: Perplexity (web research), Serper (search), Image Generation.

## Context

Tools esterni arricchiscono i workflow con ricerca web, immagini generate, dati real-time.

## Tasks

- [ ] Portare `core/infrastructure/tools/perplexity_tool.py`
- [ ] Portare `core/infrastructure/tools/serper_tool.py`
- [ ] Portare `core/infrastructure/tools/image_generation_tool.py`
- [ ] Config API keys per tools esterni
- [ ] Cost tracking per tool calls (già implementato in cost_calculator)
- [ ] Tool error handling + retry logic
- [ ] Tool timeout configuration
- [ ] API endpoints (optional, per testing):
  * `POST /api/v1/tools/perplexity` (test research)
  * `POST /api/v1/tools/serper` (test search)
  * `POST /api/v1/tools/image` (test image gen)

## Acceptance Criteria

* ✅ Perplexity integration funzionante (Sonar, Sonar Pro)
* ✅ Serper integration funzionante (Google Search API)
* ✅ Image generation funzionante (OpenAI DALL-E, Gemini Imagen)
* ✅ Cost tracking per tool call
* ✅ Error handling robusto (fallback, retry)
* ✅ Timeout configurabile

## Riferimenti

* Documento: `MigrationAnalysis/08-cost-tracking-and-framework-strategy.md`

---

### 🧩 [API-05] Implementare Prometheus Metrics & Grafana Dashboards
**ID:** FYL-58

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M4: API & Performance

**Descrizione:**

# Obiettivo

Implementare Prometheus metrics collection e Grafana dashboards.

## Context

Dal documento `02-api-architecture-analysis.md`: No metrics collection attualmente, necessario per production observability.

## Tasks

- [ ] Installare `prometheus-fastapi-instrumentator`
- [ ] Setup Prometheus endpoint `/metrics`:
  - Request rate (req/sec per endpoint)
  - Request latency (p50, p95, p99)
  - Error rate per endpoint
  - Active connections
- [ ] Custom business metrics:
  - Workflow executions (counter per workflow type)
  - LLM calls (counter per provider/model)
  - Cost metrics (gauge USD/hour, USD/day)
  - Token usage (counter per provider)
  - Cache hit rate (gauge)
  - RAG search latency (histogram)
- [ ] Grafana dashboard setup:
  - Dashboard 1: API Performance (latency, rate, errors)
  - Dashboard 2: Business Metrics (workflows, costs, tokens)
  - Dashboard 3: Infrastructure (cache, database, connections)
- [ ] Alert rules:
  - High error rate (>5%)
  - High latency (p99 >1s)
  - Cost anomalies (>200% baseline)
  - Cache hit rate low (<20%)
- [ ] Documentation Grafana setup

## Acceptance Criteria

* ✅ Prometheus `/metrics` endpoint funzionante
* ✅ 15+ custom metrics implementate
* ✅ Grafana dashboards configurati (3 totali)
* ✅ Alert rules attive
* ✅ Documentation setup completa

## Estimate

2 giorni

## Riferimenti

* Documento: `MigrationAnalysis/02-api-architecture-analysis.md` (sezione 13.5)
* Issue correlato: FYL-18 (Monitoring già creato)

---

### 🧩 [API-04] Implementare Redis Caching Layer
**ID:** FYL-57

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M4: API & Performance

**Descrizione:**

# Obiettivo

Implementare Redis caching per LLM responses, RAG retrieval, provider metadata.

## Context

Dal documento `02-api-architecture-analysis.md`: No caching attualmente, costosissimo ripetere chiamate LLM identiche.

## Tasks

- [ ] Setup Redis client (asyncio-redis)
- [ ] Implementare `CacheService`:
  - `get(key)` → Optional\[Any\]
  - `set(key, value, ttl)` → bool
  - `delete(key)` → bool
  - `clear_pattern(pattern)` → int
- [ ] Cache LLM responses:
  - Cache key: `hash(prompt + model + temperature + max_tokens)`
  - TTL: 24 ore
  - Invalidation: manual via endpoint
- [ ] Cache RAG retrieval:
  - Cache key: `hash(query + client_id + top_k)`
  - TTL: 1 ora
  - Invalidation: on document upload
- [ ] Cache provider metadata:
  - Cache key: `provider:{provider_name}:models`
  - TTL: 12 ore
- [ ] Cache invalidation endpoints:
  - `DELETE /api/v1/admin/cache` (clear all)
  - `DELETE /api/v1/admin/cache/{pattern}` (clear pattern)
  - `GET /api/v1/admin/cache/stats` (cache hit rate)
- [ ] Metrics cache hit/miss rate
- [ ] Configuration (Redis URL, TTL defaults)

## Acceptance Criteria

* ✅ Redis integration funzionante
* ✅ LLM response caching attivo
* ✅ RAG retrieval caching attivo
* ✅ Cache hit rate >40% dopo 1 settimana
* ✅ Invalidation endpoints funzionanti
* ✅ Metrics Prometheus cache hit rate

## Business Value

Riduzione costi LLM 30-50%, performance 5-10x su cache hits

## Estimate

3 giorni

## Riferimenti

* Documento: `MigrationAnalysis/02-api-architecture-analysis.md` (sezione 13.4)
* Issue correlato: FYL-20 (Caching Layer già creato)

---

### 🧩 [API-02] Implementare Pagination Standardizzata
**ID:** FYL-55

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M4: API & Performance

**Descrizione:**

# Obiettivo

Standardizzare pagination per tutti gli endpoint di listing.

## Context

Dal documento `02-api-architecture-analysis.md`: Pagination definita ma non sempre usata consistentemente.

## Tasks

- [ ] Creare model `PaginatedResponse[T]` generic:

  ```python
  class PaginatedResponse(BaseModel, Generic[T]):
      items: List[T]
      total: int
      page: int
      per_page: int
      total_pages: int
      has_next: bool
      has_prev: bool
  ```
- [ ] Query params standardizzati:
  - `page` (default: 1)
  - `per_page` (default: 50, max: 250)
  - `sort_by` (optional)
  - `sort_order` (asc/desc)
- [ ] Applicare a tutti gli endpoint:
  - `/api/v1/content/` (content listing)
  - `/api/v1/workflows/` (workflow listing)
  - `/api/v1/knowledge-base/clients/{client}/documents` (documents)
  - `/api/v1/audit/logs` (audit logs)
- [ ] Helper function `paginate()` riutilizzabile
- [ ] Documentation OpenAPI aggiornata
- [ ] Test suite pagination

## Acceptance Criteria

* ✅ PaginatedResponse model generic implementato
* ✅ Tutti gli endpoint listing usano pagination standard
* ✅ Query params validati (per_page max 250)
* ✅ Response include has_next/has_prev
* ✅ Performance tested (10k+ records)

## Estimate

2 giorni

## Riferimenti

* Documento: `MigrationAnalysis/02-api-architecture-analysis.md` (sezione 13.2)

---

### 🧩 [API-01] Implementare Content Listing & Retrieval Endpoints
**ID:** FYL-54

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M4: API & Performance

**Descrizione:**

# Obiettivo

Implementare endpoint completi per listing e retrieval dei contenuti generati.

## Context

Dal documento `02-api-architecture-analysis.md`: Attualmente `/content/` ritorna array vuoto, necessario implementare listing completo con pagination.

## Tasks

- [ ] Implementare `GET /api/v1/content/` (lista paginata)
  - Query params: `page`, `per_page`, `client_id`, `workflow_type`, `date_from`, `date_to`
  - Response: PaginatedResponse model
- [ ] Implementare `GET /api/v1/content/{id}` (dettaglio completo)
  - Include: metadata, cost breakdown, workflow metrics, agent logs
- [ ] Implementare `GET /api/v1/content/{id}/export` (export multi-format)
  - Formati: JSON, PDF, Markdown, HTML
  - Query param: `?format=pdf`
- [ ] Creare tabella database `generated_content`:
  - id, client_id, workflow_type, title, body, metadata, cost_breakdown, created_at
- [ ] Implementare filtri avanzati:
  - By workflow type
  - By date range
  - By cost range
  - By success/failure status
- [ ] Test suite completa

## Acceptance Criteria

* ✅ Listing paginato funzionante (max 100 items per page)
* ✅ Retrieval by ID con metadata completo
* ✅ Export PDF/Markdown/HTML funzionante
* ✅ Filtri query testati
* ✅ Performance <100ms (listing)

## Estimate

3 giorni

## Riferimenti

* Documento: `MigrationAnalysis/02-api-architecture-analysis.md` (sezione 13.1)
* Endpoint esistente: `POST /api/v1/content/generate`

---

### 🧩 Implementare Rate Limiting & Throttling
**ID:** FYL-21

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M4: API & Performance

**Descrizione:**

# Obiettivo

Implementare rate limiting per proteggere API da abuse e garantire fair usage.

## Context

Rate limiting è essenziale per production API con multiple client.

## Tasks

- [ ] Implementare rate limiting middleware:
  - Per API key (es. 100 req/min per key)
  - Per IP address (es. 10 req/min unauthenticated)
  - Per endpoint specifico (costly endpoints più restrictive)
- [ ] Rate limit storage (Redis)
- [ ] Rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
- [ ] Rate limit exceeded response (429 Too Many Requests)
- [ ] Configurable rate limits per client (premium clients higher limits)
- [ ] Rate limit bypass per internal services
- [ ] Metrics rate limit hits (Prometheus)

## Acceptance Criteria

* ✅ Rate limiting attivo per tutti gli endpoints
* ✅ Configurable limits per API key
* ✅ Standard headers (X-RateLimit-\*)
* ✅ 429 response con retry-after
* ✅ Metrics tracked (Prometheus)

## Riferimenti

* Best practices API rate limiting

---

### 🧩 Setup Monitoring & Observability (Prometheus + Grafana)
**ID:** FYL-18

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M4: API & Performance

**Descrizione:**

# Obiettivo

Implementare monitoring completo per production observability.

## Context

Dal documento `06-database-strategy-analysis.md`: Observability è critica per debugging rapido in production.

## Tasks

- [ ] Setup Prometheus server
- [ ] Instrumentazione FastAPI app:
  * Request latency (p50, p95, p99)
  * Request rate (per endpoint)
  * Error rate (per endpoint)
  * Active connections
- [ ] PostgreSQL metrics (postgres_exporter):
  * Query latency (pg_stat_statements)
  * Connection pool utilization
  * Cache hit ratio
  * Slow queries (>100ms)
- [ ] Custom business metrics:
  * Workflow executions (per type)
  * LLM calls (per provider)
  * Cost tracking (USD/hour, USD/day)
  * Token usage (per provider)
- [ ] Setup Grafana dashboards
- [ ] Alert rules (Alertmanager):
  * High error rate (>5%)
  * High latency (p99 >1s)
  * Database connection pool exhausted
  * Cost anomalies (>200% vs baseline)

## Acceptance Criteria

* ✅ Prometheus scraping metrics
* ✅ Grafana dashboards configurati
* ✅ Alert rules attive (email/Slack)
* ✅ pg_stat_statements enabled
* ✅ Custom business metrics tracked

## Riferimenti

* Documento: `MigrationAnalysis/06-database-strategy-analysis.md` (Observability)

---

### 🧩 API Documentation (OpenAPI/Swagger)
**ID:** FYL-22

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M4: API & Performance

**Descrizione:**

# Obiettivo

Creare documentazione API completa e interattiva per sviluppatori.

## Context

FastAPI genera automaticamente OpenAPI docs, ma serve arricchire con esempi, description, use cases.

## Tasks

- [ ] Enrichare endpoint docstrings (description, examples, responses)
- [ ] Aggiungere request/response examples per ogni endpoint
- [ ] Aggiungere security schemes (API Key, JWT) in OpenAPI spec
- [ ] Documentare error codes e error responses
- [ ] Tags per endpoint grouping (auth, workflows, costs, knowledge, etc.)
- [ ] Swagger UI customization (logo, theme)
- [ ] ReDoc alternative UI setup
- [ ] Postman collection export
- [ ] SDK generation (optional, Python/JavaScript client SDKs)

## Acceptance Criteria

* ✅ Tutti gli endpoints documentati (description + examples)
* ✅ Error responses documentate (4xx, 5xx)
* ✅ Security schemes dichiarati
* ✅ Swagger UI customizzato
* ✅ Postman collection disponibile
* ✅ /docs e /redoc accessibili

## Riferimenti

* FastAPI OpenAPI documentation best practices

---

### 🧩 Implementare Caching Layer (Redis)
**ID:** FYL-20

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M4: API & Performance

**Descrizione:**

# Obiettivo

Implementare caching per migliorare performance e ridurre costi LLM.

## Context

Dal documento `09-gloria-backend-integration-plan.md` (Week 9-10 optional): Caching può ridurre costi LLM del 30-50%.

## Tasks

- [ ] Setup Redis server (AWS ElastiCache / self-hosted)
- [ ] Implementare cache layers:
  - LLM response cache (prompt hash → response)
  - RAG search cache (query embedding hash → documents)
  - Workflow result cache (topic + workflow → content)
- [ ] Cache invalidation strategies:
  - TTL-based (1h default, configurabile)
  - Manual invalidation (API endpoint)
  - LRU eviction policy
- [ ] Cache hit rate metrics (Prometheus)
- [ ] Cache warming (optional, pre-populate common queries)
- [ ] Cache bypass header (X-Cache-Control: no-cache)

## Acceptance Criteria

* ✅ Redis integration funzionante
* ✅ LLM response caching attivo
* ✅ Cache hit rate >40% dopo 1 settimana
* ✅ TTL configurabile per cache type
* ✅ Metrics cache hit/miss rate

## Business Value

Riduzione costi LLM 30-50%, performance improvement 5-10x per cache hits

## Riferimenti

* Documento: `MigrationAnalysis/09-gloria-backend-integration-plan.md` (Week 9-10)
* Documento: `MigrationAnalysis/06-database-strategy-analysis.md` (Redis caching)

---

### 🧩 [TEST-03] Test Suite Multi-tenancy & Tenant Isolation
**ID:** FYL-51

**Status:** Backlog  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M5: Testing & Quality

**Descrizione:**

# Obiettivo

Test completi per tenant isolation (security-critical).

## Context

Tenant isolation è REQUISITO CRITICO. Zero possibilità di data leakage.

## Tasks

- [ ] Unit tests tenant context:
  - Tenant extraction da API key
  - Tenant context propagation
  - Tenant context in async tasks
- [ ] Integration tests tenant isolation:
  - Client A crea documento → Client B non può vedere
  - Client A esegue workflow → Client B non può accedere result
  - Client A query knowledge base → risultati solo suoi documenti
- [ ] Stress tests tenant isolation (100 tenant simultanei)
- [ ] Security tests:
  - Tenant ID spoofing attempts
  - SQL injection tenant bypass attempts
- [ ] Database RLS verification tests

## Acceptance Criteria

* ✅ Test coverage tenant isolation 100%
* ✅ Stress tests passed (100 tenant)
* ✅ Security tests passed (zero bypass)
* ✅ RLS policies verified

## Estimate

5 ore

---

### 🧩 Security Hardening & Best Practices
**ID:** FYL-24

**Status:** Backlog  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M5: Testing & Quality

**Descrizione:**

# Obiettivo

Implementare security best practices per production-ready application.

## Context

Security hardening è critico per evitare vulnerabilità comuni.

## Tasks

- [ ] HTTPS enforcement (redirect HTTP → HTTPS)
- [ ] CORS configuration (whitelist domains)
- [ ] Security headers:
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security (HSTS)
  - Content-Security-Policy
- [ ] Input validation (Pydantic models già implementati, verify completeness)
- [ ] SQL injection protection (asyncpg parametrized queries)
- [ ] XSS protection (escape output, CSP headers)
- [ ] Secrets management (no hardcoded secrets, use env vars/Vault)
- [ ] Dependency security audit (pip-audit, safety)
- [ ] Security scan in CI/CD (bandit, semgrep)

## Acceptance Criteria

* ✅ HTTPS enforced
* ✅ CORS configurato correttamente
* ✅ Security headers implementati
* ✅ Input validation completa
* ✅ No secrets in code (audit passed)
* ✅ Security scan passed (CI/CD)

## Riferimenti

* OWASP Top 10
* FastAPI security best practices

---

### 🧩 [TEST-04] Test Suite Cost Tracking
**ID:** FYL-52

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M5: Testing & Quality

**Descrizione:**

# Obiettivo

Test completi per cost tracking system (feature differenziante).

## Context

Cost tracking è DIFFERENZIATORE COMPETITIVO. Deve essere preciso e affidabile al 100%.

## Tasks

- [ ] Unit tests cost calculator:
  - OpenAI cost calculation (GPT-4o, GPT-4-turbo)
  - Anthropic cost calculation (Claude 3.5 Sonnet)
  - Gemini cost calculation (Gemini 2.0 Flash)
  - DeepSeek cost calculation
  - Tool cost calculation (Perplexity, Serper, Image Gen)
- [ ] Integration tests cost tracking:
  - Workflow execution → cost tracked correttamente
  - Multi-step workflow → cost breakdown per step
  - Failed workflow → cost partial tracked
- [ ] Accuracy tests (comparison con invoice provider)
- [ ] Performance tests (cost tracking overhead <5ms)

## Acceptance Criteria

* ✅ Test coverage cost tracking 100%
* ✅ Accuracy tests passed (±1% provider invoice)
* ✅ Performance tests passed
* ✅ Cost breakdown verification

## Estimate

4 ore

---

### 🧩 [TEST-02] Test Suite Authentication & Authorization
**ID:** FYL-50

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M5: Testing & Quality

**Descrizione:**

# Obiettivo

Test completi per authentication & authorization layer.

## Context

Auth è security-critical. Serve test coverage 100%.

## Tasks

- [ ] Unit tests API Key authentication:
  - Valid API key → success
  - Invalid API key → 401
  - Expired API key → 401
  - Disabled API key → 403
  - API key tenant isolation
- [ ] Unit tests JWT authentication:
  - Valid JWT → success
  - Expired JWT → 401
  - Invalid signature → 401
  - Refresh token rotation
- [ ] Integration tests RBAC:
  - Admin role → access admin endpoints
  - User role → access user endpoints
  - User role → 403 on admin endpoints
- [ ] Security tests:
  - SQL injection attempts
  - XSS attempts
  - CSRF protection
- [ ] Performance tests (auth overhead <10ms)

## Acceptance Criteria

* ✅ Test coverage authentication 100%
* ✅ Test coverage authorization 100%
* ✅ Security tests passed
* ✅ Performance tests passed

## Estimate

4 ore

---

### 🧩 [TEST-01] Setup Test Infrastructure Completo
**ID:** FYL-49

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M5: Testing & Quality

**Descrizione:**

# Obiettivo

Setup completo test infrastructure (unit, integration, E2E).

## Context

Testing è fondamentale per production readiness. Serve setup completo prima di deployment.

## Tasks

- [ ] Setup pytest configuration (`pytest.ini`, `conftest.py`)
- [ ] Setup test fixtures riutilizzabili:
  - `test_client` (FastAPI TestClient)
  - `test_db` (database test con cleanup automatico)
  - `mock_llm_provider` (mock LLM calls)
  - `test_tenant` (tenant isolation test)
- [ ] Setup test database separato (Neon branch dev-test)
- [ ] Setup mocking LLM providers (no real API calls)
- [ ] Coverage configuration (pytest-cov, target >80%)
- [ ] Test helpers:
  - `create_test_user()`
  - `create_test_api_key()`
  - `create_test_document()`
- [ ] CI integration (GitHub Actions / GitLab CI)
- [ ] Documentation test best practices

## Acceptance Criteria

* ✅ pytest setup completo
* ✅ Test fixtures riutilizzabili
* ✅ Test database configurato
* ✅ Mocking LLM providers funzionante
* ✅ Coverage >80% target
* ✅ CI integration funzionante

## Estimate

5 ore

## Riferimenti

* FYL-16 (Testing Infrastructure issue già creato)

---

### 🧩 Setup CI/CD Pipeline
**ID:** FYL-17

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M5: Testing & Quality

**Descrizione:**

# Obiettivo

Implementare CI/CD pipeline automatizzato per deploy sicuro e veloce.

## Context

Deployment automatizzato con testing, linting, security checks prima di production.

## Tasks

- [ ] Setup GitHub Actions / GitLab CI
- [ ] Pipeline stages:
  - Lint (black, flake8, mypy)
  - Security scan (bandit, safety)
  - Unit tests + coverage report
  - Integration tests
  - Build Docker image
  - Push to container registry
  - Deploy to staging (auto)
  - Deploy to production (manual approval)
- [ ] Environment management (dev, staging, prod)
- [ ] Secret management (GitHub Secrets / Vault)
- [ ] Rollback mechanism
- [ ] Deployment notifications (Slack/Discord)

## Acceptance Criteria

* ✅ CI runs on every PR (lint + tests)
* ✅ CD deploys to staging automatically
* ✅ Production deployment require manual approval
* ✅ Docker image tagging (git SHA + semver)
* ✅ Rollback mechanism funzionante
* ✅ Deploy notifications attive

## Riferimenti

* Best practices CI/CD per Python FastAPI apps

---

### 🧩 Setup Testing Infrastructure (Unit + Integration)
**ID:** FYL-16

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M5: Testing & Quality

**Descrizione:**

# Obiettivo

Implementare testing completo per garantire qualità e stabilità del codice.

## Context

Dal documento `09-gloria-backend-integration-plan.md` (Week 7-8): Testing & Polish è fase dedicata prima di production.

## Tasks

- [ ] Setup pytest configuration
- [ ] Unit tests per:
  - Cost calculator (LLM + tools)
  - LLM adapters (mock provider APIs)
  - Workflow engine (template parsing, dependency resolution)
  - Authentication middleware (API Key + JWT)
- [ ] Integration tests per:
  - End-to-end workflows (mock LLM responses)
  - Database operations (pgvector search)
  - API endpoints (FastAPI TestClient)
- [ ] Test fixtures e mocks
- [ ] Coverage report (target >80%)
- [ ] CI integration (GitHub Actions / GitLab CI)

## Acceptance Criteria

* ✅ Unit tests coverage >80%
* ✅ Integration tests per workflow principali
* ✅ CI runs tests automaticamente su PR
* ✅ Test fixtures riutilizzabili
* ✅ Mock provider APIs (no real API calls in tests)

## Riferimenti

* Documento: `MigrationAnalysis/09-gloria-backend-integration-plan.md` (Week 7-8)

---

### 🧩 Performance Optimization & Load Testing
**ID:** FYL-25

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M5: Testing & Quality

**Descrizione:**

# Obiettivo

Ottimizzare performance e verificare che l'app regga carichi production.

## Context

Performance optimization è necessaria prima di production launch.

## Tasks

- [ ] Profiling application (cProfile, py-spy):
  - Identificare bottlenecks
  - Ottimizzare query database
  - Ottimizzare workflow execution
- [ ] Database optimization:
  - Indexes (pgvector HNSW, query optimization)
  - Connection pool tuning (asyncpg min/max size)
  - Query optimization (EXPLAIN ANALYZE)
- [ ] Async optimization:
  - Parallelize independent operations
  - Use asyncio.gather() where possible
- [ ] Load testing (Locust / k6):
  - Test 100 concurrent users
  - Test 1000 req/min sustained
  - Identify breaking point
- [ ] Stress testing (peak load)
- [ ] Latency optimization (target p99 <500ms)

## Acceptance Criteria

* ✅ Load test passed (100 concurrent users)
* ✅ p99 latency <500ms
* ✅ Database queries <50ms (p95)
* ✅ Connection pool tuned (no exhaustion)
* ✅ Breaking point identified (>X req/min)

## Riferimenti

* Python performance optimization best practices

---

### 🧩 [AGENTIC-04] Implementare Streaming Response (SSE)
**ID:** FYL-63

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M6: Advanced Features

**Descrizione:**

# Obiettivo

Implementare Server-Sent Events (SSE) per streaming workflow progress.

## Context

Dal documento `07-agentic-ai-framework-analysis.md` (Improvement #4): Response sync (user aspetta), streaming migliora UX.

## Tasks

- [ ] Implementare SSE endpoint:

  ```python
  from sse_starlette.sse import EventSourceResponse
  
  @router.post("/workflows/{workflow_type}/stream")
  async def stream_workflow(workflow_type: str, request: ContentRequest):
      async def event_generator():
          async for event in execute_workflow_stream(workflow_type, request.dict()):
              yield {
                  "event": event["type"],
                  "data": json.dumps(event)
              }
      return EventSourceResponse(event_generator())
  ```
- [ ] Workflow streaming events:
  - `{"type": "progress", "step": "research", "status": "running"}`
  - `{"type": "progress", "step": "research", "status": "completed", "preview": "..."}`
  - `{"type": "tool_call", "tool": "web_search", "input": "..."}`
  - `{"type": "tool_result", "tool": "web_search", "output": "..."}`
  - `{"type": "complete", "result": {...}, "metrics": {...}}`
  - `{"type": "error", "message": "..."}`
- [ ] Frontend integration:
  - JavaScript EventSource client example
  - React hook `useWorkflowStream()`
- [ ] Error handling SSE:
  - Reconnection logic
  - Error event propagation
- [ ] Test SSE streaming:
  - Integration test end-to-end
  - Load test (100 concurrent streams)
- [ ] Documentation SSE protocol

## Acceptance Criteria

* ✅ SSE endpoint `/stream` funzionante
* ✅ Workflow events streaming real-time
* ✅ Frontend integration example
* ✅ Error handling robusto
* ✅ Load test passed (100 streams)
* ✅ Documentation completa

## Business Value

UX migliore (progress visible), perceived performance, no timeout issues

## Estimate

1-2 settimane (backend + frontend integration)

## Riferimenti

* Documento: `MigrationAnalysis/07-agentic-ai-framework-analysis.md` (sezione 4.2.4)
* Alternative: WebSocket (issue FYL-60 già creato)

---

### 🧩 [AGENTIC-03] Implementare Agent Memory (Conversation History)
**ID:** FYL-62

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M6: Advanced Features

**Descrizione:**

# Obiettivo

Implementare conversation history per agent stateful (multi-turn conversations).

## Context

Dal documento `07-agentic-ai-framework-analysis.md` (Improvement #3): Agents sono stateless, conversation history migliora context retention.

## Tasks

- [ ] Estendere `AgentExecutor` per conversation history:

  ```python
  class ConversationHistory:
      messages: List[Dict[str, str]]  # {"role": "user/assistant", "content": "..."}
      max_messages: int = 20  # Sliding window
      
      def add_message(self, role: str, content: str):
          self.messages.append({"role": role, "content": content})
          if len(self.messages) > self.max_messages:
              self.messages = self.messages[-self.max_messages:]
  ```
- [ ] Context injection in agent execution:
  - Retrieve conversation_history from context
  - Build prompt with history (OpenAI chat format)
  - Update history post-execution
- [ ] Storage conversation history:
  - In-memory per request (context dict)
  - Database persistence (optional, tabella `conversations`)
- [ ] API endpoint conversation management:
  - `GET /api/v1/conversations/{id}` (retrieve history)
  - `DELETE /api/v1/conversations/{id}` (clear history)
- [ ] Config conversation memory:
  - `max_messages` (default: 20)
  - `enable_history` (default: false, opt-in)
- [ ] Test multi-turn conversations:
  - Test: 5-turn conversation
  - Test: context retention across turns
- [ ] Documentation conversation patterns

## Acceptance Criteria

* ✅ Conversation history implementato
* ✅ Multi-turn conversations funzionanti
* ✅ Context retention verified
* ✅ Storage (memory + DB optional)
* ✅ API endpoints funzionanti
* ✅ Test coverage complete

## Business Value

Multi-turn conversational use cases, context-aware agents, chatbot support

## Estimate

1 settimana

## Riferimenti

* Documento: `MigrationAnalysis/07-agentic-ai-framework-analysis.md` (sezione 4.2.3)
* File: `core/infrastructure/orchestration/agent_executor.py`

---

### 🧩 [AGENTIC-02] Implementare Conditional Branching per Workflows
**ID:** FYL-61

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M6: Advanced Features

**Descrizione:**

# Obiettivo

Aggiungere conditional logic nei workflow per quality gates e retry strategies.

## Context

Dal documento `07-agentic-ai-framework-analysis.md` (Improvement #2): Workflow sono linear, conditional branching migliora robustezza.

## Tasks

- [ ] Estendere `WorkflowHandler` base class:

  ```python
  async def assess_quality(self, result: Any) -> QualityScore:
      # Quality assessment logic
      pass
  ```
- [ ] Implementare quality gates:
  - Research quality check (source count, content length)
  - Compliance check (brand guidelines, legal constraints)
  - Content quality check (grammar, coherence)
- [ ] Retry strategies:
  - Max retries: 2
  - Backoff strategy: immediate (no delay)
  - Alternative approach on retry (different prompt, different model)
- [ ] Workflow conditional logic examples:

  ```python
  # Research quality gate
  if quality_score < 0.7:
      research_result = await retry_research(alternative_approach)
  
  # Compliance gate
  if not compliance_check["approved"]:
      content = await revise_content(compliance_feedback)
  ```
- [ ] Metrics quality gate triggers:
  - Counter: quality_gate_triggered_total
  - Counter: retry_attempts_total
- [ ] Logging conditional paths:
  - Log: "Quality gate triggered (score=0.6), retrying"
- [ ] Test suite conditional workflows
- [ ] Documentation conditional logic patterns

## Acceptance Criteria

* ✅ Quality assessment implementato (3 tipi)
* ✅ Retry logic funzionante (max 2 retries)
* ✅ Compliance check integrato
* ✅ Metrics tracked
* ✅ Test coverage conditional paths
* ✅ Workflow robustezza improved

## Business Value

Workflow più robusti, quality assurance, compliance enforcement

## Estimate

3 giorni per workflow (feature-by-feature basis)

## Riferimenti

* Documento: `MigrationAnalysis/07-agentic-ai-framework-analysis.md` (sezione 4.2.2)
* File: `core/infrastructure/workflows/handlers/`

---

### 🧩 [AGENTIC-01] Implementare Function Calling Opzionale (Hybrid)
**ID:** FYL-60

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M6: Advanced Features

**Descrizione:**

# Obiettivo

Supportare function calling nativo per provider che lo supportano, fallback a regex pattern custom.

## Context

Dal documento `07-agentic-ai-framework-analysis.md` (Improvement #1): Pattern custom funziona ma function calling nativo migliora accuracy.

## Tasks

- [ ] Analizzare `AgentExecutor.execute_agent()` attuale
- [ ] Implementare detection provider capabilities:

  ```python
  def supports_function_calling(provider: LLMProvider) -> bool:
      return provider in [LLMProvider.OPENAI, LLMProvider.ANTHROPIC, LLMProvider.GEMINI]
  ```
- [ ] Implementare function calling path:
  - Build tools JSON schema (OpenAPI format)
  - Call LLM with tools parameter
  - Parse structured tool_calls response
- [ ] Mantenere fallback regex pattern:
  - Per DeepSeek (no function calling)
  - Per backward compatibility
- [ ] Unified tool execution (same logic per entrambi i path)
- [ ] Config flag `prefer_function_calling` (default: true)
- [ ] Test suite per entrambi i path:
  - OpenAI function calling
  - Anthropic tool use
  - DeepSeek regex pattern
  - Gemini function calling
- [ ] Metrics function calling success rate

## Acceptance Criteria

* ✅ Function calling per OpenAI/Anthropic/Gemini
* ✅ Fallback regex per DeepSeek
* ✅ Tool execution unificata
* ✅ Config flag funzionante
* ✅ Test coverage 100%
* ✅ Accuracy improvement >10% (A/B test)

## Business Value

Best of both worlds: native function calling quando possibile, flexibility fallback

## Estimate

1 settimana

## Riferimenti

* Documento: `MigrationAnalysis/07-agentic-ai-framework-analysis.md` (sezione 4.2)
* File: `core/infrastructure/orchestration/agent_executor.py`

---

### 🧩 [API-06] Implementare WebSocket Streaming per Real-time Updates
**ID:** FYL-59

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M6: Advanced Features

**Descrizione:**

# Obiettivo

Implementare WebSocket endpoint per streaming workflow progress real-time.

## Context

Dal documento `02-api-architecture-analysis.md`: WebSocket configurato ma non implementato. Use case: real-time workflow updates, streaming LLM responses.

## Tasks

- [ ] Implementare WebSocket endpoint `/ws`:
  - Connection management (connect/disconnect)
  - Authentication via query param token
  - Heartbeat ping/pong (keep-alive)
- [ ] Workflow streaming:
  - Event: `workflow.started` (workflow_id, type)
  - Event: `task.started` (task_id, agent_name)
  - Event: `task.completed` (task_id, preview)
  - Event: `tool.called` (tool_name, input)
  - Event: `tool.result` (tool_name, output)
  - Event: `workflow.completed` (result, metrics)
  - Event: `workflow.failed` (error_message)
- [ ] LLM response streaming (optional):
  - Stream tokens real-time
  - Event: `llm.token` (token_text)
- [ ] Client reconnection handling:
  - Resume from last event
  - Event replay buffer (last 100 events)
- [ ] WebSocket client example (Python, JavaScript)
- [ ] Load testing (1000 concurrent connections)
- [ ] Documentation WebSocket protocol

## Acceptance Criteria

* ✅ WebSocket endpoint `/ws` funzionante
* ✅ Workflow events streaming real-time
* ✅ Authentication implementata
* ✅ Reconnection handling
* ✅ Load test passed (1000 connections)
* ✅ Client examples funzionanti

## Business Value

UX migliore (progress real-time), perceived performance, debugging easier

## Estimate

5 giorni

## Riferimenti

* Documento: `MigrationAnalysis/02-api-architecture-analysis.md` (sezione 13.6)

---

### 🧩 [ARCH-10] Implementare Feature Flags System
**ID:** FYL-42

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M6: Advanced Features

**Descrizione:**

# Obiettivo

Sistema di feature flags per rollout controllato di nuove funzionalità.

## Context

Feature flags permettono:

* A/B testing
* Gradual rollout
* Kill switch per bug
* Tenant-specific features

## Tasks

- [ ] Creare tabella `feature_flags`:
  - flag_name
  - enabled_globally (boolean)
  - tenant_whitelist (array)
  - rollout_percentage (0-100)
- [ ] Implementare `FeatureFlagService`
- [ ] Decorator `@feature_flag("flag_name")` per endpoint
- [ ] Config UI (admin dashboard, optional)
- [ ] API endpoints:
  - `GET /api/v1/admin/feature-flags` (list)
  - `PUT /api/v1/admin/feature-flags/{name}` (update)
- [ ] Caching flags (Redis, 30s TTL)
- [ ] Metrics flag usage (Prometheus)

## Acceptance Criteria

* ✅ Feature flags configurabili per tenant
* ✅ Rollout percentage supportato
* ✅ Decorator funzionante
* ✅ Caching implementato
* ✅ Admin API funzionante

## Business Value

Risk mitigation, gradual rollout, tenant customization

## Estimate

4 ore

---

### 🧩 [ARCH-09] Implementare Versioning API (v1, v2, etc.)
**ID:** FYL-41

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M6: Advanced Features

**Descrizione:**

# Obiettivo

Sistema di API versioning per supportare breaking changes senza impatto sui client esistenti.

## Context

API versioning è essenziale per evoluzione del prodotto senza rompere client esistenti.

## Tasks

- [ ] Implementare URL-based versioning (`/api/v1/`, `/api/v2/`)
- [ ] Routing versioning in FastAPI
- [ ] Deprecation policy (v1 supportata per 6 mesi dopo v2)
- [ ] Response header `X-API-Version: v1`
- [ ] Deprecation header `Deprecation: true` per endpoint obsoleti
- [ ] Documentation versioning (separate docs per version)
- [ ] Migration guide v1 → v2

## Acceptance Criteria

* ✅ URL-based versioning funzionante
* ✅ Multiple versions supportate simultaneamente
* ✅ Deprecation headers implementati
* ✅ Documentation per ogni version
* ✅ Migration guide disponibile

## Business Value

Backward compatibility, smooth migrations, client trust

## Estimate

3 ore

---

### 🧩 Docker Containerization & Docker Compose
**ID:** FYL-23

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M7: Infrastructure & DevOps

**Descrizione:**

# Obiettivo

Containerizzare l'applicazione per deployment consistente su qualsiasi environment.

## Context

Docker permette deployment reproducibile e semplifica setup dev/staging/prod.

## Tasks

- [ ] Creare Dockerfile multi-stage (builder + runtime)
- [ ] Ottimizzazione image size (Alpine Linux, layer caching)
- [ ] Docker Compose per local development:
  - App container (FastAPI)
  - PostgreSQL container (con pgvector)
  - Redis container (caching)
  - Prometheus container (monitoring, optional)
  - Grafana container (dashboards, optional)
- [ ] Health check endpoint (/health)
- [ ] Environment variables management (.env file)
- [ ] Volume mounts per development (hot reload)
- [ ] Docker ignore file (.dockerignore)

## Acceptance Criteria

* ✅ Dockerfile multi-stage funzionante
* ✅ Image size ottimizzata (<500MB)
* ✅ Docker Compose up → full stack running
* ✅ Hot reload in development
* ✅ Health check implementato

## Riferimenti

* Best practices Dockerfile per Python FastAPI

---

### 🧩 Setup Repository gloria-backend-cgs (Modular Integration)
**ID:** FYL-8

**Status:** Backlog  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M7: Infrastructure & DevOps

**Descrizione:**

# Obiettivo

Creare nuovo repository per integrazione modulare di CGS_2 in gloria-backend.

## Context

Dal documento `09-gloria-backend-integration-plan.md`: Approccio 3 (Modular Integration) è RACCOMANDATO. Non fork, non rewrite, ma integrazione pulita.

## Tasks

- [ ] Creare repository `gloria-backend-cgs`
- [ ] Struttura directory secondo piano:

  ```
  gloria-backend-cgs/
  ├── core/ (da gloria-backend - KEEP)
  ├── middleware/ (da gloria-backend - KEEP)  
  ├── cgs_domain/ (da CGS_2 - PORT)
  │   ├── domain/
  │   ├── application/
  │   └── infrastructure/
  └── api/ (HYBRID - merge gloria + CGS_2)
  ```
- [ ] Setup git repository con branches (main, develop, staging)
- [ ] Copiare core infrastructure da gloria-backend
- [ ] .gitignore, [README.md](http://README.md), LICENSE
- [ ] requirements.txt / pyproject.toml setup

## Acceptance Criteria

* ✅ Repository creato e accessibile al team
* ✅ Struttura directory secondo piano documento 09
* ✅ Core da gloria-backend importato
* ✅ Pronto per integrare CGS_2 components

## Riferimenti

* Documento: `MigrationAnalysis/09-gloria-backend-integration-plan.md`
* Repository base: `gloria-backend/`
* Repository sorgente: `CGS_2/`

---

### 🧩 [DOC-01] Architecture Decision Records (ADRs)
**ID:** FYL-53

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M7: Infrastructure & DevOps

**Descrizione:**

# Obiettivo

Documentare tutte le decisioni architetturali chiave tramite ADR.

## Context

ADR (Architecture Decision Records) documentano il "perché" delle scelte architetturali.

## Tasks

- [ ] Setup ADR structure (`docs/adr/`)
- [ ] Creare ADR template
- [ ] Scrivere ADR per decisioni chiave:
  - **ADR-001**: Supabase → Neon PostgreSQL migration
  - **ADR-002**: API Key + JWT dual authentication
  - **ADR-003**: Multi-provider LLM orchestration pattern
  - **ADR-004**: Cost tracking as differentiator
  - **ADR-005**: Template-based workflow engine
  - **ADR-006**: Modular integration approach (gloria + CGS_2)
  - **ADR-007**: Domain-Driven Design layers
  - **ADR-008**: Async job processing (Celery vs ARQ vs RQ)
  - **ADR-009**: Caching strategy (Redis)
  - **ADR-010**: Monitoring stack (Prometheus + Grafana)
- [ ] Review ADR con team

## Acceptance Criteria

* ✅ 10+ ADR documentati
* ✅ ADR template definito
* ✅ Team review completed
* ✅ ADR accessibili nel repo

## Estimate

4 ore

## Riferimenti

* ADR format: [https://adr.github.io/](https://adr.github.io/)

---

### 🧩 Developer Documentation & Runbook
**ID:** FYL-26

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M7: Infrastructure & DevOps

**Descrizione:**

# Obiettivo

Creare documentazione completa per sviluppatori e operations.

## Context

Documentation è essenziale per onboarding team e troubleshooting production.

## Tasks

- [ ] [README.md](http://README.md) completo:
  - Project overview
  - Architecture diagram
  - Tech stack
  - Setup instructions (local dev)
  - Docker Compose setup
  - Environment variables
- [ ] [CONTRIBUTING.md](http://CONTRIBUTING.md) (contribution guidelines)
- [ ] Architecture documentation:
  - Domain-Driven Design layers
  - Database schema (ERD diagram)
  - API architecture
  - Workflow engine design
  - Cost tracking system
- [ ] Runbook per operations:
  - Deployment procedure
  - Rollback procedure
  - Database backup/restore
  - Monitoring dashboards
  - Troubleshooting common issues
  - Scaling procedures (read replicas, etc.)
- [ ] Code comments per logica complessa

## Acceptance Criteria

* ✅ [README.md](http://README.md) completo
* ✅ Architecture docs disponibili
* ✅ Runbook per operations team
* ✅ Onboarding < 1 day (new developer)
* ✅ Troubleshooting guide disponibile

## Riferimenti

* Documentation best practices

---

### 🧩 Setup Structured Logging (JSON logs)
**ID:** FYL-19

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M7: Infrastructure & DevOps

**Descrizione:**

# Obiettivo

Implementare structured logging per production-ready log management.

## Context

Logging strutturato permette parsing automatico, alerting, e analisi trend.

## Tasks

- [ ] Setup structlog (structured logging library)
- [ ] Log format JSON con campi standard:
  - timestamp
  - level (INFO, WARNING, ERROR)
  - logger_name
  - message
  - context (request_id, user_id, client_id)
  - metadata (workflow_id, agent_name, provider)
- [ ] Request ID injection (per request tracing)
- [ ] Log aggregation:
  - CloudWatch Logs (AWS)
  - oppure Elasticsearch + Kibana
  - oppure Loki + Grafana
- [ ] Log levels per environment (DEBUG dev, INFO prod)
- [ ] Sensitive data masking (API keys, tokens)
- [ ] Log rotation policy

## Acceptance Criteria

* ✅ Tutti i log in formato JSON
* ✅ Request ID tracing implementato
* ✅ Log aggregation funzionante
* ✅ Sensitive data mascherato
* ✅ Log searchable (full-text search)

## Riferimenti

* Documento: `MigrationAnalysis/04-current-strengths-detailed.md` (enhance logging)

---

### 🧩 Project Cleanup & Dependency Management
**ID:** FYL-9

**Status:** Backlog  |  **Priorità:** Medium  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M7: Infrastructure & DevOps

**Descrizione:**

# Obiettivo

Pulire dipendenze, rimuovere dead code, setup dependency management pulito.

## Context

Week 1-2 foundation: prima di integrare CGS_2, cleanare il progetto base gloria-backend.

## Tasks

- [ ] Audit dipendenze Python (requirements.txt)
- [ ] Rimuovere dipendenze unused
- [ ] Update librerie obsolete (security patches)
- [ ] Setup Poetry o uv per dependency management moderno
- [ ] Rimuovere dead code da gloria-backend
- [ ] Setup pre-commit hooks (black, flake8, mypy)
- [ ] .env.example file con tutte le variabili necessarie

## Acceptance Criteria

* ✅ requirements.txt ottimizzato (no unused deps)
* ✅ Security vulnerabilities risolte (pip audit)
* ✅ Dependency management moderno (Poetry/uv)
* ✅ Pre-commit hooks funzionanti
* ✅ Code formatting consistente

## Riferimenti

* Documento: `MigrationAnalysis/09-gloria-backend-integration-plan.md` (Week 1-2)

---

### 🧩 [DOC-05] Documentare Pattern: Service Layer e PostgreSQL Function Invocation
**ID:** FYL-73

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** nan

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Documentare i pattern aggiuntivi del service layer e invocazione PostgreSQL functions prima della pulizia del codice legacy.

## Pattern Identificati

**File chiave**:

* `app/services/base_service.py` - BaseService class
* `app/services/istres.py` - Esempio completo
* `app/api/routes/istres.py` - API layer

### 1\. BaseService Pattern

```python
class BaseService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def _set_user_context(self, conn, context: TenantContext):
        await conn.execute(f"SET myapp.userid = '{context.user_id}'")
        await conn.execute(f"SET myapp.profile = '{context.profile}'")
```

### 2\. PostgreSQL Function Invocation Pattern

```python
function_name = "resource_get"
query = f"SELECT * FROM {context.organization}.{function_name}($1, $2, $3)"
rows = await connection.fetch(query, param1, param2, param3)

# Handle JSON response from function
record = rows[0].get(function_name)
data = json.loads(record) if isinstance(record, str) else record
return Model(**data)
```

### 3\. CRUD Operations Pattern

```python
# CREATE
async def create_resource(context, data: ResourceCreate) → Resource:
    function_name = "resource_ins"
    context_param = {"user_id": context.user_id, ...}
    query = f"SELECT * FROM {context.organization}.{function_name}($1::jsonb, $2, $3)"
    ...

# READ
async def get_resource(context, id: int) → Resource:
    function_name = "resource_get"
    ...

# UPDATE
async def update_resource(context, id: int, data: ResourceUpdate) → Resource:
    function_name = "resource_upd"
    ...

# DELETE
async def delete_resource(context, id: int) → bool:
    function_name = "resource_del"
    ...
```

### 4\. Bulk Operations Pattern

```python
async def bulk_create(context, bulk_data: BulkCreate) → BulkResponse:
    async with self.db_manager.get_connection_context(context.organization) as conn:
        await self._set_user_context(conn, context)
        
        for item in bulk_data.items:
            try:
                # Call function for each item
                ...
                successful_count += 1
            except Exception as e:
                failed_count += 1
                errors.append(...)
        
        return BulkOperationResponse(
            created_count=successful_count,
            failed_count=failed_count,
            errors=errors
        )
```

### 5\. API Endpoint Decorators

```python
@router.get("/")
@with_tenant_context          # Inject context
@require_role(["admin", "member"])  # RBAC
async def get_list(request: Request):
    context = request.state.tenant_context
    ...
```

### 6\. Envelope Response Pattern

```python
return create_success_response(
    request=request,
    data=result.model_dump(mode='json'),
    message="Retrieved successfully"
)

return create_error_response(
    request=request,
    message="Error occurred",
    errors=[str(e)],
    status_code=500
)
```

## Documentazione da Creare

- [ ] ADR: Service Layer Architecture
- [ ] Pattern Guide: PostgreSQL Function Invocation
- [ ] Pattern Guide: CRUD Operations Template
- [ ] Pattern Guide: Bulk Operations
- [ ] Code Template: New Service Boilerplate
- [ ] Code Template: New API Endpoint Boilerplate
- [ ] Error Handling Guide

## Acceptance Criteria

* ✅ Documentazione ADR creata
* ✅ Service template con examples
* ✅ CRUD boilerplate code
* ✅ Bulk operations template
* ✅ Endpoint template con decorators
* ✅ Error handling best practices

## Priority

🔴 **BLOCKING** per FYL-28, 29, 30 (cleanup)

---

### 🧩 [DOC-04] Documentare Pattern: Cache Integrata a Livello Endpoint (Redis + Decorator)
**ID:** FYL-72

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** nan

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Documentare il pattern di cache integrata a livello endpoint con decorator `@with_cache` prima della pulizia del codice legacy.

## Pattern Identificato

**File chiave**:

* `app/utils/cache_decorators/cache.py` - @with_cache decorator
* `app/core/cache_config.py` - Configurazione cache per endpoint
* `app/utils/cache/manager.py` - CacheManager

**Componenti**:

### 1\. Cache Decorator Pattern

```python
@with_cache(
    endpoint="counterparts:list",
    ttl=600,                    # Optional override
    stale_ttl=120,              # Optional override
    background_refresh=True,    # Optional override
    vary_by_role=False          # Optional override
)
async def get_counterparts(context: TenantContext) → Response:
    return await service.fetch_from_db(context)
```

### 2\. Configurazione Centralizzata

```python
# app/core/cache_config.py
def get_cache_config(service: str, action: str) → dict:
    return {
        "ttl": 600,
        "stale_ttl": 120,
        "background_refresh": True,
        "vary_by_role": False,
        "stampede_protect": True,
        "compress": True,
        "jitter_pct": 0.1,
        "include_query_params": True
    }
```

### 3\. Cache Key Structure

```
Format: {env}:{org}:{endpoint}:{variant}:{params_hash}:{role}
Example: prod:acme:counterparts:list:abc123:admin
```

### 4\. Advanced Features

* **Stale-While-Revalidate**: Serve stale + background refresh
* **Stampede Protection**: Lock durante fetch
* **Compression**: zlib per payload grandi
* **Jitter**: TTL randomization per evitare thundering herd
* **Query Params**: Automatic hashing

### 5\. Cache Manager Pattern

```python
result = await cache_manager.get_or_set(
    key=cache_key,
    fetch=async_function,
    ttl=600,
    stale_ttl=120,
    background_refresh=True
)
```

## Usage Pattern

```python
# Semplice (configurazione da cache_config.py)
@with_cache("currencies:list")
async def get_currencies(context: TenantContext):
    ...

# Con override
@with_cache("market:data", ttl=60, vary_by_role=True)
async def get_market_data(context: TenantContext):
    ...
```

## Documentazione da Creare

- [ ] ADR: Caching Strategy (Redis)
- [ ] Pattern Guide: @with_cache decorator usage
- [ ] Cache Configuration Guide
- [ ] Cache Key Design Guidelines
- [ ] Performance Guide: TTL tuning strategies
- [ ] Monitoring Guide: Cache hit rates

## Acceptance Criteria

* ✅ Documentazione ADR creata
* ✅ Decorator usage guide
* ✅ Configuration template
* ✅ Performance recommendations
* ✅ Monitoring dashboard design

## Priority

🔴 **BLOCKING** per FYL-28, 29, 30 (cleanup)

---

### 🧩 [REPO-03] Inizializzare Git e Push a Nuovo Repository
**ID:** FYL-66

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Inizializzare git locale e fare push al nuovo repository GitHub.

## Context

Dopo rimozione git esistente e creazione nuovo repository GitHub, collegare locale a nuovo remote.

## Tasks

- [ ] Inizializzare nuovo git repository:
  git init
- [ ] Configurare user git (se necessario):

  ```bash
  git config user.name "Fulvio Vanacore"
  git config user.email "fulvio@fylle.ai"
  ```
- [ ] Verificare .gitignore:
  - Review file inclusi/esclusi
  - Verificare che file sensibili siano ignorati
- [ ] Stage tutti i file:

  ```bash
  git add .
  ```
- [ ] Verificare file staged:

  ```bash
  git status
  ```
- [ ] Creare primo commit:

  ```bash
  git commit -m "Initial commit: gloria-backend migration to Fylle
  
  - Migrated from origoventures/gloria-backend
  - Clean codebase ready for fylle-core-pulse project
  - Removed legacy git history
  
  🤖 Prepared for Fylle AI Application Server transformation"
  ```
- [ ] Aggiungere remote repository:

  ```bash
  git remote add origin [URL_NUOVO_REPOSITORY]
  ```
- [ ] Verificare remote:

  ```bash
  git remote -v
  ```
- [ ] Rinominare branch in main (se necessario):

  ```bash
  git branch -M main
  ```
- [ ] Push al nuovo repository:

  ```bash
  git push -u origin main
  ```
- [ ] Verificare push su GitHub web interface

## Acceptance Criteria

* ✅ Git inizializzato in locale
* ✅ Primo commit creato con messaggio descrittivo
* ✅ Remote collegato al nuovo repository
* ✅ Push completato con successo
* ✅ Codice visibile su GitHub
* ✅ Branch `main` è default branch

## Estimate

30 minuti

## Note

⚠️ Verificare che `.env`, `key.pem`, `cert.pem` NON siano committati (devono essere in .gitignore)

## Dipendenze

Dipende da: FYL-64 (rimozione git), FYL-65 (creazione repo GitHub)

---

### 🧩 [DOC-03] Documentare Pattern: Paginazione Standard con PostgreSQL Functions
**ID:** FYL-71

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** nan

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Documentare il pattern di paginazione standard utilizzato con PostgreSQL functions prima della pulizia del codice legacy.

## Pattern Identificato

**File chiave**:

* `app/services/istres.py` - get_istres() con paginazione
* `app/models/istres.py` - IstreListResponse, IstreGetListParams

**Componenti**:

### 1\. PostgreSQL Function Pattern

```sql
CREATE FUNCTION istre_getlist(
    p_page_number INT,
    p_page_size INT,
    p_total_items INT,  -- NULL on first call
    p_order_by TEXT,
    p_order_direction TEXT,
    p_filters JSONB
) RETURNS JSONB
```

### 2\. Response Structure (Standard)

```json
{
  "total_items": 150,
  "total_pages": 8,
  "page_number": 1,
  "page_size": 20,
  "data": [... items array ...],
  "has_next": true
}
```

### 3\. Service Layer Pattern

```python
async def get_items(
    context: TenantContext,
    page_number: int = 1,
    page_size: int = 20,
    total_items: Optional[int] = None,  # Optimization
    order_by: str = 'id',
    order_direction: str = 'asc',
    filters: Optional[str] = None
) → ListResponse
```

### 4\. Filters as JSONB

```python
filters_dict = filters.model_dump(exclude_none=True, by_alias=True)
query_params = json.dumps(filters_dict)
```

### 5\. API Endpoint Pattern

```python
@router.get("/")
@with_tenant_context
async def get_list(
    request: Request,
    page_number: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_by: str = Query('id'),
    order_direction: str = Query('asc'),
    filters: Optional[str] = Query(None)
)
```

## Optimization: total_items caching

* First call: `total_items=None` (DB counts)
* Subsequent calls: pass `total_items` from previous response
* Avoid expensive COUNT(\*) on each page

## Documentazione da Creare

- [ ] ADR: Pagination Strategy
- [ ] Pattern Guide: PostgreSQL Function-based Pagination
- [ ] Code Examples: Implementare nuova risorsa paginata
- [ ] SQL Template: Function boilerplate
- [ ] Performance Guide: Pagination best practices

## Acceptance Criteria

* ✅ Documentazione ADR creata
* ✅ SQL function template
* ✅ Service layer template
* ✅ Endpoint template
* ✅ Performance guidelines

## Priority

🔴 **BLOCKING** per FYL-28, 29, 30 (cleanup)

---

### 🧩 [DOC-02] Documentare Pattern: Connection Pooling Centralizzato (asyncpg)
**ID:** FYL-70

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** nan

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Documentare il pattern di connection pooling centralizzato con asyncpg prima della pulizia del codice legacy.

## Pattern Identificato

**File chiave**:

* `app/core/database.py` - DatabaseManager

**Componenti**:

### 1\. DatabaseManager Singleton

```python
class DatabaseManager:
    _connection_pool: Optional[asyncpg.Pool] = None
    
    async def initialize():
        self._connection_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=10,
            max_size=50,
            max_queries=100000,
            max_inactive_connection_lifetime=600.0,
            command_timeout=30
        )
```

### 2\. Context Manager Pattern

```python
@asynccontextmanager
async def get_connection_context(schema_name: Optional[str] = None):
    conn = await self.get_connection(schema_name)
    try:
        yield conn
    finally:
        await self.release_connection(conn)
```

### 3\. Helper Methods

```python
- fetch_one(query, *args, schema_name) → Dict
- fetch_all(query, *args, schema_name) → List[Dict]
- execute_command(query, *args, schema_name) → str
- execute_query(query, *args, schema_name) → Any
```

### 4\. Pool Monitoring

```python
def get_pool_status() → dict:
    return {
        "status": "active",
        "size": pool.get_size(),
        "free": pool.get_idle_size(),
        "max_size": pool.get_max_size()
    }
```

## Usage Pattern nei Servizi

```python
async with self.db_manager.get_connection_context(context.organization) as conn:
    await self._set_user_context(conn, context)
    result = await conn.fetch(query, *params)
```

## Documentazione da Creare

- [ ] ADR: Database Connection Pooling Strategy
- [ ] Pattern Guide: Connection Management Best Practices
- [ ] Code Examples: Come usare DatabaseManager
- [ ] Performance Guide: Pool sizing e tuning
- [ ] Migration Guide: Adattare pattern per nuovi database

## Acceptance Criteria

* ✅ Documentazione ADR creata
* ✅ Pattern guide con esempi
* ✅ Performance recommendations
* ✅ Pool monitoring dashboard design

## Priority

🔴 **BLOCKING** per FYL-28, 29, 30 (cleanup)

---

### 🧩 [REPO-02] Creare Nuovo Repository GitHub (gloria-backend-v2)
**ID:** FYL-65

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Creare nuovo repository GitHub per gloria-backend su account GitHub diverso.

## Context

Necessario nuovo repository per separare da origoventures e gestire su nuovo account Fylle.

## Tasks

- [ ] Decidere nome repository:
  * Opzione 1: `gloria-backend-v2`
  * Opzione 2: `fylle-application-server`
  * Opzione 3: `fylle-core-backend`
- [ ] Creare repository su GitHub:
  * Account: \[specificare account Fylle\]
  * Visibility: Private (raccomandato per ora)
  * Initialize: NO (repository locale già esiste)
  * NO README, NO .gitignore, NO license (già presenti in locale)
- [ ] Copiare URL del nuovo repository:
  * HTTPS: `https://github.com/[account]/[repo-name].git`
  * SSH: `git@github.com:[account]/[repo-name].git`
- [ ] Configurare GitHub repository settings:
  * Branch protection su `main` (require PR reviews)
  * Enable Issues
  * Enable Discussions (optional)

## Acceptance Criteria

* ✅ Nuovo repository GitHub creato
* ✅ Repository è private
* ✅ URL repository disponibile
* ✅ Branch protection configurata

## Estimate

15 minuti

## Riferimenti

* Account GitHub: \[da specificare\]
* Repository name: \[da decidere\]

## Dipendenze

Dipende da: FYL-64 (rimozione git esistente)

---

### 🧩 [DOC-01] Documentare Pattern: Gestione Contesto Sicurezza PostgreSQL (RLS + Tenant Isolation)
**ID:** FYL-69

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Documentare il pattern di gestione del contesto di sicurezza PostgreSQL con Row-Level Security (RLS) e tenant isolation prima della pulizia del codice legacy.

## Pattern Identificato

**File chiave**:

* `app/core/tenant.py` - TenantResolver
* `app/core/database.py` - DatabaseManager con schema context
* `app/services/base_service.py` - \_set_user_context()

**Componenti**:

### 1\. Tenant Resolution

```python
class TenantResolver:
    - resolve_tenant_schema(org_slug) → schema_name
    - Cache TTL: 5 minuti
    - Fallback: DB → YAML (tenants.yaml)
    - get_tenant_info() per metadata completi
```

### 2\. Schema Isolation

```python
# PostgreSQL search_path per tenant
await conn.execute(f"SET search_path TO {schema_name}, public")
```

### 3\. RLS Context Setting

```python
async def _set_user_context(conn, context: TenantContext):
    await conn.execute(f"SET myapp.userid = '{context.user_id}'")
    await conn.execute(f"SET myapp.profile = '{context.profile}'")
```

### 4\. TenantContext Dataclass

```python
@dataclass
class TenantContext:
    user_id: str
    org_slug: str
    organization: str  # schema_name
    profile: str  # role
    user_role: Optional[str]
```

## Documentazione da Creare

- [ ] ADR: Multi-tenant Architecture with PostgreSQL RLS
- [ ] Pattern Guide: Tenant Context Management
- [ ] Code Examples: Come usare TenantContext nei servizi
- [ ] Security Guide: RLS Best Practices
- [ ] Migration Guide: Come adattare questo pattern per nuove feature

## Acceptance Criteria

* ✅ Documentazione ADR creata
* ✅ Pattern guide con esempi di codice
* ✅ Diagrammi architetturali (tenant resolution flow)
* ✅ Best practices e anti-patterns

## Priority

🔴 **BLOCKING** per FYL-28, 29, 30 (cleanup)

---

### 🧩 [REPO-01] Rimuovere Git Esistente da gloria-backend
**ID:** FYL-64

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Rimuovere il repository git esistente da gloria-backend per preparare una codebase pulita.

## Context

Repository attualmente collegato a: `https://github.com/origoventures/gloria-backend.git`
Necessario scollegare e pulire per creare nuovo repository su GitHub diverso.

## Tasks

- [ ] Verificare stato git attuale (`git status`)
- [ ] Backup del repository esistente (opzionale)
- [ ] Rimuovere directory `.git`:
  rm -rf .git
- [ ] Verificare rimozione completa (`ls -la | grep .git`)
- [ ] Verificare che .gitignore sia ancora presente
- [ ] Verificare che file sensibili siano in .gitignore:
  * `.env`
  * `key.pem`
  * `cert.pem`
  * `venv/`
  * `.venv/`
  * `__pycache__/`

## Acceptance Criteria

* ✅ Directory `.git` rimossa completamente
* ✅ Codebase locale pulita (no git history)
* ✅ `.gitignore` preservato
* ✅ File sensibili protetti in .gitignore

## Estimate

30 minuti

## Note

⚠️ Questa operazione rimuove TUTTA la git history locale. Assicurarsi di avere backup se necessario.

---

### 🧩 [CLEANUP-04] Database Migration - Drop Financial Tables
**ID:** FYL-32

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Creare migration per drop di TUTTE le tabelle financial-specific dal database.

## Tabelle da Eliminare (stima 30+ tabelle)

### Cashflow Domain

* ❌ `cashflows`
* ❌ `cashflow_versions`
* ❌ `cashflow_scenarios`

### Counterparts

* ❌ `counterparts`

### Currencies

* ❌ `currencies`
* ❌ `currency_rates`
* ❌ `currency_forecasts`

### Currency Panel

* ❌ `currency_panel_data`
* ❌ `currency_panel_scenarios`

### Current Accounts

* ❌ `current_accounts`
* ❌ `account_balances`

### Dashboard

* ❌ `dashboard_data`
* ❌ `dashboard_kpis`

### Hedges

* ❌ `hedges`
* ❌ `hedge_positions`

### Invoices

* ❌ `invoices`
* ❌ `invoice_items`

### Istres

* ❌ `istres_data`

### Jobs

* ❌ `background_jobs`
* ❌ `job_results`

### Market Data

* ❌ `market_data`
* ❌ `forward_curves`

### Probabilities

* ❌ `probabilities`

### Reconciliations

* ❌ `reconciliations`
* ❌ `reconciliation_items`

### Simulations

* ❌ `simulations`
* ❌ `simulation_results`

### Activity Center

* ❌ `activities`

## Tabelle da MANTENERE

✅ `organizations` (multi-tenancy)
✅ `users` (gestione utenti)
✅ `api_keys` (autenticazione, da creare)
✅ `audit_logs` (se esiste)

## Tasks

- [ ] Audit completo database (lista tutte le tabelle)
- [ ] Identificare dipendenze foreign key
- [ ] Creare migration DROP TABLES (ordine corretto per FK)
- [ ] Backup database pre-migration
- [ ] Eseguire migration su dev/staging
- [ ] Verificare integrità database post-migration

## Acceptance Criteria

* ✅ Migration SQL completa (DROP TABLE statements)
* ✅ Backup database completo pre-migration
* ✅ Migration testata su staging
* ✅ Zero tabelle financial rimaste
* ✅ Tabelle core intatte (organizations, users)

## Estimate

3 ore

## Dipendenze

Dipende da: FYL-29, FYL-30, FYL-31 (eliminare tutto il codice prima)

---

### 🧩 [CLEANUP-03] Eliminare API Routes Financial (20+ routes)
**ID:** FYL-31

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Eliminare TUTTE le route API financial-specific da gloria-backend.

## Routes da Eliminare

 1. ❌ `cashflows.py` + `cashflows_legacy.py` + `cashflows_backup.py`
 2. ❌ `counterparts.py`
 3. ❌ `currencies.py`
 4. ❌ `currency_panel.py`
 5. ❌ `current_accounts.py`
 6. ❌ `dashboard.py`
 7. ❌ `hedges.py`
 8. ❌ `invoices.py`
 9. ❌ `istres.py`
10. ❌ `jobs.py` (background jobs financial)
11. ❌ `market_data.py`
12. ❌ `probabilities.py`
13. ❌ `projections.py`
14. ❌ `reconciliations.py`
15. ❌ `rfq.py` (Request for Quote)
16. ❌ `simulations.py`
17. ❌ `activity_center.py`
18. ❌ `envelope_demo.py`

## Mantenere

✅ `auth.py` (da riscrivere ma framework OK)
✅ `users.py` (gestione utenti base)
✅ `organizations.py` (multi-tenancy)
✅ `types.py` (configuration)
✅ `admin_cache.py` (utility admin)

## Aggiornare [main.py](http://main.py)

Eliminare tutti i router includes da `main.py` (linee 234-299 circa)

## Acceptance Criteria

* ✅ 18+ route files eliminati da `app/api/routes/`
* ✅ `main.py` aggiornato (router includes removed)
* ✅ API documentation aggiornata
* ✅ Nessun import rotto

## Estimate

2 ore

## Dipendenze

Dipende da: FYL-29, FYL-30 (eliminare services e models prima)

---

### 🧩 [CLEANUP-02] Eliminare Models Financial (17 moduli)
**ID:** FYL-30

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Eliminare TUTTI i 17 models financial-specific da gloria-backend.

## Models da Eliminare

 1. ❌ `cashflows.py` (modelli cashflow)
 2. ❌ `counterparts.py` (modelli controparti)
 3. ❌ `currencies.py` (modelli valute)
 4. ❌ `currency_panel.py` (modelli pannello valute)
 5. ❌ `current_accounts.py` (modelli conti correnti)
 6. ❌ `dashboard.py` (modelli dashboard)
 7. ❌ `hedges.py` (modelli hedges)
 8. ❌ `invoices.py` (modelli fatture)
 9. ❌ `istres.py` (modelli istres)
10. ❌ `jobs.py` (modelli background jobs)
11. ❌ `market_data.py` (modelli dati mercato)
12. ❌ `probabilities.py` (modelli probabilità)
13. ❌ `reconciliations.py` (modelli riconciliazioni)
14. ❌ `simulation.py` (modelli simulazione)
15. ❌ `accounts.py` (modelli account financial)

## Mantenere

✅ `organizations.py` (multi-tenancy base)
✅ `types.py` (configuration types)
✅ `database.py` (database configuration)

## Acceptance Criteria

* ✅ 15+ file eliminati da `app/models/`
* ✅ Nessun import rotto
* ✅ Database migration per drop tabelle

## Estimate

2 ore

## Dipendenze

Dipende da: FYL-29 (eliminare services prima)

---

### 🧩 [CLEANUP-01] Eliminare Services Financial (16 moduli)
**ID:** FYL-29

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Eliminare TUTTI i 16 services financial-specific da gloria-backend.

## Services da Eliminare

 1. ❌ `cashflows.py` (24KB - gestione cashflows)
 2. ❌ `counterparts.py` (gestione controparti)
 3. ❌ `currencies.py` + `currency_service.py` (gestione valute)
 4. ❌ `currency_panel.py` + `currency_panel_service.py` (pannello valute)
 5. ❌ `current_accounts.py` (conti correnti)
 6. ❌ `dashboard.py` (dashboard financial)
 7. ❌ `hedges.py` (24KB - hedges financial)
 8. ❌ `invoices.py` (20KB - fatture)
 9. ❌ `istres.py` (22KB - istres)
10. ❌ `jobs.py` (background jobs financial)
11. ❌ `market_data.py` (dati mercato)
12. ❌ `probabilities.py` (probabilità financial)
13. ❌ `projection_service.py` + `simulation_service.py` + `simulation.py` (proiezioni/simulazioni)
14. ❌ `reconciliations.py` (riconciliazioni)
15. ❌ `activity_center.py` (17KB - activity center)
16. ❌ `clerk_service.py` (auth [Clerk.com](http://Clerk.com) - DA SOSTITUIRE)

## Mantenere

✅ `organizations.py` (multi-tenancy base)
✅ `types.py` (configuration types)
✅ `base_service.py` (service base class)

## Acceptance Criteria

* ✅ 16 file eliminati da `app/services/`
* ✅ Nessun import rotto (verificare con mypy)

## Estimate

3 ore

---

### 🧩 [CLEANUP] Eliminare tutti i moduli Financial di gloria-backend
**ID:** FYL-28

**Status:** Done  |  **Priorità:** Urgent  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Eliminare TUTTI i moduli applicativi financial-specific da gloria-backend per prepararlo all'integrazione CGS_2.

## Context

gloria-backend è attualmente un'applicazione per Financial Risk Management. Dobbiamo eliminare TUTTA la logica applicativa financial e mantenere SOLO l'infrastructure core riutilizzabile.

## Moduli da ELIMINARE (16+ moduli)

### Services (app/services/)

- [ ] `cashflows.py` (24KB - gestione cashflows financial)
- [ ] `counterparts.py` (gestione controparti financial)
- [ ] `currencies.py` + `currency_service.py` (gestione valute)
- [ ] `currency_panel.py` + `currency_panel_service.py` (pannello valute)
- [ ] `current_accounts.py` (conti correnti financial)
- [ ] `dashboard.py` (dashboard financial-specific)
- [ ] `hedges.py` (24KB - gestione hedges financial)
- [ ] `invoices.py` (20KB - gestione fatture)
- [ ] `istres.py` (22KB - istres financial)
- [ ] `jobs.py` (background jobs financial-specific)
- [ ] `market_data.py` (dati di mercato financial)
- [ ] `probabilities.py` (probabilità financial)
- [ ] `projection_service.py` + `simulation_service.py` + `simulation.py` (proiezioni/simulazioni financial)
- [ ] `reconciliations.py` (riconciliazioni financial)
- [ ] `activity_center.py` (17KB - activity center financial)
- [ ] `clerk_service.py` (auth Clerk.com da sostituire)

### Models (app/models/)

- [ ] Eliminare tutti i model corrispondenti ai services sopra (18 files)

### API Routes (app/api/routes/)

- [ ] Eliminare tutti i router corrispondenti (cashflows, counterparts, currencies, etc.)

### Database Tables

- [ ] Identificare tabelle PostgreSQL da eliminare (financial-specific)
- [ ] Drop migration per tabelle obsolete

## Moduli da MANTENERE

✅ `organizations.py` (multi-tenancy base)
✅ `types.py` (configuration types)
✅ `auth_service.py` (DA RISCRIVERE ma framework base OK)
✅ `base_service.py` (service base class)
✅ Core infrastructure (app/core/, app/middleware/, app/utils/)

## Acceptance Criteria

* ✅ Tutti i 16+ moduli financial eliminati
* ✅ [Main.py](http://Main.py) aggiornato (eliminati 16+ router includes)
* ✅ requirements.txt pulito (dipendenze financial removed)
* ✅ Test suite aggiornata (removed financial tests)
* ✅ Nessun import rotto (verificare con mypy/flake8)

## Effort

8 ore (eliminazione sistematica + verifica integrità)

## Riferimenti

* `gloria-backend/main.py` linee 234-299 (router includes)
* Documento: `MigrationAnalysis/09-gloria-backend-integration-plan.md`

---

### 🧩 [CLEANUP-01] Rimozione Directory Legacy e Aggiornamento .gitignore
**ID:** FYL-67

**Status:** Done  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Pulire il repository da directory legacy non necessarie e aggiornare .gitignore per escludere assets.

## Tasks

- [ ] Aggiungere `attached_assets/` a .gitignore
- [ ] Rimuovere directory `public/mocks/*` (mock data non necessari)
- [ ] Rimuovere directory `local_export/neondb_correct/` (export database legacy)
- [ ] Rimuovere directory `tests/*` (test specifici per gloria-backend)
- [ ] Commit delle modifiche
- [ ] Push su GitHub

## Context

Queste directory contengono:

* **public/mocks/**: Mock data specifici per gloria-backend (cashflows, invoices, hedges, etc.)
* **local_export/neondb_correct/**: Export SQL del vecchio database Neon
* **tests/**: Test suite specifici per funzionalità financial (accounts, cashflows, istres, etc.)
* **attached_assets/**: Directory per assets da ignorare in git

## Acceptance Criteria

* ✅ `attached_assets/` aggiunto a .gitignore
* ✅ Directory `public/mocks/` rimossa
* ✅ Directory `local_export/neondb_correct/` rimossa
* ✅ Directory `tests/` rimossa
* ✅ Modifiche committate e pushate

## Estimate

30 minuti

## Labels

CLEANUP, Technical Debt

---

### 🧩 [BRANDING-01] Aggiornare Health Check e Branding da Gloria a Fylle Core Pulse
**ID:** FYL-68

**Status:** Done  |  **Priorità:** High  |  **Assegnato a:** fulvio@fylle.ai

**Milestone:** M1: Foundation & Cleanup

**Descrizione:**

# Obiettivo

Aggiornare il branding dell'applicazione da "Gloria Financial Risk Management API" a "Fylle Core Pulse - Application Server" in tutti gli endpoint e metadata.

## Tasks

- [ ] Aggiornare FastAPI title in `main.py`
- [ ] Aggiornare FastAPI description
- [ ] Modificare endpoint `/health` con nuovi valori:
  - `service`: "Fylle Core Pulse - Application Server"
  - `version`: "1.0.0"
  - Aggiungere campo `haiku`: "Treno nel buio\\nLa terra aperta attende –\\nAlba improvvisa"
- [ ] Modificare endpoint `/` (root) con stessi valori
- [ ] Testare endpoint dopo modifiche
- [ ] Commit e push

## Valori Attuali

```json
{
  "status": "healthy",
  "service": "Gloria Financial Risk Management API",
  "version": "1.0.1"
}
```

## Valori Target

```json
{
  "status": "healthy",
  "service": "Fylle Core Pulse - Application Server",
  "haiku": "Treno nel buio\nLa terra aperta attende –\nAlba improvvisa",
  "version": "1.0.0"
}
```

## Acceptance Criteria

* ✅ Health check endpoint ritorna nuovi valori
* ✅ Root endpoint aggiornato
* ✅ FastAPI metadata aggiornato
* ✅ Haiku incluso nella risposta
* ✅ Version downgrade a 1.0.0 (fresh start)

## Estimate

20 minuti

---

## 🚀 Fasi di Progetto
1. **Analisi e Audit (Fase 1)** – Valutazione funzionalità legacy e definizione roadmap di migrazione.
2. **Architettura Core (Fase 2)** – Implementazione Multi-tenancy, Authentication Layer e migrazione database.
3. **Sicurezza e Access Control (Fase 3)** – JWT + API Key, RBAC e audit logging.
4. **Ottimizzazione e Refactor (Fase 4)** – Migrazione completa, test di performance, cleanup dei moduli deprecati.
5. **Testing e Rilascio (Fase 5)** – QA, CI/CD pipeline, documentazione e go-live.

_Documento generato automaticamente da Linear export (ottobre 2025)._