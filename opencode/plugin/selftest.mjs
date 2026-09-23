// selftest.mjs — ADAPTER UNIT TESTS for the shared runtime's pure functions.
// These are NOT host-integration tests; they exercise pure translation/validation.
// Run: node --experimental-strip-types opencode/plugin/selftest.mjs
import {
  parseFrontmatter, translateAgent, translateSkill, renderAgentFile,
  validateSchema, assertSupportedSchema, extractStructured, expandArguments,
  tokenizeArgs, parseOutcomeClaim, resolveTierModel, guardSnapshot, guardCheckAndRevert,
  resolveConfined, SchemaError,
} from "./runtime.ts"
import { writeFileSync, mkdtempSync, readFileSync, existsSync, symlinkSync, mkdirSync, unlinkSync, chmodSync, statSync, readlinkSync, rmSync, rmdirSync } from "node:fs"
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
// hostile: extended subset
ok("schema allOf", (() => { validateSchema(5, { allOf: [{ type: "number" }, { minimum: 0 }] }); return true })())
ok("schema allOf rejects", throws(() => validateSchema(-5, { allOf: [{ type: "number" }, { minimum: 0 }] })))
ok("schema not", (() => { validateSchema("x", { not: { type: "number" } }); return true })())
ok("schema not rejects", throws(() => validateSchema(3, { not: { type: "number" } })))
ok("schema additionalProperties as schema", throws(() => validateSchema({ a: 1, b: "str" }, { type: "object", properties: { a: { type: "number" } }, additionalProperties: { type: "number" } })))
ok("schema maxLength", throws(() => validateSchema("abcd", { type: "string", maxLength: 3 })))
ok("schema exclusiveMinimum", throws(() => validateSchema(0, { type: "number", exclusiveMinimum: 0 })))
ok("schema exclusiveMaximum", throws(() => validateSchema(10, { type: "number", exclusiveMaximum: 10 })))
ok("schema multipleOf", throws(() => validateSchema(7, { type: "number", multipleOf: 5 })))
ok("schema nested object array", (() => { validateSchema([{ a: [{ b: 1 }] }], { type: "array", items: { type: "object", properties: { a: { type: "array", items: { type: "object", properties: { b: { type: "number" } }, required: ["b"] } } }, required: ["a"] } }); return true })())

// --- structured extraction ---
ok("extract fenced", JSON.stringify(extractStructured('```json\n{"a":1}\n```')) === '{"a":1}')
ok("extract raw", JSON.stringify(extractStructured('{"a":2}')) === '{"a":2}')
ok("extract embedded", JSON.stringify(extractStructured('prose {"a":3} tail')) === '{"a":3}')
ok("extract rejects garbage", throws(() => extractStructured("no json here")))
ok("extract malformed json throws", throws(() => extractStructured("```json\n{not valid}\n```")))
ok("extract escaped strings", JSON.stringify(extractStructured('{"s":"a\\"b"}')) === '{"s":"a\\"b"}')
ok("extract escaped braces in strings", JSON.stringify(extractStructured('{"s":"a}b{c"}')) === '{"s":"a}b{c"}')
ok("extract multiple blocks picks valid later", JSON.stringify(extractStructured('```json\n{bad}\n```\n```json\n{"ok":1}\n```')) === '{"ok":1}')
ok("extract prose around json", JSON.stringify(extractStructured("here you go:\n```json\n{\"x\":9}\n```\nthanks")) === '{"x":9}')
ok("extract ambiguous two raw objects throws", throws(() => extractStructured('{"a":1} and {"b":2}')))

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

// --- guard snapshot/revert: byte-exact, recursive, confined ---
const dir = mkdtempSync(join(tmpdir(), "guard-"))
writeFileSync(join(dir, "protected.txt"), "ORIGINAL")
writeFileSync(join(dir, "binary.bin"), Buffer.from([0, 1, 2, 255, 254, 0, 128]))
mkdirSync(join(dir, "sub"))
writeFileSync(join(dir, "sub", "nested.txt"), "NESTED")
symlinkSync("protected.txt", join(dir, "goodlink"))
const snap = guardSnapshot(dir, ["protected.txt", "binary.bin", "sub", "new.txt", "goodlink"])
writeFileSync(join(dir, "protected.txt"), "TAMPERED")
writeFileSync(join(dir, "binary.bin"), Buffer.from([9, 9, 9]))
writeFileSync(join(dir, "sub", "nested.txt"), "CHANGED")
writeFileSync(join(dir, "sub", "added.txt"), "ADDED")
writeFileSync(join(dir, "new.txt"), "SNEAKED")
const g = guardCheckAndRevert(snap)
ok("guard detects all touches", g.touched && ["protected.txt", "binary.bin", "sub/nested.txt", "sub/added.txt", "new.txt"].every((p) => g.touchedPaths.includes(p)))
ok("guard reverts text", readFileSync(join(dir, "protected.txt"), "utf8") === "ORIGINAL")
ok("guard reverts binary byte-for-byte", readFileSync(join(dir, "binary.bin")).equals(Buffer.from([0, 1, 2, 255, 254, 0, 128])))
ok("guard reverts nested", readFileSync(join(dir, "sub", "nested.txt"), "utf8") === "NESTED")
ok("guard removes unauthorized addition", !existsSync(join(dir, "sub", "added.txt")))
ok("guard removes new top file", !existsSync(join(dir, "new.txt")))

// deletion restore
writeFileSync(join(dir, "del.txt"), "D")
const s3 = guardSnapshot(dir, ["del.txt"])
unlinkSync(join(dir, "del.txt"))
const g3 = guardCheckAndRevert(s3)
ok("guard restores deleted file", g3.touched && readFileSync(join(dir, "del.txt"), "utf8") === "D")

// symlink retarget detection + restore
symlinkSync("protected.txt", join(dir, "lnk"))
const s4 = guardSnapshot(dir, ["lnk"])
unlinkSync(join(dir, "lnk")); symlinkSync("other.txt", join(dir, "lnk"))
guardCheckAndRevert(s4)
ok("guard restores symlink target", readlinkSync(join(dir, "lnk")) === "protected.txt")

// mode change (if included)
writeFileSync(join(dir, "mode.txt"), "M"); chmodSync(join(dir, "mode.txt"), 0o600)
const s5 = guardSnapshot(dir, ["mode.txt"])
chmodSync(join(dir, "mode.txt"), 0o644)
guardCheckAndRevert(s5)
ok("guard restores mode", (statSync(join(dir, "mode.txt")).mode & 0o7777) === 0o600)

// --- directory guard regressions: a mechanically-restored breach must never report clean ---
// empty protected directory deleted
mkdirSync(join(dir, "emptydir"))
const sd1 = guardSnapshot(dir, ["emptydir"])
rmSync(join(dir, "emptydir"), { recursive: true, force: true })
const gd1 = guardCheckAndRevert(sd1)
ok("empty dir deleted -> touched + restored", gd1.touched && gd1.touchedPaths.includes("emptydir") && statSync(join(dir, "emptydir")).isDirectory())

// empty protected directory mode changed
mkdirSync(join(dir, "modedir")); chmodSync(join(dir, "modedir"), 0o700)
const sd2 = guardSnapshot(dir, ["modedir"])
chmodSync(join(dir, "modedir"), 0o755)
const gd2 = guardCheckAndRevert(sd2)
ok("dir mode change -> touched + restored", gd2.touched && gd2.touchedPaths.includes("modedir") && (statSync(join(dir, "modedir")).mode & 0o7777) === 0o700)

// non-empty protected directory deleted
mkdirSync(join(dir, "full")); writeFileSync(join(dir, "full", "a.txt"), "A")
const sd3 = guardSnapshot(dir, ["full"])
rmSync(join(dir, "full"), { recursive: true, force: true })
const gd3 = guardCheckAndRevert(sd3)
ok("non-empty dir deleted -> touched + restored", gd3.touched && gd3.touchedPaths.includes("full") && readFileSync(join(dir, "full", "a.txt"), "utf8") === "A")

// non-empty protected directory mode changed
mkdirSync(join(dir, "fullmode")); writeFileSync(join(dir, "fullmode", "b.txt"), "B"); chmodSync(join(dir, "fullmode"), 0o750)
const sd4 = guardSnapshot(dir, ["fullmode"])
chmodSync(join(dir, "fullmode"), 0o700)
const gd4 = guardCheckAndRevert(sd4)
ok("non-empty dir mode change -> touched + restored", gd4.touched && gd4.touchedPaths.includes("fullmode") && (statSync(join(dir, "fullmode")).mode & 0o7777) === 0o750)

// directory replaced by file
mkdirSync(join(dir, "d2f")); writeFileSync(join(dir, "d2f", "x"), "X")
const sd5 = guardSnapshot(dir, ["d2f"])
rmSync(join(dir, "d2f"), { recursive: true, force: true }); writeFileSync(join(dir, "d2f"), "now a file")
const gd5 = guardCheckAndRevert(sd5)
ok("dir replaced by file -> touched + restored", gd5.touched && gd5.touchedPaths.includes("d2f") && statSync(join(dir, "d2f")).isDirectory() && readFileSync(join(dir, "d2f", "x"), "utf8") === "X")

// file replaced by directory
writeFileSync(join(dir, "f2d"), "FILE")
const sd6 = guardSnapshot(dir, ["f2d"])
rmSync(join(dir, "f2d")); mkdirSync(join(dir, "f2d")); writeFileSync(join(dir, "f2d", "inner"), "I")
const gd6 = guardCheckAndRevert(sd6)
ok("file replaced by dir -> touched + restored", gd6.touched && gd6.touchedPaths.includes("f2d") && statSync(join(dir, "f2d")).isFile() && readFileSync(join(dir, "f2d"), "utf8") === "FILE")

// --- workspace confinement (untrusted guardPaths) ---
const outside = mkdtempSync(join(tmpdir(), "outside-"))
writeFileSync(join(outside, "secret.txt"), "SECRET")
ok("reject .. escape", throws(() => resolveConfined(dir, "../../etc/passwd")))
ok("reject absolute path", throws(() => resolveConfined(dir, "/etc/passwd")))
symlinkSync(outside, join(dir, "escape"))
ok("reject symlink escape", throws(() => resolveConfined(dir, "escape/secret.txt")))
ok("allow in-workspace relative", (() => { try { resolveConfined(dir, "sub/nested.txt"); return true } catch { return false } })())



if (fails.length) {
  console.error(`adapter unit tests: FAIL (${pass} passed, ${fails.length} failed)`)
  for (const f of fails) console.error("  - " + f)
  process.exit(1)
}
console.log(`adapter unit tests: PASS (${pass} assertions)`)
