# OpenCode live integration report

Host: **OpenCode v2.0.14** (`opencode --version`), Node **v22.23.1**, bun absent, Linux x86_64.
Probes run **2026-09-23** against the installed contracts (`@opencode/plugin@2.0.14`).

Evidence labels: **VERIFIED** = live probe on the current host passed · **OBSERVED** = seen once with a stated scope · **CONJECTURED** = supported, decisive probe missing · **UNVERIFIED** = probe not run · **BOUNDARY** = real host limitation.

## 1. Host-attested verification (the merge blocker)

The plugin never executes a shell and never accepts caller-supplied `exitCode`/`passed`.
`workflow_verify({runId, verifyId})` resolves a **repo-owned** trusted command and certifies
only from OpenCode's own tool-execution telemetry for a real `shell` run of it. Replay is
blocked (one host execution certifies exactly one verification).

**Attested pass — VERIFIED** (background service, real `shell` tool, agent session):

```json
{"ok":true,"status":"verify-passed","passed":true,"attested":true,"verifyId":"adapter-validate",
 "command":"python3 /home/leah/grok-bitch/scripts/opencode-validate.py","exitCode":0,
 "sessionID":"ses_f2f6b54d9ffedCu3AKeeCk8sZg","callID":"call_lcnd1wvt",
 "receipt":{"stdoutTail":"validate grok-bitch: PASS\n ... host version gate: tested == installed (2.0.14)\n"}}
```

**Attested failure — VERIFIED** (temporary trusted verifier `always-fail` = `false`):

```json
{"status":"verify-failed","passed":false,"attested":true,"exitCode":1,"command":"false","callID":"call_l3rhzde4"}
finish -> {"verdict":"verify-failed","ok":false}
```

**No-attestation ⇒ fails — VERIFIED** (verify called without running the command):

```json
{"ok":false,"status":"no-attestation","passed":false,"attested":false,
 "hint":"run this exact command via the host shell tool, then call workflow_verify again: ..."}
```

**Replay blocked — VERIFIED**: the second `workflow_verify` after one real run returned
`no-attestation` (the attestation is consumed).

**Unknown `verifyId` rejected — VERIFIED**: `{"status":"unknown-verify", ...}`.

**Cold host (fresh `opencode run --standalone`): `finish -> verdict:"verify-passed"`** — VERIFIED.

Fabricated input is impossible: the tool schema is `{runId, verifyId, childSessionID?}`,
`additionalProperties:false`; `command`/`exitCode`/`passed` do not exist as inputs.

### Verification telemetry mechanism (probed)

- `ctx.tool.hook("execute.after", cb)` fires with
  `{tool:"shell", sessionID, agent, id, input:{command}, status:"completed", result}` where
  `result.output.exit` / `result.metadata.exit` are the real exit code.
- Hooks fire for tool executions in **agent sessions** (both the background service and a
  cold `--standalone` server). Harness/Code-Mode-owner tool executions are not observable —
  the orchestrator must run the trusted command in **its own** session (as designed).
- `ATTEST_REG` re-registers the hook on every `setup`; registration is idempotent per
  execution.

## 2. Guard directory bookkeeping (previously-restored-but-unreported)

Live child (`project-zion:tank`) mutating a guarded path; snapshot + revert in the parent:

| case | status | touchedPaths |
| --- | --- | --- |
| protected directory deleted (`rmdir emptydir`) | `guard-touch` | `["emptydir"]` |
| protected directory mode changed (`chmod 700`) | `guard-touch` | `["guardeddir"]` |
| nested protected file deleted | `guard-touch` | `["guardeddir/nested/a.txt"]` |
| protected file replaced by directory | `guard-touch` | `["guardfile"]` |

All four **VERIFIED**, exact original state restored. Unit regressions (adapter selftest,
**82 assertions PASS**) additionally cover non-empty directory deletion, non-empty directory
mode change, directory replaced by file, file replaced by directory, binary byte-for-byte
restore, symlink retarget, and `..`/absolute/symlink-escape rejection.

## 3. Four-plugin coexistence on a cold host

Fresh `opencode run --standalone` server (all four plugins cold-loaded), one real job per
namespace in the same process, correct agents and no collisions — **VERIFIED**:

```json
RESULT: {"gb":"grok-bitch/morty","pz":["project-zion/oracle","project-zion/smith"],
         "pe":"project-euler/daniel","um":true}
```

- grok-bitch → `grok-bitch/morty`
- project-zion → `project-zion/oracle` + `project-zion/smith` (real `Promise.all` parallelism)
- project-euler → `project-euler/daniel`
- upper-management → real `uppermanagement packet ...` CLI, exit 0
- `opencode run --standalone --agent <ns>/<name>` loads each generated agent;
  `--agent grok-bitch/does-not-exist` → `Agent not found` (negative control).

Runtime validators (`--runtime`) for all five repos: **PASS**.
Host version gate: `tested == installed (2.0.14)`.

## 4. Cancellation, worktrees, agent selection (previous round, unchanged)

- Workflow terminal state (OPEN → FINISHED | CANCELLED; terminal rejects new work; cancel
  idempotent) — **VERIFIED**.
- Unique worktrees for 3 parallel children, all removed; `worktree.remove force:true` —
  **VERIFIED**.
- Explicit `switchAgent` + assertion of the actual child agent id — **VERIFIED**.
- Timeout interruption (`resume:false`) → `status:"interrupted"` — **VERIFIED**.
  Full service-restart persistence of an OPEN run: **BOUNDARY** (a forced restart of the
  shared background service was not performed here; reload-persistence was verified in the
  previous round).

## 5. Reproduce

```sh
bash scripts/opencode-install.sh
python3 scripts/opencode-validate.py --runtime
bash opencode/tests/live-matrix.sh          # cold-host attestation + coexistence
```
