# Contributing

## Adding a skill

1. Add a dict to the shortest of `src/dyninst/corpus/part1.py`..`part3.py`.
2. Meet every floor: 3+ steps, 2+ signals, 1+ pattern, 2+ pitfalls, a phase from the closed set of
   13, at least one HTTPS-labelled reference, and 80+ rendered words.
3. Run `dyninst validate` — it must print `50/50 skills valid`.
4. Run `dyninst build` to regenerate `skills/`, `pack.json` and `results/catalog.md`.
5. Run `python -m pytest -q`.

## Rules for content

- Write the procedure as instructions an operator can follow, not as background reading.
- Every signal must be something observable, not a restatement of the step.
- Every pitfall must be a failure that actually wastes time, not a generic warning.
- `avoid_when` must name the condition that makes the skill the wrong choice.
- Cite primary documentation. No blog posts as the only reference.

## What will be rejected

- A skill that duplicates an existing title or summary.
- A skill added to the corpus without a rebuild, which leaves stale artifacts.
- Lowering a floor in `validate.py` to make a thin skill pass.
