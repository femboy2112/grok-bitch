# Mathematical Moves — a companion to the Truth-Seeking Audit

**Date:** 2026-09-02 · **Companion to:** `TRUTH-SEEKING-AUDIT.md`. The audit fixed the harness: what
persists, what certifies, which oracles count. This document is the other half — the moves the mind
makes *inside* that harness to turn a stuck problem into a moving one. Every move has a trigger, the
move itself, a micro-example that was executed for this document, the way it fails, and the label
its output may carry. It is a reach list, not a textbook.

**Method:** written solo, without bearings. Every micro-example marked `Observed` was run by
`mathematical-moves-verify.py` (sibling file; output quoted verbatim). Every literature claim is
marked `Disclosed[recalled]` and listed in §11 for citation-checking before it is allowed to carry
weight. The solo authorship is the document's main weakness and §11 says so.

**Vocabulary:** labels are the audit's typed forms. Move ids are stable (`R3`, `S2`, `U7`) so a
ledger row can cite the move that produced an idea. `Reach when` is the trigger; a move with no
trigger firing is not owed an attempt.

---

## 0. Reach table — read this when stuck

The stuck-state is the key. Find the row, try the moves in the order listed, log one line per
attempt (§1). If no row fits, the problem is not yet stated — go to G1 and state it with quantifiers.

| Stuck-state | Reach for, in order |
|---|---|
| I cannot even compute examples | U1 (small cases + instrument), U2 (specialize to the extreme), R7 (re-encode as matrix/graph/polynomial) |
| I have data but no pattern | R1 (transform), U1 (guess the form, PSLQ/OEIS), E1 (random model: what *should* the data look like?), U2 |
| I have a pattern but no proof | U7 (enumerate strategies, choose with a reason), S1/S2 (invariant/monovariant), U3 (strengthen the hypothesis), S3 (extremal), U5 (work backwards), R7 |
| A proof idea will not close | U4 (name the missing lemma, test it on small cases), U3, R2 (dualize), R4 (lift), G3 (which hypothesis is load-bearing?), S7 (local-to-global) |
| I do not know whether it is true | U8 (honest refutation with a structure theorem), E1 (model prediction), §8 (barrier check), U9 (change the question) |
| Everything hits the same wall | §8 (name the wall as a theorem about proof shapes), U7 (exclude the shapes it kills), U6 (analogy with a dictionary), U9 (climb one rung), U10 (tombstone and switch) |
| I need a bound, not an equality | R2 (dual certificate), S9 (positivity, Cauchy–Schwarz, SOS), E4 (averaging), E3 (dominant balance), E2 (scaling) |
| I need existence without construction | E4 (averaging), E1/E4 (probabilistic method), S4 (pigeonhole), S3 (extremal), S8 (dimension count) |
| I need termination or reachability | S2 (ranking function), S1 (invariant), C2 (rewrite tools), C4 (fixed points) |
| The proof is "done" and I do not trust it | G1 (quantifiers), G2 (type-check), G3 (minimal hypotheses), G4 (formal vs analytic), G5 (relay audit), G6 (machine-check) |
| The object is a program | C1–C6, then the mathematical moves apply to the program as an object |

Three rules of reaching:

1. **Ten before one.** List ten candidate moves with a one-line sketch each before pursuing any.
   The list is cheap and is itself an artifact; the first idea is rarely the best and always the
   most seductive.
2. **Cheapest falsifier first.** Order the list by the cost of the test that would kill each
   candidate, not by how promising it feels. A candidate with no conceivable falsifier is `Dark`.
3. **One line per attempt.** `move | idea | cheapest falsifier | result | label`. Unlogged attempts
   get re-walked; the audit's tombstone rule applies to ideas, not only to approaches.

---

## 1. Generation discipline

The audit found that the stack certifies far better than it generates. Generation is a discipline
with its own rules, not a mood.

- **Generate in the ledger, not in the head.** Candidates are rows. A row's `idea` field is one
  sentence; a candidate that cannot be stated in one sentence is two candidates or none.
- **Separate divergence from convergence.** During the ten-before-one pass nothing is criticized.
  Criticism is the *next* pass, and it starts with the cheapest falsifier, never with taste.
- **Compute before conjecturing, dwell before computing more.** This is the-euler-method's core and
  it is not repeated here; it is assumed. The moves in §2–§5 are what to do *with* the table.
- **A move gets one bounded attempt.** State the budget (minutes, or a number of probes) before
  starting. When it runs out, log the tombstone with a recurrence keyword and switch. Returning later
  is allowed; returning without reading the tombstone is not.
- **The label of a generated idea is `Conjectured[pays-off-if: …]` at birth.** Never higher. An idea
  that feels certain is the Poincaré case: the feeling is data about the author, not the theorem.

---

## 2. Representation moves — change what the object is

**R1 · Transform to where the hard operation is easy.**
*Reach when:* the object is defined by a recurrence, a convolution, a product, or a scaling law.
*Move:* pick the transform that turns the hard operation into addition or multiplication. Ordinary
generating function (convolution → product), exponential GF (labeled structures), Dirichlet series
(multiplicative structure → Euler product), Fourier (shifts and convolutions → multiplication),
logarithm (product → sum), Mellin (scaling → shift).
*Micro:* strings with no `11` have GF `(1+x)/(1−x−x²)`; the denominator *is* the recurrence, and
partial fractions give the closed form. `Observed[find_linear_recurrence → [1, 1]]` (see chain A).
*Fails when:* the transform is used outside its analytic domain. A formal identity in `Z[[x]]` is not
an equation at `x = 2` (G4).

**R2 · Dualize — solve for the certificate.**
*Reach when:* you want a bound, an optimality claim, or a proof that no solution exists.
*Move:* state the dual problem. Weak duality gives a certificate for free: any dual-feasible point is
a *proof* of a bound on the primal. Max-flow/min-cut, LP duality, Farkas, Lagrangian relaxation,
the minimax theorem are all the same move. A proof of "no solution" is usually a dual object.
*Micro:* to show a flow cannot exceed `c`, exhibit a cut of capacity `c`. The cut is the proof; no
argument about flows is needed. (Reasoning-only; the theorem is standard.)
*Fails when:* the problem is non-convex — then there is a duality gap, and weak duality is all you
get. That is still a bound, and still a certificate.

**R3 · Substitute to linearize or decouple.**
*Reach when:* a nonlinear recurrence, a product structure, or coupled equations.
*Move:* find the substitution under which the nonlinear thing becomes linear: logarithms for
products; `y = u′/u` for Riccati; `x + 1/x` for `a² − 2`; the eigenbasis for coupled linear systems;
`n = 2^k m` to split the 2-adic part from the odd part.
*Micro:* `a_{n+1} = a_n² − 2`, `a_0 = 3`, gives `3, 7, 47, 2207, 4870847`; with `x = (3+√5)/2` the
closed form `x^{2^n} + x^{−2^n}` matches every term to 12 digits.
`Observed[verify.py → [(3,'3.0'),(7,'7.0'),(47,'47.0'),(2207,'2207.0'),(4870847,'4870847.0')]]`
(this is the Lucas–Lehmer sequence).
*Fails when:* the substitution is not invertible on the domain you care about, so you prove the
theorem for the substituted object only.

**R4 · Lift — add a dimension, a parameter, or a completion.**
*Reach when:* the object resists in its native space; a symmetry is invisible; an integral or sum
has no handle.
*Move:* complexify (real integrals via contours), homogenize (affine → projective, where points at
infinity behave), add a parameter and differentiate under the integral, embed in a group or ring
where the operation is total, pass to a completion (`Z → Z_p`, `Q → R`) where analysis exists.
*Micro:* `∫_0^∞ e^{−x} sin x / x dx` has no elementary antiderivative; with
`I(a) = ∫ e^{−ax} sin x / x dx`, `I′(a) = −1/(1+a²)`, `I(∞) = 0`, so `I(1) = π/4`.
`Observed[quad → 0.785398163397448; π/4 = 0.785398163397448]`.
*Fails when:* the descent is not proven. A lift earns its keep only if upstairs has a mechanism
downstairs lacks *and* the return trip is a theorem (Hadamard's rule in the-masters).

**R5 · Quotient by symmetry — count orbits, not objects.**
*Reach when:* many objects are "the same" and you keep overcounting; or a problem has a group acting
and you have not used it.
*Move:* Burnside/Pólya for counting; work in the invariant ring; reduce to a fundamental domain;
WLOG the representative with the most structure.
*Micro:* two-color necklaces of 4 beads under rotation: brute force 6, formula
`(1/4)·Σ_{d|4} φ(d) 2^{4/d} = 6`. `Observed[brute 6, formula 6]`.
*Fails when:* the group does not actually act on the thing you are counting, or stabilizers are
ignored (they are the entire content of the formula).

**R6 · Discretize or continuize.**
*Reach when:* a sum you cannot do but an integral you can, or the reverse; a combinatorial optimum
you cannot find but a relaxation you can.
*Move:* Euler–Maclaurin (sum ↔ integral with an explicit error series); Riemann sums; LP relaxation
then rounding; the probabilistic method as a continuous relaxation of a discrete existence claim.
*Micro:* `H_n − ln n` at `n = 10^6` is `0.57721616…`; subtracting the Euler–Maclaurin term `1/(2n)`
gives `0.577215664901451` against `γ = 0.577215664901533`.
`Observed[verify.py → agreement to 12 digits after one correction term]`.
*Fails when:* the error term is the whole content. "≈" is not a label.

**R7 · Re-encode as a matrix, graph, polynomial, automaton, or lattice.**
*Reach when:* the problem has local rules and global questions.
*Move:* local rules → transfer matrix (counting = matrix power; growth rate = spectral radius);
constraints → graph (reachability, cuts, matchings); combinatorial condition → polynomial
(Combinatorial Nullstellensatz, the polynomial method: a low-degree polynomial cannot vanish on too
large a structured set); process → automaton (regularity, decidability); integer problem → lattice
(LLL finds short relations).
*Micro:* strings of length `n` with no `11`: `M = [[1,1],[1,0]]`, count = row sum of `M^n` →
`2, 3, 5, 8, 13, 21`; brute force agrees for `n ≤ 10`. `Observed[verify.py]`.
*Fails when:* the encoding loses information; then the theorem proved is about the encoding. State
the faithfulness (injective? bijective? preserves which relation?) before using it.

**R8 · Take coordinates from the invariant.**
*Reach when:* you have found an invariant or a decomposition and are still working in the original
coordinates.
*Move:* make the invariant a coordinate. `n = 2^k · m` makes the 2-adic valuation explicit;
action-angle coordinates make the conserved energy a coordinate; the eigenbasis makes the modes
independent. The map then becomes simpler in exactly the direction the invariant controls.
*Micro:* for Collatz, in coordinates `(v_2(3n+1), odd part)` the map on odd `n` is one
multiplication by `3` and one division by `2^v`; the whole E1 model is one line in these
coordinates. `Observed[E1 below]`.
*Fails when:* the invariant is only approximate; then the coordinates are only approximately
decoupled, and the coupling term is the problem you had before, wearing new clothes.

---

## 3. Structure moves — find what is conserved or forced

**S1 · Invariant.**
*Reach when:* "can state A reach state B?"; "is this configuration achievable?"
*Move:* find a quantity every allowed move preserves. If A and B differ in it, unreachable. Colorings
are homomorphisms to a smaller structure; parity, residues, determinants, Euler characteristic,
homology classes are the usual carriers. An invariant that separates is a proof; one that does not is
a hint that the invariant is too coarse.
*Micro:* the mutilated chessboard (two opposite corners removed) cannot be tiled by dominoes: each
domino covers one black and one white square, the board has 32 of one color and 30 of the other.
(Reasoning-only; standard.)
*Fails when:* the invariant is not actually preserved by every move — check the boundary moves and
the degenerate moves first.

**S2 · Monovariant / ranking function.**
*Reach when:* "does this process terminate?"; "does this iteration converge?"; "is this recursion
well-founded?"
*Move:* find a well-founded measure that strictly decreases on every step. Integers bounded below,
lexicographic tuples, multisets, ordinals. Termination in exactly `μ(start)` steps is the strong
form. For a compiler, this *is* the termination proof of a rewrite system or a fixpoint iteration.
*Micro:* rewriting `ba → ab`: the number of inversions (`b` before `a` pairs) drops by exactly 1 per
step. `Observed[300 random strings, ≤ 12 chars → every step drops inversions by exactly 1 and NF =
sorted: True]`.
*Fails when:* the measure is not well-founded (reals bounded below can decrease forever), or
decreases only weakly (needs a second component). Collatz is the case where no simple ranking is
known, and §8 says why that is not an accident.

**S3 · Extremal principle, minimal counterexample, descent.**
*Reach when:* a universal claim; an existence claim with an optimum; anything where "the smallest
bad case" can be spoken of.
*Move:* assume a counterexample exists and take the least one in a well-order; derive a smaller one.
Or: take the extremal object (largest, closest, longest) and show extremality forces the property.
Fermat's descent, the minimal criminal, the farthest-point argument, Zorn's lemma are one move.
*Micro:* in software the same move is *shrinking*: the smallest failing input is the extremal
counterexample and is what a property-based tester hands back. (Reasoning-only.)
*Fails when:* the well-order is not one (no least element in `Q_{>0}`), or the "smaller" object is
not actually in the same class.

**S4 · Pigeonhole and its quantitative cousins.**
*Reach when:* more objects than boxes, in any disguise.
*Move:* plain pigeonhole; Dirichlet's approximation (`|α − p/q| < 1/q²` infinitely often); Ramsey
and Erdős–Szekeres (large enough structures contain ordered substructures); Siegel's lemma (a
linear system with more unknowns than equations has a small integer solution); the box principle in
measure form (a set of measure `> 1` in `[0,1]` contains two points at distance in any given set).
*Micro:* convergents of `√2`: `q²·|√2 − p/q|` is `0.414, 0.343, 0.355, 0.353, 0.354, 0.354` — all
`< 1`, as Dirichlet requires, and converging to `1/(2√2) ≈ 0.3536`.
`Observed[verify.py]`.
*Fails when:* the boxes are not disjoint or the count is off by the boundary case. Count the boxes
twice.

**S5 · Symmetry — exploit it, or break it on purpose.**
*Reach when:* the problem is invariant under a group; or the answer "should" be symmetric and is
not.
*Move:* WLOG the representative; symmetrize (Steiner) to move toward the optimum; use that an
invariant function's gradient at a fixed point lies in the fixed subspace. But: "symmetric problem ⇒
symmetric answer" is a heuristic, not a theorem. Symmetry-breaking optima are common and the
symmetric point is often the saddle.
*Micro:* `f = (x²−1)² + (y²−1)²` is symmetric under `x ↔ y` and both sign flips; the symmetric point
`(0,0)` has `f = 2` and is a local max; the minima `f = 0` are at `(±1, ±1)`, none of which is fixed
by the sign symmetry. `Observed[critical points: nine; minima at (±1,±1); f(0,0) = 2]`.
*Fails when:* the extremum is on the boundary, where the symmetry argument says nothing.

**S6 · Double counting, bijection, trace.**
*Reach when:* two expressions count the same thing; a sum can be reordered; an identity is claimed.
*Move:* count one set two ways (rows then columns; Fubini for sums); build the bijection (a
bijective proof explains, an algebraic one only certifies); use the trace (`tr(AB) = tr(BA)`, so
closed walks = eigenvalue sums).
*Micro:* triangles in `K_4` = `tr(A³)/6 = 4`. `Observed[verify.py → 4]`.
*Fails when:* the "same thing" is counted with multiplicity on one side only.

**S7 · Local-to-global, and its obstructions.**
*Reach when:* the property is easy locally (on small pieces, mod every prime, in every neighborhood)
and wanted globally.
*Move:* compactness (finite subcovers turn pointwise into uniform); gluing (sheaf-style: local
sections agreeing on overlaps); Hasse principle (solvable in every `Q_p` and `R` ⇒ solvable in `Q`,
true for quadratic forms); the Lovász local lemma (mostly-independent bad events can all be avoided).
When local-to-global *fails*, the failure is itself an object: an obstruction class. Finding it is
the next theorem.
*Micro:* `3x³ + 4y³ + 5z³ = 0` has nontrivial solutions in `R` and every `Q_p` but none in `Q`
(Selmer). The obstruction is the Brauer–Manin object, not bad luck.
`Disclosed[recalled: Selmer 1951; Manin 1970]`.
*Fails when:* the pieces overlap and the overlaps are where the content lives. Check the gluing
condition before the local one.

**S8 · The linear algebra method.**
*Reach when:* "how many objects can satisfy pairwise conditions?"; "at most how many?"
*Move:* map objects to vectors so the condition becomes linear independence or a rank bound; then
the count is at most the dimension. Over `F_2`, over `R`, over polynomial spaces.
*Micro:* Oddtown — subsets of an `n`-set of odd size with pairwise even intersections: at most `n`,
because the characteristic vectors are independent over `F_2` (`v_i·v_j = |A_i ∩ A_j| mod 2` is the
identity matrix). `Observed[brute force n = 4 → max family size 4]`.
*Fails when:* the dimension bound is not tight and you needed the exact count; then this move gives
the order of magnitude and something else gives the constant.

**S9 · Positivity: squares, Cauchy–Schwarz, convexity.**
*Reach when:* an inequality; a lower bound on an energy; nonnegativity of a polynomial.
*Move:* write the difference as a sum of squares (an SOS certificate is machine-checkable and is a
complete proof); Cauchy–Schwarz as the universal inequality (nearly every `L²` bound is it in
disguise); Jensen for convex functions; the tangent-line trick (bound a convex function by its
tangent at the equality point); smoothing / mixing variables (move two variables toward each other
and show the target does not increase).
*Micro:* `x² + y² + z² ≥ xy + yz + zx` because
`2(LHS − RHS) = (x−y)² + (y−z)² + (z−x)²`. `Observed[sympy expand → 0]`.
*Fails when:* the polynomial is nonnegative but not SOS (Motzkin's polynomial); then a
Positivstellensatz multiplier is needed, and that is still machine-searchable.

**S10 · Telescoping and discrete calculus.**
*Reach when:* a sum with a "difference" shape; a product with a ratio shape; a hypergeometric term.
*Move:* find `F` with `f(k) = F(k+1) − F(k)`; Abel summation to trade a sum against a sum of partial
sums; creative telescoping (Gosper for indefinite, Zeilberger/WZ for definite hypergeometric sums)
is *decidable* and is therefore an oracle, not a heuristic.
*Micro:* `Σ_{k=1}^n 1/(k(k+1)) = n/(n+1)`. `Observed[gosper_sum → n/(n + 1)]`.
*Fails when:* the term is not hypergeometric; then Gosper says "no" and that answer is also a
theorem (no closed form of that class exists).

---

## 4. Estimation moves — know the size before you prove

**E1 · The random model first.**
*Reach when:* you do not know what to expect; a deterministic object with "random-looking"
statistics; a conjecture whose plausibility you cannot assess.
*Move:* replace the object by a random model that matches its local statistics; compute what the
model predicts; measure the real object. Agreement tells you the proof must *beat* the model's
variance; disagreement tells you where the structure is. Cramér's model for primes, GUE for zeta
zeros, the geometric-valuation model for Collatz.
*Micro:* over odd `n < 2^18`, `v_2(3n+1)` has the distribution
`{1: 0.5, 2: 0.25, 3: 0.125, 4: 0.0625, 5: 0.0312, 6: 0.0156}`, mean `1.99999`. The random walk
with this step law has mean log-step `−0.1438` per `T`-step, so `T`-steps to 1 `≈ 6.95 ln n`.
Measured on 2000 random `n ∈ [10^6, 2·10^6]`: observed mean `97.44`, predicted `98.8`.
`Observed[verify.py]`.
*Fails when:* you forget that the model predicts *density* statements. "Almost all `n` behave" is
what the model can ever say; the universal statement is exactly what the model cannot see (§8).

**E2 · Scaling, homogeneity, dimensional analysis.**
*Reach when:* before any computation; when a formula is proposed; when an answer's order of
magnitude is unknown.
*Move:* assign degrees or units and demand consistency; the answer's scaling exponent is often
forced before any constant is known; lattice points in a ball of radius `R` in `d` dimensions number
`vol·R^d + error`, and the whole difficulty of the Gauss circle problem is the error's exponent, not
the main term.
*Micro:* homogeneity is a type-check: an identity in which one side has degree 2 and the other
degree 3 is false before any algebra. (Reasoning-only.)
*Fails when:* the problem has a hidden scale (a cutoff, a lattice spacing) that breaks homogeneity;
then the answer depends on the ratio of scales, and that ratio is the real variable.

**E3 · Dominant balance and asymptotics.**
*Reach when:* a large or small parameter; an implicit equation; a sum dominated by a few terms.
*Move:* decide which two terms balance, drop the rest, solve, then check the dropped terms are
smaller in the regime found. Iterate for the next correction. Laplace/saddle-point for integrals;
the first term you drop tells you the regime.
*Micro:* `x e^x = 10^6`: first balance `x ≈ ln N = 13.82`, correct to `x ≈ ln N − ln ln N =
11.19`; the true value `W(10^6) = 11.383`; the next correction `+ ln ln N / ln N ≈ 0.19` closes the
gap. `Observed[verify.py → 11.383358 vs 11.189719]`.
*Fails when:* two regimes compete and the balance switches; matched asymptotics is the repair.

**E4 · Averaging — the poor man's probabilistic method.**
*Reach when:* existence of an object with a property "at least as good as average".
*Move:* if the average of `f` over a set is `μ`, some element has `f ≥ μ`. Choose the set and the
measure so the average is computable. Escalations: second moment (concentration says *most*
elements are near `μ`), alteration (fix a random object's few defects), the local lemma, entropy.
*Micro:* a random 2-coloring of a graph's vertices cuts each edge with probability `1/2`, so the
expected cut is `m/2` and a cut `≥ m/2` exists. On a random graph with `m = 151`: mean sampled cut
`75.45`, max sampled `94`. `Observed[verify.py]`.
*Fails when:* you need the object to be *much* better than average; then averaging gives the
existence of the mediocre and something structural is needed for the excellent.

**E5 · Entropy and incompressibility.**
*Reach when:* counting; lower bounds; "most objects have no short description".
*Move:* a set of size `N` needs `log N` bits to index, so most of its elements are incompressible;
any argument that a class of objects has short descriptions bounds its size. Shearer's lemma and the
entropy method turn counting problems into inequalities between entropies of projections.
*Micro:* comparison sorting needs `log_2(n!) ≈ n log_2 n` comparisons because each comparison yields
one bit and `n!` outcomes must be distinguished. (Reasoning-only; standard.)
*Fails when:* the description language is not fixed in advance; Kolmogorov arguments are only valid
relative to a fixed universal machine.

**E6 · The structure-versus-randomness dichotomy.**
*Reach when:* a statistic that holds on average must be shown to hold for every object of a class;
an "obvious" density result resists.
*Move:* a proof *template*: either the object is pseudorandom in a quantified sense (small Fourier
coefficients, small Gowers norm), and then the random model's count is correct; or it is not, and
then a large coefficient locates structure (a subprogression, a subspace) on which the density
*increases*. Iterate; the potential (density ≤ 1) bounds the number of iterations. Roth's theorem
is the archetype; the arithmetic regularity lemma is the industrial form.
*Micro:* none executed here; the template is `Disclosed[recalled: Roth 1953; Gowers 2001]`.
*Fails when:* the pseudorandom case is not actually enough for the count (higher-order structure,
which is what Gowers norms were built to detect).

---

## 5. Unsticking moves — search when you have nothing

**U1 · Small cases, then the instrument.**
*Reach when:* always first. Then: a constant to identify, a sequence to name, a form to guess.
*Move:* compute the first cases by hand and by program (two routes); dwell on the table
(the-euler-method); then use the instruments — OEIS for integer sequences, `identify`/PSLQ/LLL for
constants, rational-GF and linear-recurrence guessers for sequences, `sympy.nsimplify` — and *test the
guess on fresh cases past the fitting window*.
*Micro:* `mpmath.identify(ζ(2), ['pi**2'])` → `(1/6)·π²`; `pslq([ζ(2), π²])` → `[−6, 1]`.
`Observed[verify.py]`. The hazard: regions of a circle cut by chords through `n` points are
`1, 2, 4, 8, 16, 31, 57, 99`; five terms fit `2^{n−1}` and the sixth kills it.
`Observed[C(n,4)+C(n,2)+1 for n = 1..8]`.
*Fails when:* the fitting window is the whole data. A guess is `Conjectured` until it predicts a
case it was not fitted to.

**U2 · Specialize to the extreme.**
*Reach when:* too many parameters; a general statement with no handle.
*Move:* set `n = 0, 1, 2`; send a parameter to `0` or `∞`; take the trivial group, the empty set,
the identity matrix, the constant function; find where equality holds in an inequality. The
degenerate case shows what is *forced*; the equality case is a latent definition (Hadamard).
*Micro:* to test whether a claimed inequality is sharp, solve for its equality case first; if no
equality case exists the constant can be improved and the claim is not the theorem.
(Reasoning-only.)
*Fails when:* the degenerate case is degenerate in a different way than the general one (a proof for
`n = 1` that uses `n = 1` is not a base case, it is a coincidence).

**U3 · Generalize to make it easier — the inventor's paradox.**
*Reach when:* induction fails because the hypothesis is too weak; a specific case is harder than the
general one.
*Move:* prove a stronger statement whose inductive step has slack; add a parameter and prove it for
all values; replace the specific object by the class that has the property that actually matters.
*Micro:* `Σ_{k≤n} 1/k² < 2` does not go by naive induction; `Σ_{k≤n} 1/k² ≤ 2 − 1/n` does, since
`2 − 1/n + 1/(n+1)² ≤ 2 − 1/(n+1)` reduces to `n + 1 ≥ n`. `Observed[checked n < 200: True]`,
`Verified[induction above | numeric check]`.
*Fails when:* the generalization is false. Test it on small cases first (U1); a false strengthening
is the most common way this move dies, and the cheapest.

**U4 · Wishful thinking — name the missing lemma.**
*Reach when:* a proof idea is 80% there.
*Move:* write the whole proof assuming the lemma you wish were true. The residual is now a named,
bounded target with a type. Test the lemma on small cases *before* trying to prove it; it is often
false, and learning that costs a minute.
*Micro:* in a compiler: "if only this were an invariant of the loop" → assert it, run the suite,
fuzz it. A failing assertion is a counterexample to the lemma and a tombstone for the proof shape.
(Reasoning-only.)
*Fails when:* the wished lemma is equivalent to the theorem (circularity). Check that the lemma is
strictly weaker, or at least differently shaped, before spending on it.

**U5 · Work backwards — the preimage tree.**
*Reach when:* the target is known and the start is arbitrary; a reachability claim.
*Move:* compute the set of things one step from the goal, then two; the claim becomes "the backward
tree covers everything". Analysis-by-synthesis. Pólya's working backwards.
*Micro:* Collatz backwards from 1: every `m` has preimage `2m`; `m` has an odd preimage `(m−1)/3`
exactly when `m ≡ 4 (mod 6)`. `Observed[(4,1),(10,3),(16,5),(22,7),(28,9),(34,11)]`. The
conjecture becomes: this tree contains every positive integer.
*Fails when:* the backward tree is as hard to control as the forward orbit — which is the case for
Collatz, where density of the tree is the same open problem in a mirror.

**U6 · Analogy with an explicit dictionary.**
*Reach when:* a sibling problem is solved; a different field has a theorem of the same shape.
*Move:* write the dictionary as a table — `object | analog | what transfers | what does not` — and
transfer only what the table licenses. The blank cells are the research program.
*Micro:* `Z ↔ F_q[t]`: primes ↔ irreducible polynomials, `|n| ↔ q^{deg}`, `ζ ↔ zeta of a curve`,
`RH ↔ RH for curves (proved: Weil; for varieties: Deligne)`. What does not transfer: Frobenius, a
cohomology theory for `Spec Z`. The blanks are literally the modern programs.
`Disclosed[recalled]`.
*Fails when:* vocabulary is transferred instead of relations. "It is like a Hilbert space" is not a
dictionary; "the inner product is `⟨f,g⟩ = …` and the theorem needs completeness, which holds
because …" is.

**U7 · Enumerate the strategy space; choose with a reason.**
*Reach when:* about to start a proof attempt.
*Move:* the strategies for a universal statement: direct construction; induction (on *which*
well-order?); invariant/monovariant; extremal/descent; contradiction plus counting; compactness;
probabilistic/averaging; algebraic (linear algebra method, polynomial method); analytic (transforms,
asymptotics); reduction to a known theorem; dichotomy-plus-increment. Write the line
`strategy: X because Y; excluded: Z because barrier B` into the ledger. The exclusions come from §8.
*Micro:* none; this move is bookkeeping, and it is the bookkeeping the audit found missing.
*Fails when:* the list is recited rather than tried. Each strategy gets a one-sentence sketch of
what it would need; a strategy with no sketch is not on the list.

**U8 · Try, honestly, to refute — with a structure theorem.**
*Reach when:* before any proof attempt beyond an hour; whenever the claim's plausibility is not
established.
*Move:* first derive what a counterexample *must* look like (size, residue class, shape), then
search exactly there. Random search finds the easy counterexamples; structured search finds the ones
that exist.
*Micro:* Euler knew every prime factor of `F_5 = 2^32 + 1` is `≡ 1 (mod 64)`; the primes of that
form below 641 are `193, 257, 449, 577, 641`, and the fifth one divides.
`Observed[641 mod 64 = 1; (2^32+1) mod 641 = 0; candidate list as quoted]`.
*Fails when:* the structure theorem is wrong and excludes the region where the counterexample lives.
Verify the structure theorem on a known case first (the Instrument rule applied to the search).

**U9 · Change the question — the relaxation ladder.**
*Reach when:* the statement resists at its full strength; you need to know where the frontier is.
*Move:* build the ladder from the weakest true statement to the target and mark which rung is open:
verified to a bound → finite version → almost all (density) → almost all with rates → conditional on
a standard hypothesis → effective bound → the theorem. Also: swap the quantifier order; ask for the
constant; ask the conjugate question (instead of "no divergent orbit", "the set of `n` with orbit
above `n` has density 0 with a rate").
*Micro:* the Collatz ladder as recalled — verified to at least `2^68`; no nontrivial cycles of
bounded shape (Baker-type bounds on `|2^a − 3^b|`); almost all `n` have an iterate below `n`
(Terras 1976); almost all orbits attain almost bounded values (Tao 2019); every orbit bounded (open);
every orbit reaches 1 (open). `Disclosed[recalled; citations in §11]`.
*Fails when:* the rung you climb is not on the way to the target (a density result that no
bootstrapping can promote). Say which rungs are terminal.

**U10 · Carry several problems; switch on a timer; write the tombstone.**
*Reach when:* stuck for longer than the budget from §1.
*Move:* keep three to twelve live problems (Feynman, Hamming); when a new method appears, run it
against all of them. Switch when the budget is spent, and switch *to a different representation* of
the same problem before switching problems. Every switch writes the tombstone with a recurrence
keyword so the same dead path is not re-walked next session. Incubation is real; for a session its
form is "state written to the ledger, a different bearing spawned, return later".
*Micro:* none; this is the practice the audit's `TOMBSTONES.yaml` exists to hold.
*Fails when:* switching becomes avoidance. The budget is set before starting, not after failing.

---

## 6. Rigor moves — stay true while being clever

**G1 · Quantifier hygiene.**
*Reach when:* stating any claim; reading any "for all"; reading any constant.
*Move:* write every quantifier and every dependence: `∀ε ∃N(ε)` is not `∃N ∀ε`; `C` depends on
which parameters; is the bound *effective* (computable from the statement) or only known to exist?
*Micro:* Roth's theorem bounds the *number* of good rational approximations to an algebraic number
but gives no bound on their *size* — the finiteness is ineffective, and an ineffective theorem cannot
be used to compute anything. `Disclosed[recalled: Roth 1955; Davenport–Roth 1955]`.
*Fails when:* the proof silently swaps the order, usually inside an "obviously" or a "similarly".

**G2 · Type-check the equation.**
*Reach when:* any formula is written down.
*Move:* degrees and units (E2); symmetry (if the problem is symmetric in `x, y`, the answer must
be); limits (`n = 0`, `n → ∞`); sign and parity; a numeric spot-check at a random point before any
proof is attempted. Cost: one second per check. Most false identities die here.
*Micro:* the S9 certificate was spot-checked by `expand(… ) → 0` before being called a proof; the R3
closed form was spot-checked to 12 digits at five points before being called one.
`Observed[verify.py]`.
*Fails when:* the checks are run on the cases the formula was fitted to (U1's hazard again).

**G3 · Minimal-hypotheses probe.**
*Reach when:* a proof is complete; a lemma is about to be reused.
*Move:* remove each hypothesis in turn and find the counterexample. No counterexample → either a
stronger theorem is free, or the hypothesis was used silently. Either way the load-bearing step is
now located. For programs this is mutation testing.
*Micro:* in chain B, adding the rule `ab → ba` kills termination and the inversion monovariant; the
theorem's hypothesis "one orientation only" is thereby shown load-bearing. (Reasoning-only.)
*Fails when:* skipped because the proof "obviously" uses everything. The word is the trigger.

**G4 · The formal/analytic boundary.**
*Reach when:* a manipulation of infinite objects; a series evaluated outside its disc; an operator
applied without a domain.
*Move:* say in which structure the identity holds. `Σ x^n = 1/(1−x)` is an identity in `Z[[x]]` and
an equation on `|x| < 1`; `x = 2` is a category error. `1 − 1 + 1 − … = 1/2` and `ζ(−1) = −1/12`
are true statements about regularizations and false statements about sums; the label is the
regularization. Euler's formal manipulations were right because he checked them against known
values; Ramanujan's one great failure was a formal manipulation nobody checked.
*Micro:* none executed; the rule is the-masters' Ramanujan governor.
*Fails when:* the two senses are conflated in a chain: a formal step followed by an analytic one
proves nothing unless the object lives in both structures at that step.

**G5 · Relay-result audit.**
*Reach when:* a lemma has just been proved.
*Move:* re-read it *without the question that motivated it*: what is its converse? its equality
case? its limit? its minimal hypotheses? does it define something? what else does it prove for free?
Then choose the generality at which the proof becomes trivial (Grothendieck's rising sea) and
restate it there. The audit found lemma reuse absent; this move is where reuse is born.
*Micro:* none executed; the rule is Hadamard's in the-masters.
*Fails when:* run only at the end of a session. It is a per-lemma move.

**G6 · Machine-check what can be machine-checked, with the cheapest kernel of the claim's type.**
*Reach when:* any claim is about to be labeled above `Conjectured`.
*Move:* the audit's claim-typed oracle policy, restated as a reach: polynomial identity → CAS by two
routes; nonnegativity → SOS/z3; hypergeometric sum → Gosper/Zeilberger (decidable); finite statement
→ exhaustive by two implementations; asymptotic → numeric at three scales plus the error bound;
general theorem → Lean 4 with Mathlib, `sorry`-free. No kernel of the type → the label says
`UNVERIFIED[no oracle of this class]`.
*Micro:* every `Observed` in this document is one route; none is `Verified` unless two routes are
named (U3, R7 are).
*Fails when:* the kernel is calibrated on cases recalled rather than verified (the audit's own P1
error). The calibration case is itself a claim.

**G7 · The proof skeleton with typed holes.**
*Reach when:* any proof longer than a page; any multi-session pursuit.
*Move:* write the lemma tree first, each node labeled at birth (`Conjectured` until proved),
`Verified` nodes frozen, the frontier being the set of unproved leaves. This is
`state/FRONTIER.yaml` in the audit; the skeleton is the plan and the labels are the state. Progress
is measured as leaves closed, not as pages written.
*Micro:* chain A below is a three-node skeleton; every node carries its label.
*Fails when:* the skeleton is redrawn every session instead of read. Redrawing is permitted only
with a `Reformulate` entry stating what the old skeleton could not express.

---

## 7. Programs as mathematical objects — the compiler lens

**C1 · Correctness is a commuting square.**
*Reach when:* any transformation of programs (a pass, a lowering, a refactor).
*Move:* two paths must agree: compile-then-run equals run-then-translate-the-result. Every pass is a
theorem with that shape; the witness is a *simulation relation* between source and target states.
CompCert is the existence proof that this scales to a real compiler.
`Disclosed[recalled: Leroy 2009]`.
*Fails when:* the square is stated for the wrong semantics (a pass that preserves final results but
not termination, or results but not observable effects).

**C2 · Termination and confluence have standard tools.**
*Reach when:* a rewrite system, a normalizer, a simplifier, a type checker with reductions.
*Move:* termination via a well-founded order compatible with the rules (S2; recursive/lexicographic
path orders for terms); confluence via critical pairs — with termination, local confluence suffices
(Newman's lemma), and local confluence is a finite check of the rule overlaps (Knuth–Bendix).
*Micro:* `{ba → ab}`: terminates (inversions), has no critical pairs (`ba` overlaps itself nowhere:
its suffix `a` is not its prefix `b`), hence confluent, hence unique normal forms, which are the
sorted strings. `Observed[300 random runs → NF = sorted: True]`,
`Verified[monovariant argument | Newman + no critical pairs]`.
*Fails when:* the rules are applied modulo an equivalence (associativity, commutativity); then
ordinary critical pairs are insufficient and completion modulo the theory is needed.

**C3 · Abstract interpretation is a Galois connection.**
*Reach when:* a static analysis; any "approximate but sound" reasoning about all executions.
*Move:* pick an abstract lattice, an abstraction `α` and a concretization `γ` with
`α(S) ⊑ a ⟺ S ⊆ γ(a)`; soundness is a commuting square; precision loss is the price and is chosen,
not suffered.
*Micro:* the sign lattice `{⊥, −, 0, +, ⊤}`: `(−)·(−) = +` exactly, `(+) + (−) = ⊤` (information
lost, soundly). (Reasoning-only; standard.)
*Fails when:* the transfer functions are not monotone; then the fixpoint iteration of C4 has no
guarantee.

**C4 · Fixed points: Knaster–Tarski and Kleene.**
*Reach when:* dataflow analysis, type inference, any "iterate until stable".
*Move:* a monotone function on a complete lattice has a least fixed point; if the lattice has no
infinite ascending chains the iteration terminates (S2 with the chain height as the ranking); if it
does, *widening* is the monovariant you install by hand.
*Micro:* none executed; standard.
*Fails when:* the function is not monotone (a "smart" analysis that sometimes loses information as
input grows) — then the iteration can cycle, and the fix is the definition, not the loop.

**C5 · Differential and metamorphic oracles.**
*Reach when:* the correct output is unknown but *relations* between outputs are known.
*Move:* two independent implementations must agree (two-route witness for programs: two compilers,
two optimization levels); semantics-preserving mutations must preserve output (metamorphic:
Csmith, EMI); property-based testing with shrinking is the probabilistic method (E4) plus the
extremal principle (S3), automated. `Disclosed[recalled: Yang et al. 2011; Le et al. 2014]`.
*Micro:* none executed; note from the audit that `hypothesis` is not installed on this machine.
*Fails when:* both routes share a component (common-mode, the audit's central finding). The
independence of the two routes is a claim that needs its own line.

**C6 · Types are theorems; parametricity gives theorems for free.**
*Reach when:* designing an interface; reasoning about what an implementation *can* do.
*Move:* a polymorphic signature constrains behavior: any `∀a. [a] → [a]` can only rearrange, drop, or
duplicate elements, never inspect them (Wadler's free theorems). Make the type carry the invariant
and the compiler carries the proof. `Disclosed[recalled: Wadler 1989]`.
*Micro:* none executed.
*Fails when:* the language has escape hatches (casts, reflection, unsafe) that break parametricity;
the theorem is then conditional on their absence.

---

## 8. Barrier literacy — a wall tells you the shape of the door

A barrier is a theorem of the form "no proof of shape `K` can settle this". Its value is not
discouragement; it is pruning. Each barrier removes strategies from U7's list and adds an entry to
the *must-use* list: what any successful proof has to contain. The audit's `OBSTRUCTIONS.yaml`
fields (`what it blocks`, `established_by`, `where_it_stops`, `resurrection_condition`) are the
record form. Everything in this section is `Disclosed[recalled]`; §11 lists what to check.

**Collatz.**

- *Conway 1972 (Unpredictable Iterations):* there are generalized Collatz maps (piecewise affine by
  residue class) whose iteration problem is undecidable. *Must-use:* something specific to `3n+1` —
  the coprimality of 2 and 3, the size of `3/4`, the particular residue structure. Any argument that
  would work uniformly for the class is wrong before it starts.
- *Lagarias 1985 (survey), building on Terras:* the map `T` extends to the 2-adic integers, is
  measure-preserving there, and the parity-vector map conjugates it to the 2-adic shift. On `Z_2`
  the dynamics is a Bernoulli shift with uncountably many orbits that never enter the cycle; `Z` is
  a measure-zero subset. *Must-use:* the arithmetic that distinguishes integers inside `Z_2` — a
  nonnegative integer is a 2-adic number whose expansion is eventually `0`. A purely dynamical or
  ergodic argument on `Z_2` cannot see the integers and therefore cannot prove the conjecture.
- *Terras 1976; Tao 2019:* almost all `n` have an iterate below `n`; almost all orbits attain almost
  bounded values (logarithmic density). *Where it stops:* density-one statements are exactly what
  the random model (E1) predicts, and the model is blind to a measure-zero exceptional set. The
  universal statement needs a mechanism that controls every `n`, not most.
- *Cycles (Steiner 1977; Simons–de Weger 2005; extended since):* a nontrivial cycle forces
  `|2^a − 3^b|` to be small, which Baker's theorem on linear forms in logarithms bounds below; with
  the verified range this excludes cycles of all small shapes. *Shape of the door:* cycle exclusion
  is an *arithmetic* wall climbed by transcendence tools. Divergence exclusion has no analogous
  tool. That asymmetry is the frontier and should be named in any plan.
- *Drift `log(3/4)`:* `Observed` in E1. The model's prediction is the null hypothesis every claimed
  mechanism must either reproduce or explain its departure from.

**Riemann Hypothesis.**

- *Davenport–Heilbronn 1936:* there are Dirichlet series with a Riemann-type functional equation and
  analytic continuation that have zeros off the critical line. *Must-use:* the Euler product (the
  multiplicative structure). A proof from the functional equation and analyticity alone proves a
  false generalization.
- *de Bruijn–Newman; Rodgers–Tao 2018:* RH is equivalent to `Λ ≤ 0`; Rodgers and Tao proved
  `Λ ≥ 0`. So RH is equivalent to `Λ = 0`: the zeta function sits on the boundary of the heat-flow
  family. *Shape of the door:* any argument robust under small perturbation of that family would
  prove `Λ < 0`, which is false. The proof must be sharp, not approximate; "RH is barely true if
  true".
- *Weil; Deligne:* RH holds for curves and varieties over finite fields, proved via cohomology and
  Frobenius eigenvalues. *Dictionary blanks (U6):* no Frobenius, no cohomology for `Spec Z`. The
  blanks are the programs (Connes, `F_1`, Arakelov).
- *Montgomery; Odlyzko:* zero statistics match GUE. *Null model (E1):* a proposed proof should
  either yield GUE statistics or say why it is silent about them.

**P versus NP** (the cleanest barrier family, included as the pattern).

- Relativization (Baker–Gill–Solovay 1975), natural proofs (Razborov–Rudich 1994), algebrization
  (Aaronson–Wigderson 2008). Each is a theorem that a named proof technique cannot separate the
  classes. *Must-use:* something non-relativizing, non-natural, non-algebrizing — and each new
  program (GCT, hardness magnification) states which barrier it evades. That statement is the Stage
  0.5 check the audit installed.

**Compilers.**

- *Rice's theorem:* every nontrivial semantic property of programs is undecidable. *Consequence:*
  every static analysis is approximate by necessity; soundness-versus-precision is a forced choice,
  not a design failure, and C3 is the formalism for choosing it.
- *Full abstraction:* a compiler that preserves semantics need not preserve contextual equivalence;
  a target-language context can distinguish programs the source language cannot. *Consequence:*
  "correct" has more than one definition, and a security claim needs the stronger one.

**The generic rule.** Before funding an approach, write its `evades:` line against every barrier in
the class. An approach that cannot say which barrier it evades is `Dark`, and the audit's rule
applies: `Dark` is fine, "promising" is not a label.

---

## 9. Three worked chains

Each chain is a sequence of moves on a small real problem, with the labels it earns. The point is
the *chaining*, which is where the moves become thinking rather than a list.

**Chain A — a sequence becomes a theorem (U1 → R7 → U3 → G6).**
Count binary strings of length `n` with no two adjacent `1`s.
1. U1: brute force gives `2, 3, 5, 8, 13, 21, 34, 55, 89, 144`. `Observed`.
2. U1 instrument: `find_linear_recurrence` on the data returns `[1, 1]`, so `a_n = a_{n−1} + a_{n−2}`
   fits. `Conjectured[pays-off-if: a mechanism explains the recurrence]`.
3. R7: the mechanism. A valid string ends in `0` (preceded by any valid string of length `n−1`) or
   in `01` (preceded by any valid string of length `n−2`). That *is* the recurrence, and it is the
   transfer matrix `[[1,1],[1,0]]` whose row sums give `2, 3, 5, 8, 13, 21`. `Observed`.
4. U3: the induction closes with base cases `a_1 = 2, a_2 = 3`, so `a_n = F_{n+2}`.
5. G6: two routes named. `Verified[case-split induction | transfer-matrix power]`.
6. G5 relay audit, for free: the GF is `(1+x)/(1−x−x²)`; the growth rate is the golden ratio; the
   same matrix counts walks on the two-vertex graph with a loop at `0`, so the theorem is really
   about that graph.

**Chain B — a rewrite system is proved terminating and confluent (S2 → C2 → G3).**
The system `{ba → ab}` on strings over `{a, b}`.
1. S2: candidate ranking function — the number of inversions. Each application removes exactly the
   swapped pair's inversion and touches no other pair. `Observed[300 runs → drops by exactly 1]`.
   Termination in exactly `inv(s)` steps. `Verified[the pair argument | the random runs]`.
2. C2: critical pairs. The only rule's left side `ba` overlaps itself only if a proper suffix equals
   a proper prefix; `a ≠ b`, so there are no overlaps, so the system is locally confluent.
3. C2: Newman's lemma with 1 and 2 gives confluence, hence unique normal forms; the normal forms
   are the strings with no `ba`, which are the sorted strings. `Observed[NF = sorted: True]`.
4. G3: remove the hypothesis "one orientation": adding `ab → ba` gives a non-terminating system, and
   inversions are no longer monotone. The one-orientation hypothesis is load-bearing.
5. What this buys a compiler: any simplifier whose rules can be oriented by a well-founded order and
   whose overlaps join is a *decision procedure* for its equational theory, and that is a theorem to
   put in the ledger, not a comment in the code.

**Chain C — from a random model to a must-use list (R8 → E1 → U9 → §8).**
Collatz, as a demonstration of how heuristics and barriers together constrain any proof.
1. R8: coordinates `(v, odd part)`, `v = v_2(3n+1)`. The map on odd `n` is "multiply by 3, add 1,
   divide by `2^v`".
2. E1: `v` is geometric with mean `2` over odd residues (`{1: .5, 2: .25, 3: .125, …}`,
   mean `1.99999` on `2^17` odd `n`). Mean log-step `−0.1438` per `T`-step. Prediction: `T`-steps
   to 1 `≈ 6.95 ln n`. Measured: `97.44` against `98.8` on 2000 random `n ∈ [10^6, 2·10^6]`.
   `Observed`.
3. The honest gap: the model is a random walk with independent steps; it predicts density
   statements with rates, and Terras and Tao are exactly those rungs (U9). It cannot predict the
   universal statement because successive `v` values on an actual orbit are determined, not
   independent, and the integers are a measure-zero set inside the model's natural space.
4. §8 assembled into a must-use list for any proposed route:
   - uses `3n+1` specifically, not the piecewise-affine class (Conway);
   - uses integrality — the eventual-constancy of the 2-adic expansion — not 2-adic dynamics alone
     (Lagarias);
   - reproduces the `log(3/4)` drift or explains its departure (E1);
   - explains why the density-one methods stop at density one (Terras, Tao);
   - for cycles, either reproduces a Baker-type bound or says how it evades the need for one; for
     divergence, names the tool it uses in place of the one that does not exist.
5. Any route whose ledger entry cannot fill these five lines is `Dark`, and the next move is U7 with
   these as exclusions, not another attempt.

---

## 10. The one-page reach list

| id | move | one line |
|---|---|---|
| R1 | Transform | pick the transform where the hard operation becomes multiplication or addition |
| R2 | Dualize | the dual-feasible point is the certificate; weak duality is free |
| R3 | Substitute | find the coordinates in which the nonlinear thing is linear |
| R4 | Lift | add a dimension or parameter; prove the descent |
| R5 | Quotient | count orbits; use the group you have not used |
| R6 | Discretize/continuize | swap sum and integral; the error term is the content |
| R7 | Re-encode | matrix, graph, polynomial, automaton, lattice; state faithfulness |
| R8 | Invariant coordinates | make the conserved quantity a coordinate |
| S1 | Invariant | a preserved quantity that separates is a proof |
| S2 | Monovariant | a well-founded strictly decreasing measure is termination |
| S3 | Extremal | the least counterexample; the extremal object; shrinking |
| S4 | Pigeonhole | more objects than boxes, in any disguise; quantitative forms |
| S5 | Symmetry | WLOG and symmetrize; but the symmetric point may be the saddle |
| S6 | Double count | two ways, a bijection, or a trace |
| S7 | Local-to-global | compactness and gluing; when it fails, find the obstruction object |
| S8 | Linear algebra | independence bounds the count by the dimension |
| S9 | Positivity | SOS, Cauchy–Schwarz, Jensen, tangent line, smoothing |
| S10 | Telescope | discrete calculus; Gosper/WZ is a decision procedure |
| E1 | Random model | the null hypothesis every mechanism must beat or explain |
| E2 | Scaling | degrees and units before algebra; the exponent before the constant |
| E3 | Dominant balance | which two terms balance; drop, solve, check |
| E4 | Averaging | some element is at least the mean; then second moment, alteration, LLL |
| E5 | Entropy | most objects are incompressible; counting as inequality |
| E6 | Dichotomy | pseudorandom or structured; increment; bounded potential |
| U1 | Small cases + instrument | compute, dwell, guess with a tool, test past the window |
| U2 | Specialize | the extreme and degenerate cases show what is forced |
| U3 | Generalize | the stronger statement with inductive slack |
| U4 | Wishful lemma | write the proof with the hole; test the hole on small cases |
| U5 | Backwards | the preimage tree; the claim becomes coverage |
| U6 | Dictionary | analogy as a table; blanks are the program |
| U7 | Strategy enumeration | list, sketch, choose with a reason, exclude by barrier |
| U8 | Structured refutation | derive the counterexample's shape, then search there |
| U9 | Relaxation ladder | weakest true to target; mark the open rung and the terminal ones |
| U10 | Carry and switch | several problems; budget first; tombstone with keyword |
| G1 | Quantifiers | every dependence explicit; effective or not |
| G2 | Type-check | degrees, symmetry, limits, sign, a random numeric point |
| G3 | Minimal hypotheses | remove each; find the counterexample or the free theorem |
| G4 | Formal/analytic | say in which structure the identity holds |
| G5 | Relay audit | re-read the lemma without the question; find the right generality |
| G6 | Machine-check | the cheapest kernel of the claim's type; no kernel → say so |
| G7 | Skeleton | lemma tree with typed holes; progress is leaves closed |
| C1 | Commuting square | compile-then-run equals run-then-translate; simulation relation |
| C2 | Rewrite tools | well-founded order for termination; critical pairs for confluence |
| C3 | Galois connection | abstraction with chosen, sound precision loss |
| C4 | Fixed points | monotone on a lattice; chain height or widening for termination |
| C5 | Differential oracle | two independent routes; metamorphic relations; shrinking |
| C6 | Types as theorems | the signature constrains the implementation |

---

## 11. This document's ledger and boundary

**Observed (executed by `mathematical-moves-verify.py`, outputs quoted above):** U1 identify and
PSLQ; U1 Moser regions; R3 Lucas–Lehmer closed form; R4 the parameter integral; R5 Burnside
necklaces; R6 Euler–Maclaurin for `γ`; R7 transfer matrix and recurrence guess; S4 convergents of
`√2`; S5 symmetric function with asymmetric minima; S6 trace count; S8 Oddtown at `n = 4`; S9 SOS
expansion; S10 Gosper; U3 the strengthened inequality; U5 the preimage rule; U8 Euler's 641; E1 the
valuation distribution, drift, and stopping-time comparison; E3 Lambert W; E4 the cut expectation;
C2 the rewrite runs.

**Verified (two named routes):** U3, R7/chain A, chain B step 1 and step 3.

**Disclosed[recalled] — check the citation before any of these carries weight:** Selmer 1951 and
the Brauer–Manin obstruction (S7); Roth 1953 and Gowers 2001 (E6); Roth 1955 ineffectivity (G1);
Leroy 2009 CompCert (C1); Yang et al. 2011 Csmith and Le et al. 2014 EMI (C5); Wadler 1989 (C6);
Conway 1972; Lagarias 1985 and the conjugacy to the 2-adic shift; Terras 1976; Tao 2019; Steiner
1977; Simons–de Weger 2005; the verified range `2^68`; Davenport–Heilbronn 1936; de Bruijn,
Newman, Rodgers–Tao 2018; Weil and Deligne; Montgomery and Odlyzko; Baker–Gill–Solovay 1975;
Razborov–Rudich 1994; Aaronson–Wigderson 2008; Rice's theorem. The audit's own lesson applies:
the orchestrator planted a calibration error from a recalled folklore fact, so a recalled citation
is a claim about memory, not about the literature.

**Reasoning-only (standard results restated, not executed):** R2, S1, S3, E2, E5, U2, U4, C3, C4.

**Boundary.** Written by one bearing with no council, so it carries exactly the common-mode risk
the audit named: every idea here came from one model's priors about what mathematicians do. The
antidotes are the receipts (every `Observed` has a command) and the citation list (every recalled
fact is marked). What this document does not contain: a method for choosing *which* problem to
work on, anything about collaboration at Polymath scale, or the-euler-method's compute-and-dwell
discipline, which it assumes rather than repeats. Its ceiling is the audit's: on a compiler-class
pursuit these moves are most of the work; on Collatz- or RH-class pursuits they keep the walk
honest and non-repeating, and §8 is the part that keeps it from being circular.
