# 🔵 LinkedIn Integration - Code Examples

**Version**: 1.0  
**Date**: 2025-10-25

---

## 📋 TABLE OF CONTENTS

1. [LinkedIn OAuth Service](#1-linkedin-oauth-service)
2. [LinkedIn API Client](#2-linkedin-api-client)
3. [LinkedIn Adapter](#3-linkedin-adapter)
4. [Use Cases](#4-use-cases)
5. [API Endpoints](#5-api-endpoints)
6. [Frontend Components](#6-frontend-components)

---

## 1. LinkedIn OAuth Service

### File: `core/infrastructure/adapters/linkedin_oauth_service.py`

```python
from typing import Optional
from urllib.parse import urlencode
import secrets
import httpx
from datetime import datetime, timedelta

from core.domain.entities.linkedin_credential import LinkedInCredential
from core.domain.repositories.linkedin_credential_repository import LinkedInCredentialRepository
from core.infrastructure.config import settings


class LinkedInOAuthService:
    """Handles LinkedIn OAuth 2.0 flow"""
    
    AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    
    def __init__(
        self,
        credential_repository: LinkedInCredentialRepository,
        encryption_service: EncryptionService
    ):
        self.credential_repo = credential_repository
        self.encryption = encryption_service
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    def get_authorization_url(
        self,
        tenant_id: str,
        user_id: str,
        scopes: list[str] = None
    ) -> str:
        """
        Generate LinkedIn authorization URL
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID
            scopes: OAuth scopes (default: ['profile', 'email', 'w_member_social'])
        
        Returns:
            Authorization URL
        """
        if scopes is None:
            scopes = ['profile', 'email', 'w_member_social']
        
        # Generate state for CSRF protection
        state = self._generate_state(tenant_id, user_id)
        
        params = {
            'response_type': 'code',
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'redirect_uri': settings.LINKEDIN_REDIRECT_URI,
            'scope': ' '.join(scopes),
            'state': state
        }
        
        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"
    
    async def exchange_code_for_token(
        self,
        code: str,
        tenant_id: str,
        user_id: str
    ) -> LinkedInCredential:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from LinkedIn
            tenant_id: Tenant ID
            user_id: User ID
        
        Returns:
            LinkedInCredential entity
        """
        # Exchange code for token
        response = await self.http_client.post(
            self.TOKEN_URL,
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': settings.LINKEDIN_CLIENT_ID,
                'client_secret': settings.LINKEDIN_CLIENT_SECRET,
                'redirect_uri': settings.LINKEDIN_REDIRECT_URI
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()
        token_data = response.json()
        
        # Get user profile
        profile = await self._get_user_profile(token_data['access_token'])
        
        # Create credential entity
        credential = LinkedInCredential(
            tenant_id=tenant_id,
            user_id=user_id,
            linkedin_person_urn=f"urn:li:person:{profile['sub']}",
            linkedin_email=profile.get('email'),
            linkedin_name=profile.get('name'),
            access_token=self.encryption.encrypt(token_data['access_token']),
            refresh_token=self.encryption.encrypt(token_data['refresh_token']),
            access_token_expires_at=datetime.now() + timedelta(seconds=token_data['expires_in']),
            refresh_token_expires_at=datetime.now() + timedelta(seconds=token_data['refresh_token_expires_in']),
            scopes=token_data['scope'].split(' ')
        )
        
        # Save to database
        await self.credential_repo.save(credential)
        
        return credential
    
    async def refresh_access_token(self, credential_id: str) -> LinkedInCredential:
        """
        Refresh access token using refresh token
        
        Args:
            credential_id: Credential ID
        
        Returns:
            Updated LinkedInCredential
        """
        credential = await self.credential_repo.get_by_id(credential_id)
        
        if not credential:
            raise ValueError(f"Credential {credential_id} not found")
        
        # Decrypt refresh token
        refresh_token = self.encryption.decrypt(credential.refresh_token)
        
        # Refresh token
        response = await self.http_client.post(
            self.TOKEN_URL,
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': settings.LINKEDIN_CLIENT_ID,
                'client_secret': settings.LINKEDIN_CLIENT_SECRET
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()
        token_data = response.json()
        
        # Update credential
        credential.access_token = self.encryption.encrypt(token_data['access_token'])
        credential.refresh_token = self.encryption.encrypt(token_data['refresh_token'])
        credential.access_token_expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])
        credential.refresh_token_expires_at = datetime.now() + timedelta(seconds=token_data['refresh_token_expires_in'])
        credential.last_refresh_at = datetime.now()
        
        await self.credential_repo.update(credential)
        
        return credential
    
    async def _get_user_profile(self, access_token: str) -> dict:
        """Get LinkedIn user profile"""
        response = await self.http_client.get(
            "https://api.linkedin.com/v2/userinfo",
            headers={'Authorization': f'Bearer {access_token}'}
        )
        response.raise_for_status()
        return response.json()
    
    def _generate_state(self, tenant_id: str, user_id: str) -> str:
        """Generate state parameter for CSRF protection"""
        random_state = secrets.token_urlsafe(32)
        # Store state in cache/database with tenant_id and user_id
        # Return state
        return random_state
```

---

## 2. LinkedIn API Client

### File: `core/infrastructure/adapters/linkedin_api_client.py`

```python
import httpx
from typing import Optional, Dict, Any
from datetime import datetime

from core.domain.entities.linkedin_credential import LinkedInCredential
from core.infrastructure.services.encryption_service import EncryptionService


class LinkedInAPIClient:
    """HTTP client for LinkedIn REST API"""
    
    BASE_URL = "https://api.linkedin.com/rest"
    API_VERSION = "202501"  # Format: YYYYMM
    
    def __init__(
        self,
        credential: LinkedInCredential,
        encryption_service: EncryptionService
    ):
        self.credential = credential
        self.encryption = encryption_service
        self.session = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                'X-Restli-Protocol-Version': '2.0.0',
                'Linkedin-Version': self.API_VERSION
            },
            timeout=30.0
        )
    
    async def _request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make authenticated request to LinkedIn API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., '/posts')
            **kwargs: Additional request parameters
        
        Returns:
            Response JSON
        
        Raises:
            TokenExpiredError: If access token is expired
            RateLimitError: If rate limit exceeded
        """
        # Decrypt access token
        access_token = self.encryption.decrypt(self.credential.access_token)
        
        # Add authorization header
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {access_token}'
        
        # Make request
        response = await self.session.request(
            method,
            path,
            headers=headers,
            **kwargs
        )
        
        # Handle errors
        if response.status_code == 401:
            raise TokenExpiredError("Access token expired")
        elif response.status_code == 429:
            retry_after = response.headers.get('Retry-After', 60)
            raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after}s")
        
        response.raise_for_status()
        
        return response.json() if response.content else {}
    
    async def get_me(self) -> Dict[str, Any]:
        """Get authenticated user profile"""
        return await self._request('GET', '/me')
    
    async def create_post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a LinkedIn post
        
        Args:
            payload: Post payload
        
        Returns:
            Post response with URN
        """
        return await self._request('POST', '/posts', json=payload)
    
    async def get_post(self, post_id: str) -> Dict[str, Any]:
        """Get post by ID"""
        return await self._request('GET', f'/posts/{post_id}')
    
    async def delete_post(self, post_id: str) -> None:
        """Delete post by ID"""
        await self._request('DELETE', f'/posts/{post_id}')
    
    async def initialize_image_upload(self, owner_urn: str) -> Dict[str, Any]:
        """
        Initialize image upload
        
        Args:
            owner_urn: Owner URN (person or organization)
        
        Returns:
            Upload URL and image URN
        """
        payload = {
            "initializeUploadRequest": {
                "owner": owner_urn
            }
        }
        return await self._request('POST', '/images?action=initializeUpload', json=payload)
    
    async def upload_image_binary(self, upload_url: str, image_data: bytes) -> None:
        """
        Upload image binary to LinkedIn
        
        Args:
            upload_url: Upload URL from initialize_image_upload
            image_data: Image binary data
        """
        async with httpx.AsyncClient() as client:
            response = await client.put(
                upload_url,
                content=image_data,
                headers={'Content-Type': 'application/octet-stream'}
            )
            response.raise_for_status()
    
    async def close(self):
        """Close HTTP session"""
        await self.session.aclose()


class TokenExpiredError(Exception):
    """Raised when access token is expired"""
    pass


class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    pass
```

---

## 3. LinkedIn Adapter

### File: `core/infrastructure/adapters/linkedin_adapter.py`

```python
from typing import Optional, List
from datetime import datetime
import logging

from core.domain.entities.linkedin_credential import LinkedInCredential
from core.domain.entities.linkedin_publication import LinkedInPublication
from core.infrastructure.adapters.linkedin_api_client import LinkedInAPIClient, TokenExpiredError, RateLimitError
from core.infrastructure.services.encryption_service import EncryptionService


logger = logging.getLogger(__name__)


class LinkedInAdapter:
    """Adapter for LinkedIn publishing operations"""
    
    def __init__(
        self,
        credential: LinkedInCredential,
        encryption_service: EncryptionService
    ):
        self.credential = credential
        self.encryption = encryption_service
        self.client = LinkedInAPIClient(credential, encryption_service)
        self.author_urn = credential.linkedin_person_urn
    
    async def publish_text_post(
        self,
        commentary: str,
        visibility: str = "PUBLIC"
    ) -> LinkedInPublication:
        """
        Publish text-only post
        
        Args:
            commentary: Post text
            visibility: Post visibility (PUBLIC, CONNECTIONS)
        
        Returns:
            LinkedInPublication entity
        """
        payload = {
            "author": self.author_urn,
            "commentary": commentary,
            "visibility": visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED"
        }
        
        try:
            response = await self.client.create_post(payload)
            
            # Extract post URN and ID
            post_urn = response.get('id')  # e.g., "urn:li:share:123"
            post_id = post_urn.split(':')[-1] if post_urn else None
            
            # Create publication entity
            publication = LinkedInPublication(
                tenant_id=self.credential.tenant_id,
                credential_id=self.credential.id,
                linkedin_post_urn=post_urn,
                linkedin_post_id=post_id,
                linkedin_post_url=f"https://www.linkedin.com/feed/update/{post_urn}",
                post_type='text',
                commentary=commentary,
                visibility=visibility,
                status='published',
                published_at=datetime.now()
            )
            
            logger.info(f"Published text post: {post_urn}")
            return publication
            
        except TokenExpiredError:
            logger.error("Token expired during publish")
            raise
        except RateLimitError as e:
            logger.warning(f"Rate limit exceeded: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to publish text post: {e}")
            raise
    
    async def publish_image_post(
        self,
        commentary: str,
        image_data: bytes,
        image_title: Optional[str] = None,
        visibility: str = "PUBLIC"
    ) -> LinkedInPublication:
        """
        Publish post with image
        
        Args:
            commentary: Post text
            image_data: Image binary data
            image_title: Image title (optional)
            visibility: Post visibility
        
        Returns:
            LinkedInPublication entity
        """
        try:
            # Step 1: Upload image
            upload_response = await self.client.initialize_image_upload(self.author_urn)
            upload_url = upload_response['value']['uploadUrl']
            image_urn = upload_response['value']['image']
            
            await self.client.upload_image_binary(upload_url, image_data)
            
            logger.info(f"Uploaded image: {image_urn}")
            
            # Step 2: Create post with image
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
            
            response = await self.client.create_post(payload)
            
            post_urn = response.get('id')
            post_id = post_urn.split(':')[-1] if post_urn else None
            
            publication = LinkedInPublication(
                tenant_id=self.credential.tenant_id,
                credential_id=self.credential.id,
                linkedin_post_urn=post_urn,
                linkedin_post_id=post_id,
                linkedin_post_url=f"https://www.linkedin.com/feed/update/{post_urn}",
                post_type='image',
                commentary=commentary,
                visibility=visibility,
                media_urns=[image_urn],
                status='published',
                published_at=datetime.now()
            )
            
            logger.info(f"Published image post: {post_urn}")
            return publication
            
        except Exception as e:
            logger.error(f"Failed to publish image post: {e}")
            raise
    
    async def publish_article_post(
        self,
        commentary: str,
        article_url: str,
        article_title: Optional[str] = None,
        article_description: Optional[str] = None,
        visibility: str = "PUBLIC"
    ) -> LinkedInPublication:
        """
        Publish post with article link
        
        Args:
            commentary: Post text
            article_url: Article URL
            article_title: Article title (optional, LinkedIn will fetch)
            article_description: Article description (optional)
            visibility: Post visibility
        
        Returns:
            LinkedInPublication entity
        """
        payload = {
            "author": self.author_urn,
            "commentary": commentary,
            "visibility": visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED"
            },
            "content": {
                "article": {
                    "source": article_url,
                    "title": article_title,
                    "description": article_description
                }
            },
            "lifecycleState": "PUBLISHED"
        }
        
        try:
            response = await self.client.create_post(payload)
            
            post_urn = response.get('id')
            post_id = post_urn.split(':')[-1] if post_urn else None
            
            publication = LinkedInPublication(
                tenant_id=self.credential.tenant_id,
                credential_id=self.credential.id,
                linkedin_post_urn=post_urn,
                linkedin_post_id=post_id,
                linkedin_post_url=f"https://www.linkedin.com/feed/update/{post_urn}",
                post_type='article',
                commentary=commentary,
                visibility=visibility,
                article_url=article_url,
                article_title=article_title,
                article_description=article_description,
                status='published',
                published_at=datetime.now()
            )
            
            logger.info(f"Published article post: {post_urn}")
            return publication
            
        except Exception as e:
            logger.error(f"Failed to publish article post: {e}")
            raise
    
    async def close(self):
        """Close adapter resources"""
        await self.client.close()
```

---

## 4. Use Cases

### File: `core/application/use_cases/publish_to_linkedin_use_case.py`

```python
from typing import Optional
from uuid import UUID
import logging

from core.domain.entities.linkedin_publication import LinkedInPublication
from core.domain.repositories.linkedin_credential_repository import LinkedInCredentialRepository
from core.domain.repositories.linkedin_publication_repository import LinkedInPublicationRepository
from core.infrastructure.adapters.linkedin_adapter import LinkedInAdapter
from core.infrastructure.services.encryption_service import EncryptionService


logger = logging.getLogger(__name__)


class PublishToLinkedInUseCase:
    """Use case for publishing content to LinkedIn"""
    
    def __init__(
        self,
        credential_repo: LinkedInCredentialRepository,
        publication_repo: LinkedInPublicationRepository,
        encryption_service: EncryptionService
    ):
        self.credential_repo = credential_repo
        self.publication_repo = publication_repo
        self.encryption = encryption_service
    
    async def execute(
        self,
        tenant_id: UUID,
        user_id: UUID,
        content_id: UUID,
        post_type: str,
        commentary: str,
        image_data: Optional[bytes] = None,
        article_url: Optional[str] = None,
        visibility: str = "PUBLIC"
    ) -> LinkedInPublication:
        """
        Publish content to LinkedIn
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID
            content_id: Content ID (reference to generated content)
            post_type: Post type ('text', 'image', 'article')
            commentary: Post text
            image_data: Image binary (for image posts)
            article_url: Article URL (for article posts)
            visibility: Post visibility
        
        Returns:
            LinkedInPublication entity
        """
        # Get credential
        credential = await self.credential_repo.get_active_by_user(tenant_id, user_id)
        
        if not credential:
            raise ValueError(f"No active LinkedIn credential for user {user_id}")
        
        # Create publication record (status='publishing')
        publication = await self.publication_repo.create(
            tenant_id=tenant_id,
            credential_id=credential.id,
            content_id=content_id,
            post_type=post_type,
            commentary=commentary,
            visibility=visibility,
            status='publishing'
        )
        
        try:
            # Create adapter
            adapter = LinkedInAdapter(credential, self.encryption)
            
            # Publish based on type
            if post_type == 'text':
                result = await adapter.publish_text_post(commentary, visibility)
            elif post_type == 'image':
                if not image_data:
                    raise ValueError("Image data required for image post")
                result = await adapter.publish_image_post(commentary, image_data, visibility=visibility)
            elif post_type == 'article':
                if not article_url:
                    raise ValueError("Article URL required for article post")
                result = await adapter.publish_article_post(commentary, article_url, visibility=visibility)
            else:
                raise ValueError(f"Unsupported post type: {post_type}")
            
            # Update publication with success
            publication.linkedin_post_urn = result.linkedin_post_urn
            publication.linkedin_post_id = result.linkedin_post_id
            publication.linkedin_post_url = result.linkedin_post_url
            publication.status = 'published'
            publication.published_at = result.published_at
            
            await self.publication_repo.update(publication)
            
            logger.info(f"Successfully published to LinkedIn: {publication.id}")
            
            await adapter.close()
            
            return publication
            
        except Exception as e:
            # Update publication with failure
            publication.status = 'failed'
            publication.error_message = str(e)
            publication.retry_count += 1
            
            await self.publication_repo.update(publication)
            
            logger.error(f"Failed to publish to LinkedIn: {e}")
            raise
```

---

## 5. API Endpoints

### File: `api/routes/linkedin.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from core.application.use_cases.publish_to_linkedin_use_case import PublishToLinkedInUseCase
from core.infrastructure.adapters.linkedin_oauth_service import LinkedInOAuthService
from api.dependencies import get_current_user, get_current_tenant


router = APIRouter(prefix="/api/linkedin", tags=["LinkedIn"])


# ============================================================================
# DTOs
# ============================================================================

class ConnectLinkedInRequest(BaseModel):
    scopes: Optional[list[str]] = None


class ConnectLinkedInResponse(BaseModel):
    authorization_url: str


class LinkedInCallbackRequest(BaseModel):
    code: str
    state: str


class PublishToLinkedInRequest(BaseModel):
    content_id: UUID
    post_type: str  # 'text', 'image', 'article'
    commentary: str
    image_url: Optional[str] = None
    article_url: Optional[str] = None
    visibility: str = "PUBLIC"


class PublishToLinkedInResponse(BaseModel):
    publication_id: UUID
    linkedin_post_urn: str
    linkedin_post_url: str
    status: str


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/connect", response_model=ConnectLinkedInResponse)
async def connect_linkedin(
    request: ConnectLinkedInRequest,
    current_user = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant),
    oauth_service: LinkedInOAuthService = Depends()
):
    """
    Initiate LinkedIn OAuth flow

    Returns authorization URL for user to visit
    """
    authorization_url = oauth_service.get_authorization_url(
        tenant_id=current_tenant.id,
        user_id=current_user.id,
        scopes=request.scopes
    )

    return ConnectLinkedInResponse(authorization_url=authorization_url)


@router.get("/callback")
async def linkedin_callback(
    code: str = Query(...),
    state: str = Query(...),
    oauth_service: LinkedInOAuthService = Depends()
):
    """
    OAuth callback endpoint

    LinkedIn redirects here after user authorization
    """
    # Validate state (CSRF protection)
    tenant_id, user_id = oauth_service.validate_state(state)

    # Exchange code for token
    credential = await oauth_service.exchange_code_for_token(
        code=code,
        tenant_id=tenant_id,
        user_id=user_id
    )

    # Redirect to frontend success page
    return {
        "message": "LinkedIn connected successfully",
        "credential_id": str(credential.id)
    }


@router.post("/publish", response_model=PublishToLinkedInResponse)
async def publish_to_linkedin(
    request: PublishToLinkedInRequest,
    current_user = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant),
    publish_use_case: PublishToLinkedInUseCase = Depends()
):
    """
    Publish content to LinkedIn
    """
    # Download image if image_url provided
    image_data = None
    if request.image_url:
        image_data = await download_image(request.image_url)

    # Execute use case
    publication = await publish_use_case.execute(
        tenant_id=current_tenant.id,
        user_id=current_user.id,
        content_id=request.content_id,
        post_type=request.post_type,
        commentary=request.commentary,
        image_data=image_data,
        article_url=request.article_url,
        visibility=request.visibility
    )

    return PublishToLinkedInResponse(
        publication_id=publication.id,
        linkedin_post_urn=publication.linkedin_post_urn,
        linkedin_post_url=publication.linkedin_post_url,
        status=publication.status
    )


@router.get("/publications")
async def get_publications(
    current_user = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant),
    publication_repo = Depends()
):
    """
    Get all LinkedIn publications for current user
    """
    publications = await publication_repo.get_by_tenant_and_user(
        tenant_id=current_tenant.id,
        user_id=current_user.id
    )

    return {"publications": publications}


@router.get("/credentials")
async def get_credentials(
    current_user = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant),
    credential_repo = Depends()
):
    """
    Get LinkedIn credentials for current user
    """
    credentials = await credential_repo.get_by_tenant_and_user(
        tenant_id=current_tenant.id,
        user_id=current_user.id
    )

    return {"credentials": credentials}


@router.delete("/credentials/{credential_id}")
async def disconnect_linkedin(
    credential_id: UUID,
    current_user = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant),
    credential_repo = Depends()
):
    """
    Disconnect LinkedIn account
    """
    credential = await credential_repo.get_by_id(credential_id)

    if not credential or credential.tenant_id != current_tenant.id:
        raise HTTPException(status_code=404, detail="Credential not found")

    credential.is_active = False
    await credential_repo.update(credential)

    return {"message": "LinkedIn disconnected successfully"}
```

---

## 6. Frontend Components

### Component: `ConnectLinkedInButton.tsx`

```typescript
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { LinkedInIcon } from '@/components/icons';
import { useToast } from '@/hooks/use-toast';

interface ConnectLinkedInButtonProps {
  onSuccess?: () => void;
}

export const ConnectLinkedInButton: React.FC<ConnectLinkedInButtonProps> = ({
  onSuccess
}) => {
  const [isConnecting, setIsConnecting] = useState(false);
  const { toast } = useToast();

  const handleConnect = async () => {
    setIsConnecting(true);

    try {
      // Call API to get authorization URL
      const response = await fetch('/api/linkedin/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scopes: ['profile', 'email', 'w_member_social']
        })
      });

      const data = await response.json();

      // Redirect to LinkedIn authorization page
      window.location.href = data.authorization_url;

    } catch (error) {
      console.error('Failed to connect LinkedIn:', error);
      toast({
        title: 'Error',
        description: 'Failed to connect LinkedIn. Please try again.',
        variant: 'destructive'
      });
      setIsConnecting(false);
    }
  };

  return (
    <Button
      onClick={handleConnect}
      disabled={isConnecting}
      className="bg-[#0A66C2] hover:bg-[#004182] text-white"
    >
      <LinkedInIcon className="mr-2 h-4 w-4" />
      {isConnecting ? 'Connecting...' : 'Connect LinkedIn'}
    </Button>
  );
};
```

### Component: `PublishToLinkedInButton.tsx`

```typescript
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { LinkedInIcon } from '@/components/icons';
import { useToast } from '@/hooks/use-toast';

interface PublishToLinkedInButtonProps {
  contentId: string;
  postType: 'text' | 'image' | 'article';
  commentary: string;
  imageUrl?: string;
  articleUrl?: string;
  visibility?: 'PUBLIC' | 'CONNECTIONS';
  onSuccess?: (publicationId: string) => void;
}

export const PublishToLinkedInButton: React.FC<PublishToLinkedInButtonProps> = ({
  contentId,
  postType,
  commentary,
  imageUrl,
  articleUrl,
  visibility = 'PUBLIC',
  onSuccess
}) => {
  const [isPublishing, setIsPublishing] = useState(false);
  const { toast } = useToast();

  const handlePublish = async () => {
    setIsPublishing(true);

    try {
      const response = await fetch('/api/linkedin/publish', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content_id: contentId,
          post_type: postType,
          commentary,
          image_url: imageUrl,
          article_url: articleUrl,
          visibility
        })
      });

      if (!response.ok) {
        throw new Error('Failed to publish');
      }

      const data = await response.json();

      toast({
        title: 'Success',
        description: 'Published to LinkedIn successfully!',
      });

      onSuccess?.(data.publication_id);

    } catch (error) {
      console.error('Failed to publish to LinkedIn:', error);
      toast({
        title: 'Error',
        description: 'Failed to publish to LinkedIn. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <Button
      onClick={handlePublish}
      disabled={isPublishing}
      className="bg-[#0A66C2] hover:bg-[#004182] text-white"
    >
      <LinkedInIcon className="mr-2 h-4 w-4" />
      {isPublishing ? 'Publishing...' : 'Publish to LinkedIn'}
    </Button>
  );
};
```

### Component: `LinkedInPublicationStatus.tsx`

```typescript
import React from 'react';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, Clock, Loader } from 'lucide-react';

interface LinkedInPublicationStatusProps {
  status: 'pending' | 'publishing' | 'published' | 'failed' | 'scheduled';
  linkedInPostUrl?: string;
  errorMessage?: string;
}

export const LinkedInPublicationStatus: React.FC<LinkedInPublicationStatusProps> = ({
  status,
  linkedInPostUrl,
  errorMessage
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'published':
        return {
          icon: <CheckCircle className="h-4 w-4" />,
          label: 'Published',
          variant: 'success' as const,
          color: 'text-green-600'
        };
      case 'failed':
        return {
          icon: <XCircle className="h-4 w-4" />,
          label: 'Failed',
          variant: 'destructive' as const,
          color: 'text-red-600'
        };
      case 'publishing':
        return {
          icon: <Loader className="h-4 w-4 animate-spin" />,
          label: 'Publishing',
          variant: 'default' as const,
          color: 'text-blue-600'
        };
      case 'scheduled':
        return {
          icon: <Clock className="h-4 w-4" />,
          label: 'Scheduled',
          variant: 'secondary' as const,
          color: 'text-yellow-600'
        };
      default:
        return {
          icon: <Clock className="h-4 w-4" />,
          label: 'Pending',
          variant: 'outline' as const,
          color: 'text-gray-600'
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className="flex items-center gap-2">
      <Badge variant={config.variant} className="flex items-center gap-1">
        {config.icon}
        {config.label}
      </Badge>

      {status === 'published' && linkedInPostUrl && (
        <a
          href={linkedInPostUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-blue-600 hover:underline"
        >
          View on LinkedIn
        </a>
      )}

      {status === 'failed' && errorMessage && (
        <span className="text-sm text-red-600">{errorMessage}</span>
      )}
    </div>
  );
};
```

---

**Next**: See `LINKEDIN_QUICK_START.md` for setup guide.

