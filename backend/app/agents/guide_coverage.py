"""Guide Coverage Agent.

Analyses a transcript against the interview guide to determine:
- Which questions were covered
- Depth score per question (1-5)
- Which questions were skipped
- Supporting turn indices for each covered question
"""

from __future__ import annotations

import json

import anthropic

from app.models.core import InterviewGuide, QuestionCoverageResult, Turn

SYSTEM_PROMPT = """\
You are a qualitative research analysis agent. Your task is to analyse an \
interview transcript against an interview guide and determine which guide \
questions were covered during the interview.

For each question in the guide, determine:
1. Whether the question was covered (directly asked or organically addressed)
2. A depth score from 1-5:
   - 1: Mentioned but no substance
   - 2: Brief answer, no elaboration
   - 3: Moderate detail, some specifics
   - 4: Rich detail with specific examples or stories
   - 5: Deep, nuanced response with emotional resonance and actionable detail
3. Which transcript turns support that assessment

Be conservative with depth scores. A question is "covered" only if the \
participant provided a substantive response — the interviewer merely asking \
it does not count.

Respond with valid JSON only — no markdown fencing, no commentary.\
"""


class GuideCoverageAgent:
    """Analyses transcript coverage against the interview guide."""

    def __init__(self, client: anthropic.Anthropic | None = None):
        self.client = client or anthropic.Anthropic()

    async def analyse(
        self,
        turns: list[Turn],
        guide: InterviewGuide,
    ) -> list[QuestionCoverageResult]:
        """Run guide coverage analysis.

        Args:
            turns: Parsed transcript turns.
            guide: The interview guide to check coverage against.

        Returns:
            A QuestionCoverageResult for each guide question.
        """
        questions_json = [
            {
                "id": q.id,
                "text": q.text,
                "section": q.section,
                "probes": q.probes,
            }
            for q in guide.all_questions
        ]

        transcript_json = [
            {
                "turn_index": t.turn_index,
                "speaker": t.speaker,
                "text": t.text,
                "is_interviewer": t.is_interviewer,
            }
            for t in turns
        ]

        user_prompt = (
            f"## Interview Guide Questions\n\n"
            f"{json.dumps(questions_json, indent=2)}\n\n"
            f"## Transcript\n\n"
            f"{json.dumps(transcript_json, indent=2)}\n\n"
            f"## Task\n\n"
            f"For each guide question, output a JSON array of objects with:\n"
            f'- "question_id": the question ID\n'
            f'- "covered": boolean\n'
            f'- "depth_score": integer 1-5 (null if not covered)\n'
            f'- "supporting_turn_indices": list of turn indices\n'
            f'- "notes": brief explanation of your assessment\n\n'
            f"Respond with the JSON array only."
        )

        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw = message.content[0].text
        parsed = json.loads(raw)

        results = []
        for item in parsed:
            results.append(QuestionCoverageResult(
                question_id=item["question_id"],
                covered=item["covered"],
                depth_score=item.get("depth_score"),
                supporting_turn_indices=item.get("supporting_turn_indices", []),
                notes=item.get("notes"),
            ))

        return results
