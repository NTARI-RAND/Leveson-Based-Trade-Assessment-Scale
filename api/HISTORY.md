# Rating history pagination

`GET /ratings/{rated_party}/{role}` accepts opt-in pagination. It uses the
existing `X-API-Key` read capability and local SQLite store. It does not add
party-scoped authentication, adjudicator identity binding, federation, or an
external store.

Calls without pagination retain the existing response shape and complete
`events` and `dismissed` arrays. Those legacy reads still use memory proportional
to history size. Existing event and annotation fields remain unchanged.

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
Do not silently present the first page as the entire history: show full counts
and offer navigation to both active and dismissed records.

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

Each paged request opens one SQLite read transaction before its first summary
query and releases it after all summaries and both pages have been read. A
concurrent rating, dismissal, contest or uphold cannot split that response across
different database snapshots. No persistent snapshot is held across HTTP calls.

Later requests see later committed state. Appends are ordered by their stored
timestamp and ID. A dismissal can move an older event from the active collection
to a position before an already-issued dismissal cursor. To refresh after
adjudication, restart both collections; this is a live history, not a frozen
cross-request export. Original records are never deleted or modified by reads.

SQL computes full-history summaries and fetches at most `limit + 1` rows per
collection. Python page memory is bounded by those rows and their stored field
sizes; the store does not impose new narrative or identity limits. Summary SQL
still scans the scoped history and distinct-exchange aggregation can use SQLite
temporary storage. This change promises no constant-time history reads or fixed
SQLite memory bound. A `(rated_party, role, timestamp, id)` index supports ordered
reads and is created non-destructively by existing initialization on old and new
databases. Index creation can take time on large existing databases.

## Verification

Install `api/requirements.txt` and the test client dependency `httpx2`, then run:

```sh
python -m unittest api.test_history -v
python api/test_event_store.py
python api/test_rating_validation.py
```

The suite covers role/party isolation, all six counts, distinct exchanges,
timeouts, contest/uphold details, dismissal navigation, equal timestamps,
independent cursors, invalid parameters, failed authorization, legacy reads,
exhausted and dismissed-only histories, append/dismissal changes, and a second
connection committing a write during a read. A 40,009-row scoped history checks
both 100-row bounds, exact totals and Python allocation below 2 MB.
