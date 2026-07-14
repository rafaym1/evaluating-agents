# Reading & Research Notes
Tasks: (one sentence — what job did the AI agent have to do in this paper? e.g. 'act as a customer service agent handling airline
booking changes')
Failure definition/metric: (one sentence — how did the authors decide the AI succeeded or failed? What number did they
measure?)
Weakness I can exploit: (one sentence — what did they NOT test, or test poorly, that you could add or do better in your own
project?)

## Paper Notes

### τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains

**Tasks:** The AI agent acted as an airline customer service representative. It interacted with database API tools to complete tasks given by an LM-simulated user.

**Failure definition/metric:** A binary, rule-based reward system.
- **Action/Database State:** The final state of the database at the end of the conversation must perfectly match a unique, pre-defined ground-truth outcome.
- **Output Information:** The agent's text responses to the user must contain all necessary information, which is verified by checking for required substrings.

For numbers, they used a metric called pass^k, as well as the baseline average success rate, pass^1. GPT-4o achieved a pass^1 (success rate) of approximately 61% in the retail domain and 35% in the airline domain. When measuring consistency over multiple interactions, they found that the pass^8 score for GPT-4o dropped to less than 25% in the retail domain, quantifying how inconsistently current agents follow rules and handle user stochasticity.

**Weakness I can exploit:**
1. Agents should have long-horizon information tracking and memory.
2. Could add a process-level judge (rule-based or LLM-judge) that scores policy adherence independent of final-state correctness.
3. τ-bench's entire evaluation rests on the assumption that an LM (gpt-4-0613) simulating a human user is a faithful proxy for real user behavior, but they never test this. There is no human study comparing simulated vs. real user utterances, and no measure of whether the simulated user's information-revealing behavior (when it discloses preferences, how it phrases ambiguity, when it gets impatient) resembles that of real customers.

### GAIA: A Benchmark for General AI Assistants

**Tasks:** The AI agents acted as general assistants that help with questions involving reasoning, multi-modality handling, web browsing, and general tool-use proficiency.

**Failure definition/metric:** Evaluation is done via quasi-exact match between a model's answer and the ground truth.

**Weakness I can exploit:**
1. Combine human and model-based evaluation.
2. GAIA runs each model 3 times when an API is available and reports an average, but it never reports variance and never checks whether the same question gets solved consistently.
3. Could add a validated judge that classifies GAIA failures by capability (browsing, vision, reasoning, formatting) rather than just pass/fail.

### AgentBench: Evaluating LLMs as Agents

**Tasks:** The LLM-as-Agent had to perform different actions across a wide array of real-world challenges spanning 8 distinct environments.

**Failure definition/metric:** To quantify performance, the authors measured specific metrics tailored to each of the 8 environments:
- **Success Rate (SR):** Used in Operating System, Database, House-Holding, and Web Browsing (Step SR). It measures the ratio of tasks successfully completed over the total number of tasks.
- **F1 Score:** Used for Knowledge Graphs.
- **Game Progress:** Used for Lateral Thinking Puzzles to measure how many key milestone points the agent guessed.
- **Reward:** Used for environments allowing partial success, such as Web Shopping and the Digital Card Game. For example, the Digital Card Game reward combines the win rate and damage rate into a single continuous metric: reward = 0.7 × metric_winrate + 0.3 × metric_damagerate.

**Weakness I can exploit:**
1. The benchmark relies exclusively on basic Chain-of-Thought (CoT) prompting and deliberately excludes advanced reasoning architectures. Should add pass^k and variance decomposition.
2. It heavily simplified complex environments to accommodate LLM context limits and parsing struggles. An improved benchmark would force models to handle raw, noisy, long-context environments without this "training wheels" approach.
3. Final-state checks reward right-answer-wrong-reason equally — add step-level process-adherence judging.

## Week 1
- [ ] tau-bench (arXiv 2406.12045)
- [ ] GAIA (arXiv 2311.12983)

## Week 2
- [ ] AgentBench (arXiv 2308.03688)
- [ ] BALROG (arXiv 2411.13543) — read twice, closest neighbor to Paper 1
- [ ] Crafter (arXiv 2109.06780) — skim
- [ ] Voyager (arXiv 2305.16291) — skim

## Week 3 verdict
(5 sentences, Friday Jul 24: engaging? failures interesting? setup manageable?
could this be Paper 1? what must change?)

## Lit sweep table (Week 4)
paper,year,environment,metric,has_failure_taxonomy,gap

## Friday arXiv skims
(one line per relevant paper)
