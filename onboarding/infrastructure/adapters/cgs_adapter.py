"""CGS adapter for workflow execution.

Invokes CGS API to execute content generation workflows.
"""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

import httpx

from onboarding.config.settings import OnboardingSettings
from onboarding.domain.cgs_contracts import (
    CgsPayloadLinkedInPost,
    CgsPayloadNewsletter,
    ResultEnvelope,
    ContentResult,
    WorkflowMetrics,
)

logger = logging.getLogger(__name__)


class CgsAdapter:
    """
    Adapter for CGS API invocation.
    
    Handles HTTP communication with CGS backend for workflow execution.
    """
    
    def __init__(self, settings: OnboardingSettings):
        """
        Initialize CGS adapter.
        
        Args:
            settings: Onboarding settings with CGS configuration
        """
        self.settings = settings
        self.base_url = settings.cgs_api_url
        self.timeout = settings.cgs_api_timeout
        self.api_key = settings.cgs_api_key
        
        logger.info(f"CGS adapter initialized: {self.base_url}")
    
    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for CGS requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def execute_workflow(
        self,
        payload: CgsPayloadLinkedInPost | CgsPayloadNewsletter,
    ) -> ResultEnvelope:
        """
        Execute CGS workflow with payload.
        
        Args:
            payload: CGS payload (LinkedIn post or newsletter)
        
        Returns:
            ResultEnvelope with execution results
        
        Raises:
            httpx.HTTPError: If CGS request fails
            ValueError: If response is invalid
        """
        logger.info(
            f"Executing CGS workflow: {payload.workflow} "
            f"(session: {payload.session_id})"
        )
        
        # Convert payload to CGS API format
        cgs_request = self._convert_to_cgs_request(payload)
        
        endpoint = f"{self.base_url}/api/v1/content/generate"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    endpoint,
                    json=cgs_request,
                    headers=self._build_headers(),
                )
                
                response.raise_for_status()
                data = response.json()
            
            # Convert CGS response to ResultEnvelope
            result = self._convert_to_result_envelope(data, payload)
            
            logger.info(
                f"CGS workflow completed: status={result.status}, "
                f"run_id={result.cgs_run_id}"
            )
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(
                f"CGS request failed: {e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.TimeoutException as e:
            logger.error(f"CGS request timeout after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"CGS workflow execution failed: {str(e)}")
            raise
    
    def _convert_to_cgs_request(
        self,
        payload: Any,  # CgsPayloadOnboardingContent | CgsPayloadLinkedInPost | CgsPayloadNewsletter
    ) -> Dict[str, Any]:
        """
        Convert onboarding payload to CGS API request format.

        Maps onboarding contracts to CGS ContentGenerationRequestModel.
        Includes rich context (company_snapshot + clarifying_answers) for agents.
        """
        # Import here to avoid circular dependency
        from onboarding.domain.cgs_contracts import CgsPayloadOnboardingContent

        # Base request
        request = {
            "workflow_type": payload.workflow,
            "client_profile": payload.input.client_profile,
        }

        # Add provider if specified
        if payload.metadata.requested_provider:
            request["provider"] = payload.metadata.requested_provider
            # Add default model for Gemini
            if payload.metadata.requested_provider == "gemini":
                request["model"] = "gemini-2.5-pro"

        # 🆕 RICH CONTEXT: Add company_snapshot and clarifying_answers
        # This makes the full snapshot available to CGS agents via context
        rich_context = {}

        if payload.company_snapshot:
            rich_context["company_snapshot"] = payload.company_snapshot.model_dump(mode="json")
            logger.info(
                f"📦 Rich context: Including company_snapshot "
                f"(industry={payload.company_snapshot.company.industry}, "
                f"differentiators={len(payload.company_snapshot.company.differentiators)})"
            )

        if payload.clarifying_answers:
            rich_context["clarifying_answers"] = payload.clarifying_answers
            logger.info(
                f"📦 Rich context: Including {len(payload.clarifying_answers)} clarifying answers"
            )

        # 🆕 NEW: Add content_type and content_config for unified onboarding workflow
        if isinstance(payload, CgsPayloadOnboardingContent):
            rich_context["content_type"] = payload.input.content_type
            rich_context["content_config"] = payload.input.content_config
            logger.info(
                f"📦 Rich context: content_type={payload.input.content_type}, "
                f"config={payload.input.content_config}"
            )

        # Add rich context to request
        if rich_context:
            request["context"] = rich_context
        
        # Map based on payload type
        if isinstance(payload, CgsPayloadOnboardingContent):
            # 🆕 NEW: Unified onboarding content payload
            request.update({
                "topic": payload.input.topic,
                "client_name": payload.input.client_name,
                "target_audience": payload.input.target_audience,
                "tone": payload.input.tone,
                "context": payload.input.context,
                "custom_instructions": payload.input.custom_instructions,
            })
            logger.info(
                f"✅ Mapped CgsPayloadOnboardingContent to request "
                f"(content_type={payload.input.content_type})"
            )

        elif isinstance(payload, CgsPayloadLinkedInPost):
            # Legacy LinkedIn post payload
            request.update({
                "topic": payload.input.topic,
                "client_name": payload.input.client_name,
                "target_audience": payload.input.target_audience,
                "tone": payload.input.tone,
                "target_word_count": payload.input.target_word_count,
                "include_statistics": payload.input.include_statistics,
                "include_examples": payload.input.include_examples,
                "include_sources": payload.input.include_sources,
                "context": payload.input.context,
                "custom_instructions": payload.input.custom_instructions or "",  # Convert None to empty string
            })

        elif isinstance(payload, CgsPayloadNewsletter):
            # Legacy newsletter payload
            request.update({
                "topic": payload.input.topic,
                "newsletter_topic": payload.input.newsletter_topic,
                "client_name": payload.input.client_name,
                "target_audience": payload.input.target_audience,
                "target_word_count": payload.input.target_word_count,
                "premium_sources": payload.input.premium_sources,
                "custom_instructions": payload.input.custom_instructions or "",  # Convert None to empty string
            })

        return request
    
    def _convert_to_result_envelope(
        self,
        cgs_response: Dict[str, Any],
        payload: CgsPayloadLinkedInPost | CgsPayloadNewsletter,
    ) -> ResultEnvelope:
        """Convert CGS response to ResultEnvelope."""
        # Determine status
        success = cgs_response.get("success", False)
        status = "completed" if success else "failed"
        
        # Extract content
        content = None
        if success and cgs_response.get("body"):
            content = ContentResult(
                content_id=cgs_response.get("content_id"),
                title=cgs_response.get("title", ""),
                body=cgs_response.get("body", ""),
                format=cgs_response.get("content_format", "markdown"),
                word_count=cgs_response.get("word_count", 0),
                character_count=cgs_response.get("character_count", 0),
                reading_time_minutes=cgs_response.get("reading_time_minutes"),
                metadata=cgs_response.get("metadata", {}),
                generated_image=cgs_response.get("generated_image"),
                image_metadata=cgs_response.get("image_metadata"),
            )
        
        # Extract workflow metrics
        workflow_metrics = None
        if cgs_response.get("workflow_metrics"):
            metrics_data = cgs_response["workflow_metrics"]
            workflow_metrics = WorkflowMetrics(**metrics_data)
        
        # Extract error
        error = None
        if not success:
            error = {
                "message": cgs_response.get("error_message", "Unknown error"),
                "code": "cgs_execution_failed",
                "retryable": False,
            }
        
        return ResultEnvelope(
            session_id=payload.session_id,
            trace_id=payload.trace_id,
            workflow=payload.workflow,
            goal=payload.goal,
            status=status,
            cgs_run_id=cgs_response.get("workflow_id"),
            error=error,
            content=content,
            workflow_metrics=workflow_metrics,
        )
    
    async def health_check(self) -> bool:
        """
        Check if CGS API is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"CGS health check failed: {str(e)}")
            return False

