# LBTAS Deployment Guide

This guide covers building, running, and deploying LBTAS **v2.0.0** — the
distribution release. Reputation is a count of ratings at each level (`-1`..`+4`)
plus the total; ratings are never averaged. `CLAUDE.md` is the source of truth
for the model and the production API; this guide is operational only.

The repository at `NTARI-RAND/Leveson-Based-Trade-Assessment-Scale` ships four
behaviourally identical reference CLIs. The production surface is a networked API
served on the **NTARIHQ** machine (see `CLAUDE.md` → *What the API does*); the
API service itself is not yet in this repository, so the steps below cover the
reference implementations.

---

## What ships

| File | Language | Build/run toolchain |
|------|----------|---------------------|
| `lbtas.py` | Python ≥3.8 | standard library only |
| `lbtas.go` | Go ≥1.21 | `go.mod` (standard library only) |
| `lbtas.rs` | Rust 2021 | `Cargo.toml` (serde, serde_json, chrono, csv) |
| `lbtas.ts` | TypeScript ≥5 / Node ≥16 | `package.json`, `tsconfig.json` |

`LICENSE` is the canonical AGPL-3.0 text. `CHANGELOG.md` records the release
history. The CLI JSON storage shape (`exchange → { category: [int…], _metadata }`)
is shared across all four implementations.

---

## Build and run

### Python
```bash
python3 lbtas.py --help
python3 -m py_compile lbtas.py        # smoke check
python3 lbtas.py add --exchange "MyService" --criterion reliability --rating 3
python3 lbtas.py view --exchange "MyService"   # prints the distribution + counts
```

### Go
```bash
go vet ./...
go build -o lbtas ./...               # uses go.mod
./lbtas report
```

### Rust
```bash
cargo build --release                 # uses Cargo.toml; binary target is lbtas.rs
./target/release/lbtas report
```

### TypeScript
```bash
npm install
npm run build                         # tsc --strict must exit 0
node lbtas.js report
```

Smoke test that no implementation averages: a dataset of `20×(-1)` and
`5000×(+3)` on one category must render `-1: 20` and `+3: 5000` with
`total: 5020`, and `report` must list that exchange under `harm_flagged` with a
count of `20`.

---

## Pre-flight review checklist

1. **License posture.** The AGPL-3.0 designation is treated as a correction of a
   prior documentation error, not a relicensing. That framing is clean only if
   NTARI is the sole copyright holder. Confirm:
   ```bash
   git log --format="%an <%ae>" | sort -u
   ```
   If external contributors appear, the license history needs their consent;
   pause and reach out before proceeding.
2. **No averaging regressed in.** `grep -niE 'average|mean|system_average'` over
   the four CLI files should match only ban-explaining comments — no logic.
3. **Versions in sync.** Every version string is `2.0.0` (`lbtas.py`
   `__version__`, `init.py`, `package.json`, `Cargo.toml`, `lbtas.rs` `VERSION`,
   `lbtas.go` `Version`, `lbtas.ts` `VERSION`).
4. **Builds find their files.** `Cargo.toml`, `go.mod`, and `lbtas.py` exist
   under those exact names (no `view ` prefix, no uppercase `LBTAS.py`).

---

## Landing changes

Work on a branch and open a pull request; do not push to `main` directly. Let CI
and reviewers gate the merge.

```bash
git checkout -b <feature-branch>
# ...changes...
git add -A
git commit -m "..."
git push -u origin <feature-branch>
gh pr create --base main --head <feature-branch>
```

## Post-merge verification

After the PR merges, verify on github.com:

1. The README renders correctly (tables, code blocks, links).
2. The license badge shows **AGPL-3.0** (GitHub auto-detects from `LICENSE`).
3. `CHANGELOG.md` renders cleanly and the top entry is the released version.

Then update external references as needed — e.g. any internal NTARI docs that
still say "MIT" or plain "GPL-3.0" for LBTAS should be corrected to AGPL-3.0.

## If something goes wrong

Prefer a follow-up commit over a force-push, especially for anything with legal
weight (the license). For a substantive defect, revert the offending commit and
land a corrected one:

```bash
git revert <commit-sha>
```

---

## References

- LBTAS whitepaper: https://www.ntari.org/post/lbtas-leveson-based-trade-assessment-scale
- NTARI Licensing and Enforcement Strategy (P2-004): https://www.ntari.org/post/licensing-and-enforcement-strategy-ntari-policy-p2-004
- AGPL-3.0 canonical text: https://www.gnu.org/licenses/agpl-3.0.txt
- Canonical model and API contract: `CLAUDE.md`
