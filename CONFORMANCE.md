# Conformance — Janus-Facing Architecture

The repo's self-description in the architecture's own terms, stated **before** anything product-specific, per the architecture's ordering rule. Every conformance claim is bound to the mechanism and check that enforces it, or it is labeled a stand-in. Unbound prose is marketing.

The architecture is **Janus-Facing Architecture (JFA)** — NTARI's unified architecture document, free documentation under the project's AGPL-3.0 commons.

## Role declaration

LBTAS is the **assessment scale** of the JFA **covenant layer**: reputation as a standing promise not to harm, carried as a full distribution — never a score. The logic is the safety engineer's (Leveson): harm is a discrete event to be surfaced, not a quantity to be smoothed; two crashes in seventy-three flights grounds the fleet. The scale is domain-general: a consuming economy adopts it and interprets it in context.

| This repo's term | Architecture role |
|---|---|
| The 6-level ordinal scale (−1..+4) | the covenant's meaning-loaded rating vocabulary; **−1 is the breach itself** |
| `{distribution, total}` | reputation as the architecture requires it carried: count at each level beside the total |
| Bidirectional rating | covenant symmetry between counterparties |
| Per-category distributions | relation-scoped reads (never collapsed into one figure) |

## Invariants and their bindings — as of `main` (v2.0.0)

| Invariant (architecture) | Mechanism here | Check |
|---|---|---|
| Reputation MUST NOT be averaged into a score | v2.0.0 read API returns `{distribution, total}` per category; `system_average`, `category_averages`, and average-ranked performer lists are **removed** | CHANGELOG 2.0.0 (breaking); the unit-of-reputation comment in code; no averaging path exists to call |
| The **lowest rating is the breach itself** | −1 ("No Trust") is a discrete harm event held permanently visible in the distribution beside any volume | Distribution shape; no cancellation arithmetic exists |
| The covenant is **symmetric** between counterparties | Bidirectional by design: one exchange can produce two ratings, producer↔consumer, same scale both ways | Scale definition; API |
| The scale is **meaning-loaded, ordinal** — not a continuous axis | Each level carries a specific definition; integers −1..+4 | CLAUDE.md canonical table; validation |
| Reputation gates **whether**, never **how much** | The library derives no credit limit, weight, or ceiling from the distribution — no such API exists | API surface |
| **Non-portable by default** | Per-platform data; no cross-platform identity or import path in the library | API surface |
| **Observational diversity across implementations** | Four reference implementations (Go, Python, Rust, TypeScript) that must stay in parity — independent encodings of one behavior | CLAUDE.md parity rule; see stand-ins |

## Deliberately out of scope

Contestation mechanics — claim filing, adjudication, dismissal-as-annotation, the seal — belong to the consuming platform's **record and dispute layers**, not to this library. LBTAS supplies the vocabulary and the distribution; the record supplies answerability. A consuming platform that adopts the scale without an answerable-claim pipeline has not implemented the covenant.

## Stand-ins and open residuals

- **Cross-implementation golden vectors are a target, not yet a gate.** Parity across the four implementations is a stated rule enforced by review; a shared vector suite that fails CI on drift (the protocol repo's pattern) is the committed check. Until it exists, parity is review-enforced and labeled so.
- **Adjudicator answerability** is the architecture's named symmetry breach — a rated party with no answer. It binds on consuming platforms' dispute layers; this library must not paper over it by exposing any unanswerable rating path.
- **Relation typing** (trade / adjudication-conduct / verdict-satisfaction) is carried here only as per-category distributions; full typed-relation discipline binds at the record layer of consuming platforms.

## Dependency declaration

A leaf library: no dependency on any coordinator, front end, or record implementation. Consuming economies depend on it; it depends on none of them.

## Product-specific notes (last, per the ordering rule)

Adopted per economy at the economic level. Consuming platforms pin a released version; the v2 distribution model is the floor for any new adoption.
