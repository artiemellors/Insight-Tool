"""Orchestrator — manages StudyState and routes work to specialist agents.

The Orchestrator owns mutation of StudyState. Specialist agents read from
and write to StudyState only through the Orchestrator.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import anthropic

from app.agents.deductive_coder import DeductiveCoderAgent
from app.agents.guide_coverage import GuideCoverageAgent
from app.models.core import (
    Codebook,
    InterviewGuide,
    Session,
    SessionScorecard,
    StudyState,
    Turn,
)
from app.parsers.codebook import load_codebook
from app.parsers.guide import load_interview_guide
from app.parsers.transcript import parse_transcript


class Orchestrator:
    """Central coordinator for the Insight Tool analysis pipeline."""

    def __init__(self, client: anthropic.Anthropic | None = None):
        self.client = client or anthropic.Anthropic()
        self.guide_agent = GuideCoverageAgent(client=self.client)
        self.coder_agent = DeductiveCoderAgent(client=self.client)

    def create_study(
        self,
        study_name: str,
        product_area: str = "",
        research_objectives: list[str] | None = None,
    ) -> StudyState:
        """Create a new study with basic metadata."""
        return StudyState(
            study_name=study_name,
            product_area=product_area,
            research_objectives=research_objectives or [],
        )

    def load_guide(
        self,
        state: StudyState,
        guide_path: str | Path,
    ) -> StudyState:
        """Load an interview guide into the study."""
        guide = load_interview_guide(guide_path)
        state.interview_guide = guide
        return state

    def load_codebook(
        self,
        state: StudyState,
        codebook_path: str | Path,
    ) -> StudyState:
        """Load a codebook into the study."""
        codebook = load_codebook(codebook_path)
        state.codebook = codebook
        return state

    def ingest_transcript(
        self,
        state: StudyState,
        transcript_path: str | Path,
        participant_id: str,
        interviewer_name: str | None = None,
    ) -> tuple[StudyState, Session]:
        """Parse a transcript and add it as a new session.

        Does not run analysis — call analyse_session() after ingestion.
        """
        turns = parse_transcript(
            transcript_path,
            interviewer_name=interviewer_name,
        )

        session = Session(
            participant_id=participant_id,
            transcript=turns,
        )
        state.sessions.append(session)
        return state, session

    async def analyse_session(
        self,
        state: StudyState,
        session: Session,
    ) -> Session:
        """Run guide coverage and deductive coding in parallel on a session.

        This is the fan-out/fan-in pattern: both agents run concurrently
        on the same parsed transcript, then results are merged.
        """
        if state.interview_guide is None:
            raise ValueError("Interview guide must be loaded before analysis")
        if state.codebook is None:
            raise ValueError("Codebook must be loaded before analysis")

        # Fan-out: run both agents in parallel
        coverage_task = self.guide_agent.analyse(
            session.transcript,
            state.interview_guide,
        )
        coding_task = self.coder_agent.code_turns(
            session.transcript,
            state.codebook,
        )

        coverage_results, coded_turns = await asyncio.gather(
            coverage_task, coding_task
        )

        # Write results to session
        session.coverage_result = coverage_results
        session.coded_turns = coded_turns

        # Compute scorecard
        covered_count = sum(1 for r in coverage_results if r.covered)
        total_questions = len(coverage_results)
        depths = [r.depth_score for r in coverage_results if r.depth_score is not None]

        session.quality_scorecard = SessionScorecard(
            coverage_pct=round(covered_count / total_questions * 100, 1) if total_questions else 0,
            avg_depth=round(sum(depths) / len(depths), 1) if depths else 0,
            coded_turn_count=len(coded_turns),
            emergent_theme_count=len(session.emergent_themes),
        )

        return session
