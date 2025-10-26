"""
Card Service Domain - Card Types and Enums
"""

from enum import Enum
from typing import Literal


class CardType(str, Enum):
    """Enum for card types"""
    PRODUCT = "product"
    PERSONA = "persona"
    CAMPAIGN = "campaign"
    TOPIC = "topic"


class RelationshipType(str, Enum):
    """Enum for relationship types between cards"""
    TARGETS = "targets"  # ProductCard targets PersonaCard
    PROMOTED_IN = "promoted_in"  # ProductCard promoted in CampaignCard
    IS_TARGET_OF = "is_target_of"  # PersonaCard is target of CampaignCard
    DISCUSSES = "discusses"  # CampaignCard discusses TopicCard
    LINKS_TO = "links_to"  # Generic link
    DERIVES_FROM = "derives_from"  # Derives from another card
    SUPPORTS = "supports"  # Supports another card


# Type aliases for content fields
ProductCardType = Literal["product"]
PersonaCardType = Literal["persona"]
CampaignCardType = Literal["campaign"]
TopicCardType = Literal["topic"]

