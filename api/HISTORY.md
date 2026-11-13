# Rating history pagination

`GET /ratings/{rated_party}/{role}` accepts opt-in pagination. It uses the
existing `X-API-Key` read capability and local SQLite store. It does not add
party-scoped authentication, adjudicator identity binding, federation, or an
external store.

Calls without pagination retain complete `events` and `dismissed` arrays and
existing fields. Both read modes add `harm_index` and `dismissed_distribution`.
Dismissed entries additionally retain any prior contest/uphold trail. These are
additive response changes, not byte-for-byte unchanged legacy responses.
Unpaged reads still use memory proportional to history size.

## Request and response

Add `limit` to enable paging: an integer from 1 through 100, applied separately
to each array. There is no implicit paged default. For example:

```sh
curl --get --header "X-API-Key: $LBTAS_API_KEY" \
  --data-urlencode 'limit=25' \
  'http://localhost:8000/ratings/Bob/market_seller'
```

The response retains these **full-history** fields on every page:

- `distribution`: counts for all six levels among active, non-dismissed events.
- `total`: number of active rating events.
- `transaction_count`: distinct exchange IDs among active events, not page length.
- `first_rated_at`, `last_rated_at`: active-history timestamp extrema, or null
  when all events are dismissed. Existing stored-text ordering is preserved.
- `defaulted_count`: active system-attributed timeout defaults.
- `dismissed_count`: number of dismissed events, including those outside this page.
- `dismissed_distribution`: six independent counts (`-1` through `4`) for all
  dismissed events. Its sum equals `dismissed_count`; no levels are pooled.
- `harm_index`: every −1 event, active or dismissed, plus every dismissed event
  at any level, each once. It ignores `limit` and both cursors, including on an
  exhausted page. Entries are newest rating first by `(stored timestamp, event_id)`
  descending, with deterministic ID ordering for equal timestamps.

Each `harm_index` entry includes `event_id`, `exchange_id`, `rated_at`, `value`,
`state` (`active` or `dismissed`), and boolean `contested`/`upheld` markers.
Dismissed entries also include `dismissed_by`, `reason`, and `dismissed_at`.
Full rating comments and detailed contest/uphold annotations remain in the event
arrays. An empty harm index is `[]`; absent dismissal levels have count zero.
The index is scoped to the requested party and role, under the same read gate.

`events` and `dismissed` each contain at most `limit` entries. Active events retain
timeout markers and contest/uphold details. Dismissed events retain the original
rating, comment, dismissing party, reason and dismissal time. Pagination adds:

```json
{
  "pagination": {
    "limit": 25,
    "next_active_cursor": "a:42",
    "next_dismissed_cursor": "d:57"
  }
}
```

The cursor values above are illustrative. Treat returned cursors as opaque.
Send each through its corresponding `active_cursor` or `dismissed_cursor`
parameter, together with `limit`, on the same party/role route. Both parameters
may be sent in one request. Each collection advances independently; null means
that collection is exhausted. A client should stop appending that collection
once its cursor is null. Omitting its cursor starts that collection again.
A client MUST show `distribution`, `dismissed_distribution` and `harm_index`
from any page it displays, and MUST NOT present one page as the whole history
(SPEC §4, §6). Offer navigation to both active and dismissed event arrays for
full comments and annotation details. Page the volume, never the harm.

Ordering is ascending `(stored timestamp, event_id)`. Event ID breaks equal-time
ties without offset-based skips. Cursors are continuation positions, not
credentials or signed attestations; they confer no additional access. A cursor
is resolved only within the requested party/role, and its stream prefix must
match the requested parameter. An anchor remains usable if later dismissed.

Invalid limits return 422. Malformed, nonexistent or wrong-scope cursors return
400 (overlong cursors return 422). Cursors without `limit` return 400. A history
with neither active nor dismissed events returns 404. A valid exhausted page
returns empty arrays and full summaries. A dismissed-only history returns 200,
zero active counts, all-zero distribution and navigable dismissal records.

## Consistency and resource bounds

Every history request, paged or unpaged, opens one SQLite read transaction
before its first summary query and releases it after summaries, index and event
arrays have been read. A
concurrent rating, dismissal, contest or uphold cannot split that response across
different database snapshots. No persistent snapshot is held across HTTP calls.

Later requests see later committed state. Appends are ordered by their stored
timestamp and ID. A dismissal can move an older event from the active collection
to a position before an already-issued dismissal cursor. To refresh after
adjudication, restart both collections; this is a live history, not a frozen
cross-request export. A rating timestamp can precede its commit: a late commit
can fall behind an issued cursor. A complete refreshed view requires a new
traversal from the first page, even when only ratings were appended. Original
records are never deleted or modified by reads.

SQL computes full-history summaries and fetches at most `limit + 1` narrative
rows per paged collection. Python event-page allocation is bounded by those rows
and stored field sizes. The mandatory complete `harm_index` is deliberately
unpaged: response size and Python memory grow with the number of −1/dismissed
events and their identifier/reason sizes. There is no fixed whole-response
memory or byte bound, and no index truncation. The store imposes no new narrative
or identity limits. Summary SQL still scans the scoped history and distinct-exchange
aggregation can use SQLite temporary storage. This change promises no constant-time
history reads or fixed SQLite memory bound. A `(rated_party, role, timestamp, id)`
index supports ordered
reads and is created non-destructively by existing initialization on old and new
databases. Index creation can take time on large existing databases.

## Verification

Install `api/requirements.txt` and the test client dependency `httpx2`
(or `httpx` with older FastAPI/Starlette releases), then run:

```sh
python -m unittest api.test_history -v
python -m unittest api.test_initialization -v
python api/test_event_store.py
python api/test_rating_validation.py
```

Run the history and initialization suites in separate processes: initialization
sets its database environment before importing the store. These API checks are
run manually until CI runs them; the existing build workflow does not do so.

The suite covers complete off-page harm/dismissal indexes, six separate dismissed
counts, lifespan startup, role/party isolation, all six counts, distinct exchanges,
timeouts, contest/uphold details, dismissal navigation, equal timestamps,
independent cursors, invalid parameters, failed authorization, legacy reads,
exhausted and dismissed-only histories, append/dismissal changes, and a second
connection committing a write during a read. A 40,009-row scoped history checks
both 100-row bounds, exact totals, all 20,003 harm-index entries, and event-page
Python allocation below 2 MB measured separately from the complete index.
