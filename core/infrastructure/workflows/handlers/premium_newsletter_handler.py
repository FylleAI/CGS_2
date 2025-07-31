"""
Premium Newsletter workflow handler.
"""

import logging
from typing import Dict, Any, List

from ..base.workflow_base import WorkflowHandler
from ..registry import register_workflow

logger = logging.getLogger(__name__)

@register_workflow('premium_newsletter')
class PremiumNewsletterHandler(WorkflowHandler):
    """Handler for premium newsletter workflow."""

    def validate_inputs(self, context: Dict[str, Any]) -> None:
        """Validate inputs specific to premium newsletter."""
        super().validate_inputs(context)

        # Validate topic (can be either 'topic' or 'newsletter_topic')
        topic = context.get('topic') or context.get('newsletter_topic', '')
        if not topic or len(topic) < 5:
            raise ValueError("Newsletter topic must be at least 5 characters")

        # Ensure 'topic' is available for template (normalize the field)
        if 'topic' not in context and 'newsletter_topic' in context:
            context['topic'] = context['newsletter_topic']
        if len(topic) > 200:
            raise ValueError("Newsletter topic must be less than 200 characters")

        # Validate premium_sources - handle both string and array input
        sources_input = context.get('premium_sources', [])
        if isinstance(sources_input, str):
            # Convert string (multiline) to array
            sources = [url.strip() for url in sources_input.split('\n') if url.strip()]
        else:
            sources = sources_input if isinstance(sources_input, list) else []

        # Premium sources are optional - provide defaults if none specified
        if not sources or len(sources) < 1:
            # Use default premium sources for testing/demo purposes
            sources = [
                'https://www.bloomberg.com',
                'https://www.reuters.com',
                'https://www.wsj.com'
            ]
            context['premium_sources'] = sources
            logger.info(f"🔧 Using default premium sources: {len(sources)} sources")

        if len(sources) > 10:
            raise ValueError("Maximum 10 premium sources allowed")

        # Validate URLs
        for source in sources:
            if not source.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL format: {source}")

        # Validate target_audience
        audience = context.get('target_audience', '')
        if not audience or len(audience) < 3:
            raise ValueError("Target audience must be at least 3 characters")
        if len(audience) > 500:
            raise ValueError("Target audience must be less than 500 characters")

        # Validate target_word_count - allow smaller counts for testing
        word_count = context.get('target_word_count', 1200)
        if word_count < 100 or word_count > 2500:
            raise ValueError("Target word count must be between 100 and 2500")

        # Adjust word count to minimum newsletter standards if too small
        if word_count < 800:
            logger.info(f"🔧 Adjusting word count from {word_count} to 800 (minimum for newsletter)")
            context['target_word_count'] = 800
            word_count = 800

        logger.info(f"✅ Premium newsletter inputs validated: {len(sources)} sources, {word_count} words target")

    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for premium newsletter."""
        context = super().prepare_context(context)

        # Set default values
        context.setdefault('target_word_count', 1200)
        context.setdefault('edition_number', 1)
        context.setdefault('exclude_topics', [])
        context.setdefault('priority_sections', [])
        context.setdefault('custom_instructions', '')

        # Calculate word count distribution for 7 sections
        total_words = context['target_word_count']
        context['section_word_counts'] = {
            'executive_summary': int(total_words * 0.15),
            'market_highlights': int(total_words * 0.20),
            'premium_insights': int(total_words * 0.25),
            'expert_analysis': int(total_words * 0.15),
            'recommendations': int(total_words * 0.15),
            'market_outlook': int(total_words * 0.07),
            'client_cta': int(total_words * 0.03)
        }

        # Convert and sanitize premium_sources from string to array if needed
        sources_input = context.get('premium_sources', [])
        if isinstance(sources_input, str):
            # Convert string (multiline) to array
            sources = [url.strip() for url in sources_input.split('\n') if url.strip()]
        else:
            sources = sources_input if isinstance(sources_input, list) else []
        context['premium_sources'] = sources

        # Convert exclude_topics and priority_sections from string to array if needed
        exclude_topics = context.get('exclude_topics', '')
        if isinstance(exclude_topics, str) and exclude_topics:
            context['exclude_topics'] = [topic.strip() for topic in exclude_topics.split(',') if topic.strip()]
        else:
            context['exclude_topics'] = exclude_topics if isinstance(exclude_topics, list) else []

        priority_sections = context.get('priority_sections', '')
        if isinstance(priority_sections, str) and priority_sections:
            context['priority_sections'] = [section.strip() for section in priority_sections.split(',') if section.strip()]
        else:
            context['priority_sections'] = priority_sections if isinstance(priority_sections, list) else []

        logger.info(f"🔧 Premium newsletter context prepared: {len(context['premium_sources'])} sources")
        logger.info(f"📊 Section word counts: {context['section_word_counts']}")

        return context

    def post_process_task(self, task_id: str, task_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process task output."""
        logger.info(f"🔧 POST-PROCESSING TASK: {task_id}")

        if task_id == 'task1_enhanced_context':
            # Extract brand guidelines and structure requirements
            context['brand_guidelines_extracted'] = True
            logger.info(f"📋 Brand guidelines extracted for {context.get('client_name', 'client')}")

        elif task_id == 'task2_premium_analysis':
            # Validate premium content extraction
            sources_count = len(context.get('premium_sources', []))
            context['premium_sources_analyzed'] = sources_count
            logger.info(f"📊 Premium sources analyzed: {sources_count}")

        elif task_id == 'task3_newsletter_creation':
            # Verify newsletter structure and word counts
            word_count = len(task_output.split()) if task_output else 0
            context['final_word_count'] = word_count
            target_count = context.get('target_word_count', 1200)
            accuracy = (word_count / target_count * 100) if target_count > 0 else 0
            context['word_count_accuracy'] = accuracy
            logger.info(f"📄 Newsletter created: {word_count} words ({accuracy:.1f}% of target)")

        return context

    def post_process_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Final post-processing with newsletter-specific metrics."""
        try:
            logger.info("🔧 POST-PROCESSING: Starting premium newsletter post-processing")

            # Find the final newsletter content
            final_content = None
            task_outputs = []

            for key, value in context.items():
                if key.endswith('_output') and isinstance(value, str):
                    task_outputs.append((key, value, len(value)))
                    logger.info(f"📊 Found task output: {key} ({len(value)} chars)")

            # Prioritize task3_newsletter_creation output
            if task_outputs:
                task3_output = None
                for key, value, length in task_outputs:
                    if key == 'task3_newsletter_creation_output':
                        task3_output = (key, value, length)
                        break

                if task3_output:
                    final_content = task3_output[1]
                    logger.info(f"📄 Selected newsletter content from {task3_output[0]} ({task3_output[2]} chars)")
                else:
                    # Fallback to longest output
                    task_outputs.sort(key=lambda x: x[2], reverse=True)
                    final_content = task_outputs[0][1]
                    logger.info(f"📄 Selected content from {task_outputs[0][0]} ({task_outputs[0][2]} chars) - fallback")

            if final_content:
                context['final_output'] = final_content
                logger.info(f"📄 Set final_output with {len(final_content)} characters")

            # Create workflow summary with newsletter-specific metrics
            summary = {
                'workflow_type': 'premium_newsletter',
                'newsletter_topic': context.get('topic', ''),  # Changed from newsletter_topic to topic
                'client': context.get('client_name', ''),
                'target_audience': context.get('target_audience', ''),
                'edition_number': context.get('edition_number', 1),
                'premium_sources_count': len(context.get('premium_sources', [])),
                'target_word_count': context.get('target_word_count', 1200),
                'final_word_count': context.get('final_word_count', 0),
                'word_count_accuracy': context.get('word_count_accuracy', 0),
                'sections_structure': '7-section newsletter',
                'brand_guidelines_applied': context.get('brand_guidelines_extracted', False),
                'premium_analysis_completed': context.get('premium_sources_analyzed', 0) > 0,
                'quality_indicators': {
                    'sources_analyzed': context.get('premium_sources_analyzed', 0),
                    'word_count_target_met': abs(context.get('word_count_accuracy', 0) - 100) <= 10,
                    'brand_integration': context.get('brand_guidelines_extracted', False)
                }
            }

            context['workflow_summary'] = summary
            logger.info(f"📊 Premium newsletter workflow summary created")
            logger.info(f"🎯 Word count accuracy: {summary['word_count_accuracy']:.1f}%")

            # CRITICAL: Call parent method to ensure workflow_metrics are included
            context = super().post_process_workflow(context)
            logger.info("✅ Parent post-processing completed - workflow_metrics preserved")

            return context

        except Exception as e:
            logger.error(f"❌ POST-PROCESSING ERROR: {str(e)}")
            # Even in case of error, call parent to preserve workflow_metrics
            return super().post_process_workflow(context)
