# 📋 Card Models - Pydantic + TypeScript

**Data**: 2025-10-25  
**Scope**: Definizione completa dei 4 card types

---

## 🐍 PYDANTIC MODELS (Backend)

### File: `core/card_service/domain/card_entity.py`

```python
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# ============================================================================
# ENUMS
# ============================================================================

class CardType(str, Enum):
    PRODUCT = "product"
    PERSONA = "persona"
    CAMPAIGN = "campaign"
    TOPIC = "topic"

class RelationshipType(str, Enum):
    LINKS_TO = "links_to"
    TARGETS = "targets"
    FEATURES = "features"
    DERIVES_FROM = "derives_from"
    SUPPORTS = "supports"

# ============================================================================
# VALUE OBJECTS
# ============================================================================

class ProductContent(BaseModel):
    value_proposition: str = Field(..., min_length=10, max_length=500)
    features: List[str] = Field(..., min_items=1, max_items=10)
    differentiators: List[str] = Field(..., min_items=1, max_items=5)
    use_cases: List[str] = Field(..., min_items=1, max_items=10)
    target_market: str = Field(..., min_length=5, max_length=200)

class PersonaContent(BaseModel):
    icp_profile: str = Field(..., min_length=10, max_length=500)
    pain_points: List[str] = Field(..., min_items=1, max_items=10)
    goals: List[str] = Field(..., min_items=1, max_items=10)
    preferred_language: str = Field(default="English")
    communication_channels: List[str] = Field(..., min_items=1, max_items=5)
    demographics: Optional[Dict[str, Any]] = None
    psychographics: Optional[Dict[str, Any]] = None

class CampaignContent(BaseModel):
    objective: str = Field(..., min_length=10, max_length=500)
    key_messages: List[str] = Field(..., min_items=1, max_items=5)
    tone: str = Field(..., min_length=3, max_length=50)
    target_personas: List[str] = Field(default_factory=list)
    assets_produced: List[str] = Field(default_factory=list)
    results: Optional[str] = None
    learnings: Optional[str] = None

class TopicContent(BaseModel):
    keywords: List[str] = Field(..., min_items=1, max_items=20)
    angles: List[str] = Field(..., min_items=1, max_items=10)
    related_content: List[str] = Field(default_factory=list)
    trend_status: str = Field(..., regex="^(emerging|stable|declining)$")
    frequency: str = Field(default="weekly")
    audience_interest: str = Field(default="high")

# ============================================================================
# BASE CARD
# ============================================================================

class BaseCard(BaseModel):
    id: UUID
    tenant_id: UUID
    card_type: CardType
    title: str = Field(..., min_length=3, max_length=500)
    content: Dict[str, Any]  # Flexible per tipo
    metrics: Dict[str, Any] = Field(default_factory=dict)
    version: int = Field(default=1, ge=1)
    is_active: bool = Field(default=True)
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
                "card_type": "product",
                "title": "Enterprise CRM",
                "content": {...},
                "version": 1,
                "is_active": True,
                "created_at": "2025-10-25T10:00:00Z",
                "updated_at": "2025-10-25T10:00:00Z"
            }
        }

# ============================================================================
# SPECIALIZED CARDS
# ============================================================================

class ProductCard(BaseCard):
    card_type: CardType = CardType.PRODUCT
    content: ProductContent

class PersonaCard(BaseCard):
    card_type: CardType = CardType.PERSONA
    content: PersonaContent

class CampaignCard(BaseCard):
    card_type: CardType = CardType.CAMPAIGN
    content: CampaignContent

class TopicCard(BaseCard):
    card_type: CardType = CardType.TOPIC
    content: TopicContent

# ============================================================================
# RELATIONSHIPS
# ============================================================================

class CardRelationship(BaseModel):
    id: UUID
    source_card_id: UUID
    target_card_id: UUID
    relationship_type: RelationshipType
    strength: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime

# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class CreateCardRequest(BaseModel):
    card_type: CardType
    title: str
    content: Dict[str, Any]
    metrics: Optional[Dict[str, Any]] = None

class UpdateCardRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None

class CardResponse(BaseModel):
    id: UUID
    card_type: CardType
    title: str
    content: Dict[str, Any]
    metrics: Dict[str, Any]
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    relationships: List[CardRelationship] = Field(default_factory=list)

class ListCardsResponse(BaseModel):
    items: List[CardResponse]
    total: int
    page: int
    page_size: int
```

---

## 📘 TYPESCRIPT TYPES (Frontend)

### File: `onboarding-frontend/src/types/card.ts`

```typescript
// ============================================================================
// ENUMS
// ============================================================================

export enum CardType {
  PRODUCT = 'product',
  PERSONA = 'persona',
  CAMPAIGN = 'campaign',
  TOPIC = 'topic'
}

export enum RelationshipType {
  LINKS_TO = 'links_to',
  TARGETS = 'targets',
  FEATURES = 'features',
  DERIVES_FROM = 'derives_from',
  SUPPORTS = 'supports'
}

// ============================================================================
// VALUE OBJECTS
// ============================================================================

export interface ProductContent {
  value_proposition: string;
  features: string[];
  differentiators: string[];
  use_cases: string[];
  target_market: string;
}

export interface PersonaContent {
  icp_profile: string;
  pain_points: string[];
  goals: string[];
  preferred_language: string;
  communication_channels: string[];
  demographics?: Record<string, any>;
  psychographics?: Record<string, any>;
}

export interface CampaignContent {
  objective: string;
  key_messages: string[];
  tone: string;
  target_personas: string[];
  assets_produced: string[];
  results?: string;
  learnings?: string;
}

export interface TopicContent {
  keywords: string[];
  angles: string[];
  related_content: string[];
  trend_status: 'emerging' | 'stable' | 'declining';
  frequency: string;
  audience_interest: string;
}

// ============================================================================
// BASE CARD
// ============================================================================

export interface BaseCard {
  id: string;
  tenant_id: string;
  card_type: CardType;
  title: string;
  content: Record<string, any>;
  metrics: Record<string, any>;
  version: number;
  is_active: boolean;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// SPECIALIZED CARDS
// ============================================================================

export interface ProductCard extends BaseCard {
  card_type: CardType.PRODUCT;
  content: ProductContent;
}

export interface PersonaCard extends BaseCard {
  card_type: CardType.PERSONA;
  content: PersonaContent;
}

export interface CampaignCard extends BaseCard {
  card_type: CardType.CAMPAIGN;
  content: CampaignContent;
}

export interface TopicCard extends BaseCard {
  card_type: CardType.TOPIC;
  content: TopicContent;
}

export type Card = ProductCard | PersonaCard | CampaignCard | TopicCard;

// ============================================================================
// RELATIONSHIPS
// ============================================================================

export interface CardRelationship {
  id: string;
  source_card_id: string;
  target_card_id: string;
  relationship_type: RelationshipType;
  strength: number;
  created_at: string;
}

// ============================================================================
// REQUEST/RESPONSE
// ============================================================================

export interface CreateCardRequest {
  card_type: CardType;
  title: string;
  content: Record<string, any>;
  metrics?: Record<string, any>;
}

export interface UpdateCardRequest {
  title?: string;
  content?: Record<string, any>;
  metrics?: Record<string, any>;
}

export interface CardResponse {
  id: string;
  card_type: CardType;
  title: string;
  content: Record<string, any>;
  metrics: Record<string, any>;
  version: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  relationships: CardRelationship[];
}

export interface ListCardsResponse {
  items: CardResponse[];
  total: number;
  page: number;
  page_size: number;
}

// ============================================================================
// ZODSCHEMAS (Validation)
// ============================================================================

import { z } from 'zod';

export const ProductContentSchema = z.object({
  value_proposition: z.string().min(10).max(500),
  features: z.array(z.string()).min(1).max(10),
  differentiators: z.array(z.string()).min(1).max(5),
  use_cases: z.array(z.string()).min(1).max(10),
  target_market: z.string().min(5).max(200)
});

export const PersonaContentSchema = z.object({
  icp_profile: z.string().min(10).max(500),
  pain_points: z.array(z.string()).min(1).max(10),
  goals: z.array(z.string()).min(1).max(10),
  preferred_language: z.string().default('English'),
  communication_channels: z.array(z.string()).min(1).max(5),
  demographics: z.record(z.any()).optional(),
  psychographics: z.record(z.any()).optional()
});

export const CampaignContentSchema = z.object({
  objective: z.string().min(10).max(500),
  key_messages: z.array(z.string()).min(1).max(5),
  tone: z.string().min(3).max(50),
  target_personas: z.array(z.string()).default([]),
  assets_produced: z.array(z.string()).default([]),
  results: z.string().optional(),
  learnings: z.string().optional()
});

export const TopicContentSchema = z.object({
  keywords: z.array(z.string()).min(1).max(20),
  angles: z.array(z.string()).min(1).max(10),
  related_content: z.array(z.string()).default([]),
  trend_status: z.enum(['emerging', 'stable', 'declining']),
  frequency: z.string().default('weekly'),
  audience_interest: z.string().default('high')
});

export const CreateCardRequestSchema = z.object({
  card_type: z.nativeEnum(CardType),
  title: z.string().min(3).max(500),
  content: z.record(z.any()),
  metrics: z.record(z.any()).optional()
});
```

---

## 🔄 CONVERSIONE SNAPSHOT → CARD

### Mapping Logic

```python
# core/card_service/application/create_cards_from_snapshot_use_case.py

async def execute(self, snapshot: CompanySnapshot, tenant_id: UUID):
    """Convert CompanySnapshot to 4 atomic cards"""
    
    cards = []
    
    # 1. ProductCard
    product_card = ProductCard(
        id=uuid4(),
        tenant_id=tenant_id,
        title=snapshot.company.name,
        content=ProductContent(
            value_proposition=snapshot.company.description,
            features=snapshot.company.key_offerings,
            differentiators=snapshot.company.differentiators,
            use_cases=[],  # From insights
            target_market=snapshot.audience.primary
        )
    )
    cards.append(product_card)
    
    # 2. PersonaCard
    persona_card = PersonaCard(
        id=uuid4(),
        tenant_id=tenant_id,
        title=f"Target: {snapshot.audience.primary}",
        content=PersonaContent(
            icp_profile=snapshot.audience.primary,
            pain_points=snapshot.audience.pain_points,
            goals=[],
            preferred_language="English",
            communication_channels=[]
        )
    )
    cards.append(persona_card)
    
    # 3. CampaignCard
    campaign_card = CampaignCard(
        id=uuid4(),
        tenant_id=tenant_id,
        title="Onboarding Campaign",
        content=CampaignContent(
            objective="Establish brand presence",
            key_messages=snapshot.voice.style_guidelines,
            tone=snapshot.voice.tone,
            target_personas=[persona_card.id],
            assets_produced=[]
        )
    )
    cards.append(campaign_card)
    
    # 4. TopicCard
    topic_card = TopicCard(
        id=uuid4(),
        tenant_id=tenant_id,
        title="Core Topics",
        content=TopicContent(
            keywords=[],
            angles=[],
            related_content=[],
            trend_status="stable",
            frequency="weekly"
        )
    )
    cards.append(topic_card)
    
    # Save all cards
    for card in cards:
        await self.card_repository.create(card)
    
    # Link cards
    await self._link_cards(cards)
    
    return cards
```


