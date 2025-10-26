"""
Fylle Shared Enums

LOCKED enums for Fylle microservices.
DO NOT modify without cross-team approval.
"""

from enum import Enum


class CardType(str, Enum):
    """
    Card types for context cards.
    
    v1.0: Only COMPANY, AUDIENCE, VOICE, INSIGHT are active.
    v1.1: Will add PRODUCT, PERSONA, CAMPAIGN, TOPIC.
    
    LOCKED: Do not modify without migration plan.
    """
    COMPANY = "company"
    AUDIENCE = "audience"
    VOICE = "voice"
    INSIGHT = "insight"
    
    # v1.1 (NOT USED IN v1.0 - keep commented):
    # PRODUCT = "product"
    # PERSONA = "persona"
    # CAMPAIGN = "campaign"
    # TOPIC = "topic"


class WorkflowType(str, Enum):
    """
    Workflow types for content generation.
    
    LOCKED: Do not modify without migration plan.
    """
    PREMIUM_NEWSLETTER = "premium_newsletter"
    ONBOARDING_CONTENT = "onboarding_content"
    # Future workflow types can be added here

