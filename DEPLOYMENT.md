# LBTAS Repository Update — Deployment Guide

This guide walks you through landing the five files in this package into the
`NTARI-ForgeLab/Leveson-Based-Trade-Assessment-Scale` repository on GitHub.

The change is a license correction, a README addition, and a source file
cleanup — substantively a single commit, though you may want to split it
into two if you prefer separate license-and-attribution and code-changes
history entries.

---

## Files In This Package

| File | Purpose | Destination |
|------|---------|-------------|
| `README.md` | Developer-focused project README | repo root (replaces any existing README) |
| `LBTAS.py` | Corrected source file with AGPL header, `submit_rating()`, extensible criteria | repo root (replaces existing `LBTAS.py`) |
| `LICENSE` | Canonical AGPL-3.0 license text (661 lines) | repo root (new file, replaces any prior `LICENSE`) |
| `CHANGELOG.md` | Documentation of the license correction and additions | repo root (new file) |
| `DEPLOYMENT.md` | This file | **do not commit** |

---

## Pre-Flight Review Checklist

Run through this list before pushing. Each item is a thing that could go
wrong if you don't check it.

### 1. Confirm sole copyright holder status

The README and CHANGELOG treat the MIT-to-AGPL transition as correcting a
documentation error rather than as a relicensing. This framing is legally
clean only if NTARI is the sole copyright holder on the existing code.

```bash
cd /path/to/Leveson-Based-Trade-Assessment-Scale
git log --format="%an <%ae>" | sort -u
```

If the output shows only NTARI contributors (you, named NTARI volunteers,
or NTARI service accounts), proceed. If it shows external contributors,
the language in `README.md` ("Note on prior versions") and `CHANGELOG.md`
("License correction") needs to be revised to reflect an explicit
relicensing with their consent. Pause and reach out to them before
proceeding in that case.

### 2. Diff the source file against your current `LBTAS.py`

I reconstructed `LBTAS.py` from the search-result fragments and the
behavior documented in your whitepaper. I added three new methods
(`submit_rating`, `get_raw_ratings`, and the `criteria` parameter on
`add_exchange`) that did not exist in the original. The original
`get_rating`, `rate_exchange`, `view_ratings`, and `add_exchange` methods
are preserved with the same external behavior.

Before committing, diff against your actual current source:

```bash
diff /path/to/current/LBTAS.py /path/to/package/LBTAS.py
```

Look for any subtle differences in the original methods (return values,
exception messages, edge cases) and adjust if needed. The added methods
are additive and should not affect existing integrations.

### 3. Verify the demo still works

```bash
cd /path/to/package
python3 LBTAS.py
# Enter an exchange name when prompted, then rate it on the four criteria.
# Confirm it prints averages at the end.
```

### 4. Verify the README example runs

```bash
cd /path/to/package
python3 -c "
from LBTAS import LevesonRatingSystem
rs = LevesonRatingSystem()
rs.add_exchange('vendor_acme_farms')
rs.submit_rating('vendor_acme_farms', 'reliability', 3)
rs.submit_rating('vendor_acme_farms', 'usability', 2)
rs.submit_rating('vendor_acme_farms', 'performance', 4)
rs.submit_rating('vendor_acme_farms', 'support', 3)
print(rs.view_ratings('vendor_acme_farms'))
"
# Expected: {'reliability': 3.0, 'usability': 2.0, 'performance': 4.0, 'support': 3.0}
```

### 5. Verify the LICENSE file is the canonical AGPL-3.0

```bash
md5sum /path/to/package/LICENSE
# Expected: 73f1eb20517c55bf9493b7dd6e480788
```

If the hash differs, re-fetch from
https://www.gnu.org/licenses/agpl-3.0.txt before committing.

---

## Deployment Commands

### Option A: Single commit to main

If you have direct push access and want to land everything together:

```bash
cd /path/to/Leveson-Based-Trade-Assessment-Scale
git checkout main
git pull origin main

# Copy the four files into the repo (adjust source path as needed)
cp /path/to/package/README.md ./README.md
cp /path/to/package/LBTAS.py ./LBTAS.py
cp /path/to/package/LICENSE ./LICENSE
cp /path/to/package/CHANGELOG.md ./CHANGELOG.md

# Stage and review
git add README.md LBTAS.py LICENSE CHANGELOG.md
git status
git diff --cached

# Commit
git commit -m "Correct license to AGPL-3.0; add README, CHANGELOG; clean source header

- License: replace MIT placeholder header in LBTAS.py with AGPL-3.0
  notice block; add canonical AGPL-3.0 text as LICENSE. The
  authoritative license is and has been AGPL-3.0 per NTARI Policy
  P2-004; the prior MIT designation was a documentation error.
- Attribution: clarify that Professor Leveson does not endorse this
  application of her methodology and has not restricted NTARI's use.
- README: add developer-focused project README with rating scale,
  installation, integration patterns, schema, and extensibility.
- Source: add submit_rating() and get_raw_ratings() methods for
  non-interactive platform integration; add optional criteria
  parameter to add_exchange() for domain-specific extensibility.
- CHANGELOG: document all changes."

git push origin main
```

### Option B: Pull request workflow

If you prefer review before merge (recommended if other NTARI members
should sign off):

```bash
cd /path/to/Leveson-Based-Trade-Assessment-Scale
git checkout main
git pull origin main
git checkout -b license-correction-readme-update

cp /path/to/package/README.md ./README.md
cp /path/to/package/LBTAS.py ./LBTAS.py
cp /path/to/package/LICENSE ./LICENSE
cp /path/to/package/CHANGELOG.md ./CHANGELOG.md

git add README.md LBTAS.py LICENSE CHANGELOG.md
git commit -m "Correct license to AGPL-3.0; add README, CHANGELOG; clean source header"
git push -u origin license-correction-readme-update
```

Then open a pull request on GitHub. Use the commit message above as the
PR description, or expand it with the full rationale from `CHANGELOG.md`.

### Option C: Split into two commits

If you want the history to separate the license correction from the
feature additions:

```bash
# Commit 1: License + attribution
cp /path/to/package/LICENSE ./LICENSE
# Edit LBTAS.py to update only the docstring header (lines 1-72 of the
# package version); leave the class body alone for now.
git add LICENSE LBTAS.py
git commit -m "Correct license to AGPL-3.0; clarify Leveson attribution

The authoritative license is and has been AGPL-3.0 per NTARI Policy
P2-004; the prior MIT designation in the source header was a
documentation error. Add canonical AGPL-3.0 LICENSE file. Clarify in
the source docstring that Professor Leveson does not endorse this
application of her methodology and has not restricted NTARI's use."

# Commit 2: README + new methods + CHANGELOG
cp /path/to/package/LBTAS.py ./LBTAS.py  # full version with new methods
cp /path/to/package/README.md ./README.md
cp /path/to/package/CHANGELOG.md ./CHANGELOG.md
git add LBTAS.py README.md CHANGELOG.md
git commit -m "Add README, CHANGELOG; add programmatic submit_rating() and extensibility

- README: developer-focused project introduction with rating scale,
  installation, integration patterns, schema, and extensibility.
- submit_rating(name, criterion, rating): non-interactive entry point
  for platform integrations.
- get_raw_ratings(name): expose full rating lists for custom analytics.
- add_exchange(name, criteria): optional criteria parameter for
  domain-specific extensibility.
- CHANGELOG: document all changes."

git push origin main  # or your feature branch
```

---

## Post-Push Verification

After pushing, verify on github.com:

1. The repo's main page renders the new README correctly (tables, code
   blocks, links all working).
2. The repo's license badge now shows AGPL-3.0 (GitHub auto-detects this
   from the LICENSE file; may take a few minutes).
3. The `LBTAS.py` source page shows the new docstring at the top.
4. The CHANGELOG renders cleanly.

Then update any external references:

- The NTARI blog post on LBTAS — update the "Document Information" footer
  to reference the new README and CHANGELOG if appropriate.
- The "How to Build Community Using AI" article that mentions LBTAS — no
  changes needed; it already points to the right places.
- Any internal NTARI documentation that references the LBTAS license — search
  for "MIT" and update to "AGPL-3.0".

---

## If Something Goes Wrong

If you push and discover an error, the cleanest recovery is a follow-up
commit rather than a force-push. The license correction is the only
change with legal weight, and it should not be force-pushed away even if
something else needs fixing.

For small typo fixes in the README or CHANGELOG, just commit the fix on
top:

```bash
# fix the typo, then
git add README.md
git commit -m "README: fix typo"
git push origin main
```

For a more substantial issue — say, the source file has a bug — revert
the problematic commit and commit a corrected version:

```bash
git revert <commit-sha>
# then prepare the corrected version and commit normally
```

---

## Questions

If anything in this package needs clarification, the relevant references
are:

- LBTAS whitepaper: https://www.ntari.org/post/lbtas-leveson-based-trade-assessment-scale
- NTARI Licensing and Enforcement Strategy (P2-004): https://www.ntari.org/post/licensing-and-enforcement-strategy-ntari-policy-p2-004
- AGPL-3.0 canonical text: https://www.gnu.org/licenses/agpl-3.0.txt
