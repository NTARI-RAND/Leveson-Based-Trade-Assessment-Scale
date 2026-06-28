# CLAUDE.md — Canonical guidance for the Leveson-Based Trade Assessment Scale

This file is the **source of truth** for working on LBTAS. When any other
document, code comment, or committed implementation conflicts with this file,
this file wins — treat the conflict as a bug in the other artifact, not here.

## What LBTAS is

LBTAS is a reputation system for digital commerce adapted from Nancy Leveson's
aircraft-software assessment methodology, where a system failure means loss of
life or wasted R&D rather than a bruised ego. It rates interactions on a 6-point
scale and is **bidirectional**: both producers and consumers are rated.

| Level | Label | Meaning |
|------:|-------|---------|
| +4 | Delight | Anticipates the evolution of user practices and concerns post-transaction |
| +3 | No Negative Consequences | Designed to prevent loss; exceeds basic quality |
| +2 | Basic Satisfaction | Meets socially acceptable standards beyond articulated demands |
| +1 | Basic Promise | Meets all articulated demands, no more |
|  0 | Cynical Satisfaction | Fulfills a basic promise with little to no discipline toward satisfaction |
| -1 | No Trust | User was harmed, exploited, or received service with no discipline or malicious intent |

The project ships four reference CLI implementations that must stay
**behaviourally identical**: `LBTAS.py`, `lbtas.go`, `lbtas.rs`, `lbtas.ts`.
A networked API (see *Data model*, below) is the production surface.

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

## Critical divergence from the existing code

The originally committed CLI code computed averages everywhere — `system_average`,
`category_averages`, per-exchange means, and average-ranked `top_performers` /
`bottom_performers`, plus average-based `view`, `list`, and demo output. **That
was wrong.** As of v2.0.0 all of it has been replaced by the distribution model
described above. If you ever find mean/average logic reappearing in a read or
report path, it is a regression: remove it. The acceptance bar is that
`grep -iE 'average|mean|system_average'` finds no averaging logic in any CLI read
or report path (a comment that *explains* the ban is fine).

## Storage format (do not change)

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

## Data model (the API event store)

The production API stores each rating as an **event** carrying, at minimum:

- a per-event **timestamp**,
- a **triggering exchange / transaction id**,
- the rated party, the criterion, and the level (`-1`..`+4`).

Because events carry timestamps and transaction ids, API reads for a rated party
expose — alongside the distribution and `total` — `first_rated_at`,
`last_rated_at`, and a transaction/event count (distinct triggering exchanges).
This is where precise transaction volume and time in service live; the CLI's
per-category totals are a coarser stand-in and must not be claimed to equal
transaction count.

Out of scope for the CLI (API event-model features): the `-1` mandatory-comment /
500-word-limit enforcement, and the FastAPI service itself.

## Versioning

The distribution change is a **breaking** change to the read API. The project is
at **2.0.0**. Keep every version string in sync when bumping: `__version__` in
`LBTAS.py`, `version` in `package.json`, `version` in `Cargo.toml`, `VERSION` in
`lbtas.rs`, `Version` in `lbtas.go`, `VERSION` in `lbtas.ts`, and `__version__`
in `init.py`.

## Licensing

The project is **AGPL-3.0**. Network use counts as distribution, which is the
relevant case for a networked API, so AGPL-3.0 is correct and wins any conflict
with stray `GPL-3.0` strings. Every source file should declare AGPL-3.0.
