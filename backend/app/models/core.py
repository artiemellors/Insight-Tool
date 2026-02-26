"""Core data models for the Insight Tool.

These Pydantic models define the shared vocabulary across all agents.
Every agent input/output is a typed model — no raw text passes between agents.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Transcript
# ---------------------------------------------------------------------------

class Turn(BaseModel):
    """A single speaker turn in a transcript, normalised from any source format."""

    turn_index: int
    speaker: str
    text: str
    start: Optional[float] = None  # seconds from start
    end: Optional[float] = None
    is_interviewer: bool = False


# ---------------------------------------------------------------------------
# Interview Guide
# ---------------------------------------------------------------------------

class GuideQuestion(BaseModel):
    """A single question in the interview guide."""

    id: str = Field(description="Short identifier, e.g. 'OB1', 'FD2'")
    text: str
    section: str
    required: bool = True
    mapped_objective: Optional[str] = None
    probes: list[str] = Field(default_factory=list)


class GuideSection(BaseModel):
    name: str
    questions: list[GuideQuestion]


class InterviewGuide(BaseModel):
    sections: list[GuideSection]
    version: int = 1
    locked: bool = False
    locked_at: Optional[datetime] = None

    @property
    def all_questions(self) -> list[GuideQuestion]:
        return [q for s in self.sections for q in s.questions]


# ---------------------------------------------------------------------------
# Codebook
# ---------------------------------------------------------------------------

class CodeType(str, Enum):
    DEDUCTIVE = "deductive"
    EMERGENT = "emergent"


class Code(BaseModel):
    """A single code in the codebook."""

    id: str = Field(description="Short identifier, e.g. 'CONFUSION_NAV'")
    definition: str
    indicators: list[str] = Field(default_factory=list)
    example_quotes: list[str] = Field(default_factory=list)
    code_type: CodeType = CodeType.DEDUCTIVE


class Theme(BaseModel):
    """A top-level theme grouping one or more codes."""

    name: str
    codes: list[Code]


class Codebook(BaseModel):
    themes: list[Theme]
    version: int = 1
    locked: bool = False
    locked_at: Optional[datetime] = None

    @property
    def all_codes(self) -> list[Code]:
        return [c for t in self.themes for c in t.codes]


# ---------------------------------------------------------------------------
# Analysis outputs
# ---------------------------------------------------------------------------

class CodedTurn(BaseModel):
    """A turn with one or more codes applied by the Deductive Coder Agent."""

    turn_index: int
    code_id: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_quote: str
    needs_review: bool = False  # True when confidence < 0.6


class QuestionCoverageResult(BaseModel):
    """Coverage analysis for a single guide question."""

    question_id: str
    covered: bool
    depth_score: Optional[int] = Field(default=None, ge=1, le=5)
    supporting_turn_indices: list[int] = Field(default_factory=list)
    notes: Optional[str] = None


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SessionScorecard(BaseModel):
    coverage_pct: float
    avg_depth: float
    coded_turn_count: int
    emergent_theme_count: int


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

class EmergentTheme(BaseModel):
    label: str
    definition: str
    supporting_turn_indices: list[int] = Field(default_factory=list)
    session_count: int = 1


class Session(BaseModel):
    session_id: str = Field(default_factory=lambda: uuid4().hex[:8])
    participant_id: str
    transcript: list[Turn] = Field(default_factory=list)
    coverage_result: list[QuestionCoverageResult] = Field(default_factory=list)
    coded_turns: list[CodedTurn] = Field(default_factory=list)
    emergent_themes: list[EmergentTheme] = Field(default_factory=list)
    quality_scorecard: Optional[SessionScorecard] = None
    review_status: ReviewStatus = ReviewStatus.PENDING


# ---------------------------------------------------------------------------
# Study State — the shared object all agents read/write via the Orchestrator
# ---------------------------------------------------------------------------

class StudyState(BaseModel):
    study_id: str = Field(default_factory=lambda: uuid4().hex[:12])
    study_name: str = ""
    product_area: str = ""
    research_objectives: list[str] = Field(default_factory=list)
    interview_guide: Optional[InterviewGuide] = None
    codebook: Optional[Codebook] = None
    sessions: list[Session] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Structured JSON export — traceable, evidence-backed output
# ---------------------------------------------------------------------------

class EvidenceRef(BaseModel):
    """A single piece of evidence linking back to a specific transcript location."""

    turn_index: int
    speaker: str
    quote: str = Field(description="Exact text excerpt used as evidence")
    timestamp_start: Optional[float] = Field(
        default=None, description="Seconds from transcript start"
    )
    session_id: str
    participant_id: str


class CodeApplication(BaseModel):
    """A code applied to a turn, with full evidence traceability."""

    code_id: str
    code_definition: str
    theme: str
    confidence: float = Field(ge=0.0, le=1.0)
    needs_review: bool
    evidence: EvidenceRef


class CoverageDetail(BaseModel):
    """Coverage result for a single guide question, with supporting evidence."""

    question_id: str
    question_text: str
    section: str
    covered: bool
    depth_score: Optional[int] = Field(default=None, ge=1, le=5)
    notes: Optional[str] = None
    supporting_evidence: list[EvidenceRef] = Field(default_factory=list)


class SessionExport(BaseModel):
    """Fully traceable export of a single session's analysis."""

    session_id: str
    participant_id: str
    turn_count: int
    coverage: list[CoverageDetail] = Field(default_factory=list)
    coded_evidence: list[CodeApplication] = Field(default_factory=list)
    emergent_themes: list[EmergentTheme] = Field(default_factory=list)
    scorecard: Optional[SessionScorecard] = None


class StudyExport(BaseModel):
    """Full study export with evidence chain for every finding.

    Design principle: every coded turn and coverage result links back to
    the exact transcript turn, speaker, quote, and timestamp so that
    downstream consumers can verify any claim against the source material.
    """

    study_id: str
    study_name: str
    product_area: str
    research_objectives: list[str]
    exported_at: datetime = Field(default_factory=datetime.utcnow)
    codebook_version: Optional[int] = None
    guide_version: Optional[int] = None
    sessions: list[SessionExport] = Field(default_factory=list)
