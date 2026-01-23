"""
Onboarding Service for Fylle Onboarding v3
Orchestrates the onboarding flow: research -> questions -> cards
"""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.core.llm import LLMRouter, LLMMessage, LLMConfig, LLMProvider
from app.core.prompts import PromptEngine
from app.domain.entities import Card, CardType


class OnboardingService:
    """
    Service for managing the onboarding flow.
    
    Flow:
    1. User provides brand info
    2. Research company using Perplexity
    3. Synthesize snapshot
    4. Generate clarifying questions
    5. Process answers
    6. Generate cards
    """
    
    def __init__(
        self,
        llm_router: LLMRouter,
        prompt_engine: PromptEngine,
        user_repository: Any,
        session_repository: Any,
        cards_repository: Any,
    ):
        self.llm = llm_router
        self.prompts = prompt_engine
        self.users_repo = user_repository
        self.sessions_repo = session_repository
        self.cards_repo = cards_repository
    
    async def start_onboarding(
        self,
        email: str,
        brand_name: str,
        website: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Start the onboarding process.
        
        1. Create or get user
        2. Create session
        3. Research company
        4. Generate snapshot
        5. Generate questions
        
        Returns session with snapshot and questions.
        """
        # 1. Get or create user
        user = await self.users_repo.get_by_email(email)
        if not user:
            user = await self.users_repo.create(
                email=email,
                brand_name=brand_name,
                website=website,
            )
        
        # 2. Create session
        session_id = uuid4()
        session = await self.sessions_repo.create(
            id=session_id,
            user_id=user.id,
            state="researching",
        )
        
        try:
            # 3. Research company
            snapshot = await self._research_company(
                brand_name=brand_name,
                website=website,
                additional_context=additional_context,
            )
            
            await self.sessions_repo.update(
                session_id,
                state="synthesizing",
                snapshot=snapshot,
            )
            
            # 4. Generate questions
            questions = await self._generate_questions(snapshot)
            
            await self.sessions_repo.update(
                session_id,
                state="questions_ready",
                clarifying_questions=questions,
            )
            
            return {
                "session_id": str(session_id),
                "user_id": str(user.id),
                "state": "questions_ready",
                "snapshot_summary": {
                    "company_name": snapshot.get("company_name", brand_name),
                    "industry": snapshot.get("industry"),
                    "description": snapshot.get("description", ""),
                    "questions_count": len(questions),
                },
                "clarifying_questions": questions,
                "message": "Onboarding avviato con successo",
                "next_action": "submit_answers",
            }
            
        except Exception as e:
            await self.sessions_repo.update(
                session_id,
                state="error",
                error_message=str(e),
            )
            raise
    
    async def _research_company(
        self,
        brand_name: str,
        website: Optional[str],
        additional_context: Optional[str],
    ) -> Dict[str, Any]:
        """Research company using Perplexity or other research provider."""
        
        # Get research query prompt
        research_query = await self.prompts.get_prompt(
            "onboarding.research.research_query",
            {
                "brand_name": brand_name,
                "website": website,
                "additional_context": additional_context,
            },
        )
        
        # Use Perplexity for research
        research_response = await self.llm.research(research_query)
        
        # Synthesize into structured snapshot
        system_prompt = await self.prompts.get_prompt(
            "onboarding.research.system",
        )
        
        synthesis_prompt = await self.prompts.get_prompt(
            "onboarding.research.snapshot_synthesis",
            {"research_data": research_response.content},
        )
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=synthesis_prompt),
        ]
        
        snapshot = await self.llm.generate_json(messages)
        return snapshot
    
    async def _generate_questions(
        self,
        snapshot: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate clarifying questions based on snapshot."""
        
        system_prompt = await self.prompts.get_prompt(
            "onboarding.questions.system",
        )
        
        questions_prompt = await self.prompts.get_prompt(
            "onboarding.questions.generate_questions",
            {"snapshot": snapshot},
        )
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=questions_prompt),
        ]
        
        result = await self.llm.generate_json(messages)
        return result.get("questions", [])
    
    async def submit_answers(
        self,
        session_id: str,
        answers: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Process user answers and generate cards.
        
        Returns generated card IDs.
        """
        session = await self.sessions_repo.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Update session with answers
        await self.sessions_repo.update(
            session_id,
            state="generating_cards",
            answers=answers,
        )
        
        try:
            # Generate cards
            cards = await self._generate_cards(
                user_id=session.user_id,
                snapshot=session.snapshot,
                answers=answers,
            )
            
            # Save cards
            card_ids = []
            for card_data in cards:
                card = await self.cards_repo.create(
                    user_id=session.user_id,
                    **card_data,
                )
                card_ids.append(str(card.id))
            
            await self.sessions_repo.update(
                session_id,
                state="done",
            )
            
            return {
                "session_id": session_id,
                "user_id": str(session.user_id),
                "state": "done",
                "message": f"{len(cards)} cards generate con successo",
                "card_ids": card_ids,
                "cards_created": len(cards),
                "redirect_url": f"/cards?user_id={session.user_id}",
            }
            
        except Exception as e:
            await self.sessions_repo.update(
                session_id,
                state="error",
                error_message=str(e),
            )
            raise
    
    async def _generate_cards(
        self,
        user_id: UUID,
        snapshot: Dict[str, Any],
        answers: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate all 8 card types."""
        
        system_prompt = await self.prompts.get_prompt(
            "cards.generation.system",
        )
        
        generation_prompt = await self.prompts.get_prompt(
            "cards.generation.generate_all_cards",
            {
                "snapshot": snapshot,
                "answers": answers,
            },
        )
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=generation_prompt),
        ]
        
        result = await self.llm.generate_json(messages)
        return result.get("cards", [])
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session status."""
        session = await self.sessions_repo.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": str(session.id),
            "user_id": str(session.user_id),
            "state": session.state,
            "has_snapshot": bool(session.snapshot),
            "snapshot_complete": session.state in ["questions_ready", "generating_cards", "done"],
            "error_message": session.error_message,
        }
