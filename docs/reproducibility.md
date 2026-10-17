# Reproducibility guide

Everything here runs offline, reads the dataset read-only, and writes only inside the project.

## 1. Environment

Python **3.11** with exactly two direct dependencies, pinned and hash-locked:

| Package | Version |
|---|---|
| numpy | 2.2.6 |
| pandas | 2.3.3 |
| *(transitive)* python-dateutil | 2.9.0.post0 |
| *(transitive)* pytz | 2026.5 |
| *(transitive)* six | 1.17.0 |
| *(transitive)* tzdata | 2026.5 |

The published results were produced with CPython 3.11.0 on Windows (x86-64).

**With uv (recommended):**

```bash
uv venv --python 3.11 .venv
uv pip sync requirements.lock.txt --python .venv/Scripts/python.exe --require-hashes --only-binary :all:   # Windows
uv pip sync requirements.lock.txt --python .venv/bin/python --require-hashes --only-binary :all:           # macOS/Linux
```

**With pip:**

```bash
python3.11 -m venv .venv
.venv/Scripts/python -m pip install --require-hashes --only-binary :all: -r requirements.lock.txt   # Windows
.venv/bin/python     -m pip install --require-hashes --only-binary :all: -r requirements.lock.txt   # macOS/Linux
```

`--require-hashes` verifies every wheel against the SHA-256 values in the lock file; `--only-binary :all:` forbids source builds. The lock file pins the whole graph, so no resolver decisions are made at install time.

The tests assert that the installed numpy and pandas versions match the lock file, so a mismatched environment fails loudly instead of producing different numbers quietly.

## 2. Dataset

The dataset is **not** in this repository. Obtain it as described in [`../data/README.md`](../data/README.md), then:

```bash
python -I -B scripts/verify_dataset.py                       # expects data/raw/india_crop_production_district.csv
python -I -B scripts/verify_dataset.py --data /path/to.csv   # or anywhere else
```

The expected SHA-256 is `af4d84ed95ca0cf4ae823a332189ae79fd773531e1effc44163fe2e6b4ddbedd`. Every entry point verifies it and refuses to run on a different file, so a near-identical copy cannot silently change the results.

### Configuring the path without hardcoding it

Three options, in increasing precedence:

1. The default: `dataset.path` in `configs/tg_baselines_v1.json`, a path **relative to the project root** (`data/raw/india_crop_production_district.csv`).
2. `--data PATH` on `tg_baselines.py`, `verify_dataset.py` and `summarize_results.py`.
3. `TCI_DATA=PATH` for the test suite.

No script contains an absolute or machine-specific path.

## 3. Running

Run from the project root with the project interpreter. `-I` isolates the interpreter from user site-packages and `PYTHON*` environment variables; `-B` stops `__pycache__` from being written.

```bash
# one run produces BOTH evaluation designs (fixed origin and rolling origin)
python -I -B src/tg_baselines.py --config configs/tg_baselines_v1.json --out runs/run_a

# a second run for the reproducibility check
python -I -B src/tg_baselines.py --config configs/tg_baselines_v1.json --out runs/run_b
python -I -B src/compare_runs.py --config configs/tg_baselines_v1.json \
    --run-a runs/run_a --run-b runs/run_b --report runs/reproducibility_report

# derived tables and figures
python -I -B scripts/summarize_results.py --config configs/tg_baselines_v1.json --run runs/run_a --out runs/run_a_analysis
python -I -B scripts/make_figures.py
```

An output directory must not already exist; the scripts refuse to overwrite one. Exit codes: `0` success, `2` integrity or coverage failure (**no scores are written**), `3` runs differ (`compare_runs.py`), `4` report target exists.

## 4. Tests

```bash
python -I -B -m unittest discover -s tests -v                       # 45 tests
TCI_RUN_DIR=runs/run_a python -I -B -m unittest discover -s tests -v  # also validates that run
```

The suite runs in three modes, and skips are reported as skips, never as passes:

| Mode | Tests | Skipped | What it checks |
|---|---:|---:|---|
| No dataset | 45 | 18 | Baseline arithmetic, fallback order, leakage logic, metric formulas, published-result integrity, repository hygiene |
| Dataset present | 45 | 11 | …plus schema, hash, duplicate keys, exclusion counts, coverage rules on the real data |
| Dataset + `TCI_RUN_DIR` | 45 | 0 | …plus output schema, forecast cutoffs, traceability, independent recomputation of all 4,290 predictions, manifest hashes, and byte-for-byte agreement with the published results |

Setting `TCI_RUN_DIR` is the strongest check: `test_run_reproduces_published_results` requires every file in `results/tg_baselines_v1/` to be byte-identical to your own run's corresponding file.

## 5. Output files

A run writes eleven files:

| File | Published here | Contents |
|---|---|---|
| `predictions.csv` | no (record-level) | One row per design × crop-season × district × target year × baseline (4,290 rows), with source line, rule, fallback chain and baseline-specific provenance |
| `metrics_by_crop_season.csv` | yes | Per design × crop-season × baseline |
| `metrics_by_crop_season_year.csv` | yes | …split by test year |
| `baseline_summary.csv` | yes | Cross-crop overview, unit-free only |
| `coverage.csv` | yes | All 216 coverage-rule checks |
| `data_audit.json` | yes | Hash, schema, scope funnel, exclusion counts, year coverage |
| `data_quality_report.md` | yes | The same audit in prose |
| `exclusions.csv` | no (record-level) | Every excluded row with its reason |
| `outlier_flags.csv` | no (record-level) | Flagged rows (never removed or capped) |
| `run_manifest.json` | yes | SHA-256 of config, source files, dataset and **all** outputs, including unpublished ones; package versions; assertions passed |
| `run_timing.json` | no | Start/finish times, elapsed seconds, output path, argv |

The unpublished files can be regenerated exactly; their expected hashes are in the published `run_manifest.json`.

## 6. What is deterministic

**Deterministic** — identical across runs on the same data, code, config and environment:
everything above except `run_timing.json`. Repeat runs are compared file by file, by name and SHA-256.

**Not deterministic, and excluded from comparison:** `run_timing.json` only (wall-clock timestamps, elapsed seconds, the output path and argv). `compare_runs.py` reads the excluded list from `output.nondeterministic_files` in the config and applies it identically to both runs, so the exclusion cannot be used selectively.

No step uses randomness: there is no sampling, shuffling, random splitting or seeded initialisation anywhere, which is why `random_seed` is `null` in the config. Row order is fixed by explicit sorts, floats are written with `%.6f`, JSON keys are sorted, and all files use LF line endings (enforced by `.gitattributes`, so a Windows checkout does not alter the hashes).

Two caveats worth knowing:

- Results are byte-identical for a given numpy/pandas build. Different builds or platforms could in principle differ in the last floating-point digits; the `%.6f` output format absorbs ordinary differences, and the version assertions catch mismatched environments.
- `run_manifest.json` records the config path and dataset path **as given on the command line**, so invoking the same run through different paths changes that file while leaving every data-bearing file identical.

## 7. Provenance of the published results

The published files came from a verification run of this public code, which reproduced every data-bearing output of the original private experiment byte-for-byte: `predictions.csv`, both metrics tables, `baseline_summary.csv`, `coverage.csv`, `exclusions.csv`, `outlier_flags.csv` and `data_audit.json` were identical. Only `data_quality_report.md` and `run_manifest.json` differed, and only in path strings and the hashes of the refactored source files. The experiment logic is unchanged; the public version differs only in path handling.
