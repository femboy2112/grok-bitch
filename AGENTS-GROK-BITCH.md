# Driving grok-bitch (for Claude Code)

`grok-bitch` lets you offload **mechanical, well-specified, verifiable** work to
grok so you don't waste your own rigor on it. grok is dumb and untrusted; the
harness cages it and hands you a structured verdict. **Always re-check grok's
output** — it prints a disclaimer to that effect on every run.

## When to delegate (and when not)

Delegate: writing/running scratch probes, bulk numeric grids, mechanical refactors,
adding type hints / docstrings, generating test fixtures, running an existing test
suite and pasting output, repetitive edits across files, boilerplate.

Do **not** delegate: anything needing judgment, novel design, the actual
certification/verdict, proofs, or touching inviolable state. Those are yours.

## The call

```bash
grok-bitch run "<one precise, self-contained task>" --dir <workspace> [--profile P] [--verify "CMD"]
```

- Be specific and bounded. grok does exactly what you say, badly if vague.
- Parse **stdout** as JSON. Branch on **`exit_code`** / `verdict`.
- Pre-flight once per session with `grok-bitch doctor`.

## Pick a profile

- `readonly` — read & report only; grok cannot write or run shell. Safe default for "look at X".
- `scratch` *(default)* — write scratch files & run code, confined to `--dir`.
- `edit` — modify project files. **Always pair with `--verify`.**
- `online` — only when the task truly needs the web.

## Branch on the result

```
0  success            → use it (then double-check)
10 guard_violation    → grok tried to touch an inviolable path; it was reverted. Do NOT retry blindly.
11 verify_failed      → grok's work failed the gate. Read .verify.tail, fix the task, or do it yourself.
12 grok_error         → grok broke. Read .grok.stderr_tail.
13 timeout            → task too big / stuck. Narrow it or raise --timeout.
15 resource_exceeded  → grok tried to OOM/flood the box; killed. Narrow the task.
14 preflight_error    → your args/env are wrong. Read .error.
```

```bash
out=$(grok-bitch run "..." --dir /repo --profile edit --verify "make check"); rc=$?
verdict=$(echo "$out" | jq -r .verdict)
[ "$rc" -eq 0 ] && echo "$out" | jq -r .changes   # review what changed, then verify yourself
```

## Protected paths are automatic

`docs/core`, `docs/papers`, `canonical/`, `.git/hooks` are auto-guarded if present.
Add more with `--guard PATH` (repeatable) or a `.grok-bitch.guards` file in the repo.
Anything guarded that changes → the run fails (exit 10) and is reverted. You never
have to trust grok to respect them.

## Resource caps are on by default

grok's whole process tree is capped (default 4 GB / 4 cores, no swap) via a kernel
cgroup. A `make check` that needs more memory: raise `--mem-max`. Never use
`--no-resource-limit` on a shared box — it can OOM the machine.

## Examples

```bash
# agi2: a throwaway probe (docs/core & docs/papers auto-guarded)
grok-bitch run "Create scratch/rank_probe.py that loads the encoder, prints output \
eff-rank over 50 steps; run it; paste the numbers. Touch nothing else." \
  --dir /home/leah/agi2 --profile scratch

# agi2: mechanical edit gated on the real CI
grok-bitch run "Add a boundedness regression test for the new cache cap in \
agi/language/lexicon.py, mirroring the existing ones. Additive only." \
  --dir /home/leah/agi2 --profile edit --verify "timeout 600 make check"

# Collatz: bulk numerics (canonical/ auto-guarded, exact-arith discipline is yours to state)
grok-bitch run "Run tools/spectral.py for r=2 over the t-grid in scratch/grid.json, \
write results to scratch/out.json. Do not edit anything under canonical/." \
  --dir /home/leah/Collatz/C --profile scratch --verify "python3 tools/anchors.py"
```

Remember: grok is the bitch. You are the one accountable for the result. Verify.
