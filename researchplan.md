# Revised Build Plan: Transcript Analysis with Guide Comparison

---

## What Changes From the Original Plan

| Original | Adjusted |
|---|---|
| Started from audio/video | Starts from raw transcript files |
| No audio transcription layer needed | File format detection + parsing layer instead |
| Single-pass insight extraction | Three-way triangulation: transcript × interview guide × theme guide |
| Insights were emergent only | Insights are both deductive (from guides) AND emergent (discovered) |
| No quality assessment | Session quality scoring: coverage, depth, off-script detection |

---

## New Inputs (First-Class)

### 1. Transcript File

Raw conversational text in any of these formats:

| Format | Source |
|---|---|
| `.vtt` | Zoom, Teams, Otter.ai, Whisper |
| `.srt` | Zoom, YouTube, older services |
| `.docx` | Teams Word export, Rev human transcription |
| `.pdf` | Rev.com deliverables, NVivo exports |
| `.txt` | Otter.ai free, manual transcription |
| `.json` | Rev.ai API, AssemblyAI API |

All formats get normalised into a canonical internal `Transcript` structure: `{speaker, text, start, end, turn_index}` per turn.

### 2. Interview Guide (YAML/JSON)

Structured document containing:
- Study research questions and objectives
- Sections (intro, warmup, core topics, closing)
- Per-question: the question text, required/optional flag, associated probes

### 3. Theme Guide / Codebook (YAML/JSON)

Structured document containing:
- Theme hierarchy: top-level theme → sub-themes → codes
- Per code: definition, inclusion criteria, exclusion criteria, example quotes, linguistic indicators

---

## Core Analysis — Three-Way Triangulation

```
Transcript File
      │
      ▼
 [Parse & Normalise]
      │
      ▼
Canonical Turns ──────────────────────────────────┐
      │                                            │
      │    Interview Guide                         │
      ├──────────────────► Guide Coverage Analysis │
      │                     - Which Qs covered?    │
      │                     - Depth per question   │
      │                     - Off-script moments   │
      │                                            │
      │    Theme Guide                             │
      ├──────────────────► Deductive Coding        │
      │                     - Apply codebook codes │
      │                     - Confidence scoring   │
      │                                            ▼
      └──────────────────► Inductive Pass ──► GAP ANALYSIS REPORT
                            - Uncoded segments
                            - Emergent themes
```

---

## Phase Plan

### Phase 1 — MVP (4–6 weeks)

- Multi-format transcript parser (VTT, SRT, DOCX, TXT, PDF, JSON)
- Auto-detect format + normalise to canonical `Turn` objects
- Interview guide upload (YAML/JSON) — define questions, sections, probes
- Theme guide upload (YAML/JSON) — define codes, definitions, indicators, examples
- Embedding-based pre-filter: match turns to guide questions + codes using cosine similarity (reduces LLM calls by ~70%)
- LLM deductive coding pass: apply codebook codes to candidate turns, return confidence + evidence quote
- Guide coverage report: which questions were covered, skipped, shallow
- Basic annotated transcript view: turns highlighted by code, linked to source

**Stack:** FastAPI + PostgreSQL + OpenAI API + React

---

### Phase 2 — Core Product (6–8 weeks)

- LLM depth scoring per guide question (specificity, elaboration, emotional salience, actionability — each 1–5)
- Off-script detection: classify uncovered segments as `productive_emergent | productive_rapport | unproductive_tangent | interviewer_error`
- Inductive pass: find recurring patterns in uncoded turns → propose emergent themes
- Three-way gap analysis report:
  - Guide gaps: questions asked but not answered, questions never asked
  - Codebook gaps: expected themes with zero evidence
  - Emergent gaps: patterns in transcript covered by neither guide nor codebook
- Session quality scorecard (coverage %, avg depth score, emergent count)
- Cross-session theme heatmap: theme × participant occurrence matrix
- Codebook iteration recommendations: add/split/retire codes based on evidence

---

### Phase 3 — Advanced (8–12 weeks)

- Multi-session saturation tracking: new theme emergence rate per additional transcript
- Speaker-level breakdown: which themes appear in interviewer vs. participant turns
- Interviewer behaviour analysis: probe usage rate, leading question detection, missed probe flags
- Guide evolution workflow: accept/reject suggested additions to interview guide and codebook from within the tool
- PII redaction before LLM processing (Microsoft Presidio)
- RAG-powered Q&A across all sessions: "Which participants mentioned workarounds for X?"
- Export: annotated transcript HTML, gap analysis Markdown, updated codebook YAML draft, CSV for cross-session heatmap

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

### Codebook Recommendations

```
ADD:    EXPORT_PAIN — appeared in 4/5 sessions, high salience, not in codebook
SPLIT:  CONFUSION_NAV → separate nav vs. information architecture confusion
RETIRE: DELIGHT — only 2/5 sessions, low confidence, collapse into "Positive Moments"
PROBE:  Add to OB2 — "Did you look for help anywhere?" (3 sessions surfaced this organically)
```

---

## Technical Stack

### Parsing

| Library | Purpose |
|---|---|
| `webvtt-py` | VTT files |
| `python-docx` | DOCX files |
| `pdfplumber` | PDF files (structured) |
| `PyMuPDF (fitz)` | Complex/scanned PDFs |
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
| `openai` / `anthropic` | Deductive coding, depth scoring, emergent themes |
| `Pydantic` | Structured LLM output validation |
| FastAPI | Backend API |
| PostgreSQL | Data persistence |
| React | Frontend |

---

## Key Algorithmic Decisions

### Chunking Granularity

Speaker turn is the natural unit. Avoid sentence-level chunking (loses context). For long monologues (>300 words), split on sentence boundaries into ~150-word windows with 50-word overlap.

### LLM Model Choice

- GPT-4o achieves κ = 0.61–0.65 agreement with human coders for thematic coding
- GPT-4o-mini achieves κ = 0.41–0.58 — adequate for first pass, requires human review on low-confidence codes
- Use `temperature=0` for deductive passes; `temperature=0.3–0.5` for emergent theme generation

### Embedding Pre-Filter

Before sending every segment to the LLM for every code (O(n×m) calls), use `sentence-transformers` cosine similarity to pre-filter candidates. Only send segment→code pairs where similarity > 0.3. Reduces LLM calls by 60–80% in practice.

### Human-in-the-Loop

Always expose confidence scores. Surface turns with `confidence < 0.6` for researcher review. Never auto-accept low-confidence codes into permanent records.

### Caching

Cache LLM responses by `hash(segment_text + code_id + model_version)`. Rerunning after codebook updates only reprocesses turns affected by changed codes.
