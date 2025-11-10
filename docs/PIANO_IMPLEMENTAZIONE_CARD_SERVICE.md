# 🃏 Piano di Implementazione - Card Service

## 🎯 Obiettivi Principali

- Normalizzare l'acquisizione del `CompanySnapshot` con schema stabile (v1).
- Generare e mantenere card atomiche persistenti per le quattro tipologie primarie (Prodotto/Servizio, Persona/Target, Campagna/Progetto, Tema/Topic).
- Trattare le card come **tool collaborativo** accessibile sia agli agenti CGS sia all'utente finale, con livelli di permesso granulari (read/edit/fetch/export).
- Esporre le card via API REST, webhook e SDK Python per orchestrazione CGS/Content Workflow e interazioni dirette utente.
- Integrare le card nel renderer registry frontend e standardizzare il consumo nel Content Workflow.

### 🔺 Core Concept Alignment (MVP)

1. **Motore di Workflow** → orchestration centrata sui contexts generati dalle card e sugli eventi `card.*`.
2. **Onboarding Utente** → principale fonte dei `CompanySnapshot` che alimentano la generazione e l'aggiornamento delle card.
3. **Card Interattive** → fonte di verità condivisa e strumento manipolabile (tool) da agenti e utenti, con audit e permessi controllati.

---

## 🧱 CompanySnapshot v1

| Sezione        | Campi principali |
|----------------|------------------|
| `company`      | `name`, `domain`, `industry`, `size`, `markets`, `positioning`, `competitors` |
| `offerings[]`  | `name`, `value_prop`, `features`, `differentiators`, `use_cases`, `pricing`, `kpi` |
| `audiences[]`  | `icp_name`, `segments`, `pains`, `goals`, `language`, `channels` |
| `voice`        | `tone`, `style_guides`, `brand_do_dont`, `compliance_notes` |
| `campaigns[]`  | `name`, `objectives`, `key_messages`, `tone`, `assets`, `results`, `learnings` |
| `topics[]`     | `topic`, `keywords`, `angles`, `related_content`, `trends` |
| `evidence`     | `sources`, `provenance`, `timestamps`, `confidence` |
| `meta`         | `snapshot_id`, `tenant_id`, `version`, `created_at`, `source_tooling` |

**Convenzioni comuni**: `uuid v7` per gli ID, versionamento semantico (`snapshot_version`, `card_version`), `locale` obbligatorio, `provenance` (`source`, `tool`, `model`, `timestamp`, `confidence`).

---

## 🂡 Card Persistenti

### Tipologie di prodotto

- **Prodotto/Servizio** → `value_prop`, `features[]`, `differentiators[]`, `use_cases[]`, `performance_metrics[]`
- **Persona/Target** → `icp_profile`, `pains[]`, `goals[]`, `preferred_language`, `channels[]`
- **Campagna/Progetto** → `objectives[]`, `key_messages[]`, `tone`, `assets[]`, `results`, `learnings`
- **Tema/Topic** → `topic`, `keywords[]`, `angles[]`, `related_content[]`, `trends`

### Card atomiche CGS/UI

- **Company Profile**
- **Audience**
- **Voice**
- **Insights**

Tutte le card includono: `id` (uuid v7), `tenant_id`, `snapshot_id`, `type`, `title`, `locale`, `content` (JSONB), `version`, `ui_schema`, `provenance`, `created_at`, `updated_at`.

### 🛠️ Card come Tool Collaborativo

- **Principio**: ogni card è un'entità interattiva manipolabile dagli agenti (automazioni CGS) e dagli utenti, con la stessa sorgente di verità.
- **Permessi**: livelli `read`, `comment`, `edit`, `share`, `export`; supporto a ruoli (`user`, `agent`, `service`) e delegation temporanea.
- **Azioni Tool**: `fetch`, `suggest_update`, `apply_update`, `pin_to_context`, `export_payload`, tutte tracciate con audit trail.
- **UI/SDK parity**: qualunque azione disponibile agli agenti deve avere equivalenza nell'SDK o via UI per l'utente.
- **Estensibilità**: nuove tipologie di card si definiscono tramite template registrati (nessun hard coding nei servizi).

---

## 🗄️ Schema Supabase (ridotto)

- `tenants`
  - `id`, `name`, `domain`, `created_at`
- `company_snapshots`
  - `id`, `tenant_id` (FK), `version`, `locale`, `payload` (JSONB), `created_at`, `created_by`, `hash_dedup` (unique), `provenance` (JSONB)
- `cards`
  - `id`, `tenant_id` (FK), `snapshot_id` (FK), `type` (ENUM), `title`, `locale`, `content` (JSONB), `version`, `ui_schema` (JSONB), `provenance` (JSONB), `created_at`, `updated_at`
- `card_templates`
  - `id`, `key` (unique), `title`, `description`, `content_schema` (JSONB schema), `default_ui_schema` (JSONB), `version`, `created_at`, `created_by`
- `card_access_policies`
  - `id`, `card_id` (FK), `principal_type` (`user|agent|service`), `principal_id`, `permissions` (ARRAY), `granted_by`, `granted_at`, `expires_at`
- `card_activity_log`
  - `id`, `card_id` (FK), `actor_type`, `actor_id`, `action`, `payload` (JSONB), `created_at`
- `events`
  - `id`, `type`, `payload` (JSONB), `status` (`pending|published|failed`), `created_at`

**Indici**: `idx_cards_tenant_type_locale`, `idx_snapshots_tenant_version`, indici GIN su JSONB, `idx_card_access_card_principal`, `idx_card_templates_key`.

---

## 🧩 Template Registry & Estendibilità

- **Registrazione dinamica**: i template definiscono shape dei campi (`content_schema` JSON Schema) e metadati UI (`default_ui_schema`).
- **Versionamento template**: ogni cambiamento breaking produce nuova `version`; le card indicano `template_version` per compatibilità.
- **Lifecycle**:
  1. Creazione template (admin/lead) → `POST /v1/card-templates`.
  2. Validazione automatica (`content_schema` coerente con linee guida CGS).
  3. Pubblicazione evento `card.template.published` consumato da frontend e agenti per aggiornare il registry locale.
- **No hard coding**: gli agenti caricano dinamicamente il catalogo template e possono istanziare card per nuove tipologie senza deploy.
- **Fallback**: se un template non è disponibile localmente, il tool richiede on-demand via API e cache con TTL.

---

## 🔌 API & SDK

### REST Endpoints

- `POST /v1/snapshots` → persiste `CompanySnapshot v1`, genera card, emette `card.generated`
- `GET /v1/cards?tenant_id=&type=&locale=&snapshot_id=`
- `GET /v1/cards/{card_id}`
- `GET /v1/contexts/content?tenant_id=&locale=&types=product,persona,voice,insights`
- `POST /v1/cards/{card_id}/refresh`
- `POST /v1/cards/rebuild?snapshot_id=`
- `GET /v1/card-templates` / `POST /v1/card-templates` → gestione template dinamici
- `POST /v1/cards/{card_id}/actions/{action}` → esecuzione tool (`suggest_update`, `apply_update`, `export_payload`, ...)
- `PUT /v1/cards/{card_id}/permissions` → gestione ACL granulari (grant/revoke, delega temporanea)

### Webhook

- `card.generated`
- `card.updated`
- `snapshot.ingested`
- `card.permission.updated`
- `card.template.published`

### SDK Python

- `cards.create_from_snapshot(snapshot)`
- `cards.get(type, tenant_id, locale)`
- `contexts.build_for_generation(tenant_id, types, locale)`
- `cards.register_template(template_definition)`
- `cards.execute_action(card_id, action, payload=None, actor=None)`
- `cards.share(card_id, principal, permissions, expires_at=None)`
- Helpers: mapping `CompanySnapshot` → schema card, validazioni Pydantic.

### Tool Interface Contracts

- **Actor Awareness**: tutte le chiamate tool devono includere `actor_type`, `actor_id`, `actor_context` per audit e decisioni di autorizzazione.
- **Permission Check**: middleware comune che risolve le policy e valuta override temporanei.
- **Version Safety**: azioni mutative richiedono `if-match` con `card_version` per garantire conflitti gestiti.
- **Suggested vs Applied**: gli agenti possono proporre modifiche (`suggest_update`) che restano in stato `pending` finché l'utente non approva tramite UI o regole automatizzate.

---

## 🔁 Integrazioni

### Onboarding → Card Service

- Output normalizzato `CompanySnapshot v1` (con `provenance`, `hash_dedup`).
- Contratto: `Content-Type: application/json; profile=company-snapshot-v1`.
- Validazioni: schema rigido, normalizzazione stringhe, fallback valori mancanti.
- Persistenza: crea snapshot se hash differente, genera card atomiche + tipologie prodotto.
- Policy iniziali: grant automatico `read/edit/export` al tenant owner, `read` agli agenti di workflow registrati.

### Content Workflow & CGS → Card Service

- `contexts.build_for_generation` restituisce `topic_context`, `audience_context`, `voice_guidelines`, `insights_context` (+ eventuale `RAG_texts`).
- Fallback se card mancanti: pipeline legacy o default sicuri.
- Tracciamento: `context_id`, `snapshot_id`, `card_ids`, `versions` nei metadata dei job.
- RAG: endpoint export testi normalizzati (`GET /v1/cards/export?format=plain`).
- Tool usage: gli agenti invocano `suggest_update` per proporre miglioramenti e `pin_to_context` per rendere esplicita la selezione delle card.

---

## 🎨 Renderer Registry Frontend

- Registry: `type → component` (`product → FylleCard.Product`, `persona → FylleCard.Persona`, `campaign → FylleCard.Campaign`, `topic → FylleCard.Topic`, `company/audience/voice/insights → dedicated`).
- Contract UI: `content` con shape minimale e stabile, `ui_schema` per varianti.
- Coerenza visiva: un singolo componente `FylleCard` con slot per varianti.

---

## 🛣️ Roadmap (3 Sprint)

### Sprint 1 – Fondamenta

1. Definire schema Pydantic (`CompanySnapshot v1`, `Card v1`, `Context v1`).
2. Definire modelli `CardTemplate` e `CardAccessPolicy` con migrazioni Supabase.
3. Implementare `POST /v1/snapshots` (validazione + persistenza + generazione card atomiche).
4. Abilitare `GET /v1/cards`, `GET /v1/card-templates` e metodo SDK `cards.get()`.
5. Implementare grant automatico permessi baseline (tenant owner + agenti).
6. Accettazione: snapshot → card atomiche persistite, ACL baseline attive, query per `tenant/type` funzionante.

### Sprint 2 – Tipologie e Contexts

1. Mappare card Prodotto/Persona/Campagna/Topic dallo snapshot e registrare i template corrispondenti.
2. Implementare `GET /v1/contexts/content` + SDK `contexts.build_for_generation()`.
3. Abilitare webhook `card.generated` e integrazione minima Content Workflow.
4. Implementare API azioni tool (`/actions/{action}`) con audit log e flusso `suggest_update` → `pending`.
5. Export testi per RAG (`GET /v1/cards/export?format=plain`).
6. Accettazione: CGS consuma contexts, job metadata con versioni/ID, agenti possono proporre aggiornamenti controllati.

### Sprint 3 – Frontend & Hardening

1. Registry frontend + componenti `FylleCard*` per tipologie/atomiche, caricamento dinamico template.
2. Endpoint `refresh/rebuild`, dedup e idempotenza.
3. UX per tool condiviso: approvazione aggiornamenti, gestione permessi e cronologia.
4. Observability (tracing, metrics, audit provenance) con focus su azioni tool e permessi.
5. Hardening: rate limit, pagination, fallback locale.
6. Accettazione: UI coerente, rebuild deterministico, telemetria attiva, esperienza tool condiviso stabilizzata.

---

## ✅ Criteri di Accettazione Trasversali

- Stabilità schema (`version`, `ids` in tutte le risposte; breaking change → v2).
- Idempotenza (`POST /snapshots` con stesso hash non duplica record).
- Completezza (contexts includono almeno audience, voice, product o insights).
- Performance P95: `create_from_snapshot ≤ 2.5s`; `contexts.get ≤ 200ms` (cache-hit) / `≤ 600ms` (miss).
- Sicurezza: isolamento per tenant, auth middleware, audit log.

---

## ⚠️ Rischi & Mitigazioni

| Rischio | Mitigazione |
|---------|-------------|
| Snapshot incompleto | Validazioni soft, default sicuri, flag `partial`. |
| Drift dello schema | Contract test tra Onboarding, Card Service, Content Workflow. |
| Drift UI | `ui_schema` versionato + visual regression test. |
| Permessi incoerenti | Policy centralizzate, audit trail completo e simulatore permessi nei test end-to-end. |
| Duplicati snapshot | `hash_dedup` su payload normalizzato. |

