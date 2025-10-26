"""
Card Export Pipeline - Exports CompanySnapshot to Card Service.

This pipeline orchestrates the export of a CompanySnapshot to the Card Service,
which creates 4 atomic cards (Product, Persona, Campaign, Topic) from the snapshot.

Flow:
1. Receive CompanySnapshot from Onboarding
2. Normalize snapshot for Card Service
3. Call Card Service API to create cards
4. Receive CardSummary list
5. Return cards to Onboarding for workflow context
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from services.onboarding.domain.models import CompanySnapshot
from services.onboarding.infrastructure.card_service_client import CardServiceClient

logger = logging.getLogger(__name__)


class CardExportPipeline:
    """
    Pipeline for exporting CompanySnapshot to Card Service.
    
    Responsibilities:
    - Normalize snapshot for Card Service API
    - Call Card Service to create cards
    - Handle errors and retries
    - Return CardSummary list
    """
    
    def __init__(self, card_service_client: CardServiceClient):
        """
        Initialize CardExportPipeline.
        
        Args:
            card_service_client: Client for communicating with Card Service
        """
        self.card_service = card_service_client
        logger.info("CardExportPipeline initialized")
    
    async def export_snapshot(
        self,
        tenant_id: str,
        snapshot: CompanySnapshot,
    ) -> Dict[str, Any]:
        """
        Export CompanySnapshot to Card Service.
        
        Creates 4 atomic cards from the snapshot and returns CardSummary list.
        
        Args:
            tenant_id: Tenant ID (user email or UUID)
            snapshot: CompanySnapshot to export
        
        Returns:
            Dict with:
            - cards: List of CardSummary dicts
            - snapshot_id: ID of the snapshot
            - status: "success" or "error"
        
        Raises:
            Exception: If Card Service call fails
        """
        logger.info(f"Exporting snapshot to Card Service for tenant: {tenant_id}")
        
        try:
            # 1. Normalize snapshot
            normalized_snapshot = self._normalize_snapshot(snapshot)
            logger.debug(f"Snapshot normalized with keys: {normalized_snapshot.keys()}")
            
            # 2. Call Card Service
            logger.info("Calling Card Service to create cards...")
            response = await self.card_service.create_cards_from_snapshot(
                tenant_id=tenant_id,
                snapshot=normalized_snapshot,
            )
            
            logger.info(f"Card Service returned {len(response.get('cards', []))} cards")
            
            # 3. Return response
            return {
                "status": "success",
                "snapshot_id": str(snapshot.snapshot_id),
                "cards": response.get("cards", []),
                "message": f"Successfully created {len(response.get('cards', []))} cards",
            }
        
        except Exception as e:
            logger.error(f"Failed to export snapshot: {str(e)}", exc_info=True)
            raise Exception(f"Card export failed: {str(e)}")
    
    def _normalize_snapshot(self, snapshot: CompanySnapshot) -> Dict[str, Any]:
        """
        Normalize CompanySnapshot for Card Service API.

        Converts Pydantic model to dict with proper structure and serializes datetime objects.

        Args:
            snapshot: CompanySnapshot to normalize

        Returns:
            Dict with normalized snapshot data
        """
        # Use model_dump with mode='json' to properly serialize datetime objects
        snapshot_dict = snapshot.model_dump(mode='json')

        return {
            "version": snapshot_dict.get("version", "1.0"),
            "snapshot_id": snapshot_dict.get("snapshot_id"),
            "generated_at": snapshot_dict.get("generated_at"),
            "trace_id": snapshot_dict.get("trace_id"),
            "company": snapshot_dict.get("company", {}),
            "audience": snapshot_dict.get("audience", {}),
            "voice": snapshot_dict.get("voice", {}),
            "insights": snapshot_dict.get("insights", {}),
            "clarifying_questions": snapshot_dict.get("clarifying_questions", []),
            "clarifying_answers": snapshot_dict.get("clarifying_answers", {}),
            "source_metadata": snapshot_dict.get("source_metadata", []),
        }

