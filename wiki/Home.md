# grok-bitch — Wiki

The full guide to **grok-bitch**: a Rick & Morty multi-agent orchestrator for Claude
Code, built on a deterministic safety cage.

This is the manual. The [README](../README.md) is the quick tour; everything here is
the long version.

---

## Pages

| Page | What's in it |
|------|--------------|
| **[The Safety Cage](The-Safety-Cage.md)** | The 6-layer containment model, the guard+revert guarantee, the Opus fallback, exit codes. The foundation everything else stands on. |
| **[The Cast](The-Cast.md)** | All 12 persona subagents — roles, model tiers, tools, show-accurate skills, and how each renders in the terminal. |
| **[Session Modes](Session-Modes.md)** | `/rick-mode` (become Rick), `/adventure-mode` (a goal → an episode run as a Workflow), `/family-mode` (a standing ensemble every turn). |
| **[Reasoning Methods](Reasoning-Methods.md)** | Rick's Algorithms, the research-grade *Lab Notebook*, and the *Citadel* fan-out / triangulation method. How Rick reasons and certifies. |
| **[The Iron Rule](The-Iron-Rule.md)** | *Maniac in the prose, surgeon in the facts* — the one contract that makes the whole bit safe to turn on. |
| **[CLI Reference](CLI-Reference.md)** | `grok-bitch` subcommands, every `run` option, profiles, guards, exit codes, and the JSON result schema. |
| **[FAQ](FAQ.md)** | Quick answers to the questions people actually ask. |

---

## The story — how a diss became an orchestrator

grok-bitch started as a bit.

The premise was pure shade: take Grok, treat it as an **untrusted, dim executor**, and
build a harness that hands it only the grunt work Claude doesn't want to spend rigor on.
Cage it so it can't hurt anything. Make it render *every* human-readable thing it writes
in the anxious, self-doubting voice of **Morty**. Stamp every single run with a
disclaimer that roasts it:

> DISCLAIMER: You are only as smart as your dumbest model: Morty (grok). Please double check the work.

And the cage was real engineering, not just a costume. An OS sandbox, hard resource
caps, byte-snapshot guard+revert on protected paths, a verify gate, a structured JSON
verdict on the way out. The safety never depended on Grok behaving — it came from the
harness. (See [The Safety Cage](The-Safety-Cage.md).)

Then the cast grew.

If Grok is Morty, then the thing *driving* Morty is **Rick** — a 300-IQ handler that
decomposes the work, cradles Morty through it, and never trusts his word. Once Rick
existed, the rest of the family followed: **Mr. Meeseeks** for one bounded job,
**Jerry** for the trivial scraps, **Beth** the surgeon, **Space Beth** the commander,
**Summer** the generalist, **Birdperson** the principled reviewer, **Mr. Poopybutthole**
for the warm docs, **Evil Morty** the cold directed red-teamer, **Randotron** the
seeded-chaos fuzzer who breaks plans with pure entropy, and a whole **Citadel** of Ricks
for fanning out across a wide problem. Twelve personas, each a genuine engineering role
with its own model tier and skills. (See [The Cast](The-Cast.md).)

Then came the modes. `/rick-mode` turns *your own* session into Rick.
`/adventure-mode` decomposes a goal into an episode and shoots it as a deterministic
multi-agent Workflow. `/family-mode` seats a standing ensemble that weighs in every
turn. (See [Session Modes](Session-Modes.md).)

And underneath the voice, the rigor kept getting sharper — Rick's show problem-solving
recast as an engineering method, then a research-grade *Lab Notebook* lifted from a real
proof shop, then *Citadel* triangulation for conclusions that have to survive being
attacked from several angles. (See [Reasoning Methods](Reasoning-Methods.md).)

Somewhere in there the joke quietly became a tool. The voice is paint. The rigor
underneath is surgical and enforced — that's the whole deal, and it's spelled out in
[The Iron Rule](The-Iron-Rule.md).

---

## How the pieces fit

```
              YOUR CLAUDE CODE SESSION
                       │
        ┌──────────────┼───────────────────────────┐
        │              │                            │
   /rick-mode    /adventure-mode              /family-mode
  (become Rick)  (goal → episode,          (standing ensemble,
        │         run as a Workflow)         every turn)
        │              │                            │
        └──────────────┴───────────────┬───────────┘
                                        │  delegates to
                                        ▼
                              ┌──────────────────────┐
                              │      THE CAST         │   12 persona subagents
                              │  rick · morty · beth ·│   each renders as
                              │  evil-morty·randotron·│   persona(task) in
                              │  citadel-rick · …     │   the terminal
                              └───────────┬──────────┘
                                          │  the grunt-work hands
                                          │  (morty, rick) drive…
                                          ▼
                              ┌──────────────────────┐
                              │   THE grok-bitch CLI  │   the deterministic cage
                              │  sandbox · guard+     │   → JSON verdict + exit code
                              │  revert · caps · verify│
                              └───────────┬──────────┘
                                          ▼
                                grok-build  (or the Opus fallback)
```

The cage is the floor. The cast stands on it. The modes orchestrate the cast. Rigor is
enforced top to bottom; the personas are the part you see.

---

## Publishing this as a GitHub Wiki

This `wiki/` folder is browsable as-is on GitHub and locally — every link is a relative
`.md` path. To publish it as the repository's actual GitHub **Wiki** (the separate
`<repo>.wiki.git`), copy these pages in and rename links from `Page.md` to `[[Page]]`
wiki-link form. Kept in-repo here so the docs version with the code.
