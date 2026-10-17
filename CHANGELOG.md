# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-10-17

First release: the complete `tg_baselines_v1` experiment, its published aggregate results and documentation.

### Added

- **Experiment** (`src/tg_baselines.py`): five historical baselines (B0–B4) over 12 Telangana crop-seasons and 9 districts, in two time-based designs — fixed origin (primary, trained through 2009) and rolling origin (secondary). Includes run-time integrity and temporal assertions, coverage rules that abort before scoring on failure, and a SHA-256 run manifest.
- **Reproducibility comparison** (`src/compare_runs.py`): file-by-file comparison of two runs, excluding only the documented non-deterministic file.
- **Scripts**: `verify_dataset.py` (SHA-256 and schema check), `summarize_results.py` (derived tables), `make_figures.py` (SVG figures from published aggregates, no plotting dependency).
- **Tests** (`tests/test_tg_baselines.py`): 45 tests covering baseline arithmetic and fallback order, leakage and temporal isolation, metric formulas including undefined cases, real-data schema and counts, output schema and traceability, independent recomputation of all 4,290 predictions, published-result integrity and repository hygiene. They degrade to skips, not passes, when the dataset is absent.
- **Published results** (`results/tg_baselines_v1/`): aggregate metrics, coverage checks, data audit, run manifest, analysis tables and a reproducibility report. Record-level outputs are withheld.
- **Documentation**: README, research report, executive summary, reproducibility guide, data acquisition guide, contributing and security policies, citation metadata.

### Results summary

Fixed origin (primary), medians across 12 crop-seasons: B2 (recent five-year district mean) achieved **22.6% WAPE** and beat the B1 district-mean reference in **9 of 12** crop-seasons (median skill +0.150). Under rolling origin the advantage narrowed to 7 of 12 and +0.031. Full numbers in `results/tg_baselines_v1/baseline_summary.csv`.

### Known limitations

Test-set exposure during development, with unknown influence on design decisions; inferred production units with cotton left in unconverted bales; unconfirmed `Crop_Year` convention; data ending in 2014 with 2012 missing and only the 10 pre-2016 districts; a small, correlated test sample; no weather or input features; district-level rather than farm-level estimates; unresolved source-repository and dataset licences. See the README and research report §9–10.

### Notes on provenance

The experiment was developed and run in a private workspace. This repository's code differs from that version only in path handling (relative paths, a `--data` option, no machine-specific paths in manifests). A verification run reproduced every data-bearing output of the original run byte-for-byte; only path strings and the source-file hashes differ.
