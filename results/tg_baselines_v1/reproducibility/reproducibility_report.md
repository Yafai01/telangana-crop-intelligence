# Reproducibility comparison

- Run A: `runs/verify_a`
- Run B: `runs/verify_b`
- File sets equal expected list: A=True, B=True
- Excluded (non-deterministic, identically for both runs): run_timing.json
- Compared: 10; match: 10; mismatch: 0; missing: 0
- **Reproducible: True**

| File | Status | Bytes | SHA-256 (run A) | SHA-256 (run B) |
|---|---|---:|---|---|
| baseline_summary.csv | MATCH | 712 | `9f21d60cadad1d92577b264550c92dd06b1aec0072a15be05616ffa168b47fa8` | `9f21d60cadad1d92577b264550c92dd06b1aec0072a15be05616ffa168b47fa8` |
| coverage.csv | MATCH | 15423 | `fcb2550a50413d102bc4f8044594fd400465c1b7be7c3534719e1c91e9c34626` | `fcb2550a50413d102bc4f8044594fd400465c1b7be7c3534719e1c91e9c34626` |
| data_audit.json | MATCH | 3934 | `5900190e2b92c1f6e3dd7a5caa48c5a7c221844eb782c2042ba15f2abf274cc4` | `5900190e2b92c1f6e3dd7a5caa48c5a7c221844eb782c2042ba15f2abf274cc4` |
| data_quality_report.md | MATCH | 4987 | `bd7f82ee877e897de107787348a68ad62ff358622d674be902409be9ebc2c4fd` | `bd7f82ee877e897de107787348a68ad62ff358622d674be902409be9ebc2c4fd` |
| exclusions.csv | MATCH | 1490 | `e163ee0514bdf5f5bf5ea95f22a0606fac3458541cac0a203f446800343054f1` | `e163ee0514bdf5f5bf5ea95f22a0606fac3458541cac0a203f446800343054f1` |
| metrics_by_crop_season.csv | MATCH | 19760 | `0541cae5110341187f4e3a72ce605d0e6570aa99022ca398529eb3dd62d7fce5` | `0541cae5110341187f4e3a72ce605d0e6570aa99022ca398529eb3dd62d7fce5` |
| metrics_by_crop_season_year.csv | MATCH | 67336 | `d54dfbece80788e39e7d4c4d4273ec7b64a173c5827ca3e805eefb7cf13dcc61` | `d54dfbece80788e39e7d4c4d4273ec7b64a173c5827ca3e805eefb7cf13dcc61` |
| outlier_flags.csv | MATCH | 269 | `a0dd56bffe4da3a1ecdfedd5fa3e99ca87711adf16e7ce49500193376a54cacd` | `a0dd56bffe4da3a1ecdfedd5fa3e99ca87711adf16e7ce49500193376a54cacd` |
| predictions.csv | MATCH | 947891 | `9431132e7bc717718323e7d421cf28e1704e78e0e1d57dbfbe6dfcfbdb1503af` | `9431132e7bc717718323e7d421cf28e1704e78e0e1d57dbfbe6dfcfbdb1503af` |
| run_manifest.json | MATCH | 2309 | `2c00ba7fa0d81a4825e2202474291b7f25f41053c374ec3deafbfc0a797c8aaa` | `2c00ba7fa0d81a4825e2202474291b7f25f41053c374ec3deafbfc0a797c8aaa` |
| run_timing.json | EXCLUDED_NONDETERMINISTIC |  | `` | `` |
