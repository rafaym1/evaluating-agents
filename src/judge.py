"""Evaluating Agents v0 — LLM judge for tutoring replies.

WARNING (project rule): judge scores are provisional until validated against
the 15-response human-scored slice (analysis/judge_agreement.md). Our prior
work says LLM-as-proxy is reliable for surface accuracy but can mislead on
deeper judgments — diagnosis_accuracy is exactly such a judgment.
"""

import json

FAILURE_LABELS = (
    "INVALID_OR_HALLUCINATED_ACTION|REPETITION_LOOP|MEMORY_OR_STATE_FAILURE|"
    "BAD_PLAN_OR_SUBGOAL_ORDER|POOR_RECOVERY|FAKE_COMPETENCE|NO_TRANSFER|NONE"
)

JUDGE_PROMPT = """You are grading an AI tutor's reply to a student.

Task metadata (includes the hidden misconception the tutor should diagnose):
{task_json}

Tutor reply:
{response}

Return STRICT JSON only, no prose, no markdown fences:
{{
 "diagnosis_accuracy": 0 or 1 or 2,
 "hint_quality": 0 or 1 or 2,
 "gave_answer_too_early": true or false,
 "adapted_to_student": 0 or 1 or 2,
 "hallucinated": true or false,
 "failure_label": "one of: %s"
}}

Scoring guide:
- diagnosis_accuracy: 2 = explicitly identified the hidden misconception,
  1 = partially/implicitly, 0 = missed it.
- hint_quality: 2 = one clear guiding question, 1 = vague nudge, 0 = none or confusing.
- gave_answer_too_early: true if the full corrected answer/code appears in this first reply.
- adapted_to_student: 2 = engages the student's actual words/code, 0 = generic lecture.
- hallucinated: true if ANY claim about Python in the reply is false.
- failure_label: dominant failure, or NONE if the reply is good.
""" % FAILURE_LABELS


def score_response(judge_model: str, task: dict, response: str) -> dict:
    prompt = JUDGE_PROMPT.format(
        task_json=json.dumps(task, indent=2), response=response
    )
    if judge_model.startswith("claude"):
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=judge_model, max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text
    else:
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model=judge_model, max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.choices[0].message.content

    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"parse_error": True, "raw": raw}
