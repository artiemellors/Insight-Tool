"""Supabase database service layer.

Translates between Pydantic models and Supabase rows.
Studies and sessions are stored as rows with JSONB columns for nested structures.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from app.models.core import (
    Codebook,
    InterviewGuide,
    Session,
    StudyState,
)

if TYPE_CHECKING:
    from supabase import Client

_client: Optional[Any] = None


def get_client() -> Client:
    """Return a cached Supabase client. Creates one on first call.

    The supabase SDK is imported lazily so that serialization helpers
    and tests can be used without a working supabase installation.
    """
    global _client
    if _client is None:
        from dotenv import load_dotenv
        from supabase import create_client

        load_dotenv()
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_KEY"]
        _client = create_client(url, key)
    return _client


# ---------------------------------------------------------------------------
# Serialization helpers — Pydantic ↔ DB rows
# ---------------------------------------------------------------------------

def _study_to_row(state: StudyState) -> dict:
    """Convert a StudyState to a database row."""
    return {
        "study_id": state.study_id,
        "study_name": state.study_name,
        "product_area": state.product_area,
        "research_objectives": state.research_objectives,
        "interview_guide": (
            state.interview_guide.model_dump(mode="json")
            if state.interview_guide else None
        ),
        "codebook": (
            state.codebook.model_dump(mode="json")
            if state.codebook else None
        ),
        "created_at": state.created_at.isoformat(),
    }


def _row_to_study(row: dict) -> StudyState:
    """Convert a database row back to a StudyState."""
    return StudyState(
        study_id=row["study_id"],
        study_name=row["study_name"],
        product_area=row["product_area"],
        research_objectives=row.get("research_objectives", []),
        interview_guide=(
            InterviewGuide.model_validate(row["interview_guide"])
            if row.get("interview_guide") else None
        ),
        codebook=(
            Codebook.model_validate(row["codebook"])
            if row.get("codebook") else None
        ),
        created_at=row["created_at"],
    )


def _session_to_row(session: Session, study_id: str) -> dict:
    """Convert a Session to a database row."""
    return {
        "session_id": session.session_id,
        "study_id": study_id,
        "participant_id": session.participant_id,
        "transcript": [t.model_dump(mode="json") for t in session.transcript],
        "coverage_result": [
            cr.model_dump(mode="json") for cr in session.coverage_result
        ],
        "coded_turns": [
            ct.model_dump(mode="json") for ct in session.coded_turns
        ],
        "emergent_themes": [
            et.model_dump(mode="json") for et in session.emergent_themes
        ],
        "quality_scorecard": (
            session.quality_scorecard.model_dump(mode="json")
            if session.quality_scorecard else None
        ),
        "review_status": session.review_status.value,
    }


def _row_to_session(row: dict) -> Session:
    """Convert a database row back to a Session."""
    return Session.model_validate({
        "session_id": row["session_id"],
        "participant_id": row["participant_id"],
        "transcript": row.get("transcript", []),
        "coverage_result": row.get("coverage_result", []),
        "coded_turns": row.get("coded_turns", []),
        "emergent_themes": row.get("emergent_themes", []),
        "quality_scorecard": row.get("quality_scorecard"),
        "review_status": row.get("review_status", "pending"),
    })


# ---------------------------------------------------------------------------
# Study CRUD
# ---------------------------------------------------------------------------

def save_study(state: StudyState) -> StudyState:
    """Upsert a study (insert or update)."""
    row = _study_to_row(state)
    get_client().table("studies").upsert(row).execute()
    return state


def get_study(study_id: str) -> Optional[StudyState]:
    """Fetch a study by ID, including its sessions."""
    result = (
        get_client()
        .table("studies")
        .select("*")
        .eq("study_id", study_id)
        .execute()
    )
    if not result.data:
        return None

    state = _row_to_study(result.data[0])

    # Fetch associated sessions
    sess_result = (
        get_client()
        .table("sessions")
        .select("*")
        .eq("study_id", study_id)
        .order("created_at")
        .execute()
    )
    state.sessions = [_row_to_session(r) for r in sess_result.data]
    return state


def list_studies() -> list[StudyState]:
    """Fetch all studies (without sessions for the list view)."""
    result = (
        get_client()
        .table("studies")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return [_row_to_study(r) for r in result.data]


def delete_study(study_id: str) -> bool:
    """Delete a study and cascade to its sessions."""
    result = (
        get_client()
        .table("studies")
        .delete()
        .eq("study_id", study_id)
        .execute()
    )
    return len(result.data) > 0


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------

def save_session(session: Session, study_id: str) -> Session:
    """Upsert a session."""
    row = _session_to_row(session, study_id)
    get_client().table("sessions").upsert(row).execute()
    return session


def get_session(study_id: str, session_id: str) -> Optional[Session]:
    """Fetch a single session."""
    result = (
        get_client()
        .table("sessions")
        .select("*")
        .eq("study_id", study_id)
        .eq("session_id", session_id)
        .execute()
    )
    if not result.data:
        return None
    return _row_to_session(result.data[0])


def list_sessions(study_id: str) -> list[Session]:
    """Fetch all sessions for a study."""
    result = (
        get_client()
        .table("sessions")
        .select("*")
        .eq("study_id", study_id)
        .order("created_at")
        .execute()
    )
    return [_row_to_session(r) for r in result.data]
