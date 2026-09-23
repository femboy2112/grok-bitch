// selftest.mjs — deterministic tests for the shared adapter's pure functions.
// Run: node --experimental-strip-types opencode/host/selftest.mjs
import {
  parseFrontmatter,
  translateAgent,
  translateSkill,
  validateSchema,
  extractStructured,
  expandArguments,
  tokenizeArgs,
  SchemaError,
} from "./runtime.ts"

let pass = 0
const fails = []
const ok = (name, cond) => { if (cond) pass++; else fails.push(name) }
const throws = (fn) => { try { fn(); return false } catch { return true } }

// --- frontmatter ---
ok("no frontmatter -> body intact", parseFrontmatter("hello").body === "hello")
ok("unterminated frontmatter is not frontmatter", parseFrontmatter("---\nname: x\nbody").data.name === undefined)
const fm = parseFrontmatter('---\ndescription: "A: b"\nmodel: opus\n---\nBODY')
ok("quoted value with colon", fm.data.description === "A: b")
ok("plain value", fm.data.model === "opus")
ok("body extracted", fm.body.includes("BODY"))

// --- agent translation ---
const agent = translateAgent(
  "---\ndescription: Morty\ntools: Bash, Read, Grep\nmodel: haiku\neffort: high\ncolor: yellow\n---\nBody text",
  "/x/morty.md",
  { id: "g-b", name: "g-b", agentNamespace: "g-b", tiers: { haiku: "anthropic/claude-haiku-4-5" } },
)
ok("agent id namespaced", agent.id === "g-b/morty")
ok("tier + effort -> variant", agent.model === "anthropic/claude-haiku-4-5#high")
ok("color mapped to hex", agent.color === "#f5d90a")
ok("unlisted action denied", agent.permissions.some((p) => p.action === "edit" && p.effect === "deny"))
ok("listed action allowed", agent.permissions.some((p) => p.action === "shell" && p.effect === "allow"))
ok("no __boundaries leaked", agent.__boundaries === undefined || Array.isArray(agent.__boundaries))
const inherit = translateAgent("---\nmodel: inherit\n---\nB", "/x/a.md", { id: "p", name: "p" })
ok("model: inherit -> no model", inherit.model === undefined)
const noTools = translateAgent("---\ndescription: x\n---\nB", "/x/a.md", { id: "p", name: "p" })
ok("no tools -> broad allow", noTools.permissions[0].action === "*" && noTools.permissions[0].effect === "allow")

// --- skill translation ---
const skill = translateSkill("---\nname: S\ndescription: D\n---\nBODY", "/r/skills/the-x/SKILL.md")
ok("skill id from dir", skill.id === "the-x")
ok("skill uses path", skill.path === "/r/skills/the-x/SKILL.md")
ok("skill empty body skipped", translateSkill("---\nname: S\n---\n", "/r/skills/e/SKILL.md") === null)

// --- schema ---
ok("schema accepts valid", (() => { validateSchema({ a: 1 }, { type: "object", properties: { a: { type: "number" } }, required: ["a"] }); return true })())
ok("schema rejects missing", throws(() => validateSchema({}, { type: "object", required: ["a"] })))
ok("schema rejects wrong type", throws(() => validateSchema({ a: "x" }, { type: "object", properties: { a: { type: "number" } } })))
ok("schema additionalProperties false", throws(() => validateSchema({ a: 1, b: 2 }, { type: "object", properties: { a: {} }, additionalProperties: false })))

// --- structured extraction ---
ok("extract fenced", JSON.stringify(extractStructured('```json\n{"a":1}\n```')) === '{"a":1}')
ok("extract raw", JSON.stringify(extractStructured('{"a":2}')) === '{"a":2}')
ok("extract embedded", JSON.stringify(extractStructured('prose {"a":3} tail')) === '{"a":3}')
ok("extract rejects garbage", throws(() => extractStructured("no json here")))
ok("extract malformed json throws", throws(() => extractStructured("```json\n{not valid}\n```")))

// --- args ---
ok("tokenize quotes", JSON.stringify(tokenizeArgs('a "b c" d')) === '["a","b c","d"]')
ok("expand $ARGUMENTS", expandArguments("Run $ARGUMENTS now", "x y") === "Run x y now")
ok("expand positional", expandArguments("Do $1 then $2", 'one "two three"') === "Do one then two three")
ok("expand fallback appends", expandArguments("Explain.", "file.ts") === "Explain.\n\nfile.ts")

if (fails.length) {
  console.error(`adapter selftest: FAIL (${pass} passed, ${fails.length} failed)`)
  for (const f of fails) console.error("  - " + f)
  process.exit(1)
}
console.log(`adapter selftest: PASS (${pass} assertions)`)
