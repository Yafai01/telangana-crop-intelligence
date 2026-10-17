# Data quality and exclusion report - tg_baselines_v1

Generated deterministically by `src/tg_baselines.py`.

## Source dataset

- Path: `data/raw/india_crop_production_district.csv`
- SHA-256: `af4d84ed95ca0cf4ae823a332189ae79fd773531e1effc44163fe2e6b4ddbedd` (matches config: True)
- Rows: 246091; columns: State_Name, District_Name, Crop_Year, Season, Crop, Area, Production
- Crop_Year range (all states): 1997-2015
- Duplicate keys (State_Name, District_Name, Crop_Year, Season, Crop) after whitespace normalisation: 0 rows in full dataset, 0 in core scope

## Telangana coverage

- Raw state label(s): ["'Telangana '"]
- Telangana rows: 5649
- Telangana years present: [1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2013, 2014]
- Expected-absent years confirmed absent: True
- Districts (raw): ADILABAD, HYDERABAD, KARIMNAGAR, KHAMMAM, MAHBUBNAGAR, MEDAK, NALGONDA, NIZAMABAD, RANGAREDDI, WARANGAL
- Crop-district-years with both 'Whole Year' and a seasonal record: 8 (crops: Castor seed); none are core crop-seasons

## Scope funnel

| Step | Rows |
|---|---:|
| dataset_rows | 246091 |
| rows_other_states | 240442 |
| rows_target_state | 5649 |
| target_state_rows_excluded_season | 1084 |
| target_state_rows_excluded_crop | 77 |
| target_state_rows_non_core_crop_season | 2674 |
| target_state_rows_core_crop_season | 1814 |

## Core-scope exclusions (primary reason)

| Reason | Rows |
|---|---:|
| district_excluded | 8 |
| production_missing | 2 |
| production_zero | 0 |
| production_negative | 0 |
| area_missing | 0 |
| area_below_minimum | 2 |
| **total excluded** | 12 |
| **eligible panel rows** | 1802 |

## Excluded core rows by crop-season and split

| crop_season_id | split | reason | rows |
|---|---|---|---:|
| kharif_dry_chillies | train(<=2009) | district_excluded | 1 |
| kharif_jowar | test/later | area_below_minimum | 2 |
| kharif_moong | train(<=2009) | production_missing | 1 |
| kharif_rice | train(<=2009) | district_excluded | 4 |
| rabi_gram | train(<=2009) | production_missing | 1 |
| rabi_rice | train(<=2009) | district_excluded | 3 |

## Eligible observations per crop-season

| crop_season_id | unit | train (<=2009) | test (2010, 2011, 2013, 2014) | districts |
|---|---|---:|---:|---:|
| kharif_rice | t/ha | 117 | 36 | 9 |
| kharif_maize | t/ha | 117 | 36 | 9 |
| kharif_cotton_lint | bales/ha | 117 | 36 | 9 |
| kharif_arhar_tur | t/ha | 108 | 36 | 9 |
| kharif_jowar | t/ha | 112 | 33 | 9 |
| kharif_moong | t/ha | 116 | 36 | 9 |
| kharif_dry_chillies | t/ha | 107 | 36 | 9 |
| rabi_rice | t/ha | 117 | 36 | 9 |
| rabi_maize | t/ha | 117 | 36 | 9 |
| rabi_jowar | t/ha | 115 | 36 | 9 |
| rabi_groundnut | t/ha | 117 | 36 | 9 |
| rabi_gram | t/ha | 113 | 36 | 9 |

## Coverage rules

- Minimum eligible training years per district: 10
- Minimum districts per test year: 7
- Minimum test observations per evaluation: 30
- Checks evaluated: 216; failed: 0

Lowest observed values per check and design:

| design | check | lowest value | threshold |
|---|---|---:|---:|
| fixed_origin | min_districts_per_test_year | 7 | 7 |
| fixed_origin | min_test_obs_per_evaluation | 33 | 30 |
| fixed_origin | min_train_years_per_district | 10 | 10 |
| rolling_origin | min_districts_per_test_year | 7 | 7 |
| rolling_origin | min_test_obs_per_evaluation | 33 | 30 |
| rolling_origin | min_train_years_per_district | 10 | 10 |

## Unit caveats

The source has no unit column. Units below are inferred, not verified:

- **kharif_rice** (t/ha): Production assumed to be tonnes (no unit column in source). Whether rice is recorded as paddy or milled rice is not stated.
- **kharif_maize** (t/ha): Production assumed to be tonnes (no unit column in source).
- **kharif_cotton_lint** (bales/ha): Recorded production units per hectare. Magnitudes are consistent with bales (government statistics convention: 170 kg lint per bale), but the unit is NOT stated in the source and is NOT converted.
- **kharif_arhar_tur** (t/ha): Production assumed to be tonnes (no unit column in source).
- **kharif_jowar** (t/ha): Production assumed to be tonnes (no unit column in source).
- **kharif_moong** (t/ha): Production assumed to be tonnes (no unit column in source).
- **kharif_dry_chillies** (t/ha): Production assumed to be tonnes of dry chillies (no unit column in source).
- **rabi_rice** (t/ha): Production assumed to be tonnes (no unit column in source). Whether rice is recorded as paddy or milled rice is not stated.
- **rabi_maize** (t/ha): Production assumed to be tonnes (no unit column in source).
- **rabi_jowar** (t/ha): Production assumed to be tonnes (no unit column in source).
- **rabi_groundnut** (t/ha): Production assumed to be tonnes (no unit column in source); pod vs kernel basis not stated.
- **rabi_gram** (t/ha): Production assumed to be tonnes (no unit column in source).

- Area cutoff: The 10 ha cutoff is a methodological choice to drop tiny, noisy plots; it is not a proven universal rule.
