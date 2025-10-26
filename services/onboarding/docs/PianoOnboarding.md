/docs/CGS.onboarding.analysis.md
CGS Onboarding – Analisi tecnica
1. Panoramica architetturale
CGS_2 espone un backend FastAPI con router v1 per contenuti, workflow, agenti, sistema, logging e knowledge base; la configurazione avviene in api/rest/main.py e monta middleware CORS, logging e handler di eccezioni.

Il dominio modella contenuti, workflow, task e agent attraverso entità e value object fortemente tipizzate, mantenendo la logica business indipendente dalle infrastrutture.

Il caso d’uso GenerateContentUseCase orchestra il flusso: costruisce il contesto dinamico, registra strumenti (web search, RAG, Perplexity), avvia il workflow, persiste il contenuto e aggiorna il tracker Supabase.

Le integrazioni esterne sono incapsulate in adapter: LLMProviderFactory istanzia provider (OpenAI, Anthropic, DeepSeek, Gemini), mentre GeminiAdapter supporta API key o Vertex SA; strumenti come PerplexityResearchTool, WebSearchTool e RAGTool forniscono funzionalità modulari riutilizzabili.

La configurazione centralizza segreti, retry e directory con Pydantic Settings, garantendo la creazione preventiva delle cartelle necessarie.

2. Layer e moduli
Interfaccia (API REST)
/api/v1/content/generate accetta ContentGenerationRequestModel ricca di parametri (topic, workflow_type, target audience, RAG docs) e restituisce ContentGenerationResponseModel con output, metriche e immagini facoltative.

/api/v1/workflows espone l’elenco dinamico e l’esecuzione asincrona di workflow registrati.

/api/v1/knowledge-base consente CRUD documenti, anteprime e backfill embedding contro Supabase; fornisce anche un formato ottimizzato per il frontend.

/api/v1/system aggrega health/config, sfruttando Settings per enumerare provider, storage e DB.

/api/v1/logs fornisce sintesi, performance agent e breakdown costi basati sui log strutturati di agent_logger e workflow_reporter.

La middleware LoggingMiddleware traccia tempo di risposta e richieste, ma non è presente autenticazione o rate-limiting nativi.

Application & Domain
Il caso d’uso costruisce il contesto aggiungendo agent executor, repository e tracker, inietta parametri di generazione e gestisce fallback su workflow legacy via TaskOrchestrator se un workflow dinamico non è registrato.

Il dominio dei contenuti traccia metriche, versioning e regole di stato, fungendo da contratto di persistenza per repository file/Supabase.

Infrastruttura e strumenti
execute_dynamic_workflow garantisce che agent_repository (YAML) e agent_executor siano disponibili, registra tool canonici e ripulisce l’output da oggetti non serializzabili, mantenendo il pattern port/adapter.

Gli agenti sono definiti in YAML per profilo cliente ed esposti tramite YamlAgentRepository, supportando ricerca, filtri per ruolo/tool e aggiornamenti asincroni.

SupabaseTracker fornisce run lifecycle, logging dettagliato, cost ledger e tracciamento RAG/documenti, mentre workflow_reporter aggrega metriche di workflow a partire dai log agent.

Il knowledge base persistente utilizza schema SQL con tabelle clients, documents, content_generations, policy RLS e indici dedicati; il tracking utilizza workflow_runs, agent_executions, run_cost_events per analytics granulari.

3. Workflow & orchestrazione
WorkflowRegistry registra handler via decorator, gestisce cache, crea agent executor e tool (Serper, RAG, Perplexity, image generation, brand style) e invoca l’handler asincrono.

WorkflowHandler definisce il ciclo: validazione, preparazione, creazione tasks da template JSON, esecuzione, post-processing e raccolta metriche, con tracking automatico sul reporter.

Template JSON modellano variabili e task per enhanced_article e premium_newsletter, allineati ai metodi di validazione/contesto nei rispettivi handler (topic, client_name, premium_sources, target_word_count, etc.).

TaskOrchestrator rimane disponibile come fallback/legacy, con gestione dipendenze, template substitution e update dello stato workflow.

4. Persistenza, knowledge base e analytics
I documenti KB vengono letti/scritti tramite Supabase o fallback filesystem; il tool RAG supporta selezione documenti per run e traccia retrieval verso il tracker.

Le API /knowledge-base/... usano Supabase per elencare, recuperare, caricare e indicizzare documenti, costruendo preview e filtrando per tag/testo.

Il caso d’uso salva contenuti via repository e, se configurato, registra l’output come content_generations in Supabase, riutilizzabile per card KB o auditing.

5. Autenticazione, sicurezza e limiti
Pur esistendo secret_key e parametri di sicurezza nei settings, l’API pubblica non applica ancora JWT o rate limit: ogni endpoint è accessibile senza Depends di autenticazione o throttling; occorrerà introdurre guardie nell’adapter esterno per evitare abuso.

Configurare CORS, directory dei dati, tool cost override e timeout è possibile via env, utile per separare ambienti e minimizzare privilegi.

6. Payload/response correnti per i workflow
ContentGenerationRequestModel definisce il payload accettato (topic, workflow_type, target audience, parametri newsletter, RAG docs) e ContentGenerationResponseModel restituisce corpo, metriche, immagini e metadata; WorkflowExecutionRequest/Response offrono alternativa low-level per orchestrazione diretta.

Il workflow premium_newsletter richiede topic/premium_sources/target audience; enhanced_article esige topic, client_name e optional su tono/statistiche. La costruzione del payload onboarding dovrà rispettare questi contratti.

7. Interfacce pubbliche e extension points
Nuovi workflow possono registrarsi via @register_workflow, fornendo template JSON e handler dedicati senza modificare core.

Nuovi agent/ruoli si aggiungono creando YAML in data/profiles/<client>/agents, sfruttando repository e tool registry dell’AgentExecutor.

Tool esterni supplementari si innestano chiamando agent_executor.register_tools, mantenendo naming canonico (ToolNames).

Logging/analytics possono essere estesi tramite workflow_reporter, agent_logger e tracker Supabase, già predisposti per cost breakdown e log granulari.

8. Inserimento di un Onboarding Adapter esterno
L’adapter raccoglie input user, invoca Perplexity per ricerca esterna e alimenta Gemini per la sintesi e la generazione delle tre domande chiarificatrici, riusando gli adapter nativi (timeout, cost tracking già gestiti).

Arricchisce il CompanySnapshot, raccoglie le risposte follow-up e costruisce un ContentGenerationRequest coerente con ContentGenerationRequestModel, popolando campi workflow-specifici prima di chiamare /api/v1/content/generate o /api/v1/workflows/execute con session_id idempotente.

Aggrega run_id e trace id condiviso per log/metriche, sfruttando SupabaseTracker per cost ledger e save_run_content per produrre la knowledge-base card immediata.

L’adapter rimane fuori da CGS, operando come port/adapter: costruisce payload versionati, invoca API pubbliche, osserva risposte, orchestra delivery Brevo e archivia su Supabase, senza introdurre breaking change.

9. State machine (testuale breve)
created -> researching -> synthesizing -> awaiting_user -> payload_ready -> executing -> delivering -> done|failed

10. Sequence (pseudocode)
POST /onboarding -> enrich(Perplexity) -> synth(Gemini) -> ask(3 Q) -> buildPayload(goal) -> CGS/execute -> Brevo/send -> persist(Supabase)
11. Rischi & mitigazioni
Schema drift tra adapter e CGS – gli handler validano campi (topic, client_name, premium_sources) e generano errori se assenti; versionare i payload e introdurre contract test contro /api/v1/content/generate.

Suggested task
Stabilizzare i contratti CGS prima del rollout

Start task
Latenza/timeout provider AI – Gemini Vertex e Perplexity prevedono timeout configurabili; l’adapter deve propagare timeouts e fallback per mantenere UX fluida.

Suggested task
Gestire timeouts e fallback provider

Start task
Rate limit provider – i tool non implementano throttling; l’adapter deve fare budgeting richieste Perplexity/Gemini e loggare costi via tracker.

Suggested task
Applicare rate-limit e budgeting lato onboarding

Start task
Contenuti vuoti o parziali – WorkflowHandler dipende da output final_output; introdurre validazioni extra sull’adapter e fallback se body vuoto.

Suggested task
Validare l’output CGS prima della delivery

Start task
Deliverability email Brevo – CGS non gestisce email; l’adapter deve gestire idempotenza invio e fallback su storage Supabase in caso di errore SMTP (Brevo).

Suggested task
Garantire consegna email affidabile

Start task
12. Osservabilità e tracing
Ogni agent execution produce log strutturati (agent_logger) e cost event run_cost_events; mantenere session_id/trace_id condivisi tra onboarding, CGS e Brevo per correlare richieste.

workflow_reporter aggrega costi e success rate, esposizione già prevista dagli endpoint logging per consultazione rapida.

13. Domande aperte (blocking)
Limiti massimi (lunghezza, attachment) accettati dai workflow CGS oltre a quanto validato dagli handler?

Enumerazione ufficiale dei workflow “goal” da esporre in onboarding (esiste un mapping linkedin_post → enhanced_article lato CGS)?

Semantica degli errori CGS (error_message, HTTP status) e policy di retry suggerita?

Preferenza CGS per webhook vs polling sul completamento workflow (oggi la risposta è sincrona, ma per run lunghi serve callback)?

Struttura target della knowledge-base card (HTML/CSS) e limiti di storage in Supabase/KB?

/docs/CGS.onboarding.plan.md
CGS Onboarding – Piano di implementazione
MVP (Fase essenziale, rischio basso)
Onboarding Adapter Service – Endpoint esterno che riceve input utente (brand, sito, goal) e genera session_id idempotente; mantiene stato sessione in Supabase (nuova tabella onboarding_sessions) con riferimenti al run CGS (workflow_runs).

Modulo ricerca & sintesi – Client asincroni verso Perplexity (ricerca pubblica) e Gemini (sintesi snapshot + domande); riutilizzano logica di timeout/costi degli adapter esistenti per coerenza con CGS.

Gestione follow-up – Persistenza Q&A nel record sessione con versione snapshot; garantire mapping domande→risposte per arricchire il payload.

Costruzione payload CGS – Mapper che prende snapshot, risposte e goal e compila ContentGenerationRequest/WorkflowExecutionRequest coerenti con i template enhanced_article o premium_newsletter (topic, client_name, premium_sources, tone, target_word_count, etc.).

Invocazione CGS – Chiamata a /api/v1/content/generate con session_id e trace_id nei metadata; gestione di risposta sincrona (success/failure) e memorizzazione content_id/workflow_metrics.

Persistenza Supabase – Salvare snapshot, payload, risposta CGS e stato delivery in tabelle dedicate, collegandole a workflow_runs per analytics cross-sistema.

Delivery Brevo (baseline) – Inviare email transazionale con contenuto generato e link alla knowledge-base card; loggare stato per eventuali retry manuali.

Knowledge-base card – Comporre card HTML/JSON da snapshot+output e salvarla su Supabase (content_generations.metadata) per immediate reuse dai workflow CGS.

Dipendenze e responsabilità
Sequenza: creare sessione → ricerca Perplexity → sintesi Gemini → Q&A → assemble payload → chiamare CGS → salvare/mandare output → archiviare card.

Prerequisiti: API key Perplexity/Gemini, credenziali Brevo, Supabase URL/key, URL CGS e secret.

Deliverable principali: Onboarding API, mapping contratti v1, storage Supabase, job di delivery.

Hardening
Osservabilità – Propagare trace_id, integrare con SupabaseTracker (log_llm_call, log_tool_execution) e arricchire workflow_metrics nel ResultEnvelope.

Retry & idempotenza – Applicare retry esponenziale su provider esterni e CGS (solo errori transitori), rispettando Settings.max_retries come cap, e usare session_id come chiave idempotente per non duplicare run/email.

Timeout dichiarati – Allineare timeouts adapter con quelli dei client CGS (Gemini GEMINI_HTTP_TIMEOUT_SECONDS, Perplexity 30s) e fallire rapidamente in onboarding se superati.

Dead-letter & alerting – Introdurre coda per delivery Brevo fallite e allarmi sul canale operativo.

Security posture – Isolare segreti in store sicuro, applicare principio del minimo privilegio su chiavi Supabase/Brevo e cifrare snapshot sensibili prima di logging.

Testabilità – Creare fake adapter CGS/Perplexity/Gemini per dry-run end-to-end con injection nella pipeline.

Estensioni
Nuovi workflow – Mappare obiettivi aggiuntivi (es. whitepaper) ai template CGS, riutilizzando register_workflow e aggiungendo contratti payload specifici.

Caching ricerca – Memorizzare risultati Perplexity/Supabase per ridurre costi e latenza per brand ricorrenti.

Preset tonalità/brand – Arricchire snapshot con preferenze da Supabase (clients, documents) per precompilare campi tone/custom instructions.

A/B test prompt – Annotare versione prompt in payload e confrontare metriche di engagement tramite workflow_metrics/delivery analytics.

Definition of Done
Onboarding adapter produce CompanySnapshot, tre domande e raccoglie risposte persistendo in Supabase.

Chiamata CGS riuscita per almeno enhanced_article e premium_newsletter, con ContentGenerationResponseModel popolato e salvato per audit.

Email Brevo inviata (o in coda) con link alla knowledge-base card salvata in Supabase.

Metriche base registrate: tempo end-to-end, successo/errore, costi per provider.

Test automatici: contract test payload→CGS, dry-run e fault injection 429/5xx su provider.

Criteri di rollback
Errore ≥5% nelle chiamate CGS o tempo end-to-end > SLA per 3 run consecutivi → disattivare onboarding adapter (feature flag) e reindirizzare utenti al flusso manuale.

Deliverability Brevo <95% in 24h → sospendere invii automatici e notificare via Supabase run log.

Metriche (monitoraggio continuo)
Time to Value (TTV) – tempo dalla creazione sessione a contenuto consegnato (logging session start + delivery timestamp).

Success rate – percentuale run completati vs falliti dal tracker CGS (workflow_metrics.success_rate).

Error rate provider – conteggio errori Perplexity/Gemini per tipo (429, timeout) nel ledger costi.

Latency CGS – execution_time / duration_seconds dal response CGS.

Deliverability – success/fail email da Brevo, correlato al session_id.

/docs/CGS.onboarding.contracts.md
CGS Onboarding – Contratti
Versionamento e compatibilità
I contratti sono versionati v1.0. Ogni payload include version e session_id per idempotenza.

I campi derivano dai requisiti degli handler CGS (enhanced_article, premium_newsletter) e dai modelli API (ContentGenerationRequestModel, ContentGenerationResponseModel, WorkflowMetricsModel).

Compatibilità: versioni 1.x devono restare backward-compatible (solo aggiunte opzionali). Incremento major richiesto per breaking changes.

CompanySnapshot v1
Snapshot post-Gemini che consolida ricerca Perplexity, sintesi Gemini e risposte follow-up.

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://fylle.ai/schemas/company_snapshot.v1.json",
  "title": "CompanySnapshot",
  "type": "object",
  "required": [
    "version",
    "snapshot_id",
    "generated_at",
    "company",
    "audience",
    "voice",
    "insights",
    "clarifying_questions"
  ],
  "properties": {
    "version": {
      "type": "string",
      "enum": ["1.0"]
    },
    "snapshot_id": {
      "type": "string",
      "format": "uuid"
    },
    "generated_at": {
      "type": "string",
      "format": "date-time"
    },
    "trace_id": {
      "type": "string"
    },
    "company": {
      "type": "object",
      "required": ["name", "description"],
      "properties": {
        "name": { "type": "string", "minLength": 1 },
        "legal_name": { "type": "string" },
        "website": { "type": "string", "format": "uri", "nullable": true },
        "industry": { "type": "string" },
        "headquarters": { "type": "string" },
        "size_range": { "type": "string" },
        "description": { "type": "string" },
        "key_offerings": { "type": "array", "items": { "type": "string" } },
        "differentiators": { "type": "array", "items": { "type": "string" } },
        "evidence": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["source", "excerpt"],
            "properties": {
              "source": { "type": "string", "format": "uri-reference" },
              "excerpt": { "type": "string" },
              "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
            }
          }
        }
      },
      "additionalProperties": false
    },
    "audience": {
      "type": "object",
      "properties": {
        "primary": { "type": "string" },
        "secondary": { "type": "array", "items": { "type": "string" } },
        "pain_points": { "type": "array", "items": { "type": "string" } },
        "desired_outcomes": { "type": "array", "items": { "type": "string" } }
      },
      "additionalProperties": false
    },
    "voice": {
      "type": "object",
      "properties": {
        "tone": { "type": "string" },
        "style_guidelines": { "type": "array", "items": { "type": "string" } },
        "forbidden_phrases": { "type": "array", "items": { "type": "string" } },
        "cta_preferences": { "type": "array", "items": { "type": "string" } }
      },
      "additionalProperties": false
    },
    "insights": {
      "type": "object",
      "properties": {
        "positioning": { "type": "string" },
        "key_messages": { "type": "array", "items": { "type": "string" } },
        "recent_news": { "type": "array", "items": { "type": "string" } },
        "competitors": { "type": "array", "items": { "type": "string" } }
      },
      "additionalProperties": false
    },
    "clarifying_questions": {
      "type": "array",
      "minItems": 1,
      "maxItems": 3,
      "items": {
        "type": "object",
        "required": ["id", "question", "reason", "expected_response_type"],
        "properties": {
          "id": { "type": "string" },
          "question": { "type": "string" },
          "reason": { "type": "string" },
          "expected_response_type": {
            "type": "string",
            "enum": ["string", "enum", "boolean", "number"]
          },
          "options": { "type": "array", "items": { "type": "string" } },
          "required": { "type": "boolean", "default": true }
        },
        "additionalProperties": false
      }
    },
    "clarifying_answers": {
      "type": "object",
      "patternProperties": {
        "^q[0-9]+$": { "type": ["string", "number", "boolean", "array", "object", "null"] }
      }
    },
    "source_metadata": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["tool", "timestamp"],
        "properties": {
          "tool": { "type": "string" },
          "timestamp": { "type": "string", "format": "date-time" },
          "cost_usd": { "type": "number", "minimum": 0 },
          "token_usage": { "type": "integer", "minimum": 0 }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
CgsPayload v1 – linkedin_post → enhanced_article
Payload destinato al workflow enhanced_article, arricchito per output stile LinkedIn (tono, CTA, hashtag) ma compatibile con i template e le validazioni CGS.

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://fylle.ai/schemas/cgs_payload.linkedin_post.v1.json",
  "title": "CgsPayloadLinkedInPost",
  "type": "object",
  "required": ["version", "session_id", "workflow", "goal", "input", "company_snapshot"],
  "properties": {
    "version": { "type": "string", "enum": ["1.0"] },
    "session_id": { "type": "string", "format": "uuid" },
    "workflow": { "type": "string", "const": "enhanced_article" },
    "goal": { "type": "string", "const": "linkedin_post" },
    "trace_id": { "type": "string" },
    "company_snapshot": {
      "$ref": "company_snapshot.v1.json"
    },
    "clarifying_answers": {
      "type": "object",
      "description": "Echo delle risposte utente alle domande chiarificatrici",
      "patternProperties": {
        "^q[0-9]+$": { "type": ["string", "number", "boolean", "array", "object", "null"] }
      }
    },
    "input": {
      "type": "object",
      "required": ["topic", "client_name", "target_audience", "tone"],
      "properties": {
        "topic": { "type": "string", "minLength": 3 },
        "client_name": { "type": "string", "minLength": 1 },
        "client_profile": { "type": "string", "default": "default" },
        "context": { "type": "string" },
        "target_audience": { "type": "string" },
        "tone": {
          "type": "string",
          "enum": ["professional", "authoritative", "conversational", "playful", "bold"]
        },
        "call_to_action": { "type": "string" },
        "key_points": { "type": "array", "items": { "type": "string" } },
        "hashtags": { "type": "array", "items": { "type": "string" }, "maxItems": 10 },
        "target_word_count": { "type": "integer", "minimum": 50, "maximum": 800, "default": 220 },
        "include_statistics": { "type": "boolean", "default": true },
        "include_examples": { "type": "boolean", "default": true },
        "include_sources": { "type": "boolean", "default": true },
        "custom_instructions": { "type": "string" },
        "post_format": {
          "type": "string",
          "enum": ["thought_leadership", "event_promo", "product_launch", "talent_branding"],
          "default": "thought_leadership"
        },
        "hero_quote": { "type": "string" },
        "image_prompt": { "type": "string" }
      },
      "additionalProperties": false
    },
    "metadata": {
      "type": "object",
      "properties": {
        "source": { "type": "string", "const": "onboarding_adapter" },
        "dry_run": { "type": "boolean", "default": false },
        "requested_provider": { "type": "string" },
        "language": { "type": "string", "default": "it" }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
CgsPayload v1 – newsletter → premium_newsletter
Payload allineato al workflow premium_newsletter, comprendente sorgenti premium e distribuzione sezioni.

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://fylle.ai/schemas/cgs_payload.newsletter.v1.json",
  "title": "CgsPayloadNewsletter",
  "type": "object",
  "required": ["version", "session_id", "workflow", "goal", "input", "company_snapshot"],
  "properties": {
    "version": { "type": "string", "enum": ["1.0"] },
    "session_id": { "type": "string", "format": "uuid" },
    "workflow": { "type": "string", "const": "premium_newsletter" },
    "goal": { "type": "string", "const": "newsletter_premium" },
    "trace_id": { "type": "string" },
    "company_snapshot": { "$ref": "company_snapshot.v1.json" },
    "clarifying_answers": {
      "type": "object",
      "patternProperties": {
        "^q[0-9]+$": { "type": ["string", "number", "boolean", "array", "object", "null"] }
      }
    },
    "input": {
      "type": "object",
      "required": ["topic", "target_audience"],
      "properties": {
        "topic": { "type": "string", "minLength": 5 },
        "newsletter_topic": { "type": "string" },
        "client_name": { "type": "string" },
        "client_profile": { "type": "string", "default": "default" },
        "target_audience": { "type": "string", "minLength": 3 },
        "target_word_count": { "type": "integer", "minimum": 800, "maximum": 2500, "default": 1200 },
        "edition_number": { "type": "integer", "minimum": 1, "default": 1 },
        "premium_sources": {
          "type": "array",
          "items": { "type": "string", "format": "uri" },
          "maxItems": 10
        },
        "exclude_topics": { "type": "array", "items": { "type": "string" } },
        "priority_sections": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": [
              "executive_summary",
              "market_highlights",
              "premium_insights",
              "expert_analysis",
              "recommendations",
              "market_outlook",
              "client_cta"
            ]
          }
        },
        "custom_instructions": { "type": "string" },
        "section_overrides": {
          "type": "object",
          "additionalProperties": { "type": "string" }
        },
        "cta_variants": { "type": "array", "items": { "type": "string" } },
        "compliance_notes": { "type": "string" }
      },
      "additionalProperties": false
    },
    "metadata": {
      "type": "object",
      "properties": {
        "source": { "type": "string", "const": "onboarding_adapter" },
        "requested_provider": { "type": "string" },
        "language": { "type": "string", "default": "it" },
        "dry_run": { "type": "boolean", "default": false }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
ResultEnvelope v1
Envelope restituito all’onboarding dopo la chiamata CGS, riflettendo ContentGenerationResponseModel e WorkflowMetricsModel, con informazioni delivery e Supabase.

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://fylle.ai/schemas/result_envelope.v1.json",
  "title": "ResultEnvelope",
  "type": "object",
  "required": ["version", "session_id", "workflow", "status", "content"],
  "properties": {
    "version": { "type": "string", "enum": ["1.0"] },
    "session_id": { "type": "string", "format": "uuid" },
    "trace_id": { "type": "string" },
    "workflow": { "type": "string" },
    "goal": { "type": "string" },
    "status": { "type": "string", "enum": ["completed", "failed"] },
    "cgs_run_id": { "type": "string", "format": "uuid" },
    "supabase_run_id": { "type": "string", "format": "uuid" },
    "error": {
      "type": "object",
      "required": ["message"],
      "properties": {
        "message": { "type": "string" },
        "code": { "type": "string" },
        "retryable": { "type": "boolean" }
      },
      "additionalProperties": false
    },
    "content": {
      "type": "object",
      "required": ["title", "body"],
      "properties": {
        "content_id": { "type": "string", "format": "uuid" },
        "title": { "type": "string" },
        "body": { "type": "string" },
        "format": {
          "type": "string",
          "enum": ["markdown", "html", "plain_text", "json"],
          "default": "markdown"
        },
        "word_count": { "type": "integer", "minimum": 0 },
        "character_count": { "type": "integer", "minimum": 0 },
        "reading_time_minutes": { "type": "number", "minimum": 0 },
        "metadata": { "type": "object" },
        "generated_image": { "type": "object" },
        "image_metadata": { "type": "object" }
      },
      "additionalProperties": false
    },
    "workflow_metrics": {
      "type": ["object", "null"],
      "properties": {
        "total_cost": { "type": "number", "minimum": 0 },
        "total_tokens": { "type": "integer", "minimum": 0 },
        "duration_seconds": { "type": "number", "minimum": 0 },
        "agents_used": { "type": "integer", "minimum": 0 },
        "success_rate": { "type": "number", "minimum": 0, "maximum": 1 },
        "tasks_completed": { "type": "integer", "minimum": 0 },
        "tasks_failed": { "type": "integer", "minimum": 0 },
        "tool_calls": { "type": "integer", "minimum": 0 },
        "llm_calls": { "type": "integer", "minimum": 0 },
        "cost_by_provider": { "type": "object" },
        "cost_by_agent": { "type": "object" }
      },
      "additionalProperties": false
    },
    "delivery": {
      "type": "object",
      "properties": {
        "channel": { "type": "string", "enum": ["email", "webhook", "none"] },
        "recipient": { "type": "string" },
        "status": { "type": "string", "enum": ["pending", "sent", "failed"] },
        "timestamp": { "type": "string", "format": "date-time" },
        "message_id": { "type": "string" }
      },
      "additionalProperties": false
    },
    "knowledge_base_card": {
      "type": "object",
      "properties": {
        "storage_url": { "type": "string", "format": "uri" },
        "format": { "type": "string", "enum": ["html", "json"] }
      },
      "additionalProperties": false
    },
    "logs": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["timestamp", "level", "message"],
        "properties": {
          "timestamp": { "type": "string", "format": "date-time" },
          "level": { "type": "string" },
          "message": { "type": "string" },
          "metadata": { "type": "object" }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
Policy di compatibilità
Aggiunte opzionali (workflow_metrics, knowledge_base_card) non devono rompere client esistenti; nuovi campi devono essere opzionali.

Qualsiasi modifica a tipi obbligatori richiede bump a 2.0 e migrazione coordinata.

session_id e trace_id garantiscono deduplicazione e correlazione cross-sistema con SupabaseTracker/Brevo.