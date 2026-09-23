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
`workflow_status`, `workflow_cancel`, `workflow_finish` — registered under the
plugin's own tool namespace. `workflow_agent` owns: fresh session creation, agent
selection, model-tier application, structured-output validation, timeout, worktree
isolation, guard snapshot/revert, the verify gate, receipts, and cleanup.

**Status contract:** `{ ok, status, report, claim, guard, verify, output, childSessionID }`.
- `status` ∈ `done | handed-back | too-big | guard-touch | verify-failed | executor-error | interrupted | schema-error`.
- terminal success/failure comes from the session's real `idle.outcome`, never an invented marker.
- the child's `report`/`claim` is testimony; `guard`/`verify`/`status` are mechanical.

### Cage machinery (grok-bitch)

`guardPaths` snapshot files before a step and revert any change after, yielding
`guard-touch`. `verifyCommand`/`verifyExpectExit` run the acceptance command and yield
`verify-failed` on a non-zero exit. The verify execution is trusted cage machinery,
enabled only by this repo's committed manifest (`cage.verifyExec`), equivalent in trust
to OpenCode's own shell tool.

### Not reproduced (boundaries)

- No hosted `/workflows` monitoring pane; inspect runs with `workflow_status`.
- `meta`/declarative DAGs from Claude workflows are not pre-registered; Code Mode composes.
- Claude's `PushNotification` has no OpenCode action and is recorded, not granted.
- Programmatic sessions cannot set a native `parentID` (create drops it); ownership is our
  own recorded metadata, and the Session API's `idle.outcome` is the completion contract.
- Server plugins have no toast API; hook advisories are durable (`workflow_status`) — native
  UI surfacing would require a separate TUI plugin.

## grok-bitch is a Rick & Morty orchestrator

Despite the historical name, **grok-bitch does not manage or call Grok/xAI**. The external
Grok CLI/model harness was retired; Morty is the bounded, untrusted-by-default executor
subagent, Rick is the handler/orchestrator, and the reusable contribution is the cage
discipline. The OpenCode port preserves this: Rick orchestrates, Morty does bounded grunt
work, the cage constrains the work, and the caller verifies. Grok is history, not runtime.
