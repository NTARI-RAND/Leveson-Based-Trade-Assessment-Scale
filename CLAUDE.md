# CLAUDE.md — Canonical guidance for the Leveson-Based Trade Assessment Scale

This file is the **source of truth** for working on LBTAS. When any other
document, code comment, or committed implementation conflicts with this file,
this file wins — treat the conflict as a bug in the other artifact, not here.
Read it before writing or modifying code in this repository.

**Conformance self-description: see `CONFORMANCE.md`** — the repo's role in
Janus-Facing Architecture (the covenant layer's assessment scale), the
invariant-to-binding table, and the named stand-ins. A change that alters any
binding there updates that file in the same PR. The architecture's covenant
invariants (never average; the lowest rating is the breach; symmetric;
whether-never-how-much; non-portable by default) are not negotiable by
feature request; a request to reintroduce an average, a single score, or a
ranking derived from one is refused and surfaced, not implemented.

## What LBTAS is

LBTAS is a reputation system for digital commerce adapted from Nancy Leveson's
aircraft-software assessment methodology, where a system failure means loss of
life or wasted R&D rather than a bruised ego. It rates interactions on a 6-point
ordinal scale and is **bidirectional**: both producers and consumers are rated,
so a single completed exchange can produce two ratings — one for the producer
rating the consumer, and one for the consumer rating the producer.

| Level | Label | Meaning |
|------:|-------|---------|
| +4 | Delight | Anticipates the evolution of user practices and concerns post-transaction |
| +3 | No Negative Consequences | Designed to prevent loss; exceeds basic quality |
| +2 | Basic Satisfaction | Meets socially acceptable standards beyond articulated demands |
| +1 | Basic Promise | Meets all articulated demands, no more |
|  0 | Cynical Satisfaction | Fulfills a basic promise with little to no discipline toward satisfaction |
| -1 | No Trust | User was harmed, exploited, or received service with no discipline or malicious intent |

Ratings are integers from -1 to +4; higher is better. The scale is
meaning-loaded — each level carries a specific definition and must not be
treated as an interchangeable point on a continuous axis.

The project ships four reference CLI implementations that must stay
**behaviourally identical**: `lbtas.py`, `lbtas.go`, `lbtas.rs`, `lbtas.ts`.
A networked API (below) is the production surface and the canonical successor to
the CLIs. The CLI files are a reference for the scale definitions and storage
shape; their behaviour must follow this document, not the other way around.

## What the API does

The API runs on the **NTARIHQ machine** and is responsible for three things:

1. **Serving rating prompts on triggers.** When a transaction or interaction
   event fires, the API presents the appropriate LBTAS prompt to the relevant
   party. Because LBTAS is bidirectional, one completed exchange can trigger two
   prompts: the producer to rate the consumer, and the consumer to rate the
   producer.
2. **Storing ratings locally.** Persistence stays on NTARIHQ — no external
   rating store, no third-party dependency for the data layer. The local store
   is the system of record.
3. **Serving records to authorized users for review.** Reading rating history
   is gated behind authorization. Unauthenticated or unauthorized callers must
   not be able to read records.

## Do not average ratings

**Ratings are never averaged.** This is the central design rule and it is
non-negotiable.

A reputation is a **distribution**: the count of ratings received at each of the
six levels (`-1, 0, +1, +2, +3, +4`), together with the **total** number of
ratings. There is no `system_average`, no per-category mean, no per-exchange
mean, no average-ranked "top/bottom performers", and no convenience "overall
average" field anywhere — not in a return value, not in a report, not in a
printed display.

Why averaging is banned:

- **It buries the safety signal.** A `-1` ("No Trust") means a user was harmed.
  Averaging lets a single `-1` be diluted by surrounding praise, so a provider
  who harmed someone can still present a comfortable 3.8. In a Leveson-derived
  system, harm is a discrete event to be surfaced, not smoothed away. The
  distribution keeps every `-1` visible, and `report.harm_flagged` raises it
  explicitly.
- **A mean compresses away the shape.** Two parties with very different rating
  shapes can share the same average. The distribution preserves exactly what the
  mean discards.
- **A mean is dimensionless with respect to count** — see the next section.

### The rating count is itself a signal

The `total` for a rated party is not a denominator — it is information. It
records how many rated interactions the party has accumulated, which means it
carries two things at once: **transaction volume** (how much the party
transacts) and a **proxy for time in service** (a large count generally cannot
accumulate without sustained participation in the network over time). A high
total with no `-1`s is therefore a stronger trust signal than the same clean
distribution at a low total: the seasoned, high-volume provider and the
brand-new one are different parties, and the count is exactly what distinguishes
them.

This is a further reason averaging is forbidden. A mean is dimensionless with
respect to count: a party with 5 ratings and a party with 5,000 ratings that
share the same distribution shape collapse to the same average. Averaging
discards the very magnitude that encodes volume and tenure. Distributions
preserve it — always report the count alongside the per-level breakdown.

Respect the limits of the proxy. The count is a count of *ratings*, not raw
transactions; precise transaction volume is the number of rating events
(distinct triggering exchanges), which the event store captures. And `total`
correlates with longevity but does not measure it — a burst of volume in a short
window also produces a high count. A precise *time in service* requires
timestamps. Each rating event in the store carries a timestamp and a triggering
exchange id, so API reads can expose `first_rated_at`, `last_rated_at`, and an
event/transaction count beside `total`. The reference CLI files store only a
per-exchange `created` date; surface that as a coarse "in service since" and
leave precise volume and tenure to the API.

## Reading and reporting reputation — the output contract

All four CLI implementations must produce these exact shapes (key order in JSON
is not significant; presence and values are).

`view_ratings(name)` returns a per-category distribution plus its total:

```json
{
  "<category>": {
    "distribution": { "-1": 0, "0": 0, "1": 0, "2": 0, "3": 0, "4": 0 },
    "total": 0
  }
}
```

`generate_report()` returns overall, per-category, and per-exchange
distributions, plus the harm list:

```json
{
  "total_exchanges": 0,
  "total_ratings": 0,
  "overall_distribution":   { "-1": 0, "0": 0, "1": 0, "2": 0, "3": 0, "4": 0 },
  "category_distributions": { "<category>": { "-1": 0, "0": 0, "1": 0, "2": 0, "3": 0, "4": 0 } },
  "exchange_distributions": { "<exchange>": { "distribution": { "...": 0 }, "total": 0 } },
  "harm_flagged": [ ["<exchange>", 0] ],
  "generated_at": "ISO-8601"
}
```

- `harm_flagged` lists every exchange that received one or more `-1` ratings,
  sorted by `-1` count descending (ties broken by name ascending for stable
  output).
- **Display order** for printed distributions is best-to-worst (`+4` down to
  `-1`), one line per level: `level  label : count`.
- `list` shows the total number of ratings per exchange and appends a harm flag
  (e.g. `, 20x -1 No Trust`) when the exchange has any `-1`. It shows no average.
- `view` and `report` label the total explicitly as transaction volume
  (`Total ratings (transaction volume): N`) and surface the stored `created`
  date as `In service since: <date>`.
- Interactive / demo output prints counts, never an average.

## The -1 comment requirement

A rating of **-1 must carry a justifying comment of 500 words or less.**

- The comment is **mandatory** for `-1`. Reject any attempt to submit a `-1`
  without one.
- Enforce the **500-word maximum** at the API boundary. Reject submissions that
  exceed it rather than silently truncating.
- For ratings 0 through +4, comments are optional unless product requirements
  say otherwise.

The reasoning: `-1` is the only level that asserts harm or bad faith against
another party in the network. Requiring a bounded, written justification makes
the most consequential rating accountable and reviewable, and gives authorized
reviewers the context they need without permitting an unbounded dumping ground.
(The reference CLI store predates this requirement and has no comment field;
enforcement lives at the API boundary.)

## Data model — the API event store

Because reputation is a distribution and `-1`s carry comments, the store keeps
**individual rating events**, not running tallies. Each event captures at least:

- the **rated party** (the subject of the reputation),
- the **rater** (bidirectional: producer or consumer),
- the **rating value** (`-1`..`+4`),
- the **category**, if categories are in use,
- the **comment** (required when value is `-1`, ≤500 words),
- a **timestamp**,
- the **triggering exchange / transaction id**.

Distributions are computed from these events on read; the events also preserve
the audit trail authorized reviewers depend on. Because events carry timestamps
and transaction ids, API reads for a rated party expose — alongside the
distribution and `total` — `first_rated_at`, `last_rated_at`, and a
transaction/event count (distinct triggering exchanges). This is where precise
transaction volume and time in service live; the CLI's per-category totals are a
coarser stand-in and must not be claimed to equal transaction count.

## Authorization

Reading records is a privileged operation. Implement an explicit authorization
layer between callers and the rating store. Submitting a rating in response to a
served prompt and reviewing accumulated records are **distinct capabilities and
must be authorized separately**. When in doubt, **fail closed** — an
unauthenticated or unauthorized caller must never read records.

## Critical divergence from the existing code

The originally committed CLI code computed averages everywhere — `system_average`,
`category_averages`, per-exchange means, and average-ranked `top_performers` /
`bottom_performers`, plus average-based `view`, `list`, and demo output. **That
was wrong.** As of v2.0.0 all of it has been replaced by the distribution model
described above. If you ever find mean/average logic reappearing in a read or
report path, it is a regression: remove it. The acceptance bar is that
`grep -iE 'average|mean|system_average'` finds no averaging logic in any CLI read
or report path (a comment that *explains* the ban is fine).

## Storage format (CLI — do not change)

The CLI persists JSON of the shape:

```json
{ "<exchange>": { "<category>": [int, ...], "_metadata": { "created": "...", "total_ratings": 0 } } }
```

Distributions are **computed on read** from these raw rating lists; they are not
stored. Do not change this storage shape — it is what lets the four
implementations read each other's data files. In particular, do **not** add
per-rating timestamps to the CLI store; honest per-rating timestamps belong only
to the API event records (see *Data model*).

## CSV export honesty

CSV export columns are `exchange, category, rating, index`, where `index` is the
1-based position of a rating within its category. There is deliberately **no
timestamp column**: the CLI store does not record per-rating times, so a column
of `datetime.now()` values written at export time would falsely imply each
rating was made then. All four implementations must use the same header.

## Versioning

The distribution change is a **breaking** change to the read API. The project is
at **2.0.0**. Keep every version string in sync when bumping: `__version__` in
`lbtas.py`, `version` in `package.json`, `version` in `Cargo.toml`, `VERSION` in
`lbtas.rs`, `Version` in `lbtas.go`, `VERSION` in `lbtas.ts`, and `__version__`
in `init.py`.

## Licensing

The project is **AGPL-3.0** — the GNU **Affero** General Public License v3.0, not
the plain GPL v3. Network use counts as distribution, which is the relevant case
for a networked API, so AGPL-3.0 is correct and wins any conflict with stray
`GPL-3.0` strings. Every source file should declare AGPL-3.0, and the `LICENSE`
file must be the full AGPL-3.0 text.

## Contact

Network Theory Applied Research Institute — info@ntari.org
