# Executive Summary — Telangana Crop Intelligence: Historical Baselines

**What we asked:** How well can simple, transparent rules based only on past records forecast district-level crop yield in Telangana?

**Data:** District-level Indian crop production records (246,091 rows; SHA-256 verified). Telangana: 9 districts (Hyderabad excluded), 1997–2014 with 2012 missing; 12 crop–season combinations (Kharif Rice, Maize, Cotton, Arhar/Tur, Jowar, Moong, Dry chillies; Rabi Rice, Maize, Jowar, Groundnut, Gram). 1,802 eligible observations after documented exclusions (12 rows: 8 Hyderabad, 2 missing production, 2 under 10 ha). Yield = production ÷ area in each crop's recorded units (t/ha; cotton in bales/ha, unconverted).

**Method:** Five baselines — B0 crop-season mean, B1 district mean, B2 district mean of the last five years, B3 last observed value, B4 district mean plus a within-district trend. Forecasts for 2010, 2011, 2013 and 2014 using only data up to 2009 (primary, fixed origin) and, separately, only data before each target year (secondary, rolling origin). No random splits, no external features, no machine learning. Errors reported per crop-season in native units; cross-crop comparisons only with unit-free WAPE and skill relative to B1.

**Key results (fixed origin, 12 crop-seasons):**

| Baseline | Median WAPE | Median skill vs B1 | Beats B1 in |
|---|---:|---:|---:|
| B0 crop-season mean | 27.9% | −0.21 | 2 / 12 |
| **B1 district mean (reference)** | **25.8%** | 0 | — |
| **B2 recent 5-year mean** | **22.6%** | **+0.15** | **9 / 12** |
| B3 last observed | 28.3% | −0.10 | 4 / 12 |
| B4 mean + trend | 27.4% | −0.21 | 5 / 12 |

- **B2 is the strongest simple baseline**, especially for Rice (skill +0.55 to +0.63) and Rabi Maize (+0.57). Under rolling origin its advantage shrinks (7 / 12, median +0.03).
- **Long-run averages under-predict:** B1 was too low in 41 of 48 crop-season-year cells, meaning 2010–2014 yields were generally above 1997–2009 levels.
- **B3 is fragile** because 2009 was unusual (e.g. Kharif Moong at about a quarter of its normal yield). **B4 can overshoot** when past trends stop (Rabi Gram skill −2.17).
- **2011 was hard for every method**; with only four test years, results carry substantial uncertainty.
- Typical district-level errors remain large (WAPE ≈ 9%–34% for the best baseline per crop-season). These are benchmarks, **not production-ready forecasts**.

**Reliability:** Baseline definitions were fixed in the configuration before any scores existed, and the code was hash-frozen before the official runs. 37/37 automated tests passed (including leakage, traceability and independent recomputation of all 4,290 predictions). Two full runs produced byte-identical outputs. The source dataset and original repository were verified unchanged.

**Test-set exposure (research-integrity note):** The test years were excluded from every computation; tests confirm there is no computational leakage. They were **not unseen**, however. Descriptive statistics that included test-period yields, and one development run's summary scores, were viewed before the code was locked.
- That development run's outputs are byte-identical to the official run, so no result changed after its scores were seen.
- Whether the earlier descriptive exposure influenced design choices (crop selection, the 10 ha cutoff, coverage thresholds, baseline windows) **cannot be determined from the records**.
- See Section 9 of the research report.

**Main limitations:**
- Development exposure, as above.
- Inferred production units: no unit column; cotton assumed to be bales and not converted.
- Unconfirmed `Crop_Year` convention (calendar or agricultural year).
- Data ends in 2014, with 2012 missing, and covers only the 10 old districts.
- The original repository's licence is unresolved (no LICENSE file), and the dataset's licence is unverified.
- Small, correlated test sample (4 years × at most 9 districts).
- No weather or input data.
- District aggregates, not farm yields.

**Next step:** use B1 and B2 as the benchmarks that any future machine-learning model must beat — per crop-season, under the same time-based protocol and tests — after obtaining newer official district data and resolving the original repository's licence.
