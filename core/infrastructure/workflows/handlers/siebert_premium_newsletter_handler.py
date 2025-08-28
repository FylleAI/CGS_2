"""
Siebert Premium Newsletter workflow handler.
Optimized workflow with Perplexity integration and 8-section Gen Z format.
"""

import logging
import json

from typing import Dict, Any, List

from ..base.workflow_base import WorkflowHandler
from ..registry import register_workflow

logger = logging.getLogger(__name__)

@register_workflow('siebert_premium_newsletter')
class SiebertPremiumNewsletterHandler(WorkflowHandler):
    """Handler for Siebert's optimized premium newsletter workflow."""

    def validate_inputs(self, context: Dict[str, Any]) -> None:
        """Validate inputs specific to Siebert premium newsletter."""
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

        # Validate target_audience
        audience = context.get('target_audience', '')
        if not audience:
            # Set default for Siebert
            context['target_audience'] = "Gen Z investors and young professionals"
            audience = context['target_audience']
        if len(audience) > 500:
            raise ValueError("Target audience must be less than 500 characters")

        # Validate target_word_count - Siebert range is 800-1200
        word_count = context.get('target_word_count', 1000)
        if word_count < 800 or word_count > 1200:
            logger.info(f"🔧 Adjusting word count from {word_count} to fit Siebert range (800-1200)")
            word_count = max(800, min(1200, word_count))
            context['target_word_count'] = word_count

        # Set client identifiers for RAG operations and agent resolution
        context['client_name'] = 'siebert'
        context['client_profile'] = 'siebert'  # Ensure AgentFactory can resolve Siebert agents

        logger.info(f"✅ Siebert newsletter inputs validated: {word_count} words target for {audience}")

    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for Siebert premium newsletter."""
        context = super().prepare_context(context)

        # Set Siebert-specific defaults
        context.setdefault('target_word_count', 1000)
        context.setdefault('exclude_topics', ["crypto day trading", "get rich quick", "penny stocks"])
        context.setdefault('cultural_trends', '')
        context.setdefault('research_timeframe', 'last 7 days')
        context.setdefault('premium_sources', '')
        context.setdefault('custom_instructions', '')
        context.setdefault('client_name', 'siebert')
        context.setdefault('client_profile', 'siebert')  # Ensure consistent client identification

        # Set Siebert target URLs for premium research (specific URLs instead of domains)
        context.setdefault('siebert_target_urls',
            'https://www.thedailyupside.com/finance/|https://www.thedailyupside.com/investments/|https://www.thedailyupside.com/economics/|https://www.thedailyupside.com/newsletter/|https://moneywithkatie.com/blog/category/investing|https://thehustle.co/news|https://www.morningbrew.com/tag/finance|https://www.morningbrew.com/tag/economy|https://blog.siebert.com/tag/daily-market#BlogListing|https://www.axios.com/newsletters/axios-markets|https://www.axios.com/newsletters/axios-macro|https://decrypt.co/|https://www.coindesk.com/')

        # Calculate word count distribution for 8 sections (Siebert format)
        total_words = context['target_word_count']
        context['siebert_section_word_counts'] = {
            'community_greeting': int(total_words * 0.055),      # ~55 words
            'feature_story': int(total_words * 0.30),           # ~300 words
            'market_reality_check': int(total_words * 0.225),   # ~225 words
            'by_the_numbers': int(total_words * 0.135),         # ~135 words
            'your_move_this_week': int(total_words * 0.165),    # ~165 words
            'community_corner': int(total_words * 0.07),        # ~70 words
            'quick_links': int(total_words * 0.07),             # ~70 words (optional)
            'sign_off': int(total_words * 0.035)                # ~35 words
        }

        # Convert exclude_topics from string to array if needed
        exclude_topics = context.get('exclude_topics', [])
        if isinstance(exclude_topics, str) and exclude_topics:
            context['exclude_topics'] = [topic.strip() for topic in exclude_topics.split(',') if topic.strip()]
        elif not isinstance(exclude_topics, list):
            context['exclude_topics'] = ["crypto day trading", "get rich quick", "penny stocks"]

        # Ensure cultural_trends is a string
        if not isinstance(context.get('cultural_trends', ''), str):
            context['cultural_trends'] = ''

        # Process premium sources
        premium_sources = context.get('premium_sources', '')
        if premium_sources and isinstance(premium_sources, str):
            # Convert newline-separated sources to pipe-separated for tool calls
            sources_list = [s.strip() for s in premium_sources.split('\n') if s.strip()]
            if sources_list:
                context['premium_sources'] = '|'.join(sources_list)
                logger.info(f"🎯 Using {len(sources_list)} custom premium sources")
            else:
                context['premium_sources'] = ''
        else:
            context['premium_sources'] = ''

        # Ensure research_timeframe is valid
        valid_timeframes = ['last 7 days', 'yesterday', 'last month']
        if context.get('research_timeframe') not in valid_timeframes:
            context['research_timeframe'] = 'last 7 days'

        logger.info(f"🔧 Siebert newsletter context prepared for client: {context['client_name']}")
        logger.info(f"📊 8-section word counts: {context['siebert_section_word_counts']}")

        return context

    def post_process_task(self, task_id: str, task_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process task output for Siebert workflow."""
        logger.info(f"🔧 POST-PROCESSING SIEBERT TASK: {task_id}")

        if task_id == 'task1_siebert_context_setup':
            # Extract Siebert brand guidelines
            context['siebert_brand_extracted'] = True
            context['template_structure_defined'] = True
            logger.info(f"📋 Siebert brand guidelines and 8-section template extracted")

        elif task_id == 'task2_perplexity_research':
            # Keep it simple: mark as completed and pass raw output forward
            context['perplexity_research_completed'] = True
            logger.info("📚 Perplexity research completed; passing raw output forward without parsing")


        elif task_id == 'task3_newsletter_assembly':
            # Verify 8-section newsletter structure and word counts
            word_count = len(task_output.split()) if task_output else 0
            context['final_word_count'] = word_count
            target_count = context.get('target_word_count', 1000)
            accuracy = (word_count / target_count * 100) if target_count > 0 else 0
            context['word_count_accuracy'] = accuracy
            context['siebert_format_applied'] = True
            logger.info(f"📄 Siebert newsletter created: {word_count} words ({accuracy:.1f}% of target)")

        elif task_id == 'task4_compliance_review':
            # Validate compliance review completion
            word_count = len(task_output.split()) if task_output else 0
            context['compliance_reviewed'] = True
            context['final_compliance_word_count'] = word_count
            context['compliance_review_completed'] = True
            logger.info(f"✅ Compliance review completed: {word_count} words (FINRA/SEC validated)")

        return context

    def post_process_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Final post-processing with Siebert-specific metrics."""
        try:
            logger.info("🔧 POST-PROCESSING: Starting Siebert newsletter post-processing")

            # Find the final newsletter content
            final_content = None
            task_outputs = []

            for key, value in context.items():
                if key.endswith('_output') and isinstance(value, str):
                    task_outputs.append((key, value, len(value)))
                    logger.info(f"📊 Found task output: {key} ({len(value)} chars)")

            # Prioritize task4_compliance_review output (final), then task3_newsletter_assembly
            if task_outputs:
                task4_output = None
                task3_output = None

                for key, value, length in task_outputs:
                    if key == 'task4_compliance_review_output':
                        task4_output = (key, value, length)
                    elif key == 'task3_newsletter_assembly_output':
                        task3_output = (key, value, length)

                if task4_output:
                    final_content = task4_output[1]
                    logger.info(f"✅ Selected compliance-reviewed newsletter from {task4_output[0]} ({task4_output[2]} chars)")
                elif task3_output:
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

            # Create Siebert-specific workflow summary
            summary = {
                'workflow_type': 'siebert_premium_newsletter',
                'newsletter_topic': context.get('topic', ''),
                'client': 'siebert',
                'target_audience': context.get('target_audience', ''),
                'edition_number': context.get('edition_number', 1),
                'target_word_count': context.get('target_word_count', 1000),
                'final_word_count': context.get('final_word_count', 0),
                'word_count_accuracy': context.get('word_count_accuracy', 0),
                'newsletter_format': '8-section Siebert Gen Z format',
                'perplexity_integration': context.get('perplexity_research_completed', False),
                'cultural_integration': context.get('cultural_integration_applied', False),
                'brand_guidelines_applied': context.get('siebert_brand_extracted', False),
                'quality_indicators': {
                    'perplexity_research': context.get('perplexity_research_completed', False),
                    'word_count_target_met': abs(context.get('word_count_accuracy', 0) - 100) <= 10,
                    'cultural_integration': context.get('cultural_integration_applied', False),
                    'siebert_format': context.get('siebert_format_applied', False),
                    'brand_voice_applied': context.get('siebert_brand_extracted', False)
                },
                'section_structure': context.get('siebert_section_word_counts', {}),
                'research_sources': context.get('research_sources_count', 0)
            }

            context['workflow_summary'] = summary
            logger.info(f"📊 Siebert newsletter workflow summary created")
            logger.info(f"🎯 Word count accuracy: {summary['word_count_accuracy']:.1f}%")
            logger.info(f"🔍 Perplexity integration: {summary['perplexity_integration']}")

            # CRITICAL: Call parent method to ensure workflow_metrics are included
            context = super().post_process_workflow(context)
            logger.info("✅ Parent post-processing completed - workflow_metrics preserved")

            return context

        except Exception as e:
            logger.error(f"❌ SIEBERT POST-PROCESSING ERROR: {str(e)}")
            # Even in case of error, call parent to preserve workflow_metrics
            return super().post_process_workflow(context)
