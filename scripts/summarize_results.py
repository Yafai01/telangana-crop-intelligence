"""Derive report tables from a completed run (read-only on the run folder).

    python -I -B scripts/summarize_results.py --config configs/tg_baselines_v1.json \
        --run runs/my_run --out runs/my_run_analysis [--data PATH]

Writes analysis_tables.md and per-table CSVs. Deterministic; no new modelling.
The 2009-vs-history table reads the dataset (training years only), so the dataset must be available.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import tg_baselines as tb  # noqa: E402


def md_table(df: pd.DataFrame, floatfmt: str = "{:.3f}") -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                cells.append("n/a" if pd.isna(v) else floatfmt.format(v))
            else:
                cells.append(str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--data", type=Path, default=None, help="dataset CSV; overrides dataset.path in the config")
    args = ap.parse_args(argv)
    if args.out.exists():
        print(f"refusing to overwrite {args.out}", file=sys.stderr)
        return 4
    cfg = tb.load_config(args.config)
    m = pd.read_csv(args.run / "metrics_by_crop_season.csv")
    my = pd.read_csv(args.run / "metrics_by_crop_season_year.csv")
    summary = pd.read_csv(args.run / "baseline_summary.csv")
    order = [c["id"] for c in cfg["scope"]["core_crop_seasons"]]
    units = {c["id"]: c["unit"] for c in cfg["scope"]["core_crop_seasons"]}
    args.out.mkdir(parents=True)
    sections = ["# Analysis tables - tg_baselines_v1", "",
                "Derived from a complete run's `metrics_by_crop_season.csv`, `metrics_by_crop_season_year.csv` and "
                "`baseline_summary.csv` by `scripts/summarize_results.py`. Native-unit metrics are per crop-season only.", ""]

    for design in ("fixed_origin", "rolling_origin"):
        s = m[m["design"] == design]
        for metric in ("skill_vs_b1", "wape", "rmse", "bias"):
            p = s.pivot(index="crop_season_id", columns="baseline", values=metric).reindex(order).reset_index()
            if metric in ("rmse", "bias"):
                p.insert(1, "unit", p["crop_season_id"].map(units))
            p.to_csv(args.out / f"{design}_{metric}.csv", index=False, lineterminator="\n", float_format="%.6f")
            sections += [f"## {design}: {metric}", "", md_table(p), ""]
        best = s.loc[s.groupby("crop_season_id")["rmse"].idxmin(), ["crop_season_id", "baseline", "rmse", "skill_vs_b1"]]
        best = best.set_index("crop_season_id").reindex(order).reset_index()
        best.insert(1, "unit", best["crop_season_id"].map(units))
        best.to_csv(args.out / f"{design}_lowest_rmse_baseline.csv", index=False, lineterminator="\n", float_format="%.6f")
        sections += [f"## {design}: lowest-RMSE baseline per crop-season", "", md_table(best), ""]

        y = my[my["design"] == design]
        per_year = []
        for b in ("B0", "B2", "B3", "B4"):
            sub = y[y["baseline"] == b]
            for yr, g in sub.groupby("target_year"):
                sk = g["skill_vs_b1"].dropna()
                per_year.append({"baseline": b, "target_year": int(yr), "n_crop_seasons": int(len(g)),
                                 "n_beats_b1": int((sk > 0).sum()), "median_skill_vs_b1": float(sk.median()),
                                 "median_wape": float(g["wape"].median())})
        py = pd.DataFrame(per_year)
        py.to_csv(args.out / f"{design}_per_year_vs_b1.csv", index=False, lineterminator="\n", float_format="%.6f")
        sections += [f"## {design}: per-test-year comparison with B1 (counts across 12 crop-seasons)", "", md_table(py), ""]

        b1 = y[y["baseline"] == "B1"].copy()
        b1["relative_bias"] = b1["bias"] / (b1["mae"] / b1["wape"])   # bias / mean observed yield
        rb = b1.pivot(index="crop_season_id", columns="target_year", values="relative_bias").reindex(order).reset_index()
        rb.to_csv(args.out / f"{design}_b1_relative_bias_by_year.csv", index=False, lineterminator="\n", float_format="%.6f")
        sections += [f"## {design}: B1 bias relative to mean observed yield, by test year (negative = under-prediction)",
                     "", md_table(rb), ""]

    # 2009 relative to the 1997-2008 training mean (training data only; explains B3 behaviour)
    df, _ = tb.load_dataset(cfg, tb.resolve_data_path(cfg, args.config, args.data))
    panel, _, _ = tb.classify_rows(df, cfg)
    rows = []
    for cs in order:
        sub = panel[panel["crop_season_id"] == cs]
        hist = sub[sub["Crop_Year"] <= 2008].groupby("District_Name")["yield_obs"].mean()
        y09 = sub[sub["Crop_Year"] == 2009].set_index("District_Name")["yield_obs"]
        ratio = (y09 / hist.reindex(y09.index)).dropna()
        rows.append({"crop_season_id": cs, "n_districts_2009": int(len(ratio)),
                     "median_ratio_2009_to_1997_2008_district_mean": float(ratio.median())})
    a09 = pd.DataFrame(rows)
    a09.to_csv(args.out / "year_2009_vs_history.csv", index=False, lineterminator="\n", float_format="%.6f")
    sections += ["## 2009 yield relative to each district's 1997-2008 mean (training data only)", "",
                 "B3 (fixed origin) uses the 2009 value for most districts, so an unusual 2009 propagates to all test years.",
                 "", md_table(a09), ""]

    sections += ["## Baseline summary (unit-free)", "", md_table(summary, "{:.4f}"), ""]
    (args.out / "analysis_tables.md").write_text("\n".join(sections), encoding="utf-8", newline="\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
