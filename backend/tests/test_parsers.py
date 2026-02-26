"""Tests for transcript, guide, and codebook parsers."""

from pathlib import Path

import pytest

from app.models.core import CodeType
from app.parsers.codebook import load_codebook
from app.parsers.guide import load_interview_guide
from app.parsers.transcript import (
    TranscriptFormat,
    detect_format,
    parse_transcript,
)

FIXTURES = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------

class TestDetectFormat:
    def test_vtt(self):
        assert detect_format("interview.vtt") == TranscriptFormat.VTT

    def test_srt(self):
        assert detect_format("interview.srt") == TranscriptFormat.SRT

    def test_txt(self):
        assert detect_format("interview.txt") == TranscriptFormat.TXT

    def test_json(self):
        assert detect_format("interview.json") == TranscriptFormat.JSON

    def test_unsupported_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            detect_format("interview.mp3")


# ---------------------------------------------------------------------------
# VTT parser
# ---------------------------------------------------------------------------

class TestVTTParser:
    def test_parses_turns(self):
        turns = parse_transcript(FIXTURES / "sample.vtt")
        assert len(turns) > 0

    def test_detects_speakers(self):
        turns = parse_transcript(FIXTURES / "sample.vtt")
        speakers = {t.speaker for t in turns}
        assert "Interviewer" in speakers
        assert "Participant" in speakers

    def test_merges_consecutive_turns(self):
        turns = parse_transcript(FIXTURES / "sample.vtt")
        # No two consecutive turns should have the same speaker
        for i in range(1, len(turns)):
            assert turns[i].speaker != turns[i - 1].speaker

    def test_has_timestamps(self):
        turns = parse_transcript(FIXTURES / "sample.vtt")
        for turn in turns:
            assert turn.start is not None
            assert turn.end is not None

    def test_interviewer_tagging(self):
        turns = parse_transcript(
            FIXTURES / "sample.vtt",
            interviewer_name="Interviewer",
        )
        interviewer_turns = [t for t in turns if t.is_interviewer]
        participant_turns = [t for t in turns if not t.is_interviewer]
        assert len(interviewer_turns) > 0
        assert len(participant_turns) > 0


# ---------------------------------------------------------------------------
# SRT parser
# ---------------------------------------------------------------------------

class TestSRTParser:
    def test_parses_turns(self):
        turns = parse_transcript(FIXTURES / "sample.srt")
        assert len(turns) > 0

    def test_detects_speakers(self):
        turns = parse_transcript(FIXTURES / "sample.srt")
        speakers = {t.speaker for t in turns}
        assert "Interviewer" in speakers
        assert "Participant" in speakers

    def test_has_timestamps(self):
        turns = parse_transcript(FIXTURES / "sample.srt")
        for turn in turns:
            assert turn.start is not None


# ---------------------------------------------------------------------------
# TXT parser
# ---------------------------------------------------------------------------

class TestTXTParser:
    def test_parses_turns(self):
        turns = parse_transcript(FIXTURES / "sample.txt")
        assert len(turns) > 0

    def test_detects_speakers(self):
        turns = parse_transcript(FIXTURES / "sample.txt")
        speakers = {t.speaker for t in turns}
        assert "Interviewer" in speakers
        assert "Participant" in speakers


# ---------------------------------------------------------------------------
# JSON parser
# ---------------------------------------------------------------------------

class TestJSONParser:
    def test_parses_turns(self):
        turns = parse_transcript(FIXTURES / "sample_transcript.json")
        assert len(turns) > 0

    def test_has_timestamps(self):
        turns = parse_transcript(FIXTURES / "sample_transcript.json")
        for turn in turns:
            assert turn.start is not None

    def test_detects_speakers(self):
        turns = parse_transcript(FIXTURES / "sample_transcript.json")
        speakers = {t.speaker for t in turns}
        assert "Interviewer" in speakers
        assert "Participant" in speakers


# ---------------------------------------------------------------------------
# Interview guide loader
# ---------------------------------------------------------------------------

class TestGuideLoader:
    def test_loads_sections(self):
        guide = load_interview_guide(FIXTURES / "sample_guide.yaml")
        assert len(guide.sections) == 2
        assert guide.sections[0].name == "Core Questions"
        assert guide.sections[1].name == "Feature Discovery"

    def test_loads_questions(self):
        guide = load_interview_guide(FIXTURES / "sample_guide.yaml")
        all_q = guide.all_questions
        assert len(all_q) == 4
        assert all_q[0].id == "OB1"
        assert all_q[0].required is True

    def test_loads_probes(self):
        guide = load_interview_guide(FIXTURES / "sample_guide.yaml")
        ob1 = guide.all_questions[0]
        assert len(ob1.probes) == 2
        assert "What did you expect to see?" in ob1.probes

    def test_mapped_objective(self):
        guide = load_interview_guide(FIXTURES / "sample_guide.yaml")
        ob1 = guide.all_questions[0]
        assert ob1.mapped_objective == "Understand onboarding friction"


# ---------------------------------------------------------------------------
# Codebook loader
# ---------------------------------------------------------------------------

class TestCodebookLoader:
    def test_loads_themes(self):
        cb = load_codebook(FIXTURES / "sample_codebook.yaml")
        assert len(cb.themes) == 2
        assert cb.themes[0].name == "Navigation Confusion"

    def test_loads_codes(self):
        cb = load_codebook(FIXTURES / "sample_codebook.yaml")
        all_codes = cb.all_codes
        assert len(all_codes) == 4
        assert all_codes[0].id == "CONFUSION_NAV"

    def test_code_type(self):
        cb = load_codebook(FIXTURES / "sample_codebook.yaml")
        for code in cb.all_codes:
            assert code.code_type == CodeType.DEDUCTIVE

    def test_indicators(self):
        cb = load_codebook(FIXTURES / "sample_codebook.yaml")
        nav = cb.all_codes[0]
        assert "couldn't find" in nav.indicators

    def test_example_quotes(self):
        cb = load_codebook(FIXTURES / "sample_codebook.yaml")
        nav = cb.all_codes[0]
        assert len(nav.example_quotes) > 0
