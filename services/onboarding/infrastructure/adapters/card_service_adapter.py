"""Adapter for Card Service API invocation."""

import logging
from typing import Any, Dict, List, Optional, Union

import httpx

from services.onboarding.config.settings import OnboardingSettings
from packages.contracts.onboarding import CompanySnapshot

logger = logging.getLogger(__name__)


class CardServiceAdapter:
    """
    Adapter for Card Service API invocation.
    
    Handles HTTP communication with Card Service backend for creating cards
    from services.onboarding snapshots.
    """
    
    def __init__(self, settings: OnboardingSettings):
        """
        Initialize Card Service adapter.
        
        Args:
            settings: Onboarding settings with Card Service configuration
        """
        self.settings = settings
        self.base_url = settings.card_service_api_url
        self.timeout = settings.card_service_api_timeout
        self.api_key = settings.card_service_api_key
        
        logger.info(f"Card Service adapter initialized: {self.base_url}")
    
    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for Card Service requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def create_cards_from_snapshot(
        self,
        tenant_id: str,
        snapshot: Union[CompanySnapshot, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Create atomic cards from CompanySnapshot.
        
        Args:
            tenant_id: Tenant identifier (user email)
            snapshot: CompanySnapshot dict with company_info, audience_info, goal, insights
            
        Returns:
            List of created cards with id, card_type, title, content
            
        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If response is invalid
        """
        endpoint = f"{self.base_url}/api/v1/cards/onboarding/create-from-snapshot"
        
        try:
            payload = (
                snapshot.to_card_payload()
                if isinstance(snapshot, CompanySnapshot)
                else snapshot
            )

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    endpoint,
                    json=payload,
                    headers=self._build_headers(),
                    params={"tenant_id": tenant_id},
                )
                
                response.raise_for_status()
                data = response.json()
            
            # Validate response
            if not isinstance(data, list):
                raise ValueError(f"Expected list of cards, got {type(data)}")
            
            logger.info(
                f"✨ Created {len(data)} cards from snapshot for tenant {tenant_id}"
            )
            
            return data
            
        except httpx.HTTPStatusError as e:
            error_msg = f"Card Service API error: {e.response.status_code}"
            try:
                error_detail = e.response.json().get("detail", "")
                if error_detail:
                    error_msg += f" - {error_detail}"
            except Exception:
                pass
            
            logger.error(error_msg)
            raise
        
        except Exception as e:
            logger.error(f"Card Service request failed: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if Card Service API is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Card Service health check failed: {str(e)}")
            return False

