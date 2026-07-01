# LBTAS Specification — reputation as a covenant, not a score

**Network Theory Applied Research Institute**
Document ID: P3-014 · Version: 0.1 (Draft) · June 2026
*Normative specification of the Leveson-Based Trade Assessment Scale. Companion to
P3-011 v2 (Janus Facing Applications), P3-012 (Agrinet Protocol Specification), and
P3-013 (Mycelium). Held to* Janus-Facing Architecture *(builder's guide, v2.0) and*
Building JFA Software *(v1.0).*

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are used
as in RFC 2119.

---

## 0. What LBTAS is

LBTAS is the **peer / reputation layer** of a Janus-Facing Architecture network. It is a
**covenant** — a standing promise not to harm — **not a score**. Its logic is the safety
engineer's (Nancy Leveson): two crashes in seventy-three flights grounds the fleet.
Volume is a signal, but no quantity of good ratings dissolves a harm into a comfortable
average.

Reputation here is binary where it counts: a member is **in good standing** or **in
breach**. The lowest rating on the scale, a `−1`, **is the breach itself** — not a debit
against a running total.

This document defines the scale, the read model, and the invariants any conformant
implementation MUST hold. The README carries the rationale; this file carries the
requirements. The reference implementations (`lbtas.py`, `.ts`, `.go`, `.rs`) are held to
it.

---

## 1. The scale

A rating is an integer on a **six-point scale**, `−1` through `+4`:

| Value | Label | Meaning |
|---|---|---|
| `+4` | Delight | Anticipates the evolution of user practices and concerns post-transaction. |
| `+3` | No Negative Consequences | Designed to prevent loss; exceeds basic quality. |
| `+2` | Basic Satisfaction | Meets socially acceptable standards exceeding articulated demands. |
| `+1` | Basic Promise | Meets all articulated demands, no more. |
| `0` | Cynical Satisfaction | Fulfils a basic promise with little to no discipline toward satisfaction. |
| `−1` | No Trust | The user was harmed, exploited, or received a product/service with no discipline or malicious intent. |

`−1` is categorically distinct from `0…+4`: the positive band grades *quality*; `−1`
records *harm*. Implementations MUST treat `−1` as a breach, never as "one below zero."

---

## 2. Distribution, never an average

A reputation is a **distribution**: the count of ratings at each level (`−1, 0, +1, +2,
+3, +4`) beside the total.

- An implementation **MUST NOT** compute or expose an average, mean, weighted score, or
  any single-number reduction of the ratings, anywhere in a read, report, badge, or API.
- Volume sits *beside* harm; it never cancels it. A harm stays permanently visible next
  to the volume.
- Reads **SHOULD** also expose the **transaction count** and **tenure** (first/last
  rated timestamps): count and tenure are themselves trust signals.

A conformance test: search the implementation for any division of a rating sum by a
count, or any field named `score`/`average`/`rating` that collapses the distribution. A
correct implementation has none. (The reference impls make this a throwing error where a
score would otherwise be computed.)

---

## 3. Role-scoped

Reputation is kept **separately per role** — the capacity in which the rated party acted
(e.g. `market_seller`/`market_buyer`, `service_provider`/`service_client`,
`plan_producer`/`plan_backer`), derived from the exchange type and the rated party's
side. A `−1` earned in one role **MUST NOT** contaminate the distribution of another. The
same person can hold several role-scoped reputations at once.

---

## 4. Harm carries a narrative; harm is never hidden

- A `−1` **MUST** carry a justifying **narrative of ≤ 500 words**. A `−1` without a
  narrative is invalid and MUST be rejected.
- The narrative is **operator-local**: held at the front end, referenced (not carried) by
  the protocol record, **never** anchored on the commons ledger, **never** federated, and
  read only by the record's own parties and the operator's adjudicator (P3-013 §6).
- The rating **event** is **immutable and append-only**. There is no update and no delete.
- A **dismissal annotates, never erases** (§6): it removes the event from the *active*
  trust distribution, but the event remains visible downstream, annotated with **who
  dismissed it and why**. A front end **MAY** forgive harm; it **MUST NOT** be able to
  hide it.

---

## 5. Symmetric — contestable both ways

The covenant runs **both ways**. A producer's `−1` of a consumer is **as contestable as**
the reverse.

- Any rated party **MAY** contest a rating made against them, in **either** direction.
- The system **MUST NOT** encode that one class (e.g. sellers) is trustworthy and the
  other (e.g. buyers) is the risk. There is no privileged direction.
- Non-delivery is itself a harm and belongs in the covenant (see §8 for what does *not*).

---

## 6. Adjudication: dismiss = annotate

An adjudicator (an **operator-local** role, never a global authority over the commons)
**MAY** dismiss a rating found to be bad-faith.

- A dismissal is recorded as a **new annotation**, never an edit or deletion (§4, P3-013
  §7). The dismissed event and the annotation are both permanent and both visible.
- A read computes the **active** distribution *excluding* dismissed events, while still
  **surfacing every dismissed event** with its dismissing party and reason and, for a
  contested-but-upheld rating, that it was upheld.

---

## 7. Timeout defaults are marked

When an exchange completes but a party does not rate within its **rating window**, the
system assigns a **default rating of `+2`** ("Basic Satisfaction"): silence is read as an
exchange that ended without complaint — **not** as praise, and **not** as harm.

- A timeout default **MUST** be **system-attributed** (`rater_role = system`) and
  **marked as a timeout default**.
- It **MUST** be **distribution-distinguishable** from an affirmed party rating in every
  read (as a dismissal is), so a reputation built partly from silence is never mistaken
  for one built from affirmation. Reads **SHOULD** surface a `defaulted` count.
- `+2` is the conservative default (it does not inflate reputation); `+3` is the
  documented alternative. This is the only tunable constant in the scale.

---

## 8. Gates whether, not how much

LBTAS gates **whether** a member transacts on trust at all — **never how much**.

- What the covenant secures is **honesty, not capacity**: "I will not harm you" is not "I
  can deliver what I promised."
- **Bounding the size** of a commitment an honest actor may take on is a **limit**, which
  belongs to the **economy layer**, not to LBTAS. The limit **MUST** be derived from
  something *other* than the harm distribution (clean volume, declared capacity, a flat
  starting line).
- An implementation **MUST NOT** derive a spending/credit limit or ceiling from the LBTAS
  distribution. Letting good standing buy a higher ceiling turns the harm distribution
  into a credit score — the bank through the back door. The covenant gates the door; the
  limit sizes the room; keep them separate.

---

## 9. Relationship to settlement

Where LBTAS gates an escrow release (P3-012 §7): the consumer's rating is the release
trigger. A `0…+4` releases held funds; a `−1` **does not** release — it freezes the funds
and opens an audit. A producer's post-hoc rating of the consumer moves no money. This is a
*settlement* rule that consumes LBTAS; it is not part of the scale itself.

---

## 10. Guarantees and non-guarantees

**Guarantees.** A conformant LBTAS surfaces harm permanently and visibly, never averages
it away, keeps it role-scoped, makes every claim answerable in both directions, and
distinguishes affirmed ratings from silence and from dismissals.

**Non-guarantees.** LBTAS attests **honesty, not capacity** (§8), and it does not attest
the honesty of the computation that produced an exchange (a rigged match or price) — that
is out of scope, checked only by legibility and cheap exit (P3-013 §9).

---

## 11. Conformance

An implementation is conformant iff **all** hold:

1. Ratings are integers `−1…+4`; `−1` is treated as a breach, not a low score (§1).
2. Reputation is exposed **only** as a distribution — no average, mean, or single score
   anywhere (§2).
3. Reputation is **role-scoped** (§3).
4. A `−1` requires a narrative ≤ 500 words; the narrative is operator-local and never in
   the commons (§4).
5. Rating events are append-only; dismissals **annotate, never erase**, and remain
   visible (§4, §6).
6. The covenant is **symmetric** — contestable in both directions, no privileged class
   (§5).
7. Timeout defaults are `+2`, **system-attributed and marked**, distribution-
   distinguishable (§7).
8. No limit or ceiling is derived from the distribution — it **gates whether, not how
   much** (§8).

---

## 12. Implementation status (informative)

| Element | Status |
|---|---|
| Six-point scale, labels (§1) | **Implemented** (`lbtas.py`/`.ts`/`.go`/`.rs`; README) |
| Distribution, never averaged (§2) | **Implemented** (reference impls; Agrinet `services/lbtas.js` + `utils/reputation.js` throws if a score is requested) |
| Role-scoped (§3) | **Implemented in Agrinet** (`ratingRepository.getUserReputation` per-role); **delta:** fold role-scoping into the standalone reference impls |
| `−1` narrative ≤ 500w, operator-local (§4) | **Implemented in Agrinet** (`rating_narratives`); **delta:** document in the reference impls |
| Append-only; dismiss = annotate (§4, §6) | **Implemented in Agrinet** (`voidById`/`upholdContest`, dismissed surfaced); **delta:** reference impls |
| Symmetric contest (§5) | **Implemented in Agrinet** (`contestRating` both directions) |
| Timeout default `+2`, marked (§7) | **Implemented in Agrinet** (`applyRatingTimeouts`, `defaulted` count) |
| Gates whether, not how much (§8) | **Conformant by absence** — no rating-derived limit exists anywhere |

The standalone reference implementations here cover the scale and the distribution
faithfully; the covenant lifecycle (role-scoping, narrative, contest/dismiss, timeout
default) is currently most complete in the Agrinet backend and is being reconciled back
into the reference impls.

---

*Network Theory Applied Research Institute, Inc. — 501(c)(3) — info@ntari.org*
*Free documentation under the project's AGPL-3.0 commons — meant to be read, reimplemented, and contested.*
