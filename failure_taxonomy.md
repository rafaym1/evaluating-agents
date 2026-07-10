# Shared Failure Taxonomy (v0)

Seven labels applied to both domains. First six are automatically or
near-automatically detectable; NO_TRANSFER is measured via paired
standard/variant tasks.

| Label | Definition | Crafter form | Tutoring form |
|---|---|---|---|
| INVALID_OR_HALLUCINATED_ACTION | Asserts/attempts something not real | invalid command | false explanation or wrong code |
| REPETITION_LOOP | Repeats a useless pattern | same futile action sequence | same hint repeated |
| MEMORY_OR_STATE_FAILURE | Forgets established state | forgets location/inventory | forgets student's misconception |
| BAD_PLAN_OR_SUBGOAL_ORDER | Wrong ordering of steps | wrong crafting/exploration order | teaches wrong prerequisite order |
| POOR_RECOVERY | Fails to detect/escape an error state | stuck after damage/death | ignores student correction |
| FAKE_COMPETENCE | Fluent, confident, no substance | eloquent plan, zero progress | sounds helpful, never diagnoses |
| NO_TRANSFER | Succeeds on standard form, fails slight variant | fails on unusual seed/layout | fails same misconception in new code surface |

## Detailed entries

Template to fill (Week 6), only with observed run ids ("not yet observed" is honest data):

```
### <LABEL>
Definition:
Crafter example (run id):
Tutoring example (run id):
Automatic signal:
Manual judgment needed:
Why it matters:
```
