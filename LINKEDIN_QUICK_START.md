# 🔵 LinkedIn Integration - Quick Start Guide

**Version**: 1.0  
**Date**: 2025-10-25  
**Estimated Time**: 2-3 hours

---

## 📋 OVERVIEW

Questa guida ti aiuterà a configurare rapidamente l'integrazione LinkedIn per pubblicare contenuti direttamente sui profili LinkedIn dei tuoi clienti.

### Cosa Costruiremo

- ✅ OAuth 2.0 flow per connettere account LinkedIn
- ✅ Pubblicazione di post text e image
- ✅ Tracking delle pubblicazioni
- ✅ UI components per connessione e pubblicazione

### Prerequisites

- LinkedIn Developer Account
- PostgreSQL database
- Python 3.10+ (backend)
- Node.js 18+ (frontend)
- Supabase account (optional, per encryption)

---

## 🚀 PHASE 1: Setup LinkedIn Developer App

### Step 1.1: Create LinkedIn App

1. Vai su [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Click **"Create app"**
3. Compila il form:
   - **App name**: `CGS LinkedIn Integration`
   - **LinkedIn Page**: Seleziona la tua company page
   - **App logo**: Upload logo (almeno 100x100px)
   - **Legal agreement**: Accetta i termini

4. Click **"Create app"**

### Step 1.2: Configure OAuth Settings

1. Nella dashboard dell'app, vai su **"Auth"** tab
2. In **"OAuth 2.0 settings"**:
   - **Redirect URLs**: Aggiungi:
     ```
     http://localhost:3000/api/auth/linkedin/callback  (development)
     https://yourdomain.com/api/auth/linkedin/callback  (production)
     ```
3. Click **"Update"**

### Step 1.3: Request API Access

1. Vai su **"Products"** tab
2. Request access a:
   - ✅ **"Share on LinkedIn"** (self-service, instant approval)
   - ✅ **"Sign In with LinkedIn using OpenID Connect"** (self-service)

3. Attendi l'approvazione (di solito istantanea per questi prodotti)

### Step 1.4: Get Credentials

1. Vai su **"Auth"** tab
2. Copia:
   - **Client ID**
   - **Client Secret** (click "Show" per visualizzare)

3. Salva in un posto sicuro (userai questi nel `.env`)

---

## 🔧 PHASE 2: Backend Setup

### Step 2.1: Environment Variables

Crea/aggiorna il file `.env`:

```bash
# LinkedIn OAuth
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:3000/api/auth/linkedin/callback

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cgs_db

# Encryption (per tokens)
ENCRYPTION_KEY=your_32_byte_encryption_key_here
```

**⚠️ IMPORTANTE**: NON committare il `.env` su Git!

### Step 2.2: Database Migration

Esegui la migration per creare le tabelle:

```bash
# Copia il contenuto di DATABASE_SCHEMA_LINKEDIN_INTEGRATION.sql
psql -U your_user -d cgs_db -f DATABASE_SCHEMA_LINKEDIN_INTEGRATION.sql
```

Oppure con Alembic:

```bash
# Crea migration
alembic revision --autogenerate -m "Add LinkedIn integration tables"

# Esegui migration
alembic upgrade head
```

Verifica che le tabelle siano state create:

```sql
\dt linkedin_*

-- Output atteso:
-- linkedin_credentials
-- linkedin_publications
-- linkedin_publication_events
-- linkedin_publication_performance
```

### Step 2.3: Install Dependencies

```bash
# Backend dependencies
pip install httpx pydantic cryptography python-jose

# O aggiungi a requirements.txt:
echo "httpx>=0.25.0" >> requirements.txt
echo "pydantic>=2.0.0" >> requirements.txt
echo "cryptography>=41.0.0" >> requirements.txt
echo "python-jose>=3.3.0" >> requirements.txt

pip install -r requirements.txt
```

### Step 2.4: Create Core Files

Crea la struttura di file:

```bash
mkdir -p core/infrastructure/adapters
mkdir -p core/application/use_cases
mkdir -p core/domain/entities
mkdir -p core/domain/repositories
mkdir -p api/routes
```

Copia i file da `EXAMPLES_LINKEDIN_INTEGRATION.md`:

1. `core/infrastructure/adapters/linkedin_oauth_service.py`
2. `core/infrastructure/adapters/linkedin_api_client.py`
3. `core/infrastructure/adapters/linkedin_adapter.py`
4. `core/application/use_cases/publish_to_linkedin_use_case.py`
5. `api/routes/linkedin.py`

### Step 2.5: Create Entities

**File**: `core/domain/entities/linkedin_credential.py`

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID

@dataclass
class LinkedInCredential:
    id: Optional[UUID] = None
    tenant_id: UUID = None
    user_id: Optional[UUID] = None
    linkedin_person_urn: str = None
    linkedin_email: Optional[str] = None
    linkedin_name: Optional[str] = None
    access_token: str = None
    refresh_token: str = None
    access_token_expires_at: datetime = None
    refresh_token_expires_at: datetime = None
    scopes: List[str] = None
    is_active: bool = True
    last_used_at: Optional[datetime] = None
    last_refresh_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
```

**File**: `core/domain/entities/linkedin_publication.py`

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID

@dataclass
class LinkedInPublication:
    id: Optional[UUID] = None
    tenant_id: UUID = None
    credential_id: UUID = None
    content_id: Optional[UUID] = None
    linkedin_post_urn: Optional[str] = None
    linkedin_post_id: Optional[str] = None
    linkedin_post_url: Optional[str] = None
    post_type: str = None
    commentary: str = None
    visibility: str = "PUBLIC"
    media_urns: Optional[List[str]] = None
    article_url: Optional[str] = None
    article_title: Optional[str] = None
    status: str = "pending"
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    published_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
```

### Step 2.6: Test Backend

Avvia il server:

```bash
uvicorn main:app --reload --port 8000
```

Testa gli endpoint:

```bash
# Health check
curl http://localhost:8000/health

# Get authorization URL (richiede auth)
curl -X POST http://localhost:8000/api/linkedin/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"scopes": ["profile", "email", "w_member_social"]}'
```

---

## 🎨 PHASE 3: Frontend Setup

### Step 3.1: Install Dependencies

```bash
cd frontend

# Install dependencies
npm install lucide-react
npm install @radix-ui/react-dialog
npm install @radix-ui/react-toast
```

### Step 3.2: Create Components

Crea i componenti da `EXAMPLES_LINKEDIN_INTEGRATION.md`:

1. `components/linkedin/ConnectLinkedInButton.tsx`
2. `components/linkedin/PublishToLinkedInButton.tsx`
3. `components/linkedin/LinkedInPublicationStatus.tsx`

### Step 3.3: Create LinkedIn Icon

**File**: `components/icons/LinkedInIcon.tsx`

```typescript
import React from 'react';

export const LinkedInIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="currentColor"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
  </svg>
);
```

### Step 3.4: Create OAuth Callback Page

**File**: `app/auth/linkedin/callback/page.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

export default function LinkedInCallbackPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');

    if (!code || !state) {
      setStatus('error');
      return;
    }

    // Call backend callback endpoint
    fetch(`/api/linkedin/callback?code=${code}&state=${state}`)
      .then(response => {
        if (response.ok) {
          setStatus('success');
          setTimeout(() => router.push('/dashboard'), 2000);
        } else {
          setStatus('error');
        }
      })
      .catch(() => setStatus('error'));
  }, [searchParams, router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      {status === 'loading' && <p>Connecting LinkedIn...</p>}
      {status === 'success' && <p>LinkedIn connected! Redirecting...</p>}
      {status === 'error' && <p>Failed to connect LinkedIn. Please try again.</p>}
    </div>
  );
}
```

---

## ✅ PHASE 4: Testing

### Step 4.1: Test OAuth Flow

1. Avvia backend e frontend:
   ```bash
   # Terminal 1 - Backend
   uvicorn main:app --reload --port 8000
   
   # Terminal 2 - Frontend
   npm run dev
   ```

2. Vai su `http://localhost:3000`
3. Click su **"Connect LinkedIn"** button
4. Dovresti essere reindirizzato a LinkedIn
5. Autorizza l'app
6. Dovresti essere reindirizzato a `/auth/linkedin/callback`
7. Verifica che il credential sia salvato nel database:
   ```sql
   SELECT * FROM linkedin_credentials;
   ```

### Step 4.2: Test Text Post Publishing

1. Usa il `PublishToLinkedInButton` component
2. Pubblica un post di test:
   ```typescript
   <PublishToLinkedInButton
     contentId="test-content-id"
     postType="text"
     commentary="Test post from CGS! 🚀"
     onSuccess={(publicationId) => console.log('Published:', publicationId)}
   />
   ```

3. Verifica su LinkedIn che il post sia stato pubblicato
4. Verifica nel database:
   ```sql
   SELECT * FROM linkedin_publications WHERE status = 'published';
   ```

### Step 4.3: Test Image Post Publishing

1. Prepara un'immagine di test
2. Pubblica un post con immagine:
   ```typescript
   <PublishToLinkedInButton
     contentId="test-content-id"
     postType="image"
     commentary="Test image post! 📸"
     imageUrl="https://example.com/image.jpg"
     onSuccess={(publicationId) => console.log('Published:', publicationId)}
   />
   ```

3. Verifica su LinkedIn

---

## 🎯 SUCCESS CRITERIA

Hai completato con successo il setup quando:

- ✅ OAuth flow funziona (user può connettere LinkedIn)
- ✅ Credentials salvati nel database
- ✅ Text post pubblicato con successo
- ✅ Image post pubblicato con successo
- ✅ Publications tracked nel database
- ✅ UI components funzionanti

---

## 🐛 TROUBLESHOOTING

### Problema: "Invalid redirect_uri"

**Soluzione**: Verifica che il `LINKEDIN_REDIRECT_URI` nel `.env` corrisponda esattamente a quello configurato nella LinkedIn App.

### Problema: "Token expired"

**Soluzione**: Implementa il token refresh automatico (vedi `LI-1.4` e `LI-3.4` nel roadmap).

### Problema: "Rate limit exceeded"

**Soluzione**: Implementa rate limiting (vedi `LI-3.1` nel roadmap).

### Problema: "Image upload failed"

**Soluzione**: 
- Verifica che l'immagine sia <5MB
- Verifica formato (JPEG, PNG)
- Check logs per errori specifici

---

## 📚 NEXT STEPS

Dopo aver completato il Quick Start:

1. **Implement Error Handling** (EPIC 3)
   - Rate limiting
   - Retry logic
   - Monitoring

2. **Add Advanced Features** (EPIC 4)
   - Scheduled publishing
   - Video support
   - Multi-image posts

3. **Add Organization Support** (EPIC 5)
   - Company page publishing

4. **Add Analytics** (EPIC 6)
   - Performance tracking
   - Analytics dashboard

Vedi `LINEAR_ROADMAP_LINKEDIN_INTEGRATION.md` per il piano completo.

---

## 🔗 RESOURCES

- [LinkedIn API Documentation](https://learn.microsoft.com/en-us/linkedin/)
- [LinkedIn OAuth 2.0](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [LinkedIn Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)
- [LinkedIn Developer Portal](https://www.linkedin.com/developers/)

---

**Buon lavoro! 🚀**

