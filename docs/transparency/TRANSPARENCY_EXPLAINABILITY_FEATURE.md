# 🔍 Transparency & Explainability Feature

**Status**: 📋 Planning  
**Priority**: 🔥 High (Core Differentiator)  
**Owner**: Fylle AI Team  
**Last Updated**: 2025-01-25

---

## 📖 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Strategic Context](#strategic-context)
3. [Current State Analysis](#current-state-analysis)
4. [Architecture Options](#architecture-options)
5. [Implementation Specifications](#implementation-specifications)
6. [Database Schema](#database-schema)
7. [API Design](#api-design)
8. [Frontend Components](#frontend-components)
9. [Roadmap](#roadmap)
10. [Success Metrics](#success-metrics)

---

## 📊 Executive Summary

### **Obiettivo**

Implementare un sistema di **Transparency & Explainability** che permetta agli utenti di:

1. ✅ **VEDERE** cosa il sistema sa di loro (dati, context, insights)
2. ✅ **CAPIRE** come l'AI ha ottenuto queste informazioni (sources, citations, confidence)
3. ✅ **VERIFICARE** l'accuratezza dei dati (evidence, references)
4. ✅ **CORREGGERE** informazioni errate (feedback loop)
5. ✅ **TRACCIARE** come i dati vengono usati dagli agent (usage tracking)

### **Value Proposition**

> **"Fylle non offre solo integrazione AI - offre un modo per chiarire cosa l'AI sta utilizzando come contesto e perché e come."**

### **Differenziazione Competitiva**

| Feature | Competitors | Fylle |
|---------|-------------|-------|
| **Source Citations** | ❌ No | ✅ Field-level citations |
| **Confidence Scores** | ⚠️ Generic | ✅ Per-field confidence |
| **Agent Usage Tracking** | ❌ No | ✅ Full audit trail |
| **User Verification** | ❌ No | ✅ Interactive verification |
| **Data Lineage** | ❌ No | ✅ Complete lineage |

---

## 🎯 Strategic Context

### **Why This Matters**

1. **Trust**: Utenti vedono esattamente da dove vengono i dati
2. **Control**: Utenti capiscono come l'AI ha ragionato
3. **Compliance**: GDPR/AI Act ready con audit trail completo
4. **Quality**: Feedback loop migliora accuracy nel tempo
5. **Differentiation**: Nessun competitor offre questo livello di trasparenza

### **Use Cases**

#### **Use Case 1: User Verifies Company Data**
```
User: "Perché l'AI pensa che la mia industry sia 'SaaS'?"
System: "Questa informazione proviene da 3 fonti:
  • LinkedIn (95% confidence): 'Industry: SaaS'
  • Website (88% confidence): 'Cloud-based software platform'
  • TechCrunch (72% confidence): 'SaaS startup launches...'
"
User: "Corretto! ✅"
```

#### **Use Case 2: User Corrects Wrong Data**
```
User: "La mia target audience non è 'Enterprise' ma 'SMB'"
System: "Grazie! Aggiorno il dato e marco le fonti come inaccurate.
  Fonti originali:
  • LinkedIn (65% confidence): 'Serving enterprise clients'
  Nuova fonte:
  • User correction (100% confidence): 'Target: SMB'
"
```

#### **Use Case 3: User Tracks Agent Usage**
```
User: "Quali dati ha usato l'AI per generare questo post?"
System: "Il Copywriter agent ha usato:
  • Company Name (da fylle.ai)
  • Voice Tone: Professional (da website analysis)
  • Target Audience: Tech leaders (da LinkedIn)
  • Recent News: Product launch (da TechCrunch)
  
  Usato 3 volte negli ultimi 7 giorni per:
  • LinkedIn post (2x)
  • Blog article (1x)
"
```

---

## 🔍 Current State Analysis

### **✅ What We Have**

#### 1. **Source Tracking in Cards**
```sql
CREATE TABLE context_cards (
    source_session_id UUID,  -- Onboarding session that created this
    source_workflow_id UUID, -- Workflow run that created this
    created_by TEXT NOT NULL,  -- 'user:{user_id}', 'agent:{agent_name}'
    ...
);
```

#### 2. **Evidence System in CompanySnapshot**
```python
class Evidence(BaseModel):
    source: str  # Source URL or reference
    excerpt: str  # Relevant excerpt from source
    confidence: Optional[float]  # Confidence score (0-1)
```

#### 3. **Confidence Scores**
```sql
confidence_score FLOAT DEFAULT 0.8,
quality_score FLOAT,
```

#### 4. **Usage Tracking**
```sql
usage_count INTEGER DEFAULT 0,
last_used_at TIMESTAMPTZ,
```

#### 5. **Performance Events**
```sql
CREATE TABLE card_performance_events (
    event_type TEXT,  -- 'content_generated', 'content_published', etc.
    event_data JSONB,
    workflow_run_id UUID,
    ...
);
```

### **❌ What's Missing**

| Gap | Impact | Priority |
|-----|--------|----------|
| **Citations from Perplexity** | Can't show sources | 🔥 Critical |
| **Field-level references** | Generic evidence only | 🔥 Critical |
| **Agent usage tracking** | No visibility into AI usage | 🔥 Critical |
| **UI for sources** | Users can't see citations | 🔥 Critical |
| **Verification workflow** | No user feedback loop | ⚠️ High |
| **Data lineage** | Can't trace data origin | ⚠️ High |

---

## 🏗️ Architecture Options

### **Option 1: Centralized References (Recommended)**

**Concept**: Store all references in card `content` JSONB with field-level granularity.

```json
{
  "card_id": "card-123",
  "content": {
    "company_name": "Fylle AI",
    "industry": "AI-powered content generation",
    "references": [
      {
        "field": "company_name",
        "source": "https://fylle.ai",
        "excerpt": "Fylle AI - AI-powered content generation platform",
        "confidence": 0.95,
        "extraction_method": "perplexity",
        "extracted_at": "2025-01-25T10:00:00Z"
      },
      {
        "field": "industry",
        "source": "https://linkedin.com/company/fylle",
        "excerpt": "Industry: AI-powered content generation",
        "confidence": 0.88,
        "extraction_method": "perplexity",
        "extracted_at": "2025-01-25T10:00:00Z"
      }
    ]
  }
}
```

**✅ Pros**:
- Simple schema (no new tables)
- JSONB flexibility
- Easy to query with PostgreSQL JSONB operators
- Backward compatible

**❌ Cons**:
- JSONB can become large
- Harder to aggregate across cards
- No referential integrity

---

### **Option 2: Separate References Table**

**Concept**: Create dedicated `card_references` table with foreign keys.

```sql
CREATE TABLE card_references (
    reference_id UUID PRIMARY KEY,
    card_id UUID REFERENCES context_cards(card_id),
    field_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    excerpt TEXT,
    confidence FLOAT,
    extraction_method TEXT,
    extracted_at TIMESTAMPTZ
);
```

**✅ Pros**:
- Normalized schema
- Easy to query and aggregate
- Referential integrity
- Better for analytics

**❌ Cons**:
- More complex schema
- Additional JOIN required
- Migration needed

---

### **Option 3: Hybrid Approach (Best of Both)**

**Concept**: Store references in JSONB but also maintain a materialized view for analytics.

```sql
-- Store in JSONB (Option 1)
CREATE TABLE context_cards (
    content JSONB  -- includes 'references' array
);

-- Materialized view for analytics (Option 2)
CREATE MATERIALIZED VIEW v_card_references AS
SELECT 
    card_id,
    ref->>'field' as field_name,
    ref->>'source' as source_url,
    (ref->>'confidence')::float as confidence
FROM context_cards,
     jsonb_array_elements(content->'references') as ref;
```

**✅ Pros**:
- Flexibility of JSONB
- Performance of normalized view
- Best for both OLTP and OLAP

**❌ Cons**:
- Slightly more complex
- Need to refresh materialized view

---

### **🎯 Recommendation: Option 3 (Hybrid)**

**Rationale**:
1. ✅ Maintains JSONB flexibility for rapid iteration
2. ✅ Provides normalized view for analytics
3. ✅ Backward compatible with existing schema
4. ✅ Best performance for both use cases

---

## 📐 Implementation Specifications

### **Component 1: Enhanced Data Models**

```python
# onboarding/domain/models.py

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class FieldReference(BaseModel):
    """Reference for a specific field in a card."""
    
    field: str = Field(
        ..., 
        description="Field name (e.g., 'company_name', 'industry')"
    )
    source: str = Field(
        ..., 
        description="Source URL or reference"
    )
    excerpt: str = Field(
        ..., 
        description="Relevant excerpt from source (max 500 chars)"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score (0-1)"
    )
    extracted_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this reference was extracted"
    )
    extraction_method: str = Field(
        default="perplexity",
        description="How extracted: perplexity, web_search, user_input, agent_inference"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata (e.g., page_rank, freshness)"
    )

class CompanyInfo(BaseModel):
    """Company information with field-level references."""
    
    name: str
    industry: Optional[str] = None
    description: str
    key_offerings: List[str] = Field(default_factory=list)
    differentiators: List[str] = Field(default_factory=list)
    
    # ⭐ NEW: Field-level references
    references: List[FieldReference] = Field(
        default_factory=list,
        description="References for each field"
    )
    
    # Legacy evidence (keep for backward compatibility)
    evidence: List[Evidence] = Field(default_factory=list)
    
    def get_references_for_field(self, field_name: str) -> List[FieldReference]:
        """Get all references for a specific field."""
        return [ref for ref in self.references if ref.field == field_name]
    
    def get_confidence_for_field(self, field_name: str) -> Optional[float]:
        """Get average confidence for a specific field."""
        refs = self.get_references_for_field(field_name)
        if not refs:
            return None
        return sum(ref.confidence for ref in refs) / len(refs)
```

---

### **Component 2: Enhanced Perplexity Adapter**

```python
# onboarding/infrastructure/adapters/perplexity_adapter.py

async def research_company(
    self,
    brand_name: str,
    website: Optional[str] = None,
    additional_context: Optional[str] = None,
) -> Dict[str, Any]:
    """Research company with citation extraction."""

    # Build query
    query = self._build_research_query(brand_name, website, additional_context)

    # Execute search via CGS tool
    result = await self.tool.search(query)

    # Extract response
    data = result.get("data", {})
    choices = data.get("choices", [])

    if not choices:
        raise ValueError("No research results returned from Perplexity")

    # Get first choice content
    content = choices[0].get("message", {}).get("content", "")

    # ⭐ NEW: Extract citations from Perplexity response
    citations = self._extract_citations(data)

    # Build structured response
    research_result = {
        "brand_name": brand_name,
        "website": website,
        "raw_content": content,
        "citations": citations,  # ← NEW!
        "provider": result.get("provider"),
        "model_used": result.get("model_used"),
        "duration_ms": result.get("duration_ms"),
        "usage_tokens": result.get("usage_tokens"),
        "cost_usd": result.get("cost_usd"),
        "cost_source": result.get("cost_source"),
    }

    logger.info(
        f"Research completed: {len(citations)} citations, "
        f"{result.get('usage_tokens', 0)} tokens, "
        f"${result.get('cost_usd', 0):.4f}"
    )

    return research_result

def _extract_citations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract citations from Perplexity response.

    Perplexity includes citations in different formats depending on model:
    - Sonar: citations in message.citations
    - Sonar Pro: citations in data.citations

    Returns:
        List of citation dicts with url, title, snippet
    """
    citations = []

    # Try message-level citations first
    choices = data.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        if "citations" in message:
            citations = message["citations"]

    # Fallback to data-level citations
    if not citations and "citations" in data:
        citations = data["citations"]

    # Normalize citation format
    normalized_citations = []
    for citation in citations:
        if isinstance(citation, str):
            # Simple URL string
            normalized_citations.append({
                "url": citation,
                "title": None,
                "snippet": None
            })
        elif isinstance(citation, dict):
            # Structured citation
            normalized_citations.append({
                "url": citation.get("url", citation.get("link", "")),
                "title": citation.get("title"),
                "snippet": citation.get("snippet", citation.get("text"))
            })

    logger.info(f"Extracted {len(normalized_citations)} citations from Perplexity")

    return normalized_citations
```

---

### **Component 3: Enhanced Gemini Synthesis**

```python
# onboarding/infrastructure/adapters/gemini_adapter.py

async def synthesize_snapshot(
    self,
    brand_name: str,
    research_result: Dict[str, Any],
) -> CompanySnapshot:
    """
    Synthesize snapshot with field-level references.

    Maps Perplexity citations to specific fields in CompanySnapshot.
    """

    # Extract citations
    citations = research_result.get("citations", [])
    citations_text = json.dumps(citations, indent=2) if citations else "No citations available"

    # Build enhanced prompt with citation instruction
    prompt = f"""
Analyze this research about {brand_name} and create a structured company snapshot.

Research Content:
{research_result['raw_content']}

Available Citations:
{citations_text}

CRITICAL INSTRUCTIONS:
1. For EACH field you extract, you MUST include the citation source
2. Match each piece of information to the most relevant citation
3. Assign a confidence score (0-1) based on:
   - Source credibility (official website = 0.95, news = 0.8, social = 0.6)
   - Information freshness (recent = higher confidence)
   - Consistency across sources (multiple sources = higher confidence)

Return ONLY valid JSON with this EXACT structure:
{{
  "company": {{
    "name": "...",
    "industry": "...",
    "description": "...",
    "key_offerings": ["...", "..."],
    "differentiators": ["...", "..."],
    "references": [
      {{
        "field": "name",
        "source": "https://...",
        "excerpt": "Exact quote from source (max 200 chars)",
        "confidence": 0.95,
        "extraction_method": "perplexity"
      }},
      {{
        "field": "industry",
        "source": "https://...",
        "excerpt": "Exact quote from source (max 200 chars)",
        "confidence": 0.88,
        "extraction_method": "perplexity"
      }}
    ]
  }},
  "audience": {{
    "primary": "...",
    "pain_points": ["...", "..."],
    "desired_outcomes": ["...", "..."],
    "references": [...]
  }},
  "voice": {{
    "tone": "...",
    "style_guidelines": ["...", "..."],
    "references": [...]
  }},
  "insights": {{
    "positioning": "...",
    "key_messages": ["...", "..."],
    "recent_news": ["...", "..."],
    "competitors": ["...", "..."],
    "references": [...]
  }},
  "clarifying_questions": [...]
}}

IMPORTANT:
- Every field MUST have at least one reference
- Use the provided citations URLs
- If no citation available for a field, use "inference" as extraction_method with lower confidence
"""

    # Call Gemini
    response = await self._call_gemini_with_retry(prompt)

    # Parse JSON response
    try:
        snapshot_data = json.loads(response)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        # Fallback: try to extract JSON from markdown code block
        snapshot_data = self._extract_json_from_markdown(response)

    # Create CompanySnapshot
    snapshot = CompanySnapshot(**snapshot_data)

    # Log reference statistics
    total_refs = (
        len(snapshot.company.references) +
        len(snapshot.audience.references) +
        len(snapshot.voice.references) +
        len(snapshot.insights.references)
    )
    logger.info(f"Synthesized snapshot with {total_refs} field-level references")

    return snapshot
```

---

## 📊 Database Schema

### **Schema Option 1: JSONB References (Recommended)**

```sql
-- No schema changes needed!
-- References stored in content JSONB

-- Example card with references
INSERT INTO context_cards (
    card_id,
    tenant_id,
    card_type,
    title,
    content,
    source_session_id,
    created_by
) VALUES (
    gen_random_uuid(),
    '550e8400-e29b-41d4-a716-446655440000',
    'product',
    'Fylle AI - Product Card',
    '{
        "company_name": "Fylle AI",
        "industry": "AI-powered content generation",
        "description": "Fylle AI is a platform...",
        "references": [
            {
                "field": "company_name",
                "source": "https://fylle.ai",
                "excerpt": "Fylle AI - AI-powered content generation platform",
                "confidence": 0.95,
                "extraction_method": "perplexity",
                "extracted_at": "2025-01-25T10:00:00Z"
            },
            {
                "field": "industry",
                "source": "https://linkedin.com/company/fylle",
                "excerpt": "Industry: AI-powered content generation",
                "confidence": 0.88,
                "extraction_method": "perplexity",
                "extracted_at": "2025-01-25T10:00:00Z"
            }
        ]
    }'::jsonb,
    'session-123',
    'agent:research_specialist'
);

-- Query references for a specific field
SELECT
    card_id,
    title,
    ref->>'field' as field_name,
    ref->>'source' as source_url,
    (ref->>'confidence')::float as confidence
FROM context_cards,
     jsonb_array_elements(content->'references') as ref
WHERE card_id = 'card-123'
  AND ref->>'field' = 'company_name';
```

---

### **Schema Addition: Agent Usage Tracking**

```sql
-- ============================================================================
-- TABLE: agent_card_usage
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_card_usage (
    -- Identity
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id UUID NOT NULL REFERENCES context_cards(card_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,

    -- Agent Info
    agent_name TEXT NOT NULL,  -- 'copywriter', 'research_specialist', etc.
    workflow_run_id UUID,      -- Workflow that triggered this usage

    -- Usage Context
    context_used JSONB NOT NULL,  -- {fields_read: [...], purpose: "..."}

    -- Metadata
    used_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX idx_agent_card_usage_card_id ON agent_card_usage(card_id);
CREATE INDEX idx_agent_card_usage_tenant_id ON agent_card_usage(tenant_id);
CREATE INDEX idx_agent_card_usage_agent_name ON agent_card_usage(agent_name);
CREATE INDEX idx_agent_card_usage_workflow_run_id ON agent_card_usage(workflow_run_id);
CREATE INDEX idx_agent_card_usage_used_at ON agent_card_usage(used_at DESC);

-- Comments
COMMENT ON TABLE agent_card_usage IS 'Tracks which agents use which cards and how';
COMMENT ON COLUMN agent_card_usage.context_used IS 'JSONB: {fields_read: [field names], purpose: description}';

-- ============================================================================
-- VIEW: Card Usage Summary
-- ============================================================================

CREATE OR REPLACE VIEW v_card_usage_summary AS
SELECT
    c.card_id,
    c.tenant_id,
    c.title,
    c.card_type,
    COUNT(DISTINCT u.usage_id) as total_uses,
    COUNT(DISTINCT u.agent_name) as unique_agents,
    COUNT(DISTINCT u.workflow_run_id) as unique_workflows,
    MAX(u.used_at) as last_used_at,
    jsonb_agg(DISTINCT u.agent_name) as agents_used,
    jsonb_agg(
        jsonb_build_object(
            'agent_name', u.agent_name,
            'used_at', u.used_at,
            'purpose', u.context_used->'purpose'
        ) ORDER BY u.used_at DESC
    ) FILTER (WHERE u.usage_id IS NOT NULL) as recent_usage
FROM context_cards c
LEFT JOIN agent_card_usage u ON c.card_id = u.card_id
GROUP BY c.card_id, c.tenant_id, c.title, c.card_type;

COMMENT ON VIEW v_card_usage_summary IS 'Summary of card usage by agents';

-- ============================================================================
-- VIEW: Reference Analytics
-- ============================================================================

CREATE MATERIALIZED VIEW v_card_references AS
SELECT
    c.card_id,
    c.tenant_id,
    c.card_type,
    c.title,
    ref->>'field' as field_name,
    ref->>'source' as source_url,
    ref->>'excerpt' as excerpt,
    (ref->>'confidence')::float as confidence,
    ref->>'extraction_method' as extraction_method,
    (ref->>'extracted_at')::timestamptz as extracted_at,
    c.created_at as card_created_at
FROM context_cards c,
     jsonb_array_elements(c.content->'references') as ref
WHERE c.is_active = true;

-- Indexes for materialized view
CREATE INDEX idx_v_card_references_card_id ON v_card_references(card_id);
CREATE INDEX idx_v_card_references_tenant_id ON v_card_references(tenant_id);
CREATE INDEX idx_v_card_references_field_name ON v_card_references(field_name);
CREATE INDEX idx_v_card_references_source_url ON v_card_references(source_url);
CREATE INDEX idx_v_card_references_confidence ON v_card_references(confidence DESC);

COMMENT ON MATERIALIZED VIEW v_card_references IS 'Normalized view of all card references for analytics';

-- Refresh function
CREATE OR REPLACE FUNCTION refresh_card_references()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY v_card_references;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- EXAMPLE QUERIES
-- ============================================================================

-- Get all references for a card
SELECT * FROM v_card_references
WHERE card_id = 'card-123'
ORDER BY confidence DESC;

-- Get cards with low confidence
SELECT
    card_id,
    title,
    field_name,
    confidence,
    source_url
FROM v_card_references
WHERE confidence < 0.7
ORDER BY confidence ASC;

-- Get most used cards
SELECT
    card_id,
    title,
    total_uses,
    unique_agents,
    last_used_at
FROM v_card_usage_summary
ORDER BY total_uses DESC
LIMIT 10;

-- Get agent usage patterns
SELECT
    agent_name,
    COUNT(DISTINCT card_id) as cards_used,
    COUNT(*) as total_uses,
    MAX(used_at) as last_used
FROM agent_card_usage
WHERE tenant_id = '550e8400-e29b-41d4-a716-446655440000'
GROUP BY agent_name
ORDER BY total_uses DESC;
```

---

## 🔌 API Design

### **Endpoint 1: Get Card with References**

```python
# GET /api/v1/cards/{card_id}/references

@router.get("/{card_id}/references")
async def get_card_references(
    card_id: UUID,
    field: Optional[str] = Query(None, description="Filter by field name"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    request: Request = None
) -> CardReferencesResponse:
    """
    Get all references for a card.

    Query Parameters:
    - field: Filter references by field name
    - min_confidence: Filter references by minimum confidence

    Returns:
        CardReferencesResponse with references list
    """
    tenant_id = request.state.tenant_id

    # Get card
    card = await card_repository.get_by_id(card_id, tenant_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Extract references from content
    references = card.content.get("references", [])

    # Filter by field if specified
    if field:
        references = [ref for ref in references if ref.get("field") == field]

    # Filter by confidence if specified
    if min_confidence is not None:
        references = [ref for ref in references if ref.get("confidence", 0) >= min_confidence]

    return CardReferencesResponse(
        card_id=card_id,
        card_title=card.title,
        references=references,
        total_count=len(references)
    )
```

---

### **Endpoint 2: Get Agent Usage for Card**

```python
# GET /api/v1/cards/{card_id}/usage

@router.get("/{card_id}/usage")
async def get_card_usage(
    card_id: UUID,
    limit: int = Query(10, ge=1, le=100),
    request: Request = None
) -> CardUsageResponse:
    """
    Get agent usage history for a card.

    Returns:
        CardUsageResponse with usage history
    """
    tenant_id = request.state.tenant_id

    # Get usage from database
    usage_records = await db.fetch_all(
        """
        SELECT
            usage_id,
            agent_name,
            workflow_run_id,
            context_used,
            used_at
        FROM agent_card_usage
        WHERE card_id = $1 AND tenant_id = $2
        ORDER BY used_at DESC
        LIMIT $3
        """,
        card_id,
        tenant_id,
        limit
    )

    # Get summary statistics
    summary = await db.fetch_one(
        """
        SELECT
            COUNT(*) as total_uses,
            COUNT(DISTINCT agent_name) as unique_agents,
            MAX(used_at) as last_used_at
        FROM agent_card_usage
        WHERE card_id = $1 AND tenant_id = $2
        """,
        card_id,
        tenant_id
    )

    return CardUsageResponse(
        card_id=card_id,
        total_uses=summary["total_uses"],
        unique_agents=summary["unique_agents"],
        last_used_at=summary["last_used_at"],
        usage_history=[
            UsageRecord(
                usage_id=record["usage_id"],
                agent_name=record["agent_name"],
                workflow_run_id=record["workflow_run_id"],
                fields_read=record["context_used"].get("fields_read", []),
                purpose=record["context_used"].get("purpose"),
                used_at=record["used_at"]
            )
            for record in usage_records
        ]
    )
```

---

### **Endpoint 3: Track Agent Usage (Internal)**

```python
# POST /api/v1/cards/{card_id}/track-usage (Internal only)

@router.post("/{card_id}/track-usage")
async def track_card_usage(
    card_id: UUID,
    usage: TrackUsageRequest,
    request: Request = None
) -> TrackUsageResponse:
    """
    Track agent usage of a card.

    This endpoint is called internally by agents when they read cards.
    """
    tenant_id = request.state.tenant_id

    # Insert usage record
    usage_id = await db.execute(
        """
        INSERT INTO agent_card_usage (
            card_id,
            tenant_id,
            agent_name,
            workflow_run_id,
            context_used,
            used_at
        ) VALUES ($1, $2, $3, $4, $5, NOW())
        RETURNING usage_id
        """,
        card_id,
        tenant_id,
        usage.agent_name,
        usage.workflow_run_id,
        json.dumps({
            "fields_read": usage.fields_read,
            "purpose": usage.purpose
        })
    )

    # Update card usage_count
    await db.execute(
        """
        UPDATE context_cards
        SET
            usage_count = usage_count + 1,
            last_used_at = NOW()
        WHERE card_id = $1 AND tenant_id = $2
        """,
        card_id,
        tenant_id
    )

    return TrackUsageResponse(
        usage_id=usage_id,
        tracked_at=datetime.utcnow()
    )
```

---

## 🎨 Frontend Components

### **Component 1: SourceCitation**

```tsx
// onboarding-frontend/src/components/transparency/SourceCitation.tsx

import React, { useState } from 'react';
import { ExternalLink, CheckCircle, AlertCircle, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Reference {
  field: string;
  source: string;
  excerpt: string;
  confidence: number;
  extraction_method: string;
  extracted_at: string;
}

interface SourceCitationProps {
  references: Reference[];
  field?: string;  // If provided, show only references for this field
  compact?: boolean;  // Compact mode for inline display
}

export const SourceCitation: React.FC<SourceCitationProps> = ({
  references,
  field,
  compact = false
}) => {
  const [expanded, setExpanded] = useState(false);

  // Filter references by field if specified
  const filteredRefs = field
    ? references.filter(ref => ref.field === field)
    : references;

  if (filteredRefs.length === 0) return null;

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.85) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (confidence >= 0.6) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 0.85) return <CheckCircle className="h-3 w-3" />;
    return <AlertCircle className="h-3 w-3" />;
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.85) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Compact mode: just show count and confidence
  if (compact) {
    const avgConfidence = filteredRefs.reduce((sum, ref) => sum + ref.confidence, 0) / filteredRefs.length;
    return (
      <button
        onClick={() => setExpanded(!expanded)}
        className={`inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-medium transition-all ${getConfidenceColor(avgConfidence)}`}
      >
        {getConfidenceIcon(avgConfidence)}
        <span>{filteredRefs.length} {filteredRefs.length === 1 ? 'source' : 'sources'}</span>
        <span className="text-xs opacity-70">({Math.round(avgConfidence * 100)}%)</span>
      </button>
    );
  }

  return (
    <div className="mt-2 rounded-lg border border-gray-200 bg-gray-50 p-3">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between text-xs font-medium text-gray-700 hover:text-gray-900 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Info className="h-4 w-4 text-blue-500" />
          <span>📚 Sources ({filteredRefs.length})</span>
        </div>
        <motion.span
          animate={{ rotate: expanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          ▼
        </motion.span>
      </button>

      {/* Expanded Content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="mt-2 space-y-2 overflow-hidden"
          >
            {filteredRefs.map((ref, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: index * 0.05 }}
                className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm hover:shadow-md transition-shadow"
              >
                {/* Source URL and Confidence */}
                <div className="flex items-start justify-between gap-2">
                  <a
                    href={ref.source}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    <ExternalLink className="h-3 w-3 flex-shrink-0" />
                    <span className="truncate">{new URL(ref.source).hostname}</span>
                  </a>

                  {/* Confidence Badge */}
                  <div className={`flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium ${getConfidenceColor(ref.confidence)}`}>
                    {getConfidenceIcon(ref.confidence)}
                    <span>{getConfidenceLabel(ref.confidence)}</span>
                    <span className="opacity-70">({Math.round(ref.confidence * 100)}%)</span>
                  </div>
                </div>

                {/* Excerpt */}
                <p className="mt-2 text-xs italic text-gray-600 leading-relaxed">
                  "{ref.excerpt.slice(0, 150)}{ref.excerpt.length > 150 ? '...' : ''}"
                </p>

                {/* Metadata */}
                <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
                  <span className="rounded bg-gray-100 px-1.5 py-0.5">
                    {ref.field}
                  </span>
                  <span>•</span>
                  <span>{ref.extraction_method}</span>
                  <span>•</span>
                  <span>{formatDate(ref.extracted_at)}</span>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
```

---

### **Component 2: AgentUsageTracker**

```tsx
// onboarding-frontend/src/components/transparency/AgentUsageTracker.tsx

import React, { useState, useEffect } from 'react';
import { Bot, Clock, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

interface UsageRecord {
  usage_id: string;
  agent_name: string;
  workflow_run_id: string;
  fields_read: string[];
  purpose: string;
  used_at: string;
}

interface AgentUsageTrackerProps {
  cardId: string;
  compact?: boolean;
}

export const AgentUsageTracker: React.FC<AgentUsageTrackerProps> = ({
  cardId,
  compact = false
}) => {
  const [usage, setUsage] = useState<{
    total_uses: number;
    unique_agents: number;
    last_used_at: string;
    usage_history: UsageRecord[];
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    fetchUsage();
  }, [cardId]);

  const fetchUsage = async () => {
    try {
      const response = await fetch(`/api/v1/cards/${cardId}/usage`);
      const data = await response.json();
      setUsage(data);
    } catch (error) {
      console.error('Failed to fetch usage:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse rounded-lg border border-gray-200 bg-gray-50 p-3">
        <div className="h-4 w-32 bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (!usage || usage.total_uses === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-3 text-xs text-gray-500">
        <Bot className="inline h-3 w-3 mr-1" />
        Not yet used by agents
      </div>
    );
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Compact mode
  if (compact) {
    return (
      <div className="inline-flex items-center gap-2 rounded-md border border-purple-200 bg-purple-50 px-2 py-1 text-xs font-medium text-purple-700">
        <Bot className="h-3 w-3" />
        <span>{usage.total_uses}x by {usage.unique_agents} agents</span>
      </div>
    );
  }

  return (
    <div className="mt-3 rounded-lg border border-purple-200 bg-purple-50 p-3">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between text-xs font-medium text-purple-900 hover:text-purple-700 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4" />
          <span>🤖 Used by Agents ({usage.total_uses} times)</span>
        </div>
        <motion.span
          animate={{ rotate: expanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          ▼
        </motion.span>
      </button>

      {/* Summary Stats */}
      <div className="mt-2 flex items-center gap-4 text-xs text-purple-700">
        <div className="flex items-center gap-1">
          <Zap className="h-3 w-3" />
          <span>{usage.unique_agents} unique agents</span>
        </div>
        <div className="flex items-center gap-1">
          <Clock className="h-3 w-3" />
          <span>Last: {formatTimeAgo(usage.last_used_at)}</span>
        </div>
      </div>

      {/* Expanded History */}
      {expanded && usage.usage_history.length > 0 && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          transition={{ duration: 0.2 }}
          className="mt-3 space-y-2 overflow-hidden"
        >
          {usage.usage_history.map((record, index) => (
            <div
              key={record.usage_id}
              className="rounded border border-purple-200 bg-white p-2 text-xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-medium text-purple-900">
                  {record.agent_name}
                </span>
                <span className="text-purple-600">
                  {formatTimeAgo(record.used_at)}
                </span>
              </div>
              {record.purpose && (
                <p className="mt-1 text-gray-600 italic">
                  {record.purpose}
                </p>
              )}
              {record.fields_read.length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1">
                  {record.fields_read.map((field, i) => (
                    <span
                      key={i}
                      className="rounded bg-purple-100 px-1.5 py-0.5 text-xs text-purple-700"
                    >
                      {field}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </motion.div>
      )}
    </div>
  );
};
```

---

### **Component 3: Enhanced Card with Transparency**

```tsx
// onboarding-frontend/src/components/cards/CompanySnapshotCardV2.tsx (Enhanced)

import { SourceCitation } from '../transparency/SourceCitation';
import { AgentUsageTracker } from '../transparency/AgentUsageTracker';

export const CompanySnapshotCardV2: React.FC<CompanySnapshotCardV2Props> = ({ snapshot }) => {
  const [showTransparency, setShowTransparency] = useState(false);

  return (
    <FylleCard category="company" className="h-full">
      <CardHeader
        icon={Building2}
        title={snapshot.company.name}
        subtitle={snapshot.company.industry || 'Industry not specified'}
        confidence={avgConfidence}
        category="company"
      />

      <CardContent className="space-y-4">
        {/* Description */}
        <div>
          <p className="text-sm leading-relaxed text-gray-700">
            {truncateText(snapshot.company.description)}
          </p>

          {/* ⭐ NEW: Source Citations */}
          {snapshot.company.references && snapshot.company.references.length > 0 && (
            <SourceCitation
              references={snapshot.company.references}
              field="description"
            />
          )}
        </div>

        {/* Industry */}
        {snapshot.company.industry && (
          <Section icon={Briefcase} title="Industry">
            <Chip label={snapshot.company.industry} />

            {/* ⭐ NEW: Source Citations for Industry */}
            {snapshot.company.references && (
              <SourceCitation
                references={snapshot.company.references}
                field="industry"
                compact
              />
            )}
          </Section>
        )}

        {/* Key Offerings */}
        {snapshot.company.key_offerings && snapshot.company.key_offerings.length > 0 && (
          <Section icon={Package} title="Key Offerings">
            <div className="flex flex-wrap gap-2">
              {snapshot.company.key_offerings.slice(0, 3).map((offering, i) => (
                <Chip key={i} label={offering} />
              ))}
            </div>
          </Section>
        )}

        {/* Differentiators */}
        {snapshot.company.differentiators && snapshot.company.differentiators.length > 0 && (
          <Section icon={Sparkles} title="Differentiators">
            <ul className="space-y-1 text-sm text-gray-700">
              {snapshot.company.differentiators.slice(0, 3).map((diff, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-emerald-500 mt-0.5">✓</span>
                  <span>{diff}</span>
                </li>
              ))}
            </ul>
          </Section>
        )}

        {/* ⭐ NEW: Transparency Toggle */}
        <button
          onClick={() => setShowTransparency(!showTransparency)}
          className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-xs font-medium text-gray-700 hover:bg-gray-100 transition-colors"
        >
          {showTransparency ? '🔒 Hide' : '🔍 Show'} Transparency Info
        </button>

        {/* ⭐ NEW: Transparency Panel */}
        {showTransparency && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-3 rounded-lg border border-blue-200 bg-blue-50 p-3"
          >
            <h4 className="text-sm font-semibold text-blue-900">
              📊 Transparency & Explainability
            </h4>

            {/* All Sources */}
            <div>
              <p className="text-xs font-medium text-blue-800 mb-2">All Sources:</p>
              <SourceCitation references={snapshot.company.references} />
            </div>

            {/* Agent Usage */}
            <div>
              <p className="text-xs font-medium text-blue-800 mb-2">Agent Usage:</p>
              <AgentUsageTracker cardId={snapshot.snapshot_id} />
            </div>

            {/* Data Quality */}
            <div className="rounded border border-blue-200 bg-white p-2">
              <p className="text-xs font-medium text-blue-900 mb-1">Data Quality:</p>
              <div className="space-y-1 text-xs text-gray-600">
                <div className="flex justify-between">
                  <span>Average Confidence:</span>
                  <span className="font-medium">{Math.round(avgConfidence * 100)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Total References:</span>
                  <span className="font-medium">{snapshot.company.references?.length || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>Last Updated:</span>
                  <span className="font-medium">
                    {new Date(snapshot.generated_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </CardContent>

      <CardFooter className="flex items-center justify-between">
        <div className="text-xs text-gray-500">
          Updated {new Date(snapshot.generated_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          })}
        </div>
        <button className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 transition-all duration-200 hover:bg-emerald-100">
          Refine Details
        </button>
      </CardFooter>
    </FylleCard>
  );
};
```

---

## 📋 Roadmap

### **Phase 1: Foundation (2 weeks) - 21 Story Points**

#### Epic 1.1: Data Models & Schema
**Story Points**: 8

- [ ] **Task 1.1.1**: Create `FieldReference` model (2 SP)
  - Add to `onboarding/domain/models.py`
  - Unit tests
  - Documentation

- [ ] **Task 1.1.2**: Update `CompanyInfo` with references (2 SP)
  - Add `references` field
  - Add helper methods
  - Backward compatibility

- [ ] **Task 1.1.3**: Create `agent_card_usage` table (2 SP)
  - SQL migration
  - Indexes
  - Views

- [ ] **Task 1.1.4**: Create materialized view for analytics (2 SP)
  - `v_card_references` view
  - Refresh function
  - Indexes

#### Epic 1.2: Perplexity Integration
**Story Points**: 8

- [ ] **Task 1.2.1**: Extract citations from Perplexity (3 SP)
  - Modify `PerplexityAdapter._extract_citations()`
  - Handle different response formats
  - Unit tests

- [ ] **Task 1.2.2**: Update research flow (3 SP)
  - Pass citations to synthesis
  - Store in research_result
  - Integration tests

- [ ] **Task 1.2.3**: Error handling & fallbacks (2 SP)
  - Handle missing citations
  - Fallback to inference
  - Logging

#### Epic 1.3: Gemini Synthesis
**Story Points**: 5

- [ ] **Task 1.3.1**: Update synthesis prompt (2 SP)
  - Add citation mapping instructions
  - Field-level reference format
  - Examples

- [ ] **Task 1.3.2**: Parse references from response (2 SP)
  - Extract references from JSON
  - Validate structure
  - Error handling

- [ ] **Task 1.3.3**: Integration testing (1 SP)
  - End-to-end test
  - Reference quality validation

---

### **Phase 2: Agent Tracking (1 week) - 13 Story Points**

#### Epic 2.1: ContextCardTool Enhancement
**Story Points**: 8

- [ ] **Task 2.1.1**: Add usage tracking to tool (3 SP)
  - Track when agent reads card
  - Record fields accessed
  - Store purpose/context

- [ ] **Task 2.1.2**: Create tracking repository (3 SP)
  - `AgentUsageRepository`
  - CRUD operations
  - Unit tests

- [ ] **Task 2.1.3**: Integration with workflow (2 SP)
  - Auto-track in workflow execution
  - Pass workflow_run_id
  - Testing

#### Epic 2.2: Analytics & Reporting
**Story Points**: 5

- [ ] **Task 2.2.1**: Usage summary queries (2 SP)
  - Most used cards
  - Agent usage patterns
  - Time-based analytics

- [ ] **Task 2.2.2**: Reference quality metrics (2 SP)
  - Low confidence detection
  - Source diversity
  - Freshness tracking

- [ ] **Task 2.2.3**: Dashboard queries (1 SP)
  - Aggregate statistics
  - Trend analysis

---

### **Phase 3: API & Frontend (2 weeks) - 21 Story Points**

#### Epic 3.1: API Endpoints
**Story Points**: 8

- [ ] **Task 3.1.1**: GET /cards/{id}/references (2 SP)
  - Endpoint implementation
  - Query filters
  - Response models

- [ ] **Task 3.1.2**: GET /cards/{id}/usage (2 SP)
  - Endpoint implementation
  - Pagination
  - Summary statistics

- [ ] **Task 3.1.3**: POST /cards/{id}/track-usage (2 SP)
  - Internal endpoint
  - Validation
  - Rate limiting

- [ ] **Task 3.1.4**: API documentation (2 SP)
  - OpenAPI specs
  - Examples
  - Integration guide

#### Epic 3.2: Frontend Components
**Story Points**: 13

- [ ] **Task 3.2.1**: SourceCitation component (3 SP)
  - React component
  - Animations
  - Responsive design

- [ ] **Task 3.2.2**: AgentUsageTracker component (3 SP)
  - React component
  - Real-time updates
  - Compact mode

- [ ] **Task 3.2.3**: Integrate into cards (4 SP)
  - Update all card components
  - Transparency toggle
  - Testing

- [ ] **Task 3.2.4**: UI/UX polish (3 SP)
  - Animations
  - Loading states
  - Error handling

---

### **Phase 4: Testing & Refinement (1 week) - 8 Story Points**

- [ ] **Task 4.1**: End-to-end testing (3 SP)
- [ ] **Task 4.2**: Performance optimization (2 SP)
- [ ] **Task 4.3**: Documentation (2 SP)
- [ ] **Task 4.4**: User acceptance testing (1 SP)

---

### **Total Effort**

| Phase | Duration | Story Points |
|-------|----------|--------------|
| Phase 1: Foundation | 2 weeks | 21 SP |
| Phase 2: Agent Tracking | 1 week | 13 SP |
| Phase 3: API & Frontend | 2 weeks | 21 SP |
| Phase 4: Testing | 1 week | 8 SP |
| **TOTAL** | **6 weeks** | **63 SP** |

**Team**: 2 developers (1 backend, 1 frontend)
**Velocity**: ~10 SP/week per developer
**Timeline**: 6 weeks (1.5 months)

---

## 📊 Success Metrics

### **Adoption Metrics**

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Users viewing sources** | 60% of active users | % users clicking "Show Sources" |
| **Source verification rate** | 30% of cards | % cards with user verification |
| **Transparency panel usage** | 40% of sessions | % sessions with transparency toggle |

### **Quality Metrics**

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Average confidence** | >85% | Avg confidence across all references |
| **References per field** | >2 sources | Avg references per field |
| **Citation coverage** | >95% | % fields with at least 1 reference |
| **Low confidence alerts** | <5% | % references with confidence <60% |

### **Trust Metrics**

| Metric | Target | Measurement |
|--------|--------|-------------|
| **User corrections** | <10% | % fields corrected by users |
| **Source trust score** | >4.5/5 | User rating of source quality |
| **Transparency NPS** | >50 | Net Promoter Score for transparency |

### **Business Metrics**

| Metric | Target | Measurement |
|--------|--------|-------------|
| **User retention** | +15% | Retention lift vs control group |
| **Feature adoption** | 70% | % users using transparency features |
| **Support tickets** | -20% | Reduction in "wrong data" tickets |
| **Competitive differentiation** | Top 3 | Ranking in user surveys |

---

## 🎯 Next Steps

### **Immediate Actions**

1. ✅ **Review & Approve** this document with stakeholders
2. ✅ **Create Linear tickets** from roadmap tasks
3. ✅ **Assign team members** to Phase 1 tasks
4. ✅ **Set up tracking** for success metrics

### **Week 1 Priorities**

- [ ] Implement `FieldReference` model
- [ ] Update Perplexity adapter for citation extraction
- [ ] Create database migration for `agent_card_usage`
- [ ] Start Gemini synthesis prompt updates

### **Dependencies**

- ✅ Existing Adaptive Cards system
- ✅ Perplexity integration
- ✅ Gemini synthesis
- ⚠️ Need: Perplexity API documentation for citations format
- ⚠️ Need: Design review for UI components

---

## 📚 References

- [Adaptive Cards Architecture](../CARD_SYSTEM_ARCHITECTURE.md)
- [Perplexity API Documentation](https://docs.perplexity.ai)
- [GDPR Compliance Guidelines](https://gdpr.eu)
- [EU AI Act Requirements](https://artificialintelligenceact.eu)

---

**Document Owner**: Fylle AI Team
**Last Updated**: 2025-01-25
**Status**: 📋 Ready for Review
**Next Review**: 2025-02-01







