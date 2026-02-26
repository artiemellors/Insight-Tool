"""Interview guide loader — YAML and JSON."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from app.models.core import GuideQuestion, GuideSection, InterviewGuide


def load_interview_guide(file_path: str | Path) -> InterviewGuide:
    """Load an interview guide from a YAML or JSON file.

    Expected structure (YAML example):

        sections:
          - name: Core Questions
            questions:
              - id: OB1
                text: "Walk me through your first login"
                required: true
                mapped_objective: "Objective 1"
                probes:
                  - "What did you expect to see?"
                  - "Were you surprised by anything?"
    """
    file_path = Path(file_path)
    raw = _load_file(file_path)

    sections = []
    for section_data in raw.get("sections", []):
        questions = []
        for q in section_data.get("questions", []):
            questions.append(GuideQuestion(
                id=q["id"],
                text=q["text"],
                section=section_data["name"],
                required=q.get("required", True),
                mapped_objective=q.get("mapped_objective"),
                probes=q.get("probes", []),
            ))
        sections.append(GuideSection(
            name=section_data["name"],
            questions=questions,
        ))

    return InterviewGuide(
        sections=sections,
        version=raw.get("version", 1),
        locked=raw.get("locked", False),
    )


def _load_file(file_path: Path) -> dict:
    """Load YAML or JSON file based on extension."""
    suffix = file_path.suffix.lower()
    content = file_path.read_text(encoding="utf-8")

    if suffix in (".yaml", ".yml"):
        return yaml.safe_load(content)
    elif suffix == ".json":
        return json.loads(content)
    else:
        # Try YAML first, fall back to JSON
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError:
            return json.loads(content)
