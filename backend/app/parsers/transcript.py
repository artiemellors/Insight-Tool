"""Multi-format transcript parser.

Supports VTT, SRT, TXT, JSON, and Markdown transcript files.
All formats are normalised to a list of Turn objects.
"""

from __future__ import annotations

import json
import re
from enum import Enum
from pathlib import Path
from typing import Optional

from app.models.core import Turn


class TranscriptFormat(str, Enum):
    VTT = "vtt"
    SRT = "srt"
    TXT = "txt"
    JSON = "json"
    MD = "md"


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------

def detect_format(file_path: str | Path) -> TranscriptFormat:
    """Detect transcript format from file extension."""
    suffix = Path(file_path).suffix.lower()
    mapping = {
        ".vtt": TranscriptFormat.VTT,
        ".srt": TranscriptFormat.SRT,
        ".txt": TranscriptFormat.TXT,
        ".json": TranscriptFormat.JSON,
        ".md": TranscriptFormat.MD,
    }
    fmt = mapping.get(suffix)
    if fmt is None:
        raise ValueError(f"Unsupported transcript format: {suffix}")
    return fmt


# ---------------------------------------------------------------------------
# Parsers per format
# ---------------------------------------------------------------------------

def _parse_vtt(file_path: Path) -> list[Turn]:
    """Parse a WebVTT file into turns."""
    import webvtt

    turns: list[Turn] = []
    raw_cues = list(webvtt.read(str(file_path)))

    for i, cue in enumerate(raw_cues):
        speaker, text = _split_speaker(cue.text)
        turns.append(Turn(
            turn_index=i,
            speaker=speaker or "Unknown",
            text=text.strip(),
            start=_timestamp_to_seconds(cue.start),
            end=_timestamp_to_seconds(cue.end),
        ))

    return _merge_consecutive_speaker_turns(turns)


def _parse_srt(file_path: Path) -> list[Turn]:
    """Parse an SRT file into turns."""
    content = file_path.read_text(encoding="utf-8")
    blocks = re.split(r"\n\n+", content.strip())

    turns: list[Turn] = []
    for i, block in enumerate(blocks):
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        # Line 0: sequence number
        # Line 1: timestamps
        # Lines 2+: text
        timestamp_line = lines[1]
        text_lines = " ".join(lines[2:])

        start_str, end_str = timestamp_line.split(" --> ")
        speaker, text = _split_speaker(text_lines)

        turns.append(Turn(
            turn_index=i,
            speaker=speaker or "Unknown",
            text=text.strip(),
            start=_timestamp_to_seconds(start_str.strip()),
            end=_timestamp_to_seconds(end_str.strip()),
        ))

    return _merge_consecutive_speaker_turns(turns)


def _parse_txt(file_path: Path) -> list[Turn]:
    """Parse a plain text transcript. Expects 'Speaker: text' lines."""
    content = file_path.read_text(encoding="utf-8")
    turns: list[Turn] = []
    idx = 0

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        speaker, text = _split_speaker(line)
        turns.append(Turn(
            turn_index=idx,
            speaker=speaker or "Unknown",
            text=text.strip(),
        ))
        idx += 1

    return _merge_consecutive_speaker_turns(turns)


def _parse_json(file_path: Path) -> list[Turn]:
    """Parse a JSON transcript.

    Expects either:
    - A list of objects with 'speaker'/'text' (and optional 'start'/'end')
    - A Rev.ai-style 'monologues' structure
    """
    data = json.loads(file_path.read_text(encoding="utf-8"))

    # Rev.ai style: {"monologues": [{"speaker": 0, "elements": [...]}]}
    if isinstance(data, dict) and "monologues" in data:
        return _parse_revai_json(data)

    # Simple list of turn objects
    if isinstance(data, list):
        turns = []
        for i, item in enumerate(data):
            turns.append(Turn(
                turn_index=i,
                speaker=str(item.get("speaker", "Unknown")),
                text=item.get("text", ""),
                start=item.get("start"),
                end=item.get("end"),
            ))
        return _merge_consecutive_speaker_turns(turns)

    raise ValueError("Unsupported JSON transcript structure")


# ---------------------------------------------------------------------------
# Markdown parser
# ---------------------------------------------------------------------------

_MD_SPEAKER_BOLD = re.compile(
    r"^\*\*(.+?)(?::\*\*|\*\*\s*:)\s*(.+)", re.DOTALL
)
_MD_SPEAKER_HEADING = re.compile(
    r"^#{1,6}\s+(.+?)\s*:\s*(.+)", re.DOTALL
)
_MD_TIMESTAMP = re.compile(
    r"\[(\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?)\]"
)


def _parse_md(file_path: Path) -> list[Turn]:
    """Parse a Markdown transcript into turns.

    Supports common markdown transcript conventions:
    - **Speaker Name:** text
    - ## Speaker Name: text
    - Optional [MM:SS] or [HH:MM:SS] timestamps anywhere in the line
    - Continuation lines (non-speaker lines) are appended to the previous turn
    """
    content = file_path.read_text(encoding="utf-8")
    turns: list[Turn] = []
    idx = 0

    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue

        # Skip metadata-only header lines (e.g. "# Interview Transcript")
        if re.match(r"^#{1,6}\s+\w", stripped) and ":" not in stripped:
            continue

        # Try bold speaker pattern: **Speaker:** text
        m = _MD_SPEAKER_BOLD.match(stripped)
        if not m:
            # Try heading speaker pattern: ## Speaker: text
            m = _MD_SPEAKER_HEADING.match(stripped)

        if m:
            speaker = m.group(1).strip()
            text = m.group(2).strip()

            # Extract optional timestamp from text
            start_seconds = None
            ts_match = _MD_TIMESTAMP.search(text)
            if ts_match:
                start_seconds = _timestamp_to_seconds(ts_match.group(1))
                text = text[:ts_match.start()].strip() + " " + text[ts_match.end():].strip()
                text = text.strip()

            turns.append(Turn(
                turn_index=idx,
                speaker=speaker,
                text=text,
                start=start_seconds,
            ))
            idx += 1
        elif turns:
            # Continuation line — append to previous turn
            extra = stripped
            ts_match = _MD_TIMESTAMP.search(extra)
            if ts_match:
                extra = extra[:ts_match.start()].strip() + " " + extra[ts_match.end():].strip()
                extra = extra.strip()
            if extra:
                prev = turns[-1]
                turns[-1] = Turn(
                    turn_index=prev.turn_index,
                    speaker=prev.speaker,
                    text=f"{prev.text} {extra}",
                    start=prev.start,
                    end=prev.end,
                    is_interviewer=prev.is_interviewer,
                )

    return _merge_consecutive_speaker_turns(turns)


def _parse_revai_json(data: dict) -> list[Turn]:
    """Parse Rev.ai monologue-style JSON."""
    turns: list[Turn] = []
    idx = 0
    for mono in data["monologues"]:
        speaker = f"Speaker {mono.get('speaker', idx)}"
        text_parts = []
        start_ts: Optional[float] = None
        end_ts: Optional[float] = None

        for elem in mono.get("elements", []):
            if elem.get("type") == "text":
                text_parts.append(elem.get("value", ""))
                if start_ts is None and "ts" in elem:
                    start_ts = elem["ts"]
                if "end_ts" in elem:
                    end_ts = elem["end_ts"]
            elif elem.get("type") == "punct":
                text_parts.append(elem.get("value", ""))

        turns.append(Turn(
            turn_index=idx,
            speaker=speaker,
            text="".join(text_parts).strip(),
            start=start_ts,
            end=end_ts,
        ))
        idx += 1

    return _merge_consecutive_speaker_turns(turns)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SPEAKER_PATTERN = re.compile(
    r"^(?:<v\s+)?([^>:]+?)(?:>|:\s)", re.IGNORECASE
)


def _split_speaker(text: str) -> tuple[Optional[str], str]:
    """Extract speaker name from the start of a line.

    Handles formats like:
    - "Speaker Name: text"
    - "<v Speaker Name>text" (VTT voice spans)
    """
    m = _SPEAKER_PATTERN.match(text)
    if m:
        speaker = m.group(1).strip()
        rest = text[m.end():].strip()
        return speaker, rest
    return None, text


def _timestamp_to_seconds(ts: str) -> float:
    """Convert HH:MM:SS.mmm or MM:SS.mmm to seconds."""
    ts = ts.replace(",", ".")  # SRT uses comma
    parts = ts.strip().split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return float(ts)


def _merge_consecutive_speaker_turns(turns: list[Turn]) -> list[Turn]:
    """Merge consecutive turns from the same speaker into a single turn."""
    if not turns:
        return turns

    merged: list[Turn] = [turns[0]]
    for turn in turns[1:]:
        prev = merged[-1]
        if turn.speaker == prev.speaker:
            merged[-1] = Turn(
                turn_index=prev.turn_index,
                speaker=prev.speaker,
                text=f"{prev.text} {turn.text}",
                start=prev.start,
                end=turn.end,
                is_interviewer=prev.is_interviewer,
            )
        else:
            merged.append(turn.model_copy(update={"turn_index": len(merged)}))

    return merged


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_PARSER_MAP = {
    TranscriptFormat.VTT: _parse_vtt,
    TranscriptFormat.SRT: _parse_srt,
    TranscriptFormat.TXT: _parse_txt,
    TranscriptFormat.JSON: _parse_json,
    TranscriptFormat.MD: _parse_md,
}


def parse_transcript(
    file_path: str | Path,
    fmt: TranscriptFormat | None = None,
    interviewer_name: str | None = None,
) -> list[Turn]:
    """Parse a transcript file into canonical Turn objects.

    Args:
        file_path: Path to the transcript file.
        fmt: Explicit format override. Auto-detected from extension if None.
        interviewer_name: If provided, turns from this speaker are marked as interviewer.

    Returns:
        List of Turn objects in chronological order.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Transcript file not found: {file_path}")

    if fmt is None:
        fmt = detect_format(file_path)

    parser = _PARSER_MAP.get(fmt)
    if parser is None:
        raise ValueError(f"No parser registered for format: {fmt}")

    turns = parser(file_path)

    # Tag interviewer turns
    if interviewer_name:
        name_lower = interviewer_name.lower()
        for turn in turns:
            if turn.speaker.lower() == name_lower:
                turn.is_interviewer = True

    return turns
