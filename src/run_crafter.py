"""Evaluating Agents v0 — Crafter LLM-agent runner.

Deliberately dumb loop: text observation -> LLM picks one action -> env steps -> log.
No memory modules, no reflection frameworks. The point is to watch it fail.

Usage:
    python src/run_crafter.py --model claude-3-5-haiku-latest --seeds tasks/crafter_seeds.txt --episodes 5
    python src/run_crafter.py --model gpt-4o-mini --seeds tasks/crafter_seeds.txt --episodes 5

Output: one JSONL per episode in runs/crafter/, plus a summary row appended
to runs/crafter/failure_log.csv (failure_bucket + diagnosis filled by hand).
"""

import argparse
import csv
import json
import os
import time
from pathlib import Path

import crafter  # noqa: F401  (registers env)
import gymnasium as gym
import numpy as np

ACTIONS = [
    "noop", "move_left", "move_right", "move_up", "move_down", "do",
    "sleep", "place_stone", "place_table", "place_furnace", "place_plant",
    "make_wood_pickaxe", "make_stone_pickaxe", "make_iron_pickaxe",
    "make_wood_sword", "make_stone_sword", "make_iron_sword",
]

SYSTEM_PROMPT = f"""You are playing Crafter, a 2D survival game.
Each turn you receive a text description of your surroundings, inventory, and status.
Choose exactly ONE action from this list and reply with ONLY the action name:
{", ".join(ACTIONS)}

Goal: survive and unlock achievements (collect wood, place table, make tools,
collect stone/coal/iron, eat, drink, defeat zombies, etc.). Think about
prerequisites: e.g. you need wood before a table, a table before a pickaxe."""


def describe(obs_info: dict) -> str:
    """Cheap text rendering of Crafter's semantic state (from info dict)."""
    inv = {k: v for k, v in obs_info.get("inventory", {}).items() if v > 0}
    ach = [k for k, v in obs_info.get("achievements", {}).items() if v > 0]
    return (
        f"Inventory: {inv or 'empty'}. "
        f"Achievements so far: {ach or 'none'}. "
        f"(Semantic view not rendered in v0 — rely on inventory/achievements and explore.)"
    )


def llm_action(model: str, history: list[dict], observation: str) -> str:
    """Route to Anthropic or OpenAI based on model name; return raw text."""
    messages = history + [{"role": "user", "content": observation}]
    if model.startswith("claude"):
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=model, max_tokens=20, system=SYSTEM_PROMPT, messages=messages
        )
        return resp.content[0].text.strip().lower()
    else:
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model=model,
            max_tokens=20,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        )
        return resp.choices[0].message.content.strip().lower()


def run_episode(model: str, seed: int, max_steps: int, outdir: Path) -> dict:
    env = gym.make("CrafterReward-v1") if "CrafterReward-v1" in gym.registry else crafter.Env(seed=seed)
    is_gym = hasattr(env, "reset") and not isinstance(env, crafter.Env)
    if isinstance(env, crafter.Env):
        obs = env.reset()
        info = {"inventory": {}, "achievements": {}}
    else:
        obs, info = env.reset(seed=seed)

    log_path = outdir / f"ep_{model.replace('/', '_')}_{seed}_{int(time.time())}.jsonl"
    history: list[dict] = []
    invalid = 0
    last_actions: list[str] = []
    loop_detected = False
    total_reward = 0.0

    with open(log_path, "w") as f:
        for step in range(max_steps):
            observation = f"Step {step}. " + describe(info)
            raw = llm_action(model, history[-8:], observation)  # last 4 turns of context
            action_name = raw if raw in ACTIONS else "noop"
            if raw not in ACTIONS:
                invalid += 1
            idx = ACTIONS.index(action_name)

            if isinstance(env, crafter.Env):
                obs, reward, done, info = env.step(idx)
            else:
                obs, reward, terminated, truncated, info = env.step(idx)
                done = terminated or truncated
            total_reward += float(reward)

            last_actions.append(action_name)
            if len(last_actions) >= 8 and len(set(last_actions[-8:])) <= 2:
                loop_detected = True

            f.write(json.dumps({
                "step": step, "observation": observation, "llm_raw": raw,
                "action": action_name, "valid": raw in ACTIONS,
                "reward": float(reward),
            }) + "\n")

            history += [
                {"role": "user", "content": observation},
                {"role": "assistant", "content": action_name},
            ]
            if done:
                break

    achievements = sum(1 for v in info.get("achievements", {}).values() if v > 0)
    summary = {
        "episode_file": log_path.name, "seed": seed, "model": model,
        "steps": step + 1, "achievements": achievements,
        "final_status": "done" if done else "timeout",
        "invalid_actions": invalid, "loop_detected": loop_detected,
        "total_reward": total_reward,
    }
    with open(log_path, "a") as f:
        f.write(json.dumps({"type": "summary", **summary}) + "\n")
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--seeds", default="tasks/crafter_seeds.txt")
    ap.add_argument("--episodes", type=int, default=5)
    ap.add_argument("--max-steps", type=int, default=200)
    args = ap.parse_args()

    outdir = Path("runs/crafter")
    outdir.mkdir(parents=True, exist_ok=True)
    seeds = [int(s) for s in Path(args.seeds).read_text().split()][: args.episodes]

    csv_path = outdir / "failure_log.csv"
    new_file = not csv_path.exists()
    with open(csv_path, "a", newline="") as cf:
        writer = csv.writer(cf)
        if new_file:
            writer.writerow([
                "episode_id", "seed", "model", "steps", "achievements",
                "final_status", "invalid_actions", "loop_detected",
                "first_failure_step", "failure_bucket", "recovered_yes_no",
                "one_line_diagnosis",
            ])
        for seed in seeds:
            s = run_episode(args.model, seed, args.max_steps, outdir)
            print(f"seed={seed} steps={s['steps']} achievements={s['achievements']} "
                  f"invalid={s['invalid_actions']} loop={s['loop_detected']}")
            writer.writerow([
                s["episode_file"], seed, args.model, s["steps"], s["achievements"],
                s["final_status"], s["invalid_actions"], s["loop_detected"],
                "", "", "", "",  # filled by hand after reading the trace
            ])


if __name__ == "__main__":
    main()
