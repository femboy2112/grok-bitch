# Factorial Interference: Configuration Cross-Terms

## Purpose

Use this mode when two or more factors can be toggled independently. A real structure may be written
not only in the response to each factor but in the **non-additive response of their joint
configuration**. This is the disciplined double-slit analogue: measure the missing cross-term rather
than treating ordinary agreement as interference.

The method is classical experimental design. A nonzero interaction is not evidence that the system
is physically quantum.

## 1. The complete two-factor design

For binary factors \(A,B\), measure all four cells:

\[
Y_{00},\quad Y_{10},\quad Y_{01},\quad Y_{11}.
\]

The baseline-anchored mixed difference is

\[
I_{AB}=Y_{11}-Y_{10}-Y_{01}+Y_{00}.
\]

For a purely additive model \(Y_{ab}=\beta_0+\beta_Aa+\beta_Bb\), \(I_{AB}=0\). A value distinct from
zero beyond calibrated uncertainty shows non-additivity at the measured scale.

Never infer a two-factor interaction from only three cells. The missing fourth cell is the very
quantity that separates a joint effect from additive extrapolation.

## 2. More factors: Walsh–Hadamard basis

For \(k\) binary factors, encode configuration coordinates as \(z_i\in\{-1,+1\}\). For subset
\(S\subseteq\{1,\ldots,k\}\), define

\[
\widehat Y(S)=2^{-k}\sum_{z\in\{-1,+1\}^k}Y(z)\prod_{i\in S}z_i.
\]

- \(S=\varnothing\): grand mean;
- \(|S|=1\): main effects;
- \(|S|=2\): pair interactions;
- higher order: configuration effects not reducible to lower-order additive terms.

This is an orthogonal decomposition of a complete binary factorial table. It is an exact algebraic
identity for the supplied cells, not a causal theorem.

## 3. From interaction to structure

A detected cross-term earns only the claim “the response is non-additive under this design and
measurement.” To infer a mechanism, require rivals to predict additional structure:

- sign and approximate magnitude;
- symmetry or antisymmetry under factor exchange;
- scaling with dose, resolution, time, or system size;
- disappearance under a negative control;
- persistence through independent implementation or source path;
- lawful transformation under a second basis;
- replication on a fresh holdout.

An unmodeled ceiling, normalization, selection rule, measurement nonlinearity, or shared dependency
can also produce an interaction.

## 4. Controls and uncertainty

A serious design should include:

1. repeated cells or a justified error model;
2. positive and negative interaction controls;
3. randomized execution order where order effects are possible;
4. blinding where analyst or source expectations can leak;
5. preregistered factors, cell definitions, contrast, and stopping rule;
6. a source/dependence map for every observation;
7. uncertainty intervals or an exact proof when the domain is mathematical.

For continuous, multi-level, or constrained factors, use the appropriate regression/ANOVA, response
surface, causal, or algebraic design rather than forcing a binary table.

## 5. Bundled instrument

```bash
python3 scripts/factorial_interference.py --self-test
python3 scripts/factorial_interference.py assets/factorial-double-slit.json
```

The tool requires all \(2^k\) cells, computes Walsh–Hadamard coefficients and baseline-anchored mixed
differences, and emits explicit nonclaims. It does not estimate uncertainty from a single table and
does not identify a mechanism by itself.
