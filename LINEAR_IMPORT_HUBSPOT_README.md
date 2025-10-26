# 📋 Linear Import Guide - HubSpot Integration

**Project**: Native HubSpot Publishing with MCP Integration  
**Timeline**: 8-10 settimane  
**Story Points**: 144 points (aggiornato con MCP)

---

## 🚀 QUICK START

### Opzione 1: Import CSV (Raccomandato)

```bash
# 1. Apri Linear
# 2. Vai a Settings → Import
# 3. Seleziona "CSV Import"
# 4. Upload LINEAR_IMPORT_HUBSPOT_TASKS.csv
# 5. Map columns:
#    - Title → Title
#    - Description → Description
#    - Priority → Priority
#    - Estimate → Estimate
#    - Status → Status
#    - Milestone → Milestone
#    - Epic → Epic
#    - Dependencies → Dependencies (custom field)
#    - Assignee → Assignee
# 6. Review and import
```

### Opzione 2: Manual Creation

Usa `LINEAR_ROADMAP_HUBSPOT_INTEGRATION.md` come riferimento per creare task manualmente.

### Opzione 3: Linear API

```bash
# Usa Linear API per import programmatico
# Vedi: https://developers.linear.app/docs/graphql/working-with-the-graphql-api
```

---

## 📁 FILE STRUCTURE

```
.
├── LINEAR_ROADMAP_HUBSPOT_INTEGRATION.md    # Roadmap completa (32 task)
├── LINEAR_IMPORT_HUBSPOT_TASKS.csv          # CSV per import Linear
├── HUBSPOT_INTEGRATION_ANALYSIS.md          # Analisi tecnica completa
├── HUBSPOT_QUICK_START.md                   # Quick start guide
├── DATABASE_SCHEMA_HUBSPOT_INTEGRATION.sql  # Schema SQL
├── EXAMPLES_HUBSPOT_INTEGRATION.md          # Code examples
└── LINEAR_IMPORT_HUBSPOT_README.md          # Questo file
```

---

## 🏗️ LINEAR STRUCTURE

### Milestones (6)

| Milestone | Durata | Points | Deliverables |
|-----------|--------|--------|--------------|
| **M1: Foundation** | Week 1-2 | 18 | Database, models, MCP setup |
| **M2: Adapter & Blog** | Week 2-4 | 28 | HubSpot adapter, blog publishing |
| **M3: API & Frontend** | Week 4-5 | 19 | API endpoints, UI |
| **M4: OAuth & Multi-Tenant** | Week 6-7 | 34 | OAuth flow, multi-tenant |
| **M5: Advanced Features** | Week 8-10 | 27 | Scheduling, social, analytics |
| **M6: MCP Integration** 🆕 | Week 6-8 | 10 | MCP client, context-aware publishing |

### Epics (9)

1. **EPIC 0: MCP Setup & Integration** 🆕 (3 tasks, 10 points)
   - Setup HubSpot MCP Server
   - Implement MCP client wrapper
   - Setup Developer MCP Server

2. **EPIC 1: Database Schema & Models** (4 tasks, 18 points)
   - Design schema
   - Create migration
   - Implement domain models
   - Create repositories

3. **EPIC 2: HubSpot Adapter** (4 tasks, 21 points)
   - Implement adapter
   - Markdown converter
   - Rate limiter
   - Error handling

4. **EPIC 3: Blog Publishing** (3 tasks, 13 points)
   - Publish use case
   - Metadata handling
   - Integration tests

5. **EPIC 4: API Endpoints** (3 tasks, 13 points)
   - Publish endpoint
   - Status endpoint
   - Retry endpoint

6. **EPIC 5: Frontend UI** (2 tasks, 8 points)
   - Publish button
   - Status tracking

7. **EPIC 6: OAuth & Multi-Tenant** (5 tasks, 34 points)
   - OAuth flow
   - Token refresh
   - Credential management
   - Multi-tenant isolation
   - Admin UI

8. **EPIC 7: Advanced Features** (5 tasks, 27 points)
   - Scheduling
   - Social media
   - Performance tracking
   - Retry logic
   - A/B testing

9. **EPIC 8: Testing & Documentation** (3 tasks, 10 points)
   - Integration tests
   - E2E tests
   - Documentation

### Labels

Create questi labels in Linear:

- `hubspot-integration` (Project label)
- `mcp` 🆕 (MCP-related tasks)
- `backend` (Backend tasks)
- `frontend` (Frontend tasks)
- `database` (Database tasks)
- `api` (API tasks)
- `oauth` (OAuth tasks)
- `testing` (Testing tasks)
- `documentation` (Documentation tasks)
- `p0-critical` (Critical priority)
- `p1-high` (High priority)
- `p2-medium` (Medium priority)
- `p3-low` (Low priority)

---

## 📅 SPRINT PLANNING

### Sprint 1 (Week 1-2): Foundation + MCP Setup 🆕

**Goal**: Database ready, MCP connected, models implemented

**Tasks** (28 points):
- HS-0.1: Setup HubSpot MCP Server (3 pts) 🆕
- HS-0.2: Implement MCP Client Wrapper (5 pts) 🆕
- HS-0.3: Setup Developer MCP Server (2 pts) 🆕
- HS-1.1: Design Database Schema (5 pts)
- HS-1.2: Create Database Migration (3 pts)
- HS-1.3: Implement Domain Models (5 pts)
- HS-1.4: Implement Repositories (5 pts)

**Deliverables**:
- ✅ Database schema deployed
- ✅ MCP client connected to HubSpot
- ✅ Developer MCP setup for team
- ✅ Domain models implemented
- ✅ Repositories with CRUD operations

---

### Sprint 2 (Week 3-4): HubSpot Adapter & Blog Publishing

**Goal**: Publish blog posts to HubSpot via Direct API

**Tasks** (34 points):
- HS-2.1: Implement HubSpot Adapter (8 pts)
- HS-2.2: Implement Markdown Converter (5 pts)
- HS-2.3: Implement Rate Limiter (5 pts)
- HS-2.4: Implement Error Handling (3 pts)
- HS-3.1: Implement Publish Use Case (8 pts)
- HS-3.2: Implement Metadata Handling (3 pts)
- HS-3.3: Integration Tests (2 pts)

**Deliverables**:
- ✅ HubSpot adapter with rate limiting
- ✅ Markdown → HTML conversion
- ✅ Blog post publishing working
- ✅ Integration tests passing

---

### Sprint 3 (Week 5): API & Frontend

**Goal**: UI for publishing content

**Tasks** (21 points):
- HS-4.1: Implement Publish Endpoint (5 pts)
- HS-4.2: Implement Status Endpoint (5 pts)
- HS-4.3: Implement Retry Endpoint (3 pts)
- HS-5.1: Implement Publish Button (5 pts)
- HS-5.2: Implement Status Tracking (3 pts)

**Deliverables**:
- ✅ API endpoints deployed
- ✅ Publish button in UI
- ✅ Status tracking dashboard
- ✅ Manual retry functionality

---

### Sprint 4 (Week 6-7): OAuth & Multi-Tenant

**Goal**: Production-ready multi-tenant system

**Tasks** (34 points):
- HS-6.1: Implement OAuth Flow (13 pts)
- HS-6.2: Implement Token Refresh (8 pts)
- HS-6.3: Implement Credential Management (8 pts)
- HS-6.4: Multi-Tenant Isolation (3 pts)
- HS-6.5: Admin UI for Credentials (2 pts)

**Deliverables**:
- ✅ OAuth 2.0 flow complete
- ✅ Automatic token refresh
- ✅ Multi-tenant credential management
- ✅ Admin UI for managing credentials

---

### Sprint 5 (Week 8): Advanced Features Part 1

**Goal**: Scheduling & social media

**Tasks** (15 points):
- HS-7.1: Implement Scheduled Publishing (8 pts)
- HS-7.2: Implement Social Media Publishing (5 pts)
- HS-7.4: Implement Retry Logic (2 pts)

**Deliverables**:
- ✅ Scheduled publishing
- ✅ Social media (LinkedIn) publishing
- ✅ Automatic retry on failure

---

### Sprint 6 (Week 9-10): Advanced Features Part 2 + Testing

**Goal**: Analytics, testing, documentation

**Tasks** (22 points):
- HS-7.3: Implement Performance Tracking (8 pts)
- HS-7.5: Implement A/B Testing (4 pts)
- HS-8.1: Integration Tests (3 pts)
- HS-8.2: E2E Tests (5 pts)
- HS-8.3: Documentation (2 pts)

**Deliverables**:
- ✅ Performance tracking from HubSpot
- ✅ A/B testing framework
- ✅ Complete test coverage
- ✅ Documentation complete

---

## ✅ PRE-IMPORT CHECKLIST

Before importing to Linear:

- [ ] Review roadmap with team
- [ ] Adjust estimates based on team velocity
- [ ] Assign team members to epics
- [ ] Create milestones in Linear
- [ ] Create labels in Linear
- [ ] Setup custom fields (Dependencies, Epic)
- [ ] Review sprint planning
- [ ] Get stakeholder approval

---

## 📊 POST-IMPORT ACTIONS

After importing to Linear:

### Week 1
- [ ] Kickoff meeting with team
- [ ] Review Sprint 1 tasks
- [ ] Setup HubSpot developer account
- [ ] Setup MCP Server (HS-0.1) 🆕
- [ ] Create database migration (HS-1.2)

### Week 2
- [ ] Daily standups
- [ ] Review MCP integration progress 🆕
- [ ] Review database schema
- [ ] Sprint 1 retrospective
- [ ] Plan Sprint 2

### Ongoing
- [ ] Weekly sprint planning
- [ ] Daily standups
- [ ] Bi-weekly demos to stakeholders
- [ ] Track velocity and adjust estimates
- [ ] Update documentation

---

## 🎯 SUCCESS CRITERIA

### MVP (Sprint 1-3)
- ✅ MCP client connected and working 🆕
- ✅ Blog posts published to HubSpot
- ✅ UI for publishing
- ✅ Basic error handling

### Production-Ready (Sprint 1-4)
- ✅ OAuth flow complete
- ✅ Multi-tenant support
- ✅ Token refresh automation
- ✅ Admin UI

### Complete (All Sprints)
- ✅ Scheduled publishing
- ✅ Social media publishing
- ✅ Performance tracking
- ✅ A/B testing
- ✅ Complete documentation

---

## 🚨 RISK MANAGEMENT

### High Priority Risks

1. **MCP Write Operations Non Disponibili** 🆕
   - **Impact**: High
   - **Mitigation**: Usa Direct API (già pianificato)
   - **Owner**: Backend Lead

2. **OAuth 2.1 Migration** 🆕
   - **Impact**: Medium
   - **Mitigation**: Monitor HubSpot changelog, test early
   - **Owner**: Backend Lead

3. **Rate Limiting**
   - **Impact**: Medium
   - **Mitigation**: Implement rate limiter (HS-2.3)
   - **Owner**: Backend Engineer

4. **Token Expiration**
   - **Impact**: Low
   - **Mitigation**: Background refresh job (HS-6.2)
   - **Owner**: Backend Engineer

---

## 📚 TRAINING PLAN

### Week 1: MCP & HubSpot Basics 🆕
- [ ] HubSpot MCP Server overview
- [ ] Developer MCP Server setup
- [ ] HubSpot API basics
- [ ] OAuth 2.0 flow

### Week 2: Development Setup
- [ ] Database schema review
- [ ] Repository pattern
- [ ] Adapter pattern
- [ ] Use case pattern

### Week 3: Testing & Deployment
- [ ] Integration testing
- [ ] E2E testing
- [ ] Deployment process
- [ ] Monitoring & alerts

---

## 🔗 USEFUL LINKS

### HubSpot
- [HubSpot MCP Server](https://developers.hubspot.com/mcp) 🆕
- [HubSpot Developer Platform](https://developers.hubspot.com/)
- [HubSpot API Docs](https://developers.hubspot.com/docs/api/overview)
- [HubSpot CLI](https://developers.hubspot.com/docs/cms/developer-reference/local-development-cli)

### MCP 🆕
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Specification](https://spec.modelcontextprotocol.io/)

### Internal
- [Codebase](https://github.com/FylleAI/CGS_2)
- [Supabase Dashboard](https://supabase.com/dashboard)
- [Linear Project](https://linear.app/)

---

**Last Updated**: 2025-10-25  
**Version**: 2.0 (Updated with MCP)  
**Status**: Ready for Import

