"""Deductive Coder Agent.

Applies codebook codes to transcript turns. For each turn, determines which
codes apply, with a confidence score and evidence quote.

Uses temperature=0 for deterministic, reproducible coding.
"""

from __future__ import annotations

import json

import anthropic

from app.models.core import Codebook, CodedTurn, Turn

SYSTEM_PROMPT = """\
You are a qualitative research coding agent. Your task is to apply a \
predefined codebook to interview transcript turns.

For each transcript turn, determine which codes from the codebook apply. \
A code applies when the turn contains language or meaning that matches the \
code's definition and indicators.

Rules:
- Only apply codes where there is clear evidence in the text.
- A single turn can have multiple codes applied.
- Provide a confidence score (0.0 to 1.0) for each applied code.
- Extract the specific phrase from the turn that supports the code as evidence.
- Flag any code with confidence below 0.6 as needs_review=true.
- If no codes apply to a turn, omit it from the output.
- Do NOT invent new codes. Only use codes from the provided codebook.

Respond with valid JSON only — no markdown fencing, no commentary.\
"""


class DeductiveCoderAgent:
    """Applies codebook codes to transcript turns."""

    def __init__(self, client: anthropic.Anthropic | None = None):
        self.client = client or anthropic.Anthropic()

    async def code_turns(
        self,
        turns: list[Turn],
        codebook: Codebook,
    ) -> list[CodedTurn]:
        """Apply deductive codes to transcript turns.

        Args:
            turns: Parsed transcript turns (participant turns only recommended).
            codebook: The codebook to apply.

        Returns:
            List of CodedTurn objects for turns where codes were applied.
        """
        codebook_json = [
            {
                "id": code.id,
                "definition": code.definition,
                "indicators": code.indicators,
                "example_quotes": code.example_quotes,
            }
            for code in codebook.all_codes
        ]

        # Only send participant turns (skip interviewer turns)
        participant_turns = [
            {
                "turn_index": t.turn_index,
                "speaker": t.speaker,
                "text": t.text,
            }
            for t in turns
            if not t.is_interviewer
        ]

        user_prompt = (
            f"## Codebook\n\n"
            f"{json.dumps(codebook_json, indent=2)}\n\n"
            f"## Transcript Turns\n\n"
            f"{json.dumps(participant_turns, indent=2)}\n\n"
            f"## Task\n\n"
            f"For each turn where one or more codes apply, output a JSON array "
            f"of objects with:\n"
            f'- "turn_index": the turn index\n'
            f'- "code_id": the code ID from the codebook\n'
            f'- "confidence": float 0.0-1.0\n'
            f'- "evidence_quote": the specific phrase that supports the code\n'
            f'- "needs_review": true if confidence < 0.6\n\n'
            f"Respond with the JSON array only."
        )

        # Process in batches if the transcript is long
        all_coded: list[CodedTurn] = []
        batch_size = 50
        for i in range(0, len(participant_turns), batch_size):
            batch = participant_turns[i : i + batch_size]
            batch_prompt = (
                f"## Codebook\n\n"
                f"{json.dumps(codebook_json, indent=2)}\n\n"
                f"## Transcript Turns\n\n"
                f"{json.dumps(batch, indent=2)}\n\n"
                f"## Task\n\n"
                f"For each turn where one or more codes apply, output a JSON array "
                f"of objects with:\n"
                f'- "turn_index": the turn index\n'
                f'- "code_id": the code ID from the codebook\n'
                f'- "confidence": float 0.0-1.0\n'
                f'- "evidence_quote": the specific phrase that supports the code\n'
                f'- "needs_review": true if confidence < 0.6\n\n'
                f"If no codes apply to any turn in this batch, respond with [].\n\n"
                f"Respond with the JSON array only."
            )

            message = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                temperature=0,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": batch_prompt}],
            )

            raw = message.content[0].text
            parsed = json.loads(raw)

            for item in parsed:
                all_coded.append(CodedTurn(
                    turn_index=item["turn_index"],
                    code_id=item["code_id"],
                    confidence=item["confidence"],
                    evidence_quote=item["evidence_quote"],
                    needs_review=item.get("needs_review", item["confidence"] < 0.6),
                ))

        return all_coded
