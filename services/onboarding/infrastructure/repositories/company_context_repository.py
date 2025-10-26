"""Supabase repository for company contexts (RAG system).

Handles CRUD operations for company contexts in Supabase.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from supabase import Client

from services.onboarding.config.settings import OnboardingSettings
from services.onboarding.domain.models import CompanySnapshot

logger = logging.getLogger(__name__)


class CompanyContextRepository:
    """
    Repository for persisting company contexts to Supabase (RAG system).
    
    Handles context CRUD operations, versioning, and usage tracking.
    """
    
    TABLE_NAME = "company_contexts"
    
    def __init__(self, settings: OnboardingSettings, client: Optional[Client] = None):
        """
        Initialize company context repository.
        
        Args:
            settings: Onboarding settings with Supabase configuration
            client: Optional Supabase client (for dependency injection)
        """
        self.settings = settings
        
        if client:
            self.client = client
        else:
            if not settings.is_supabase_configured():
                raise ValueError("Supabase not configured")
            
            from supabase import create_client
            self.client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key,
            )
        
        logger.info(f"CompanyContextRepository initialized")
    
    async def find_by_company_name(
        self, 
        company_name: str,
        max_age_days: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Find active context for company (RAG retrieval).
        
        Args:
            company_name: Company name (will be normalized)
            max_age_days: Maximum age in days (default: 30)
        
        Returns:
            Context dict or None if not found
        """
        normalized_name = self._normalize_company_name(company_name)
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        
        logger.info(f"🔍 RAG lookup: {normalized_name} (max age: {max_age_days} days)")
        
        try:
            result = self.client.table(self.TABLE_NAME) \
                .select("*") \
                .eq("company_name", normalized_name) \
                .eq("is_active", True) \
                .gte("updated_at", cutoff_date.isoformat()) \
                .order("version", desc=True) \
                .limit(1) \
                .execute()
            
            if result.data and len(result.data) > 0:
                context = result.data[0]
                logger.info(f"✅ RAG HIT: Found context {context['context_id']} (v{context['version']})")
                return context
            else:
                logger.info(f"❌ RAG MISS: No context found for {normalized_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding context: {str(e)}")
            raise
    
    async def create_context(
        self,
        company_name: str,
        company_display_name: str,
        website: Optional[str],
        snapshot: CompanySnapshot,
        source_session_id: UUID,
    ) -> Dict[str, Any]:
        """
        Create new company context.
        
        Args:
            company_name: Company name (will be normalized)
            company_display_name: Original company name for display
            website: Company website
            snapshot: CompanySnapshot object
            source_session_id: Session ID that created this context
        
        Returns:
            Created context dict
        """
        normalized_name = self._normalize_company_name(company_name)
        
        logger.info(f"💾 Creating context for: {company_display_name} ({normalized_name})")
        
        try:
            # Check if context exists (any version)
            existing = await self._find_any_version(normalized_name)
            version = (existing["version"] + 1) if existing else 1
            
            # Deactivate old versions
            if existing:
                logger.info(f"   Deactivating old version {existing['version']}")
                await self._deactivate_old_versions(normalized_name)
            
            # Extract metadata from snapshot
            industry = snapshot.company.industry if snapshot.company else None
            primary_audience = snapshot.audience.primary if snapshot.audience else None
            key_offerings = snapshot.company.key_offerings[:5] if snapshot.company and snapshot.company.key_offerings else []
            tags = self._generate_tags(snapshot)
            
            # Prepare data
            data = {
                "company_name": normalized_name,
                "company_display_name": company_display_name,
                "website": website,
                "version": version,
                "company_snapshot": snapshot.model_dump(mode="json"),
                "industry": industry,
                "primary_audience": primary_audience,
                "key_offerings": key_offerings,
                "tags": tags,
                "source_session_id": str(source_session_id),
                "usage_count": 0,
                "is_active": True,
            }
            
            # Insert new context
            result = self.client.table(self.TABLE_NAME).insert(data).execute()
            
            if result.data and len(result.data) > 0:
                context = result.data[0]
                logger.info(f"✅ Context created: {context['context_id']} (v{version})")
                return context
            else:
                raise ValueError("Failed to create context: no data returned")
                
        except Exception as e:
            logger.error(f"Error creating context: {str(e)}")
            raise
    
    async def increment_usage(self, context_id: UUID) -> None:
        """
        Increment usage counter for a context.
        
        Args:
            context_id: Context UUID
        """
        logger.info(f"♻️ Incrementing usage for context: {context_id}")
        
        try:
            # Get current context
            result = self.client.table(self.TABLE_NAME) \
                .select("usage_count") \
                .eq("context_id", str(context_id)) \
                .execute()
            
            if not result.data or len(result.data) == 0:
                logger.warning(f"Context not found: {context_id}")
                return
            
            current_count = result.data[0].get("usage_count", 0)
            new_count = current_count + 1
            
            # Update
            self.client.table(self.TABLE_NAME) \
                .update({
                    "usage_count": new_count,
                    "last_used_at": datetime.utcnow().isoformat()
                }) \
                .eq("context_id", str(context_id)) \
                .execute()
            
            logger.info(f"   Usage count: {current_count} → {new_count}")
            
        except Exception as e:
            logger.error(f"Error incrementing usage: {str(e)}")
            # Don't raise - this is not critical
    
    async def get_by_id(self, context_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get context by ID.
        
        Args:
            context_id: Context UUID
        
        Returns:
            Context dict or None if not found
        """
        try:
            result = self.client.table(self.TABLE_NAME) \
                .select("*") \
                .eq("context_id", str(context_id)) \
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
            raise
    
    async def list_contexts(
        self,
        limit: int = 50,
        offset: int = 0,
        industry: Optional[str] = None,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        List company contexts.
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            industry: Filter by industry
            active_only: Only return active contexts
        
        Returns:
            List of context dicts
        """
        try:
            query = self.client.table(self.TABLE_NAME).select("*")
            
            if active_only:
                query = query.eq("is_active", True)
            
            if industry:
                query = query.eq("industry", industry)
            
            result = query \
                .order("updated_at", desc=True) \
                .range(offset, offset + limit - 1) \
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error listing contexts: {str(e)}")
            raise
    
    async def deactivate_context(self, context_id: UUID) -> None:
        """
        Deactivate a context.
        
        Args:
            context_id: Context UUID
        """
        logger.info(f"Deactivating context: {context_id}")
        
        try:
            self.client.table(self.TABLE_NAME) \
                .update({"is_active": False}) \
                .eq("context_id", str(context_id)) \
                .execute()
            
            logger.info(f"✅ Context deactivated: {context_id}")
            
        except Exception as e:
            logger.error(f"Error deactivating context: {str(e)}")
            raise
    
    # ========================================================================
    # Private helper methods
    # ========================================================================
    
    async def _find_any_version(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Find any version of a company context (active or not)."""
        try:
            result = self.client.table(self.TABLE_NAME) \
                .select("*") \
                .eq("company_name", company_name) \
                .order("version", desc=True) \
                .limit(1) \
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error finding any version: {str(e)}")
            return None
    
    async def _deactivate_old_versions(self, company_name: str) -> None:
        """Deactivate all versions of a company context."""
        try:
            self.client.table(self.TABLE_NAME) \
                .update({"is_active": False}) \
                .eq("company_name", company_name) \
                .execute()
        except Exception as e:
            logger.error(f"Error deactivating old versions: {str(e)}")
            # Don't raise - not critical
    
    def _normalize_company_name(self, name: str) -> str:
        """
        Normalize company name for matching.
        
        Rules:
        - Lowercase
        - Remove spaces
        - Remove dashes
        - Remove special characters
        
        Examples:
            "Peter Legwood" → "peterlegwood"
            "peter-legwood" → "peterlegwood"
            "PETERLEGWOOD" → "peterlegwood"
        """
        return name.lower().strip().replace(" ", "").replace("-", "").replace("_", "")
    
    def _generate_tags(self, snapshot: CompanySnapshot) -> List[str]:
        """
        Generate tags from snapshot for categorization.
        
        Args:
            snapshot: CompanySnapshot object
        
        Returns:
            List of tags (max 10)
        """
        tags = []
        
        # Add industry
        if snapshot.company and snapshot.company.industry:
            tags.append(snapshot.company.industry.lower())
        
        # Add keywords from audience
        if snapshot.audience and snapshot.audience.primary:
            # Extract keywords (words longer than 4 chars)
            words = snapshot.audience.primary.lower().split()
            keywords = [w for w in words if len(w) > 4 and w.isalpha()]
            tags.extend(keywords[:3])  # Max 3 keywords from audience
        
        # Add keywords from key offerings
        if snapshot.company and snapshot.company.key_offerings:
            for offering in snapshot.company.key_offerings[:2]:  # Max 2 offerings
                words = offering.lower().split()
                keywords = [w for w in words if len(w) > 4 and w.isalpha()]
                tags.extend(keywords[:1])  # 1 keyword per offering
        
        # Deduplicate and limit
        unique_tags = list(dict.fromkeys(tags))  # Preserve order
        return unique_tags[:10]

