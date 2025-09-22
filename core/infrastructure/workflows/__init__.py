"""
Dynamic workflow system for CGSRef.

This module provides a flexible, dynamic workflow system that allows:
- Creating new workflows without modifying core code
- Dynamic variable handling from frontend forms
- Template-based task descriptions with variable substitution
- Workflow-specific business logic in handlers
"""

# Import handlers to register them automatically
from .handlers.enhanced_article_handler import EnhancedArticleHandler
from .handlers.enhanced_article_with_image_handler import EnhancedArticleWithImageHandler
from .handlers.premium_newsletter_handler import PremiumNewsletterHandler
from .handlers.siebert_premium_newsletter_handler import SiebertPremiumNewsletterHandler
from .registry import workflow_registry, execute_dynamic_workflow, list_available_workflows

__all__ = [
    'EnhancedArticleHandler',
    'EnhancedArticleWithImageHandler',
    'PremiumNewsletterHandler',
    'SiebertPremiumNewsletterHandler',
    'workflow_registry',
    'execute_dynamic_workflow',
    'list_available_workflows'
]
