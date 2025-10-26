"""
Card Service Client - HTTP client for communicating with Card Service.

This client handles all communication with the Card Service API,
including creating cards from snapshots and retrieving card information.
"""

import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)


class CardServiceClient:
    """
    HTTP client for Card Service API.
    
    Responsibilities:
    - Create cards from snapshot
    - Retrieve card information
    - Handle errors and retries
    - Manage HTTP connections
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        timeout: int = 30,
        retry_attempts: int = 3,
    ):
        """
        Initialize CardServiceClient.
        
        Args:
            base_url: Base URL of Card Service API
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
        )
        logger.info(f"CardServiceClient initialized with base_url: {self.base_url}")
    
    async def create_cards_from_snapshot(
        self,
        tenant_id: str,
        snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create cards from CompanySnapshot.
        
        Calls Card Service API to create 4 atomic cards from the snapshot.
        
        Args:
            tenant_id: Tenant ID (user email or UUID)
            snapshot: Normalized CompanySnapshot dict
        
        Returns:
            Response dict with:
            - cards: List of CardSummary dicts
            - status: "success" or "error"
        
        Raises:
            Exception: If API call fails after retries
        """
        endpoint = "/api/v1/cards/onboarding/create-from-snapshot"
        
        logger.info(f"Creating cards from snapshot for tenant: {tenant_id}")
        
        for attempt in range(self.retry_attempts):
            try:
                response = await self.client.post(
                    endpoint,
                    params={"tenant_id": tenant_id},
                    json=snapshot,
                )
                
                # Check for success
                if response.status_code == 201:
                    data = response.json()

                    # Handle both list and dict responses
                    if isinstance(data, list):
                        cards = data
                    elif isinstance(data, dict) and "cards" in data:
                        cards = data.get("cards", [])
                    else:
                        cards = []

                    logger.info(f"Successfully created cards: {len(cards)} cards")
                    return {
                        "status": "success",
                        "cards": cards,
                    }
                
                # Check for client errors (4xx)
                elif response.status_code >= 400 and response.status_code < 500:
                    error_msg = response.text
                    logger.error(f"Client error (4xx): {response.status_code} - {error_msg}")
                    raise Exception(f"Card Service client error: {response.status_code} - {error_msg}")
                
                # Server errors (5xx) - retry
                else:
                    logger.warning(f"Server error (5xx): {response.status_code}, attempt {attempt + 1}/{self.retry_attempts}")
                    if attempt == self.retry_attempts - 1:
                        raise Exception(f"Card Service server error: {response.status_code}")
            
            except httpx.RequestError as e:
                logger.warning(f"Request error on attempt {attempt + 1}/{self.retry_attempts}: {str(e)}")
                if attempt == self.retry_attempts - 1:
                    raise Exception(f"Card Service connection error: {str(e)}")
        
        raise Exception("Failed to create cards after all retry attempts")
    
    async def get_cards(
        self,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """
        Get all cards for a tenant.
        
        Args:
            tenant_id: Tenant ID
        
        Returns:
            List of cards
        
        Raises:
            Exception: If API call fails
        """
        endpoint = "/api/v1/cards"
        
        logger.info(f"Retrieving cards for tenant: {tenant_id}")
        
        try:
            response = await self.client.get(
                endpoint,
                params={"tenant_id": tenant_id},
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get cards: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Failed to get cards: {str(e)}")
            raise
    
    async def close(self):
        """Close HTTP client connection."""
        await self.client.aclose()
        logger.info("CardServiceClient closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

