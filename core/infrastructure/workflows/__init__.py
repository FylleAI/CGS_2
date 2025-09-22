"""Dynamic workflow system for CGSRef."""

# Import handlers to register them automatically
from .handlers.enhanced_article_handler import EnhancedArticleHandler
from .handlers.premium_newsletter_handler import PremiumNewsletterHandler
from .handlers.siebert_premium_newsletter_handler import SiebertPremiumNewsletterHandler
from .handlers.siebert_newsletter_html_handler import SiebertNewsletterHtmlHandler
from .handlers.reopla_enhanced_article_with_image_handler import ReoplaEnhancedArticleWithImageHandler
from .registry import workflow_registry, execute_dynamic_workflow, list_available_workflows

__all__ = [
    'EnhancedArticleHandler',
    'PremiumNewsletterHandler',
    'SiebertPremiumNewsletterHandler',
    'SiebertNewsletterHtmlHandler',
    'ReoplaEnhancedArticleWithImageHandler',
    'workflow_registry',
    'execute_dynamic_workflow',
    'list_available_workflows'
]
