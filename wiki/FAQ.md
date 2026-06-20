# FAQ

← [Wiki Home](Home.md)

---

### Wait — is this a serious tool or a Rick & Morty bit?

Both, and that's the point. It started as a bit (cage Grok, call it Morty, roast it on
every run) and the cage turned out to be real, useful engineering. The
[personas are paint](The-Iron-Rule.md); the [containment](The-Safety-Cage.md) and the
[reasoning discipline](Reasoning-Methods.md) underneath are surgical. You can use it
po-faced as a delegation harness and never see a burp, or turn on
[`/rick-mode`](Session-Modes.md#rick-mode) and get the full show. Same rigor either way.

---

### Is it actually safe to run an "untrusted, dim executor" against my repo?

Yes, and the safety doesn't depend on the executor behaving — it comes from the harness.
Six layers of defense in depth, the load-bearing one being **byte-snapshot guard+revert**
of protected paths (deterministic, kernel-independent, and proven by a hermetic fuzz
suite). Read [The Safety Cage](The-Safety-Cage.md) for the full model and the honest
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

That loads the skill, the subagents, and the `bin/` onto `PATH`. (`claude plugin update`
*does* need a restart; `install` + `/reload-plugins` does not.) Inspect any time with
`claude plugin details grok-bitch@grok-bitch`.

---

### What does the plugin actually ship?

- **A Skill** (`grok-bitch`) — its description sits in Claude's context, so Claude reaches
  for it on its own for mechanical/verifiable work; also runnable as `/grok-bitch`. It
  pre-approves `Bash(grok-bitch:*)`.
- **12 persona subagents** — the whole [Cast](The-Cast.md).
- **Three session modes** — [`/rick-mode`, `/adventure-mode`, `/family-mode`](Session-Modes.md).
- **The `grok-bitch` CLI** on `PATH` via the plugin's `bin/`. See the
  [CLI Reference](CLI-Reference.md).

---

### Do I need Grok installed?

No. If the `grok` binary is missing or out of usage, "Morty" falls back to **Claude
(`opus`/`medium`)** through the *exact same cage*. `grok-bitch doctor` stays **READY** on
the fallback. Details: [the Opus
fallback](The-Safety-Cage.md#the-opus-fallback--when-grok-is-unavailable).

---

### Why is grok "Morty"? And why does everything it writes sound so anxious?

The persona is a deliberate act of subjugation, and a load-bearing reminder: *you are
only as smart as your dumbest model.* grok renders every human-readable thing it writes
in Morty's anxious, self-doubting voice — prose, comments, commit messages. But the voice
never touches executable or machine-parsed substance ([The Iron Rule](The-Iron-Rule.md)).

And *why grok specifically* gets cast as the dim one? Because it has the one thing no
other model has, and it isn't a brain: **unfiltered access to the world's lowest common
denominator, X.com.** It didn't train on the library — it trained on the comment section.
That's the motive that powers the whole harness: a model marinated in the dumbest firehose
in any dimension is never taken at its word (so it runs caged, behind a verify gate) *and*
is exactly what you point at disposable grunt work. That's the *bitch* in grok-bitch.

Every run also prints the disclaimer:

> DISCLAIMER: You are only as smart as your dumbest model: Morty (grok). Please double check the work.

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
| Warm, accurate docs / changelog | [`mr-poopybutthole`](The-Cast.md) |
| Turn my whole session into Rick | [`/rick-mode`](Session-Modes.md#rick-mode) |
| Decompose a goal and run it as a Workflow | [`/adventure-mode`](Session-Modes.md#adventure-mode) |
| A standing crew that weighs in every turn | [`/family-mode`](Session-Modes.md#family-mode) |
| Recap the whole session as an episode / honest worklog | [`/episode`](Session-Modes.md#episode) |
| Let Rick invest spare capacity on small asks (anticipate, scout, pre-draft) | [`/auto-rick`](Session-Modes.md#auto-rick) |

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

### Will it `git push` or do something irreversible on its own?

No. The standing rule across every mode and agent: **never `git push` unless you
explicitly say so**, and pause before any irreversible/outward action. Commits happen
when the task needs them; pushing is your call.

---

## See also

- [Wiki Home](Home.md) · [The Safety Cage](The-Safety-Cage.md) · [The Cast](The-Cast.md) ·
  [Session Modes](Session-Modes.md) · [Reasoning Methods](Reasoning-Methods.md) ·
  [The Iron Rule](The-Iron-Rule.md) · [CLI Reference](CLI-Reference.md)
