"""
Brief Generator Service for Fylle Onboarding v3
Generates editorial briefs from user context and pack templates.
"""

import time
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.core.llm import LLMRouter, LLMMessage, LLMConfig
from app.core.prompts import PromptEngine
from app.core.context import ContextManager
from app.domain.entities import Brief, BriefDocument, BriefQuestion


class BriefGeneratorService:
    """
    Service for generating editorial briefs.
    
    Flow:
    1. User selects a pack (Newsletter, Blog Post)
    2. Generate questions based on pack and user context
    3. User answers questions
    4. Generate complete brief document
    """
    
    def __init__(
        self,
        llm_router: LLMRouter,
        prompt_engine: PromptEngine,
        context_manager: ContextManager,
        briefs_repository: Any,
        packs_repository: Any,
    ):
        self.llm = llm_router
        self.prompts = prompt_engine
        self.context = context_manager
        self.briefs_repo = briefs_repository
        self.packs_repo = packs_repository
        
        # In-memory store for brief sessions (questions + context)
        self._brief_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def start_brief(
        self,
        user_id: str,
        pack_id: str,
    ) -> Dict[str, Any]:
        """
        Start brief generation process.
        
        1. Get pack details
        2. Build user context from cards
        3. Generate brief-specific questions
        
        Returns questions for the user to answer.
        """
        # Get pack
        pack = await self.packs_repo.get(pack_id)
        if not pack:
            raise ValueError(f"Pack not found: {pack_id}")
        
        # Build context from user's cards
        context = await self.context.build_context(user_id)
        
        # Generate questions based on pack type
        questions = await self._generate_brief_questions(
            pack_name=pack.name,
            context=context,
        )
        
        # Create brief session
        brief_session_id = str(uuid4())
        self._brief_sessions[brief_session_id] = {
            "user_id": user_id,
            "pack_id": pack_id,
            "pack_name": pack.name,
            "context": context,
            "questions": questions,
            "created_at": time.time(),
        }
        
        return {
            "brief_session_id": brief_session_id,
            "questions": questions,
            "message": f"Rispondi a {len(questions)} domande per generare il brief",
        }
    
    async def _generate_brief_questions(
        self,
        pack_name: str,
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate brief-specific questions."""
        
        # Get prompt based on pack type
        prompt_key = f"briefs.{pack_name}.generate_questions"
        
        system_prompt = await self.prompts.get_prompt(
            f"briefs.{pack_name}.system",
        )
        
        questions_prompt = await self.prompts.get_prompt(
            prompt_key,
            {"context": context},
        )
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=questions_prompt),
        ]
        
        result = await self.llm.generate_json(messages)
        return result.get("questions", [])
    
    async def submit_answers(
        self,
        brief_session_id: str,
        answers: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Process answers and generate brief.
        
        Returns the generated brief document.
        """
        # Get brief session
        session = self._brief_sessions.get(brief_session_id)
        if not session:
            raise ValueError(f"Brief session not found: {brief_session_id}")
        
        start_time = time.time()
        
        # Generate brief
        brief_content = await self._generate_brief(
            pack_name=session["pack_name"],
            context=session["context"],
            answers=answers,
        )
        
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        # Save brief to database
        brief = await self.briefs_repo.create(
            user_id=session["user_id"],
            pack_id=session["pack_id"],
            title=brief_content.get("purpose", "")[:100],
            content=brief_content,
            answers=answers,
            context_snapshot=session["context"],
            llm_provider=self.llm.default_provider.value,
            llm_model=self.llm.get_provider()._get_default_model(),
            generation_time_ms=generation_time_ms,
        )
        
        # Clean up session
        del self._brief_sessions[brief_session_id]
        
        return {
            "brief_id": str(brief.id),
            "brief": brief_content,
            "message": "Brief generato con successo",
        }
    
    async def _generate_brief(
        self,
        pack_name: str,
        context: Dict[str, Any],
        answers: Dict[str, str],
    ) -> Dict[str, Any]:
        """Generate complete brief document."""
        
        system_prompt = await self.prompts.get_prompt(
            f"briefs.{pack_name}.system",
        )
        
        brief_prompt = await self.prompts.get_prompt(
            f"briefs.{pack_name}.generate_brief",
            {
                "context": context,
                "answers": answers,
            },
        )
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=brief_prompt),
        ]
        
        return await self.llm.generate_json(messages)
    
    async def get_user_briefs(
        self,
        user_id: str,
        pack_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get all briefs for a user, optionally filtered by pack."""
        briefs = await self.briefs_repo.get_by_user(user_id, pack_id)
        return [
            {
                "id": str(b.id),
                "pack_id": str(b.pack_id),
                "title": b.title,
                "created_at": b.created_at.isoformat(),
            }
            for b in briefs
        ]
    
    async def get_brief(self, brief_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific brief by ID."""
        brief = await self.briefs_repo.get(brief_id)
        if not brief:
            return None
        
        return {
            "id": str(brief.id),
            "user_id": str(brief.user_id),
            "pack_id": str(brief.pack_id),
            "title": brief.title,
            "content": brief.content,
            "created_at": brief.created_at.isoformat(),
        }
