# LBTAS Conformance Record

Status of each implementation against [`SPEC.md`](SPEC.md) (P3-014). Per the JFA
method, this ships the status plainly rather than performing the absence of a gap.

**Audited:** 2026-07-01 against SPEC v0.1. **Result:** no violations — no averaging
anywhere, no label drift, no limit derived from the harm distribution.

Legend: **yes** = implemented · **no** = not yet (code-level) · **app** = operator-app
concern, documented not implemented in a standalone reference impl.

## Matrix

| # | Invariant (SPEC §) | py | ts | go | rs | Agrinet¹ |
|---|---|:--:|:--:|:--:|:--:|:--:|
| 1 | Scale −1..+4 with exact labels (§1) | yes | yes | yes | yes | yes |
| 2 | Distribution, never an average (§2) | yes | yes | yes | yes | yes² |
| 3 | Role-scoped reputation (§3) | no | no | no | no | yes |
| 4 | −1 carries a narrative ≤500w, operator-local (§4) | app | app | app | app | yes |
| 5 | Append-only; dismissal annotates, never erases (§4, §6) | app | app | app | app | yes |
| 6 | Symmetric — contestable both ways (§5) | app | app | app | app | yes |
| 7 | Timeout default +2, system-attributed & marked (§7) | app | app | app | app | yes |
| 8 | Gates whether, not how much (§8) | yes | yes | yes | yes | yes |

¹ Agrinet = `services/lbtas.js` + `repositories/ratingRepository.js` in `NTARI-RAND/Agrinet`.
² Agrinet additionally **throws** if a single-number reputation score is ever requested (`utils/reputation.js`).

## What each layer is responsible for

The scale and the distribution read-model are the **algorithm core** — every reference
implementation carries them, and all five agree on the six labels (Delight, No Negative
Consequences, Basic Satisfaction, Basic Promise, Cynical Satisfaction, No Trust) with no
drift.

The rest of the covenant lifecycle divides by layer:

- **Code-level, belongs in a reference impl:** the scale and the distribution (§1, §2),
  and **role-scoping** (§3). Role-scoping — keying the distribution by the rated party's
  role — is the one code-level invariant not yet in the standalone reference impls; it is
  fully implemented in Agrinet and is the tracked enhancement for py/ts/go/rs.
- **Operator-app concerns, correctly *documented* not implemented in a reference impl:**
  the ≤500-word narrative and its operator-local storage (§4), append-only events with
  dismissal-as-annotation (§4, §6), bidirectional contest (§5), and the rating-window
  timeout default (§7). These require a datastore, an adjudicator role, and a clock —
  they live in the operator (Agrinet), which realizes all of them.

## Honest gaps

- **Role-scoping in py/ts/go/rs** — not yet implemented (tracked). The core reads are
  role-agnostic; an operator needing per-role distributions does so as Agrinet does.
- No implementation averages, exposes a single score, or derives a limit from the harm
  distribution — the invariants whose violation would rebuild the credit bureau all hold.

## Operator API history reads

The `api/` implementation scopes histories by party and role (SPEC §§2–3).
Every paged or unpaged response carries the complete active distribution,
counts/timestamps, six-level `dismissed_distribution`, and `harm_index` naming
every −1 and every dismissal with its state and dismissal explanation (§§4, 6).
Only detailed event arrays are paged; timeout and contest/uphold annotations
remain available (§§5–7). Summaries, index and arrays share one SQLite snapshot.
Clients MUST display both distributions and the full harm index from any page,
and MUST NOT present one page as the entire history.

Bindings: `python -m unittest api.test_history -v` (off-page accountability,
all six dismissal counts, party/role isolation, annotations, both cursors,
large history and concurrent writes); `python -m unittest api.test_initialization -v`
(startup and request-time schema boundary). Run these in separate processes.
These API checks run by hand until CI runs the `api/` tests; no hosted API-test
coverage is claimed. See [API contract and resource limits](api/HISTORY.md).
This implementation note does not change the standalone-library matrix above.
