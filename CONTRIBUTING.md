# Contributing

Thanks for your interest. This is a research project, so the rules below protect the validity of the published numbers rather than a product roadmap.

## Hard rules

1. **Never commit the dataset** or any record-level output derived from it (`predictions.csv`, `exclusions.csv`, `outlier_flags.csv`). `data/raw/` and `runs/` are git-ignored; keep it that way. Its redistribution rights are unverified.
2. **Never commit secrets or machine-specific paths.** `tests/test_tg_baselines.py::TestRepositoryHygiene` scans the tree for both and fails the build.
3. **Do not change the experiment to improve a score.** The protocol in `configs/tg_baselines_v1.json` is fixed: 12 crop-seasons, exclusion rules, coverage thresholds, both designs, the five baselines and their fallback order. A better score obtained by changing the protocol is not a better model.
4. **No leakage.** Statistics may use only rows up to a forecast's training cutoff. Keep the run-time assertions and the temporal tests intact.
5. **No pooled metrics across crops with different units.** MAE/RMSE/bias are per crop-season. Cross-crop summaries use WAPE and skill only. No pooled R².
6. **No new runtime dependencies** without a clear justification. The project is deliberately numpy + pandas, hash-locked.

## Before opening a pull request

```bash
python -I -B -m unittest discover -s tests -v
python -I -B src/tg_baselines.py --config configs/tg_baselines_v1.json --out runs/pr_check
TCI_RUN_DIR=runs/pr_check python -I -B -m unittest discover -s tests -v
```

The last command includes `test_run_reproduces_published_results`, which requires your run to match the published files byte-for-byte.

**If your change alters the published numbers,** that is a finding, not a problem to hide. Say so explicitly in the pull request: what changed, which files differ, and why the new values are more correct. Then update `results/`, the affected reports and `CHANGELOG.md` in the same pull request, and bump the experiment id (for example `tg_baselines_v2`) rather than silently replacing `v1`.

## Kinds of contributions that fit well

- Additional baselines, as new ids alongside B0–B4, never replacing them.
- Uncertainty estimates (for example a year-block bootstrap) around skill differences.
- Support for newer or official district data with explicit units, including a documented district re-mapping for the 33 present-day districts.
- Independent verification: re-implement a baseline and check it against `predictions.csv`.
- Resolving the open questions in `data/README.md`: the dataset's licence, the exact `Crop_Year` convention, and the cotton unit.

## Style

- Python 3.11, standard library plus numpy/pandas, 4-space indent, type hints on public functions, ~120-column lines.
- Tests use `unittest` and must run offline.
- Prefer an explicit failure over a silent fallback. Integrity problems raise `IntegrityError`; an undefined metric is reported as undefined with a note, never as zero.
