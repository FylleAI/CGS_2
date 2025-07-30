"""Content generation endpoints."""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel

from core.application.use_cases.generate_content import GenerateContentUseCase
from core.application.dto.content_request import ContentGenerationRequest, ContentGenerationResponse
from core.domain.entities.content import ContentType, ContentFormat
from core.domain.value_objects.provider_config import ProviderConfig, LLMProvider
from core.domain.value_objects.generation_params import GenerationParams
from core.infrastructure.factories.provider_factory import LLMProviderFactory
from core.infrastructure.config.settings import get_settings
from ..dependencies import get_content_use_case

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for API
class ContentGenerationRequestModel(BaseModel):
    """API model for content generation request."""
    topic: str
    content_type: str = "article"
    content_format: str = "markdown"
    client_profile: Optional[str] = None
    workflow_type: Optional[str] = None
    provider: str = "openai"
    model: str = "gpt-4o"
    temperature: float = 0.7

    # Enhanced Article specific parameters
    target_word_count: Optional[int] = None
    target: Optional[str] = None  # Target audience for Enhanced Article
    context: Optional[str] = None  # Additional context
    tone: Optional[str] = "professional"
    include_statistics: bool = True
    include_examples: bool = True

    # Newsletter Premium specific parameters
    newsletter_topic: Optional[str] = None
    edition_number: Optional[int] = None
    featured_sections: Optional[List[str]] = None

    # General parameters
    custom_instructions: str = ""
    target_audience: str = "general"  # Fallback for general use
    include_sources: bool = True

    # Additional frontend parameters (will be ignored if not needed)
    client_name: Optional[str] = None
    brand_voice: Optional[str] = None


class WorkflowMetricsModel(BaseModel):
    """Model for workflow execution metrics."""
    total_cost: float = 0.0
    total_tokens: int = 0
    duration_seconds: float = 0.0
    agents_used: int = 0
    success_rate: float = 1.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tool_calls: int = 0
    llm_calls: int = 0


class ContentGenerationResponseModel(BaseModel):
    """API model for content generation response."""
    content_id: str
    title: str
    body: str
    content_type: str
    content_format: str
    workflow_id: Optional[str] = None
    generation_time_seconds: Optional[float] = None
    word_count: int = 0
    character_count: int = 0
    reading_time_minutes: float = 0.0
    tasks_completed: int = 0
    total_tasks: int = 0
    success: bool = True
    error_message: Optional[str] = None
    warnings: List[str] = []
    metadata: dict = {}
    workflow_metrics: Optional[WorkflowMetricsModel] = None


class ContentListResponseModel(BaseModel):
    """API model for content list response."""
    content_id: str
    title: str
    content_type: str
    status: str
    created_at: str
    word_count: int
    client_profile: Optional[str] = None


@router.post("/generate", response_model=ContentGenerationResponseModel)
async def generate_content(
    request: ContentGenerationRequestModel,
    background_tasks: BackgroundTasks
):
    """
    Generate content based on the provided parameters.
    
    This endpoint orchestrates the entire content generation process,
    from workflow selection to final content creation.
    """
    try:
        logger.info(f"Received content generation request: {request.dict()}")
        logger.info(f"🔧 Requested provider: {request.provider}")

        # Get use case with dynamic provider selection
        use_case = get_content_use_case(provider_type=request.provider)
        logger.info(f"✅ Use case created with provider: {request.provider}")

        # Convert API model to application DTO
        try:
            provider_config = ProviderConfig(
                provider=LLMProvider(request.provider),
                model=request.model,
                temperature=request.temperature
            )
            logger.info("Provider config created successfully")
        except Exception as e:
            logger.error(f"Error creating provider config: {str(e)}")
            raise
        
        # Build generation params based on workflow type
        generation_params_dict = {
            'topic': request.topic,
            'content_type': ContentType(request.content_type),
            'content_format': ContentFormat(request.content_format),
            'target_word_count': request.target_word_count,
            'custom_instructions': request.custom_instructions,
            'target_audience': request.target_audience or request.target,  # Use target if available
            'include_sources': request.include_sources,
            'include_statistics': request.include_statistics
        }

        # Add workflow-specific parameters
        if request.workflow_type == "enhanced_article":
            generation_params_dict.update({
                'target': request.target,
                'context': request.context,
                'tone': request.tone,
                'include_examples': request.include_examples
            })
        elif request.workflow_type == "newsletter_premium":
            generation_params_dict.update({
                'newsletter_topic': request.newsletter_topic,
                'edition_number': request.edition_number,
                'featured_sections': request.featured_sections
            })

        try:
            generation_params = GenerationParams(**generation_params_dict)
            logger.info("Generation params created successfully")
        except Exception as e:
            logger.error(f"Error creating generation params: {str(e)}")
            logger.error(f"Generation params dict: {generation_params_dict}")
            raise

        try:
            content_request = ContentGenerationRequest(
            topic=request.topic,
            content_type=ContentType(request.content_type),
            content_format=ContentFormat(request.content_format),
            client_profile=request.client_profile,
            workflow_type=request.workflow_type,
            provider_config=provider_config,
            generation_params=generation_params,
            custom_instructions=request.custom_instructions,
            context=request.context
        )
            logger.info("Content request created successfully")
        except Exception as e:
            logger.error(f"Error creating content request: {str(e)}")
            raise
        
        # Execute content generation
        logger.info("Starting content generation execution")
        try:
            response = await use_case.execute(content_request)
            logger.info("Content generation completed successfully")
        except Exception as e:
            logger.error(f"Error during content generation: {str(e)}")
            raise
        
        # Convert workflow metrics if present
        workflow_metrics = None
        if response.workflow_metrics:
            workflow_metrics = WorkflowMetricsModel(
                total_cost=response.workflow_metrics.total_cost,
                total_tokens=response.workflow_metrics.total_tokens,
                duration_seconds=response.workflow_metrics.duration_seconds,
                agents_used=response.workflow_metrics.agents_used,
                success_rate=response.workflow_metrics.success_rate,
                tasks_completed=response.workflow_metrics.tasks_completed,
                tasks_failed=response.workflow_metrics.tasks_failed,
                tool_calls=response.workflow_metrics.tool_calls,
                llm_calls=response.workflow_metrics.llm_calls
            )

        # Convert application DTO to API model
        return ContentGenerationResponseModel(
            content_id=str(response.content_id),
            title=response.title,
            body=response.body,
            content_type=response.content_type.value,
            content_format=response.content_format.value,
            workflow_id=str(response.workflow_id) if response.workflow_id else None,
            generation_time_seconds=response.generation_time_seconds,
            word_count=response.word_count,
            character_count=response.character_count,
            reading_time_minutes=response.reading_time_minutes,
            tasks_completed=response.tasks_completed,
            total_tasks=response.total_tasks,
            success=response.success,
            error_message=response.error_message,
            warnings=response.warnings,
            metadata=response.metadata,
            workflow_metrics=workflow_metrics
        )
        
    except ValueError as e:
        logger.error(f"Validation error in content generation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in content generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[ContentListResponseModel])
async def list_content(
    limit: int = 10,
    offset: int = 0,
    content_type: Optional[str] = None,
    client_profile: Optional[str] = None,
    use_case: GenerateContentUseCase = Depends(get_content_use_case)
):
    """
    List generated content with optional filtering.
    """
    try:
        # This would need to be implemented in the use case
        # For now, return empty list
        return []
        
    except Exception as e:
        logger.error(f"Error listing content: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


class ProviderInfo(BaseModel):
    """Information about an LLM provider."""
    name: str
    available: bool
    models: List[str]
    default_model: str


class ProvidersResponse(BaseModel):
    """Response model for available providers."""
    providers: List[ProviderInfo]
    default_provider: str


@router.get("/providers", response_model=ProvidersResponse)
async def get_available_providers():
    """
    Get available LLM providers and their models.

    Returns information about all configured providers,
    their availability status, and supported models.
    """
    try:
        settings = get_settings()
        available_providers = LLMProviderFactory.get_available_providers(settings)
        default_provider = LLMProviderFactory.get_default_provider(settings)

        providers_info = []

        for provider_name in ["openai", "anthropic", "deepseek"]:
            try:
                provider_enum = LLMProvider(provider_name)

                # Create a dummy config to get available models
                dummy_config = ProviderConfig(provider=provider_enum)
                models = dummy_config.get_available_models()
                default_model = dummy_config._get_default_model()

                providers_info.append(ProviderInfo(
                    name=provider_name,
                    available=available_providers.get(provider_name, False),
                    models=models,
                    default_model=default_model
                ))
            except ValueError:
                # Skip invalid provider names
                continue

        return ProvidersResponse(
            providers=providers_info,
            default_provider=default_provider.value
        )

    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get providers: {str(e)}")


@router.get("/{content_id}", response_model=ContentGenerationResponseModel)
async def get_content(
    content_id: UUID,
    use_case: GenerateContentUseCase = Depends(get_content_use_case)
):
    """
    Get specific content by ID.
    """
    try:
        # This would need to be implemented in the use case
        # For now, raise not found
        raise HTTPException(status_code=404, detail="Content not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content {content_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{content_id}")
async def delete_content(
    content_id: UUID,
    use_case: GenerateContentUseCase = Depends(get_content_use_case)
):
    """
    Delete content by ID.
    """
    try:
        # This would need to be implemented in the use case
        # For now, return success
        return {"message": "Content deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting content {content_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{content_id}/export")
async def export_content(
    content_id: UUID,
    format: str = "markdown",
    use_case: GenerateContentUseCase = Depends(get_content_use_case)
):
    """
    Export content in different formats.
    """
    try:
        # This would need to be implemented
        raise HTTPException(status_code=501, detail="Export not implemented yet")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting content {content_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
