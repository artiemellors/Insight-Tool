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
| `anthropic` | Deductive coding, depth scoring, emergent themes, synthesis |
| `Pydantic` | Structured LLM output validation |
| FastAPI | Backend API |
| PostgreSQL | Data persistence |
| React | Frontend |

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
