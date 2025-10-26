"""Use case for executing complete onboarding workflow."""

import logging
from typing import Optional
from uuid import UUID

from services.onboarding.domain.models import OnboardingSession, SessionState
from services.onboarding.domain.cgs_contracts import ResultEnvelope
from services.onboarding.application.builders.payload_builder import PayloadBuilder
from services.onboarding.infrastructure.adapters.cgs_adapter import CgsAdapter
from services.onboarding.infrastructure.adapters.brevo_adapter import BrevoAdapter
from services.onboarding.infrastructure.repositories.supabase_repository import SupabaseSessionRepository
from services.onboarding.application.pipelines.card_export import (
    CardExportPipeline,
    CardExportResult,
)

logger = logging.getLogger(__name__)


class ExecuteOnboardingUseCase:
    """
    Use case for executing complete onboarding workflow.
    
    Orchestrates: payload building → CGS execution → email delivery → persistence.
    """
    
    def __init__(
        self,
        payload_builder: PayloadBuilder,
        cgs_adapter: CgsAdapter,
        brevo_adapter: Optional[BrevoAdapter] = None,
        repository: Optional[SupabaseSessionRepository] = None,
        auto_delivery: bool = True,
        card_service_client: Optional[object] = None,
        card_export_pipeline: Optional[CardExportPipeline] = None,
    ):
        """
        Initialize use case.

        Args:
            payload_builder: Payload builder
            cgs_adapter: CGS adapter for workflow execution
            brevo_adapter: Optional Brevo adapter for email delivery
            repository: Optional repository for persistence
            auto_delivery: Whether to auto-deliver via email
            card_service_client: Optional Card Service HTTP client for creating cards
        """
        self.payload_builder = payload_builder
        self.cgs = cgs_adapter
        self.brevo = brevo_adapter
        self.repository = repository
        self.auto_delivery = auto_delivery
        self.card_service_client = card_service_client
        self.card_export_pipeline = (
            card_export_pipeline
            if card_export_pipeline is not None
            else (
                CardExportPipeline(card_service_client)
                if card_service_client is not None
                else None
            )
        )
    
    async def execute(
        self,
        session: OnboardingSession,
        dry_run: bool = False,
        requested_provider: Optional[str] = None,
    ) -> ResultEnvelope:
        """
        Execute onboarding workflow.
        
        Args:
            session: OnboardingSession with complete snapshot
            dry_run: Whether to run in dry-run mode
            requested_provider: Optional LLM provider override
        
        Returns:
            ResultEnvelope with execution results
        """
        logger.info(f"Executing onboarding for session: {session.session_id}")
        
        # Validate session state
        if session.state != SessionState.PAYLOAD_READY:
            raise ValueError(f"Invalid state for execution: {session.state}")
        
        if not session.snapshot or not session.snapshot.is_complete():
            raise ValueError("Session snapshot is not complete")
        
        try:
            # Step 1: Build payload
            logger.info("Step 1: Building CGS payload...")
            payload = self.payload_builder.build_payload(
                session_id=session.session_id,
                trace_id=session.trace_id,
                snapshot=session.snapshot,
                goal=session.goal,
                dry_run=dry_run,
                requested_provider=requested_provider,
            )
            
            session.cgs_payload = payload.model_dump(mode="json")
            
            if self.repository:
                await self.repository.save_session(session)
            
            # Step 2: Execute CGS workflow
            logger.info("Step 2: Executing CGS workflow...")
            session.update_state(SessionState.EXECUTING)
            
            if self.repository:
                await self.repository.update_session_state(
                    session.session_id, SessionState.EXECUTING
                )
            
            result = await self.cgs.execute_workflow(payload)
            
            # Store CGS response
            session.cgs_run_id = result.cgs_run_id
            session.cgs_response = result.model_dump(mode="json")

            # Debug: Log the serialized response
            logger.info(f"📦 Serialized CGS response keys: {list(session.cgs_response.keys())}")
            if session.cgs_response.get("content"):
                content_keys = list(session.cgs_response["content"].keys())
                logger.info(f"📦 Content keys: {content_keys}")
                if "metadata" in session.cgs_response["content"]:
                    metadata = session.cgs_response["content"]["metadata"]
                    logger.info(f"📦 Content metadata: {metadata}")

            if self.repository:
                await self.repository.save_session(session)
            
            # Check if successful
            if not result.is_successful():
                error_msg = result.get_error_message() or "CGS execution failed"
                logger.error(f"CGS execution failed: {error_msg}")
                session.mark_failed(error_msg)
                
                if self.repository:
                    await self.repository.update_session_state(
                        session.session_id, SessionState.FAILED, error_msg
                    )
                
                return result
            
            logger.info(f"CGS execution successful: run_id={result.cgs_run_id}")

            # Step 3: Create atomic cards from snapshot (if Card Service is available)
            card_ids = []
            if self.card_export_pipeline and session.snapshot:
                logger.info("Step 3: Creating atomic cards from snapshot...")
                try:
                    export_result: CardExportResult = await self.card_export_pipeline.export(
                        session=session
                    )
                    card_ids = [str(summary.id) for summary in export_result.cards]

                    logger.info(f"✨ Created {len(card_ids)} cards: {card_ids}")

                    # Store card metadata for later retrieval
                    session.metadata["card_ids"] = card_ids
                    session.metadata["card_context"] = export_result.context.to_dict()

                    if self.repository:
                        await self.repository.save_session(session)

                except Exception as e:
                    logger.warning(f"Card creation failed (non-blocking): {str(e)}")
                    session.metadata["card_creation_error"] = str(e)
            else:
                logger.info("Step 3: Skipping card creation (Card Service not configured)")

            # Step 4: Deliver via email (if configured and enabled)
            if self.auto_delivery and self.brevo and session.user_email and result.content:
                logger.info("Step 4: Delivering content via email...")
                session.update_state(SessionState.DELIVERING)
                
                if self.repository:
                    await self.repository.update_session_state(
                        session.session_id, SessionState.DELIVERING
                    )
                
                try:
                    delivery_result = await self.brevo.send_content_email(
                        recipient_email=session.user_email,
                        recipient_name=None,
                        content=result.content,
                        session_id=str(session.session_id),
                        brand_name=session.brand_name,
                    )
                    
                    session.delivery_status = delivery_result["status"]
                    session.delivery_message_id = delivery_result["message_id"]
                    session.delivery_timestamp = delivery_result["timestamp"]
                    
                    logger.info(
                        f"Email delivered: message_id={delivery_result['message_id']}"
                    )
                    
                except Exception as e:
                    logger.error(f"Email delivery failed: {str(e)}")
                    # Don't fail the whole workflow for email issues
                    session.delivery_status = "failed"
                    session.error_message = f"Email delivery failed: {str(e)}"
            else:
                logger.info("Step 4: Skipping email delivery (not configured or disabled)")

            # Step 5: Mark as done
            session.update_state(SessionState.DONE)
            
            if self.repository:
                await self.repository.save_session(session)
            
            logger.info(f"Onboarding completed successfully: {session.session_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Onboarding execution failed: {str(e)}")
            session.mark_failed(str(e))
            
            if self.repository:
                await self.repository.update_session_state(
                    session.session_id, SessionState.FAILED, str(e)
                )
            
            raise

