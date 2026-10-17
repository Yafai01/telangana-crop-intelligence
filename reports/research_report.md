# Telangana Crop Intelligence — Historical Baseline Evaluation (tg_baselines_v1)

**Project:** Telangana Crop Intelligence (final-year B.Tech major project)
**Experiment:** `tg_baselines_v1` — transparent historical baselines for district-level crop yield in Telangana
**Date of runs:** 2026-10-16
**Status:** Complete. Two identical runs; 37/37 automated tests passed against each run (in the original private experiment workspace).

> **Publication note.** The experiment was run in a private workspace. This public version of the code differs only in path handling: relative paths, a `--data` option, and no machine-specific paths in manifests. A verification run of the public code reproduced every data-bearing output of the original official run byte-for-byte (`predictions.csv`, both metrics tables, `baseline_summary.csv`, `coverage.csv`, `exclusions.csv`, `outlier_flags.csv`, `data_audit.json`); only path strings in `data_quality_report.md` and `run_manifest.json` changed. Record-level outputs and the private development records cited below (execution log, file inventory, test logs) are **not** published, because they contain values from, or are tied to, a dataset whose redistribution rights are unverified.
**Research-integrity note:** the test years were excluded from every computation (no computational leakage), but they were **not unseen** during development — see Section 9.

Labels used throughout:
**[Verified]** = checked directly against the source data or files by code/tests.
**[Calculated]** = computed by the experiment code from the verified data.
**[Assumption]** = a methodological choice or an inference that the data cannot confirm.
**[Limitation]** = a known weakness that affects how the results may be used.

---

## 1. Abstract

We measured how well five simple, fully transparent historical baselines forecast district-level crop yield (production ÷ area) in Telangana for 12 crop–season combinations across 9 districts, using only past observations from the district-level Indian crop production dataset (1997–2014 for Telangana). Forecasts were scored on temporally held-out years 2010, 2011, 2013 and 2014 under a primary fixed-origin design (all information up to 2009) and a secondary rolling-origin design (information strictly before each target year). These years were excluded from every estimate by construction, but they were not a sealed, unseen hold-out: test-period data and one development run's summary scores were viewed during development (Section 9).

The district historical mean (B1) — the natural reference — had a median weighted absolute percentage error (WAPE) of **25.8%** across crop-seasons (fixed origin). A **recent five-year district mean (B2)** was the most consistent improvement: it beat B1 in **9 of 12** crop-seasons with a median skill of **+0.15** (fixed origin), but only **7 of 12** with a median skill of **+0.03** under rolling origin. B1 under-predicted in **41 of 48** crop-season × year cells, indicating that test-period yields were generally higher than long-run history. Last-observed (B3) and trend-extrapolation (B4) baselines were unstable: B3 was damaged by an atypical 2009 season, and B4 badly over-predicted pulses with steep historical trends.

These results define the minimum accuracy any future model must beat. They are **not** production-ready forecasts.

## 2. Objective and scope

Determine how accurately simple, transparent historical baselines can forecast district-level crop yield in Telangana, using a temporally valid, leakage-resistant, reproducible design that is honest about data limitations. No machine-learning model was trained; no weather, irrigation, fertiliser or other external feature was used; the original repository's model and its filtered 50,000-row training file were not used as evidence.

## 3. Data

### 3.1 Source [Verified]

| Item | Value |
|---|---|
| File | `india_crop_production_district.csv` (read-only; not redistributed here — see `data/README.md`) |
| SHA-256 | `af4d84ed95ca0cf4ae823a332189ae79fd773531e1effc44163fe2e6b4ddbedd` (matches the previously recorded hash) |
| Rows / columns | 246,091 rows; `State_Name, District_Name, Crop_Year, Season, Crop, Area, Production` |
| Years (all states) | 1997–2015 |
| Duplicate keys (state, district, year, season, crop) after whitespace stripping | **0** in the full dataset; 0 in the core scope |
| Telangana label | stored as `'Telangana '` (trailing space); whitespace stripped in memory only |
| Telangana rows | 5,649 |
| Telangana years | 1997–2011, 2013, 2014 — **2012 is absent** (confirmed by assertion and test); 2015 absent |
| Telangana districts | 10 pre-2016 districts; HYDERABAD has records only for 1997–2000 and is excluded |
| Whole Year + seasonal overlaps | 8 crop-district-years, all **Castor seed, 2013**; none are core crop-seasons |

### 3.2 Scope funnel and exclusions [Verified]

| Step | Rows |
|---|---:|
| Dataset rows | 246,091 |
| Other states | 240,442 |
| Telangana rows | 5,649 |
| — excluded season (`Whole Year`) | 1,084 |
| — excluded crops (Turmeric, Soyabean; Kharif/Rabi rows) | 77 |
| — other (non-core) crop-seasons | 2,674 |
| Core crop-season rows | 1,814 |
| — excluded: district HYDERABAD | 8 |
| — excluded: Production missing | 2 (Kharif Moong, Nalgonda 2009; Rabi Gram, Warangal 1998) |
| — excluded: Production zero | 0 |
| — excluded: Area below 10 ha | 2 (Kharif Jowar 2014: Karimnagar 4 ha, Khammam 1 ha) |
| **Eligible panel rows** | **1,802** |

Every excluded row is listed with its reason in `exclusions.csv` of a local run (record-level; not published).
Labels were matched exactly after whitespace stripping; look-alike labels (`Dry ginger`, `Horse-gram`, `Moong(Green Gram)` vs `Gram`) were **not** merged.

### 3.3 Eligible observations per crop-season [Verified]

| Crop-season | Unit | Train rows (1997–2009) | Test rows (2010, 2011, 2013, 2014) | Districts |
|---|---|---:|---:|---:|
| Kharif Rice | t/ha | 117 | 36 | 9 |
| Kharif Maize | t/ha | 117 | 36 | 9 |
| Kharif Cotton(lint) | bales/ha | 117 | 36 | 9 |
| Kharif Arhar/Tur | t/ha | 108 | 36 | 9 |
| Kharif Jowar | t/ha | 112 | **33** | 9 |
| Kharif Moong(Green Gram) | t/ha | 116 | 36 | 9 |
| Kharif Dry chillies | t/ha | 107 | 36 | 9 |
| Rabi Rice | t/ha | 117 | 36 | 9 |
| Rabi Maize | t/ha | 117 | 36 | 9 |
| Rabi Jowar | t/ha | 115 | 36 | 9 |
| Rabi Groundnut | t/ha | 117 | 36 | 9 |
| Rabi Gram | t/ha | 113 | 36 | 9 |

Kharif Jowar has 33 test rows: Karimnagar 2011 is absent from the source, and Karimnagar/Khammam 2014 fall below the 10 ha cutoff.

### 3.4 Units [Assumption]

The source has **no unit column**. Yield is reported as *recorded production units per hectare*:

- Cereals, pulses, oilseeds, dry chillies: production is assumed to be **tonnes**, giving t/ha. Magnitudes are agronomically plausible (e.g. Kharif Rice 0.95–4.09 t/ha in the eligible panel). Whether rice is recorded as paddy or milled rice, and groundnut as pods or kernels, is not stated.
- **Cotton(lint)**: magnitudes (0.46–3.48 per ha) are consistent with **bales** (the government statistics convention is 170 kg lint per bale) and implausible as tonnes of lint. The unit is **not converted**; cotton metrics are in bales/ha.
- Because units differ, no metric in native units is pooled across crop-seasons.

## 4. Methodology

### 4.1 Coverage rules [Verified: all passed]

Each crop-season evaluation required: ≥10 eligible training years for **every** one of the 9 panel districts within each forecast's information set; ≥7 districts in each test year; ≥30 test observations. Failure would abort scoring (no automatic dropping). All **216** checks passed in both designs. The binding cases were Kharif Jowar 2014 (exactly 7 districts) and Kharif Jowar / Rabi Gram (minimum exactly 10 training years). These thresholds were set after viewing row counts (including test-year coverage) and before any baseline scores existed; descriptive yield statistics that included test years had already been viewed at that point (Section 9.2).

### 4.2 Evaluation designs

| Design | Role | Target years | Training cutoff | Forecast origin |
|---|---|---|---|---|
| Fixed origin | **Primary** | 2010, 2011, 2013, 2014 | 2009 for all | 2009 |
| Rolling origin | Secondary | 2010 / 2011 / 2013 / 2014 | 2009 / 2010 / 2011 / 2013 | 2009 / 2010 / 2012 / 2013 |

The information set for a forecast is the eligible rows of the same crop-season with `Crop_Year ≤ training cutoff`. For the rolling 2013 forecast the origin (target − 1 = 2012) is a year with no records; the code asserts that no eligible row lies between cutoff and origin, so the information set equals "all years ≤ 2011".

### 4.3 Baselines

| ID | Definition | Fallback |
|---|---|---|
| B0 | Mean yield of all information-set rows of the crop-season | — |
| B1 | District mean of information-set rows (≥5 rows required) | B0 |
| B2 | District mean over the five calendar-year labels `[origin−4, origin]` (≥3 rows required) | B1, then B0 |
| B3 | District's most recent yield within `[origin−2, origin]` | B1, then B0 |
| B4 | B1 + β·(target year − district's mean information-set year), where β is the Telangana-wide **within-district** OLS slope: β = Σ_d Σ_i (t_i − t̄_d)(y_i − ȳ_d) / Σ_d Σ_i (t_i − t̄_d)² over the information set | B0 + β·(target − mean information-set year) if B1 falls back; B0 alone if β is undefined |

Centering by district prevents persistent level differences between districts from being mistaken for a time trend (verified by a unit test in which the uncentred pooled slope has the wrong sign). Negative B4 predictions are **not clipped**; they are flagged.

**Interpretation decisions [Assumption]** (resolved from the previously approved design, documented here):
- B2 and B3 windows are anchored at the forecast origin (2009 for fixed origin; target − 1 for rolling).
- B3 uses a three-year lookback `[origin−2, origin]`; if the district has no observation there it falls back to B1 rather than reaching further back. This affected only Karimnagar Kharif Jowar.

### 4.4 Leakage controls [Verified by assertions and tests]

- No random splitting; all splits are by year.
- Means, slopes, windows, fallbacks and outlier flags use training-period rows only. Outliers are **flagged, never removed or capped**.
- Run-time assertions: information-set max year ≤ cutoff < target; target rows never in the information set; B3 source year ≤ origin; same target rows in both designs; five baselines per target row; no rows between cutoff and origin.
- Tests show predictions are **unchanged when test-period yields are replaced by extreme values**, and rolling forecasts are unaffected by later years.
- Every one of the 4,290 predictions was **independently recomputed** by a separate pure-Python implementation reading the raw CSV with the `csv` module; maximum difference < 1e-6 (the written precision).
- Each prediction records its source CSV line, training cutoff, forecast origin, rule (including fallback chain), and baseline-specific provenance (B2 window, B3 source line/year, B4 slope and centre year).

These controls establish the absence of **computational** leakage (test-year values entering a prediction). They do not make the test years unseen by the people developing the method; that separate issue is documented in Section 9.

### 4.5 Metrics

With e = prediction − observed: MAE = mean|e|; RMSE = √mean(e²); bias = mean(e) (positive = over-prediction); WAPE = Σ|e| / Σ|observed| (left blank with an explanatory note if the denominator is zero — it never was); skill vs B1 = 1 − MSE_baseline / MSE_B1 on identical rows (undefined if MSE_B1 = 0 — it never was). "Beats B1" means skill > 0. Native-unit metrics are reported per crop-season only; cross-crop summaries use only unit-free WAPE and skill. No pooled MAE, RMSE or R² was computed.

## 5. Results [Calculated]

Source files: `results/tg_baselines_v1/` (`metrics_by_crop_season.csv`, `metrics_by_crop_season_year.csv`, `baseline_summary.csv`, `predictions.csv`) and derived tables in `results/tg_baselines_v1/analysis/`.

### 5.1 Overview across 12 crop-seasons (unit-free)

| Design | Baseline | Median WAPE | Median skill vs B1 | Beats B1 | Worse than B1 | Fallback predictions | Negative predictions |
|---|---|---:|---:|---:|---:|---:|---:|
| Fixed (primary) | B0 crop-season mean | 0.279 | −0.207 | 2 | 10 | 0 | 0 |
| Fixed (primary) | **B1 district mean** | **0.258** | 0 (reference) | — | — | 0 | 0 |
| Fixed (primary) | **B2 recent 5-yr mean** | **0.226** | **+0.150** | **9** | 3 | 2 | 0 |
| Fixed (primary) | B3 last observed | 0.283 | −0.098 | 4 | 8 | 2 | 0 |
| Fixed (primary) | B4 mean + trend | 0.274 | −0.210 | 5 | 7 | 0 | 0 |
| Rolling (secondary) | B0 | 0.274 | −0.250 | 2 | 10 | 0 | 0 |
| Rolling (secondary) | B1 | 0.255 | 0 (reference) | — | — | 0 | 0 |
| Rolling (secondary) | B2 | 0.252 | +0.031 | 7 | 5 | 2 | 0 |
| Rolling (secondary) | B3 | 0.313 | −0.394 | 4 | 8 | 1 | 0 |
| Rolling (secondary) | B4 | 0.251 | +0.011 | 6 | 6 | 0 | 0 |

All fallbacks were Karimnagar Kharif Jowar (B2 and B3 → B1). No baseline produced a negative prediction in either design; the lowest fixed-origin B4 prediction was 0.138 t/ha (Kharif Moong). No metric was undefined.

### 5.2 Skill vs B1 by crop-season — fixed origin (primary)

| Crop-season | B0 | B2 | B3 | B4 |
|---|---:|---:|---:|---:|
| Kharif Rice | −0.235 | **+0.629** | +0.221 | +0.485 |
| Kharif Maize | −0.523 | +0.173 | −1.255 | +0.104 |
| Kharif Cotton(lint) | −0.178 | +0.105 | −0.292 | −0.332 |
| Kharif Arhar/Tur | +0.040 | +0.052 | −0.089 | −0.868 |
| Kharif Jowar | +0.053 | −0.220 | −0.727 | −0.405 |
| Kharif Moong | −0.123 | −0.086 | −3.006 | −0.234 |
| Kharif Dry chillies | −1.548 | +0.249 | −0.931 | −0.533 |
| Rabi Rice | −0.258 | +0.553 | +0.207 | **+0.637** |
| Rabi Maize | −0.309 | **+0.568** | +0.443 | +0.567 |
| Rabi Jowar | −0.333 | −0.307 | −0.107 | −0.186 |
| Rabi Groundnut | −0.058 | +0.197 | −0.084 | +0.138 |
| Rabi Gram | −0.085 | +0.126 | +0.068 | −2.167 |

### 5.3 RMSE in native units — fixed origin (primary)

| Crop-season | Unit | B0 | B1 | B2 | B3 | B4 |
|---|---|---:|---:|---:|---:|---:|
| Kharif Rice | t/ha | 0.627 | 0.564 | **0.343** | 0.498 | 0.404 |
| Kharif Maize | t/ha | 1.318 | 1.068 | **0.971** | 1.604 | 1.011 |
| Kharif Cotton(lint) | bales/ha | 0.678 | 0.625 | **0.591** | 0.710 | 0.721 |
| Kharif Arhar/Tur | t/ha | 0.199 | 0.204 | **0.198** | 0.212 | 0.278 |
| Kharif Jowar | t/ha | **0.376** | 0.387 | 0.427 | 0.508 | 0.458 |
| Kharif Moong | t/ha | 0.227 | **0.214** | 0.223 | 0.429 | 0.238 |
| Kharif Dry chillies | t/ha | 1.036 | 0.649 | **0.562** | 0.902 | 0.804 |
| Rabi Rice | t/ha | 0.632 | 0.564 | 0.377 | 0.502 | **0.340** |
| Rabi Maize | t/ha | 1.245 | 1.088 | **0.716** | 0.812 | 0.716 |
| Rabi Jowar | t/ha | 0.356 | **0.308** | 0.352 | 0.324 | 0.336 |
| Rabi Groundnut | t/ha | 0.428 | 0.416 | **0.373** | 0.434 | 0.387 |
| Rabi Gram | t/ha | 0.430 | 0.412 | **0.386** | 0.398 | 0.734 |

(Rabi Maize: B2 and B4 are equal to three decimals.) Lowest-RMSE baseline per crop-season (fixed origin): B2 in 8, B1 in 2, B0 in 1, B4 in 1.

### 5.4 WAPE — fixed origin (primary)

| Crop-season | B0 | B1 | B2 | B3 | B4 |
|---|---:|---:|---:|---:|---:|
| Kharif Rice | 0.168 | 0.150 | 0.093 | 0.140 | 0.113 |
| Kharif Maize | 0.340 | 0.278 | 0.255 | 0.397 | 0.265 |
| Kharif Cotton(lint) | 0.267 | 0.249 | 0.232 | 0.293 | 0.278 |
| Kharif Arhar/Tur | 0.303 | 0.332 | 0.308 | 0.315 | 0.482 |
| Kharif Jowar | 0.283 | 0.309 | 0.308 | 0.428 | 0.371 |
| Kharif Moong | 0.351 | 0.341 | 0.339 | 0.717 | 0.389 |
| Kharif Dry chillies | 0.365 | 0.200 | 0.174 | 0.297 | 0.270 |
| Rabi Rice | 0.164 | 0.149 | 0.100 | 0.128 | 0.087 |
| Rabi Maize | 0.208 | 0.181 | 0.111 | 0.128 | 0.106 |
| Rabi Jowar | 0.297 | 0.289 | 0.284 | 0.273 | 0.286 |
| Rabi Groundnut | 0.202 | 0.209 | 0.178 | 0.192 | 0.170 |
| Rabi Gram | 0.275 | 0.267 | 0.220 | 0.245 | 0.527 |

### 5.5 Rolling origin (secondary) — skill vs B1 and RMSE

| Crop-season | Unit | B1 RMSE | B2 skill | B3 skill | B4 skill | Lowest-RMSE baseline |
|---|---|---:|---:|---:|---:|---|
| Kharif Rice | t/ha | 0.520 | +0.644 | +0.316 | +0.460 | B2 |
| Kharif Maize | t/ha | 1.039 | +0.042 | −0.859 | +0.038 | B2 |
| Kharif Cotton(lint) | bales/ha | 0.622 | −0.182 | −0.801 | −0.127 | B1 |
| Kharif Arhar/Tur | t/ha | 0.200 | −0.143 | −0.041 | −0.345 | B0 |
| Kharif Jowar | t/ha | 0.382 | −0.146 | −0.752 | −0.189 | B0 |
| Kharif Moong | t/ha | 0.205 | −0.067 | −0.466 | +0.094 | B4 |
| Kharif Dry chillies | t/ha | 0.627 | +0.127 | −0.323 | −0.128 | B2 |
| Rabi Rice | t/ha | 0.524 | +0.604 | +0.183 | +0.574 | B2 |
| Rabi Maize | t/ha | 1.020 | +0.523 | +0.314 | +0.523 | B2 |
| Rabi Jowar | t/ha | 0.306 | −0.274 | −0.684 | −0.016 | B1 |
| Rabi Groundnut | t/ha | 0.394 | +0.219 | +0.175 | +0.195 | B2 |
| Rabi Gram | t/ha | 0.408 | +0.020 | −0.761 | −0.804 | B2 |

### 5.6 Year-by-year behaviour (fixed origin)

Number of crop-seasons (of 12) in which each baseline beats B1, by test year:

| Baseline | 2010 | 2011 | 2013 | 2014 |
|---|---:|---:|---:|---:|
| B0 | 4 | 3 | 3 | 2 |
| B2 | 9 | **2** | 9 | 9 |
| B3 | 9 | **3** | 4 | 3 |
| B4 | 7 | **2** | 7 | 5 |

B1's bias relative to the mean observed yield was negative (under-prediction) in **41 of 48** crop-season × year cells. Five of the seven exceptions fall in 2011 (Kharif Maize, Cotton(lint), Arhar/Tur, Dry chillies; Rabi Gram); the other two are Kharif Maize and Kharif Jowar in 2014.

### 5.7 Outlier flags (training statistics only; flag only)

Two training rows exceed |robust z| > 5: Kharif Arhar/Tur, Nizamabad 2008 (1.368 t/ha, z = 5.74) and Rabi Jowar, Rangareddi 2008 (2.156 t/ha, z = 5.95). No test row was flagged. Both rows were retained.

## 6. Discussion

1. **Recent history beats long history in most crop-seasons.** B2 outperformed the district long-run mean in 9 of 12 crop-seasons (fixed origin) — strongest for Rice (both seasons, skill +0.55 to +0.63) and Rabi Maize (+0.57). This is consistent with the systematic under-prediction by B1: yields in 2010–2014 were generally higher than the 1997–2009 average, so averages dominated by older years are biased low. The B2 advantage is smaller and less consistent under rolling origin (7 of 12, median +0.03), because B1 there also absorbs recent years.
2. **The gain is not stable across years.** In 2011, B2, B3 and B4 all lost to B1 in most crop-seasons; several Kharif crops had yields at or below their historical means that year. Year-to-year shocks common to all districts dominate the error, so 36 district observations represent only ~4 effectively independent years.
3. **Last observed value (B3) is fragile.** Under fixed origin B3 uses 2009 for nearly every district. Training data show 2009 was atypical for several crops: Kharif Moong at a median 0.25× and Kharif Maize at 0.68× of their 1997–2008 district means (Rabi Gram at 1.45×). This produced B3 skill of −3.0 (Kharif Moong) and −1.3 (Kharif Maize).
4. **Trend extrapolation (B4) helps when growth is steady, hurts otherwise.** B4 was best or near-best for Rice and Rabi Maize, but over-predicted Rabi Gram (bias +0.66 t/ha, skill −2.17) and Kharif Arhar/Tur (skill −0.87), whose training slopes (≈0.10 and ≈0.03 t/ha/yr on means of ~1.1 and ~0.45 t/ha) did not continue. No B4 prediction was negative, so negative-yield risk did not materialise in this data, but the mechanism remains (Section 4.3).
5. **Typical error is large in agronomic terms.** Even the lowest-RMSE baseline for each crop-season (fixed origin) has a WAPE between 0.087 (Rabi Rice, B4) and 0.341 (Kharif Moong, B1), median ≈0.23, at district level (e.g. Kharif Maize B2 RMSE 0.97 t/ha). These baselines are reference points, not decision-grade forecasts.

## 7. Reproducibility and testing [Verified]

- Definitions frozen before the official runs: SHA-256 of config, `src/tg_baselines.py`, `src/compare_runs.py`, `tests/test_tg_baselines.py` recorded in a private frozen-definitions file and re-verified after the runs. The freeze followed two development runs (`attempt_1`, `attempt_2`), the first of whose summary scores were viewed; their substantive outputs are byte-identical to `run_a` (Section 9.3).
- Two complete runs (`run_a`, `run_b`) with identical code, data, configuration and environment: **10 of 10 substantive output files byte-identical** (SHA-256); only `run_timing.json` (timestamps, elapsed time, output path) excluded, identically for both. The public code's equivalent check is in `results/tg_baselines_v1/reproducibility/`.
- Automated tests: **37 tests, 37 passed** against `run_a` and again against `run_b` (private test logs). Coverage: schema, hash, duplicates, Telangana filtering, exact-label matching, exclusion counts and order, eligible counts, 2012 absence, coverage rules (pass and fail cases), forecast cutoffs, baseline values and fallback order, within-district trend, training-only behaviour (target-value perturbation), rolling-origin isolation, gap assertion, negative-prediction retention, metric formulas including zero denominators, metric recomputation from predictions, prediction traceability to source CSV lines, independent recomputation of all predictions, manifest hashes, no pooled cross-unit metrics, and source dataset / original repository / dependency files unchanged.
- Environment: CPython 3.11.0 virtual environment with numpy 2.2.6, pandas 2.3.3 (plus python-dateutil 2.9.0.post0, pytz 2026.5, six 1.17.0, tzdata 2026.5) from a hash-locked `requirements.lock.txt`. No packages were added. All commands ran offline with `-I -B`.

## 8. Methodological assumptions

1. Production units are inferred (tonnes; bales for cotton); no conversion applied.
2. `Crop_Year` is used as an ordinal label. Whether it denotes a calendar year or an agricultural year (e.g. 2009-10) is not stated; this does not affect these baselines but matters for any future weather alignment.
3. Pre-2014 Telangana records are those of the 10 erstwhile districts of undivided Andhra Pradesh, relabelled in the source; district boundaries are treated as stable within 1997–2014.
4. The 10 ha minimum area is a methodological choice to remove tiny, noisy plots; it is not a proven universal rule and it removed 2 test rows (both Kharif Jowar 2014).
5. Coverage thresholds (10 / 7 / 30) were set after viewing row counts (including test-year coverage) and before any baseline scores existed, but after descriptive statistics that included test-period yields had been viewed (Section 9.2).
6. B2/B3 window anchoring and B3's three-year lookback follow the previously approved design (Section 4.3).
7. Unweighted means across districts (not area-weighted).

## 9. Development exposure to test-period data (research-integrity review)

Reviewed after completion, without re-running or modifying the experiment, from: the execution log; the file inventory with SHA-256 hashes and modification times; the frozen-definition record; and the session record of the earlier repository audit and planning phases. All four are private development records and are not included in this repository.

### 9.1 Computational leakage versus test-set exposure

- **Computational leakage** means test-year information entering a prediction. None was detected: the run-time assertions and tests in Section 4.4 show that every prediction uses only rows up to its training cutoff and is unchanged when test-year yields are replaced.
- **Test-set exposure** means the people developing the method (here, the AI assistant that implemented it and the project owner reviewing its outputs) seeing test-period data or scores before the method was final. This **did occur** (Section 9.2).
- Therefore 2010, 2011, 2013 and 2014 are **temporally held out from the computations, but they are not an unseen or independently sealed hold-out set**, and the results should not be described as such.

### 9.2 What was observed before the code was locked

The code was locked by the hash freeze at 20:18:02 (execution log item 11).

| Stage | Information involving 2010–2014 that was viewed | Record |
|---|---|---|
| Repository audit and planning (before the experiment workspace existed) | Descriptive statistics pooled over all years including test years: Telangana median production/area per crop (e.g. Rice ≈2.75, Cotton(lint) ≈1.72); India-wide median and 99th-percentile yields per crop; Telangana Kharif Rice area by year; per-district, per-year presence and exclusion status for each crop-season | Session record only |
| Experiment planning (Phase 3) | Per-crop-season minimum, mean and maximum eligible yield computed over training **and** test years combined; test-year district counts; the fact that both area-cutoff exclusions are 2014 test rows | Session record only |
| Development run `attempt_1` (20:14:56; log items 6–7) | The complete `baseline_summary.csv` for both designs (median WAPE, median skill vs B1, beats-B1 counts, fallback and negative counts — identical to Section 5.1); two prediction rows (Adilabad Kharif Arhar/Tur 2010: observed yield and B0/B1 predictions); exclusions; outlier flags | Execution log and session record |
| Development run `attempt_2` (20:17:26; log item 9) | Test pass/fail results only | Execution log |

Per-crop-season and per-year metric tables were first displayed after the lock (log item 18).

### 9.3 Did development results influence decisions?

- **Implemented results: no evidence of influence.** The configuration, which holds every baseline definition, window, threshold and exclusion, was last modified at 20:12:16, before any score existed (20:14:56). The only changes after the first scores were seen were: the test suite; reordering the label check in `classify_rows` (an error-handling path only); and the new `src/compare_runs.py`. All nine substantive output files of `attempt_1`, `attempt_2` and `run_a` are **byte-identical** (SHA-256 in the inventory). So no change made after score exposure altered any prediction, metric or exclusion. Only `run_manifest.json` (which records source-code hashes) and `run_timing.json` differ.
- **Interpretation: shaped after seeing results.** The analysis tables (`scripts/summarize_results.py`), the 2009-anomaly check and the explanations in Section 6 were produced after the results were seen. They are post-hoc explanations, not pre-specified hypotheses.
- **Design choices made after the descriptive exposure: influence unknown.** These choices were all made after descriptive statistics including test-year yields had been viewed (Section 9.2):
  - the crop-season list;
  - the Turmeric and Soyabean exclusion;
  - the 10 ha cutoff;
  - the coverage thresholds (10 / 7 / 30);
  - the B2/B3 window and lookback definitions.

  Some of them also used test-period *availability*: row counts, season-label changes, and which districts appear in test years. Their documented rationales are coverage and data quality, not accuracy, and no baseline scores existed when they were made. **Whether the descriptive test-year information influenced them cannot be established from the available records and remains unknown.** It is also unknown what, if anything, the project owner examined beyond the session outputs.

### 9.4 Consequences

- Describe these results as a transparent benchmark with no computational leakage, scored on temporally held-out years. Do not describe them as a sealed out-of-sample estimate.
- Any future model compared on these same years inherits the same exposure. A genuinely unseen evaluation needs data that has not yet been examined (for example, 2015 onward from a new source), with the protocol frozen before that data is opened.

## 10. Limitations

1. **Development exposure:** test-period data and one development run's aggregate scores were viewed before the code was locked (Section 9). Computational leakage is ruled out by tests, but the test years are not unseen. Whether the earlier descriptive exposure shaped design choices is unknown.
2. **Inferred production units:** the source has no unit column. Tonnes are assumed; cotton is assumed to be in bales and is not converted. Whether rice is paddy or milled, and whether groundnut is pods or kernels, is not stated.
3. **Unconfirmed `Crop_Year` convention:** whether it is a calendar or an agricultural year is unknown. This does not matter for these baselines, but it must be settled before adding season-aligned weather features.
4. **Dataset ends in 2014:** 2012 is missing. Only the 10 pre-2016 districts are covered (Hyderabad excluded), so the 33 present-day districts are not represented.
5. **Unresolved licence of the original repository:** it has no LICENSE file, although its README claims MIT. The experiment code here was written independently and does not reuse that repository's code. However, the dataset file was taken from it, and the dataset's own licence is also unverified. Do not redistribute derived data or publish the project until both are clarified.
6. **Small, correlated test sample:** 4 test years × at most 9 districts per crop-season, with errors strongly correlated within a year. Skill differences below roughly ±0.1 should not be treated as meaningful, and no confidence intervals were computed.
7. **District-level aggregates only:** the results say nothing about farm-level yields.
8. **No explanatory features:** weather, irrigation, inputs, prices and shifts in sown area are excluded by design, so the baselines cannot anticipate shocks such as the 2011 shortfall.
9. **Limited scope:** only 12 crop-seasons. Turmeric, Soyabean, Castor and other crops are excluded, as are Whole Year records.
10. **Single data source:** values were not cross-checked against official Telangana or Directorate of Economics and Statistics publications.

## 11. Recommended next steps

1. Treat **B1 and B2** as the reference baselines any future model must beat, per crop-season, under the same fixed- and rolling-origin protocol and the same tests.
2. Add uncertainty estimates (e.g. year-block bootstrap) before comparing models whose skill differences are small.
3. Obtain newer and official district data (2015 onward, 33 districts) with explicit units; document district re-mapping.
4. Resolve the `Crop_Year` convention before introducing season-aligned weather features.
5. Only then evaluate learned models (e.g. regularised regression or gradient boosting with lagged yields and season-window weather), reporting skill relative to B1/B2 per crop-season — never pooled R² across crops.
6. Resolve the original repository's licence before reusing any of its code in a public project.

## 12. File index

| Deliverable | Path in this repository |
|---|---|
| Configuration | `configs/tg_baselines_v1.json` |
| Experiment code | `src/tg_baselines.py`; comparison `src/compare_runs.py`; report tables `scripts/summarize_results.py` |
| Tests | `tests/test_tg_baselines.py` |
| Prediction-level CSV | Not published (record-level). Regenerate locally; its SHA-256 is recorded in `results/tg_baselines_v1/run_manifest.json` |
| Metrics per crop-season / per year | `results/tg_baselines_v1/metrics_by_crop_season.csv`, `metrics_by_crop_season_year.csv` |
| Baseline comparison summary | `results/tg_baselines_v1/baseline_summary.csv`; `results/tg_baselines_v1/analysis/` |
| Data-quality report | `results/tg_baselines_v1/data_quality_report.md`, `coverage.csv`, `data_audit.json` (exclusion list is record-level; not published) |
| Reproducibility report | `results/tg_baselines_v1/reproducibility/` |
| Run manifest | `results/tg_baselines_v1/run_manifest.json` |
| Executive summary | `reports/executive_summary.md` |
| Reproduction commands | `docs/reproducibility.md` |
