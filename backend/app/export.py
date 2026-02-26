"""Build structured, traceable JSON exports from study/session data.

Every coded turn and coverage result is resolved to full evidence references
so downstream consumers can verify any claim against the source material.
"""

from __future__ import annotations

from app.models.core import (
    CodeApplication,
    Codebook,
    CoverageDetail,
    EvidenceRef,
    InterviewGuide,
    Session,
    SessionExport,
    StudyExport,
    StudyState,
    Turn,
)


def _build_turn_lookup(turns: list[Turn]) -> dict[int, Turn]:
    return {t.turn_index: t for t in turns}


def _evidence_from_turn(
    turn: Turn,
    session: Session,
    quote_override: str | None = None,
) -> EvidenceRef:
    """Create an EvidenceRef pointing back to a specific transcript turn."""
    return EvidenceRef(
        turn_index=turn.turn_index,
        speaker=turn.speaker,
        quote=quote_override or turn.text,
        timestamp_start=turn.start,
        session_id=session.session_id,
        participant_id=session.participant_id,
    )


def export_session(
    session: Session,
    guide: InterviewGuide | None = None,
    codebook: Codebook | None = None,
) -> SessionExport:
    """Export a single session with full evidence traceability."""
    turn_lookup = _build_turn_lookup(session.transcript)

    # --- Build code lookup for definitions and themes ---
    code_meta: dict[str, tuple[str, str]] = {}  # code_id -> (definition, theme)
    if codebook:
        for theme in codebook.themes:
            for code in theme.codes:
                code_meta[code.id] = (code.definition, theme.name)

    # --- Build question lookup ---
    question_meta: dict[str, tuple[str, str]] = {}  # question_id -> (text, section)
    if guide:
        for section in guide.sections:
            for q in section.questions:
                question_meta[q.id] = (q.text, section.name)

    # --- Coded evidence with full traceability ---
    coded_evidence: list[CodeApplication] = []
    for ct in session.coded_turns:
        turn = turn_lookup.get(ct.turn_index)
        if turn is None:
            continue
        defn, theme_name = code_meta.get(ct.code_id, (ct.code_id, "Unknown"))
        coded_evidence.append(CodeApplication(
            code_id=ct.code_id,
            code_definition=defn,
            theme=theme_name,
            confidence=ct.confidence,
            needs_review=ct.needs_review,
            evidence=_evidence_from_turn(turn, session, ct.evidence_quote),
        ))

    # --- Coverage with supporting evidence ---
    coverage: list[CoverageDetail] = []
    for cr in session.coverage_result:
        q_text, q_section = question_meta.get(cr.question_id, (cr.question_id, "Unknown"))
        supporting = []
        for ti in cr.supporting_turn_indices:
            turn = turn_lookup.get(ti)
            if turn:
                supporting.append(_evidence_from_turn(turn, session))
        coverage.append(CoverageDetail(
            question_id=cr.question_id,
            question_text=q_text,
            section=q_section,
            covered=cr.covered,
            depth_score=cr.depth_score,
            notes=cr.notes,
            supporting_evidence=supporting,
        ))

    return SessionExport(
        session_id=session.session_id,
        participant_id=session.participant_id,
        turn_count=len(session.transcript),
        coverage=coverage,
        coded_evidence=coded_evidence,
        emergent_themes=session.emergent_themes,
        scorecard=session.quality_scorecard,
    )


def export_study(state: StudyState) -> StudyExport:
    """Export an entire study with evidence chains for every finding."""
    sessions = [
        export_session(s, state.interview_guide, state.codebook)
        for s in state.sessions
    ]

    return StudyExport(
        study_id=state.study_id,
        study_name=state.study_name,
        product_area=state.product_area,
        research_objectives=state.research_objectives,
        codebook_version=state.codebook.version if state.codebook else None,
        guide_version=state.interview_guide.version if state.interview_guide else None,
        sessions=sessions,
    )
