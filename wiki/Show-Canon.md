# Show Canon — the multiverse map

← [Wiki Home](Home.md)

Every piece of grok-bitch starts as a Rick & Morty bit and has to earn its keep as real
engineering. This page is the map: each show element, the technique it became, and where it
lives. Two tests every entry passes — **it's a genuine engineering role/method**, and **the
character actually fits it**. Flavor-only ideas are listed at the bottom as *not built, on
purpose.*

---

## The cast — character → engineering role

| Show element | Engineering role | Lives in |
|---|---|---|
| **Rick Sanchez** | the 300-IQ orchestrator/handler that decomposes & verifies | [`rick`](The-Cast.md), [`/rick-mode`](Session-Modes.md#rick-mode) |
| **Morty** (= grok) | the caged, untrusted grunt executor | [`morty`](The-Cast.md) |
| **Mr. Meeseeks** | one bounded task, start to verified finish, then poof | [`mr-meeseeks`](The-Cast.md) |
| **Jerry** | trivial, cheap, low-stakes scraps — *and* the inverted floor-gauge: legibility read off what the dumbest reader can't grasp | [`jerry`](The-Cast.md), [`/jerry-test`](Session-Modes.md#jerry-test) |
| **Citadel Rick** | one orthogonal fan-out bearing / rabbit-hole dig | [`citadel-rick`](The-Cast.md) |
| **The Council of Ricks** | N-way **consensus** — triangulate, trust only the agreement | [`council-rick`](The-Cast.md), [`/council`](Session-Modes.md#council) |
| **Beth** | the surgeon — delicate, precise, minimal-incision fix | [`beth`](The-Cast.md) |
| **Space Beth** | the commander — high-stakes ops, revert staged first | [`space-beth`](The-Cast.md) |
| **Summer** | the capable generalist for ordinary multi-step work | [`summer`](The-Cast.md) |
| **Birdperson** | the principled, blunt, honest reviewer | [`birdperson`](The-Cast.md) |
| **Mr. Poopybutthole** | warm, accurate human-facing writing | [`mr-poopybutthole`](The-Cast.md) |
| **Evil Morty** | the cold, *directed* adversary who proves the break | [`evil-morty`](The-Cast.md) |
| **Randotron** | the *random*-search complement — seeded chaos & fuzz | [`randotron`](The-Cast.md) |
| **Mr. President** | the stakeholder — acceptance & release authority (SHIP/NO-SHIP) | [`mr-president`](The-Cast.md) |
| **Snowball** | the escalation / capability-uplift reasoner | [`snowball`](The-Cast.md) |
| **Dr. Xenon Bloom** (Anatomy Park) | the architecture cartographer — maps the body | [`dr-xenon-bloom`](The-Cast.md) |
| **Jessica** | the UX / human-empathy reviewer | [`jessica`](The-Cast.md) |
| **Diane** | the archivist — decision records, the keeper of *why* | [`diane`](The-Cast.md) |
| **Butter Robot** | the YAGNI / anti-over-engineering gate | [`butter-robot`](The-Cast.md) |
| **Noob-Noob** | the thankless recurring maintenance runner | [`noob-noob`](The-Cast.md) |

---

## The methods & commands — device/concept → technique

| Show element | Technique | Lives in |
|---|---|---|
| **Portal gun** | relocate, don't reinvent | Algorithm #3 |
| **Microverse battery** | encapsulate, and name the hidden cost | Algorithm #5 |
| **Operation Phoenix** | pre-stage the revert before the risky move | Algorithm #9 |
| **Time Crystal** | golden-value regression anchors — catch silent drift | `grok-bitch --anchor` |
| **Council of Ricks (in the cage)** | N-attempt consensus by content signature | `grok-bitch --consensus N` |
| **The Jerry test** (Jerry = the benchmark of average) | the **inverted instrument** — a legibility/complexity gauge read off how the floor-level reader *fails*, not how he succeeds (`/council`'s triangulation with the meaning flipped: Jerries agreeing = *obvious*, not *true*) | [`/jerry-test`](Session-Modes.md#jerry-test), [`jerry`](The-Cast.md) |
| **"I do science, not magic"** | empiricism — verify the path that actually ships | Algorithm #8 |
| **"Nobody exists on purpose"** | kill darlings without ego; ship the correct thing | Algorithm #10 |
| **Interdimensional Cable** | lateral idea search when the obvious path is bad | [`/adventure-mode`](Session-Modes.md#adventure-mode) |
| **The Detoxifier** (*Rest and Ricklaxation*) | Toxic Rick — perfectionism channeled as rigor (a darker rick-mode) | [`/detox`](Session-Modes.md#detox), [`toxic-rick`](The-Cast.md#the-mode-twin-agents) |
| **Director's commentary track** | the cast annotates the *source* in-voice, not just the chat — default on, droppable | [`/commentary`](Session-Modes.md#commentary) |
| **The Citadel** | parallel orthogonal fan-out + triangulation | [Reasoning Methods](Reasoning-Methods.md#the-citadel-of-ricks) |
| **Cronenberg world** | rehearse the disaster in a throwaway dimension | [`/cronenberg`](Session-Modes.md#cronenberg) |
| **Pickle Rick** | minimal-footprint constraint — do more with less | [`/pickle-rick`](Session-Modes.md#pickle-rick), [`pickle-rick`](The-Cast.md#the-mode-twin-agents) |
| **Blips & Chitz** | disposable prototyping / A-B sandbox | [`/blips-n-chitz`](Session-Modes.md#blips-n-chitz) |
| **The Vindicators** | preset ensemble squads for common job types | [`/family-mode`](Session-Modes.md#family-mode) |

---

## The backlog — mapped, not yet built

Honest about what's a real next step versus what's flavor:

- **Get Schwifty → a release ceremony.** A ship/release gate with a pre-flight checklist.
  Backlog; fun *and* functional.

**Shipped since (no longer backlog), both proven by hermetic fuzz scenarios:**
- **Time Crystal → regression anchors.** `grok-bitch run --anchor PATH` snapshots a golden
  value before the run and fails (exit 16) if it drifts — *even when `--verify` passed*.
  The silent regression a green check misses.
- **CLI `--consensus N`.** `grok-bitch run --consensus N` runs the task N independent times
  (reverting between), accepts only the agreement by content signature, and leaves the tree
  clean with the winning patch saved — the [`/council`](Session-Modes.md#council) discipline
  baked into the cage itself.

**Not built, on purpose (flavor-only):** a "Wubba Lubba Dub Dub" pep-talk mode, and
characters whose only mapping is a costume (e.g. Noob-Noob's *redundant* cousins). The bar
is a real role; a skin on an existing worker doesn't clear it.

---

## See also

- [The Cast](The-Cast.md) · [Session Modes](Session-Modes.md) ·
  [Reasoning Methods](Reasoning-Methods.md) · [The Iron Rule](The-Iron-Rule.md)
