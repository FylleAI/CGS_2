# 🔍 Transparency & Explainability Documentation

**Last Updated**: 2025-01-25  
**Status**: 📋 Planning Phase  
**Priority**: 🔥 High (Core Differentiator)

---

## 📖 Overview

This directory contains comprehensive documentation for Fylle's **Transparency & Explainability** feature - a core differentiator that allows users to see, understand, and verify what the AI knows about them and how it uses that information.

---

## 🎯 Quick Links

| Document | Description | Audience |
|----------|-------------|----------|
| **[TRANSPARENCY_EXPLAINABILITY_FEATURE.md](./TRANSPARENCY_EXPLAINABILITY_FEATURE.md)** | Complete technical specification | All |
| **[EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md)** | High-level overview | Product, Leadership |
| **[IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)** | Step-by-step implementation | Developers |

---

## 🚀 What is Transparency & Explainability?

### **The Problem**

Most AI systems are "black boxes":
- ❌ Users don't know what data the AI has about them
- ❌ Users can't see where the AI got its information
- ❌ Users can't verify if the data is accurate
- ❌ Users can't track how their data is being used

### **Fylle's Solution**

> **"Fylle doesn't just offer AI integration - it offers a way to clarify what the AI is using as context, why, and how."**

We provide:
1. ✅ **Source Citations**: Every piece of data has references to original sources
2. ✅ **Confidence Scores**: Field-level confidence metrics (0-100%)
3. ✅ **Agent Usage Tracking**: Complete audit trail of how agents use data
4. ✅ **User Verification**: Users can verify and correct information
5. ✅ **Data Lineage**: Full traceability from source to usage

---

## 📊 Key Features

### **1. Field-Level Source Citations**

```
Company Name: "Fylle AI"
📚 Sources (3):
  • fylle.ai (95% confidence)
    "Fylle AI - AI-powered content generation platform"
  • LinkedIn (88% confidence)
    "Company: Fylle AI | Industry: AI/ML"
  • TechCrunch (72% confidence)
    "Fylle AI launches new platform..."
```

### **2. Agent Usage Tracking**

```
🤖 Used by Agents (5 times):
  • Copywriter (3x) - Last: 2h ago
    Purpose: "Generate LinkedIn post"
    Fields: company_name, voice_tone, target_audience
  
  • Research Specialist (2x) - Last: 1d ago
    Purpose: "Competitor analysis"
    Fields: industry, competitors, positioning
```

### **3. Interactive Verification**

```
User: "My target audience is SMB, not Enterprise"
System: ✅ Updated!
  Old: Enterprise (65% confidence from LinkedIn)
  New: SMB (100% confidence from user correction)
```

---

## 🏗️ Architecture

### **High-Level Flow**

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                            │
│  • View sources for each field                              │
│  • See confidence scores                                    │
│  • Track agent usage                                        │
│  • Verify/correct data                                      │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                  TRANSPARENCY LAYER                          │
│  • Field-level references in JSONB                          │
│  • Agent usage tracking table                               │
│  • Materialized views for analytics                         │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                  DATA SOURCES                                │
│  • Perplexity (with citations)                              │
│  • Gemini (with reference mapping)                          │
│  • User input (100% confidence)                             │
└─────────────────────────────────────────────────────────────┘
```

### **Key Components**

1. **Data Models**: `FieldReference` with source, excerpt, confidence
2. **Perplexity Adapter**: Extract citations from API response
3. **Gemini Synthesis**: Map citations to specific fields
4. **Database**: JSONB references + agent_card_usage table
5. **API**: Endpoints for references and usage tracking
6. **Frontend**: SourceCitation and AgentUsageTracker components

---

## 📋 Implementation Roadmap

### **Phase 1: Foundation (2 weeks) - 21 SP**
- Data models & schema
- Perplexity citation extraction
- Gemini reference mapping

### **Phase 2: Agent Tracking (1 week) - 13 SP**
- ContextCardTool enhancement
- Usage tracking repository
- Analytics queries

### **Phase 3: API & Frontend (2 weeks) - 21 SP**
- API endpoints
- React components
- Card integration

### **Phase 4: Testing & Refinement (1 week) - 8 SP**
- E2E testing
- Performance optimization
- Documentation

**Total**: 6 weeks, 63 story points

---

## 📊 Success Metrics

### **Adoption**
- 60% of users view sources
- 30% verify card data
- 40% use transparency panel

### **Quality**
- >85% average confidence
- >2 sources per field
- >95% citation coverage

### **Trust**
- <10% user corrections
- >4.5/5 source trust score
- >50 transparency NPS

### **Business**
- +15% user retention
- 70% feature adoption
- -20% support tickets

---

## 🎯 Competitive Differentiation

| Feature | Competitors | Fylle |
|---------|-------------|-------|
| **Source Citations** | ❌ No | ✅ Field-level |
| **Confidence Scores** | ⚠️ Generic | ✅ Per-field |
| **Agent Usage Tracking** | ❌ No | ✅ Full audit trail |
| **User Verification** | ❌ No | ✅ Interactive |
| **Data Lineage** | ❌ No | ✅ Complete |

---

## 🚦 Current Status

### **✅ What We Have**
- Source tracking in cards (`source_session_id`, `source_workflow_id`)
- Evidence system in CompanySnapshot
- Confidence scores
- Usage count tracking
- Performance events

### **❌ What's Missing**
- Citations from Perplexity
- Field-level references
- Agent usage tracking
- UI for sources
- Verification workflow

---

## 📚 Documentation Structure

```
docs/transparency/
├── README.md                                    # This file
├── TRANSPARENCY_EXPLAINABILITY_FEATURE.md       # Complete specification
├── EXECUTIVE_SUMMARY.md                         # High-level overview
├── IMPLEMENTATION_GUIDE.md                      # Developer guide
└── examples/
    ├── field_reference_example.json             # Data model example
    ├── perplexity_citation_example.json         # API response example
    └── ui_component_example.tsx                 # Frontend example
```

---

## 🎓 Getting Started

### **For Product Managers**
1. Read [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md)
2. Review success metrics and business impact
3. Understand competitive differentiation

### **For Developers**
1. Read [TRANSPARENCY_EXPLAINABILITY_FEATURE.md](./TRANSPARENCY_EXPLAINABILITY_FEATURE.md)
2. Review architecture options (Section 4)
3. Follow [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)

### **For Designers**
1. Review UI components (Section 8)
2. Check frontend examples in `examples/`
3. Design transparency panel mockups

---

## 🔗 Related Documentation

- [Adaptive Cards Architecture](../CARD_SYSTEM_ARCHITECTURE.md)
- [Onboarding System](../../onboarding/README.md)
- [Perplexity Integration](../../onboarding/infrastructure/adapters/perplexity_adapter.py)
- [Gemini Synthesis](../../onboarding/infrastructure/adapters/gemini_adapter.py)

---

## 📞 Contact

**Feature Owner**: Fylle AI Team  
**Technical Lead**: TBD  
**Product Manager**: TBD  
**Email**: davide@fylle.ai

---

## 📝 Changelog

### 2025-01-25
- ✅ Initial documentation created
- ✅ Complete technical specification
- ✅ Architecture options defined
- ✅ Roadmap with 63 story points
- ✅ Success metrics defined

### Next Steps
- [ ] Review with stakeholders
- [ ] Create Linear tickets
- [ ] Assign team members
- [ ] Start Phase 1 implementation

---

**Status**: 📋 Ready for Review  
**Next Review**: 2025-02-01

