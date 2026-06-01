# Changelog

All notable changes to LBTAS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **License correction.** The authoritative license for LBTAS is and has been
  AGPL-3.0, consistent with NTARI's Licensing and Enforcement Strategy
  (P2-004). Earlier copies of `LBTAS.py` carried an MIT license header; this
  was a documentation error inconsistent with published NTARI policy and has
  been corrected. The full AGPL-3.0 text is now present as `LICENSE` at the
  repository root, and the source file header carries the standard AGPL-3.0
  notice block. Use under the previously stated MIT terms prior to this
  correction is honored; new derivative work follows AGPL-3.0.

- **Attribution clarified.** The README and source file now state explicitly
  that Professor Nancy Leveson, whose safety-critical software assessment
  methodology LBTAS adapts, has been informed of this work and does not
  endorse the application of her methodology to commerce assessment. She has
  not restricted NTARI's use of the underlying framework. LBTAS is an
  independent application of methods she developed for other purposes; any
  errors in the adaptation are NTARI's alone. Her academic work is published
  independently of this project and should be consulted directly for
  authoritative treatment of safety-critical software assessment.

- **Source file authorship.** The `Author: Your Name` placeholder in earlier
  versions of `LBTAS.py` has been replaced with proper attribution to the
  Network Theory Applied Research Institute, Inc., Forge Laboratory.

### Added

- **`README.md`.** A new top-level README provides a developer-focused
  introduction to LBTAS, including the rating scale with definitions,
  installation instructions, a minimal integration example, a typical
  platform integration pattern, a recommended database schema, and
  guidance on extending the criteria. The README links to the existing
  whitepaper for the research framing and longer argument.

- **`LBTAS.submit_rating(name, criterion, rating)`.** A new method on
  `LevesonRatingSystem` provides a programmatic, non-interactive entry
  point for platform integrations. The existing `rate_exchange()` and
  `get_rating()` methods (which use stdin) are preserved for CLI and demo
  use but are no longer the recommended integration path.

- **`LBTAS.get_raw_ratings(name)`.** A new method returns the full list of
  recorded ratings for each criterion, enabling integrating platforms to
  compute their own statistics (medians, distributions, weighted averages)
  beyond the simple averages returned by `view_ratings()`.

- **Extensible criteria.** `add_exchange()` now accepts an optional
  `criteria` argument, allowing integrating platforms to define
  domain-specific assessment dimensions (e.g., ecological impact for
  agricultural networks, accessibility for civic platforms) while
  retaining the core rating logic, validation, and aggregation.

- **Input validation on `submit_rating()`.** The new programmatic entry
  point validates that the exchange exists, the criterion is registered
  for that exchange, and the rating is an integer within the -1 to +4
  range. Validation errors raise `ValueError` with descriptive messages.

### Documentation

- Module docstring in `LBTAS.py` rewritten to match the README's framing,
  with the full 6-point scale documented inline.
- Attribution paragraph added to the source file header.
- Repository and whitepaper URLs included in the source file header for
  developers landing in the source before the README.

---

## [3.0] - 2025-06

Educational Research Edition. See the
[LBTAS whitepaper](https://www.ntari.org/post/lbtas-leveson-based-trade-assessment-scale)
for the research framing of this release.

## [Earlier versions]

Earlier versions are not separately documented here. The
`LevesonRatingSystem` class, the 6-point scale from -1 to +4, the four
default criteria (reliability, usability, performance, support), and the
interactive `rate_exchange()` workflow predate this changelog.

---

[Unreleased]: https://github.com/NTARI-ForgeLab/Leveson-Based-Trade-Assessment-Scale/compare/v3.0...HEAD
[3.0]: https://github.com/NTARI-ForgeLab/Leveson-Based-Trade-Assessment-Scale/releases/tag/v3.0
