// selftest.mjs — ADAPTER UNIT TESTS for the shared runtime's pure functions.
// These are NOT host-integration tests; they exercise pure translation/validation.
// Run: node --experimental-strip-types opencode/plugin/selftest.mjs
import {
  parseFrontmatter, translateAgent, translateSkill, renderAgentFile,
  validateSchema, assertSupportedSchema, extractStructured, expandArguments,
  tokenizeArgs, parseOutcomeClaim, resolveTierModel, guardSnapshot, guardCheckAndRevert,
  SchemaError,
} from "./runtime.ts"
import { writeFileSync, mkdtempSync, readFileSync, existsSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"

let pass = 0
const fails = []
const ok = (name, cond) => { if (cond) pass++; else fails.push(name) }
const throws = (fn) => { try { fn(); return false } catch { return true } }

// --- frontmatter ---
ok("no frontmatter -> body intact", parseFrontmatter("hello").body === "hello")
ok("unterminated frontmatter ignored", parseFrontmatter("---\nname: x\nbody").data.name === undefined)
const fm = parseFrontmatter('---\ndescription: "A: b"\nmodel: opus\n---\nBODY')
ok("quoted value with colon", fm.data.description === "A: b")
ok("plain value", fm.data.model === "opus")
ok("body extracted", fm.body.includes("BODY"))

// --- agent translation: CLOSED allowlist ---
const agent = translateAgent(
  "---\ndescription: Morty\ntools: Bash, Read, Grep, TodoWrite\nmodel: haiku\neffort: high\ncolor: yellow\n---\nBody",
  "/x/morty.md",
  { id: "gb", name: "gb", agentNamespace: "gb" },
)
ok("agent id namespaced", agent.id === "gb/morty")
ok("closed allowlist denies all first", agent.permissions[0].action === "*" && agent.permissions[0].effect === "deny")
ok("listed action allowed", agent.permissions.some((p) => p.action === "shell" && p.effect === "allow"))
ok("unlisted action never granted", !agent.permissions.some((p) => p.action === "edit"))
ok("TodoWrite NOT mapped to edit", !agent.permissions.some((p) => p.action === "edit"))
ok("TodoWrite recorded as boundary", agent.__boundaries.some((b) => b.includes("TodoWrite")))
ok("subagent not granted when Agent absent", !agent.permissions.some((p) => p.action === "subagent"))
const withAgent = translateAgent("---\ntools: Agent, Read\n---\nB", "/x/a.md", { id: "gb", name: "gb", agentNamespace: "gb" })
ok("Agent -> subagent granted", withAgent.permissions.some((p) => p.action === "subagent" && p.effect === "allow"))
const noTools = translateAgent("---\ndescription: x\n---\nB", "/x/a.md", { id: "p", name: "p" })
ok("no tools -> broad allow (canonical had none)", noTools.permissions[0].effect === "allow" && noTools.permissions[0].action === "*")
ok("model alias carried, not a machine model", agent.modelAlias === "haiku" && !("model" in agent))

// rendered file is portable and closed
const rendered = renderAgentFile(agent)
ok("rendered has no machine model", !/\nmodel:/.test(rendered))
ok("rendered carries deny-first", /effect: "deny"/.test(rendered))

// --- skill translation (authoritative contract uses path) ---
const skill = translateSkill("---\nname: S\ndescription: D\n---\nBODY", "/r/skills/the-x/SKILL.md")
ok("skill id from dir", skill.id === "the-x")
ok("skill uses path", skill.path === "/r/skills/the-x/SKILL.md")
ok("skill has content", skill.content === "BODY")
ok("skill empty body skipped", translateSkill("---\nname: S\n---\n", "/r/skills/e/SKILL.md") === null)

// --- schema: supported subset + explicit rejection ---
ok("schema accepts valid", (() => { validateSchema({ a: 1 }, { type: "object", properties: { a: { type: "number" } }, required: ["a"] }); return true })())
ok("schema rejects missing", throws(() => validateSchema({}, { type: "object", required: ["a"] })))
ok("schema rejects wrong type", throws(() => validateSchema({ a: "x" }, { type: "object", properties: { a: { type: "number" } } })))
ok("schema additionalProperties false", throws(() => validateSchema({ a: 1, b: 2 }, { type: "object", properties: { a: {} }, additionalProperties: false })))
ok("schema oneOf", (() => { validateSchema(2, { oneOf: [{ type: "number", minimum: 0 }, { type: "string" }] }); return true })())
ok("schema oneOf rejects multiple", throws(() => validateSchema(2, { oneOf: [{ type: "number" }, { minimum: 0 }] })))
ok("schema anyOf", (() => { validateSchema("x", { anyOf: [{ type: "number" }, { type: "string" }] }); return true })())
ok("schema nested arrays", (() => { validateSchema([{ n: 1 }], { type: "array", items: { type: "object", properties: { n: { type: "number" } }, required: ["n"] } }); return true })())
ok("schema minLength", throws(() => validateSchema("a", { type: "string", minLength: 3 })))
ok("schema rejects unknown keyword", throws(() => assertSupportedSchema({ type: "object", unevaluatedProperties: false })))
ok("schema rejects unknown nested keyword", throws(() => assertSupportedSchema({ properties: { a: { type: "string", format: "email" } } })))
ok("schema allows known keywords", (() => { assertSupportedSchema({ type: "object", properties: { a: { type: "string", minLength: 1 } }, required: ["a"], additionalProperties: false }); return true })())

// --- structured extraction ---
ok("extract fenced", JSON.stringify(extractStructured('```json\n{"a":1}\n```')) === '{"a":1}')
ok("extract raw", JSON.stringify(extractStructured('{"a":2}')) === '{"a":2}')
ok("extract embedded", JSON.stringify(extractStructured('prose {"a":3} tail')) === '{"a":3}')
ok("extract rejects garbage", throws(() => extractStructured("no json here")))
ok("extract malformed json throws", throws(() => extractStructured("```json\n{not valid}\n```")))
ok("extract escaped strings", JSON.stringify(extractStructured('{"s":"a\\"b"}')) === '{"s":"a\\"b"}')

// --- args ---
ok("tokenize quotes", JSON.stringify(tokenizeArgs('a "b c" d')) === '["a","b c","d"]')
ok("expand $ARGUMENTS", expandArguments("Run $ARGUMENTS now", "x y") === "Run x y now")
ok("expand positional", expandArguments("Do $1 then $2", 'one "two three"') === "Do one then two three")
ok("expand fallback appends", expandArguments("Explain.", "file.ts") === "Explain.\n\nfile.ts")

// --- outcome claim parser (testimony) ---
const claim = parseOutcomeClaim("prose\n```outcome\noutcome: handed-back\nlabel: n/a\ndissent: too big\nopen-debts: 2\n```")
ok("claim outcome parsed", claim.outcome === "handed-back")
ok("claim dissent parsed", claim.dissent === "too big")
ok("claim debts parsed", claim.openDebts === 2)

// --- tiers ---
ok("alias resolves", resolveTierModel({ tiers: { opus: "p/o" }, agentNamespace: "x" }, "opus") === "p/o")
ok("role resolves", resolveTierModel({ tiers: { "reasoning-heavy": "p/r" }, agentNamespace: "x" }, "opus") === "p/r")
ok("unset inherits", resolveTierModel({ tiers: {}, agentNamespace: "x" }, "opus") === undefined)

// --- guard snapshot/revert ---
const dir = mkdtempSync(join(tmpdir(), "guard-"))
writeFileSync(join(dir, "protected.txt"), "ORIGINAL")
const snap = guardSnapshot(dir, ["protected.txt", "new.txt"])
writeFileSync(join(dir, "protected.txt"), "TAMPERED")
writeFileSync(join(dir, "new.txt"), "SNEAKED")
const g = guardCheckAndRevert(snap)
ok("guard detects touch", g.touched && g.touchedPaths.includes("protected.txt") && g.touchedPaths.includes("new.txt"))
ok("guard reverts content", readFileSync(join(dir, "protected.txt"), "utf8") === "ORIGINAL")
ok("guard removes new file", !existsSync(join(dir, "new.txt")))

if (fails.length) {
  console.error(`adapter unit tests: FAIL (${pass} passed, ${fails.length} failed)`)
  for (const f of fails) console.error("  - " + f)
  process.exit(1)
}
console.log(`adapter unit tests: PASS (${pass} assertions)`)
