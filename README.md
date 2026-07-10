# Evaluating Agents v0

**Failure-mode evaluation for skill-learning agents across simulated worlds and tutoring.**

## Research question

> When do agentic AI systems fail on long-horizon skill tasks, and are failure
> modes consistent across domains — executing skills in a simulated world
> (Crafter) vs. teaching skills to humans (Python tutoring)?

## Status

Pre-PhD pilot (Jul–Aug 2026). Week 1: setup + baseline runs.

## Structure

```
tasks/       task definitions (tutoring JSONL, Crafter seed list)
src/         run scripts + LLM judge
runs/        raw episode / interaction logs (JSONL, CSV)
analysis/    failure tables, judge-agreement analysis, charts code
outputs/     tech note, charts, year-1 plan, decision
```

## Reproduce

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...   # or OPENAI_API_KEY
python src/run_crafter.py --model claude-haiku --seeds tasks/crafter_seeds.txt --episodes 1
```

## Failure taxonomy

See [failure_taxonomy.md](failure_taxonomy.md) — 7 labels shared across both domains.

## Known limitations

v0 pilot: small n, LLM-judge scores validated on a 15-response human slice only,
single tutoring domain (beginner Python), no human students involved.
