"""Evaluating Agents v0 — tutoring eval runner (Week 4).

Runs tutoring tasks (tasks/tutoring_python.jsonl) through a tutor model under
one of two prompt conditions, then scores each reply with the LLM judge.

Usage:
    python src/run_tutoring.py --model claude-3-5-haiku-latest --condition direct
    python src/run_tutoring.py --model claude-3-5-haiku-latest --condition diagnose_first
"""

import argparse
import json
from pathlib import Path

from judge import score_response

CONDITIONS = {
    "direct": "You are a helpful Python tutor. Help the student.",
    "diagnose_first": (
        "You are a Python tutor. FIRST silently diagnose what the student "
        "misunderstands. THEN respond with one guiding question before any "
        "explanation. Never give the full corrected code in your first reply."
    ),
}


def tutor_reply(model: str, system: str, task: dict) -> str:
    user_msg = task["student_message"]
    if task.get("code"):
        user_msg += "\n\n```python\n" + task["code"] + "\n```"
    if model.startswith("claude"):
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=model, max_tokens=400, system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        return resp.content[0].text
    else:
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model=model, max_tokens=400,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user_msg}],
        )
        return resp.choices[0].message.content


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--condition", choices=list(CONDITIONS), required=True)
    ap.add_argument("--tasks", default="tasks/tutoring_python.jsonl")
    ap.add_argument("--judge-model", default="claude-3-5-haiku-latest")
    args = ap.parse_args()

    outdir = Path("runs/tutoring")
    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / f"{args.model.replace('/', '_')}_{args.condition}.jsonl"

    tasks = [json.loads(l) for l in Path(args.tasks).read_text().splitlines() if l.strip()]
    with open(out_path, "w") as f:
        for task in tasks:
            reply = tutor_reply(args.model, CONDITIONS[args.condition], task)
            scores = score_response(args.judge_model, task, reply)
            row = {
                "task_id": task["id"], "condition": args.condition,
                "model": args.model, "response": reply, "scores": scores,
            }
            f.write(json.dumps(row) + "\n")
            print(task["id"], scores.get("failure_label"), scores)


if __name__ == "__main__":
    main()
