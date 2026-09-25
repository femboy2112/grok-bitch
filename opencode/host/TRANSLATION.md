# OpenCode host translation

This repository is a **dual-host** plugin. `skills/`, `agents/`, `commands/`,
`scripts/`, and research content are canonical and shared. `opencode/` holds a thin
adapter; no canonical content is rewritten for OpenCode.

## Architecture

```
canonical plugin content  +  opencode/plugin/manifest.json
        |
        +-- Claude host   (.claude-plugin, unchanged)
        |
        +-- OpenCode host (opencode/plugin/, thin)
```

`opencode/plugin/runtime.ts` is vendored verbatim from a single canonical source and
pinned by `opencode/plugin/RUNTIME.sha256`. `index.ts` is a two-line file that imports
`./runtime.ts` and calls `defineHostPlugin(manifest)` — so the hash pins the code that
actually loads, with no duplicated implementation. The installer writes a **loader**
`~/.config/opencode/plugins/<id>.ts` that re-exports `<repo>/opencode/plugin/index.ts`;
because the target file is imported by absolute path, relative imports and
`import.meta.dir` resolve inside the repository.

## Runtime contract (probed against the installed OpenCode 2.0.14)

| Claude Code concept | OpenCode realization | Difference that matters |
| --- | --- | --- |
| `skills/<x>/SKILL.md` | `ctx.skill.transform` → `SkillEditor.add({ id, name, description, path, content })` | the field is **`path`** (verified against the installed `Skill.Info` schema); supporting files resolve via that path |
| `commands/<x>.md` | `ctx.command.transform` → `CommandEditor.add({ name, description, execute })` | registered as **`<plugin-id>/<x>`** to avoid collisions; `$ARGUMENTS`/`$1..$n` expansion reimplemented identically |
| `agents/<x>.md` | generated native `opencode/agents/<x>.md` (`AgentEditor` has **no `add`**) | body → system prompt; `tools:` → a **closed** permission allowlist |
| `tools: Bash, Read, …` | `permissions` list built **deny-first** | `{action:"*",deny}` then explicit allows — an explicit canonical allowlist grants no extra capability class; `TodoWrite` is *not* mapped to `edit` |
| `model: opus/sonnet/haiku` | canonical alias → role (`reasoning-heavy`/`directed`/`cheap`) → model, resolved at runtime | provider-agnostic; unset inherits the invoking model; a rejected `#variant` falls back to the base model and says so |
| `SubagentStop` hook | `session.execution.{succeeded,failed,interrupted}` event → hook script | fires **only** for this plugin's own workflow children or its own agent namespace |
| `Workflow` tool | plugin **workflow primitives** composed in OpenCode Code Mode | **no `new Function`**; model-authored code runs only in OpenCode's sandbox and reaches the world solely through permission-checked tools |
| `CLAUDE_PLUGIN_ROOT` | `resolveRepoRoot(realpath(import.meta.dir))` | no absolute machine paths committed |
| `CLAUDE_PLUGIN_DATA` | plugin-scoped `ctx.storage` | one storage scope per plugin; simultaneous installs cannot collide |

## Workflow primitives (safe)

`workflow_start`, `workflow_agent`, `workflow_phase`, `workflow_log`,
`workflow_status`, `workflow_verify_prepare`, `workflow_verify`, `workflow_cancel`,
`workflow_finish` —
registered under the plugin's own tool namespace. `workflow_agent` owns: fresh session
creation, **explicit `switchAgent` + assertion of the actual agent**, model-tier
application, structured-output validation, timeout, **unique** worktree isolation, guard
snapshot/revert, receipts, and cleanup.

**No server-side shell execution, and no self-certification.** `verifyId` resolves to a
**repo-owned trusted command** (never model-supplied). Verification is **two-stage and
fresh-bound**:

1. `workflow_verify_prepare({runId, verifyId})` opens a single-use **challenge** and returns
   `{challengeId, command, createdAt, boundAt}`;
2. the orchestrator runs that exact command with the host's normal `shell` tool
   (OpenCode's shell permission surface) **in the same session**;
3. `workflow_verify({runId, verifyId, challengeId})` certifies only from OpenCode's own
   tool-execution telemetry for that run, and only if the execution happened **after the
   challenge** and **after the latest child completion** (`attestation.at >= max(challenge.createdAt, run.lastChildAt)`).

The caller cannot supply `command`, `exitCode`, or `passed`. Stale evidence (a real but
pre-challenge/pre-child execution) is refused with `status:"stale-attestation"`; absent
evidence with `status:"no-attestation"`; a mismatch with `unknown-challenge` /
`challenge-mismatch` / `wrong-session`. Both the challenge and the attestation are consumed
on every valid attempt, so a verification can never be replayed. **Why this is sufficient:**
the challenge pins the evidence boundary to a single workflow state (nothing before the
challenge or before the last child change can certify it), the one-use consumption forbids
replay, and the telemetry source is the host's own execution — the caller only chooses
*which* trusted verifier to request, never the evidence. The plugin never `spawn`s a
model-supplied command.

**Requested verification is a mandatory debt.** `workflow_agent(... verifyId:"X")` records
`X` as required (distinct from *completed* verification; it is never inferred from the
absence of a receipt). `workflow_finish` computes the required set against the latest
receipt per verifier and fails unless every required verifier has a fresh, host-attested,
**passing** receipt:

- missing ⇒ `verdict:"verify-missing"`; stale ⇒ `verify-stale`; failed/unattested ⇒ `verify-failed`;
- on unmet debt the run is **not** terminated, so the caller can open a new challenge,
  reverify, and finish again (a corrected-and-reverified run is not permanently poisoned);
- a run with no requested verifier finishes normally (`verdict:"finished"`).

**State machine:** `OPEN → FINISHED | CANCELLED`, both terminal. After a terminal state,
`workflow_agent`/`workflow_phase`/`workflow_log`/`workflow_verify_prepare`/`workflow_verify`/`workflow_finish`
return explicit `{ok:false,status:"terminal"}` errors; `workflow_cancel` is idempotent only.
A `workflow_finish` that fails on an **unmet verification debt** does **not** terminate the
run — the caller discharges the debt and finishes again.

**Status contract:** `{ ok, status, report, claim, guard, verifyHint, output, childSessionID }`.
- `status` ∈ `done | handed-back | too-big | guard-touch | guard-rejected | schema-error | executor-error | interrupted`.
- terminal success/failure comes from the session's real `idle.outcome`, never an invented marker.

**Evidence semantics (do not overclaim):**
- a child's `report`/`claim` is **testimony**;
- `status` and `guard` are **mechanical observations**;
- a `verify` receipt is a **fresh host-attested execution** — only when `attested:true AND fresh:true`;
- the final verdict is the **caller/orchestrator reasoning** over that evidence.


### Cage machinery (grok-bitch)

- **Byte-exact, recursive guard.** `guardPaths` snapshots protected files, directories
  (recursively), and symlinks as raw bytes + mode; after the step it detects modified /
  deleted / created files, directory-membership changes, type replacement, symlink
  retargets, and mode changes, then restores exact original state and reports every touched
  path. No UTF-8 round-trip; binary restores byte-for-byte.
- **Workspace confinement.** Model-supplied `guardPaths` are resolved and rejected if they
  escape the workspace via `..`, an absolute path, or a symlink. Repo-owned
  `defaultProtected` paths are trusted.
- **Verify is host-attested and fresh-bound, never self-certified.** See above — the plugin
  executes no verify shell, and a verification receipt is produced only from OpenCode's own
  telemetry for a real execution of the repo-owned trusted command, bound to a single-use
  challenge. Stale (`stale-attestation`) and absent (`no-attestation`) evidence fail; no
  caller-supplied exit code is ever accepted.
- **Directory/type/mode breaches are reported.** A protected directory that is deleted,
  mode-changed, or replaced by a file (and a file replaced by a directory) is restored and
  reported in `touchedPaths` — a mechanically restored breach never reports `clean`.

### Not reproduced (boundaries)

- No hosted `/workflows` monitoring pane; inspect runs with `workflow_status`.
- `meta`/declarative DAGs from Claude workflows are not pre-registered; Code Mode composes.
- Claude's `PushNotification` has no OpenCode action and is recorded, not granted.
- Programmatic sessions cannot set a native `parentID` (create drops it). The recorded
  `pluginId/runId/parentSessionID/sessionID/agentID/role` is a **logical parent
  relationship managed by our workflow layer**, not a native OpenCode parent-child session.
- Server plugins have no toast API; hook advisories are durable and read via `workflow_status`.
- **Host compatibility gate:** this adapter was probed against OpenCode **2.0.14** and uses
  the 2.0.14 `Skill.Info` contract (`path`, verified against the live host's skill registry).
  A different host version is reported as `host compatibility not established` in
  `host:status`/validation (a non-fatal warning), not silently accepted.
- **2.0.x is the OpenCode V2 line.** As of this writing the public OpenCode release channel is
  **1.x** (e.g. 1.18.x); **2.0.x is the V2 preview**, so this adapter currently requires a V2
  host to run and will report drift on a 1.x install. The pin tracks the V2 API, not a shipped
  public build — expect to bump `HOST_TESTED_VERSION`/`hostTested` when V2 releases publicly.

## Regeneration (provenance)

Every file in `opencode/` and `scripts/opencode-*` is **managed** — generated by the shared
`opencode-host` generator (`generate.py`, which vendors `runtime.ts`/`selftest.mjs` verbatim and
pins the sha). That generator is the single source of truth for this and the sibling family
plugins and is **kept under its own version control** — do not hand-edit the managed files here;
change the generator and re-vendor (`generate.py --only <repo>` to touch just one repo).

## grok-bitch is a Rick & Morty orchestrator

**CURRENT —** grok-bitch is a **Rick & Morty multi-agent orchestrator with a deterministic
cage/verification discipline**:

- **Rick** — the handler/orchestrator: plans, delegates bounded steps, verifies independently.
- **Morty** — the bounded, untrusted-by-default executor: does one well-specified step.
- **cage** — bounded scope, protected-path guard + revert, a verification gate, never
  self-certify, hand back if too large/ambiguous, no autonomous push/deploy/delete.

**HISTORICAL —** the original external **Grok/xAI executor** that gave the project its name.
It was retired; the name stayed, the runtime moved on.

**NOT CURRENT —** grok-bitch does **not** manage or call Grok, does **not** integrate xAI,
and does **not** wrap a Grok CLI or Grok runtime. There is no xAI dependency.
