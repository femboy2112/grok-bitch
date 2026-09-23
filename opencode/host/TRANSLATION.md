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
`workflow_status`, `workflow_record_verify`, `workflow_cancel`, `workflow_finish` —
registered under the plugin's own tool namespace. `workflow_agent` owns: fresh session
creation, **explicit `switchAgent` + assertion of the actual agent**, model-tier
application, structured-output validation, timeout, **unique** worktree isolation, guard
snapshot/revert, receipts, and cleanup.

**No server-side shell execution.** `verifyId` returns a trusted command as a *hint*; the
orchestrator runs it with the host's normal `shell` tool (so OpenCode's shell permission
surface applies) and records the observed result with `workflow_record_verify`. The plugin
never `spawn`s a model-supplied command.

**State machine:** `OPEN → FINISHED | CANCELLED`, both terminal. After a terminal state,
`workflow_agent`/`workflow_phase`/`workflow_log`/`workflow_finish` return explicit
`{ok:false,status:"terminal"}` errors; `workflow_cancel` is idempotent only.

**Status contract:** `{ ok, status, report, claim, guard, verifyHint, output, childSessionID }`.
- `status` ∈ `done | handed-back | too-big | guard-touch | guard-rejected | schema-error | executor-error | interrupted`.
- terminal success/failure comes from the session's real `idle.outcome`, never an invented marker.
- the child's `report`/`claim` is testimony; `guard`/`status` are mechanical; verify is recorded separately.

### Cage machinery (grok-bitch)

- **Byte-exact, recursive guard.** `guardPaths` snapshots protected files, directories
  (recursively), and symlinks as raw bytes + mode; after the step it detects modified /
  deleted / created files, directory-membership changes, type replacement, symlink
  retargets, and mode changes, then restores exact original state and reports every touched
  path. No UTF-8 round-trip; binary restores byte-for-byte.
- **Workspace confinement.** Model-supplied `guardPaths` are resolved and rejected if they
  escape the workspace via `..`, an absolute path, or a symlink. Repo-owned
  `defaultProtected` paths are trusted.
- **Verify via host permissions.** See above — the plugin executes no verify shell.

### Not reproduced (boundaries)

- No hosted `/workflows` monitoring pane; inspect runs with `workflow_status`.
- `meta`/declarative DAGs from Claude workflows are not pre-registered; Code Mode composes.
- Claude's `PushNotification` has no OpenCode action and is recorded, not granted.
- Programmatic sessions cannot set a native `parentID` (create drops it). The recorded
  `pluginId/runId/parentSessionID/sessionID/agentID/role` is a **logical parent
  relationship managed by our workflow layer**, not a native OpenCode parent-child session.
- Server plugins have no toast API; hook advisories are durable and read via `workflow_status`.
- **Host compatibility gate:** this adapter was probed against OpenCode **2.0.14** and uses
  the 2.0.14 `Skill.Info` contract (`path`). A different host version is reported as
  `host compatibility not established` in `host:status`/validation, not silently accepted.

## grok-bitch is a Rick & Morty orchestrator

Despite the historical name, **grok-bitch does not manage or call Grok/xAI**. The external
Grok CLI/model harness was retired; Morty is the bounded, untrusted-by-default executor
subagent, Rick is the handler/orchestrator, and the reusable contribution is the cage
discipline. The OpenCode port preserves this: Rick orchestrates, Morty does bounded grunt
work, the cage constrains the work, and the caller verifies. Grok is history, not runtime.
