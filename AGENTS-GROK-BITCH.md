# Driving grok-bitch (for Claude Code)

`grok-bitch` lets you offload **mechanical, well-specified, verifiable** work to
**Morty** — a bounded, untrusted-by-default Claude subagent — so you don't waste your
own rigor on it. Morty is dim and untrusted; the **cage discipline** bounds him and you
independently verify what he claims. **Always re-check Morty's output** — he ends every
report with a disclaimer to that effect.

> **grok is gone.** This was once a CLI that caged an external **grok** model; grok and
> the CLI have been retired. "Morty" is now a caged Claude subagent, the cage is a
> discipline, and the name `grok-bitch` stays as the brand.

## When to delegate (and when not)

Delegate: writing/running scratch probes, bulk numeric grids, mechanical refactors,
adding type hints / docstrings, generating test fixtures, running an existing test
suite and pasting output, repetitive edits across files, boilerplate.

Do **not** delegate: anything needing judgment, novel design, the actual
certification/verdict, proofs, or touching inviolable state. Those are yours.

## The call

Spawn the caged executor with the **Agent tool**:

- **`grok-bitch:rick`** — the handler. Hand him the goal, the workspace dir, and a
  verify command; he decomposes it, cradles Morty step by step, independently verifies,
  and returns a clean verdict. Preferred for anything non-trivial.
- **`grok-bitch:morty`** — a single bounded, mechanical step you'll verify yourself.

```text
Agent(subagent_type="grok-bitch:rick",
      prompt="<one precise, self-contained goal>. Workspace: <dir>.
              Verify with: <CMD>. Guard (do not touch): <protected paths>.")
```

- Be specific and bounded. Morty does exactly what you say, badly if vague.
- Read the **outcome**, then **verify the real path yourself** — never trust the word.

## The cage discipline (what keeps offloading safe)

- **Bounded scope** — one step, confined to the workspace. No wandering.
- **Protected paths** — name the inviolable ones (e.g. `docs/core`, `docs/papers`,
  `canonical/`, `.git/hooks`); if one is touched it's reverted and reported, never
  blind-retried.
- **Verify gate** — pair any edit with a verify command; not "done" until it's green
  *and you re-ran it*.
- **Never self-certify** — the report is a claim, not proof; verify the path a user
  actually runs, plus a static pass (linter/type-checker) for branches one run skips.
- **Hand back if too big; never push** — nothing irreversible or outward on the
  executor's say-so.

## Branch on the outcome

```
done          → use it (then double-check yourself)
guard-touch   → Morty touched an inviolable path; it was reverted. Do NOT retry blindly.
verify-failed → Morty's work failed the gate. Read the failure tail, fix the task, or do it yourself.
too-big/stuck → too big, wedged, or gone silent (a hang is a FAILURE). Narrow it or take it back.
executor-error→ Morty broke / came back garbled. Reformulate smaller.
handed-back   → Morty bailed honestly. Re-scope it.
```

Precedence: **guard-touch > verify-failed > too-big/stuck > executor-error > done.** A
safety breach always surfaces.

## For truth-hunts, not grunt-work

When the job is to *find or trust a truth* rather than grind out mechanical labor, reach
for the bundled **Aletheia Method** (`skills/the-aletheia-method/`) and its
**Interferometry instruments** (`skills/aletheia-interferometry/`): triangulate from
independent blind bearings (Council Rick, the Citadel Ricks), build a discriminating
probe yourself, and certify dominance, not truth. They auto-invoke on their own.

## Examples

```text
# A throwaway probe (guard docs/core & docs/papers if present)
Agent(subagent_type="grok-bitch:morty",
      prompt="Create scratch/rank_probe.py that loads the encoder and prints output
              eff-rank over 50 steps; run it; paste the numbers. Touch nothing else.
              Workspace: /home/leah/agi2. Guard: docs/core, docs/papers. Report the outcome.")

# A mechanical edit gated on the real CI, cradled by Rick
Agent(subagent_type="grok-bitch:rick",
      prompt="Add a boundedness regression test for the new cache cap in
              agi/language/lexicon.py, mirroring the existing ones. Additive only.
              Workspace: /home/leah/agi2. Verify with: timeout 600 make check. Guard: docs/core.")
```

Remember: Morty is the bitch. You are the one accountable for the result. Verify.
