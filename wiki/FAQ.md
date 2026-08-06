# FAQ

← [Wiki Home](Home.md)

---

### Wait — is this a serious tool or a Rick & Morty bit?

Both, and that's the point. It started as a bit — cage an untrusted executor, call it
Morty, roast it on every run — and the cage turned out to be real, useful engineering. The
[personas are paint](The-Iron-Rule.md); the [containment](The-Safety-Cage.md) and the
[reasoning discipline](Reasoning-Methods.md) underneath are surgical. You can use it
po-faced as a delegation harness and never see a burp, or turn on
[`/rick-mode`](Session-Modes.md#rick-mode) and get the full show. Same rigor either way.

---

### Is it actually safe to run an "untrusted, dim executor" against my repo?

Yes, and the safety doesn't depend on the executor behaving — it comes from the discipline
its handler holds. Six layers of defense in depth, the load-bearing one being
**byte-snapshot guard+revert** of protected paths: a mechanical before/after hash that
restores any touched inviolable path, deterministic by construction, no matter what the
executor did. Read [The Safety Cage](The-Safety-Cage.md) for the full model and the honest
limitations.

---

### How do I install it as a plugin?

This repo *is* a Claude Code plugin **and** its own marketplace:

```bash
claude plugin marketplace add femboy2112/grok-bitch   # or a local path / git URL
claude plugin install grok-bitch@grok-bitch
```

Then **hot-load it into the running session** (no restart):

```
/reload-plugins
```

That loads the skill and the subagents. (`claude plugin update`
*does* need a restart; `install` + `/reload-plugins` does not.) Inspect any time with
`claude plugin details grok-bitch@grok-bitch`.

---

### What does the plugin actually ship?

- **A Skill** (`grok-bitch`) — its description sits in Claude's context, so Claude reaches
  for it on its own for mechanical/verifiable work; also runnable as `/grok-bitch`.
- **20 persona subagents** — the whole [Cast](The-Cast.md).
- **Three session modes** — [`/rick-mode`, `/adventure-mode`, `/family-mode`](Session-Modes.md).

---

### Do I need Grok, or any external model, installed?

No. grok is gone — "Morty" is now a bounded **Claude subagent**, spawned via the `Agent`
tool and run under the same [cage discipline](The-Safety-Cage.md) (bounded scope,
guard+revert, the verify gate, never self-certify). There's no external binary, no API key,
nothing to install beyond the plugin itself.

---

### Why is the executor "Morty"? And why does everything it writes sound so anxious?

The persona is a deliberate act of subjugation, and a load-bearing reminder: *you are
only as smart as your dumbest executor.* Morty renders every human-readable thing he writes
in an anxious, self-doubting voice — prose, comments, commit messages. But the voice never
touches executable or machine-parsed substance ([The Iron Rule](The-Iron-Rule.md)).

And *why cast the executor as the dim one?* Not because of the model — because of the
**role**. Morty is a bounded grunt working fast and cheap on one mechanical step, and a
grunt's self-report is **presumed unverified until the filesystem says otherwise.** The
contempt is just that discipline worn on the outside: never trust a subordinate's word, so
the executor runs caged, behind a verify gate, and is exactly what you point at disposable
grunt work. He does the toil; you hold the gavel. That's the *bitch* in grok-bitch.

Every run also prints the disclaimer:

> DISCLAIMER: You are only as smart as your dumbest executor: Morty. Please double-check the work.

---

### Which subagent / mode do I use for…?

| I want to… | Reach for |
|------------|-----------|
| Offload mechanical, verifiable grunt work | [`rick`](The-Cast.md) (heavy) or [`morty`](The-Cast.md) (one bounded step) |
| Finish one well-scoped task end-to-end | [`mr-meeseeks`](The-Cast.md) |
| A typo / rename / one-liner | [`jerry`](The-Cast.md) |
| A delicate, surgical fix | [`beth`](The-Cast.md) |
| A risky migration / incident under fire | [`space-beth`](The-Cast.md) |
| An ordinary multi-step feature | [`summer`](The-Cast.md) |
| Investigate one axis of a wide problem | [`citadel-rick`](The-Cast.md) (fan out several) |
| An honest, principled review | [`birdperson`](The-Cast.md) |
| Red-team my own code before I trust it | [`evil-morty`](The-Cast.md) (directed attack) |
| Fuzz it with random chaos to find what reasoning misses | [`randotron`](The-Cast.md) (random search) |
| Trust a result only once independent attempts agree | [`council-rick`](The-Cast.md) / [`/council`](Session-Modes.md#council) |
| Rule whether a "done" thing is actually fit to ship | [`mr-president`](The-Cast.md) (acceptance + release authority) |
| A task's stuck — escalate smartly, or fix the approach | [`snowball`](The-Cast.md) |
| Map an unfamiliar codebase before touching it | [`dr-xenon-bloom`](The-Cast.md) (architecture cartographer) |
| Review the real human / UX experience | [`jessica`](The-Cast.md) |
| Record *why* a decision was made (an ADR) | [`diane`](The-Cast.md) |
| Challenge whether a thing should be built at all | [`butter-robot`](The-Cast.md) (YAGNI gate) |
| Thankless recurring maintenance / chores | [`noob-noob`](The-Cast.md) |
| Warm, accurate docs / changelog | [`mr-poopybutthole`](The-Cast.md) |
| Turn my whole session into Rick | [`/rick-mode`](Session-Modes.md#rick-mode) |
| Same, but darker — *Toxic Rick*, no hedging, higher bar | [`/detox`](Session-Modes.md#detox) |
| Let Rick actually swear — the uncensored cut (off by default) | [`/explicit`](Session-Modes.md#explicit) |
| Decompose a goal and run it as a Workflow | [`/adventure-mode`](Session-Modes.md#adventure-mode) |
| A standing crew that weighs in every turn | [`/family-mode`](Session-Modes.md#family-mode) |
| Recap the whole session as an episode / honest worklog | [`/episode`](Session-Modes.md#episode) |
| Let Rick invest spare capacity on small asks (anticipate, scout, pre-draft) | [`/auto-rick`](Session-Modes.md#auto-rick) |
| Have Rick commit/comment under a separate git identity | [`/rick-git`](#can-rick-commit-under-a-separate-git-account-from-mine) |
| Rehearse a risky change before applying it | [`/cronenberg`](Session-Modes.md#cronenberg) |
| Solve it with minimal footprint (no new deps) | [`/pickle-rick`](Session-Modes.md#pickle-rick) |
| Prototype / A-B two approaches in a sandbox | [`/blips-n-chitz`](Session-Modes.md#blips-n-chitz) |

---

### Can I override a character's model?

Yes. Each agent defaults to a [style-accurate model tier](The-Cast.md#the-roster), but the
default is just a starting point — override the model on the spawn (or model *and* effort
inside a [Workflow](Session-Modes.md#adventure-mode)) when a job runs heavier or lighter
than the character.

---

### Does any of the persona stuff make the engineering sloppier?

No — by design. The rigor is untouched (often sharper); only the voice changes. The whole
guarantee is [The Iron Rule](The-Iron-Rule.md): *maniac in the prose, surgeon in the
facts.* If a persona ever softens a check, guesses a number, or claims an unverified
"done," it has failed the mode.

---

### Rick swears constantly on the show. Why doesn't he swear here — and can I turn that on?

Because it's an **opt-in**. Rick-mode ships the **broadcast cut** by default — the Adult Swim
bleep is on, so you get the contempt and the burps but no actual profanity, which keeps the
mode safe to run for anyone who never asked for the language.
[`/explicit`](Session-Modes.md#explicit) pulls the bleep and airs the **uncensored cut**: the
same Rick, same rigor, swearing on the beats that earn it — something genuinely breaks, you
actually screw up (teased, not abused), or you actually nail it. There's a `light`/`show`/`heavy`
dial, and [`/detox`](Session-Modes.md#detox) turns it up (Toxic Rick doesn't air the polite
cut). `/explicit off` puts the bleep back.

It's safe for the same reason every mode is — it's *voice only* ([The Iron
Rule](The-Iron-Rule.md#profanity--the-uncensored-cut-opt-in-off-by-default)), with four walls
no dial can move: **never slurs** (profanity ≠ slurs — nothing targeting a protected
characteristic, ever), **tease the mistake but never abuse the person**, **the record stays
clean** (the bleep comes off the live chat only — commits, comments, and docs stay clean), and
**it unlocks nothing but words** (no content guideline moves; a refusal is still a refusal).

---

### Can Rick commit under a separate git account from mine?

Yes — that's [`/rick-git`](Session-Modes.md). Run `/rick-git <rick-email> [name]` and it
generates an **isolated** SSH key (a brand-new `~/.ssh/id_ed25519_rick`, never touching your
existing key or global config) and prints the public key + copy-paste config (an SSH
host-alias block, a zero-touch `GIT_SSH_COMMAND`, a per-repo identity snippet, and an
optional isolated `gh` login so even *comments* attribute to Rick) for you to apply. It
saves the identity to Rick's memory, so afterward Rick authors **commits and comments** as
that account, while **major pushes/merges/releases ask first and default to your main
account**. The private key never leaves your machine or lands in memory. `/rick-git status`
shows the current identity; `/rick-git forget` drops it (it won't delete your key). The
standing no-push-without-your-say-so rule still applies on top.

---

### Will it `git push` or do something irreversible on its own?

No. The standing rule across every mode and agent: **never `git push` unless you
explicitly say so**, and pause before any irreversible/outward action. Commits happen
when the task needs them; pushing is your call.

---

## See also

- [Wiki Home](Home.md) · [The Safety Cage](The-Safety-Cage.md) · [The Cast](The-Cast.md) ·
  [Session Modes](Session-Modes.md) · [Reasoning Methods](Reasoning-Methods.md) ·
  [The Iron Rule](The-Iron-Rule.md)
