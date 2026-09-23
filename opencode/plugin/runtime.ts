/**
 * Canonical dual-host adapter runtime — OpenCode side.
 *
 * HOST RUNTIME CONTRACT (probed against the installed OpenCode 2.0.14):
 *   - plugin = default export { id, setup(ctx) } (or { id, effect })
 *   - ctx.tool.transform(editor) — editor.add / namespace / update / remove / list / get
 *     tool Info = { name, description, input, execute, output?, options? }
 *     tool options = { namespace?, permission?, codemode?, pinned? }
 *   - ctx.agent.transform — AgentEditor = list/get/default/update/remove (NO add)
 *       => agents are native files; the adapter only applies model tiers
 *   - ctx.skill.transform — SkillEditor.add(Skill.Info) with
 *       Skill.Info = { id, name, description?, autoinvoke?, path, content }   (path, NOT location)
 *   - ctx.command.transform — CommandEditor.add({ name, description?, execute })
 *   - ctx.session.create/get/switchAgent/switchModel/prompt/wait/context/interrupt/move/synthetic
 *       Session.Info has parentID *field* but create SILENTLY DROPS a supplied parentID,
 *       so programmatic sessions are top-level; ownership is our own recorded metadata.
 *   - terminal lifecycle contract = the `idle` message's `outcome` (succeeded|failed|interrupted)
 *       (Session.Info.outcome mirrors it). We never invent a marker.
 *   - ctx.storage is plugin-scoped JSON. ctx.event.subscribe yields session.execution.*
 *
 * DESIGN LAWS (this revision):
 *   P0  NO model-authored string is ever evaluated as JavaScript by the plugin/server.
 *       Workflow orchestration is a set of permission-checked Code Mode PRIMITIVES; the
 *       model composes them with ordinary JS inside OpenCode's own Code Mode sandbox.
 *   P1  Every plugin registers its OWN namespaced tool set and its OWN storage scope,
 *       so all plugins can be installed simultaneously with no load-order collisions.
 *   P1  Agent permissions are translated as a CLOSED allowlist (deny-first).
 *   P1  Workflow children carry explicit ownership metadata; a plugin's completion hooks
 *       fire only for that plugin's own children (or its own agent namespace).
 *
 * grok-bitch NOTE: despite the historical name, grok-bitch is a Rick & Morty orchestrator
 * with a deterministic cage/verification discipline. Grok/xAI is history, not runtime.
 * The adapter never connects to Grok or xAI.
 */

import { existsSync, readFileSync, readdirSync, statSync, mkdirSync, writeFileSync, rmSync } from "node:fs"
import { join, dirname, basename, isAbsolute, relative } from "node:path"
import { spawn } from "node:child_process"

export const RUNTIME_VERSION = "2.0.0"
export const RUNTIME_API = "opencode-2.0.14"

// --------------------------- manifest shape --------------------------------

export interface HostManifest {
  id: string
  name?: string
  version?: string
  /** Agent id namespace, e.g. "grok-bitch" -> agents "grok-bitch/rick". */
  agentNamespace: string
  /** Canonical tier alias -> provider/model[#variant]. opus|sonnet|haiku are aliases. */
  tiers?: Record<string, string>
  /** Canonical alias -> role name used when the alias itself is unset. */
  tierRoles?: Record<string, string>
  /** Claude tool name -> OpenCode permission action. */
  toolMap?: Record<string, string>
  /** Named colors -> hex. */
  colorMap?: Record<string, string>
  agentsDirs?: string[]
  commandsDirs?: string[]
  skillsDirs?: string[]
  /** Command basenames that are globally unique across the family and may keep a bare alias. */
  commandAliases?: string[]
  /** Register the safe workflow primitives. Default false. */
  workflow?: boolean
  /** Cage machinery (grok-bitch). verifyExec must be enabled by the repo-committed manifest. */
  cage?: { verifyExec?: boolean; defaultProtected?: string[] }
  /** Completion hooks (Claude SubagentStop analogue). */
  hooks?: HostHookDefinition[]
  /** Text appended to every translated command body. */
  commandHostNote?: string
  registerCommands?: boolean
  registerSkills?: boolean
  registerMcp?: boolean
  registerAgents?: boolean
  applyAgentTiers?: boolean
}

export interface HostHookDefinition {
  claudeEvent: "SubagentStop"
  command: string
  timeoutMs?: number
  /** Only fire for children that carry the cast outcome contract. */
  ownsOutcomeContract?: boolean
}

// ------------------------------ small helpers ------------------------------

const isObj = (v: unknown): v is Record<string, any> =>
  typeof v === "object" && v !== null && !Array.isArray(v)

export function parseFrontmatter(source: string): { data: Record<string, any>; body: string } {
  const text = source.replace(/^\uFEFF/, "")
  if (!text.startsWith("---")) return { data: {}, body: text }
  const end = text.indexOf("\n---", 3)
  if (end === -1) return { data: {}, body: text }
  const head = text.slice(3, end).replace(/^\n/, "")
  const body = text.slice(end + 4).replace(/^\n/, "")
  const data: Record<string, any> = {}
  for (const line of head.split("\n")) {
    const m = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line)
    if (!m) continue
    let value = m[2].trim()
    if (/^".*"$/.test(value) || /^'.*'$/.test(value)) value = value.slice(1, -1)
    data[m[1]] = value
  }
  return { data, body }
}

export function tokenizeArgs(input: string): string[] {
  const out: string[] = []
  const re = /"([^"]*)"|'([^']*)'|(\S+)/g
  let m: RegExpExecArray | null
  while ((m = re.exec(input)) !== null) out.push(m[1] ?? m[2] ?? m[3] ?? "")
  return out
}

export function expandArguments(body: string, raw: string): string {
  const args = tokenizeArgs(raw.trim())
  let replaced = false
  let out = body.replace(/\$ARGUMENTS/g, () => { replaced = true; return raw.trim() })
  out = out.replace(/\$(\d+)/g, (_, n) => { replaced = true; return args[Number(n) - 1] ?? "" })
  if (!replaced && raw.trim()) out = `${out}\n\n${raw.trim()}`
  return out
}

const DEFAULT_COLORS: Record<string, string> = {
  blue: "#5c9cf5", green: "#46a758", red: "#e5484d", orange: "#f76b15",
  purple: "#8e4ec6", pink: "#d6409f", cyan: "#00a2c7", yellow: "#f5d90a",
  gray: "#8b8d98", grey: "#8b8d98", magenta: "#d6409f", teal: "#12a594",
  indigo: "#3e63dd", violet: "#8e4ec6", lime: "#8fbf00", fuchsia: "#d6409f",
  gold: "#f5d90a", brown: "#a18072", silver: "#8b8d98", aqua: "#00a2c7",
  blueviolet: "#8e4ec6", crimson: "#e5484d",
}

/** Accept only a hex colour or a mapped name; unknown names are omitted so OpenCode never drops the agent. */
function resolveColor(name: string | undefined, colorMap: Record<string, string>): string | undefined {
  if (!name) return undefined
  if (/^#[0-9a-f]{3,8}$/i.test(name)) return name
  return colorMap[name.toLowerCase()]
}

// --------------------------- JSON Schema (subset) --------------------------
// A deliberately explicit subset. UNKNOWN KEYWORDS ARE REJECTED, never ignored.

export class SchemaError extends Error {}

const KNOWN_SCHEMA_KEYWORDS = new Set([
  "type", "properties", "required", "additionalProperties", "items", "enum", "const",
  "minItems", "maxItems", "minLength", "maxLength", "pattern", "minimum", "maximum",
  "exclusiveMinimum", "exclusiveMaximum", "multipleOf", "oneOf", "anyOf", "allOf", "not",
  "description", "title", "$schema", "$id", "default", "examples",
])

export function assertSupportedSchema(schema: any, path = "$"): void {
  if (!isObj(schema)) return
  for (const key of Object.keys(schema)) {
    if (!KNOWN_SCHEMA_KEYWORDS.has(key)) {
      throw new SchemaError(`unsupported schema keyword "${key}" at ${path}`)
    }
  }
  const sub = (s: any, p: string) => { if (s !== undefined) assertSupportedSchema(s, p) }
  if (isObj(schema.properties)) for (const [k, v] of Object.entries(schema.properties)) sub(v, `${path}.properties.${k}`)
  if (schema.items !== undefined) sub(schema.items, `${path}.items`)
  for (const kw of ["oneOf", "anyOf", "allOf"]) {
    if (Array.isArray(schema[kw])) schema[kw].forEach((s: any, i: number) => sub(s, `${path}.${kw}[${i}]`))
  }
  if (schema.not !== undefined) sub(schema.not, `${path}.not`)
  if (schema.additionalProperties !== undefined && typeof schema.additionalProperties === "object") {
    sub(schema.additionalProperties, `${path}.additionalProperties`)
  }
}

function typeOf(v: any): string {
  if (v === null) return "null"
  if (Array.isArray(v)) return "array"
  return typeof v
}

export function validateSchema(value: any, schema: any, path = "$"): void {
  if (!isObj(schema) || Object.keys(schema).length === 0) return
  if (schema.type) {
    const want = Array.isArray(schema.type) ? schema.type : [schema.type]
    const got = typeOf(value)
    const numericAsInteger = schema.type === "integer" && typeof value === "number" && Number.isInteger(value)
    if (!want.includes(got) && !numericAsInteger) {
      throw new SchemaError(`expected ${want.join("|")} at ${path}, got ${got}`)
    }
  }
  if (schema.enum && !schema.enum.some((e: any) => JSON.stringify(e) === JSON.stringify(value))) {
    throw new SchemaError(`value at ${path} not in enum`)
  }
  if (schema.const !== undefined && JSON.stringify(schema.const) !== JSON.stringify(value)) {
    throw new SchemaError(`value at ${path} != const`)
  }
  if (typeof value === "number") {
    if (typeof schema.minimum === "number" && value < schema.minimum) throw new SchemaError(`minimum at ${path}`)
    if (typeof schema.maximum === "number" && value > schema.maximum) throw new SchemaError(`maximum at ${path}`)
    if (typeof schema.exclusiveMinimum === "number" && value <= schema.exclusiveMinimum) throw new SchemaError(`exclusiveMinimum at ${path}`)
    if (typeof schema.exclusiveMaximum === "number" && value >= schema.exclusiveMaximum) throw new SchemaError(`exclusiveMaximum at ${path}`)
    if (typeof schema.multipleOf === "number" && value % schema.multipleOf !== 0) throw new SchemaError(`multipleOf at ${path}`)
  }
  if (typeof value === "string") {
    if (typeof schema.minLength === "number" && value.length < schema.minLength) throw new SchemaError(`minLength at ${path}`)
    if (typeof schema.maxLength === "number" && value.length > schema.maxLength) throw new SchemaError(`maxLength at ${path}`)
    if (schema.pattern && !new RegExp(schema.pattern).test(value)) throw new SchemaError(`pattern at ${path}`)
  }
  if (Array.isArray(value)) {
    if (typeof schema.minItems === "number" && value.length < schema.minItems) throw new SchemaError(`minItems at ${path}`)
    if (typeof schema.maxItems === "number" && value.length > schema.maxItems) throw new SchemaError(`maxItems at ${path}`)
    if (schema.items !== undefined) value.forEach((v, i) => validateSchema(v, schema.items, `${path}[${i}]`))
  }
  if (isObj(value) && (schema.properties || schema.required || schema.additionalProperties !== undefined)) {
    const props = isObj(schema.properties) ? schema.properties : {}
    for (const key of schema.required ?? []) {
      if (!(key in value)) throw new SchemaError(`missing required "${key}" at ${path}`)
    }
    for (const [k, v] of Object.entries(value)) {
      if (props[k] !== undefined) validateSchema(v, props[k], `${path}.${k}`)
      else if (schema.additionalProperties === false) throw new SchemaError(`unexpected property "${k}" at ${path}`)
      else if (isObj(schema.additionalProperties)) validateSchema(v, schema.additionalProperties, `${path}.${k}`)
    }
  }
  if (Array.isArray(schema.allOf)) schema.allOf.forEach((s: any, i: number) => validateSchema(value, s, `${path}.allOf[${i}]`))
  if (Array.isArray(schema.anyOf)) {
    const ok = schema.anyOf.some((s: any) => { try { validateSchema(value, s, path); return true } catch { return false } })
    if (!ok) throw new SchemaError(`no anyOf matched at ${path}`)
  }
  if (Array.isArray(schema.oneOf)) {
    const n = schema.oneOf.filter((s: any) => { try { validateSchema(value, s, path); return true } catch { return false } }).length
    if (n !== 1) throw new SchemaError(`expected exactly one oneOf match at ${path}, got ${n}`)
  }
  if (schema.not !== undefined) {
    try { validateSchema(value, schema.not, path); throw new SchemaError(`not matched at ${path}`) } catch (e) {
      if (e instanceof SchemaError && /not matched/.test(e.message)) throw e
    }
  }
}

export function extractStructured(text: string): any {
  const fenced = /```(?:json)?\s*([\s\S]*?)```/gi
  let m: RegExpExecArray | null
  const candidates: string[] = []
  while ((m = fenced.exec(text)) !== null) candidates.push(m[1].trim())
  const firstBrace = text.indexOf("{")
  const lastBrace = text.lastIndexOf("}")
  if (firstBrace !== -1 && lastBrace > firstBrace) candidates.push(text.slice(firstBrace, lastBrace + 1))
  candidates.push(text.trim())
  let lastErr: any
  for (const c of candidates) {
    try { return JSON.parse(c) } catch (e) { lastErr = e }
  }
  throw new SchemaError(`no parseable JSON found in report: ${lastErr?.message ?? "unknown"}`)
}

// ------------------------------ translation --------------------------------

const DEFAULT_TOOL_MAP: Record<string, string> = {
  Bash: "shell", BashOutput: "shell", KillShell: "shell",
  Read: "read", NotebookRead: "read",
  Grep: "grep", Glob: "glob",
  Edit: "edit", Write: "edit", MultiEdit: "edit", NotebookEdit: "edit",
  Agent: "subagent", Task: "subagent",
  WebFetch: "webfetch", WebSearch: "websearch",
  Skill: "skill",
}

/** Claude tool names with no faithful OpenCode permission action (recorded, never granted). */
const UNMAPPABLE_TOOLS = new Set([
  "TodoWrite", "PushNotification", "SlashCommand", "exit_plan_mode", "BashOutput",
])

export function translateAgent(
  source: string,
  agentFile: string,
  manifest: Pick<HostManifest, "id" | "name" | "agentNamespace" | "tiers" | "toolMap" | "colorMap">,
): Record<string, any> | null {
  const { data, body } = parseFrontmatter(source)
  if (!body.trim()) return null
  const name = basename(agentFile, ".md")
  const namespace = manifest.agentNamespace
  const id = namespace ? `${namespace}/${name}` : name
  const toolMap = { ...DEFAULT_TOOL_MAP, ...(manifest.toolMap ?? {}) }
  const colorMap = { ...DEFAULT_COLORS, ...(manifest.colorMap ?? {}) }

  const boundaries: string[] = []
  const rawTools = typeof data.tools === "string"
    ? data.tools.split(",").map((t: string) => t.trim()).filter(Boolean)
    : undefined
  const permissions: Array<{ action: string; resource: string; effect: string }> = []
  if (rawTools && rawTools.length) {
    // CLOSED allowlist: deny everything first, then grant only what the canonical list names.
    permissions.push({ action: "*", resource: "*", effect: "deny" })
    const actions = new Set<string>()
    for (const t of rawTools) {
      if (UNMAPPABLE_TOOLS.has(t)) { boundaries.push(`tool ${t} has no OpenCode action`); continue }
      const action = toolMap[t]
      if (!action) { boundaries.push(`unmapped tool ${t}`); continue }
      actions.add(action)
    }
    for (const action of actions) permissions.push({ action, resource: "*", effect: "allow" })
  } else {
    // No explicit allowlist in canonical metadata: preserve the agent's broad default.
    permissions.push({ action: "*", resource: "*", effect: "allow" })
  }

  // Model tier intent is preserved but resolved at runtime (see resolveModel).
  const modelAlias = typeof data.model === "string" ? data.model.trim().toLowerCase() : undefined
  const effort = typeof data.effort === "string" ? data.effort.trim() : undefined

  const system = body.trim()
  const color = resolveColor(data.color, colorMap)
  const steps = data.steps ? Number(data.steps) : undefined

  return {
    id, name, namespace,
    description: data.description || `Translated agent ${name}`,
    system, color, steps,
    permissions,
    modelAlias,
    effort,
    __boundaries: boundaries,
    __source: agentFile,
  }
}

export function translateSkill(source: string, skillFile: string): Record<string, any> | null {
  const { data, body } = parseFrontmatter(source)
  const id = basename(dirname(skillFile))
  if (!body.trim()) return null
  // Authoritative Skill.Info contract (2.0.14): { id, name, description?, autoinvoke?, path, content }
  return {
    id,
    name: data.name || id,
    description: data.description || "",
    path: skillFile,
    content: body.trim(),
  }
}

export function translateCommandBody(source: string, manifest: HostManifest): { data: Record<string, any>; body: string } {
  const { data, body } = parseFrontmatter(source)
  const note = manifest.commandHostNote ? `\n\n${manifest.commandHostNote}` : ""
  return { data, body: body.trim() + note }
}

export function renderAgentFile(agent: Record<string, any>): string {
  const q = (s: string) => JSON.stringify(String(s))
  const fm = ["---", `description: ${q(agent.description)}`, "mode: all"]
  if (agent.color) fm.push(`color: ${q(agent.color)}`)
  if (agent.steps) fm.push(`steps: ${agent.steps}`)
  fm.push("permissions:")
  for (const p of agent.permissions) {
    fm.push(`  - action: ${q(p.action)}`, `    resource: ${q(p.resource)}`, `    effect: ${q(p.effect)}`)
  }
  fm.push("---", "", agent.system, "")
  return fm.join("\n")
}

// ------------------------------ repo + tiers -------------------------------

export function resolveRepoRoot(startDir: string): string {
  let dir = startDir
  for (let i = 0; i < 8; i++) {
    if (existsSync(join(dir, ".claude-plugin", "plugin.json")) || existsSync(join(dir, "opencode", "host", "manifest.json"))) return dir
    const parent = dirname(dir)
    if (parent === dir) break
    dir = parent
  }
  return startDir
}

function parseModelString(s: string): { providerID: string; id: string; variant?: string } | null {
  if (!s || !s.includes("/")) return null
  const [providerID, rest] = s.split("/")
  const [id, variant] = rest.split("#")
  if (!providerID || !id) return null
  return variant ? { providerID, id, variant } : { providerID, id }
}

export function resolveTierModel(manifest: HostManifest, aliasOrRole?: string): string | undefined {
  if (!aliasOrRole) return undefined
  const key = aliasOrRole.toLowerCase()
  const tiers = manifest.tiers ?? {}
  if (tiers[key]) return tiers[key]
  const role = (manifest.tierRoles ?? { opus: "reasoning-heavy", sonnet: "directed", haiku: "cheap" })[key]
  if (role && tiers[role]) return tiers[role]
  return undefined
}

function mergeLocalTiers(repoRoot: string, manifest: HostManifest): void {
  try {
    const tf = join(repoRoot, "opencode", "host", "tiers.local.json")
    if (existsSync(tf)) manifest.tiers = { ...(manifest.tiers ?? {}), ...JSON.parse(readFileSync(tf, "utf8")) }
  } catch { /* malformed local tiers are ignored; defaults still apply */ }
  for (const [alias, role] of Object.entries(manifest.tierRoles ?? { opus: "reasoning-heavy", sonnet: "directed", haiku: "cheap" })) {
    const envKey = `OPENCODE_MODEL_${alias.toUpperCase()}`
    const roleKey = `OPENCODE_MODEL_${String(role).toUpperCase().replace(/-/g, "_")}`
    const v = process.env[envKey] ?? process.env[roleKey]
    if (v) manifest.tiers = { ...(manifest.tiers ?? {}), [alias]: v, [String(role)]: v }
  }
}

// ------------------------------ cage machinery -----------------------------

export interface GuardSnapshot { root: string; files: Array<{ path: string; existed: boolean; content: string }> }

export function guardSnapshot(root: string, paths: string[]): GuardSnapshot {
  const files = paths.map((p) => {
    const abs = isAbsolute(p) ? p : join(root, p)
    const existed = existsSync(abs)
    return { path: abs, existed, content: existed ? readFileSync(abs, "utf8") : "" }
  })
  return { root, files }
}

export function guardCheckAndRevert(snap: GuardSnapshot): { touched: boolean; touchedPaths: string[] } {
  const touchedPaths: string[] = []
  for (const f of snap.files) {
    const now = existsSync(f.path) ? readFileSync(f.path, "utf8") : undefined
    const changed = f.existed ? now !== f.content : now !== undefined
    if (changed) { touchedPaths.push(relative(snap.root, f.path) || f.path); if (f.existed) writeFileSync(f.path, f.content); else if (existsSync(f.path)) rmSync(f.path) }
  }
  return { touched: touchedPaths.length > 0, touchedPaths }
}

export function runVerify(root: string, command: string, expectExit: number, timeoutMs: number): Promise<{
  command: string; exitCode: number | null; ok: boolean; executed: boolean; stdout: string; stderr: string; timedOut: boolean
}> {
  return new Promise((resolve) => {
    const child = spawn(command, { cwd: root, shell: true })
    let stdout = "", stderr = "", timedOut = false
    const timer = setTimeout(() => { timedOut = true; child.kill("SIGKILL") }, timeoutMs)
    child.stdout?.on("data", (d) => { stdout += d.toString() })
    child.stderr?.on("data", (d) => { stderr += d.toString() })
    child.on("close", (code) => {
      clearTimeout(timer)
      resolve({ command, exitCode: code, ok: code === expectExit && !timedOut, executed: true, stdout: stdout.slice(-4000), stderr: stderr.slice(-4000), timedOut })
    })
    child.on("error", (e) => {
      clearTimeout(timer)
      resolve({ command, exitCode: null, ok: false, executed: true, stdout, stderr: String(e), timedOut })
    })
  })
}

/** Parse the cast's machine-readable outcome footer (claims are testimony). */
export function parseOutcomeClaim(text: string): { outcome?: string; label?: string; dissent?: string; openDebts?: number } {
  const block = /```\s*outcome\s*\n([\s\S]*?)```/i.exec(text)
  const body = block ? block[1] : text
  const get = (k: string) => {
    const m = new RegExp(`^\\s*${k}\\s*:\\s*(.*)$`, "im").exec(body)
    return m ? m[1].trim() : undefined
  }
  const debts = get("open-debts")
  return {
    outcome: get("outcome")?.toLowerCase(),
    label: get("label"),
    dissent: get("dissent"),
    openDebts: debts !== undefined && debts !== "" ? Number(debts) : undefined,
  }
}

// ------------------------------- the plugin --------------------------------

function readSessionResult(messages: any[]): { text: string; outcome?: string; messageTypes: string[] } {
  let text = ""
  let outcome: string | undefined
  const messageTypes: string[] = []
  for (const m of messages) {
    messageTypes.push(m?.type)
    if (m?.type === "idle" && typeof m.outcome === "string") outcome = m.outcome
    if (m?.type === "assistant") {
      const parts = Array.isArray(m.content) ? m.content : []
      const joined = parts.filter((p: any) => p?.type === "text").map((p: any) => p.text).join("")
      if (joined) text = joined
    }
  }
  return { text, outcome, messageTypes }
}

export function defineHostPlugin(manifest: HostManifest): { id: string; setup: (ctx: any) => Promise<any> } {
  return {
    id: manifest.id,
    async setup(ctx: any) {
      const pluginDir = (import.meta as any).dir || process.cwd()
      const repoRoot = resolveRepoRoot(pluginDir)
      const boundaries: string[] = []
      mergeLocalTiers(repoRoot, manifest)

      // ------------- skills -------------
      if (manifest.registerSkills !== false) {
        const byId = new Map<string, Record<string, any>>()
        for (const rel of manifest.skillsDirs ?? ["skills"]) {
          const dir = join(repoRoot, rel)
          if (!existsSync(dir) || !statSync(dir).isDirectory()) continue
          for (const d of readdirSync(dir)) {
            const f = join(dir, d, "SKILL.md")
            if (!existsSync(f)) continue
            const s = translateSkill(readFileSync(f, "utf8"), f)
            if (s) byId.set(s.id, s)
          }
        }
        const skills = [...byId.values()]
        if (skills.length) {
          try { await ctx.skill.transform((e: any) => skills.forEach((s) => e.add(s))) }
          catch (err: any) { boundaries.push(`skill registration failed: ${err?.message ?? err}`) }
        }
      }

      // ------------- commands (namespaced) -------------
      if (manifest.registerCommands !== false) {
        const defs: any[] = []
        const seen = new Set<string>()
        for (const rel of manifest.commandsDirs ?? ["commands"]) {
          const dir = join(repoRoot, rel)
          if (!existsSync(dir) || !statSync(dir).isDirectory()) continue
          for (const f of readdirSync(dir)) {
            if (!f.endsWith(".md")) continue
            const base = basename(f, ".md")
            const { data, body } = translateCommandBody(readFileSync(join(dir, f), "utf8"), manifest)
            const names = [`${manifest.id}/${base}`]
            if ((manifest.commandAliases ?? []).includes(base)) names.push(base)
            const rawArgs = body
            for (const name of names) {
              if (seen.has(name)) continue
              seen.add(name)
              defs.push({
                name,
                description: data.description || `Command ${base}`,
                execute: async (inv: any) => {
                  const text = expandArguments(rawArgs, inv.prompt?.text ?? "")
                  await ctx.session.prompt({ sessionID: inv.sessionID, text, delivery: inv.delivery ?? "steer" })
                },
              })
            }
          }
        }
        if (defs.length) {
          try { await ctx.command.transform((e: any) => defs.forEach((d) => e.add(d))) }
          catch (err: any) { boundaries.push(`command registration failed: ${err?.message ?? err}`) }
        }
      }

      // ------------- agents: native files + runtime tier models -------------
      if (manifest.applyAgentTiers !== false && Object.keys(manifest.tiers ?? {}).length) {
        try {
          await ctx.agent.transform((e: any) => {
            if (typeof e.get !== "function") return
            for (const rel of manifest.agentsDirs ?? ["agents"]) {
              const dir = join(repoRoot, rel)
              if (!existsSync(dir) || !statSync(dir).isDirectory()) continue
              for (const f of readdirSync(dir)) {
                if (!f.endsWith(".md")) continue
                const name = basename(f, ".md")
                const id = manifest.agentNamespace ? `${manifest.agentNamespace}/${name}` : name
                if (!e.get(id)) continue
                const data = parseFrontmatter(readFileSync(join(dir, f), "utf8")).data
                let model = resolveTierModel(manifest, String(data.model ?? ""))
                if (model && data.effort && !model.includes("#")) model = `${model}#${data.effort}`
                if (model) e.update(id, (a: any) => { a.model = model })
              }
            }
          })
        } catch (err: any) { boundaries.push(`agent tier update failed: ${err?.message ?? err}`) }
      }

      // ------------- workflow primitives (safe; no eval) -------------
      const live = new Map<string, Set<string>>()
      const liveSessions = () => {
        let s = new Set<string>()
        for (const set of live.values()) for (const id of set) s.add(id)
        return s
      }
      if (manifest.workflow) await registerWorkflow(ctx, manifest, repoRoot, boundaries, live)

      // ------------- completion hooks -------------
      const cleanups: Array<() => void> = []
      for (const hook of manifest.hooks ?? []) {
        if (hook.claudeEvent !== "SubagentStop") continue
        const controller = new AbortController()
        cleanups.push(() => controller.abort())
        void (async () => {
          try {
            for await (const ev of ctx.event.subscribe({ signal: controller.signal })) {
              const t = (ev as any).type
              if (!/^session\.execution\.(succeeded|failed|interrupted)$/.test(t)) continue
              const sid = (ev as any).data?.sessionID
              if (!sid) continue
              const receipt: any = await ctx.storage.get(`child:${sid}`).catch(() => undefined)
              let info: any
              try { info = await ctx.session.get({ sessionID: sid }) } catch { info = undefined }
              const ownAgent = typeof info?.agent === "string" && info.agent.startsWith(`${manifest.agentNamespace}/`)
              const ownChild = !!receipt && receipt.pluginId === manifest.id
              if (!ownChild && !ownAgent) continue // negative control: never lint another plugin's work
              if (hook.ownsOutcomeContract && !ownChild && !ownAgent) continue
              const msgs = await ctx.session.context({ sessionID: sid }).catch(() => [])
              const { text } = readSessionResult(msgs as any[])
              await runClaudeHook(ctx, repoRoot, hook, {
                hook_event_name: "SubagentStop",
                opencode_event: t,
                session_id: receipt?.parentSessionID ?? null,
                agent_id: sid,
                agent_type: receipt?.agentID ?? info?.agent ?? null,
                last_assistant_message: text,
                cwd: receipt?.worktree ?? repoRoot,
                plugin_id: manifest.id,
                run_id: receipt?.runId ?? null,
                role: receipt?.role ?? null,
              })
            }
          } catch { /* stream closed */ }
        })()
      }

      await ctx.storage.set("host:status", {
        version: RUNTIME_VERSION, api: RUNTIME_API, id: manifest.id, repoRoot,
        workflow: !!manifest.workflow, boundaries,
      } as any).catch(() => {})

      if (cleanups.length) return () => cleanups.forEach((c) => c())
    },
  }
}

// --------------------------- workflow primitives ---------------------------

interface RunMeta {
  runId: string; pluginId: string; name?: string; parentSessionID?: string
  phases: Array<{ title: string; at: number }>
  logs: Array<{ message: string; at: number }>
  createdAt: number; status: "open" | "finished" | "cancelled"
}

function newRunId(): string {
  return `wf_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`
}

async function registerWorkflow(
  ctx: any, manifest: HostManifest, repoRoot: string,
  boundaries: string[], live: Map<string, Set<string>>,
) {
  const ns = manifest.id
  const tools: any[] = []

  const getRun = async (runId: string): Promise<RunMeta | undefined> =>
    (await ctx.storage.get(`wf:run:${runId}`).catch(() => undefined)) as RunMeta | undefined
  const putRun = async (run: RunMeta) => ctx.storage.set(`wf:run:${run.runId}`, run as any)
  const addReceipt = async (runId: string, r: any) => {
    const list = ((await ctx.storage.get(`wf:receipts:${runId}`).catch(() => undefined)) as any[]) ?? []
    list.push(r)
    await ctx.storage.set(`wf:receipts:${runId}`, list as any)
  }
  const registerLive = (runId: string, sid: string) => {
    if (!live.has(runId)) live.set(runId, new Set())
    live.get(runId)!.add(sid)
  }
  const clearLive = (runId: string, sid: string) => { live.get(runId)?.delete(sid) }
  const interruptRun = async (runId: string) => {
    const set = live.get(runId)
    if (!set) return 0
    let n = 0
    for (const sid of [...set]) { try { await ctx.session.interrupt({ sessionID: sid, resume: false }); n++ } catch { /* best effort */ } }
    return n
  }

  // start
  tools.push({
    name: "workflow_start",
    description: "Open a workflow run owned by this plugin. Returns a runId used by the other workflow primitives. Compose them with ordinary JavaScript in Code Mode.",
    input: { type: "object", properties: { name: { type: "string" }, parentSessionID: { type: "string" } }, required: [], additionalProperties: false },
    execute: async (input: any, tc: any) => {
      const runId = newRunId()
      const run: RunMeta = { runId, pluginId: manifest.id, name: input.name, parentSessionID: input.parentSessionID ?? tc.sessionID, phases: [], logs: [], createdAt: Date.now(), status: "open" }
      await putRun(run)
      return { content: JSON.stringify({ ok: true, runId, pluginId: manifest.id, parentSessionID: run.parentSessionID }) }
    },
  })

  // phase
  tools.push({
    name: "workflow_phase",
    description: "Record a named phase on a workflow run (durable).",
    input: { type: "object", properties: { runId: { type: "string" }, title: { type: "string" } }, required: ["runId", "title"], additionalProperties: false },
    execute: async (input: any) => {
      const run = await getRun(input.runId)
      if (!run || run.pluginId !== manifest.id) return { content: JSON.stringify({ ok: false, error: "unknown runId for this plugin" }) }
      run.phases.push({ title: input.title, at: Date.now() })
      await putRun(run)
      return { content: JSON.stringify({ ok: true, phases: run.phases.map((p) => p.title) }) }
    },
  })

  // log
  tools.push({
    name: "workflow_log",
    description: "Append a log line to a workflow run (durable).",
    input: { type: "object", properties: { runId: { type: "string" }, message: { type: "string" } }, required: ["runId", "message"], additionalProperties: false },
    execute: async (input: any) => {
      const run = await getRun(input.runId)
      if (!run || run.pluginId !== manifest.id) return { content: JSON.stringify({ ok: false, error: "unknown runId for this plugin" }) }
      run.logs.push({ message: input.message, at: Date.now() })
      await putRun(run)
      return { content: JSON.stringify({ ok: true }) }
    },
  })

  // status
  tools.push({
    name: "workflow_status",
    description: "Read a workflow run's durable record, receipts, and any completion-hook advisories.",
    input: { type: "object", properties: { runId: { type: "string" } }, required: ["runId"], additionalProperties: false },
    execute: async (input: any) => {
      const run = await getRun(input.runId)
      if (!run || run.pluginId !== manifest.id) return { content: JSON.stringify({ ok: false, error: "unknown runId for this plugin" }) }
      const receipts = ((await ctx.storage.get(`wf:receipts:${input.runId}`).catch(() => undefined)) as any[]) ?? []
      let hooks: any[] = []
      try {
        const scan = await ctx.storage.scan({ prefix: "hook:" })
        hooks = (scan?.entries ?? []).map((e: any) => ({ key: e.key, ...e.value }))
      } catch { /* best effort */ }
      return { content: JSON.stringify({ ok: true, run, receipts, hooks }) }
    },
  })

  // cancel
  tools.push({
    name: "workflow_cancel",
    description: "Cancel a workflow run: interrupt every live child it started. The run is never reported as ok afterwards.",
    input: { type: "object", properties: { runId: { type: "string" } }, required: ["runId"], additionalProperties: false },
    execute: async (input: any) => {
      const run = await getRun(input.runId)
      if (!run || run.pluginId !== manifest.id) return { content: JSON.stringify({ ok: false, error: "unknown runId for this plugin" }) }
      const n = await interruptRun(input.runId)
      run.status = "cancelled"
      await putRun(run)
      return { content: JSON.stringify({ ok: true, cancelled: true, interrupted: n }) }
    },
  })

  // finish
  tools.push({
    name: "workflow_finish",
    description: "Mark a workflow run finished.",
    input: { type: "object", properties: { runId: { type: "string" }, value: {} }, required: ["runId"], additionalProperties: false },
    execute: async (input: any) => {
      const run = await getRun(input.runId)
      if (!run || run.pluginId !== manifest.id) return { content: JSON.stringify({ ok: false, error: "unknown runId for this plugin" }) }
      run.status = "finished"
      await putRun(run)
      await ctx.storage.set(`wf:value:${input.runId}`, input.value ?? null as any).catch(() => {})
      return { content: JSON.stringify({ ok: true }) }
    },
  })

  // agent — the bounded executor primitive
  tools.push({
    name: "workflow_agent",
    description:
      "Run ONE bounded agent step in a fresh session and return its report plus the mechanical result. " +
      "The agent's words are testimony; `sessionOutcome`, `guard`, and `verify` are mechanical. " +
      "Options: agentType ('ns:name'), label, phase, schema (JSON Schema subset), model, timeoutMs, worktree, " +
      "guardPaths (snapshot+revert on touch), verifyCommand/verifyExpectExit (executed only when the repo manifest enables cage.verifyExec).",
    input: {
      type: "object",
      properties: {
        runId: { type: "string" }, prompt: { type: "string" }, label: { type: "string" },
        agentType: { type: "string" }, phase: { type: "string" }, schema: {}, model: { type: "string" },
        timeoutMs: { type: "number" }, worktree: { type: "boolean" },
        guardPaths: { type: "array", items: { type: "string" } },
        verifyCommand: { type: "string" }, verifyExpectExit: { type: "number" },
      },
      required: ["runId", "prompt"], additionalProperties: false,
    },
    execute: async (input: any, tc: any) => {
      const run = await getRun(input.runId)
      if (!run || run.pluginId !== manifest.id) {
        return { content: JSON.stringify({ ok: false, status: "executor-error", error: "unknown runId for this plugin" }) }
      }
      const label = input.label || input.agentType || "workflow agent"
      const startedAt = Date.now()
      let sessionID: string | undefined
      let worktreeDir: string | undefined
      let worktreeProjectID: string | undefined
      const onAbort = async () => { if (sessionID) { try { await ctx.session.interrupt({ sessionID, resume: false }) } catch { /* best effort */ } } }
      tc?.signal?.addEventListener?.("abort", onAbort, { once: true })
      try {
        if (input.agentType && input.schema) assertSupportedSchema(input.schema)

        let agentID: string | undefined = input.agentType
        if (agentID && agentID.includes(":")) { const [p, n] = agentID.split(":"); agentID = `${p}/${n}` }
        if (agentID && typeof ctx.agent.get === "function") {
          const known = await ctx.agent.get({ agentID }).catch(() => undefined)
          if (!known) throw new Error(`unknown agentType "${input.agentType}" (resolved "${agentID}")`)
        }

        const created = await ctx.session.create({
          title: (input.phase ? `[${input.phase}] ` : "") + label,
          agent: agentID,
        })
        sessionID = created.id
        registerLive(run.runId, sessionID)
        const receipt: any = {
          pluginId: manifest.id, runId: run.runId, parentSessionID: run.parentSessionID ?? tc.sessionID,
          sessionID, agentID: agentID ?? null, role: input.agentType ?? null, label,
          phase: input.phase ?? run.phases[run.phases.length - 1]?.title ?? null, startedAt,
        }
        await ctx.storage.set(`child:${sessionID}`, receipt as any)

        // model (tier alias -> provider/model[#variant]); honest fallback, recorded
        let modelNote: string | undefined
        if (input.model || agentID) {
          const alias = input.model
          let spec = alias ? (resolveTierModel(manifest, alias) ?? alias) : undefined
          if (!spec && agentID) {
            // derive tier from the generated agent's canonical model: alias if it looks like one
            spec = undefined
          }
          const parsed = spec ? parseModelString(spec) : null
          if (parsed) {
            try { await ctx.session.switchModel({ sessionID, model: parsed }) }
            catch {
              const base = { providerID: parsed.providerID, id: parsed.id }
              try { await ctx.session.switchModel({ sessionID, model: base }); modelNote = "variant rejected; used base model" }
              catch (e2: any) { modelNote = `model not applied (${e2?.message ?? e2}); inheriting`; boundaries.push(`model ${spec} rejected`) }
            }
            receipt.model = spec
          }
        }

        // worktree isolation
        if (input.worktree) {
          try {
            const projectID = tc?.projectID ?? (await ctx.session.get({ sessionID }).catch(() => undefined))?.projectID
            if (projectID) {
              const wt = await ctx.worktree.create({ projectID, name: `${ns}-${run.runId}` })
              worktreeDir = wt?.directory
              if (worktreeDir) { await ctx.session.move({ sessionID, directory: worktreeDir }); await ctx.worktree.refresh?.().catch?.(() => {}) }
              worktreeProjectID = projectID
            } else { receipt.worktree = null; boundaries.push("worktree requested but no project id") }
          } catch (e: any) { receipt.worktreeError = String(e); boundaries.push(`worktree failed: ${e?.message ?? e}`) }
        }
        const workRoot = worktreeDir ?? (await ctx.session.get({ sessionID }).catch(() => undefined))?.location?.directory ?? repoRoot

        // guard snapshot
        const guardPaths: string[] = (input.guardPaths ?? manifest.cage?.defaultProtected ?? []) as string[]
        const snap = guardPaths.length ? guardSnapshot(workRoot, guardPaths) : undefined

        // run
        const timeoutMs = typeof input.timeoutMs === "number" ? input.timeoutMs : undefined
        await ctx.session.prompt({ sessionID, text: input.prompt, delivery: "steer" })
        let waitErr: any
        const waitPromise = ctx.session.wait({ sessionID }).catch((e: any) => { waitErr = e; return undefined })
        let timedOut = false
        if (timeoutMs) {
          await Promise.race([
            waitPromise,
            new Promise((res) => setTimeout(() => { timedOut = true; res(undefined) }, timeoutMs)),
          ])
          if (timedOut) { try { await ctx.session.interrupt({ sessionID, resume: false }) } catch { /* best effort */ } }
        } else {
          await waitPromise
        }

        const msgs = await ctx.session.context({ sessionID }).catch(() => [])
        const { text, outcome } = readSessionResult(msgs as any[])
        receipt.sessionOutcome = outcome ?? null
        const claim = parseOutcomeClaim(text)

        // guard check + revert (mechanical)
        let guard: any
        if (snap) { guard = guardCheckAndRevert(snap); receipt.guard = guard }

        // verify (mechanical; only if the repo-committed manifest enables it)
        let verify: any
        if (input.verifyCommand) {
          if (manifest.cage?.verifyExec) {
            verify = await runVerify(workRoot, input.verifyCommand, typeof input.verifyExpectExit === "number" ? input.verifyExpectExit : 0, 60_000)
            receipt.verify = verify
          } else {
            verify = { command: input.verifyCommand, executed: false, note: "manifest did not enable cage.verifyExec" }
            receipt.verify = verify
          }
        }

        // structured output (real validation; a schema miss is a hard, reported status)
        let output: any
        let schemaError: string | undefined
        if (input.schema) {
          try {
            const parsed = extractStructured(text)
            validateSchema(parsed, input.schema)
            output = parsed
          } catch (e: any) { schemaError = e?.message ?? String(e) }
        }

        // derive the mechanical status — testimony never upgrades itself.
        // precedence: interruption > executor error > guard-touch > verify-failed > schema-error > claim
        let status = "done"
        if (timedOut) status = "interrupted"
        else if (outcome === "interrupted") status = "interrupted"
        else if (waitErr) status = "executor-error"
        else if (outcome && outcome !== "succeeded") status = "executor-error"
        if (status === "done" && guard?.touched) status = "guard-touch"
        if (status === "done" && verify?.executed && !verify.ok) status = "verify-failed"
        if (status === "done" && schemaError) status = "schema-error"
        if (status === "done" && claim.outcome === "handed-back") status = "handed-back"
        if (status === "done" && (claim.outcome === "too-big" || claim.outcome === "stuck")) status = "too-big"

        const ok = status === "done"
        const result = {
          ok, status, runId: run.runId, pluginId: manifest.id,
          childSessionID: sessionID, agentID: agentID ?? null, role: input.agentType ?? null,
          sessionOutcome: outcome ?? null, timedOut, schemaError: schemaError ?? null,
          report: text, claim, guard: guard ?? null, verify: verify ?? null,
          output: output ?? null, worktree: worktreeDir ?? null, model: receipt.model ?? null, modelNote: modelNote ?? null,
          elapsedMs: Date.now() - startedAt,
          testimony: "The agent's report and claim are testimony; status/guard/verify are mechanical.",
        }
        receipt.outcome = status; receipt.elapsedMs = result.elapsedMs
        await addReceipt(run.runId, receipt)
        return { content: JSON.stringify(result) }
      } catch (e: any) {
        if (sessionID) { try { await ctx.session.interrupt({ sessionID, resume: false }) } catch { /* best effort */ } }
        const receipt: any = {
          pluginId: manifest.id, runId: run.runId, parentSessionID: run.parentSessionID ?? tc.sessionID,
          sessionID: sessionID ?? null, role: input.agentType ?? null, label,
          outcome: "executor-error", error: e?.message ?? String(e), elapsedMs: Date.now() - startedAt,
        }
        try { await addReceipt(run.runId, receipt) } catch { /* best effort */ }
        return { content: JSON.stringify({ ok: false, status: "executor-error", error: e?.message ?? String(e), childSessionID: sessionID ?? null }) }
      } finally {
        tc?.signal?.removeEventListener?.("abort", onAbort)
        if (sessionID) clearLive(run.runId, sessionID)
        if (worktreeDir && worktreeProjectID) {
          try {
            await ctx.worktree.remove({ projectID: worktreeProjectID, directory: worktreeDir })
            await addReceipt(run.runId, { pluginId: manifest.id, runId: run.runId, sessionID, label, outcome: "worktree-removed", worktree: worktreeDir })
          } catch (e: any) {
            await addReceipt(run.runId, { pluginId: manifest.id, runId: run.runId, sessionID, label, outcome: "worktree-remove-failed", worktree: worktreeDir, error: String(e) }).catch(() => {})
          }
        }
      }
    },
  })

  await ctx.tool.transform((e: any) => {
    if (typeof e.namespace === "function") e.namespace({ name: ns, description: `${manifest.name ?? ns} workflow primitives (safe, no eval)` })
    for (const t of tools) {
      e.add({ ...t, options: { ...(t.options ?? {}), namespace: ns } })
    }
  })
}

// --------------------------- completion hooks ------------------------------

async function runClaudeHook(
  ctx: any, repoRoot: string, hook: HostHookDefinition,
  payload: Record<string, any>,
): Promise<void> {
  return new Promise((resolve) => {
    const command = hook.command.replace(/\{root\}/g, repoRoot)
    const child = spawn(command, { cwd: repoRoot, shell: true, env: { ...process.env, CLAUDE_PLUGIN_ROOT: repoRoot } })
    let stdout = "", stderr = ""
    const timer = setTimeout(() => child.kill("SIGKILL"), hook.timeoutMs ?? 15_000)
    child.stdin?.write(JSON.stringify(payload)); child.stdin?.end()
    child.stdout?.on("data", (d) => { stdout += d.toString() })
    child.stderr?.on("data", (d) => { stderr += d.toString() })
    const finish = async () => {
      clearTimeout(timer)
      let systemMessage: string | undefined
      try { const parsed = JSON.parse(stdout.trim()); if (parsed?.systemMessage) systemMessage = parsed.systemMessage } catch { /* non-JSON output */ }
      await ctx.storage.set(`hook:last:${payload.agent_id}`, { at: Date.now(), pluginId: payload.plugin_id, runId: payload.run_id, role: payload.role, systemMessage, raw: stdout.slice(0, 4000), stderr: stderr.slice(0, 1000) } as any).catch(() => {})
      if (stderr) await ctx.storage.set(`hook:error:${payload.agent_id}`, { at: Date.now(), stderr: stderr.slice(0, 1000) } as any).catch(() => {})
      resolve()
    }
    child.on("close", finish)
    child.on("error", finish)
  })
}
