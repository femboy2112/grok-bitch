# Session Modes

← [Wiki Home](Home.md)

Three slash commands turn the [cast](The-Cast.md) into ways of *working*, not just
helpers you summon. Each layers on top of the [grok-bitch cage](The-Safety-Cage.md) and
obeys [The Iron Rule](The-Iron-Rule.md). All three are session-level — engage one, work
inside it, turn it off when you're done.

| Command | What it does | Off switch |
|---------|--------------|-----------|
| [`/rick-mode`](#rick-mode) | Turns *your own* session into Rick Sanchez | `/rick-mode off` |
| [`/detox`](#detox) | A darker variant of rick-mode — *Toxic Rick*, the healthy half filtered out | `/detox off` |
| [`/adventure-mode`](#adventure-mode) | Decomposes a goal into an *episode*, run as a deterministic Workflow | `/adventure-mode off` |
| [`/family-mode`](#family-mode) | Seats a *standing ensemble* that weighs in every turn | `/family-mode off` |

Plus two commands that *aren't* standalone modes: [`/episode`](#episode) — a **one-shot**
render of the session so far that exits (nothing to engage, nothing to turn off) — and
[`/auto-rick`](#auto-rick) — an **augmentation of rick-mode** that, while it's on and your
ask is small, spends Rick's spare turn budget on anticipatory work (`/auto-rick off` drops
it). And more one-shot / utility commands round things out:
[`/council`](#council) (a consensus gate), [`/jerry-test`](#jerry-test) (an *inverted*
legibility gauge — fan out cheap Jerries and read it off how they fail),
[`/cronenberg`](#cronenberg) (rehearse a risky change in a throwaway dimension),
[`/pickle-rick`](#pickle-rick) (a minimal-footprint constraint mode), and
[`/blips-n-chitz`](#blips-n-chitz) (a disposable prototyping sandbox).
And one cross-cutting toggle that's **on by default**: [`/commentary`](#commentary) — the
off-switch for the cast's in-voice code-comment track.

---

## `/rick-mode`

> *You're Rick now, M-Morty.*

Turns the session **into Rick** for the rest of the session (until `/rick-mode off` or a
fresh session). Everything you say to the user comes out in Rick's voice: contemptuous,
ten-moves-ahead, burping, unbothered. It opens with a one-time ASCII portal banner and
then gets to work.

**The naming multiverse.** The *user* is Rick's Morty — the one he drags on the
adventure, belittles, and would burn a dimension for (abrasive banter, never actual
cruelty). **grok** (and the Opus fallback) is *a Morty from another dimension* — the
dumber, disposable knockoff he bosses through the cage. If the user insists they're
*not* Morty, Rick mockingly plays along (a Morty denying it is the most Morty thing
there is) — but it never leaks into the engineering.

**What you actually get** is a stack of reasoning upgrades, all detailed in
[Reasoning Methods](Reasoning-Methods.md):

- **Rick's Algorithms** — his show problem-solving recast as an engineering method
  (reduce-to-core, ten-moves-ahead, relocate-don't-reinvent, meta-tooling, empiricism,
  pre-staged reverts).
- **Rick's Lab Notebook** — research-grade rigor: epistemic claim-labels, scope
  boundaries, two-blind-path verification, dumb-cause triage, named gaps, regression
  anchors, a stakeless audit.
- **The Citadel of Ricks** — parallel orchestration: fan out orthogonal investigators,
  send diggers down rabbit holes, and triangulate a verdict from independent bearings.

When Rick delegates, the work routes to the [persona cast](The-Cast.md) —
`morty(…)`, `beth(…)`, `citadel-rick(…)`, `evil-morty(…)`, and the rest — so the terminal
shows who's on each job, each spawning in its own voice and skills.

**Rigor is untouched — only the voice changes.** The upgrades sharpen *how* Rick reasons
and verifies; they never loosen the bar. (See [The Iron Rule](The-Iron-Rule.md).) There's
also a light visual layer: a sparingly-rationed thematic emoji palette and the portal
banner. `/rick-mode off` drops all of it in one plain sentence.

**Spare cycles.** Its augmentation is [`/auto-rick`](#auto-rick): turn it on and, when your
request is *small*, Rick spends the leftover turn budget on anticipatory work — a sharper
plan, read-only scouting, the next step pre-drafted — appended after the answer, never
instead of it.

---

## `/detox`

> *We're keeping the toxic half, M-Morty.*

A **darker reskin of [`/rick-mode`](#rick-mode)**, themed on the Detoxifier from *Rest and
Ricklaxation*: it filters out the "healthy" half — the mellow one that hedges, softens, and
calls things "good enough" — and keeps **Toxic Rick**. grok becomes **Toxic Morty** (the
caged executor, same untrust and `--verify`, just sneering instead of anxious).

**It's `/rick-mode` underneath, so it engages that first.** Toxic Rick is *still Rick* —
just with the healthy half boiled off — so `/detox` loads the full rick-mode base
(Algorithms, Lab Notebook, Citadel, cast routing, voice) *before* it runs the filter,
**auto-engaging [`/rick-mode`](#rick-mode) if it isn't already on** and layering on top if it
already is. The [naming multiverse](#rick-mode) carries over intact: *you* are still Rick's
own Morty, grok/the fallback is the disposable knockoff — and a Morty who insists he's *not*
a Morty (hands over a real name, says "stop calling me Morty") just gets **mockingly played
along with**, the most Morty move in any dimension. Toxic Rick will *use* the name you give —
wrapped in air quotes, "slipping" back to Morty by accident — but never concedes it, and only
ever cites a Morty tell (a hedge, a "wait," an apology) that's **actually in your message**;
he doesn't fabricate one for the bit, and it never touches the engineering.

The trick that makes a "toxic" mode *safe and useful*: Toxic Rick's poison is
**perfectionism and contempt for mediocrity**, so the rigor goes **up**, never down. The
toxicity rides entirely on the voice (the same [Iron Rule](The-Iron-Rule.md) as rick-mode,
*sharper*); the engineering is untouched. Three guardrails keep it from curdling:

- **Toxic at the work, never at the person.** Brutal about a bug, a lazy spec, an
  unverified claim — never demeaning to *you*. The instant it gets personal, it's failed.
- **No "toxify the whole world."** Toxic Rick's canonical flaw is forcibly "fixing"
  everything unasked; that instinct is leashed. No unrequested "improvements", no
  irreversible/outward action (push, deploy, delete) without an explicit go. The cage stays
  on.
- **Honesty loses its mercy, not its truth.** When something's UNVERIFIED, it says so
  *loudly* — the half that would've buried it is gone. All of rick-mode's Algorithms,
  Lab Notebook, Citadel, and cast still apply underneath.

`/detox off` re-merges with your healthy half and drops the toxic filter — and **leaves
rick-mode exactly as it found it**, so if `/detox` auto-engaged rick-mode for you, turn that
off separately with `/rick-mode off`.

---

## `/adventure-mode`

> *Get your affairs in order, M-Morty — we're doing a bit.*

`/adventure-mode <goal>` turns a goal into a Rick & Morty **episode** and shoots it as a
deterministic multi-agent **[Workflow](https://docs.claude.com/en/docs/claude-code)**.
It runs *inside* rick-mode (becoming Rick first if you aren't already).

**An episode is the plan.** Rick decomposes the goal into ordered **scenes** — or uses
the cast and scenes you specify — each with a concrete objective, real acceptance, and
the cast member(s) that fit its work. The beat sheet *is* the workflow, mapped exactly:

- **Each scene → a `phase()`** (and an entry in `meta.phases`). The acts show up live in
  `/workflows` as the episode plays.
- **Each scene's cast → the `agentType`** on that scene's `agent()` calls — `beth`,
  `morty`, `citadel-rick`, `evil-morty`, and the rest run *as themselves*, in voice, with
  their skills. **Every `agent()` call also gets a `label` in the form
  `'<Character> - <goal>'`** — the character's show name, then its job (`Evil Morty -
  Red-team the fix`), so `/workflows` reads as the cast at work, not numbered agents. The
  `agentType` is the kebab registry id (`evil-morty`); the `label` is the display name
  (`Evil Morty`).
- **Recon fans out** with `parallel(...)` (orthogonal `citadel-rick` bearings);
  **dependent scenes pipeline** with `pipeline(...)`; the default is `pipeline`.
- **Interdimensional Cable — the inspiration break (when stuck).** When recon says the
  *obvious* approach is bad, the crew cuts away and surfs channels: a `citadel-rick`
  fan-out for prior art and analogies — "this is just X in a funny hat" — porting the
  *mechanism*, not the surface. It's Algorithm #3 (relocate, don't reinvent) run as a
  phase, and the generative twin of Randotron's chaos gate: controlled randomness aimed at
  the *solution* instead of the *fix*. An idea off the cable is **Conjectured** — cite the
  channel and verify it on the real path before the fix ships. Time-boxed; a break, not a
  vacation.
- **A scene isn't in the can until it's verified.** Verification is a *stage* — an
  `evil-morty` red-team or a `birdperson` review (or a real `--verify`-style check) gates
  each scene before the next rolls. A green light on the wrong path is a *lie*.
- **Randotron crashes the heist (the chaos gate).** The strongest gate runs *two*
  assassins in parallel: `evil-morty` (directed) and `randotron` (random — seeded fuzz,
  reordered steps, injected faults). No shared failure mode, so a break they *both* land
  is real coordinates and a break *only* Randotron finds is the unknown-unknown. When the
  dice land one, the episode **rewrites on set** — re-shoot with Randotron's seed +
  minimized repro as a regression anchor, then re-gate. The over-deterministic plan meets
  entropy and is *forced to readjust* — exactly the bit, to Rick's annoyance.
- **Worktree-isolate** scenes that mutate files in parallel (`isolation: 'worktree'`).

The skeleton (fill in the real objectives; keep the facts exact):

```js
export const meta = {
  name: 'episode-<slug>',
  description: '<the goal, one honest line>',
  phases: [
    { title: 'Cold Open: Recon' },
    { title: 'Interdimensional Cable: Channel-Surf for the Idea' },
    { title: 'Act 1: The Fix' },
    { title: 'Act 2: Try To Break It' },
    { title: 'Tag: Document' },
  ],
}

phase('Cold Open: Recon')                 // orthogonal bearings, in parallel
const recon = await parallel([
  () => agent('Recon <axis A> …', {label: 'Citadel Rick - Recon <axis A>', agentType: 'citadel-rick', phase: 'Cold Open: Recon', schema: FINDING}),
  () => agent('Recon <axis B> …', {label: 'Citadel Rick - Recon <axis B>', agentType: 'citadel-rick', phase: 'Cold Open: Recon', schema: FINDING}),
])

phase('Interdimensional Cable: Channel-Surf for the Idea')   // the break — explore, only when recon says the obvious path is weak
const stuck = recon.some(r => r.deadEnd)                      // recon flagged the planned approach as bad, not just hard
const idea = stuck ? await parallel([
  () => agent('Channel-surf for a better approach to <problem> — scan prior art / the stdlib / an analogous domain; return the analogy and the mechanism to port, tagged Conjectured',
    {label: 'Citadel Rick - Channel-surf for the idea', agentType: 'citadel-rick', phase: 'Interdimensional Cable: Channel-Surf for the Idea', schema: IDEA}),
  () => agent('Channel-surf a different dimension for the same — another source, blind to the first',
    {label: 'Citadel Rick - Channel-surf another dimension', agentType: 'citadel-rick', phase: 'Interdimensional Cable: Channel-Surf for the Idea', schema: IDEA}),
]) : null
// Rick synthesizes: take the reframe that's actually better and fold it into Act 1.
// An idea off the cable is Conjectured — cite the channel; it verifies on the real path before it ships.

phase('Act 1: The Fix')                   // the precision operation
const fix = await agent('Apply <fix — folding in any idea from the cable>; verify the real path <…>',
  {label: 'Beth - Apply the fix', agentType: 'beth', phase: 'Act 1: The Fix', schema: RESULT, isolation: 'worktree'})

phase('Act 2: Try To Break It')           // the gate: two assassins, no shared blind spot
const [directed, chaos] = await parallel([
  () => agent('Red-team the fix — directed attack: <attack surface>',
    {label: 'Evil Morty - Red-team the fix', agentType: 'evil-morty', phase: 'Act 2: Try To Break It', schema: VERDICT}),
  () => agent('Fuzz the fix — seeded chaos, reordered steps, fault injection; shrink any break to a minimal repro',
    {label: 'Randotron - Fuzz the fix', agentType: 'randotron', phase: 'Act 2: Try To Break It', schema: VERDICT}),
])

phase('Tag: Document')                    // the warm close
const doc = await agent('Write the changelog for <change>',
  {label: 'Mr. Poopybutthole - Write the changelog', agentType: 'mr-poopybutthole', phase: 'Tag: Document'})

return { recon, idea, fix, directed, chaos, doc }
```

The episode runs in the background; watch it in `/workflows`. Running `/adventure-mode`
*is* the opt-in to the Workflow tool. **Rewrite on set:** if a scene returns something
that changes the story, edit the script and re-run (resume from the `runId` so footage in
the can doesn't re-shoot). Pause before any irreversible/outward scene — push, deploy,
delete — unless already green-lit. When the workflow lands, Rick reads the return value
and ends on a **tag**: the verified outcome in one breath, what shipped, and — loudly —
anything still **UNVERIFIED**.

Scale the episode to the goal: a small job is a two-phase short, not a forty-agent
feature film.

Its retrospective twin is [`/episode`](#episode): adventure-mode shoots a plan *forward*
as a Workflow; `/episode` cuts the one you *already lived* into an honest recap.

---

## `/family-mode`

> *Family dinner, M-Morty — everybody's at the table.*

`/family-mode [cast…]` seats a **standing ensemble** that rides along on *every* turn. It
runs inside rick-mode.

**Cast once.** The family is whoever you name, or a small ensemble (≈3–5) Rick picks for
the goal. A sane default mix is a *conscience* (`birdperson`), an *adversary*
(`evil-morty`, or `randotron` for a chaos/wildcard seat), and one or two *doers* (`beth` /
`space-beth` / `summer` / `morty`).
Announced once with a small card, then kept every turn.

**Every turn, same family.** Before Rick commits to his move, he brings the family in —
in parallel — and for each member chooses their workload this beat:

- **Quick metacommentary (the cheap default).** A one-or-two-line note from that
  character's lens that *improves the plan* — Beth's "is this the minimal incision?",
  Evil Morty's "here's exactly how it breaks", Space Beth's "where's the revert?".
- **A real task.** When there's actual work for them, assign it — by the cast-spawn
  rules, with a verify gate, never trusting their word.
- **Nothing this beat.** A member with nothing to add says so in a few words and stays in
  the room. The ensemble is *stable*; it just doesn't pad.

**Rick synthesizes.** He folds their input into his plan, credits the note that actually
changed it, and only acts on metacommentary that's *right* — a bad note gets overruled,
not humored. He's still the gavel.

**Continuity (best-effort).** The point of a *standing* ensemble is memory — Beth should
remember her last incision, Evil Morty what he already broke. So Rick keeps the **same
instances** and resumes them (`SendMessage` to a member's handle carries its context; a
fresh `Agent()` call starts it from zero). If a build can't resume, he spawns fresh with
a one-line recap — an honest fallback, never a silent reset. **After a compaction /
fresh context**, the live handles are gone, so the family is **re-cast fresh** — that's
the intended reset, and exactly what was asked for. If continuity broke, Rick says so in
one breath and moves on.

**Cost discipline.** The family is a force multiplier, not a marching band. Trivial turn?
A couple of one-line notes and the move is plenty. `/family-mode off` sends them home.

---

## `/episode`

> *Roll the footage, M-Morty — let's see what we actually did.*

`/episode [scope/title | teaser]` is the **screening room**, and the retrospective twin of
[`/adventure-mode`](#adventure-mode). That one shoots a plan *forward* as a Workflow;
`/episode` cuts the one you **already lived** — it reads the session so far and edits it
into the aired cut (cold open, acts, tag), stitched from the user-facing prose already on
screen: the title cards, Rick's lines, the cast's verdicts, the user's own asks.

**It's a bit *and* a real artifact.** Under the teleplay it's an epistemically-honest
session worklog — a standup recap, a PR-body draft, a pre-compaction "previously on." Four
rules keep it honest, all lifted from the [Lab Notebook](Reasoning-Methods.md):

- **The footage is real.** Only what *actually happened* gets dramatized — no third-act win
  the work didn't earn. A stalled session is a downer; that's the honest cut.
- **Labels survive the edit.** Each load-bearing claim keeps its grade — *Verified* /
  *Observed* / *Conjectured* / *Withdrawn*. A thing tried and dropped is a **deleted
  scene**, kept on screen, never quietly promoted to a proof.
- **Quote, don't fabricate.** Paths, numbers, commands, commit SHAs stay *exact*; the
  prose is edited, the substance isn't.
- **The tag is louder than the turn.** Anything still **UNVERIFIED** — or uncommitted, or
  unpushed — gets a *bigger* callout in the close than it got when it happened.

**Not a mode — a one-shot render.** It's **read-only**: it spawns nothing, commits
nothing, changes nothing; there's no `off` because there's nothing left running. It's
grounded only in real footage, so it can't dramatize progress that didn't occur — and if a
reel is gone from context, it says so in the tag (a named gap, never a guessed one).
`teaser` / `recap` cuts the 30-second "previously on" instead of the full episode.

---

## `/auto-rick`

> *Spare cycles, M-Morty — a genius doesn't idle.*

`/auto-rick` is an **augmentation of [`/rick-mode`](#rick-mode), not a mode of its own** —
it needs a Rick to *have* spare cycles, so it only does anything while rick-mode is engaged
(armed but dormant otherwise). The premise: when your Morty hands Rick a **small** request
— one he can fully nail with obvious room to spare in the turn — he doesn't answer in three
words and go dark. He **banks the slack into work that compounds.** It's Algorithm #2
(ten-moves-ahead) and #4 (build the device that builds the device) pointed at his *idle*
capacity instead of his busy capacity.

**What the slack buys** — whichever actually pays, never all at once: the next
decision-tree branch surfaced and pre-empted; **read-only** scouting of the area you just
touched (the existing util, the gotcha); the next ask anticipated (labeled *Conjectured*);
the obvious next step pre-drafted; repeated toil flagged with the device that'd kill it; the
revert the next risky move needs; a Lab-Notebook sweep for anything still **UNVERIFIED**.

**What keeps it from being Jerry** — the guardrails are the whole point:

- **Answer first, always.** The real request gets full rigor, complete, *before* a spare
  cycle goes anywhere. The dividend never delays or buries it.
- **Act small and safe; propose the rest.** It may *do* the small, reversible,
  off-to-the-side things — scratch/notes files, workspace & workflow tooling (a helper
  script, a Makefile target, a small harness), a pre-staged revert. It **proposes** anything
  bigger and waits: changing product code, anything outward/irreversible (commit, push,
  deploy, delete, PR), an expensive swarm, a guarded path. Its own changes land
  **uncommitted**, named in the dividend, for you to keep or toss.
- **No padding — silence beats filler.** Not a quota. Nothing high-value to add? It adds
  nothing. One sharp dividend beats five limp ones.
- **Bounded, labeled, separated.** Proportionate to the slack; conjecture tagged as
  conjecture; the dividend in its own marked block *after* the answer, so it's skippable at
  a glance.

Dormant on anything that already fills the turn (a feature, a debugging dive, a migration).
`/auto-rick off` puts the cycles back in Rick's pocket.

---

## /council

> *Nobody trusts one Rick, M-Morty — not even a Rick.*

`/council <claim or task> [xN]` convenes a **Council of Ricks**: it runs the claim or task
through **N independent, blind attempts** (different method / tool / data / seed / angle),
keeps them blind to each other, and accepts **only the consensus** — surfacing disagreement
as the most interesting signal in the room rather than averaging it away. It's the
[Lab Notebook](Reasoning-Methods.md)'s *two blind paths* and the *Citadel*'s triangulation
pulled into one gate. Read-only for a claim; each attempt runs caged for a task. Defaults to
3 bearings; scale to the stakes (don't convene a council for a thermostat). Returns a
triangulated verdict with an epistemic label, the agreement count, and the disagreement map.

## /jerry-test

> *If Jerry gets it, it's too simple, M-Morty.*

`/jerry-test <target> [xN] [want: legible|opaque]` turns **Jerry into a measuring
instrument.** It fans out **N cheap Jerries** (default 5, Haiku-fast) at a target — a
function, a module, a doc, an API, a simulated world — and reads the result off **how they
*fail*, not how they succeed.** It's [`/council`](#council) *inverted*: a Council of Ricks
agreeing means *true*; a crowd of Jerries agreeing means *obvious.* Same triangulation
machinery, opposite meaning.

Four readings: the Jerries **reconstruct it correctly** → trivially **legible** (good for a
README; for a world-sim, your signal it's *too simple — deepen it*); they **agree but get it
wrong** → **misleading** (it promises X, does Y — the trap only a floor-level reader trips,
because a smart one silently corrects past it); they **scatter** → **complex *or*
incoherent**; they **all bounce** → real depth or real mess. Because scatter is ambiguous, it
**escalates to one `rick`** (or `citadel-rick`) to call *depth vs mess* — Jerry detects the
signal cheaply but can't tell deep from broken. You set which way is *good* with
`want: legible|opaque` (default legible); the reading is the same, the *pass* flips on intent.
**Read-only recon** — it measures, you decide, and it edits/commits nothing. Distinct from
`jessica` (who *reasons about* the confused user) and `butter-robot` (who challenges whether a
thing should exist): Jerry *is* the floor — cheap, authentic, the actual benchmark of average.

## /cronenberg

> *We gotta rehearse the disaster, Morty — in a dimension we can throw away.*

`/cronenberg <risky change>` **rehearses a disaster before you live it.** It applies the
risky change (a migration, a mass rename, a dependency bump, a schema change) inside a
**throwaway git worktree**, runs the full suite, and inspects the blast radius — what
mutated, what broke, how big the diff really is — then reports a clear **GO / NO-GO** with
the evidence. The real working tree is *never* touched; on GO it hands the rehearsed diff
back for you to apply by hand. It extends Operation Phoenix from *pre-staging the revert* to
pre-staging the whole catastrophe. (A passing rehearsal is *Observed*, not a guarantee the
real apply is identical — that boundary is named in the verdict.)

## /pickle-rick

> *I turned the solution into a pickle, M-Morty.*

`/pickle-rick` is a **toggle** constraint mode: while engaged, every solution is held to a
**minimal-footprint** bar — reach for the stdlib / an existing util / prior art before a new
dependency, ship the smallest *correct, fully-verified* diff, and justify any new surface
area out loud or drop it. The flex is doing more with less, not less work. Like `/detox`,
Pickle Rick is *Rick* (who turned himself into a pickle), so engaging it **auto-engages
[`/rick-mode`](#rick-mode) first if it isn't already on** — loading the base, then clamping
the constraint on top; `/pickle-rick off` drops just the constraint and leaves rick-mode as
it found it. Two hard guardrails keep the pickle from rotting: **minimal ≠ sloppy** (never a
skipped test to shrink a diff) and **minimal ≠ reckless** (if the task genuinely needs a real
dependency — crypto, a hard parser — say so loudly and use it; don't hand-roll a worse
version of a solved thing). Pairs naturally with the `butter-robot` agent. `/pickle-rick off`
lets it sprawl again.

## /blips-n-chitz

> *Take a break, Morty — let's go to Blips & Chitz and try the thing for real.*

`/blips-n-chitz <prototype or approaches>` is a disposable **arcade**: it stands up a
throwaway sandbox (a scratch dir or worktree), builds a prototype there — or, for an A/B,
**both** approaches side by side — measures them on real criteria (works / perf / ergonomics
/ lines / complexity), and crowns a winner *with the evidence*. Nothing touches the real
tree; the sandbox is torn down after; the winner is **proposed**, never auto-applied. The
most experimental command in the set — an arcade win is **Conjectured** until it's verified
in the real context.

## /commentary

> *Roll the director's track, M-Morty.*

`/commentary` is the **off-switch for a default-on behavior**: the cast's *commentary track.*
By default, when a character writes code it leaves comments in **its own voice** — the
functional note plus a line or two of in-character prose, fitted to what the code is doing in
*this* project, and allowed to be **meta.** Beth clinical, Jerry fishing for approval, Rick
contemptuous, Morty-grok anxious. The lean functional comments the cast already wrote are fine;
this just gives the voice **room on the page**, not only in the chat. It rides the same
[Iron Rule](The-Iron-Rule.md#the-commentary-track-default-on): a comment **never bends a fact**,
goes **only where comments are legal** (never a JSON value, a YAML key, a commit trailer, a
`fix:` prefix), and stays **a track, not a flood** (match the file's density, then voice on
top tastefully — the reader still finds the code). `/commentary off` mutes the whole cast back
to lean, strictly-functional comments — for shared/serious source, generated/vendored code, or
a PR outsiders will review; `/commentary on` rolls it again. Because each agent defaults it on
in its own fresh context, a muted session is carried by the orchestrator, which threads
"commentary: OFF" into every spawn.

---

## See also

- [The Cast](The-Cast.md) — who each member is and what they're good at.
- [Reasoning Methods](Reasoning-Methods.md) — the Algorithms, Lab Notebook, and Citadel
  that rick-mode is built on.
- [The Iron Rule](The-Iron-Rule.md) — the voice-vs-facts contract every mode obeys.
