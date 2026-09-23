# OpenCode host translation

This repository is a **dual-host** plugin. Its `skills/`, `agents/`, `commands/`,
`scripts/`, and research content are canonical and shared. `opencode/` holds the
thin OpenCode adapter; no canonical content is rewritten for OpenCode.

The adapter (`opencode/host/runtime.ts`) is vendored verbatim from a single
canonical source and pinned in `opencode/host/RUNTIME.sha256`. Every plugin in the
family uses the same adapter; per-host behavior is data in
`opencode/host/manifest.json`. This is a deliberate tradeoff: a hash-pinned,
validator-checked copy in each self-contained repo instead of a new public
dependency or five drifting forks.

## Semantics

| Claude Code concept | OpenCode realization | Difference that matters |
| --- | --- | --- |
| `skills/<x>/SKILL.md` | registered via `ctx.skill.transform` with `path` at the real `SKILL.md` | supporting files resolve as before |
| `commands/<x>.md` | registered via `ctx.command.transform` | `$ARGUMENTS`/`$1..$n` expansion reimplemented identically; unknown frontmatter ignored |
| `agents/<x>.md` | generated native `opencode/agents/<x>.md` (committed, deterministic) | body -> `system`, `description`, `color`, `steps` preserved; `tools` -> `permissions` |
| `model: opus/sonnet/haiku` | resolved at runtime from `opencode/host/tiers.local.json` > env `OPENCODE_MODEL_*` > manifest, applied to the generated agent | unset tier => inherit invoking model (honest fallback) |
| `effort: high` | model `#variant` when the tier maps to a variant | falls back to the base model if the variant is rejected |
| `tools: Bash, Edit, ...` | `permissions` rules | last-match-wins; unmapped tools are recorded, not granted |
| `SubagentStop` hook | `session.execution.{succeeded,failed,interrupted}` event -> the hook script | advisory hooks never block, same as Claude |
| `Workflow` tool: `agent/parallel/pipeline/phase/log`, `meta`, `schema` | `workflow.run` tool executing the same JS over OpenCode child sessions | see below |
| `.mcp.json` | `ctx.mcp.transform` | local stdio + remote configs pass through |
| `CLAUDE_PLUGIN_ROOT` | repo root from `realpath(import.meta.dir)` walking up to `.claude-plugin/plugin.json` | no absolute machine paths committed |
| `CLAUDE_PLUGIN_DATA` | OpenCode plugin `ctx.storage` | durable JSON in the plugin's own scope |

## Workflow compatibility runtime

`workflow.run({ script, args })` executes a canonical workflow script that uses:

- `agent(prompt, { label, agentType, phase, schema, model, timeoutMs, worktree })`
  -> one fresh-context OpenCode child session; returns validated structured output
  or text. `agentType: '<namespace>:<name>'` resolves to agent id `<namespace>/<name>`.
  An unknown `agentType` throws.
- `parallel([() => agent(...), ...])` -> concurrent children.
- `pipeline(items, ...stages)` -> per-item ordered, data-dependent stages; items run concurrently.
- `phase(title)` / `log(msg)` -> durable run state plus live tool progress.

It returns `{ runId, ok, value, phases, logs, receipts }` and persists the same
under `run:<runId>:*` (`workflow.status({runId})` reads it).

Epistemic guarantees: a child's report is **testimony**, never verification;
`schema` output is validated for real and a mismatch throws; a failed, timed-out,
or interrupted child makes `ok:false` and is never reported as success; worktree
-isolated children are removed afterward and the removal result is recorded.

### Reproduced

`agent()`, `parallel()`, `pipeline()`, `phase()`, `log()`, structured schema
validation, labels, timeouts, cancellation, nested workflows, worktree isolation,
durable receipts, error propagation, fresh child context, child-completion hooks.

### Not reproduced (boundaries)

- Anthropic's hosted `/workflows` monitoring pane. OpenCode exposes child sessions
  in its own session list and `workflow.status`; there is no single workflow pane.
- `meta` is accepted as data but not used to pre-register phases.
- Claude's `PushNotification` tool has no OpenCode equivalent; agents that request
  it are recorded in the boundary report and the tool is not granted.
