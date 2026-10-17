# Analysis tables - tg_baselines_v1

Derived from a complete run's `metrics_by_crop_season.csv`, `metrics_by_crop_season_year.csv` and `baseline_summary.csv` by `scripts/summarize_results.py`. Native-unit metrics are per crop-season only.

## fixed_origin: skill_vs_b1

| crop_season_id | B0 | B1 | B2 | B3 | B4 |
|---|---|---|---|---|---|
| kharif_rice | -0.235 | 0.000 | 0.629 | 0.221 | 0.485 |
| kharif_maize | -0.523 | 0.000 | 0.173 | -1.255 | 0.104 |
| kharif_cotton_lint | -0.178 | 0.000 | 0.105 | -0.292 | -0.332 |
| kharif_arhar_tur | 0.040 | 0.000 | 0.052 | -0.089 | -0.868 |
| kharif_jowar | 0.053 | 0.000 | -0.220 | -0.727 | -0.405 |
| kharif_moong | -0.123 | 0.000 | -0.086 | -3.006 | -0.234 |
| kharif_dry_chillies | -1.548 | 0.000 | 0.249 | -0.931 | -0.533 |
| rabi_rice | -0.258 | 0.000 | 0.553 | 0.207 | 0.637 |
| rabi_maize | -0.309 | 0.000 | 0.568 | 0.443 | 0.567 |
| rabi_jowar | -0.333 | 0.000 | -0.307 | -0.107 | -0.186 |
| rabi_groundnut | -0.058 | 0.000 | 0.197 | -0.084 | 0.138 |
| rabi_gram | -0.085 | 0.000 | 0.126 | 0.068 | -2.167 |

## fixed_origin: wape

| crop_season_id | B0 | B1 | B2 | B3 | B4 |
|---|---|---|---|---|---|
| kharif_rice | 0.168 | 0.150 | 0.093 | 0.140 | 0.113 |
| kharif_maize | 0.340 | 0.278 | 0.255 | 0.397 | 0.265 |
| kharif_cotton_lint | 0.267 | 0.249 | 0.232 | 0.293 | 0.278 |
| kharif_arhar_tur | 0.303 | 0.332 | 0.308 | 0.315 | 0.482 |
| kharif_jowar | 0.283 | 0.309 | 0.308 | 0.428 | 0.371 |
| kharif_moong | 0.351 | 0.341 | 0.339 | 0.717 | 0.389 |
| kharif_dry_chillies | 0.365 | 0.200 | 0.174 | 0.297 | 0.270 |
| rabi_rice | 0.164 | 0.149 | 0.100 | 0.128 | 0.087 |
| rabi_maize | 0.208 | 0.181 | 0.111 | 0.128 | 0.106 |
| rabi_jowar | 0.297 | 0.289 | 0.284 | 0.273 | 0.286 |
| rabi_groundnut | 0.202 | 0.209 | 0.178 | 0.192 | 0.170 |
| rabi_gram | 0.275 | 0.267 | 0.220 | 0.245 | 0.527 |

## fixed_origin: rmse

| crop_season_id | unit | B0 | B1 | B2 | B3 | B4 |
|---|---|---|---|---|---|---|
| kharif_rice | t/ha | 0.627 | 0.564 | 0.343 | 0.498 | 0.404 |
| kharif_maize | t/ha | 1.318 | 1.068 | 0.971 | 1.604 | 1.011 |
| kharif_cotton_lint | bales/ha | 0.678 | 0.625 | 0.591 | 0.710 | 0.721 |
| kharif_arhar_tur | t/ha | 0.199 | 0.204 | 0.198 | 0.212 | 0.278 |
| kharif_jowar | t/ha | 0.376 | 0.387 | 0.427 | 0.508 | 0.458 |
| kharif_moong | t/ha | 0.227 | 0.214 | 0.223 | 0.429 | 0.238 |
| kharif_dry_chillies | t/ha | 1.036 | 0.649 | 0.562 | 0.902 | 0.804 |
| rabi_rice | t/ha | 0.632 | 0.564 | 0.377 | 0.502 | 0.340 |
| rabi_maize | t/ha | 1.245 | 1.088 | 0.716 | 0.812 | 0.716 |
| rabi_jowar | t/ha | 0.356 | 0.308 | 0.352 | 0.324 | 0.336 |
| rabi_groundnut | t/ha | 0.428 | 0.416 | 0.373 | 0.434 | 0.387 |
| rabi_gram | t/ha | 0.430 | 0.412 | 0.386 | 0.398 | 0.734 |

## fixed_origin: bias

| crop_season_id | unit | B0 | B1 | B2 | B3 | B4 |
|---|---|---|---|---|---|---|
| kharif_rice | t/ha | -0.411 | -0.411 | -0.133 | -0.324 | 0.091 |
| kharif_maize | t/ha | -0.355 | -0.355 | -0.110 | -1.077 | -0.069 |
| kharif_cotton_lint | bales/ha | -0.291 | -0.291 | 0.089 | -0.144 | 0.480 |
| kharif_arhar_tur | t/ha | -0.060 | -0.060 | 0.057 | -0.008 | 0.199 |
| kharif_jowar | t/ha | -0.071 | -0.069 | 0.054 | -0.081 | 0.235 |
| kharif_moong | t/ha | -0.158 | -0.157 | -0.160 | -0.367 | -0.188 |
| kharif_dry_chillies | t/ha | -0.355 | -0.352 | 0.100 | 0.150 | 0.597 |
| rabi_rice | t/ha | -0.449 | -0.449 | -0.205 | -0.253 | 0.010 |
| rabi_maize | t/ha | -0.824 | -0.824 | -0.329 | -0.523 | 0.072 |
| rabi_jowar | t/ha | -0.114 | -0.112 | -0.005 | -0.015 | 0.183 |
| rabi_groundnut | t/ha | -0.227 | -0.227 | -0.033 | -0.047 | 0.174 |
| rabi_gram | t/ha | -0.231 | -0.228 | 0.136 | 0.123 | 0.657 |

## fixed_origin: lowest-RMSE baseline per crop-season

| crop_season_id | unit | baseline | rmse | skill_vs_b1 |
|---|---|---|---|---|
| kharif_rice | t/ha | B2 | 0.343 | 0.629 |
| kharif_maize | t/ha | B2 | 0.971 | 0.173 |
| kharif_cotton_lint | bales/ha | B2 | 0.591 | 0.105 |
| kharif_arhar_tur | t/ha | B2 | 0.198 | 0.052 |
| kharif_jowar | t/ha | B0 | 0.376 | 0.053 |
| kharif_moong | t/ha | B1 | 0.214 | 0.000 |
| kharif_dry_chillies | t/ha | B2 | 0.562 | 0.249 |
| rabi_rice | t/ha | B4 | 0.340 | 0.637 |
| rabi_maize | t/ha | B2 | 0.716 | 0.568 |
| rabi_jowar | t/ha | B1 | 0.308 | 0.000 |
| rabi_groundnut | t/ha | B2 | 0.373 | 0.197 |
| rabi_gram | t/ha | B2 | 0.386 | 0.126 |

## fixed_origin: per-test-year comparison with B1 (counts across 12 crop-seasons)

| baseline | target_year | n_crop_seasons | n_beats_b1 | median_skill_vs_b1 | median_wape |
|---|---|---|---|---|---|
| B0 | 2010 | 12 | 4 | -0.151 | 0.233 |
| B0 | 2011 | 12 | 3 | -0.154 | 0.282 |
| B0 | 2013 | 12 | 3 | -0.137 | 0.233 |
| B0 | 2014 | 12 | 2 | -0.340 | 0.265 |
| B2 | 2010 | 12 | 9 | 0.290 | 0.188 |
| B2 | 2011 | 12 | 2 | -0.106 | 0.297 |
| B2 | 2013 | 12 | 9 | 0.437 | 0.141 |
| B2 | 2014 | 12 | 9 | 0.269 | 0.193 |
| B3 | 2010 | 12 | 9 | 0.260 | 0.188 |
| B3 | 2011 | 12 | 3 | -0.793 | 0.389 |
| B3 | 2013 | 12 | 4 | -0.262 | 0.242 |
| B3 | 2014 | 12 | 3 | -0.336 | 0.254 |
| B4 | 2010 | 12 | 7 | 0.204 | 0.213 |
| B4 | 2011 | 12 | 2 | -0.300 | 0.328 |
| B4 | 2013 | 12 | 7 | 0.147 | 0.199 |
| B4 | 2014 | 12 | 5 | -0.260 | 0.280 |

## fixed_origin: B1 bias relative to mean observed yield, by test year (negative = under-prediction)

| crop_season_id | 2010 | 2011 | 2013 | 2014 |
|---|---|---|---|---|
| kharif_rice | -0.166 | -0.078 | -0.171 | -0.128 |
| kharif_maize | -0.145 | 0.023 | -0.257 | 0.018 |
| kharif_cotton_lint | -0.211 | 0.253 | -0.293 | -0.160 |
| kharif_arhar_tur | -0.102 | 0.023 | -0.241 | -0.119 |
| kharif_jowar | -0.104 | -0.184 | -0.012 | 0.067 |
| kharif_moong | -0.216 | -0.276 | -0.436 | -0.213 |
| kharif_dry_chillies | -0.171 | 0.042 | -0.213 | -0.182 |
| rabi_rice | -0.179 | -0.054 | -0.142 | -0.176 |
| rabi_maize | -0.158 | -0.130 | -0.205 | -0.158 |
| rabi_jowar | -0.084 | -0.061 | -0.143 | -0.204 |
| rabi_groundnut | -0.141 | -0.067 | -0.108 | -0.207 |
| rabi_gram | -0.163 | 0.061 | -0.332 | -0.207 |

## rolling_origin: skill_vs_b1

| crop_season_id | B0 | B1 | B2 | B3 | B4 |
|---|---|---|---|---|---|
| kharif_rice | -0.344 | 0.000 | 0.644 | 0.316 | 0.460 |
| kharif_maize | -0.599 | 0.000 | 0.042 | -0.859 | 0.038 |
| kharif_cotton_lint | -0.175 | 0.000 | -0.182 | -0.801 | -0.127 |
| kharif_arhar_tur | 0.013 | 0.000 | -0.143 | -0.041 | -0.345 |
| kharif_jowar | 0.029 | 0.000 | -0.146 | -0.752 | -0.189 |
| kharif_moong | -0.127 | 0.000 | -0.067 | -0.466 | 0.094 |
| kharif_dry_chillies | -1.680 | 0.000 | 0.127 | -0.323 | -0.128 |
| rabi_rice | -0.331 | 0.000 | 0.604 | 0.183 | 0.574 |
| rabi_maize | -0.372 | 0.000 | 0.523 | 0.314 | 0.523 |
| rabi_jowar | -0.326 | 0.000 | -0.274 | -0.684 | -0.016 |
| rabi_groundnut | -0.124 | 0.000 | 0.219 | 0.175 | 0.195 |
| rabi_gram | -0.066 | 0.000 | 0.020 | -0.761 | -0.804 |

## rolling_origin: wape

| crop_season_id | B0 | B1 | B2 | B3 | B4 |
|---|---|---|---|---|---|
| kharif_rice | 0.163 | 0.138 | 0.087 | 0.119 | 0.104 |
| kharif_maize | 0.340 | 0.274 | 0.261 | 0.339 | 0.265 |
| kharif_cotton_lint | 0.268 | 0.249 | 0.270 | 0.334 | 0.248 |
| kharif_arhar_tur | 0.300 | 0.325 | 0.339 | 0.333 | 0.384 |
| kharif_jowar | 0.281 | 0.301 | 0.318 | 0.421 | 0.337 |
| kharif_moong | 0.338 | 0.324 | 0.315 | 0.364 | 0.306 |
| kharif_dry_chillies | 0.361 | 0.196 | 0.180 | 0.225 | 0.212 |
| rabi_rice | 0.157 | 0.138 | 0.086 | 0.119 | 0.086 |
| rabi_maize | 0.199 | 0.168 | 0.109 | 0.141 | 0.105 |
| rabi_jowar | 0.295 | 0.277 | 0.283 | 0.307 | 0.253 |
| rabi_groundnut | 0.196 | 0.194 | 0.144 | 0.165 | 0.155 |
| rabi_gram | 0.267 | 0.261 | 0.242 | 0.319 | 0.362 |

## rolling_origin: rmse

| crop_season_id | unit | B0 | B1 | B2 | B3 | B4 |
|---|---|---|---|---|---|---|
| kharif_rice | t/ha | 0.603 | 0.520 | 0.310 | 0.430 | 0.382 |
| kharif_maize | t/ha | 1.314 | 1.039 | 1.018 | 1.417 | 1.019 |
| kharif_cotton_lint | bales/ha | 0.675 | 0.622 | 0.676 | 0.835 | 0.661 |
| kharif_arhar_tur | t/ha | 0.198 | 0.200 | 0.213 | 0.204 | 0.231 |
| kharif_jowar | t/ha | 0.376 | 0.382 | 0.409 | 0.505 | 0.416 |
| kharif_moong | t/ha | 0.218 | 0.205 | 0.212 | 0.248 | 0.195 |
| kharif_dry_chillies | t/ha | 1.027 | 0.627 | 0.586 | 0.721 | 0.666 |
| rabi_rice | t/ha | 0.604 | 0.524 | 0.330 | 0.473 | 0.342 |
| rabi_maize | t/ha | 1.195 | 1.020 | 0.705 | 0.845 | 0.705 |
| rabi_jowar | t/ha | 0.353 | 0.306 | 0.346 | 0.398 | 0.309 |
| rabi_groundnut | t/ha | 0.418 | 0.394 | 0.349 | 0.358 | 0.354 |
| rabi_gram | t/ha | 0.421 | 0.408 | 0.404 | 0.541 | 0.548 |

## rolling_origin: bias

| crop_season_id | unit | B0 | B1 | B2 | B3 | B4 |
|---|---|---|---|---|---|---|
| kharif_rice | t/ha | -0.370 | -0.370 | -0.100 | -0.073 | 0.083 |
| kharif_maize | t/ha | -0.316 | -0.316 | -0.180 | -0.168 | -0.007 |
| kharif_cotton_lint | bales/ha | -0.268 | -0.268 | 0.032 | -0.046 | 0.309 |
| kharif_arhar_tur | t/ha | -0.055 | -0.055 | 0.027 | -0.002 | 0.128 |
| kharif_jowar | t/ha | -0.059 | -0.059 | 0.037 | -0.007 | 0.176 |
| kharif_moong | t/ha | -0.143 | -0.143 | -0.128 | -0.077 | -0.118 |
| kharif_dry_chillies | t/ha | -0.324 | -0.321 | 0.069 | 0.007 | 0.382 |
| rabi_rice | t/ha | -0.407 | -0.407 | -0.136 | -0.097 | 0.019 |
| rabi_maize | t/ha | -0.747 | -0.747 | -0.198 | -0.121 | 0.075 |
| rabi_jowar | t/ha | -0.106 | -0.105 | -0.007 | -0.025 | 0.109 |
| rabi_groundnut | t/ha | -0.209 | -0.209 | -0.028 | -0.051 | 0.109 |
| rabi_gram | t/ha | -0.214 | -0.212 | 0.064 | 0.021 | 0.415 |

## rolling_origin: lowest-RMSE baseline per crop-season

| crop_season_id | unit | baseline | rmse | skill_vs_b1 |
|---|---|---|---|---|
| kharif_rice | t/ha | B2 | 0.310 | 0.644 |
| kharif_maize | t/ha | B2 | 1.018 | 0.042 |
| kharif_cotton_lint | bales/ha | B1 | 0.622 | 0.000 |
| kharif_arhar_tur | t/ha | B0 | 0.198 | 0.013 |
| kharif_jowar | t/ha | B0 | 0.376 | 0.029 |
| kharif_moong | t/ha | B4 | 0.195 | 0.094 |
| kharif_dry_chillies | t/ha | B2 | 0.586 | 0.127 |
| rabi_rice | t/ha | B2 | 0.330 | 0.604 |
| rabi_maize | t/ha | B2 | 0.705 | 0.523 |
| rabi_jowar | t/ha | B1 | 0.306 | 0.000 |
| rabi_groundnut | t/ha | B2 | 0.349 | 0.219 |
| rabi_gram | t/ha | B2 | 0.404 | 0.020 |

## rolling_origin: per-test-year comparison with B1 (counts across 12 crop-seasons)

| baseline | target_year | n_crop_seasons | n_beats_b1 | median_skill_vs_b1 | median_wape |
|---|---|---|---|---|---|
| B0 | 2010 | 12 | 4 | -0.151 | 0.233 |
| B0 | 2011 | 12 | 3 | -0.242 | 0.277 |
| B0 | 2013 | 12 | 2 | -0.194 | 0.229 |
| B0 | 2014 | 12 | 2 | -0.508 | 0.255 |
| B2 | 2010 | 12 | 9 | 0.290 | 0.188 |
| B2 | 2011 | 12 | 3 | -0.289 | 0.295 |
| B2 | 2013 | 12 | 7 | 0.274 | 0.178 |
| B2 | 2014 | 12 | 7 | 0.105 | 0.182 |
| B3 | 2010 | 12 | 9 | 0.260 | 0.188 |
| B3 | 2011 | 12 | 3 | -0.734 | 0.335 |
| B3 | 2013 | 12 | 5 | -0.312 | 0.292 |
| B3 | 2014 | 12 | 7 | 0.243 | 0.162 |
| B4 | 2010 | 12 | 7 | 0.204 | 0.213 |
| B4 | 2011 | 12 | 3 | -0.254 | 0.318 |
| B4 | 2013 | 12 | 10 | 0.573 | 0.128 |
| B4 | 2014 | 12 | 7 | 0.212 | 0.186 |

## rolling_origin: B1 bias relative to mean observed yield, by test year (negative = under-prediction)

| crop_season_id | 2010 | 2011 | 2013 | 2014 |
|---|---|---|---|---|
| kharif_rice | -0.166 | -0.065 | -0.156 | -0.101 |
| kharif_maize | -0.145 | 0.035 | -0.250 | 0.049 |
| kharif_cotton_lint | -0.211 | 0.277 | -0.290 | -0.135 |
| kharif_arhar_tur | -0.102 | 0.032 | -0.236 | -0.095 |
| kharif_jowar | -0.104 | -0.178 | 0.010 | 0.081 |
| kharif_moong | -0.216 | -0.262 | -0.411 | -0.142 |
| kharif_dry_chillies | -0.171 | 0.059 | -0.204 | -0.158 |
| rabi_rice | -0.179 | -0.039 | -0.126 | -0.153 |
| rabi_maize | -0.158 | -0.119 | -0.187 | -0.126 |
| rabi_jowar | -0.084 | -0.054 | -0.134 | -0.187 |
| rabi_groundnut | -0.141 | -0.056 | -0.094 | -0.189 |
| rabi_gram | -0.163 | 0.076 | -0.326 | -0.175 |

## 2009 yield relative to each district's 1997-2008 mean (training data only)

B3 (fixed origin) uses the 2009 value for most districts, so an unusual 2009 propagates to all test years.

| crop_season_id | n_districts_2009 | median_ratio_2009_to_1997_2008_district_mean |
|---|---|---|
| kharif_rice | 9 | 1.062 |
| kharif_maize | 9 | 0.678 |
| kharif_cotton_lint | 9 | 1.107 |
| kharif_arhar_tur | 9 | 0.969 |
| kharif_jowar | 8 | 0.911 |
| kharif_moong | 8 | 0.255 |
| kharif_dry_chillies | 9 | 1.360 |
| rabi_rice | 9 | 1.085 |
| rabi_maize | 9 | 1.081 |
| rabi_jowar | 9 | 1.127 |
| rabi_groundnut | 9 | 1.153 |
| rabi_gram | 9 | 1.445 |

## Baseline summary (unit-free)

| design | baseline | n_evaluations | median_wape | n_wape_undefined | median_skill_vs_b1 | n_beats_b1 | n_worse_than_b1 | n_equal_to_b1 | n_skill_undefined | n_fallback_predictions | n_negative_predictions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fixed_origin | B0 | 12 | 0.2792 | 0 | -0.2066 | 2 | 10 | 0 | 0 | 0 | 0 |
| fixed_origin | B1 | 12 | 0.2584 | 0 | 0.0000 | 0 | 0 | 12 | 0 | 0 | 0 |
| fixed_origin | B2 | 12 | 0.2263 | 0 | 0.1497 | 9 | 3 | 0 | 0 | 2 | 0 |
| fixed_origin | B3 | 12 | 0.2828 | 0 | -0.0980 | 4 | 8 | 0 | 0 | 2 | 0 |
| fixed_origin | B4 | 12 | 0.2736 | 0 | -0.2097 | 5 | 7 | 0 | 0 | 0 | 0 |
| rolling_origin | B0 | 12 | 0.2744 | 0 | -0.2503 | 2 | 10 | 0 | 0 | 0 | 0 |
| rolling_origin | B1 | 12 | 0.2554 | 0 | 0.0000 | 0 | 0 | 12 | 0 | 0 | 0 |
| rolling_origin | B2 | 12 | 0.2517 | 0 | 0.0309 | 7 | 5 | 0 | 0 | 2 | 0 |
| rolling_origin | B3 | 12 | 0.3130 | 0 | -0.3944 | 4 | 8 | 0 | 0 | 1 | 0 |
| rolling_origin | B4 | 12 | 0.2507 | 0 | 0.0109 | 6 | 6 | 0 | 0 | 0 | 0 |
