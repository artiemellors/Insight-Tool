"""Tests for database serialization layer.

Tests the Pydantic ↔ DB row conversion logic without requiring a live
Supabase connection. The actual Supabase client is mocked.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.db import (
    _row_to_session,
    _row_to_study,
    _session_to_row,
    _study_to_row,
    delete_study,
    get_session,
    get_study,
    list_studies,
    save_session,
    save_study,
)
from app.models.core import (
    Code,
    Codebook,
    CodedTurn,
    CodeType,
    GuideQuestion,
    GuideSection,
    InterviewGuide,
    QuestionCoverageResult,
    ReviewStatus,
    Session,
    SessionScorecard,
    StudyState,
    Theme,
    Turn,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_guide() -> InterviewGuide:
    return InterviewGuide(sections=[
        GuideSection(name="Core", questions=[
            GuideQuestion(id="OB1", text="First login?", section="Core"),
        ]),
    ])


def _make_codebook() -> Codebook:
    return Codebook(themes=[
        Theme(name="Nav Confusion", codes=[
            Code(id="NAV1", definition="Can't find things", code_type=CodeType.DEDUCTIVE),
        ]),
    ])


def _make_study() -> StudyState:
    return StudyState(
        study_id="study_abc123",
        study_name="Onboarding Study",
        product_area="Dashboard",
        research_objectives=["Understand friction"],
        interview_guide=_make_guide(),
        codebook=_make_codebook(),
    )


def _make_session() -> Session:
    return Session(
        session_id="sess_001",
        participant_id="P01",
        transcript=[
            Turn(turn_index=0, speaker="Interviewer", text="Hello", start=0.0, end=3.0, is_interviewer=True),
            Turn(turn_index=1, speaker="P01", text="I couldn't find settings", start=4.0, end=10.0),
        ],
        coverage_result=[
            QuestionCoverageResult(question_id="OB1", covered=True, depth_score=4, supporting_turn_indices=[1]),
        ],
        coded_turns=[
            CodedTurn(turn_index=1, code_id="NAV1", confidence=0.85, evidence_quote="couldn't find settings"),
        ],
        quality_scorecard=SessionScorecard(coverage_pct=100.0, avg_depth=4.0, coded_turn_count=1, emergent_theme_count=0),
        review_status=ReviewStatus.PENDING,
    )


# ---------------------------------------------------------------------------
# Serialization round-trip tests
# ---------------------------------------------------------------------------

class TestStudySerialization:
    def test_study_to_row_basic_fields(self):
        study = _make_study()
        row = _study_to_row(study)
        assert row["study_id"] == "study_abc123"
        assert row["study_name"] == "Onboarding Study"
        assert row["product_area"] == "Dashboard"
        assert row["research_objectives"] == ["Understand friction"]

    def test_study_to_row_guide_serialized(self):
        study = _make_study()
        row = _study_to_row(study)
        assert row["interview_guide"] is not None
        assert row["interview_guide"]["sections"][0]["name"] == "Core"

    def test_study_to_row_codebook_serialized(self):
        study = _make_study()
        row = _study_to_row(study)
        assert row["codebook"] is not None
        assert row["codebook"]["themes"][0]["name"] == "Nav Confusion"

    def test_study_to_row_null_guide(self):
        study = StudyState(study_id="s1")
        row = _study_to_row(study)
        assert row["interview_guide"] is None
        assert row["codebook"] is None

    def test_round_trip(self):
        original = _make_study()
        row = _study_to_row(original)
        restored = _row_to_study(row)
        assert restored.study_id == original.study_id
        assert restored.study_name == original.study_name
        assert restored.product_area == original.product_area
        assert restored.research_objectives == original.research_objectives
        assert restored.interview_guide is not None
        assert restored.interview_guide.sections[0].name == "Core"
        assert restored.codebook is not None
        assert restored.codebook.themes[0].codes[0].id == "NAV1"


class TestSessionSerialization:
    def test_session_to_row_basic_fields(self):
        session = _make_session()
        row = _session_to_row(session, "study_abc123")
        assert row["session_id"] == "sess_001"
        assert row["study_id"] == "study_abc123"
        assert row["participant_id"] == "P01"
        assert row["review_status"] == "pending"

    def test_session_to_row_transcript_serialized(self):
        session = _make_session()
        row = _session_to_row(session, "s1")
        assert len(row["transcript"]) == 2
        assert row["transcript"][0]["speaker"] == "Interviewer"
        assert row["transcript"][1]["text"] == "I couldn't find settings"

    def test_session_to_row_analysis_results(self):
        session = _make_session()
        row = _session_to_row(session, "s1")
        assert len(row["coverage_result"]) == 1
        assert row["coverage_result"][0]["question_id"] == "OB1"
        assert len(row["coded_turns"]) == 1
        assert row["coded_turns"][0]["code_id"] == "NAV1"
        assert row["quality_scorecard"]["coverage_pct"] == 100.0

    def test_round_trip(self):
        original = _make_session()
        row = _session_to_row(original, "s1")
        restored = _row_to_session(row)
        assert restored.session_id == original.session_id
        assert restored.participant_id == original.participant_id
        assert len(restored.transcript) == 2
        assert restored.transcript[0].speaker == "Interviewer"
        assert restored.transcript[0].is_interviewer is True
        assert restored.transcript[1].start == 4.0
        assert len(restored.coverage_result) == 1
        assert restored.coverage_result[0].depth_score == 4
        assert len(restored.coded_turns) == 1
        assert restored.coded_turns[0].confidence == 0.85
        assert restored.quality_scorecard is not None
        assert restored.quality_scorecard.avg_depth == 4.0
        assert restored.review_status == ReviewStatus.PENDING

    def test_round_trip_empty_session(self):
        session = Session(session_id="empty", participant_id="P99")
        row = _session_to_row(session, "s1")
        restored = _row_to_session(row)
        assert restored.session_id == "empty"
        assert restored.transcript == []
        assert restored.coded_turns == []
        assert restored.quality_scorecard is None


# ---------------------------------------------------------------------------
# Database operations (mocked Supabase client)
# ---------------------------------------------------------------------------

def _mock_client():
    """Build a mock Supabase client with chainable table().select().eq()... pattern."""
    client = MagicMock()
    return client


class TestDatabaseOps:
    @patch("app.db.get_client")
    def test_save_study_calls_upsert(self, mock_get_client):
        client = _mock_client()
        mock_get_client.return_value = client

        study = _make_study()
        save_study(study)

        client.table.assert_called_with("studies")
        client.table("studies").upsert.assert_called_once()
        row = client.table("studies").upsert.call_args[0][0]
        assert row["study_id"] == "study_abc123"

    @patch("app.db.get_client")
    def test_get_study_returns_none_when_missing(self, mock_get_client):
        client = _mock_client()
        mock_get_client.return_value = client

        # Empty result
        client.table("studies").select("*").eq("study_id", "nope").execute.return_value = MagicMock(data=[])

        result = get_study("nope")
        assert result is None

    @patch("app.db.get_client")
    def test_save_session_calls_upsert(self, mock_get_client):
        client = _mock_client()
        mock_get_client.return_value = client

        session = _make_session()
        save_session(session, "study_abc123")

        client.table.assert_any_call("sessions")
        client.table("sessions").upsert.assert_called_once()
        row = client.table("sessions").upsert.call_args[0][0]
        assert row["session_id"] == "sess_001"
        assert row["study_id"] == "study_abc123"

    @patch("app.db.get_client")
    def test_list_studies_returns_list(self, mock_get_client):
        client = _mock_client()
        mock_get_client.return_value = client

        row = _study_to_row(_make_study())
        client.table("studies").select("*").order("created_at", desc=True).execute.return_value = MagicMock(data=[row])

        studies = list_studies()
        assert len(studies) == 1
        assert studies[0].study_id == "study_abc123"

    @patch("app.db.get_client")
    def test_delete_study(self, mock_get_client):
        client = _mock_client()
        mock_get_client.return_value = client

        row = _study_to_row(_make_study())
        client.table("studies").delete().eq("study_id", "study_abc123").execute.return_value = MagicMock(data=[row])

        result = delete_study("study_abc123")
        assert result is True
