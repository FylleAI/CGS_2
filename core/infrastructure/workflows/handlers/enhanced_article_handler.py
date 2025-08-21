"""
Enhanced Article workflow handler with dynamic context support.
"""

import logging
from typing import Dict, Any

from ..base.workflow_base import WorkflowHandler
from ..registry import register_workflow

logger = logging.getLogger(__name__)


@register_workflow('enhanced_article')
class EnhancedArticleHandler(WorkflowHandler):
    """
    Handler for enhanced article generation workflow.
    
    This workflow creates high-quality articles through:
    1. Brief creation with client knowledge base
    2. Web research and data gathering
    3. Final content creation with brand voice
    """
    
    def validate_inputs(self, context: Dict[str, Any]) -> None:
        """
        Validate inputs specific to enhanced article workflow.
        
        Args:
            context: Input context to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Call parent validation first
        super().validate_inputs(context)
        
        # Enhanced article specific validations
        topic = context.get('topic', '')
        if len(topic) < 3:
            raise ValueError("Topic must be at least 3 characters long")
        
        client_name = context.get('client_name', '')
        if not client_name:
            raise ValueError("Client name is required for brand voice and guidelines")
        
        # Validate word count if provided
        target_word_count = context.get('target_word_count')
        if target_word_count is not None:
            try:
                word_count = int(target_word_count)
                if word_count < 50:
                    raise ValueError("Target word count must be at least 50 words")
                if word_count > 5000:
                    raise ValueError("Target word count cannot exceed 5000 words")
            except (ValueError, TypeError):
                raise ValueError("Target word count must be a valid number")
        
        logger.info("✅ Enhanced article input validation passed")
    
    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare context specific to enhanced article workflow.
        
        Args:
            context: Input context
            
        Returns:
            Enhanced context with article-specific preparations
        """
        # Call parent preparation
        context = super().prepare_context(context)
        
        # Set defaults for enhanced article
        context.setdefault('target_audience', 'general')
        context.setdefault('tone', 'professional')
        context.setdefault('target_word_count', 500)
        context.setdefault('include_statistics', False)
        context.setdefault('include_examples', False)
        context.setdefault('include_sources', True)
        
        # Enhanced article specific logic
        topic = context.get('topic', '')
        target_audience = context.get('target_audience', '')
        
        # Adjust tone based on target audience
        if 'gen z' in target_audience.lower() or 'young' in target_audience.lower():
            if context.get('tone') == 'professional':
                context['tone'] = 'conversational'
                logger.info("🎯 Adjusted tone to 'conversational' for young audience")
        
        # Adjust content requirements based on topic
        if any(keyword in topic.lower() for keyword in ['finance', 'investment', 'market', 'trading']):
            context['include_statistics'] = True
            context['financial_content'] = True
            logger.info("💰 Enabled statistics for financial content")
        
        if any(keyword in topic.lower() for keyword in ['technology', 'ai', 'software', 'digital']):
            context['include_examples'] = True
            context['tech_content'] = True
            logger.info("💻 Enabled examples for technology content")
        
        # Set content complexity based on word count
        word_count = context.get('target_word_count', 500)
        if word_count < 300:
            context['content_complexity'] = 'simple'
        elif word_count < 800:
            context['content_complexity'] = 'medium'
        else:
            context['content_complexity'] = 'detailed'
        
        # Add workflow-specific metadata
        context['workflow_stage'] = 'preparation'
        context['content_type'] = 'enhanced_article'
        context['requires_research'] = True
        context['requires_brand_alignment'] = True
        
        logger.info(f"🔧 Enhanced article context prepared for topic: {topic}")
        logger.debug(f"📊 Context complexity: {context.get('content_complexity')}")
        
        return context
    
    def should_skip_task(self, task_id: str, context: Dict[str, Any]) -> bool:
        """
        Determine if a task should be skipped based on context.
        
        Args:
            task_id: ID of the task to check
            context: Current context
            
        Returns:
            True if task should be skipped
        """
        # For enhanced article, we generally don't skip tasks
        # But we could add conditional logic here
        
        # Example: Skip research if topic is very simple
        if task_id == 'task2_research':
            topic = context.get('topic', '').lower()
            if len(topic) < 10 and context.get('content_complexity') == 'simple':
                logger.info("⏭️ Skipping research for simple topic")
                return True
        
        return False
    
    def post_process_task(self, task_id: str, task_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process task output for enhanced article workflow.
        
        Args:
            task_id: ID of the completed task
            task_output: Output from the task
            context: Current context
            
        Returns:
            Updated context
        """
        if task_id == 'task1_brief':
            # Extract key information from brief
            context['brief_created'] = True
            context['workflow_stage'] = 'research'
            
            # Analyze brief for additional context
            if 'statistics' in task_output.lower() or 'data' in task_output.lower():
                context['research_focus_data'] = True
            
            if 'examples' in task_output.lower() or 'case study' in task_output.lower():
                context['research_focus_examples'] = True
            
            logger.info("📋 Brief creation completed, context enhanced")
        
        elif task_id == 'task2_research':
            # Extract insights from research
            context['research_completed'] = True
            context['workflow_stage'] = 'content_creation'
            
            # Analyze research output for content enhancement
            research_length = len(task_output)
            if research_length > 2000:
                context['research_depth'] = 'comprehensive'
            elif research_length > 1000:
                context['research_depth'] = 'moderate'
            else:
                context['research_depth'] = 'basic'
            
            # Check for specific research elements
            if 'trend' in task_output.lower():
                context['includes_trends'] = True
            
            if any(word in task_output.lower() for word in ['statistic', 'data', 'number', '%']):
                context['includes_data'] = True
            
            logger.info(f"🔍 Research completed with {context.get('research_depth')} depth")
        
        elif task_id == 'task3_content':
            # Final content analysis
            context['content_created'] = True
            context['workflow_stage'] = 'completed'
            
            # Analyze final content
            content_length = len(task_output.split())
            context['actual_word_count'] = content_length
            
            target_count = context.get('target_word_count', 500)
            variance = abs(content_length - target_count) / target_count
            
            if variance < 0.1:
                context['word_count_accuracy'] = 'excellent'
            elif variance < 0.2:
                context['word_count_accuracy'] = 'good'
            else:
                context['word_count_accuracy'] = 'needs_adjustment'
            
            logger.info(f"📝 Content created: {content_length} words (target: {target_count})")

        elif task_id == 'task4_compliance_review':
            # Post-process compliance review task
            context['compliance_reviewed'] = True
            context['compliance_timestamp'] = context.get('workflow_id', 'unknown')

            # Analyze compliance review output
            task_output = context.get(f'{task_id}_output', '')
            if task_output:
                context['compliance_review_length'] = len(task_output)
                context['compliance_completed'] = True
                logger.info("🛡️ Compliance review completed successfully")
            else:
                logger.warning("⚠️ Compliance review output is empty")

        return context
    
    def post_process_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Final post-processing for enhanced article workflow.

        Args:
            context: Final context after all tasks

        Returns:
            Final processed context with workflow summary
        """
        try:
            print("🔧 POST-PROCESSING: Starting enhanced article post-processing")
            logger.info("🔧 POST-PROCESSING: Starting enhanced article post-processing")

            # Add workflow completion summary
            context['workflow_completed'] = True
            context['workflow_type'] = 'enhanced_article'
            context['completion_timestamp'] = context.get('workflow_id', 'unknown')

            # Extract final content from the last task (task3_content)
            # The task outputs are stored with UUID keys, so we need to find the right one
            final_content = ''

            # Debug: Log all context keys to understand the structure
            logger.info(f"🔍 DEBUG: All context keys: {list(context.keys())}")

            # First, try to find the content creation task output
            # Look for task outputs that contain substantial content (likely the final article)
            task_outputs = []
            for key, value in context.items():
                if key.endswith('_output') and isinstance(value, str):
                    task_outputs.append((key, value, len(value)))
                    logger.info(f"📊 Found task output: {key} ({len(value)} chars)")
                    # Log a preview of the content
                    preview = value[:100] + "..." if len(value) > 100 else value
                    logger.info(f"📄 Content preview: {preview}")

            # Prioritize task4_compliance_review_output (final compliance-reviewed article) over other outputs
            if task_outputs:
                # First, look for task4_compliance_review_output (final compliance-reviewed article)
                task4_output = None
                task3_output = None

                for key, value, length in task_outputs:
                    if key == 'task4_compliance_review_output':
                        task4_output = (key, value, length)
                        break
                    elif key == 'task3_content_output':
                        task3_output = (key, value, length)

                if task4_output:
                    final_content = task4_output[1]
                    logger.info(f"📄 Selected final content from {task4_output[0]} ({task4_output[2]} chars) - compliance reviewed")
                elif task3_output:
                    final_content = task3_output[1]
                    logger.info(f"📄 Selected final content from {task3_output[0]} ({task3_output[2]} chars) - pre-compliance")
                else:
                    # Fallback: sort by length and take the longest output
                    task_outputs.sort(key=lambda x: x[2], reverse=True)
                    final_content = task_outputs[0][1]
                    logger.info(f"📄 Selected final content from {task_outputs[0][0]} ({task_outputs[0][2]} chars) - fallback")
            else:
                logger.warning("⚠️ No task outputs found in context!")

            # Set the final_output that the use case expects
            context['final_output'] = final_content
            logger.info(f"📄 Set final_output with {len(final_content)} characters")

            # Create workflow summary
            summary = {
                'topic': context.get('topic'),
                'client': context.get('client_name'),
                'target_audience': context.get('target_audience'),
                'word_count': context.get('actual_word_count'),
                'research_depth': context.get('research_depth'),
                'includes_data': context.get('includes_data', False),
                'includes_trends': context.get('includes_trends', False),
                'compliance_reviewed': context.get('compliance_reviewed', False),
                'compliance_completed': context.get('compliance_completed', False)
            }

            context['workflow_summary'] = summary

            logger.info("🎉 Enhanced article workflow completed successfully")
            logger.debug(f"📊 Final summary: {summary}")

            # CRITICAL: Call parent method to ensure workflow_metrics are included
            context = super().post_process_workflow(context)
            logger.info("✅ Parent post-processing completed - workflow_metrics preserved")

            return context

        except Exception as e:
            logger.error(f"❌ POST-PROCESSING ERROR: {str(e)}")
            logger.exception("Full traceback:")
            # Even in case of error, call parent to preserve workflow_metrics
            return super().post_process_workflow(context)
