"""Telangana Crop Intelligence - transparent historical yield baselines (B0-B4).

Deterministic, offline, read-only with respect to the source dataset.

Entry point (run from the project root with the project's Python 3.11 environment):
    python -I -B src/tg_baselines.py --config configs/tg_baselines_v1.json --out runs/my_run
    python -I -B src/tg_baselines.py --config configs/tg_baselines_v1.json --data D:/data/file.csv --out runs/my_run

Relative paths in the config are resolved against the project root (the parent of configs/).
The dataset is always identified by its SHA-256, wherever it is stored.

Exit codes: 0 = success, 2 = integrity/coverage failure (no scores written), 1 = unexpected error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

LABEL_COLUMNS = ("State_Name", "District_Name", "Season", "Crop")
BASELINES = ("B0", "B1", "B2", "B3", "B4")
FLOAT_FORMAT = "%.6f"

PREDICTION_COLUMNS = [
    "design", "design_role", "crop_season_id", "season", "crop", "unit",
    "district", "target_year", "training_cutoff_year", "forecast_origin_year",
    "source_line", "observed_area", "observed_production", "observed_yield",
    "baseline", "prediction", "error", "abs_error", "rule", "is_fallback", "is_negative",
    "n_info_obs_crop_season", "n_info_obs_district", "info_min_year", "info_max_year",
    "b2_window_start", "b2_window_end", "b2_window_n_obs",
    "b3_source_year", "b3_source_line", "b4_beta", "b4_center_year",
]


class IntegrityError(RuntimeError):
    """Raised when data, labels, or temporal rules are violated."""


class CoverageError(RuntimeError):
    """Raised when a crop-season evaluation fails a coverage rule."""


# --------------------------------------------------------------------------- io
def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_config(path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    for key in ("experiment_id", "dataset", "scope", "row_exclusions", "coverage_rules",
                "designs", "baselines", "metrics", "output", "expected_absent_years"):
        if key not in cfg:
            raise IntegrityError(f"config missing key: {key}")
    ids = [c["id"] for c in cfg["scope"]["core_crop_seasons"]]
    if len(ids) != len(set(ids)):
        raise IntegrityError("duplicate crop_season ids in config")
    pairs = [(c["season"], c["crop"]) for c in cfg["scope"]["core_crop_seasons"]]
    if len(pairs) != len(set(pairs)):
        raise IntegrityError("duplicate (season, crop) pairs in config")
    for name, design in cfg["designs"].items():
        for fc in design["forecasts"]:
            if not fc["training_cutoff_year"] <= fc["forecast_origin_year"] < fc["target_year"]:
                raise IntegrityError(f"{name}: need cutoff <= origin < target, got {fc}")
    return cfg


def project_root(config_path) -> Path:
    """The project root is the parent of the directory holding the config (configs/)."""
    return Path(config_path).resolve().parent.parent


def resolve_data_path(cfg: dict, config_path, override=None) -> Path:
    """Dataset location: explicit override (relative to the working directory) or config path (relative to root)."""
    if override is not None:
        return Path(override).resolve()
    p = Path(cfg["dataset"]["path"])
    return p if p.is_absolute() else (project_root(config_path) / p).resolve()


def load_dataset(cfg: dict, data_path) -> tuple[pd.DataFrame, str]:
    ds = cfg["dataset"]
    if not Path(data_path).is_file():
        raise IntegrityError(f"dataset not found: {data_path} (see data/README.md for how to obtain it)")
    digest = sha256_file(data_path)
    if digest != ds["sha256"]:
        raise IntegrityError(f"dataset sha256 mismatch: {digest} != {ds['sha256']}")
    df = pd.read_csv(data_path, dtype={c: str for c in LABEL_COLUMNS})
    if list(df.columns) != ds["expected_columns"]:
        raise IntegrityError(f"unexpected columns: {list(df.columns)}")
    if len(df) != ds["expected_rows"]:
        raise IntegrityError(f"unexpected row count: {len(df)}")
    df.insert(0, "source_line", np.arange(2, len(df) + 2, dtype=np.int64))  # 1-based file line; header is line 1
    for col in LABEL_COLUMNS:
        df[col] = df[col].str.strip()
    return df, digest


def find_duplicate_keys(df: pd.DataFrame, key_columns) -> pd.DataFrame:
    dup = df[df.duplicated(list(key_columns), keep=False)]
    return dup.sort_values(list(key_columns) + ["source_line"])


# ------------------------------------------------------------- scope & quality
def classify_rows(df: pd.DataFrame, cfg: dict):
    """Return (eligible panel, core rows with exclusion reasons, scope counts)."""
    scope = cfg["scope"]
    excl = cfg["row_exclusions"]
    state_mask = df["State_Name"] == scope["state"]
    tg = df[state_mask].copy()
    whole = tg["Season"].isin(scope["excluded_seasons"])
    excluded_crop = ~whole & tg["Crop"].isin(scope["excluded_crops"])
    core_map = {(c["season"], c["crop"]): c for c in scope["core_crop_seasons"]}
    is_core = pd.Series([(s, c) in core_map for s, c in zip(tg["Season"], tg["Crop"])], index=tg.index)
    is_core &= ~whole & ~excluded_crop
    counts = {
        "dataset_rows": int(len(df)),
        "rows_other_states": int((~state_mask).sum()),
        "rows_target_state": int(len(tg)),
        "target_state_rows_excluded_season": int(whole.sum()),
        "target_state_rows_excluded_crop": int(excluded_crop.sum()),
        "target_state_rows_non_core_crop_season": int((~whole & ~excluded_crop & ~is_core).sum()),
        "target_state_rows_core_crop_season": int(is_core.sum()),
    }
    core = tg[is_core].copy()
    for cs in scope["core_crop_seasons"]:
        if not ((core["Season"] == cs["season"]) & (core["Crop"] == cs["crop"])).any():
            raise IntegrityError(f"core crop-season not found by exact label: {cs['season']}|{cs['crop']}")
    core["crop_season_id"] = [core_map[(s, c)]["id"] for s, c in zip(core["Season"], core["Crop"])]
    core["unit"] = [core_map[(s, c)]["unit"] for s, c in zip(core["Season"], core["Crop"])]

    checks = [
        ("district_excluded", core["District_Name"].isin(scope["excluded_districts"])),
        ("production_missing", core["Production"].isna()),
        ("production_zero", core["Production"] == 0),
        ("production_negative", core["Production"] < 0),
        ("area_missing", core["Area"].isna()),
        ("area_below_minimum", core["Area"] < excl["min_area_ha"]),
    ]
    if [c[0] for c in checks] != excl["order_of_reasons"]:
        raise IntegrityError("exclusion reason order differs from config")
    masks = {name: mask.fillna(False).astype(bool).to_numpy() for name, mask in checks}
    reasons_per_row = [[name for name in masks if masks[name][i]] for i in range(len(core))]
    core["exclusion_reason"] = [r[0] if r else "" for r in reasons_per_row]
    core["all_exclusion_reasons"] = [";".join(r) for r in reasons_per_row]
    panel = core[core["exclusion_reason"] == ""].copy()
    panel["yield_obs"] = panel["Production"] / panel["Area"]
    if not np.isfinite(panel["yield_obs"]).all() or (panel["yield_obs"] <= 0).any():
        raise IntegrityError("non-finite or non-positive yield in eligible panel")
    panel = panel.sort_values(["crop_season_id", "District_Name", "Crop_Year"]).reset_index(drop=True)
    return panel, core, counts


# ---------------------------------------------------------------- coverage
def check_coverage(panel: pd.DataFrame, cfg: dict, design_name: str) -> list[dict]:
    rules = cfg["coverage_rules"]
    districts = cfg["scope"]["expected_panel_districts"]
    rows = []
    for cs in cfg["scope"]["core_crop_seasons"]:
        sub = panel[panel["crop_season_id"] == cs["id"]]
        total_test = 0
        for fc in cfg["designs"][design_name]["forecasts"]:
            info = sub[sub["Crop_Year"] <= fc["training_cutoff_year"]]
            years_by_district = info.groupby("District_Name")["Crop_Year"].nunique()
            min_years = int(min(years_by_district.get(d, 0) for d in districts))
            test = sub[sub["Crop_Year"] == fc["target_year"]]
            n_test_districts = int(test["District_Name"].nunique())
            total_test += len(test)
            rows.append({"design": design_name, "crop_season_id": cs["id"], "target_year": fc["target_year"],
                         "check": "min_train_years_per_district", "value": min_years,
                         "threshold": rules["min_train_years_per_district"],
                         "passed": min_years >= rules["min_train_years_per_district"]})
            rows.append({"design": design_name, "crop_season_id": cs["id"], "target_year": fc["target_year"],
                         "check": "min_districts_per_test_year", "value": n_test_districts,
                         "threshold": rules["min_districts_per_test_year"],
                         "passed": n_test_districts >= rules["min_districts_per_test_year"]})
        rows.append({"design": design_name, "crop_season_id": cs["id"], "target_year": "all",
                     "check": "min_test_obs_per_evaluation", "value": total_test,
                     "threshold": rules["min_test_obs_per_evaluation"],
                     "passed": total_test >= rules["min_test_obs_per_evaluation"]})
    return rows


def assert_no_gap_observations(panel: pd.DataFrame, cfg: dict) -> None:
    """Rows between training cutoff and forecast origin would make the origin ambiguous."""
    for name, design in cfg["designs"].items():
        for fc in design["forecasts"]:
            gap = panel[(panel["Crop_Year"] > fc["training_cutoff_year"]) &
                        (panel["Crop_Year"] <= fc["forecast_origin_year"])]
            if len(gap):
                raise IntegrityError(f"{name} {fc}: {len(gap)} eligible rows between cutoff and origin")


# --------------------------------------------------------------- baselines
def within_district_slope(info: pd.DataFrame):
    """Pooled within-district OLS slope of yield on year. Returns (beta or None, denominator)."""
    if len(info) == 0:
        return None, 0.0
    grp = info.groupby("District_Name")
    tc = info["Crop_Year"] - grp["Crop_Year"].transform("mean")
    yc = info["yield_obs"] - grp["yield_obs"].transform("mean")
    den = float((tc * tc).sum())
    if not den > 0:
        return None, den
    return float((tc * yc).sum() / den), den


def baseline_predictions(info: pd.DataFrame, district: str, target_year: int,
                         origin_year: int, params: dict) -> dict:
    """Compute B0-B4 for one district/target from a training-only information set."""
    if len(info) == 0:
        raise IntegrityError("empty information set")
    b1_min = params["B1"]["min_years"]
    b2_len = params["B2"]["window_years"]
    b2_min = params["B2"]["min_obs_in_window"]
    b3_len = params["B3"]["lookback_years"]

    b0 = float(info["yield_obs"].mean())
    tbar_all = float(info["Crop_Year"].mean())
    d = info[info["District_Name"] == district]
    n_d = int(len(d))
    common = {"n_info_obs_crop_season": int(len(info)), "n_info_obs_district": n_d,
              "info_min_year": int(info["Crop_Year"].min()), "info_max_year": int(info["Crop_Year"].max())}
    out = {}
    out["B0"] = {"prediction": b0, "rule": "B0:crop_season_mean", "is_fallback": False}

    if n_d >= b1_min:
        b1 = {"prediction": float(d["yield_obs"].mean()), "rule": "B1:district_mean", "is_fallback": False}
    else:
        b1 = {"prediction": b0, "rule": "B1->fallback:B0", "is_fallback": True}
    out["B1"] = b1
    b1_chain = "B1" if not b1["is_fallback"] else "B1->B0"

    w_start, w_end = origin_year - (b2_len - 1), origin_year
    w = d[(d["Crop_Year"] >= w_start) & (d["Crop_Year"] <= w_end)]
    if len(w) >= b2_min:
        out["B2"] = {"prediction": float(w["yield_obs"].mean()), "rule": "B2:recent_window_mean", "is_fallback": False}
    else:
        out["B2"] = {"prediction": b1["prediction"], "rule": f"B2->fallback:{b1_chain}", "is_fallback": True}
    out["B2"].update({"b2_window_start": w_start, "b2_window_end": w_end, "b2_window_n_obs": int(len(w))})

    lb = d[(d["Crop_Year"] >= origin_year - (b3_len - 1)) & (d["Crop_Year"] <= origin_year)]
    if len(lb):
        last = lb.sort_values("Crop_Year").iloc[-1]
        out["B3"] = {"prediction": float(last["yield_obs"]), "rule": "B3:last_observed", "is_fallback": False,
                     "b3_source_year": int(last["Crop_Year"]), "b3_source_line": int(last["source_line"])}
    else:
        out["B3"] = {"prediction": b1["prediction"], "rule": f"B3->fallback:{b1_chain}", "is_fallback": True}

    beta, _den = within_district_slope(info)
    if beta is not None and not b1["is_fallback"]:
        center = float(d["Crop_Year"].mean())
        out["B4"] = {"prediction": b1["prediction"] + beta * (target_year - center),
                     "rule": "B4:district_mean_plus_within_district_trend", "is_fallback": False,
                     "b4_beta": beta, "b4_center_year": center}
    elif beta is not None:
        out["B4"] = {"prediction": b0 + beta * (target_year - tbar_all), "rule": "B4->fallback:B0_plus_trend",
                     "is_fallback": True, "b4_beta": beta, "b4_center_year": tbar_all}
    else:
        out["B4"] = {"prediction": b0, "rule": "B4->fallback:B0", "is_fallback": True}
    for rec in out.values():
        rec.update(common)
    return out


def run_design(panel: pd.DataFrame, cfg: dict, design_name: str) -> pd.DataFrame:
    design = cfg["designs"][design_name]
    params = cfg["baselines"]
    records = []
    for cs in cfg["scope"]["core_crop_seasons"]:
        sub = panel[panel["crop_season_id"] == cs["id"]]
        for fc in design["forecasts"]:
            target, cutoff, origin = fc["target_year"], fc["training_cutoff_year"], fc["forecast_origin_year"]
            info = sub[sub["Crop_Year"] <= cutoff]
            test = sub[sub["Crop_Year"] == target]
            # --- temporal leakage guards
            if int(info["Crop_Year"].max()) > cutoff or not cutoff < target:
                raise IntegrityError("information set exceeds training cutoff")
            if set(info["source_line"]) & set(test["source_line"]):
                raise IntegrityError("target rows present in information set")
            for row in test.itertuples(index=False):
                preds = baseline_predictions(info, row.District_Name, target, origin, params)
                for b in BASELINES:
                    p = preds[b]
                    if p.get("b3_source_year") is not None and not p["b3_source_year"] <= origin < target:
                        raise IntegrityError("B3 source year outside permitted history")
                    rec = {
                        "design": design_name, "design_role": design["role"], "crop_season_id": cs["id"],
                        "season": cs["season"], "crop": cs["crop"], "unit": cs["unit"],
                        "district": row.District_Name, "target_year": target,
                        "training_cutoff_year": cutoff, "forecast_origin_year": origin,
                        "source_line": int(row.source_line), "observed_area": float(row.Area),
                        "observed_production": float(row.Production), "observed_yield": float(row.yield_obs),
                        "baseline": b,
                    }
                    rec.update(p)
                    records.append(rec)
    out = pd.DataFrame.from_records(records)
    out["error"] = out["prediction"] - out["observed_yield"]
    out["abs_error"] = out["error"].abs()
    out["is_negative"] = out["prediction"] < 0
    for col in PREDICTION_COLUMNS:
        if col not in out.columns:
            out[col] = np.nan
    for col in ("b2_window_start", "b2_window_end", "b2_window_n_obs", "b3_source_year", "b3_source_line"):
        out[col] = out[col].astype("Int64")
    return out[PREDICTION_COLUMNS]


# ------------------------------------------------------------------ metrics
def compute_metrics(observed, predicted) -> dict:
    y = np.asarray(observed, dtype=float)
    p = np.asarray(predicted, dtype=float)
    if y.shape != p.shape or y.size == 0:
        raise ValueError("observed and predicted must be non-empty and the same length")
    e = p - y
    mse = float(np.mean(e * e))
    denom = float(np.sum(np.abs(y)))
    wape = float(np.sum(np.abs(e)) / denom) if denom > 0 else None
    return {"n": int(y.size), "mae": float(np.mean(np.abs(e))), "rmse": math.sqrt(mse), "bias": float(np.mean(e)),
            "mse": mse, "wape": wape,
            "wape_note": "" if wape is not None else "undefined: sum of |observed| is zero"}


def skill_vs_reference(mse: float, mse_ref: float):
    if mse_ref > 0:
        return 1.0 - mse / mse_ref, ""
    return None, "undefined: B1 MSE is zero"


def metric_table(pred: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows = []
    for key, g in pred.groupby(group_cols + ["baseline"], sort=True):
        key = key if isinstance(key, tuple) else (key,)
        m = compute_metrics(g["observed_yield"], g["prediction"])
        rec = dict(zip(group_cols + ["baseline"], key))
        rec.update(m)
        rec["n_districts"] = int(g["district"].nunique())
        rec["n_test_years"] = int(g["target_year"].nunique())
        rec["n_fallback"] = int(g["is_fallback"].sum())
        rec["n_negative"] = int(g["is_negative"].sum())
        per_target = g.groupby("target_year")["n_info_obs_crop_season"].agg(["min", "max"])
        if (per_target["min"] != per_target["max"]).any():
            raise IntegrityError("inconsistent info-set size within a forecast")
        rec["n_train_obs_min"] = int(per_target["min"].min())
        rec["n_train_obs_max"] = int(per_target["max"].max())
        rec["n_train_obs_by_target"] = ";".join(f"{t}={int(v)}" for t, v in per_target["min"].items())
        rows.append(rec)
    tab = pd.DataFrame(rows)
    # skill vs B1 on identical rows
    skills, notes = [], []
    for _, r in tab.iterrows():
        mask = np.ones(len(tab), dtype=bool)
        for c in group_cols:
            mask &= (tab[c] == r[c]).to_numpy()
        ref = tab[mask & (tab["baseline"] == "B1").to_numpy()]
        if len(ref) != 1 or int(ref["n"].iloc[0]) != int(r["n"]):
            raise IntegrityError("B1 reference rows do not match")
        s, note = skill_vs_reference(r["mse"], float(ref["mse"].iloc[0]))
        skills.append(s)
        notes.append(note)
    tab["skill_vs_b1"] = skills
    tab["skill_note"] = notes
    return tab


def baseline_summary(cs_metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (design, b), g in cs_metrics.groupby(["design", "baseline"], sort=True):
        w = g["wape"].dropna()
        s = g["skill_vs_b1"].dropna()
        rows.append({"design": design, "baseline": b, "n_evaluations": int(len(g)),
                     "median_wape": float(w.median()) if len(w) else None,
                     "n_wape_undefined": int(g["wape"].isna().sum()),
                     "median_skill_vs_b1": float(s.median()) if len(s) else None,
                     "n_beats_b1": int((s > 0).sum()), "n_worse_than_b1": int((s < 0).sum()),
                     "n_equal_to_b1": int((s == 0).sum()), "n_skill_undefined": int(g["skill_vs_b1"].isna().sum()),
                     "n_fallback_predictions": int(g["n_fallback"].sum()),
                     "n_negative_predictions": int(g["n_negative"].sum())})
    return pd.DataFrame(rows)


def outlier_flags(panel: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    spec = cfg["outlier_flags"]
    fc = cfg["designs"][spec["design"]]["forecasts"][0]
    cutoff = fc["training_cutoff_year"]
    test_years = [f["target_year"] for f in cfg["designs"][spec["design"]]["forecasts"]]
    rows = []
    for cs_id, sub in panel.groupby("crop_season_id", sort=True):
        train = sub[sub["Crop_Year"] <= cutoff]
        med = float(train["yield_obs"].median())
        mad = float((train["yield_obs"] - med).abs().median())
        scope = sub[(sub["Crop_Year"] <= cutoff) | sub["Crop_Year"].isin(test_years)]
        for r in scope.itertuples(index=False):
            y = float(r.yield_obs)
            z = (y - med) / (1.4826 * mad) if mad > 0 else None
            if z is not None and abs(z) > spec["threshold_abs"]:
                rows.append({"crop_season_id": cs_id, "district": r.District_Name, "year": int(r.Crop_Year),
                             "split": "train" if r.Crop_Year <= cutoff else "test", "source_line": int(r.source_line),
                             "yield": y, "train_median": med, "train_mad": mad, "robust_z": z,
                             "action": "flag_only"})
    cols = ["crop_season_id", "district", "year", "split", "source_line", "yield", "train_median", "train_mad",
            "robust_z", "action"]
    return pd.DataFrame(rows, columns=cols)


# ---------------------------------------------------------------- reporting
def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, lineterminator="\n", float_format=FLOAT_FORMAT)


def write_json(obj, path: Path) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True, ensure_ascii=True, default=_json_default)
        fh.write("\n")


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    raise TypeError(type(o))


def data_quality_markdown(audit: dict, coverage: pd.DataFrame, exclusions: pd.DataFrame, cfg: dict) -> str:
    lines = [f"# Data quality and exclusion report - {cfg['experiment_id']}", "",
             "Generated deterministically by `src/tg_baselines.py`.", "",
             "## Source dataset", "",
             f"- Path: `{cfg['dataset']['path']}`",
             f"- SHA-256: `{audit['dataset_sha256']}` (matches config: {audit['dataset_sha256_matches_config']})",
             f"- Rows: {audit['dataset_rows']}; columns: {', '.join(audit['columns'])}",
             f"- Crop_Year range (all states): {audit['year_min_all']}-{audit['year_max_all']}",
             f"- Duplicate keys ({', '.join(cfg['dataset']['key_columns'])}) after whitespace normalisation: "
             f"{audit['duplicate_key_rows_all']} rows in full dataset, {audit['duplicate_key_rows_core_scope']} in core scope",
             "", "## Telangana coverage", "",
             f"- Raw state label(s): {audit['raw_state_labels']}",
             f"- Telangana rows: {audit['scope_counts']['rows_target_state']}",
             f"- Telangana years present: {audit['target_state_years_present']}",
             f"- Expected-absent years confirmed absent: {audit['expected_absent_years_confirmed']}",
             f"- Districts (raw): {', '.join(audit['target_state_districts'])}",
             f"- Crop-district-years with both 'Whole Year' and a seasonal record: {len(audit['whole_year_overlaps'])} "
             f"(crops: {', '.join(sorted({o.split('|')[1] for o in audit['whole_year_overlaps']}))}); none are core crop-seasons",
             "", "## Scope funnel", "", "| Step | Rows |", "|---|---:|"]
    for k, v in audit["scope_counts"].items():
        lines.append(f"| {k} | {v} |")
    lines += ["", "## Core-scope exclusions (primary reason)", "", "| Reason | Rows |", "|---|---:|"]
    for k, v in audit["core_exclusions_by_reason"].items():
        lines.append(f"| {k} | {v} |")
    lines += [f"| **total excluded** | {audit['core_rows_excluded']} |",
              f"| **eligible panel rows** | {audit['eligible_panel_rows']} |", "",
              "## Excluded core rows by crop-season and split", "", "| crop_season_id | split | reason | rows |",
              "|---|---|---|---:|"]
    if len(exclusions):
        cut = cfg["designs"]["fixed_origin"]["forecasts"][0]["training_cutoff_year"]
        ex = exclusions.assign(split=np.where(exclusions["Crop_Year"] <= cut, f"train(<={cut})", "test/later"))
        for (cs, sp, rs), n in ex.groupby(["crop_season_id", "split", "exclusion_reason"]).size().items():
            lines.append(f"| {cs} | {sp} | {rs} | {n} |")
    lines += ["", "## Eligible observations per crop-season", "",
              "| crop_season_id | unit | train (<=2009) | test (2010, 2011, 2013, 2014) | districts |",
              "|---|---|---:|---:|---:|"]
    for r in audit["eligible_by_crop_season"]:
        lines.append(f"| {r['crop_season_id']} | {r['unit']} | {r['train_rows_le_2009']} | {r['test_rows']} | {r['districts']} |")
    lines += ["", "## Coverage rules", "",
              f"- Minimum eligible training years per district: {cfg['coverage_rules']['min_train_years_per_district']}",
              f"- Minimum districts per test year: {cfg['coverage_rules']['min_districts_per_test_year']}",
              f"- Minimum test observations per evaluation: {cfg['coverage_rules']['min_test_obs_per_evaluation']}",
              f"- Checks evaluated: {len(coverage)}; failed: {int((~coverage['passed']).sum())}", "",
              "Lowest observed values per check and design:", "", "| design | check | lowest value | threshold |",
              "|---|---|---:|---:|"]
    for (d, c), g in coverage.groupby(["design", "check"]):
        lines.append(f"| {d} | {c} | {int(g['value'].min())} | {int(g['threshold'].iloc[0])} |")
    lines += ["", "## Unit caveats", "", "The source has no unit column. Units below are inferred, not verified:", ""]
    for cs in cfg["scope"]["core_crop_seasons"]:
        lines.append(f"- **{cs['id']}** ({cs['unit']}): {cs['unit_note']}")
    lines += ["", f"- Area cutoff: {cfg['row_exclusions']['min_area_note']}", ""]
    return "\n".join(lines)


# --------------------------------------------------------------------- main
def run(config_path: Path, out_dir: Path, data_override=None) -> int:
    started = time.time()
    started_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cfg = load_config(config_path)
    data_path = resolve_data_path(cfg, config_path, data_override)
    out_dir = out_dir.resolve()
    if out_dir == data_path.parent or data_path.parent in out_dir.parents:
        raise IntegrityError(f"refusing to write inside the dataset directory {data_path.parent}")
    if out_dir.exists():
        raise IntegrityError(f"output directory already exists: {out_dir}")

    df, digest = load_dataset(cfg, data_path)
    raw_state_labels = sorted({s for s in pd.read_csv(data_path, usecols=["State_Name"], dtype=str)["State_Name"]
                               if s.strip() == cfg["scope"]["state"]})
    dup_all = find_duplicate_keys(df, cfg["dataset"]["key_columns"])
    panel, core, scope_counts = classify_rows(df, cfg)
    dup_core = find_duplicate_keys(core, cfg["dataset"]["key_columns"])
    if len(dup_core):
        raise IntegrityError(f"{len(dup_core)} duplicate-key rows in core scope; investigate before scoring")

    tg = df[df["State_Name"] == cfg["scope"]["state"]]
    years_present = sorted(int(y) for y in tg["Crop_Year"].unique())
    absent_ok = all(y not in years_present for y in cfg["expected_absent_years"])
    if not absent_ok:
        raise IntegrityError("expected-absent year is present; design assumptions no longer hold")
    for design in cfg["designs"].values():
        for fc in design["forecasts"]:
            if fc["target_year"] not in years_present:
                raise IntegrityError(f"target year {fc['target_year']} absent from Telangana records")
    if sorted(panel["District_Name"].unique()) != sorted(cfg["scope"]["expected_panel_districts"]):
        raise IntegrityError(f"panel districts differ from config: {sorted(panel['District_Name'].unique())}")
    wy = tg.groupby(["District_Name", "Crop", "Crop_Year"])["Season"].apply(lambda s: tuple(sorted(set(s))))
    overlaps = sorted(f"{d}|{c}|{y}|{'+'.join(s)}" for (d, c, y), s in wy.items()
                      if "Whole Year" in s and len(s) > 1)
    assert_no_gap_observations(panel, cfg)

    exclusions = core[core["exclusion_reason"] != ""].sort_values(["crop_season_id", "District_Name", "Crop_Year"])
    exclusions = exclusions[["source_line", "crop_season_id", "State_Name", "District_Name", "Crop_Year", "Season",
                             "Crop", "Area", "Production", "exclusion_reason", "all_exclusion_reasons"]]
    test_years = [f["target_year"] for f in cfg["designs"]["fixed_origin"]["forecasts"]]
    fixed_cutoff = cfg["designs"]["fixed_origin"]["forecasts"][0]["training_cutoff_year"]
    if any(f["training_cutoff_year"] != fixed_cutoff for f in cfg["designs"]["fixed_origin"]["forecasts"]):
        raise IntegrityError("fixed-origin design must use a single training cutoff")
    eligible_by_cs = []
    for cs in cfg["scope"]["core_crop_seasons"]:
        sub = panel[panel["crop_season_id"] == cs["id"]]
        eligible_by_cs.append({"crop_season_id": cs["id"], "unit": cs["unit"],
                               "train_rows_le_2009": int((sub["Crop_Year"] <= fixed_cutoff).sum()),
                               "test_rows": int(sub["Crop_Year"].isin(test_years).sum()),
                               "districts": int(sub["District_Name"].nunique())})
    coverage = pd.DataFrame(check_coverage(panel, cfg, "fixed_origin") + check_coverage(panel, cfg, "rolling_origin"))
    audit = {
        "experiment_id": cfg["experiment_id"], "dataset_sha256": digest,
        "dataset_sha256_matches_config": digest == cfg["dataset"]["sha256"], "dataset_rows": int(len(df)),
        "columns": cfg["dataset"]["expected_columns"],
        "year_min_all": int(df["Crop_Year"].min()), "year_max_all": int(df["Crop_Year"].max()),
        "duplicate_key_rows_all": int(len(dup_all)), "duplicate_key_rows_core_scope": int(len(dup_core)),
        "raw_state_labels": [repr(s) for s in raw_state_labels],
        "target_state_years_present": years_present,
        "expected_absent_years": cfg["expected_absent_years"], "expected_absent_years_confirmed": absent_ok,
        "target_state_districts": sorted(tg["District_Name"].unique()),
        "whole_year_overlaps": overlaps, "scope_counts": scope_counts,
        "core_exclusions_by_reason": {r: int((core["exclusion_reason"] == r).sum())
                                      for r in cfg["row_exclusions"]["order_of_reasons"]},
        "core_rows_excluded": int((core["exclusion_reason"] != "").sum()),
        "eligible_panel_rows": int(len(panel)), "eligible_by_crop_season": eligible_by_cs,
        "coverage_checks": int(len(coverage)), "coverage_failures": int((~coverage["passed"]).sum()),
    }
    out_dir.mkdir(parents=True, exist_ok=False)
    write_csv(exclusions, out_dir / "exclusions.csv")
    write_csv(coverage, out_dir / "coverage.csv")
    write_json(audit, out_dir / "data_audit.json")
    (out_dir / "data_quality_report.md").write_text(data_quality_markdown(audit, coverage, exclusions, cfg),
                                                    encoding="utf-8", newline="\n")
    if audit["coverage_failures"]:
        failed = coverage[~coverage["passed"]]
        print("COVERAGE FAILURE - scoring aborted:\n" + failed.to_string(index=False), file=sys.stderr)
        return 2

    preds = pd.concat([run_design(panel, cfg, "fixed_origin"), run_design(panel, cfg, "rolling_origin")],
                      ignore_index=True)
    preds = preds.sort_values(["design", "crop_season_id", "target_year", "district", "baseline"]).reset_index(drop=True)
    # identical target rows in both designs, five baselines each
    keys = {d: set(map(tuple, g[["crop_season_id", "district", "target_year", "source_line"]].values))
            for d, g in preds.groupby("design")}
    if keys["fixed_origin"] != keys["rolling_origin"]:
        raise IntegrityError("fixed and rolling designs evaluate different target rows")
    if (preds.groupby(["design", "source_line"])["baseline"].nunique() != len(BASELINES)).any():
        raise IntegrityError("some target rows lack a prediction for every baseline")
    if (preds["training_cutoff_year"] >= preds["target_year"]).any():
        raise IntegrityError("training cutoff not strictly before target year")
    if (preds["info_max_year"] > preds["training_cutoff_year"]).any():
        raise IntegrityError("information set exceeds training cutoff")

    cs_metrics = metric_table(preds, ["design", "crop_season_id", "season", "crop", "unit"])
    year_metrics = metric_table(preds, ["design", "crop_season_id", "season", "crop", "unit", "target_year"])
    summary = baseline_summary(cs_metrics)
    flags = outlier_flags(panel, cfg)

    write_csv(preds, out_dir / "predictions.csv")
    metric_cols = ["n", "n_districts", "n_test_years", "n_train_obs_min", "n_train_obs_max", "n_train_obs_by_target",
                   "mae", "rmse", "bias", "mse", "wape", "wape_note", "skill_vs_b1", "skill_note",
                   "n_fallback", "n_negative"]
    write_csv(cs_metrics[["design", "crop_season_id", "season", "crop", "unit", "baseline"] + metric_cols],
              out_dir / "metrics_by_crop_season.csv")
    write_csv(year_metrics[["design", "crop_season_id", "season", "crop", "unit", "target_year", "baseline"]
                           + metric_cols], out_dir / "metrics_by_crop_season_year.csv")
    write_csv(summary, out_dir / "baseline_summary.csv")
    write_csv(flags, out_dir / "outlier_flags.csv")

    src_files = sorted(Path(__file__).resolve().parent.glob("*.py"))
    produced = sorted(p.name for p in out_dir.iterdir() if p.is_file())
    manifest = {
        "experiment_id": cfg["experiment_id"],
        "config_path": Path(config_path).resolve().relative_to(project_root(config_path)).as_posix(),
        "config_sha256": sha256_file(config_path),
        "source_files_sha256": {p.name: sha256_file(p) for p in src_files},
        "dataset_path": cfg["dataset"]["path"], "dataset_sha256": digest, "dataset_rows": int(len(df)),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__, "pandas_version": pd.__version__,
        "designs": {k: v["role"] for k, v in cfg["designs"].items()},
        "n_predictions": int(len(preds)), "n_target_rows_per_design": int(len(keys["fixed_origin"])),
        "assertions_passed": [
            "dataset_sha256_matches_config", "schema_and_row_count", "no_duplicate_keys_in_core_scope",
            "all_core_crop_seasons_found_by_exact_label", "panel_districts_match_config",
            "expected_absent_years_absent", "no_rows_between_cutoff_and_origin", "coverage_rules_pass",
            "info_set_max_year_le_cutoff", "cutoff_lt_target", "target_rows_not_in_info_set",
            "b3_source_within_permitted_history", "same_target_rows_both_designs", "five_baselines_per_target_row",
            "b1_reference_rows_match"],
        "output_files_sha256": {name: sha256_file(out_dir / name) for name in produced},
        "nondeterministic_files": cfg["output"]["nondeterministic_files"],
    }
    write_json(manifest, out_dir / "run_manifest.json")
    write_json({"started_utc": started_iso, "finished_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "elapsed_seconds": round(time.time() - started, 3), "output_dir": str(out_dir),
                "dataset_file_used": str(data_path), "python_executable": sys.executable,
                "argv": sys.argv}, out_dir / "run_timing.json")
    expected = sorted(cfg["output"]["files"])
    actual = sorted(p.name for p in out_dir.iterdir() if p.is_file())
    if actual != expected:
        raise IntegrityError(f"output file set mismatch: {actual}")
    print(f"OK: {len(preds)} predictions, {len(cs_metrics)} crop-season metric rows -> {out_dir}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True, type=Path, help="experiment configuration (configs/tg_baselines_v1.json)")
    ap.add_argument("--out", required=True, type=Path, help="new output directory (must not exist)")
    ap.add_argument("--data", type=Path, default=None,
                    help="dataset CSV location; overrides dataset.path in the config (SHA-256 is still verified)")
    args = ap.parse_args(argv)
    try:
        return run(args.config, args.out, args.data)
    except (IntegrityError, CoverageError) as exc:
        print(f"INTEGRITY FAILURE: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
