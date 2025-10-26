"""
Fylle Shared Mappings

LOCKED mappings for Fylle microservices.
DO NOT modify without cross-team approval.
"""

from fylle_shared.enums import CardType


# Mapping: CompanySnapshot fields → CardType
# Used by Onboarding service to create cards from snapshot
SNAPSHOT_TO_CARD_MAPPING = {
    "company": CardType.COMPANY,
    "audience": CardType.AUDIENCE,
    "voice": CardType.VOICE,
    "insights": CardType.INSIGHT,
}

