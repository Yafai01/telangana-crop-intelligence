# Published results — tg_baselines_v1

These are the **aggregate** outputs of the experiment: metrics, counts and audits. Every file here except this README and `run_manifest.json` is listed in `run_manifest.json` with its SHA-256, and the tests check that they match.

| File | What it contains |
|---|---|
| `baseline_summary.csv` | Cross-crop overview per design and baseline. Unit-free only: median WAPE, median skill vs B1, counts beating B1, fallbacks, negatives |
| `metrics_by_crop_season.csv` | Per design × crop-season × baseline: n, districts, test years, training-set sizes, MAE / RMSE / bias / MSE in the crop's own unit, WAPE, skill vs B1, fallbacks, negatives |
| `metrics_by_crop_season_year.csv` | The same, per test year |
| `coverage.csv` | All 216 coverage-rule checks (all passed) |
| `data_audit.json`, `data_quality_report.md` | Dataset hash and schema, scope funnel, exclusion counts, eligible counts, Telangana year coverage |
| `run_manifest.json` | Hashes of config, source code, dataset and all outputs (including unpublished ones); package versions; assertions passed |
| `analysis/` | Derived tables used in the report (`scripts/summarize_results.py`) |
| `reproducibility/` | Two runs of this repository's code compared file by file: 10 of 10 substantive files identical |

**Withheld** (record-level; the dataset's redistribution rights are unverified): `predictions.csv`, `exclusions.csv`, `outlier_flags.csv`, and the non-deterministic `run_timing.json`. They can be regenerated exactly from the dataset. Their expected SHA-256 values are in `run_manifest.json`.

Native-unit metrics (MAE, RMSE, bias, MSE) are in t/ha, except `Cotton(lint)`, which is in bales/ha (unconverted). Never pool them across crop-seasons.
