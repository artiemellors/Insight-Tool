# Insight Tool — Research Plan & Build Strategy

---

## Purpose

Build an AI-assisted tool that analyses customer interview transcripts and/or videos to produce robust, evidence-backed insights for product design opportunities.

---

## Research Process

Our research process follows five core steps. The researcher leads throughout; AI augments the labour-intensive middle steps.

| Step | Activity | Who leads | AI role |
|---|---|---|---|
| 1 | **Research Plan** — Define research focus, objectives, and interview guide (sections containing questions) | Researcher | None — this is the researcher's domain |
| 2 | **Organise Data** — Take raw interview transcripts and order responses against the corresponding guide sections/questions | Researcher reviews | AI does the heavy lifting — maps transcript turns to guide questions |
| 3 | **Pull Out Themes** — Work through organised transcripts and surface emergent themes within each individual interview | Researcher reviews | AI proposes candidate themes with supporting quotes |
| 4 | **Insights** — Compare all interviews and themes with each other; synthesise insights by identifying shared patterns, common pains, and alike themes. Summarise each insight in a sentence, pull out a hero quote, and provide clear citations and source trail | Researcher reviews & edits | AI generates candidate insights, ranks by evidence strength, links citations |
| 5 | **Report** — Compile the final deliverable | Researcher finalises | AI assembles draft structure from approved insights |

---

## How AI Works With Us

```
╔══════════════════════════════════════════════════════════════╗
║  STEP 1 — RESEARCH PLAN  (researcher-led, no AI)            ║
║                                                              ║
║  Research focus & objectives                                 ║
║  Interview guide: sections → questions                       ║
║                                                              ║
║  This is the researcher's domain — AI does not generate      ║
║  or modify the plan. It becomes the ground truth for all     ║
║  downstream analysis.                                        ║
╚══════════════════════════════════════════════════════════════╝
                          │
                          ▼  [Interviews run on Askable]
╔══════════════════════════════════════════════════════════════╗
║  STEP 2 — ORGANISE DATA  (AI-led, researcher reviews)        ║
║                                                              ║
║  Upload transcripts → parse to speaker turns                 ║
║         │                                                    ║
║         └──► Map each turn to guide sections/questions        ║
║              Researcher reviews and corrects mappings         ║
╚══════════════════════════════════════════════════════════════╝
                          │
                          ▼
╔══════════════════════════════════════════════════════════════╗
║  STEP 3 — PULL OUT THEMES  (AI-led, researcher reviews)      ║
║                                                              ║
║  For each organised transcript:                              ║
║         │                                                    ║
║         └──► Surface emergent themes with supporting quotes   ║
║              Researcher reviews, merges, or discards themes  ║
╚══════════════════════════════════════════════════════════════╝
                          │
                          ▼
╔══════════════════════════════════════════════════════════════╗
║  STEP 4 — INSIGHTS  (AI-led, researcher reviews & edits)     ║
║                                                              ║
║  Compare all interviews and themes with each other           ║
║         │                                                    ║
║         ├──► Identify shared patterns, common pains,         ║
║         │    alike themes across participants                 ║
║         │                                                    ║
║         ├──► Generate candidate insight statements            ║
║         │    Each: one-sentence summary + hero quote          ║
║         │                                                    ║
║         └──► Provide citations and source trail               ║
║                                                              ║
║  Researcher reviews, edits, and approves insights            ║
╚══════════════════════════════════════════════════════════════╝
                          │
                          ▼
╔══════════════════════════════════════════════════════════════╗
║  STEP 5 — REPORT  (AI drafts, researcher finalises)          ║
║                                                              ║
║  Key Insights → Observations → Recommendations               ║
║  All claims linked to evidence and source quotes             ║
║  Researcher reviews and finalises before delivery            ║
╚══════════════════════════════════════════════════════════════╝
```

---

## User Flow & Interface Design

### Interface Types

Two modes are used throughout the tool — chosen based on the nature of the task at each stage:

| Type | When used | Why |
|---|---|---|
| **Structured view** | Displaying and editing codebooks, guides, annotated transcripts, heatmaps | Researcher needs to scan, compare, and edit structured data efficiently |
| **Conversational UI** | Human review gate, codebook curation, next session prep, synthesis Q&A | Researcher needs to explain a judgement call in plain language; system must interpret and apply it |

---

### Overall Journey Map

```
STUDY SETUP        PRE-RESEARCH          PER SESSION           CROSS-SESSION         SYNTHESIS          REPORT
    │                    │                    │                      │                    │                 │
Create study    Brief → Guide →         Upload transcript      View heatmap         Review insights   Preview &
                Codebook seed           Anonymise + analyse    Curate codebook      Edit statements   export
                                        Human review gate      Saturation check
                                        Next session prep
                                             │
                                        [repeat per session]
```

---

### Stage 0 — Study Setup

**Interface type:** Structured form

**Screen: New Study**

| Field | Input type | Notes |
|---|---|---|
| Study name | Text | e.g. "Onboarding — Feb 2026" |
| Product area | Text or select | Context for AI throughout |
| HMW statements | Multi-line text | "How might we..." framing |
| Research objectives | Multi-line text | The questions we need to answer |
| Participant criteria | Text | Who is being recruited |
| Target session count | Number | How many interviews planned |
| Participant ID scheme | Radio | Auto-generated (P01, P02...) or custom prefix |
| AI analysis consent | Checkbox | Researcher confirms participants were informed this interview may be analysed by AI |

**Actions:**
- Save draft
- Generate Brief — triggers Brief Agent, produces structured YAML research brief
- View generated brief (read-only preview, researcher confirms or edits)

**Human judgement moment:** Researcher reviews the structured brief the AI has generated from their freeform inputs and confirms it accurately represents their intent before any downstream agents use it as ground truth.

---

### Stage 1 — Guide Review

**Interface type:** Structured view with inline edit

**Screen: Interview Guide**

```
┌─────────────────────────────────────────────────────────────┐
│  Section: Core Questions                    [+ Add section] │
├─────────────────────────────────────────────────────────────┤
│  OB1  Walk me through your first login         [Required]   │
│       Mapped to: Objective 1                               │
│       Probes: "What did you expect to see?" /              │
│       "Were you surprised by anything?"                    │
│       [Edit]  [Delete]  [Mark optional]                    │
├─────────────────────────────────────────────────────────────┤
│  ⚠️  OB3  Do you prefer X or Y?               [Flagged]    │
│       Issue: Leading question — assumes preference exists  │
│       Suggestion: "How do you think about X?"              │
│       [Accept suggestion]  [Edit manually]  [Dismiss]      │
└─────────────────────────────────────────────────────────────┘
```

**Validation panel (right sidebar):**
- Questions mapped to objectives — any objectives uncovered?
- Flagged questions (leading, ambiguous, out of scope)
- Estimated session duration based on question count

**Actions:**
- Edit any question inline
- Accept / dismiss AI flags
- Reorder sections (drag)
- Add / delete questions
- Lock guide — creates v1 baseline; any subsequent changes are versioned and flagged in cross-session analysis

**Human judgement moment:** Researcher locks the guide. This is a commitment — any changes after this point are tracked as a new version and surfaced in cross-session analysis (e.g. "Q added after session 2").

---

### Stage 2 — Codebook Review

**Interface type:** Structured view with inline edit

**Screen: Codebook**

```
┌────────────────────────────────────────────────────────────────┐
│  Theme: NAVIGATION CONFUSION            [Deductive]  v1        │
│                                                                │
│  Codes                                                         │
│  ├── CONFUSION_NAV                                             │
│  │     Definition: Participant expresses difficulty            │
│  │     locating a UI element or understanding layout           │
│  │     Indicators: "couldn't find", "kept clicking",           │
│  │     "didn't know where"                                     │
│  │     Example: "I just kept clicking different tabs"          │
│  │     [Edit]  [Delete]                                        │
│  └── CONFUSION_MENTAL_MODEL                                    │
│        Definition: Participant's expectation of system         │
│        behaviour does not match actual behaviour               │
│        [Edit]  [Delete]                                        │
│                                                                │
│  [+ Add code]                                                  │
└────────────────────────────────────────────────────────────────┘
```

**Actions:**
- Edit code definition, indicators, example quotes
- Add / delete codes
- Drag codes between themes
- Add new theme
- Lock codebook — creates v1 baseline

**Human judgement moment:** Researcher confirms the codebook accurately reflects their hypotheses before the first session runs deductive coding against it.

---

### Stage 3 — Transcript Upload (Per Session)

**Interface type:** Upload → anonymisation review → progress

This is a three-step sequence. No AI analysis begins until anonymisation is confirmed.

**Step 1 — Upload**

```
┌─────────────────────────────────────────────────────┐
│  Session 3 of 8  ·  Participant: P03                │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  Drag transcript file here                  │   │
│  │  or click to browse                         │   │
│  │  .vtt  .srt  .docx  .pdf  .txt  .json       │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Detected format: VTT                               │
│  Duration: 52 min  ·  Turns: 184                    │
│                                                     │
│  [Scan for personal information]                    │
└─────────────────────────────────────────────────────┘
```

**Step 2 — Anonymisation review (human gate — see Privacy section)**

Researcher reviews and confirms all PII redactions before any AI call is made. Original transcript is discarded at the end of this step.

**Step 3 — Processing progress**

```
  ✓  Format detected — VTT
  ✓  Parsed to 184 turns
  ✓  Anonymised — original discarded
  ●  Guide coverage analysis...
  ●  Deductive coding...         ← parallel
     Inductive pass  (waiting)
     Session QA  (waiting)
```

---

### Stage 4 — Session Analysis (Per Session)

**Interface type:** Multi-panel structured view

```
┌──────────────────┬──────────────────────────┬─────────────────────┐
│  GUIDE COVERAGE  │  ANNOTATED TRANSCRIPT    │  CODES              │
│                  │                          │                     │
│  OB1  ████  4/5  │  [00:12:34] [PARTICIPANT]│  Active filters:    │
│  OB2  ██    2/5  │  "I just kept clicking   │  All codes  ▼       │
│  OB3  ████  4/5  │   on different tabs."    │                     │
│  FD1  —     —    │  CONFUSION_NAV  ★★★      │  CONFUSION_NAV  12  │
│  FD2  ███   3/5  │  WORKAROUND_SELF  ★★     │  WORKAROUND  8      │
│                  │  OB2  depth 3/5          │  DELIGHT  2         │
│  Skipped: FD1    │                          │  [EMERGENT]         │
│  [See why]       │  [00:13:15] [PARTICIPANT]│  export_pain  4     │
│                  │  "I honestly just        │                     │
│  Coverage: 80%   │   Googled it."           │                     │
│  Avg depth: 3.2  │  WORKAROUND_EXT  ★★★    │                     │
└──────────────────┴──────────────────────────┴─────────────────────┘
```

All quotes shown are already anonymised — participant names replaced with `[PARTICIPANT]` etc. prior to this view.

**Actions — Transcript panel:**
- Click any turn to see its full coding detail
- Filter turns by code, depth score, confidence level, or guide question
- Flag a turn as noise (exclude from analysis)
- Add a manual code to a turn

**Actions — Coverage panel:**
- Click any question to jump to the first turn that covers it
- See depth breakdown (specificity / elaboration / emotional salience / actionability)
- See off-script classification for uncovered segments

**Actions — Codes panel:**
- Filter transcript by clicking a code
- Hover to see definition

---

### Stage 5 — Human Review Gate (Per Session)

**Interface type:** Conversational panel

Triggered automatically after Session QA Agent runs. Appears as a slide-in panel over the analysis screen. Nothing is committed to StudyState until the researcher completes this step.

```
┌────────────────────────────────────────────────────────────────┐
│  Review — Session 3                              3 items       │
│                                                                │
│  I've flagged 3 codes for your review before committing        │
│  this session's results.                                       │
│                                                                │
│  1 / 3                                                         │
│                                                                │
│  [00:24:11]  "It sort of reminded me of how my bank app works" │
│                                                                │
│  Proposed: CONFUSION_MENTAL_MODEL  (confidence 0.51)          │
│                                                                │
│  I'm uncertain — this could be a mental model mismatch,        │
│  or just an analogy. How do you read it?                      │
│                                                                │
│  [Confirm code]  [Change to...]  [Mark as noise]  [Skip]      │
│                                                                │
│  ── or type a response ────────────────────────────────────── │
│  > That's actually DELIGHT — they liked the familiarity       │
│                                                                │
│  Got it — coded as DELIGHT (confidence overridden by          │
│  researcher). Moving to item 2.                                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Actions:**
- Confirm proposed code
- Select alternative code from list
- Type a free-text correction (Claude interprets and applies)
- Mark as noise (no code)
- Skip (leave pending for later)
- Commit all reviewed codes and continue

**Human judgement moment:** The most important gate in the system. Nothing is written to StudyState until the researcher has reviewed flagged items.

---

### Stage 6 — Next Session Prep (Per Session)

**Interface type:** Conversational brief + structured summary

Shown after the human review gate is completed. Researcher reads this before their next interview.

```
┌────────────────────────────────────────────────────────────────┐
│  Session 4 Prep Brief                                          │
│                                                                │
│  ── Push harder ─────────────────────────────────────────      │
│  OB2 (avg depth 2.1/5 across 3 sessions)                      │
│  The probe "Did you look for help anywhere?" worked in         │
│  session 3 but wasn't used in 1 or 2. Use it.                  │
│                                                                │
│  ── Consistently skipped ────────────────────────────────      │
│  FD1 — skipped in all 3 sessions. Consider moving it           │
│  earlier in the guide before OB2 runs long.                    │
│                                                                │
│  ── Worth testing ───────────────────────────────────────      │
│  EMERGENT: export_pain has appeared in 3/3 sessions            │
│  but isn't in your codebook or guide. Probe for it             │
│  directly — try: "Tell me about a time you tried to get        │
│  information out of the product."                              │
│                                                                │
│  [Ask a question]          [Dismiss]  [Export as PDF]          │
└────────────────────────────────────────────────────────────────┘
```

**Actions:**
- Ask follow-up questions in natural language
- Dismiss / archive brief
- Export as PDF to take into the Askable session

---

### Stage 7 — Cross-Session Dashboard

**Interface type:** Structured views with conversational sidebar

Accessible at any point after session 2. Updates after each committed session.

**Screen: Heatmap**

```
┌───────────────────────────────────────────────────────────────┐
│  Theme Heatmap  ·  Sessions 1–5 of 8                         │
│                                                               │
│  Filter by: All themes ▼   All segments ▼                    │
│                                                               │
│                      P01  P02  P03  P04  P05                  │
│  CONFUSION_NAV        ██   ██   █    ██   ██                  │
│  CONFUSION_MM         ██   █    ██   —    █                   │
│  WORKAROUND_EXT       █    —    ██   █    —                   │
│  DELIGHT              —    █    —    —    █                   │
│  EXPORT_PAIN *        █    ██   —    ██   ██   ← emergent     │
│                                                               │
│  * Not yet in codebook                                        │
│                                                               │
│  [Add EXPORT_PAIN to codebook]  [Ask about this pattern]     │
└───────────────────────────────────────────────────────────────┘
```

Participant references are always IDs (P01, P02...) — never real names.

**Screen: Saturation**

```
┌───────────────────────────────────────────────────────────────┐
│  Saturation Tracker                                           │
│                                                               │
│  New themes per session                                       │
│  S1  ████████████  6 new                                      │
│  S2  ██████        3 new                                      │
│  S3  ████          2 new                                      │
│  S4  ██            1 new                                      │
│  S5  █             1 new                                      │
│                                                               │
│  ⚡  Rate is declining. If session 6 produces 0–1 new         │
│     themes, you may have reached saturation.                  │
│                                                               │
│  [Continue to session 6]   [Stop collecting, go to synthesis] │
└───────────────────────────────────────────────────────────────┘
```

**Actions:**
- Filter heatmap by theme, participant, session range
- Click any cell to see supporting (anonymised) quotes
- Accept saturation signal → transitions study to Synthesis phase
- Ask cross-session questions in conversational sidebar ("Which participants showed both CONFUSION_NAV and WORKAROUND_EXT?")

---

### Stage 8 — Codebook Curation

**Interface type:** Conversational panel

Runs every N sessions or on-demand.

```
┌────────────────────────────────────────────────────────────────┐
│  Codebook Review  ·  After session 5            4 items        │
│                                                                │
│  ── ADD ────────────────────────────────────────────────      │
│  EXPORT_PAIN — appeared in 4/5 sessions, high salience.       │
│  Suggested definition: "Participant expresses frustration      │
│  or friction when attempting to extract data or content        │
│  from the product."                                            │
│  [Accept]  [Edit definition]  [Reject]                        │
│                                                                │
│  ── SPLIT ──────────────────────────────────────────────      │
│  CONFUSION_NAV is being applied to two distinct patterns:      │
│  navigation layout confusion vs. information architecture.     │
│  Suggested: CONFUSION_NAV_LAYOUT + CONFUSION_NAV_IA           │
│  [Accept split]  [Keep as one]  [Discuss]                     │
│                                                                │
│  ── RETIRE ─────────────────────────────────────────────      │
│  DELIGHT — only 2/5 sessions, confidence consistently low.    │
│  Suggested: collapse into POSITIVE_MOMENT (broader).          │
│  [Accept]  [Keep]                                              │
└────────────────────────────────────────────────────────────────┘
```

**Actions:**
- Accept / reject each recommendation individually
- Edit suggested definitions inline before accepting
- Ask for reasoning in natural language
- Apply approved changes → bumps codebook to next version, change logged in history

---

### Stage 9 — Synthesis

**Interface type:** Structured list + conversational sidebar

**Screen: Insights**

```
┌────────────────────────────────────────────────────────────────┐
│  Candidate Insights                    Sort: Frequency ▼       │
│                                                                │
│  ── Insight 1 ────────────────────────────────────────────    │
│  Participants consistently find workarounds rather than        │
│  contacting support when stuck.                                │
│                                                                │
│  Evidence: 5/5 participants  ·  12 coded instances             │
│  Codes: WORKAROUND_SELF + WORKAROUND_EXT                       │
│  Salience: High  ·  Objective alignment: OB2 ✓                 │
│                                                                │
│  Supporting quotes (3 shown of 12)  [Expand]                  │
│  "I honestly just Googled it." — P01                          │
│  "I asked a colleague, I didn't think there was help          │
│   in the app." — P03                                          │
│                                                                │
│  [Accept]  [Edit statement]  [Reject]  [Merge with...]        │
└────────────────────────────────────────────────────────────────┘
```

All quotes attributed to participant IDs only.

**Actions:**
- Accept / edit / reject each insight
- Reorder accepted insights (drag)
- Merge two insights into one
- Ask cross-session questions ("Are there participants who bucked this pattern?")
- Promote accepted insights to report

---

### Stage 10 — Report

**Interface type:** Structured document view + export

```
┌────────────────────────────────────────────────────────────────┐
│  Research Report — Onboarding Feb 2026                        │
│                                                                │
│  KEY INSIGHTS                                                  │
│  1. Users default to self-service workarounds over in-product  │
│     help — indicating a trust deficit in the help system.      │
│     [Edit]                                                     │
│                                                                │
│  OBSERVATIONS                                                  │
│  - FD1 was consistently skipped — consider restructuring the   │
│    guide section order for future studies.                     │
│  - EXPORT_PAIN emerged in 4/5 sessions and was not in the      │
│    original brief — warrants a dedicated follow-up study.      │
│                                                                │
│  RECOMMENDATIONS  ...                                          │
│                                                                │
│  [Export PDF]  [Export DOCX]  [Export annotated transcript]   │
│  [Export codebook YAML]  [Export heatmap CSV]                  │
└────────────────────────────────────────────────────────────────┘
```

**Actions:**
- Edit any section inline
- Reorder insights
- Export in multiple formats (all exports use anonymised data)

---

### Navigation Structure

```
STUDIES
└── [Study name]
    ├── Brief
    ├── Guide             (locked after first session, versioned)
    ├── Codebook          (versioned — v1, v2...)
    ├── Sessions
    │   ├── Session 1     (upload → anonymise → analyse → review → prep)
    │   ├── Session 2
    │   └── ...
    ├── Cross-Session
    │   ├── Heatmap
    │   ├── Saturation
    │   └── Codebook Curation
    ├── Insights
    ├── Report
    └── Data & Privacy
```

---

### Key Human Judgement Moments

These are the gates that must be designed to feel trustworthy, not bureaucratic:

| Gate | Stage | What the researcher decides |
|---|---|---|
| Brief confirmation | Pre-research | Does this accurately represent my intent? |
| Guide lock | Pre-research | Am I happy to run interviews against this? |
| Codebook lock | Pre-research | Do my hypotheses map to these codes? |
| Anonymisation review | Per session | Is the PII detection correct before the original is discarded? |
| Per-session code review | Per session | Are these flagged codes correct? |
| Saturation decision | Cross-session | Do I have enough data to stop collecting? |
| Codebook curation | Cross-session | What changes does the evidence support? |
| Insight approval | Synthesis | Which of these statements do I stand behind? |

Every one of these should be conversational, not a form. The researcher should be able to explain their decision in plain language and have the system interpret it correctly.

---

## Privacy & Data Security

### Core Principles

These are design constraints, not features. They apply to every stage and every agent call:

- **Anonymise before AI sees anything** — the original transcript is never sent to an LLM. Only the anonymised version is processed.
- **No real names anywhere in the system** — participants are referenced by generated IDs only (P01, P02...).
- **Quotes propagate anonymised** — every quote in reviews, insights, and reports is already stripped of PII.
- **Original is transient** — the raw transcript is processed locally and discarded after the researcher confirms anonymisation. Only the anonymised version is stored.
- **Researcher holds the ID mapping** — the tool generates participant IDs but does not store the mapping between those IDs and real people. That mapping stays with the researcher.
- **Researcher controls retention** — explicit delete-study action purges all associated data.

---

### Anonymisation Pipeline

The upload flow is a strict two-step sequence. No AI analysis begins until the researcher has confirmed anonymisation:

```
Upload transcript
      │
      ▼
PII scan (local — before any AI call)
      │
      ▼
Anonymisation review ← HUMAN GATE
      │
      ▼
Discard original ← PERMANENT
      │
      ▼
AI analysis runs on anonymised text only
      │
      ▼
All downstream: quotes, insights, report — anonymised throughout
```

---

### Anonymisation Review Screen

```
┌─────────────────────────────────────────────────────────────────┐
│  Anonymisation review  ·  Session 3                             │
│                                                                 │
│  Found 14 items that may contain personal information.          │
│  Review each and confirm before analysis runs.                  │
│  The original file will be permanently discarded after this.    │
│                                                                 │
│  ── Auto-redacted (high confidence) ─────────────────────────   │
│  ✓  "My name is Sarah" → "My name is [PARTICIPANT]"            │
│  ✓  "sarah@example.com" → "[EMAIL]"                            │
│  ✓  [INTERVIEWER] applied to all researcher turns               │
│                                                                 │
│  ── Needs your decision (low confidence) ────────────────────   │
│                                                                 │
│  1 / 3                                                          │
│  "...my manager John kept asking about it..."                   │
│  Possible third-party name detected: "John"                     │
│                                                                 │
│  [Redact → "my manager [NAME]"]   [Keep as-is]                 │
│                                                                 │
│  ── Sensitive content flagged ───────────────────────────────   │
│  [00:34:22]  Participant disclosed a health condition.          │
│  This segment has been auto-excluded from coding.              │
│  [Review segment]  [Confirm exclusion]                         │
│                                                                 │
│  [Confirm all & discard original]                               │
└─────────────────────────────────────────────────────────────────┘
```

---

### PII Detection Table

| PII type | Replacement token | Default behaviour |
|---|---|---|
| Participant's name | `[PARTICIPANT]` | Auto-redact if high confidence |
| Interviewer's name | `[INTERVIEWER]` | Auto-redact always |
| Third-party names | `[NAME]` | Flag for researcher review |
| Email addresses | `[EMAIL]` | Auto-redact always |
| Phone numbers | `[PHONE]` | Auto-redact always |
| Company names | `[COMPANY]` | Flag for researcher review |
| Locations (city, suburb) | `[LOCATION]` | Flag for researcher review |
| Sensitive disclosures | Segment excluded | Flag for researcher review |

**Implementation:** Microsoft Presidio (`presidio-analyzer`) for PII detection, run locally before any network call. High-confidence detections (score > 0.85) are auto-redacted; lower-confidence are surfaced for researcher review.

---

### Data Storage Model

```
┌───────────────────────────────────────────────────────────────────┐
│  STORED                               NOT STORED                  │
│                                                                   │
│  ✓ Anonymised transcript              ✗ Original transcript        │
│  ✓ Participant IDs (P01, P02...)       ✗ Participant real names    │
│  ✓ Codes applied to turns             ✗ Askable profile data       │
│  ✓ Anonymised quotes                  ✗ Sensitive disclosures      │
│  ✓ Codebook + guide (versioned)       ✗ Recruiter/screener data    │
│  ✓ Insights + report                  ✗ ID-to-name mapping         │
└───────────────────────────────────────────────────────────────────┘
```

---

### StudyState — Privacy-Relevant Fields

The `sessions` entry in StudyState stores only the anonymised transcript. The original file path is never persisted:

```yaml
sessions:
  - session_id: str
    participant_id: str          # e.g. "P03" — not a real name
    transcript: Turn[]           # anonymised turns only — original discarded
    anonymisation_log:           # audit record of what was redacted
      auto_redacted: int         # count of auto-redactions
      researcher_reviewed: int   # count of items reviewed by researcher
      exclusions: int            # segments excluded (sensitive disclosures)
    coverage_result: QuestionCoverageResult[]
    coded_turns: CodedTurn[]
    emergent_themes: EmergentTheme[]
    quality_scorecard: SessionScorecard
    review_status: pending | approved | rejected
```

---

### Data & Privacy Settings Screen

Accessible from the study navigation under **Data & Privacy**:

```
┌───────────────────────────────────────────────────────────────┐
│  Data & Privacy  ·  Onboarding Feb 2026                       │
│                                                               │
│  Stored data                                                  │
│  5 anonymised transcripts  ·  1 codebook  ·  12 insights      │
│  Original transcripts: not stored                             │
│                                                               │
│  Participant ID mapping                                       │
│  You hold the mapping between IDs and real participants.      │
│  This tool does not store or have access to that mapping.     │
│                                                               │
│  Retention                                                    │
│  Auto-delete study data after:  [6 months ▼]                  │
│                                                               │
│  ───────────────────────────────────────────────────────      │
│                                                               │
│  [Delete all study data]                                      │
│  This permanently removes all transcripts, codes, insights,   │
│  and report data. This cannot be undone.                      │
└───────────────────────────────────────────────────────────────┘
```

---

### Researcher-Facing Language

Avoid legalistic privacy copy. Use plain, honest language throughout:

| Instead of | Use |
|---|---|
| "We process your data in accordance with..." | "We anonymise before analysis. Originals are discarded." |
| "Consent confirmed" | "Participants were informed this interview may be AI-analysed" |
| "PII detected" | "Found information that could identify someone" |
| "GDPR compliant" | "Real names are never stored in this tool" |

A persistent indicator appears throughout the app wherever quotes or participant data are shown:

```
  🔒  All quotes anonymised  ·  Original transcripts not stored
```

---



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
