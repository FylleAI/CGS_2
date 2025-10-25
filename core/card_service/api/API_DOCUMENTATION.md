# Card Service API Documentation

**Base URL**: `/api/v1/cards`

---

## Card CRUD Endpoints

### Create Card
```
POST /api/v1/cards?tenant_id={tenant_id}
```

**Request Body**:
```json
{
  "card_type": "product|persona|campaign|topic",
  "title": "Card Title",
  "content": {
    // Content varies by card type
  },
  "metrics": {},
  "notes": "Optional notes"
}
```

**Response**: `201 Created`
```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "card_type": "product",
  "title": "Card Title",
  "content": {},
  "metrics": {},
  "notes": "",
  "version": 1,
  "is_active": true,
  "created_by": "uuid",
  "updated_by": null,
  "created_at": "2025-10-25T...",
  "updated_at": "2025-10-25T...",
  "relationships": []
}
```

---

### List Cards
```
GET /api/v1/cards?tenant_id={tenant_id}&card_type={type}
```

**Query Parameters**:
- `tenant_id` (required): Tenant identifier
- `card_type` (optional): Filter by type (product, persona, campaign, topic)

**Response**: `200 OK`
```json
[
  { /* CardResponse */ },
  { /* CardResponse */ }
]
```

---

### Get Card
```
GET /api/v1/cards/{card_id}?tenant_id={tenant_id}
```

**Response**: `200 OK`
```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "card_type": "product",
  "title": "Card Title",
  "content": {},
  "metrics": {},
  "notes": "",
  "version": 1,
  "is_active": true,
  "created_by": "uuid",
  "updated_by": null,
  "created_at": "2025-10-25T...",
  "updated_at": "2025-10-25T...",
  "relationships": [
    {
      "id": "uuid",
      "source_card_id": "uuid",
      "target_card_id": "uuid",
      "relationship_type": "targets",
      "strength": 1.0,
      "created_at": "2025-10-25T..."
    }
  ]
}
```

---

### Update Card
```
PATCH /api/v1/cards/{card_id}?tenant_id={tenant_id}
```

**Request Body** (all fields optional):
```json
{
  "title": "New Title",
  "content": {},
  "metrics": {},
  "notes": "Updated notes"
}
```

**Response**: `200 OK` (CardResponse)

---

### Delete Card
```
DELETE /api/v1/cards/{card_id}?tenant_id={tenant_id}
```

**Response**: `204 No Content`

---

## Relationship Endpoints

### Create Relationship
```
POST /api/v1/cards/{source_card_id}/relationships?tenant_id={tenant_id}
```

**Request Body**:
```json
{
  "target_card_id": "uuid",
  "relationship_type": "targets|promoted_in|is_target_of|discusses|links_to|derives_from|supports",
  "strength": 1.0
}
```

**Response**: `201 Created`
```json
{
  "id": "uuid",
  "source_card_id": "uuid",
  "target_card_id": "uuid",
  "relationship_type": "targets",
  "strength": 1.0,
  "created_at": "2025-10-25T..."
}
```

---

### Get Relationships
```
GET /api/v1/cards/{card_id}/relationships?tenant_id={tenant_id}
```

**Response**: `200 OK`
```json
[
  {
    "id": "uuid",
    "source_card_id": "uuid",
    "target_card_id": "uuid",
    "relationship_type": "targets",
    "strength": 1.0,
    "created_at": "2025-10-25T..."
  }
]
```

---

### Delete Relationship
```
DELETE /api/v1/cards/{source_card_id}/relationships/{target_card_id}?tenant_id={tenant_id}
```

**Response**: `204 No Content`

---

## Integration Endpoints

### Create Cards from Snapshot (Onboarding)
```
POST /api/v1/cards/onboarding/create-from-snapshot?tenant_id={tenant_id}
```

**Request Body**:
```json
{
  "company_info": {
    "company_name": "string",
    "value_proposition": "string",
    "features": ["string"],
    "differentiators": ["string"],
    "use_cases": ["string"],
    "target_market": "string"
  },
  "audience_info": {
    "persona_name": "string",
    "icp_profile": "string",
    "pain_points": ["string"],
    "goals": ["string"],
    "preferred_language": "string",
    "communication_channels": ["string"]
  },
  "goal": {
    "campaign_name": "string",
    "objective": "string",
    "key_messages": ["string"],
    "tone": "string",
    "assets_produced": ["string"]
  },
  "insights": {
    "topic_name": "string",
    "keywords": ["string"],
    "angles": ["string"],
    "related_content": ["string"],
    "trend_status": "emerging|stable|declining",
    "frequency": "string",
    "audience_interest": "string"
  }
}
```

**Response**: `201 Created`
```json
[
  { /* ProductCard */ },
  { /* PersonaCard */ },
  { /* CampaignCard */ },
  { /* TopicCard */ }
]
```

---

### Get All Cards for Context (CGS)
```
GET /api/v1/cards/context/all?tenant_id={tenant_id}
```

**Response**: `200 OK`
```json
{
  "product": [{ /* ProductCard */ }],
  "persona": [{ /* PersonaCard */ }],
  "campaign": [{ /* CampaignCard */ }],
  "topic": [{ /* TopicCard */ }]
}
```

---

### Get RAG Context Text (CGS)
```
GET /api/v1/cards/context/rag-text?tenant_id={tenant_id}
```

**Response**: `200 OK`
```json
{
  "context": "## PRODUCTS/SERVICES\n### Product Name\nValue Proposition: ...\n\n## TARGET PERSONAS\n..."
}
```

---

### Get Cards by Type (CGS)
```
GET /api/v1/cards/context/by-type?tenant_id={tenant_id}&card_types=product&card_types=persona
```

**Query Parameters**:
- `tenant_id` (required): Tenant identifier
- `card_types` (optional): List of card types to retrieve

**Response**: `200 OK`
```json
{
  "product": [{ /* ProductCard */ }],
  "persona": [{ /* PersonaCard */ }]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid card type: invalid_type"
}
```

### 404 Not Found
```json
{
  "detail": "Card not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Card Types and Content Schemas

### ProductCard
```json
{
  "value_proposition": "string",
  "features": ["string"],
  "differentiators": ["string"],
  "use_cases": ["string"],
  "target_market": "string"
}
```

### PersonaCard
```json
{
  "icp_profile": "string",
  "pain_points": ["string"],
  "goals": ["string"],
  "preferred_language": "string",
  "communication_channels": ["string"],
  "demographics": {},
  "psychographics": {}
}
```

### CampaignCard
```json
{
  "objective": "string",
  "key_messages": ["string"],
  "tone": "string",
  "target_personas": ["string"],
  "assets_produced": ["string"],
  "results": "string",
  "learnings": "string"
}
```

### TopicCard
```json
{
  "keywords": ["string"],
  "angles": ["string"],
  "related_content": ["string"],
  "trend_status": "emerging|stable|declining",
  "frequency": "string",
  "audience_interest": "string"
}
```

---

## Relationship Types

- `targets` - ProductCard targets PersonaCard
- `promoted_in` - ProductCard promoted in CampaignCard
- `is_target_of` - PersonaCard is target of CampaignCard
- `discusses` - CampaignCard discusses TopicCard
- `links_to` - Generic link
- `derives_from` - Derives from another card
- `supports` - Supports another card

