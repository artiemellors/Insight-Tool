# Insight Tool — Research Plan & Build Strategy

---

## Purpose

Build an AI-assisted tool that analyses customer interview transcripts and/or videos to produce robust, evidence-backed insights for product design opportunities.

---

## Current Research Process

The baseline process this tool is designed to support and augment:

| Step | Activity | Current State |
|---|---|---|
| 1 | Theme research & discovery plan objectives | Manual — lives in a document |
| 2 | Create interview guide to target research objectives | Manual — unstructured doc |
| 3 | Interview customers on Askable platform | Human-led |
| 4 | Take raw transcript files → organise answers against guide | Partially AI-assisted |
| 5 | Analyse cleaned transcripts → compare for patterns & themes | Manual, labour-intensive |
| 6 | Synthesise insights with citations and evidence trail | Manual |
| 7 | Compile report: Key Insights, Observations, Recommendations | Manual |

**Key problems:**
- Inputs (objectives, guide, codebook) are unstructured — AI can only bolt on at step 4
- Steps run waterfall — session 1 can't inform session 2's approach
- "Organise answers against the guide" is under-ambitious — sorting, not analysis
- No principled signal for when you have enough data (saturation)
- Codebook is implicit, not explicit — limits systematic analysis

---

## Improved Process with AI & Agentic Flows

```
╔══════════════════════════════════════════════════════════════╗
║  PRE-RESEARCH                                                ║
║                                                              ║
║  Research Brief (structured YAML)                            ║
║    Objectives → hypotheses → participant criteria            ║
║         │                                                    ║
║         ▼                                                    ║
║  AI-assisted Interview Guide                                 ║
║    Generated from brief → probes suggested                   ║
║    Flags: leading questions, gaps vs. objectives             ║
║         │                                                    ║
║         ▼                                                    ║
║  Codebook / Theme Guide (explicit YAML)                      ║
║    Themes expected from hypotheses → deductive codes         ║
╚══════════════════════════════════════════════════════════════╝
                          │
                          ▼  [Interviews run on Askable]
╔══════════════════════════════════════════════════════════════╗
║  PER SESSION  (runs after each interview — not in batch)     ║
║                                                              ║
║  Ingest from Askable → auto-detect format → parse to turns   ║
║         │                                                    ║
║         ├──► Guide Coverage Analysis                         ║
║         │      Which questions covered? Depth scored?        ║
║         │      Probes used? Off-script moments classified?   ║
║         │                                                    ║
║         ├──► Deductive Coding (against codebook)             ║
║         │      Apply expected themes → confidence + quote    ║
║         │                                                    ║
║         ├──► Inductive Pass (uncoded turns)                  ║
║         │      What emerged not in guide or codebook?        ║
║         │                                                    ║
║         ├──► Human Review Gate ← low-confidence codes        ║
║         │                                                    ║
║         └──► Session Quality Scorecard                       ║
║                Feeds back into next interview preparation    ║
╚══════════════════════════════════════════════════════════════╝
                          │
                          ▼  [Updated after each new session]
╔══════════════════════════════════════════════════════════════╗
║  CROSS-SESSION                                               ║
║                                                              ║
║  Theme heatmap: which themes appear across participants       ║
║  Saturation tracking: are new themes still emerging?         ║
║  Participant segmentation: who clusters by theme pattern     ║
║  Codebook iteration: confirm / add / split / retire codes    ║
╚══════════════════════════════════════════════════════════════╝
                          │
                          ▼
╔══════════════════════════════════════════════════════════════╗
║  SYNTHESIS                                                   ║
║                                                              ║
║  AI generates candidate insight statements                   ║
║    Ranked by: frequency + emotional salience +               ║
║    alignment to research objectives                          ║
║  Each insight: theme + quotes + participant count            ║
║  Human editorial review ← researcher judgement essential     ║
╚══════════════════════════════════════════════════════════════╝
                          │
                          ▼
╔══════════════════════════════════════════════════════════════╗
║  REPORT                                                      ║
║                                                              ║
║  Key Insights → Observations → Recommendations               ║
║  All claims linked to coded evidence and source quotes       ║
║  Human review and finalisation                               ║
╚══════════════════════════════════════════════════════════════╝
```

---

## The Three Biggest Improvements

**1. Machine-readable inputs from day one**
Research objectives, interview guide, and codebook become structured YAML/JSON, not Word docs. AI uses them as ground truth throughout the entire pipeline — not just at step 4.

**2. Per-session feedback loop**
Don't wait until all interviews are done. After session 1, the tool surfaces which questions got shallow answers, what emerged unexpectedly, and what to probe harder in session 2. Each subsequent interview is smarter than the last.

**3. Saturation detection**
A principled answer to "when do we have enough data?" Cross-session theme tracking shows when new sessions stop producing new themes — that's the signal to stop collecting and start synthesising.

---

## Inputs (Machine-Readable from Day One)

### Research Brief (YAML)
- Research objectives — the questions we need to answer
- Hypotheses to test
- Participant criteria and recruitment screener
- Expected session duration and format

### Interview Guide (YAML/JSON)

| Field | Description |
|---|---|
| Research questions | Top-level objectives the guide is designed to answer |
| Sections | Intro, warmup, core topics, concept test, closing |
| Per question | Text, required/optional, mapped research objective, probes |

AI uses this to score coverage, measure depth, detect off-script moments, and suggest improvements after each session.

### Transcript File

Raw conversational text exported from Askable or any transcription platform:

| Format | Source |
|---|---|
| `.vtt` | Zoom, Teams, Otter.ai, Whisper |
| `.srt` | Zoom, YouTube, older services |
| `.docx` | Teams Word export, Rev human transcription |
| `.pdf` | Rev.com deliverables, NVivo exports |
| `.txt` | Otter.ai free, manual transcription |
| `.json` | Rev.ai API, AssemblyAI API |

All formats normalised to a canonical `Turn` structure: `{speaker, text, start, end, turn_index}`.

### Theme Guide / Codebook (YAML/JSON)

| Field | Description |
|---|---|
| Theme hierarchy | Top-level theme → sub-themes → codes |
| Per code | Definition, inclusion criteria, exclusion criteria |
| Indicators | Linguistic signals that suggest this code |
| Example quotes | Verbatim examples that exemplify the code |
| Code type | Deductive (hypothesis-driven) or emergent (discovered) |

---

## Core Analysis — Three-Way Triangulation

Every transcript is analysed against both structured inputs simultaneously:

```
Transcript Turns ──────────────────────────────────────┐
      │                                                 │
      │    Interview Guide                              │
      ├──────────────────► Guide Coverage Analysis      │
      │                     - Which Qs covered?         │
      │                     - Depth per question (1–5)  │
      │                     - Off-script classification │
      │                                                 │
      │    Theme Guide / Codebook                       │
      ├──────────────────► Deductive Coding             │
      │                     - Apply codebook codes      │
      │                     - Confidence + evidence     │
      │                                                 ▼
      └──────────────────► Inductive Pass ──► GAP ANALYSIS REPORT
                            - Uncoded segments               │
                            - Emergent themes                │
                                                             ▼
                                                  Feeds next session
                                                  prep + codebook
                                                  iteration
```

---

## Agent Orchestration Architecture

The workflow is implemented as a multi-agent system: one **Orchestrator** that manages study-level state and routes work to **Specialist Agents** that each own a single concern. Agents communicate via a shared `StudyState` object — not directly with each other.

```
                    ┌─────────────────────────┐
                    │      ORCHESTRATOR        │
                    │                          │
                    │  - Manages StudyState    │
                    │  - Routes tasks          │
                    │  - Tracks saturation     │
                    │  - Surfaces human gates  │
                    └──────────┬───────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   PRE-RESEARCH          PER-SESSION          CROSS-SESSION
   AGENTS                AGENTS               AGENTS
```

---

### Agent Registry

#### Pre-Research Agents (run once per study)

| Agent | Input | Output | Runs |
|---|---|---|---|
| **Brief Agent** | Product brief / HMW statements | Structured YAML research brief | Sequential first |
| **Guide Generator** | Research brief | Interview guide YAML + validation report | Sequential after Brief |
| **Codebook Seeder** | Brief + guide | Initial deductive codebook YAML | Sequential after Guide |

These three run sequentially — each output is ground truth for the next.

---

#### Per-Session Agents (after each Askable interview)

```
Transcript file
      │
      ▼
┌─────────────┐
│   PARSER    │  ← runs first; all others depend on its output
│   AGENT     │
└──────┬──────┘
       │  canonical Turn[]
       │
       ├──────────────────────────────────────┐
       ▼                                      ▼
┌──────────────────┐                ┌─────────────────────┐
│  GUIDE COVERAGE  │                │  DEDUCTIVE CODER    │
│  AGENT           │                │  AGENT              │
│                  │                │                     │
│ - Qs hit/missed  │                │ - Apply codebook    │
│ - Depth score    │                │ - Confidence +      │
│ - Off-script     │                │   evidence quote    │
└────────┬─────────┘                └──────────┬──────────┘
         │                                      │
         └──────────────────┬───────────────────┘
                            │  coded + annotated turns
                            ▼
                  ┌─────────────────────┐
                  │  INDUCTIVE          │
                  │  DISCOVERY AGENT    │  ← runs on uncoded turns only
                  │                     │
                  │  - Emergent themes  │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │  SESSION QA AGENT   │
                  │                     │
                  │  - Flags low-conf   │
                  │  - Quality scorecard│
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │  HUMAN REVIEW GATE  │  ← researcher confirms flagged codes
                  │                     │     before anything is committed
                  └─────────────────────┘
```

**Guide Coverage Agent** and **Deductive Coder Agent** run in **parallel** — they are fully independent on the same parsed input. This is the biggest latency reduction in the pipeline.

---

#### Cross-Session Agents (after each reviewed session is committed)

| Agent | Role | Pattern |
|---|---|---|
| **Pattern Aggregator** | Updates theme heatmap across all sessions | Accumulator — diffs new session only |
| **Saturation Monitor** | Tracks theme emergence rate; fires signal when rate drops below threshold | Event-driven trigger |
| **Codebook Curator** | Recommends add / split / retire based on cross-session evidence | Runs every N sessions or on-demand |

---

#### Synthesis & Report Agents

| Agent | Role | Runs |
|---|---|---|
| **Insight Generator** | Ranked insight statements from confirmed patterns | On-demand after researcher signals ready |
| **Evidence Linker** | Attaches verbatim quotes + participant IDs to each insight | Sequential after Insight Generator |
| **Report Compiler** | Assembles final report structure | Sequential after Evidence Linker; human finalises |

---

### Claude Capability Mapping

Each agent uses the Claude capability best suited to its task — not every agent needs the most expensive call.

| Capability | Where applied | Why |
|---|---|---|
| **Extended thinking** | Brief Agent, Codebook Seeder, Insight Generator | Multi-step reasoning across competing evidence; weighing objective hierarchy; inferring observable indicators from abstract hypotheses |
| **Tool use** | All agents | File read/write, database queries, guide/codebook validation, heatmap queries |
| **Structured output (Pydantic)** | Every agent boundary | Agents communicate via validated schemas — never raw text. Orchestrator always knows the shape of what it receives |
| **Parallel subagent spawning** | Orchestrator, per session | Guide Coverage + Deductive Coder spawned simultaneously on same transcript. Also: multiple sessions can run in parallel on batch upload |
| **`temperature=0`** | Deductive Coder | Deterministic code application; reproducible results |
| **`temperature=0.3–0.5`** | Inductive Discovery, Insight Generator | Creative pattern recognition; emergent theme generation |

---

### Shared Study State

Agents do not call each other — they read from and write to a shared `StudyState`. The Orchestrator owns mutation.

```yaml
StudyState:
  study_id: str
  research_brief: ResearchBrief
  interview_guide: InterviewGuide
  codebook:
    version: int
    codes: Code[]
  sessions:
    - session_id: str
      participant_id: str
      transcript: Turn[]
      coverage_result: QuestionCoverageResult[]
      coded_turns: CodedTurn[]
      emergent_themes: EmergentTheme[]
      quality_scorecard: SessionScorecard
      review_status: pending | approved | rejected
  cross_session:
    theme_heatmap: ThemeMatrix
    saturation_curve: float[]        # new theme emergence rate per session
    participant_clusters: Cluster[]
  insights: InsightStatement[]
  report_draft: Report | null
```

Every agent output is a typed Pydantic model. The Orchestrator writes each model into the relevant `StudyState` field after validation.

---

### The Per-Session Feedback Loop

This is the highest-value feature in the system — it makes the research process smarter across sessions, not just within them.

```
Session N complete
      │
      ▼
Session QA Agent → quality scorecard
      │
      ▼
Human review gate (researcher confirms/edits codes)
      │
      ▼
Pattern Aggregator updates StudyState
      │
      ▼
┌──────────────────────────────────────────────────┐
│  NEXT SESSION PREP AGENT                          │
│                                                  │
│  Reads: current StudyState                       │
│  Outputs: briefing delivered to researcher       │
│  before next Askable interview                   │
│                                                  │
│  Example output:                                 │
│  "In Session N+1, prioritise:                    │
│   - FD1 (skipped in last 2 sessions)             │
│   - Probe OB2 deeper (avg depth 2.1/5)           │
│   - Test EMERGENT: export_pain (3/5 sessions,    │
│     not yet in codebook — propose adding)"       │
└──────────────────────────────────────────────────┘
      │
      ▼
Researcher reads brief before Askable interview
```

---

### Orchestration Patterns in Use

| Pattern | Where applied |
|---|---|
| **Sequential pipeline** | Brief → Guide → Codebook Seeder (pre-research); Parser → Inductive → QA (per session) |
| **Fan-out / fan-in** | Orchestrator fans out to Guide Coverage + Deductive Coder in parallel; fans back in when both complete |
| **Accumulator** | Pattern Aggregator processes only the diff from the new session — not all sessions each time |
| **Event-driven trigger** | Saturation Monitor watches emergence curve; fires when slope drops below threshold, prompting researcher |
| **Human-in-the-loop gate** | After Session QA Agent; orchestrator pauses, presents flagged items, waits for researcher confirmation before committing |
| **Feedback loop** | Session N output → Next Session Prep Agent → researcher brief → improved Session N+1 |

---

## Build Phases

### Phase 1 — MVP (4–6 weeks)
*Goal: replace the manual "organise against guide" step with a robust analysis layer*

- Multi-format transcript parser (VTT, SRT, DOCX, TXT, PDF, JSON)
- Auto-detect format + normalise to canonical `Turn` objects
- Interview guide upload (YAML/JSON) — questions, sections, probes
- Theme guide / codebook upload (YAML/JSON) — codes, definitions, indicators, examples
- Embedding-based pre-filter: match turns to questions + codes via cosine similarity (reduces LLM calls ~70%)
- LLM deductive coding: apply codebook codes to candidate turns → confidence + evidence quote
- Guide coverage report: questions covered, skipped, shallow
- Basic annotated transcript view: turns highlighted by code, linked to source

**Stack:** FastAPI + PostgreSQL + Claude API + React

---

### Phase 2 — Core Product (6–8 weeks)
*Goal: enable cross-session analysis and the per-session feedback loop*

- LLM depth scoring per guide question (specificity, elaboration, emotional salience, actionability — 1–5 each)
- Off-script detection: classify uncovered segments as `productive_emergent | productive_rapport | unproductive_tangent | interviewer_error`
- Inductive pass: find recurring patterns in uncoded turns → propose emergent themes
- Session quality scorecard (coverage %, avg depth, emergent theme count)
- Cross-session theme heatmap: theme × participant occurrence matrix
- Saturation tracker: chart new theme emergence rate across sessions
- Codebook iteration recommendations: add / split / retire codes based on cross-session evidence
- Three-way gap analysis:
  - Guide gaps: questions asked but answered shallowly, or never asked
  - Codebook gaps: expected themes with zero evidence in transcript
  - Emergent gaps: patterns in transcript covered by neither guide nor codebook

---

### Phase 3 — Advanced (8–12 weeks)
*Goal: synthesis, reporting, and full research lifecycle support*

- AI-generated candidate insight statements ranked by frequency + salience + objective alignment
- Each insight: theme + definition + supporting quotes + participant count + confidence
- Participant segmentation: cluster participants by theme occurrence pattern
- Interviewer behaviour analysis: probe usage rate, leading question detection, missed probe flags
- Guide evolution workflow: accept/reject suggested additions to guide and codebook within the tool
- PII redaction before LLM processing (Microsoft Presidio)
- RAG-powered Q&A across all sessions: "Which participants mentioned workarounds for X?"
- Auto-generated report structure: Key Insights → Observations → Recommendations, all claims linked to coded evidence
- Export: annotated transcript HTML, gap analysis Markdown, updated codebook YAML draft, cross-session heatmap CSV

---

## Key Outputs

### Session Quality Scorecard
```
Guide coverage:     8/10 questions  (80%)
Avg depth score:    3.2/5.0
Useful off-script:  3 moments → 2 worth adding to guide
Wasted time:        1 tangent (4 min)
Codebook coverage:  6/9 themes observed
Absent themes:      WORKAROUND_EXTERNAL, DELIGHT
Emergent themes:    2 new patterns found
```

### Per-Question Coverage Table
```
ID    Question                       Covered?  Depth  Notes
OB1   Walk me through first login    YES       4/5    Strong, specific narrative
OB2   Was there a stuck moment?      YES       2/5    Shallow — probe not used
FD1   How did you find features?     NO        —      Skipped — ran long on OB2
```

### Annotated Transcript
```
[00:12:34] P1: "I just kept clicking on different tabs hoping to find settings."
           → CODES: [CONFUSION_NAV ★★★] [WORKAROUND_SELF ★★]
           → GUIDE: Covers OB2 (depth: 3/5)

[00:13:15] P1: "I honestly just Googled it."
           → CODES: [WORKAROUND_EXTERNAL ★★★] [EMERGENT: external_support_preference]
```

### Cross-Session Theme Heatmap
```
                       P01  P02  P03  P04  P05  Total
CONFUSION_NAV           ██   ██   █    ██   ██    9
CONFUSION_MENTAL_MODEL  ██   █    ██   —    █     6
WORKAROUND_EXTERNAL     █    —    ██   █    —     4
DELIGHT                 —    █    —    —    █     2
[EMERGENT] Export_pain  █    ██   —    ██   ██    6  ← not in codebook
```

### Codebook Iteration Recommendations
```
ADD:    EXPORT_PAIN — appeared in 4/5 sessions, high salience, not in codebook
SPLIT:  CONFUSION_NAV → separate nav confusion vs. IA confusion
RETIRE: DELIGHT — only 2/5 sessions, low confidence → collapse into "Positive Moments"
PROBE:  Add to OB2 — "Did you look for help anywhere?" (surfaced organically in 3 sessions)
```

---

## Technical Stack

### Parsing

| Library | Purpose |
|---|---|
| `webvtt-py` | VTT files |
| `python-docx` | DOCX files |
| `pdfplumber` | PDF files (structured layout) |
| `PyMuPDF (fitz)` | Complex / scanned PDFs |
| `PyYAML` | Interview guide + codebook YAML |

### NLP / Embedding

| Library | Purpose |
|---|---|
| `sentence-transformers` | Embedding pre-filter (cosine similarity) |
| `scikit-learn` | Occurrence matrix, clustering emergent themes |
| `presidio-analyzer` | PII redaction before LLM calls |

### Output

| Library | Purpose |
|---|---|
| `Jinja2` | Annotated transcript HTML |
| `pandas` | Theme heatmaps, cross-session analysis |

### Core

| Library | Purpose |
|---|---|
| `anthropic` | All LLM calls — deductive coding, depth scoring, emergent themes, synthesis, agent orchestration |
| `Pydantic` | Structured output validation at every agent boundary |
| FastAPI | Backend API |
| PostgreSQL | Data persistence (StudyState, coded turns, cross-session heatmap) |
| React | Frontend |

### Agent Orchestration

| Pattern | Implementation |
|---|---|
| Orchestrator | Single FastAPI service; owns `StudyState` mutation; routes tasks to specialist agents |
| Specialist agents | Separate async functions with typed Pydantic inputs/outputs; called via Claude tool use |
| Parallel fan-out | `asyncio.gather()` for Guide Coverage + Deductive Coder on same session |
| Shared state | `StudyState` persisted in PostgreSQL; agents read from DB, write via Orchestrator |
| Extended thinking | `thinking` parameter enabled on Brief Agent, Codebook Seeder, Insight Generator |
| Human gate | Orchestrator sets `review_status=pending`; waits for researcher API call to confirm/edit before proceeding |
| Event trigger | Saturation Monitor runs as a background task after each session commit; fires webhook to Orchestrator when threshold met |

---

## Key Algorithmic Decisions

### Chunking Granularity
Speaker turn is the natural coding unit. Avoid sentence-level chunking (loses context). For long monologues (>300 words), split on sentence boundaries into ~150-word windows with 50-word overlap.

### LLM Model Choice
- Claude Sonnet 4.6 for deductive coding — achieves κ = 0.61–0.65 agreement with human coders
- Smaller models adequate for first-pass filtering, require human review on low-confidence codes
- `temperature=0` for deductive passes; `temperature=0.3–0.5` for emergent theme generation

### Embedding Pre-Filter
Before sending every turn to the LLM for every code (O(n×m) calls), use `sentence-transformers` cosine similarity to pre-filter candidates. Only send turn→code pairs where similarity > 0.3. Reduces LLM calls by 60–80% in practice.

### Human-in-the-Loop Gates
- Always expose confidence scores alongside coded output
- Surface turns with `confidence < 0.6` for researcher review before any code is accepted
- Never auto-accept low-confidence codes into permanent records
- Synthesis insights require human editorial review before report generation

### Caching
Cache LLM responses by `hash(segment_text + code_id + model_version)`. Rerunning after codebook updates only reprocesses turns affected by changed codes.

### Agent Isolation and Failure Handling
Each specialist agent is idempotent — it can be re-run on the same input without side effects. If an agent fails, the Orchestrator retries with exponential backoff (2s, 4s, 8s, 16s) before surfacing an error to the researcher. Partial results are never committed to `StudyState` — writes are transactional.

### Parallelism Budget
Running Guide Coverage and Deductive Coder in parallel doubles the Claude API concurrency per session. Set a per-study concurrency cap (default: 5 parallel agent calls) to avoid rate limit exhaustion on batch uploads of multiple sessions.

### Extended Thinking vs. Standard for Each Agent
Use extended thinking (`budget_tokens=8000`) only where multi-step reasoning across competing evidence is required:
- Brief Agent (objective hierarchy)
- Codebook Seeder (hypothesis → observable indicator inference)
- Insight Generator (weighing frequency vs. salience vs. objective alignment)

Use standard (no thinking) for all other agents — deductive coding, parsing, guide coverage, report compilation. Thinking adds latency and cost where the task is structured and deterministic.

### Structured Output Contract
Every agent function has a typed signature: `agent_fn(input: AgentInput) -> AgentOutput`. The Orchestrator never passes raw text between agents. If a Claude response fails Pydantic validation, the Orchestrator retries once with an explicit correction prompt before raising to the researcher. This makes the pipeline auditable — every agent's output is a stored, versioned record.
