# OpenCode live integration report

Host: **OpenCode v2.0.14** (`opencode --version`), Node **v22.23.1**, bun absent, Linux x86_64.
Probes run **2026-09-23** against the installed contracts (`@opencode/plugin@2.0.14`).

Evidence labels: **VERIFIED** = live probe on the current host passed · **OBSERVED** = seen once with a stated scope · **CONJECTURED** = supported, decisive probe missing · **UNVERIFIED** = probe not run · **BOUNDARY** = real host limitation.

## 1. Fresh-bound, host-attested verification (the merge blocker)

The plugin never executes a shell and never accepts caller-supplied `command`/`exitCode`/
`passed`. Verification is **two-stage and fresh-bound**:

1. `workflow_verify_prepare({runId, verifyId})` opens a single-use **challenge**
   (`{challengeId, command, createdAt, boundAt}`) from a **repo-owned** trusted command.
2. The orchestrator runs that exact command via OpenCode's normal `shell` tool.
3. `workflow_verify({runId, verifyId, challengeId})` certifies only from OpenCode's own
   tool-execution telemetry (`ctx.tool.hook("execute.after")`) and only if
   `attestation.at >= max(challenge.createdAt, run.lastChildAt)`. Challenge **and** attestation
   are consumed on every valid attempt.

**Why this is sufficient.** The challenge pins the evidence boundary to one workflow state:
nothing that ran before the challenge, and nothing before the last child change, can certify
the run; one-use consumption forbids replay; the evidence source is the host's own execution,
so the caller only chooses *which* trusted verifier to request, never the evidence itself.

### Hostile freshness matrix — all VERIFIED (cold `--standalone` host unless noted)

| case | result |
| --- | --- |
| **A** stale pre-run execution | `status:"stale-attestation", attested:true, fresh:false` (attestationAt < challengeCreatedAt) |
| **B** stale pre-child-change execution | `status:"stale-attestation"` (attestationAt < boundAt = last child completion) |
| **C** fresh execution under challenge | `status:"verify-passed", attested:true, fresh:true, exitCode:0`; `finish → verdict:"verify-passed"` |
| **D** replay (same challenge twice) | `status:"unknown-challenge"` |
| **E** wrong `verifyId` | `status:"unknown-verify"` |
| **F** wrong command cannot certify | `status:"no-attestation"` |
| **G** wrong session (background service, 2 sessions) | `status:"wrong-session"` |
| **H** terminal run cannot newly verify | `status:"terminal"` |

Exact evidence (C and B):

```json
C: {"ok":true,"status":"verify-passed","passed":true,"attested":true,"fresh":true,
    "verifyId":"adapter-validate","command":"python3 /home/leah/grok-bitch/scripts/opencode-validate.py",
    "exitCode":0,"callID":"call_function_a6stlfdn4vml_1",
    "receipt":{"challengeId":"vc_muer5u66_rhr01y","boundAt":1790207228670,"stdoutTail":"validate grok-bitch: PASS ..."}}
  finish -> {"verdict":"verify-passed","ok":true}
B: {"status":"stale-attestation","attested":true,"fresh":false,"exitCode":0,
    "attestationAt":1790207295276,"challengeCreatedAt":1790207292756,"boundAt":1790207306756,
    "error":"the host execution predates the verification challenge or the latest child change"}
```

### Telemetry mechanism (probed)

`ctx.tool.hook("execute.after", cb)` fires with
`{tool:"shell", sessionID, agent, id, input:{command}, status:"completed", result}` where
`result.output.exit` / `result.metadata.exit` is the real exit code. Hooks fire for tool
executions in agent sessions (both the shared service and a cold `--standalone` server); the
orchestrator must therefore run the trusted command in **its own** session (as designed).

## 2. Guard directory bookkeeping (previously-restored-but-unreported)

Live child (`project-zion:tank`) mutating a guarded path; snapshot + revert in the parent:

| case | status | touchedPaths |
| --- | --- | --- |
| protected directory deleted (`rmdir emptydir`) | `guard-touch` | `["emptydir"]` |
| protected directory mode changed (`chmod 700`) | `guard-touch` | `["guardeddir"]` |
| nested protected file deleted | `guard-touch` | `["guardeddir/nested/a.txt"]` |
| protected file replaced by directory | `guard-touch` | `["guardfile"]` |

All four **VERIFIED**, exact original state restored. Adapter unit tests (**89 assertions
PASS**) additionally cover non-empty directory deletion/mode, dir↔file replacement, binary
byte-for-byte restore, symlink retarget, and `..`/absolute/symlink-escape rejection.

## 3. Four-plugin coexistence on a cold host

Fresh `opencode run --standalone` server (all four plugins cold-loaded), one real job per
namespace in one process — **VERIFIED**:

```json
RESULT: {"gb":"grok-bitch/morty","pz":["project-zion/oracle","project-zion/smith"],
         "pe":"project-euler/daniel","um":true}
```

- grok-bitch → `grok-bitch/morty`; project-zion → `oracle` + `smith` (real `Promise.all`);
  project-euler → `daniel`; upper-management → real `uppermanagement packet ...` CLI, exit 0.
- `opencode run --standalone --agent <ns>/<name>` loads each generated agent;
  `--agent grok-bitch/does-not-exist` → `Agent not found` (negative control).
- Runtime validators `--runtime` and `--live`: **PASS**; host gate `tested == installed (2.0.14)`.

## 4. Agent selection, Zion failure semantics, Euler phases (cold host)

**Agent selection = requested — VERIFIED**: `grok-bitch/morty`, `grok-bitch/rick`,
`project-zion/neo`, `project-zion/smith`, `project-euler/euler`, `project-euler/dalembert`.

**Zion — one child failure does not become consensus — VERIFIED**: parallel children gave
`statuses:["done","schema-error"]`, the failing child's `output:null`, both preserved
separately (never averaged).

**Euler phases + structured Ledger transfer — VERIFIED**: `daniel/goldbach/dalembert` with
`Observed/Conjectured/Observed` (the Ledger *value* is testimony; agent/phase/validation mechanical).

## 5. Not run / boundaries

- UpperManagement provider-backed `audit`/`reconcile` (admission `codex|claude`, none
  configured): **UNVERIFIED / explicit boundary**. `packet` path and provider admission VERIFIED.
- Full restart of the shared background service: **BOUNDARY** — cold-start of a fresh
  `--standalone` server loading all plugins IS verified; the shared service was not restarted
  to avoid terminating the auditing session.

## 6. Reproduce

```sh
bash scripts/opencode-install.sh
python3 scripts/opencode-validate.py            # static checks
python3 scripts/opencode-validate.py --runtime  # + live host registry probes
python3 scripts/opencode-validate.py --live     # + a real Code Mode round-trip
bash opencode/tests/live-matrix.sh              # cold-host fresh-verify + coexistence matrix
```
