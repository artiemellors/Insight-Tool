"""Codebook loader — YAML and JSON."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from app.models.core import Code, CodeType, Codebook, Theme


def load_codebook(file_path: str | Path) -> Codebook:
    """Load a codebook from a YAML or JSON file.

    Expected structure (YAML example):

        themes:
          - name: Navigation Confusion
            codes:
              - id: CONFUSION_NAV
                definition: "Participant expresses difficulty locating a UI element"
                indicators:
                  - "couldn't find"
                  - "kept clicking"
                code_type: deductive
                example_quotes:
                  - "I just kept clicking different tabs"
    """
    file_path = Path(file_path)
    raw = _load_file(file_path)

    themes = []
    for theme_data in raw.get("themes", []):
        codes = []
        for c in theme_data.get("codes", []):
            codes.append(Code(
                id=c["id"],
                definition=c["definition"],
                indicators=c.get("indicators", []),
                example_quotes=c.get("example_quotes", []),
                code_type=CodeType(c.get("code_type", "deductive")),
            ))
        themes.append(Theme(
            name=theme_data["name"],
            codes=codes,
        ))

    return Codebook(
        themes=themes,
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
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError:
            return json.loads(content)
