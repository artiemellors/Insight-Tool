"""FastAPI routes for the Insight Tool API."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app import db
from app.agents.orchestrator import Orchestrator
from app.export import export_session, export_study
from app.models.core import Session, SessionExport, StudyExport, StudyState

router = APIRouter(prefix="/api")

_orchestrator = Orchestrator()


# ---------------------------------------------------------------------------
# Study CRUD
# ---------------------------------------------------------------------------

@router.post("/studies", response_model=StudyState)
async def create_study(
    name: str,
    product_area: str = "",
    objectives: list[str] | None = None,
) -> StudyState:
    """Create a new study."""
    state = _orchestrator.create_study(
        study_name=name,
        product_area=product_area,
        research_objectives=objectives or [],
    )
    db.save_study(state)
    return state


@router.get("/studies/{study_id}", response_model=StudyState)
async def get_study(study_id: str) -> StudyState:
    """Get a study by ID."""
    state = db.get_study(study_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Study not found")
    return state


@router.get("/studies", response_model=list[StudyState])
async def list_studies() -> list[StudyState]:
    """List all studies."""
    return db.list_studies()


# ---------------------------------------------------------------------------
# Guide & Codebook upload
# ---------------------------------------------------------------------------

@router.post("/studies/{study_id}/guide", response_model=StudyState)
async def upload_guide(study_id: str, file: UploadFile) -> StudyState:
    """Upload an interview guide (YAML or JSON)."""
    state = db.get_study(study_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Study not found")

    tmp_path = await _save_upload(file)
    try:
        state = _orchestrator.load_guide(state, tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    db.save_study(state)
    return state


@router.post("/studies/{study_id}/codebook", response_model=StudyState)
async def upload_codebook(study_id: str, file: UploadFile) -> StudyState:
    """Upload a codebook (YAML or JSON)."""
    state = db.get_study(study_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Study not found")

    tmp_path = await _save_upload(file)
    try:
        state = _orchestrator.load_codebook(state, tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    db.save_study(state)
    return state


# ---------------------------------------------------------------------------
# Transcript upload & analysis
# ---------------------------------------------------------------------------

@router.post("/studies/{study_id}/sessions", response_model=Session)
async def upload_and_analyse_transcript(
    study_id: str,
    file: UploadFile,
    participant_id: str,
    interviewer_name: str | None = None,
) -> Session:
    """Upload a transcript, parse it, and run analysis.

    This endpoint:
    1. Parses the transcript into Turn objects
    2. Creates a new Session
    3. Runs Guide Coverage + Deductive Coding in parallel
    4. Persists the analysed session to Supabase
    5. Returns the fully analysed Session
    """
    state = db.get_study(study_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Study not found")

    if state.interview_guide is None:
        raise HTTPException(status_code=400, detail="Upload an interview guide first")
    if state.codebook is None:
        raise HTTPException(status_code=400, detail="Upload a codebook first")

    # Save uploaded file to temp location with correct extension
    tmp_path = await _save_upload(file)
    try:
        state, session = _orchestrator.ingest_transcript(
            state, tmp_path, participant_id, interviewer_name
        )
    finally:
        tmp_path.unlink(missing_ok=True)

    # Run analysis
    session = await _orchestrator.analyse_session(state, session)

    # Persist the analysed session
    db.save_session(session, study_id)

    return session


@router.get(
    "/studies/{study_id}/sessions/{session_id}",
    response_model=Session,
)
async def get_session(study_id: str, session_id: str) -> Session:
    """Get a specific session by ID."""
    session = db.get_session(study_id, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# ---------------------------------------------------------------------------
# Structured JSON export — traceable, evidence-backed output
# ---------------------------------------------------------------------------

@router.get(
    "/studies/{study_id}/export",
    response_model=StudyExport,
)
async def export_study_json(study_id: str) -> StudyExport:
    """Export the full study as structured JSON with evidence traceability.

    Every coded turn and coverage result includes a direct reference back to
    the source transcript turn (speaker, quote, timestamp, session, participant)
    so that any finding can be verified against the original data.
    """
    state = db.get_study(study_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Study not found")
    return export_study(state)


@router.get(
    "/studies/{study_id}/sessions/{session_id}/export",
    response_model=SessionExport,
)
async def export_session_json(study_id: str, session_id: str) -> SessionExport:
    """Export a single session as structured JSON with evidence traceability.

    Each code application and coverage result links directly to the transcript
    turn that supports it, including exact quotes and timestamps.
    """
    state = db.get_study(study_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Study not found")

    session = db.get_session(study_id, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return export_session(session, state.interview_guide, state.codebook)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _save_upload(file: UploadFile) -> Path:
    """Save an uploaded file to a temporary location, preserving extension."""
    suffix = Path(file.filename or "upload").suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    content = await file.read()
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)
