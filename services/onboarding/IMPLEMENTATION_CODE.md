# 💻 IMPLEMENTAZIONE CODICE: Profili Dinamici e Knowledge Base

**Versione**: 1.0  
**Data**: 2025-10-14  
**Riferimento**: [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)

---

## 📋 INDICE

1. [Task 2.1: Create Client Profile](#task-21-create-client-profile)
2. [Task 2.2: Populate Knowledge Base](#task-22-populate-knowledge-base)
3. [Task 3.1: Context Injection](#task-31-context-injection)
4. [Task 3.2: Profile Cache](#task-32-profile-cache)
5. [Integrazioni](#integrazioni)

---

## 🎯 Task 2.1: Create Client Profile

### File: `onboarding/application/use_cases/create_client_profile.py`

```python
"""Use case per creare profilo CGS dinamico da snapshot onboarding."""

from typing import Dict, Any
from uuid import UUID
import httpx
from pathlib import Path
import yaml
import logging

from onboarding.domain.models import CompanySnapshot
from onboarding.config.settings import OnboardingSettings

logger = logging.getLogger(__name__)


class CreateClientProfileUseCase:
    """Crea profilo CGS personalizzato da snapshot onboarding."""
    
    def __init__(self, settings: OnboardingSettings):
        self.settings = settings
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_anon_key
        self.profiles_dir = Path("data/profiles")
    
    async def execute(
        self,
        snapshot: CompanySnapshot,
        brand_name: str,
    ) -> Dict[str, Any]:
        """
        Crea profilo CGS completo.
        
        Steps:
        1. Crea entry in Supabase clients table
        2. Crea directory profilo in data/profiles/{brand_name}
        3. Copia agent template da default
        4. Personalizza agent con snapshot info
        
        Args:
            snapshot: Snapshot onboarding con info brand
            brand_name: Nome brand (es. "Fylle", "TestBrand")
        
        Returns:
            Dict con:
            - profile_name: Nome profilo normalizzato
            - client_id: UUID client in Supabase
            - agents_created: Lista agent creati
            - profile_path: Path directory profilo
        """
        logger.info(f"Creating CGS profile for brand: {brand_name}")
        
        # Normalizza brand name per filesystem
        profile_name = self._normalize_profile_name(brand_name)
        logger.info(f"Normalized profile name: {profile_name}")
        
        # 1. Crea entry Supabase
        client_id = await self._create_supabase_client(
            profile_name, snapshot
        )
        logger.info(f"Created Supabase client: {client_id}")
        
        # 2. Crea directory profilo
        profile_dir = self.profiles_dir / profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        (profile_dir / "agents").mkdir(exist_ok=True)
        logger.info(f"Created profile directory: {profile_dir}")
        
        # 3. Copia e personalizza agent
        agents_created = await self._create_agents(
            profile_name, snapshot
        )
        logger.info(f"Created {len(agents_created)} agents")
        
        # 4. Crea profile metadata
        await self._create_profile_metadata(
            profile_dir, snapshot
        )
        logger.info("Created profile metadata")
        
        return {
            "profile_name": profile_name,
            "client_id": str(client_id),
            "agents_created": agents_created,
            "profile_path": str(profile_dir),
        }
    
    def _normalize_profile_name(self, brand_name: str) -> str:
        """
        Normalizza nome brand per filesystem.
        
        Examples:
            "Fylle" -> "fylle"
            "Test Brand" -> "test_brand"
            "My-Company" -> "my_company"
        """
        return brand_name.lower().replace(" ", "_").replace("-", "_")
    
    async def _create_supabase_client(
        self,
        profile_name: str,
        snapshot: CompanySnapshot,
    ) -> UUID:
        """Crea entry nella tabella clients."""
        
        # Estrai info da snapshot
        company = snapshot.company
        audience = snapshot.audience
        voice = snapshot.voice
        insights = snapshot.insights
        
        client_data = {
            "name": profile_name,
            "display_name": company.name,
            "description": company.description,
            "brand_voice": voice.tone,
            "style_guidelines": " | ".join(voice.style_guidelines),
            "target_audience": audience.primary,
            "industry": company.industry or "Technology",
            "company_background": insights.positioning,
            "key_messages": insights.key_messages,
            "terminology": {},  # Può essere popolato in futuro
            "content_preferences": {
                "tone": voice.tone,
                "cta_preferences": voice.cta_preferences,
            },
            "rag_enabled": True,
            "knowledge_base_path": f"data/knowledge_base/{profile_name}",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.supabase_url}/rest/v1/clients",
                json=client_data,
                headers={
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
            )
            response.raise_for_status()
            result = response.json()
            return UUID(result[0]["id"])
    
    async def _create_agents(
        self,
        profile_name: str,
        snapshot: CompanySnapshot,
    ) -> list[str]:
        """Copia agent da default e personalizza."""
        
        default_agents_dir = self.profiles_dir / "default" / "agents"
        profile_agents_dir = self.profiles_dir / profile_name / "agents"
        
        agents_created = []
        
        # Agent essenziali da copiare
        essential_agents = [
            "rag_specialist.yaml",
            "copywriter.yaml",
            "enhanced_article_writer.yaml",
            "perplexity_researcher.yaml",
            "enhanced_article_compliance_specialist.yaml",
        ]
        
        for agent_file in essential_agents:
            source = default_agents_dir / agent_file
            dest = profile_agents_dir / agent_file
            
            if source.exists():
                # Carica agent template
                with open(source, "r") as f:
                    agent_config = yaml.safe_load(f)
                
                # Personalizza con snapshot info
                agent_config = self._personalize_agent(
                    agent_config, snapshot
                )
                
                # Attiva agent
                agent_config["is_active"] = True
                
                # Salva agent personalizzato
                with open(dest, "w") as f:
                    yaml.dump(agent_config, f, default_flow_style=False)
                
                agents_created.append(agent_file)
                logger.debug(f"Created agent: {agent_file}")
        
        return agents_created
    
    def _personalize_agent(
        self,
        agent_config: Dict[str, Any],
        snapshot: CompanySnapshot,
    ) -> Dict[str, Any]:
        """Personalizza agent con info snapshot."""
        
        # Aggiungi context brand al system_message
        brand_context = f"""

BRAND CONTEXT (from onboarding):
- Company: {snapshot.company.name}
- Industry: {snapshot.company.industry}
- Voice: {snapshot.voice.tone}
- Target Audience: {snapshot.audience.primary}
- Key Messages: {', '.join(snapshot.insights.key_messages[:3])}
- Style Guidelines: {', '.join(snapshot.voice.style_guidelines[:3])}
- Differentiators: {', '.join(snapshot.company.differentiators[:3])}
"""
        
        if "system_message" in agent_config:
            agent_config["system_message"] += brand_context
        
        # Aggiungi metadata
        agent_config["metadata"] = agent_config.get("metadata", {})
        agent_config["metadata"]["brand_name"] = snapshot.company.name
        agent_config["metadata"]["created_from_onboarding"] = True
        agent_config["metadata"]["onboarding_timestamp"] = snapshot.created_at.isoformat()
        
        return agent_config
    
    async def _create_profile_metadata(
        self,
        profile_dir: Path,
        snapshot: CompanySnapshot,
    ) -> None:
        """Crea file metadata profilo."""
        
        metadata = {
            "profile_name": snapshot.company.name,
            "created_from": "onboarding",
            "created_at": snapshot.created_at.isoformat(),
            "company_info": {
                "name": snapshot.company.name,
                "industry": snapshot.company.industry,
                "description": snapshot.company.description,
                "website": snapshot.company.website,
            },
            "voice": {
                "tone": snapshot.voice.tone,
                "style_guidelines": snapshot.voice.style_guidelines,
                "cta_preferences": snapshot.voice.cta_preferences,
            },
            "audience": {
                "primary": snapshot.audience.primary,
                "secondary": snapshot.audience.secondary,
                "pain_points": snapshot.audience.pain_points,
            },
            "insights": {
                "positioning": snapshot.insights.positioning,
                "key_messages": snapshot.insights.key_messages,
            },
        }
        
        metadata_file = profile_dir / "profile.yaml"
        with open(metadata_file, "w") as f:
            yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)
```

---

## 📚 Task 2.2: Populate Knowledge Base

### File: `onboarding/application/use_cases/populate_knowledge_base.py`

```python
"""Popola knowledge base CGS con info snapshot onboarding."""

from pathlib import Path
from typing import Dict, Any
import httpx
import logging

from onboarding.domain.models import CompanySnapshot
from onboarding.config.settings import OnboardingSettings

logger = logging.getLogger(__name__)


class PopulateKnowledgeBaseUseCase:
    """Popola knowledge base con documenti da snapshot."""
    
    def __init__(self, settings: OnboardingSettings):
        self.settings = settings
        self.kb_dir = Path("data/knowledge_base")
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_anon_key
    
    async def execute(
        self,
        profile_name: str,
        snapshot: CompanySnapshot,
    ) -> Dict[str, Any]:
        """
        Crea documenti knowledge base da snapshot.
        
        Documenti creati:
        1. company_overview.md - Info azienda
        2. brand_voice.md - Tone e style guidelines
        3. target_audience.md - Audience info
        4. key_messages.md - Messaggi chiave
        5. offerings.md - Prodotti/servizi (se presenti)
        
        Args:
            profile_name: Nome profilo normalizzato
            snapshot: Snapshot onboarding
        
        Returns:
            Dict con:
            - profile_name: Nome profilo
            - documents_created: Numero documenti creati
            - document_ids: Lista ID documenti
        """
        logger.info(f"Populating knowledge base for profile: {profile_name}")
        
        # Crea directory KB
        kb_profile_dir = self.kb_dir / profile_name
        kb_profile_dir.mkdir(parents=True, exist_ok=True)
        
        documents_created = []
        
        # 1. Company Overview
        doc_id = await self._create_document(
            profile_name,
            "company_overview.md",
            self._generate_company_overview(snapshot),
            tags=["company", "overview"],
        )
        documents_created.append(doc_id)
        
        # 2. Brand Voice
        doc_id = await self._create_document(
            profile_name,
            "brand_voice.md",
            self._generate_brand_voice(snapshot),
            tags=["brand", "voice", "tone"],
        )
        documents_created.append(doc_id)
        
        # 3. Target Audience
        doc_id = await self._create_document(
            profile_name,
            "target_audience.md",
            self._generate_target_audience(snapshot),
            tags=["audience", "targeting"],
        )
        documents_created.append(doc_id)
        
        # 4. Key Messages
        doc_id = await self._create_document(
            profile_name,
            "key_messages.md",
            self._generate_key_messages(snapshot),
            tags=["messaging", "positioning"],
        )
        documents_created.append(doc_id)
        
        # 5. Offerings (se presenti)
        if snapshot.company.key_offerings:
            doc_id = await self._create_document(
                profile_name,
                "offerings.md",
                self._generate_offerings(snapshot),
                tags=["products", "services"],
            )
            documents_created.append(doc_id)
        
        logger.info(f"Created {len(documents_created)} knowledge base documents")
        
        return {
            "profile_name": profile_name,
            "documents_created": len(documents_created),
            "document_ids": documents_created,
        }
    
    def _generate_company_overview(self, snapshot: CompanySnapshot) -> str:
        """Genera documento company overview."""
        company = snapshot.company
        
        content = f"""# {company.name} - Company Overview

## Description
{company.description}

## Industry
{company.industry or 'Not specified'}

## Website
{company.website}

## Differentiators
{chr(10).join(f'- {d}' for d in company.differentiators)}

## Positioning
{snapshot.insights.positioning}

## Recent News & Developments
{chr(10).join(f'- {n}' for n in snapshot.insights.recent_news)}

---
*Generated from onboarding snapshot on {snapshot.created_at.strftime('%Y-%m-%d')}*
"""
        return content
    
    def _generate_brand_voice(self, snapshot: CompanySnapshot) -> str:
        """Genera documento brand voice."""
        voice = snapshot.voice
        
        forbidden_section = ""
        if voice.forbidden_phrases:
            forbidden_section = f"""
## Forbidden Phrases
{chr(10).join(f'- {p}' for p in voice.forbidden_phrases)}
"""
        
        content = f"""# {snapshot.company.name} - Brand Voice Guidelines

## Tone
{voice.tone}

## Style Guidelines
{chr(10).join(f'- {g}' for g in voice.style_guidelines)}

## CTA Preferences
{chr(10).join(f'- {c}' for c in voice.cta_preferences)}
{forbidden_section}
---
*Generated from onboarding snapshot on {snapshot.created_at.strftime('%Y-%m-%d')}*
"""
        return content
    
    def _generate_target_audience(self, snapshot: CompanySnapshot) -> str:
        """Genera documento target audience."""
        audience = snapshot.audience
        
        content = f"""# {snapshot.company.name} - Target Audience

## Primary Audience
{audience.primary}

## Secondary Audiences
{chr(10).join(f'- {s}' for s in audience.secondary)}

## Pain Points
{chr(10).join(f'- {p}' for p in audience.pain_points)}

## Desired Outcomes
{chr(10).join(f'- {o}' for o in audience.desired_outcomes)}

---
*Generated from onboarding snapshot on {snapshot.created_at.strftime('%Y-%m-%d')}*
"""
        return content
    
    def _generate_key_messages(self, snapshot: CompanySnapshot) -> str:
        """Genera documento key messages."""
        insights = snapshot.insights
        
        content = f"""# {snapshot.company.name} - Key Messages

## Core Messages
{chr(10).join(f'{i+1}. {m}' for i, m in enumerate(insights.key_messages))}

## Positioning Statement
{insights.positioning}

---
*Generated from onboarding snapshot on {snapshot.created_at.strftime('%Y-%m-%d')}*
"""
        return content
    
    def _generate_offerings(self, snapshot: CompanySnapshot) -> str:
        """Genera documento offerings."""
        company = snapshot.company
        
        content = f"""# {snapshot.company.name} - Products & Services

## Key Offerings
{chr(10).join(f'- {o}' for o in company.key_offerings)}

---
*Generated from onboarding snapshot on {snapshot.created_at.strftime('%Y-%m-%d')}*
"""
        return content
    
    async def _create_document(
        self,
        profile_name: str,
        filename: str,
        content: str,
        tags: list[str],
    ) -> str:
        """Crea documento in filesystem e Supabase."""
        
        # Salva file
        file_path = self.kb_dir / profile_name / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.debug(f"Created KB document: {file_path}")
        
        # Registra in Supabase (se tabella documents esiste)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.supabase_url}/rest/v1/documents",
                    json={
                        "client_name": profile_name,
                        "title": filename.replace(".md", "").replace("_", " ").title(),
                        "content": content,
                        "file_path": str(file_path),
                        "tags": tags,
                        "document_type": "knowledge_base",
                    },
                    headers={
                        "apikey": self.supabase_key,
                        "Authorization": f"Bearer {self.supabase_key}",
                        "Content-Type": "application/json",
                        "Prefer": "return=representation",
                    },
                )
                if response.status_code == 201:
                    result = response.json()
                    logger.debug(f"Registered document in Supabase: {result[0]['id']}")
                    return result[0]["id"]
        except Exception as e:
            logger.warning(f"Could not register document in Supabase: {e}")
            pass  # Tabella documents potrebbe non esistere
        
        return filename
```

---

## 🔄 Task 3.1: Context Injection

### Modifiche a: `core/infrastructure/factories/agent_factory.py`

```python
# Aggiungere questo metodo alla classe AgentFactory

from onboarding.domain.models import CompanySnapshot  # Import necessario

def inject_snapshot_context(
    self,
    agent: Agent,
    snapshot: CompanySnapshot,
) -> Agent:
    """
    Inietta context snapshot nell'agent runtime.
    
    Questo metodo permette di personalizzare agent dinamicamente
    senza modificare file YAML, iniettando brand context direttamente
    nel system_message a runtime.
    
    Args:
        agent: Agent da personalizzare
        snapshot: Snapshot onboarding con brand info
    
    Returns:
        Agent con context iniettato
    """
    
    # Costruisci context string
    context = f"""

BRAND CONTEXT (from onboarding):
Company: {snapshot.company.name}
Industry: {snapshot.company.industry}
Voice Tone: {snapshot.voice.tone}
Target Audience: {snapshot.audience.primary}

Key Messages:
{chr(10).join(f'- {m}' for m in snapshot.insights.key_messages[:3])}

Style Guidelines:
{chr(10).join(f'- {g}' for g in snapshot.voice.style_guidelines[:3])}

Differentiators:
{chr(10).join(f'- {d}' for d in snapshot.company.differentiators[:3])}

IMPORTANT: Use this brand context to inform all your outputs.
Ensure content aligns with the brand voice, messaging, and guidelines above.
"""
    
    # Inietta nel system_message
    enhanced_system_message = f"{agent.system_message}{context}"
    
    # Crea nuovo agent con context
    return Agent(
        name=agent.name,
        role=agent.role,
        goal=agent.goal,
        backstory=agent.backstory,
        system_message=enhanced_system_message,
        tools=agent.tools,
        examples=agent.examples,
        metadata={
            **agent.metadata,
            "snapshot_context_injected": True,
            "brand_name": snapshot.company.name,
        },
        is_active=agent.is_active,
    )
```

### Integrazione in Workflow Handler

```python
# In workflow handler (es. enhanced_article_workflow.py)
# Prima di eseguire agent:

def execute_task(self, task, context):
    """Esegue task con agent personalizzato."""
    
    # Recupera agent
    agent = self.agent_factory.get_agent(
        agent_name=task.agent_name,
        client_profile=context.get("client_profile", "default"),
    )
    
    # Se snapshot disponibile, inietta context
    if "company_snapshot" in context:
        snapshot = context["company_snapshot"]
        agent = self.agent_factory.inject_snapshot_context(agent, snapshot)
        logger.info(f"Injected snapshot context into agent: {agent.name}")
    
    # Esegui task con agent personalizzato
    result = agent.execute(task)
    
    return result
```

---

## 💾 Task 3.2: Profile Cache

### File: `onboarding/infrastructure/cache/profile_cache.py`

```python
"""Cache profili CGS per performance."""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
import logging

from onboarding.config.settings import OnboardingSettings

logger = logging.getLogger(__name__)


class ProfileCache:
    """
    Cache profili CGS con TTL.
    
    Strategia:
    1. In-memory cache con TTL (default 24h)
    2. Fallback a Supabase se cache miss
    3. Invalidazione automatica su TTL expiry
    """
    
    def __init__(self, settings: OnboardingSettings, ttl_hours: int = 24):
        self.settings = settings
        self.ttl = timedelta(hours=ttl_hours)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_anon_key
        
        logger.info(f"ProfileCache initialized with TTL: {ttl_hours}h")
    
    async def get_profile(self, brand_name: str) -> Optional[Dict[str, Any]]:
        """
        Recupera profilo da cache o Supabase.
        
        Args:
            brand_name: Nome brand (es. "Fylle", "TestBrand")
        
        Returns:
            Profile dict se esiste, None altrimenti
        """
        profile_name = self._normalize_name(brand_name)
        
        # 1. Check in-memory cache
        if profile_name in self._cache:
            cached = self._cache[profile_name]
            age = datetime.now() - cached["cached_at"]
            
            if age < self.ttl:
                logger.info(f"Cache HIT for profile: {profile_name} (age: {age})")
                return cached["profile"]
            else:
                # Cache expired
                logger.info(f"Cache EXPIRED for profile: {profile_name} (age: {age})")
                del self._cache[profile_name]
        
        # 2. Check Supabase
        logger.info(f"Cache MISS for profile: {profile_name}, fetching from Supabase")
        profile = await self._fetch_from_supabase(profile_name)
        
        if profile:
            # Cache it
            self._cache[profile_name] = {
                "profile": profile,
                "cached_at": datetime.now(),
            }
            logger.info(f"Cached profile from Supabase: {profile_name}")
            return profile
        
        logger.info(f"Profile not found: {profile_name}")
        return None
    
    async def set_profile(
        self,
        brand_name: str,
        profile_data: Dict[str, Any],
    ) -> None:
        """
        Salva profilo in cache.
        
        Args:
            brand_name: Nome brand
            profile_data: Dati profilo da cachare
        """
        profile_name = self._normalize_name(brand_name)
        
        self._cache[profile_name] = {
            "profile": profile_data,
            "cached_at": datetime.now(),
        }
        
        logger.info(f"Profile cached: {profile_name}")
    
    async def invalidate(self, brand_name: str) -> None:
        """
        Invalida cache per un profilo specifico.
        
        Args:
            brand_name: Nome brand da invalidare
        """
        profile_name = self._normalize_name(brand_name)
        
        if profile_name in self._cache:
            del self._cache[profile_name]
            logger.info(f"Cache invalidated for profile: {profile_name}")
    
    async def _fetch_from_supabase(
        self,
        profile_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Recupera profilo da Supabase."""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/clients",
                    params={"name": f"eq.{profile_name}"},
                    headers={
                        "apikey": self.supabase_key,
                        "Authorization": f"Bearer {self.supabase_key}",
                    },
                )
                
                if response.status_code == 200:
                    results = response.json()
                    if results:
                        logger.debug(f"Fetched profile from Supabase: {profile_name}")
                        return results[0]
        except Exception as e:
            logger.error(f"Error fetching profile from Supabase: {e}")
        
        return None
    
    def _normalize_name(self, brand_name: str) -> str:
        """Normalizza nome brand."""
        return brand_name.lower().replace(" ", "_").replace("-", "_")
    
    def clear_cache(self) -> None:
        """Svuota cache completamente."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache cleared: {count} profiles removed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Ritorna statistiche cache."""
        return {
            "cached_profiles": len(self._cache),
            "profiles": list(self._cache.keys()),
            "ttl_hours": self.ttl.total_seconds() / 3600,
        }
```

---

## 🔗 INTEGRAZIONI

### Integrazione in `execute_onboarding.py`

```python
# File: onboarding/application/use_cases/execute_onboarding.py

# Import necessari
from onboarding.application.use_cases.create_client_profile import CreateClientProfileUseCase
from onboarding.application.use_cases.populate_knowledge_base import PopulateKnowledgeBaseUseCase
from onboarding.infrastructure.cache.profile_cache import ProfileCache

class ExecuteOnboardingUseCase:
    
    def __init__(self, settings: OnboardingSettings, ...):
        # ... existing code ...
        self.profile_cache = ProfileCache(settings)
    
    async def execute(self, session_id: UUID) -> ResultEnvelope:
        """Esegue workflow CGS con profilo dinamico."""
        
        # ... existing code fino a snapshot synthesis ...
        
        # ========================================
        # NUOVO: Gestione Profilo Dinamico
        # ========================================
        
        # 1. Check se profilo esiste già (cache + Supabase)
        existing_profile = await self.profile_cache.get_profile(session.brand_name)
        
        if existing_profile:
            # Riusa profilo esistente
            profile_name = existing_profile["name"]
            logger.info(f"Reusing existing profile: {profile_name}")
        else:
            # Crea nuovo profilo
            logger.info(f"Creating new profile for: {session.brand_name}")
            
            create_profile_uc = CreateClientProfileUseCase(self.settings)
            profile_result = await create_profile_uc.execute(
                snapshot=snapshot,
                brand_name=session.brand_name,
            )
            
            # Popola knowledge base
            populate_kb_uc = PopulateKnowledgeBaseUseCase(self.settings)
            kb_result = await populate_kb_uc.execute(
                profile_name=profile_result["profile_name"],
                snapshot=snapshot,
            )
            
            # Cache profilo
            await self.profile_cache.set_profile(
                session.brand_name,
                profile_result,
            )
            
            profile_name = profile_result["profile_name"]
            logger.info(f"Created and cached new profile: {profile_name}")
        
        # 2. Build payload con profilo dinamico
        payload = self.payload_builder.build_payload(
            session_id=session_id,
            trace_id=session.trace_id,
            snapshot=snapshot,
            goal=session.goal,
            client_profile=profile_name,  # ← Usa profilo dinamico
        )
        
        # ... resto del codice esistente ...
```

---

**Fine Implementazione Codice**

Per riferimenti completi, vedi [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)

