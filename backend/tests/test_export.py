"""Tests for structured JSON export with evidence traceability."""

from app.export import export_session, export_study
from app.models.core import (
    Code,
    Codebook,
    CodedTurn,
    CodeType,
    GuideQuestion,
    GuideSection,
    InterviewGuide,
    QuestionCoverageResult,
    Session,
    SessionScorecard,
    StudyState,
    Theme,
    Turn,
)


def _make_transcript() -> list[Turn]:
    return [
        Turn(turn_index=0, speaker="Interviewer", text="Walk me through your first login.", start=5.0, end=12.0, is_interviewer=True),
        Turn(turn_index=1, speaker="P01", text="I saw the dashboard but couldn't find settings.", start=13.0, end=25.0),
        Turn(turn_index=2, speaker="Interviewer", text="What did you expect?", start=26.0, end=30.0, is_interviewer=True),
        Turn(turn_index=3, speaker="P01", text="I expected a setup wizard. Instead I just Googled it.", start=31.0, end=40.0),
    ]


def _make_guide() -> InterviewGuide:
    return InterviewGuide(sections=[
        GuideSection(name="Core Questions", questions=[
            GuideQuestion(id="OB1", text="Walk me through your first login experience", section="Core Questions", required=True, mapped_objective="Understand onboarding friction"),
            GuideQuestion(id="OB2", text="What did you expect to see?", section="Core Questions"),
        ]),
    ])


def _make_codebook() -> Codebook:
    return Codebook(themes=[
        Theme(name="Navigation Confusion", codes=[
            Code(id="CONFUSION_NAV", definition="Participant expresses difficulty finding features", indicators=["couldn't find"], code_type=CodeType.DEDUCTIVE),
        ]),
        Theme(name="Onboarding Gap", codes=[
            Code(id="ONBOARD_MISSING", definition="Participant expected guided onboarding but found none", indicators=["setup wizard", "onboarding"], code_type=CodeType.DEDUCTIVE),
        ]),
    ])


def _make_session() -> Session:
    return Session(
        session_id="abc12345",
        participant_id="P01",
        transcript=_make_transcript(),
        coverage_result=[
            QuestionCoverageResult(question_id="OB1", covered=True, depth_score=4, supporting_turn_indices=[1, 3], notes="Participant described full experience"),
            QuestionCoverageResult(question_id="OB2", covered=True, depth_score=3, supporting_turn_indices=[3]),
        ],
        coded_turns=[
            CodedTurn(turn_index=1, code_id="CONFUSION_NAV", confidence=0.85, evidence_quote="couldn't find settings", needs_review=False),
            CodedTurn(turn_index=3, code_id="ONBOARD_MISSING", confidence=0.55, evidence_quote="expected a setup wizard", needs_review=True),
        ],
        quality_scorecard=SessionScorecard(coverage_pct=100.0, avg_depth=3.5, coded_turn_count=2, emergent_theme_count=0),
    )


class TestSessionExport:
    def test_basic_structure(self):
        session = _make_session()
        result = export_session(session, _make_guide(), _make_codebook())
        assert result.session_id == "abc12345"
        assert result.participant_id == "P01"
        assert result.turn_count == 4

    def test_coded_evidence_traceability(self):
        session = _make_session()
        result = export_session(session, _make_guide(), _make_codebook())
        assert len(result.coded_evidence) == 2

        nav_code = result.coded_evidence[0]
        assert nav_code.code_id == "CONFUSION_NAV"
        assert nav_code.code_definition == "Participant expresses difficulty finding features"
        assert nav_code.theme == "Navigation Confusion"
        assert nav_code.confidence == 0.85
        assert nav_code.needs_review is False

        # Evidence traces back to exact turn
        assert nav_code.evidence.turn_index == 1
        assert nav_code.evidence.speaker == "P01"
        assert nav_code.evidence.quote == "couldn't find settings"
        assert nav_code.evidence.timestamp_start == 13.0
        assert nav_code.evidence.session_id == "abc12345"
        assert nav_code.evidence.participant_id == "P01"

    def test_low_confidence_flagged(self):
        session = _make_session()
        result = export_session(session, _make_guide(), _make_codebook())
        onboard_code = result.coded_evidence[1]
        assert onboard_code.needs_review is True
        assert onboard_code.confidence == 0.55

    def test_coverage_traceability(self):
        session = _make_session()
        result = export_session(session, _make_guide(), _make_codebook())
        assert len(result.coverage) == 2

        ob1 = result.coverage[0]
        assert ob1.question_id == "OB1"
        assert ob1.question_text == "Walk me through your first login experience"
        assert ob1.section == "Core Questions"
        assert ob1.covered is True
        assert ob1.depth_score == 4

        # Supporting evidence traces back to transcript turns
        assert len(ob1.supporting_evidence) == 2
        assert ob1.supporting_evidence[0].turn_index == 1
        assert ob1.supporting_evidence[0].speaker == "P01"
        assert ob1.supporting_evidence[1].turn_index == 3

    def test_scorecard_preserved(self):
        session = _make_session()
        result = export_session(session, _make_guide(), _make_codebook())
        assert result.scorecard is not None
        assert result.scorecard.coverage_pct == 100.0
        assert result.scorecard.avg_depth == 3.5

    def test_export_without_guide_or_codebook(self):
        """Export still works without guide/codebook — uses IDs as fallback."""
        session = _make_session()
        result = export_session(session, guide=None, codebook=None)
        assert len(result.coded_evidence) == 2
        assert result.coded_evidence[0].code_definition == "CONFUSION_NAV"
        assert result.coded_evidence[0].theme == "Unknown"

    def test_json_serializable(self):
        session = _make_session()
        result = export_session(session, _make_guide(), _make_codebook())
        # Pydantic model_dump_json must not raise
        json_str = result.model_dump_json(indent=2)
        assert '"CONFUSION_NAV"' in json_str
        assert '"evidence"' in json_str


class TestStudyExport:
    def test_full_study_export(self):
        state = StudyState(
            study_name="Onboarding Study",
            product_area="Dashboard",
            research_objectives=["Understand onboarding friction"],
            interview_guide=_make_guide(),
            codebook=_make_codebook(),
            sessions=[_make_session()],
        )
        result = export_study(state)
        assert result.study_name == "Onboarding Study"
        assert result.product_area == "Dashboard"
        assert len(result.research_objectives) == 1
        assert result.codebook_version == 1
        assert result.guide_version == 1
        assert len(result.sessions) == 1
        assert result.sessions[0].session_id == "abc12345"

    def test_evidence_chain_end_to_end(self):
        """Verify complete traceability: study → session → code → evidence → turn."""
        state = StudyState(
            study_name="Test",
            interview_guide=_make_guide(),
            codebook=_make_codebook(),
            sessions=[_make_session()],
        )
        result = export_study(state)
        code_app = result.sessions[0].coded_evidence[0]

        # Full chain: study_id → session_id → code_id → evidence (turn, speaker, quote, timestamp)
        assert result.study_id  # non-empty
        assert code_app.evidence.session_id == "abc12345"
        assert code_app.code_id == "CONFUSION_NAV"
        assert code_app.evidence.turn_index == 1
        assert code_app.evidence.speaker == "P01"
        assert code_app.evidence.quote == "couldn't find settings"
        assert code_app.evidence.timestamp_start == 13.0

    def test_json_serializable(self):
        state = StudyState(
            study_name="Test",
            interview_guide=_make_guide(),
            codebook=_make_codebook(),
            sessions=[_make_session()],
        )
        result = export_study(state)
        json_str = result.model_dump_json(indent=2)
        assert '"study_name"' in json_str
        assert '"evidence"' in json_str
        assert '"supporting_evidence"' in json_str
