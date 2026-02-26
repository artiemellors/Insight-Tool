"""Tests for core Pydantic data models."""

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


class TestTurn:
    def test_basic_creation(self):
        turn = Turn(turn_index=0, speaker="P01", text="Hello")
        assert turn.turn_index == 0
        assert turn.speaker == "P01"
        assert turn.is_interviewer is False

    def test_optional_timestamps(self):
        turn = Turn(turn_index=0, speaker="P01", text="Hello")
        assert turn.start is None
        assert turn.end is None

    def test_with_timestamps(self):
        turn = Turn(turn_index=0, speaker="P01", text="Hello", start=5.0, end=12.0)
        assert turn.start == 5.0
        assert turn.end == 12.0


class TestInterviewGuide:
    def test_all_questions(self):
        guide = InterviewGuide(sections=[
            GuideSection(name="Core", questions=[
                GuideQuestion(id="Q1", text="Question 1", section="Core"),
                GuideQuestion(id="Q2", text="Question 2", section="Core"),
            ]),
            GuideSection(name="Follow-up", questions=[
                GuideQuestion(id="Q3", text="Question 3", section="Follow-up"),
            ]),
        ])
        assert len(guide.all_questions) == 3

    def test_default_version(self):
        guide = InterviewGuide(sections=[])
        assert guide.version == 1
        assert guide.locked is False


class TestCodebook:
    def test_all_codes(self):
        cb = Codebook(themes=[
            Theme(name="T1", codes=[
                Code(id="C1", definition="def1"),
                Code(id="C2", definition="def2"),
            ]),
            Theme(name="T2", codes=[
                Code(id="C3", definition="def3"),
            ]),
        ])
        assert len(cb.all_codes) == 3

    def test_code_type_default(self):
        code = Code(id="C1", definition="def")
        assert code.code_type == CodeType.DEDUCTIVE


class TestCodedTurn:
    def test_needs_review_flag(self):
        low = CodedTurn(
            turn_index=0, code_id="C1", confidence=0.4,
            evidence_quote="quote", needs_review=True,
        )
        assert low.needs_review is True

        high = CodedTurn(
            turn_index=0, code_id="C1", confidence=0.9,
            evidence_quote="quote", needs_review=False,
        )
        assert high.needs_review is False

    def test_confidence_bounds(self):
        import pytest
        with pytest.raises(Exception):
            CodedTurn(
                turn_index=0, code_id="C1", confidence=1.5,
                evidence_quote="quote",
            )


class TestSession:
    def test_default_status(self):
        session = Session(participant_id="P01")
        assert session.review_status == ReviewStatus.PENDING

    def test_auto_generated_id(self):
        s1 = Session(participant_id="P01")
        s2 = Session(participant_id="P02")
        assert s1.session_id != s2.session_id


class TestStudyState:
    def test_defaults(self):
        state = StudyState()
        assert state.study_name == ""
        assert state.sessions == []
        assert state.interview_guide is None
        assert state.codebook is None

    def test_auto_generated_id(self):
        s1 = StudyState()
        s2 = StudyState()
        assert s1.study_id != s2.study_id
