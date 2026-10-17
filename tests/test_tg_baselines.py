"""Automated checks for the Telangana baseline experiment (standard-library unittest).

Run from the project root:
    python -I -B -m unittest discover -s tests -v

Optional environment variables:
    TCI_DATA     dataset CSV location (default: dataset.path from the config, i.e. data/raw/...)
    TCI_RUN_DIR  a complete local run folder to validate (record-level checks and reproduction check)

Without the dataset, the dataset-dependent tests are skipped (reported as skipped, not passed).
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import tg_baselines as tb  # noqa: E402

CONFIG_PATH = ROOT / "configs" / "tg_baselines_v1.json"
CFG = tb.load_config(CONFIG_PATH)
DATA_PATH = tb.resolve_data_path(CFG, CONFIG_PATH, os.environ.get("TCI_DATA"))
HAVE_DATA = DATA_PATH.is_file()
NO_DATA_MSG = "dataset not available (see data/README.md); set TCI_DATA or place it at dataset.path"
RUN_DIR = Path(os.environ["TCI_RUN_DIR"]).resolve() if os.environ.get("TCI_RUN_DIR") else None
HAVE_RUN = RUN_DIR is not None and RUN_DIR.is_dir()
PUBLISHED = ROOT / "results" / "tg_baselines_v1"
WITHHELD = {"predictions.csv", "exclusions.csv", "outlier_flags.csv", "run_timing.json"}
TOL = 1e-6  # predictions are written with 6 decimals


def _sha(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _panel(rows):
    """rows: (district, year, yield[, source_line])"""
    recs = []
    for i, r in enumerate(rows):
        recs.append({"District_Name": r[0], "Crop_Year": r[1], "yield_obs": float(r[2]),
                     "source_line": r[3] if len(r) > 3 else 1000 + i})
    return pd.DataFrame(recs)


PARAMS = CFG["baselines"]


# =============================================================== unit tests
class TestMetrics(unittest.TestCase):
    def test_basic_values(self):
        m = tb.compute_metrics([1.0, 2.0, 3.0], [2.0, 2.0, 1.0])
        self.assertEqual(m["n"], 3)
        self.assertAlmostEqual(m["mae"], 1.0)
        self.assertAlmostEqual(m["rmse"], math.sqrt(5 / 3))
        self.assertAlmostEqual(m["bias"], -1 / 3)          # prediction minus observed
        self.assertAlmostEqual(m["wape"], 3 / 6)
        self.assertEqual(m["wape_note"], "")

    def test_wape_zero_denominator_is_undefined_not_zero(self):
        m = tb.compute_metrics([0.0, 0.0], [1.0, -1.0])
        self.assertIsNone(m["wape"])
        self.assertIn("undefined", m["wape_note"])

    def test_skill_formula_and_undefined_case(self):
        s, note = tb.skill_vs_reference(1.0, 4.0)
        self.assertAlmostEqual(s, 0.75)
        self.assertEqual(note, "")
        s, note = tb.skill_vs_reference(1.0, 0.0)
        self.assertIsNone(s)
        self.assertIn("undefined", note)

    def test_rejects_empty_or_mismatched(self):
        with self.assertRaises(ValueError):
            tb.compute_metrics([], [])
        with self.assertRaises(ValueError):
            tb.compute_metrics([1.0], [1.0, 2.0])


class TestBaselines(unittest.TestCase):
    def test_b0_b1_b2_b3_native(self):
        rows = [("A", y, v) for y, v in zip(range(2000, 2010), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])]
        rows += [("B", y, 100.0) for y in range(2000, 2010)]
        info = _panel(rows)
        p = tb.baseline_predictions(info, "A", 2010, 2009, PARAMS)
        self.assertAlmostEqual(p["B0"]["prediction"], (55 + 1000) / 20)
        self.assertAlmostEqual(p["B1"]["prediction"], 5.5)
        self.assertAlmostEqual(p["B2"]["prediction"], (6 + 7 + 8 + 9 + 10) / 5)   # 2005-2009
        self.assertEqual((p["B2"]["b2_window_start"], p["B2"]["b2_window_end"]), (2005, 2009))
        self.assertAlmostEqual(p["B3"]["prediction"], 10.0)
        self.assertEqual(p["B3"]["b3_source_year"], 2009)
        for b in tb.BASELINES:
            self.assertFalse(p[b]["is_fallback"], b)

    def test_b1_falls_back_to_b0_below_five_years(self):
        info = _panel([("A", 2006, 1), ("A", 2007, 1), ("A", 2008, 1), ("A", 2009, 1)] +
                      [("B", y, 5) for y in range(2000, 2010)])
        p = tb.baseline_predictions(info, "A", 2010, 2009, PARAMS)
        self.assertEqual(p["B1"]["rule"], "B1->fallback:B0")
        self.assertAlmostEqual(p["B1"]["prediction"], p["B0"]["prediction"])

    def test_b2_fallback_order_b1_then_b0(self):
        info = _panel([("A", y, 2.0) for y in range(1997, 2003)] + [("A", 2008, 9.0), ("A", 2009, 9.0)] +
                      [("B", y, 5.0) for y in range(2000, 2010)])
        p = tb.baseline_predictions(info, "A", 2010, 2009, PARAMS)
        self.assertEqual(p["B2"]["rule"], "B2->fallback:B1")
        self.assertAlmostEqual(p["B2"]["prediction"], p["B1"]["prediction"])
        info2 = pd.concat([info, _panel([("C", 2008, 1.0), ("C", 2009, 1.0)])], ignore_index=True)
        p2 = tb.baseline_predictions(info2, "C", 2010, 2009, PARAMS)
        self.assertEqual(p2["B2"]["rule"], "B2->fallback:B1->B0")
        self.assertAlmostEqual(p2["B2"]["prediction"], p2["B0"]["prediction"])

    def test_b3_lookback_window_and_fallback(self):
        info = _panel([("A", y, float(y - 1990)) for y in range(1997, 2007)] + [("B", 2009, 3.0)])
        p = tb.baseline_predictions(info, "A", 2010, 2009, PARAMS)   # A's latest is 2006 < 2007
        self.assertEqual(p["B3"]["rule"], "B3->fallback:B1")
        info = _panel([("A", y, float(y - 1990)) for y in range(1997, 2009)])
        p = tb.baseline_predictions(info, "A", 2010, 2009, PARAMS)   # latest 2008 within [2007, 2009]
        self.assertEqual(p["B3"]["b3_source_year"], 2008)
        self.assertAlmostEqual(p["B3"]["prediction"], 18.0)

    def test_b4_within_district_trend_removes_district_levels(self):
        rows = [("A", y, 1.0 + 0.1 * (y - 2000)) for y in range(2000, 2010)]
        rows += [("B", y, 10.0 + 0.1 * (y - 2000)) for y in range(1997, 2003)]
        info = _panel(rows)
        beta, _den = tb.within_district_slope(info)
        self.assertAlmostEqual(beta, 0.1)
        naive = np.polyfit(info["Crop_Year"], info["yield_obs"], 1)[0]
        self.assertLess(naive, 0)   # pooled, uncentred slope is confounded by district levels
        p = tb.baseline_predictions(info, "A", 2010, 2009, PARAMS)
        self.assertAlmostEqual(p["B4"]["prediction"], 1.0 + 0.1 * 10)
        self.assertEqual(p["B4"]["rule"], "B4:district_mean_plus_within_district_trend")

    def test_b4_fallbacks(self):
        info = _panel([("A", y, 1.0 + 0.1 * (y - 2000)) for y in range(2000, 2010)] + [("C", 2009, 4.0)])
        p = tb.baseline_predictions(info, "C", 2010, 2009, PARAMS)
        self.assertEqual(p["B4"]["rule"], "B4->fallback:B0_plus_trend")
        b0 = p["B0"]["prediction"]
        self.assertAlmostEqual(p["B4"]["prediction"], b0 + 0.1 * (2010 - info["Crop_Year"].mean()))
        one_year = _panel([("A", 2009, 1.0), ("B", 2009, 3.0)])
        p = tb.baseline_predictions(one_year, "A", 2010, 2009, PARAMS)
        self.assertEqual(p["B4"]["rule"], "B4->fallback:B0")
        self.assertAlmostEqual(p["B4"]["prediction"], 2.0)

    def test_negative_b4_prediction_is_kept_and_flagged(self):
        info = _panel([("A", y, 1.0 - 0.2 * (y - 2000)) for y in range(2000, 2005)])   # 1.0 ... 0.2
        p = tb.baseline_predictions(info, "A", 2014, 2004, PARAMS)
        self.assertAlmostEqual(p["B4"]["prediction"], -1.8)   # 0.6 - 0.2 * 12, not clipped


def _synthetic_cfg():
    cfg = json.loads(json.dumps(CFG))
    cfg["scope"]["core_crop_seasons"] = [{"id": "cs", "season": "Kharif", "crop": "X", "unit": "t/ha", "unit_note": ""}]
    cfg["scope"]["expected_panel_districts"] = ["A", "B"]
    return cfg


def _synthetic_panel(target_value=1.0):
    rows = []
    line = 10
    for d, level in (("A", 1.0), ("B", 3.0)):
        for y in list(range(1997, 2012)) + [2013, 2014]:
            v = level + 0.05 * (y - 1997)
            if y >= 2010:
                v = target_value
            rows.append({"crop_season_id": "cs", "District_Name": d, "Crop_Year": y, "yield_obs": v,
                         "source_line": line, "Area": 100.0, "Production": 100.0 * v})
            line += 1
    return pd.DataFrame(rows)


class TestTemporalSafety(unittest.TestCase):
    def test_predictions_do_not_depend_on_target_period_values(self):
        cfg = _synthetic_cfg()
        a = tb.run_design(_synthetic_panel(1.0), cfg, "fixed_origin")
        b = tb.run_design(_synthetic_panel(999.0), cfg, "fixed_origin")
        self.assertTrue(np.allclose(a["prediction"].to_numpy(), b["prediction"].to_numpy()))
        self.assertFalse(np.allclose(a["observed_yield"].to_numpy(), b["observed_yield"].to_numpy()))

    def test_rolling_uses_only_strictly_earlier_years(self):
        cfg = _synthetic_cfg()
        base = tb.run_design(_synthetic_panel(1.0), cfg, "rolling_origin")
        changed_panel = _synthetic_panel(1.0)
        changed_panel.loc[changed_panel["Crop_Year"] == 2014, "yield_obs"] = 500.0
        changed = tb.run_design(changed_panel, cfg, "rolling_origin")
        for year in (2010, 2011, 2013):
            m = base["target_year"] == year
            self.assertTrue(np.allclose(base.loc[m, "prediction"], changed.loc[m, "prediction"]), year)
        self.assertTrue((base["info_max_year"] < base["target_year"]).all())
        self.assertTrue((base["info_max_year"] <= base["training_cutoff_year"]).all())

    def test_gap_rows_between_cutoff_and_origin_are_rejected(self):
        cfg = _synthetic_cfg()
        panel = _synthetic_panel()
        extra = panel.iloc[[0]].copy()
        extra["Crop_Year"] = 2012
        with self.assertRaises(tb.IntegrityError):
            tb.assert_no_gap_observations(pd.concat([panel, extra], ignore_index=True), cfg)


class TestDataRules(unittest.TestCase):
    def _df(self):
        rows = [
            ("Telangana", "HYDERABAD", 2000, "Kharif", "Rice", 100.0, float("nan")),
            ("Telangana", "A", 2000, "Kharif", "Rice", 100.0, float("nan")),
            ("Telangana", "A", 2001, "Kharif", "Rice", 100.0, 0.0),
            ("Telangana", "A", 2002, "Kharif", "Rice", 9.99, 5.0),
            ("Telangana", "A", 2003, "Kharif", "Rice", 10.0, 5.0),
            ("Telangana", "A", 2003, "Whole Year", "Rice", 10.0, 5.0),
            ("Telangana", "A", 2003, "Kharif", "Turmeric", 10.0, 5.0),
            ("Telangana", "A", 2003, "Kharif", "Dry ginger", 10.0, 5.0),
            ("Andhra Pradesh", "B", 2003, "Kharif", "Rice", 10.0, 5.0),
        ]
        df = pd.DataFrame(rows, columns=CFG["dataset"]["expected_columns"])
        df.insert(0, "source_line", range(2, len(df) + 2))
        return df

    def test_exclusion_reasons_and_order(self):
        cfg = json.loads(json.dumps(CFG))
        cfg["scope"]["core_crop_seasons"] = [{"id": "kr", "season": "Kharif", "crop": "Rice", "unit": "t/ha",
                                              "unit_note": ""}]
        panel, core, counts = tb.classify_rows(self._df(), cfg)
        reasons = dict(zip(core["source_line"], core["exclusion_reason"]))
        self.assertEqual(reasons[2], "district_excluded")
        self.assertEqual(core.set_index("source_line").loc[2, "all_exclusion_reasons"],
                         "district_excluded;production_missing")
        self.assertEqual(reasons[3], "production_missing")
        self.assertEqual(reasons[4], "production_zero")
        self.assertEqual(reasons[5], "area_below_minimum")
        self.assertEqual(reasons[6], "")
        self.assertEqual(list(panel["source_line"]), [6])
        self.assertAlmostEqual(float(panel["yield_obs"].iloc[0]), 0.5)
        self.assertEqual(counts["rows_other_states"], 1)
        self.assertEqual(counts["target_state_rows_excluded_season"], 1)
        self.assertEqual(counts["target_state_rows_excluded_crop"], 1)
        self.assertEqual(counts["target_state_rows_non_core_crop_season"], 1)

    def test_missing_core_label_is_an_error(self):
        cfg = json.loads(json.dumps(CFG))
        cfg["scope"]["core_crop_seasons"] = [{"id": "x", "season": "Kharif", "crop": "rice", "unit": "t/ha",
                                              "unit_note": ""}]
        with self.assertRaises(tb.IntegrityError):
            tb.classify_rows(self._df(), cfg)

    def test_duplicate_keys_are_detected(self):
        df = self._df()
        dup = pd.concat([df, df.iloc[[4]]], ignore_index=True)
        self.assertEqual(len(tb.find_duplicate_keys(dup, CFG["dataset"]["key_columns"])), 2)
        self.assertEqual(len(tb.find_duplicate_keys(df, CFG["dataset"]["key_columns"])), 0)

    def test_coverage_rule_failure_is_reported(self):
        cfg = _synthetic_cfg()
        panel = _synthetic_panel()
        panel = panel[~((panel["District_Name"] == "B") & (panel["Crop_Year"] < 2005))]
        failed = [r for r in tb.check_coverage(panel, cfg, "fixed_origin") if not r["passed"]]
        self.assertTrue(any(r["check"] == "min_train_years_per_district" for r in failed))
        self.assertTrue(any(r["check"] == "min_districts_per_test_year" for r in failed))
        self.assertTrue(any(r["check"] == "min_test_obs_per_evaluation" for r in failed))

    def test_missing_dataset_is_an_integrity_error(self):
        with self.assertRaises(tb.IntegrityError):
            tb.load_dataset(CFG, ROOT / "data" / "raw" / "does_not_exist.csv")

    def test_relative_dataset_path_resolves_against_project_root(self):
        self.assertEqual(tb.resolve_data_path(CFG, CONFIG_PATH),
                         (ROOT / "data" / "raw" / "india_crop_production_district.csv").resolve())


# ========================================================= real-data checks
@unittest.skipUnless(HAVE_DATA, NO_DATA_MSG)
class TestRealDataset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df, cls.digest = tb.load_dataset(CFG, DATA_PATH)
        cls.panel, cls.core, cls.counts = tb.classify_rows(cls.df, CFG)

    def test_schema_rows_and_hash(self):
        self.assertEqual(self.digest, CFG["dataset"]["sha256"])
        self.assertEqual(len(self.df), 246091)
        self.assertEqual(list(self.df.columns[1:]), CFG["dataset"]["expected_columns"])

    def test_no_duplicate_keys(self):
        self.assertEqual(len(tb.find_duplicate_keys(self.df, CFG["dataset"]["key_columns"])), 0)

    def test_telangana_years_and_missing_2012(self):
        tg = self.df[self.df["State_Name"] == "Telangana"]
        self.assertEqual(sorted(tg["Crop_Year"].unique()), [y for y in range(1997, 2015) if y != 2012])
        self.assertEqual(len(tg), 5649)

    def test_panel_districts_and_crop_seasons(self):
        self.assertEqual(sorted(self.panel["District_Name"].unique()), CFG["scope"]["expected_panel_districts"])
        self.assertEqual(self.panel["crop_season_id"].nunique(), 12)
        self.assertNotIn("HYDERABAD", set(self.panel["District_Name"]))
        self.assertFalse(self.panel["Season"].isin(["Whole Year"]).any())
        self.assertFalse(self.panel["Crop"].isin(["Turmeric", "Soyabean"]).any())

    def test_exclusion_counts(self):
        by = self.core["exclusion_reason"].value_counts().to_dict()
        self.assertEqual(by.get("district_excluded", 0), 8)
        self.assertEqual(by.get("production_missing", 0), 2)
        self.assertEqual(by.get("production_zero", 0), 0)
        self.assertEqual(by.get("area_below_minimum", 0), 2)
        self.assertEqual(len(self.panel), 1802)
        self.assertEqual(self.counts["target_state_rows_core_crop_season"], 1814)

    def test_eligible_counts_per_crop_season(self):
        expected = {"kharif_rice": (117, 36), "kharif_maize": (117, 36), "kharif_cotton_lint": (117, 36),
                    "kharif_arhar_tur": (108, 36), "kharif_jowar": (112, 33), "kharif_moong": (116, 36),
                    "kharif_dry_chillies": (107, 36), "rabi_rice": (117, 36), "rabi_maize": (117, 36),
                    "rabi_jowar": (115, 36), "rabi_groundnut": (117, 36), "rabi_gram": (113, 36)}
        for cs, (n_train, n_test) in expected.items():
            sub = self.panel[self.panel["crop_season_id"] == cs]
            self.assertEqual(int((sub["Crop_Year"] <= 2009).sum()), n_train, cs)
            self.assertEqual(int(sub["Crop_Year"].isin([2010, 2011, 2013, 2014]).sum()), n_test, cs)

    def test_coverage_rules_pass_both_designs(self):
        for design in ("fixed_origin", "rolling_origin"):
            self.assertTrue(all(r["passed"] for r in tb.check_coverage(self.panel, CFG, design)), design)
        tb.assert_no_gap_observations(self.panel, CFG)


# ============================================================ output checks
def _independent_eligible_rows():
    """Re-derive eligible panel rows from the raw CSV with the csv module (independent of pandas code)."""
    core = {(c["season"], c["crop"]): c["id"] for c in CFG["scope"]["core_crop_seasons"]}
    rows, by_line = [], {}
    with open(DATA_PATH, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader)
        for line_no, rec in enumerate(reader, start=2):
            state, dist, year, season, crop, area, prod = [x.strip() for x in rec]
            by_line[line_no] = (state, dist, int(year), season, crop, area, prod)
            key = (season, crop)
            if state != "Telangana" or key not in core or dist == "HYDERABAD" or prod == "":
                continue
            a, p = float(area), float(prod)
            if p <= 0 or a < 10:
                continue
            rows.append({"cs": core[key], "d": dist, "y": int(year), "v": p / a, "line": line_no})
    return rows, by_line


def _independent_prediction(info, district, target, origin, baseline):
    vals = [r["v"] for r in info]
    b0 = sum(vals) / len(vals)
    dist = [r for r in info if r["d"] == district]
    b1 = sum(r["v"] for r in dist) / len(dist) if len(dist) >= 5 else b0
    if baseline == "B0":
        return b0
    if baseline == "B1":
        return b1
    if baseline == "B2":
        w = [r["v"] for r in dist if origin - 4 <= r["y"] <= origin]
        return sum(w) / len(w) if len(w) >= 3 else b1
    if baseline == "B3":
        lb = sorted((r for r in dist if origin - 2 <= r["y"] <= origin), key=lambda r: r["y"])
        return lb[-1]["v"] if lb else b1
    if baseline == "B4":
        num = den = 0.0
        for d in sorted({r["d"] for r in info}):
            rr = [r for r in info if r["d"] == d]
            ty = sum(r["y"] for r in rr) / len(rr)
            vy = sum(r["v"] for r in rr) / len(rr)
            num += sum((r["y"] - ty) * (r["v"] - vy) for r in rr)
            den += sum((r["y"] - ty) ** 2 for r in rr)
        if den <= 0:
            return b0
        beta = num / den
        if len(dist) >= 5:
            return b1 + beta * (target - sum(r["y"] for r in dist) / len(dist))
        return b0 + beta * (target - sum(r["y"] for r in info) / len(info))
    raise ValueError(baseline)


@unittest.skipUnless(HAVE_RUN and HAVE_DATA, "set TCI_RUN_DIR to a complete local run (dataset required)")
class TestOutputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pred = pd.read_csv(RUN_DIR / "predictions.csv")
        cls.mcs = pd.read_csv(RUN_DIR / "metrics_by_crop_season.csv")
        cls.myr = pd.read_csv(RUN_DIR / "metrics_by_crop_season_year.csv")
        cls.summary = pd.read_csv(RUN_DIR / "baseline_summary.csv")
        cls.cov = pd.read_csv(RUN_DIR / "coverage.csv")

    def test_file_set(self):
        self.assertEqual(sorted(p.name for p in RUN_DIR.iterdir() if p.is_file()), sorted(CFG["output"]["files"]))

    def test_prediction_schema_and_counts(self):
        self.assertEqual(list(self.pred.columns), tb.PREDICTION_COLUMNS)
        self.assertEqual(len(self.pred), 2 * 429 * 5)
        self.assertEqual(set(self.pred["baseline"]), set(tb.BASELINES))
        self.assertFalse(self.pred["prediction"].isna().any())
        self.assertEqual(int(self.pred.groupby(["design", "source_line"]).size().max()), 5)

    def test_forecast_cutoffs(self):
        p = self.pred
        self.assertTrue((p["training_cutoff_year"] < p["target_year"]).all())
        self.assertTrue((p["info_max_year"] <= p["training_cutoff_year"]).all())
        self.assertTrue((p["forecast_origin_year"] < p["target_year"]).all())
        fixed = p[p["design"] == "fixed_origin"]
        self.assertEqual(set(fixed["training_cutoff_year"]), {2009})
        self.assertEqual(set(fixed["forecast_origin_year"]), {2009})
        roll = p[p["design"] == "rolling_origin"]
        table = {(f["target_year"], f["training_cutoff_year"], f["forecast_origin_year"])
                 for f in CFG["designs"]["rolling_origin"]["forecasts"]}
        got = set(map(tuple, roll[["target_year", "training_cutoff_year", "forecast_origin_year"]].drop_duplicates().values))
        self.assertEqual(got, table)
        self.assertEqual({(t, c) for t, c, _ in table}, {(2010, 2009), (2011, 2010), (2013, 2011), (2014, 2013)})
        b3 = p[p["b3_source_year"].notna()]
        self.assertTrue((b3["b3_source_year"] <= b3["forecast_origin_year"]).all())
        b2 = p[p["baseline"] == "B2"]
        self.assertTrue((b2["b2_window_end"] == b2["forecast_origin_year"]).all())

    def test_traceability_to_source_rows(self):
        _, by_line = _independent_eligible_rows()
        for r in self.pred.drop_duplicates("source_line").itertuples(index=False):
            state, dist, year, season, crop, area, prod = by_line[int(r.source_line)]
            self.assertEqual((state, dist, year, season, crop), ("Telangana", r.district, r.target_year, r.season, r.crop))
            self.assertAlmostEqual(float(prod) / float(area), r.observed_yield, delta=TOL)
        for r in self.pred[self.pred["b3_source_line"].notna()].drop_duplicates("b3_source_line").itertuples(index=False):
            src = by_line[int(r.b3_source_line)]
            self.assertEqual((src[1], src[2]), (r.district, int(r.b3_source_year)))

    def test_every_prediction_matches_independent_recomputation(self):
        rows, _ = _independent_eligible_rows()
        cache = {}
        worst = 0.0
        for r in self.pred.itertuples(index=False):
            key = (r.crop_season_id, r.training_cutoff_year)
            if key not in cache:
                cache[key] = [x for x in rows if x["cs"] == r.crop_season_id and x["y"] <= r.training_cutoff_year]
            info = cache[key]
            self.assertTrue(all(x["line"] != r.source_line for x in info))
            expect = _independent_prediction(info, r.district, r.target_year, r.forecast_origin_year, r.baseline)
            worst = max(worst, abs(expect - r.prediction))
            self.assertAlmostEqual(expect, r.prediction, delta=TOL, msg=f"{r}")
        self.assertLess(worst, TOL)

    def test_negative_flags(self):
        self.assertTrue((self.pred["is_negative"] == (self.pred["prediction"] < 0)).all())
        neg = self.pred.groupby(["design", "crop_season_id", "baseline"])["is_negative"].sum()
        m = self.mcs.set_index(["design", "crop_season_id", "baseline"])["n_negative"]
        self.assertTrue((neg.sort_index() == m.sort_index()).all())

    def test_metrics_recomputed_from_predictions(self):
        for (d, cs, b), g in self.pred.groupby(["design", "crop_season_id", "baseline"]):
            row = self.mcs[(self.mcs["design"] == d) & (self.mcs["crop_season_id"] == cs) & (self.mcs["baseline"] == b)]
            self.assertEqual(len(row), 1)
            e = g["prediction"] - g["observed_yield"]
            self.assertAlmostEqual(row["mae"].iloc[0], e.abs().mean(), delta=1e-5)
            self.assertAlmostEqual(row["rmse"].iloc[0], math.sqrt((e ** 2).mean()), delta=1e-5)
            self.assertAlmostEqual(row["bias"].iloc[0], e.mean(), delta=1e-5)
            self.assertAlmostEqual(row["wape"].iloc[0], e.abs().sum() / g["observed_yield"].abs().sum(), delta=1e-5)
            ref = self.pred[(self.pred["design"] == d) & (self.pred["crop_season_id"] == cs) & (self.pred["baseline"] == "B1")]
            mse_ref = ((ref["prediction"] - ref["observed_yield"]) ** 2).mean()
            self.assertAlmostEqual(row["skill_vs_b1"].iloc[0], 1 - (e ** 2).mean() / mse_ref, delta=1e-4)
            self.assertEqual(int(row["n"].iloc[0]), len(g))
            self.assertEqual(int(row["n_fallback"].iloc[0]), int(g["is_fallback"].sum()))
        self.assertEqual(len(self.myr), 2 * 12 * 4 * 5)

    def test_no_pooled_cross_unit_metrics(self):
        forbidden = {"mae", "rmse", "mse", "bias", "r2", "r_squared"}
        self.assertFalse(forbidden & {c.lower() for c in self.summary.columns})
        self.assertEqual(len(self.summary), 2 * 5)
        self.assertTrue((self.summary["n_evaluations"] == 12).all())

    def test_coverage_file_all_passed(self):
        self.assertEqual(len(self.cov), 216)
        self.assertTrue(self.cov["passed"].all())

    def test_manifest_hashes_match_files(self):
        man = json.loads((RUN_DIR / "run_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(man["dataset_sha256"], CFG["dataset"]["sha256"])
        self.assertEqual(man["config_sha256"], _sha(CONFIG_PATH))
        self.assertEqual(man["source_files_sha256"]["tg_baselines.py"], _sha(ROOT / "src" / "tg_baselines.py"))
        for name, digest in man["output_files_sha256"].items():
            self.assertEqual(_sha(RUN_DIR / name), digest, name)

    def test_run_reproduces_published_results(self):
        """Every published result file must be byte-identical to the same file of a fresh local run."""
        for p in sorted(PUBLISHED.iterdir()):
            if p.is_file() and p.name != "README.md":
                self.assertEqual(_sha(RUN_DIR / p.name), _sha(p), p.name)


# =================================================== published results
class TestPublishedResults(unittest.TestCase):
    def setUp(self):
        self.man = json.loads((PUBLISHED / "run_manifest.json").read_text(encoding="utf-8"))

    def test_published_files_match_manifest(self):
        for p in sorted(PUBLISHED.iterdir()):
            if p.is_file() and p.name not in ("README.md", "run_manifest.json"):
                self.assertEqual(self.man["output_files_sha256"].get(p.name), _sha(p), p.name)

    def test_record_level_files_are_withheld(self):
        names = {p.name for p in PUBLISHED.rglob("*") if p.is_file()}
        self.assertFalse(WITHHELD & names, "record-level outputs must not be published")
        self.assertTrue(WITHHELD - {"run_timing.json"} <= set(self.man["output_files_sha256"]))

    def test_manifest_matches_current_code_and_config(self):
        self.assertEqual(self.man["config_sha256"], _sha(CONFIG_PATH))
        for name, digest in self.man["source_files_sha256"].items():
            self.assertEqual(_sha(ROOT / "src" / name), digest, name)

    def test_summary_has_no_pooled_native_unit_metrics(self):
        cols = {c.lower() for c in pd.read_csv(PUBLISHED / "baseline_summary.csv").columns}
        self.assertFalse({"mae", "rmse", "mse", "bias", "r2", "r_squared"} & cols)


# =================================================== repository hygiene
class TestRepositoryHygiene(unittest.TestCase):
    SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "runs"}
    PATTERNS = [
        (re.compile(r"[A-Za-z]:\\Users\\", re.I), "Windows user directory path"),
        (re.compile(r"/(home|Users)/[A-Za-z0-9._-]+/"), "Unix home directory path"),
        (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
        (re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"), "GitHub token"),
        (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
        (re.compile(r"[A-Za-z0-9._%+-]+@(gmail|yahoo|outlook|hotmail)\.com", re.I), "personal e-mail address"),
    ]

    def _files(self):
        for p in ROOT.rglob("*"):
            rel = p.relative_to(ROOT)
            if p.is_file() and not (set(rel.parts) & self.SKIP_DIRS) and rel.parts[:2] != ("data", "raw"):
                yield p, rel

    def test_no_private_paths_or_secrets(self):
        problems = []
        for p, rel in self._files():
            if rel.as_posix() == "tests/test_tg_baselines.py":   # contains the patterns themselves
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            for rx, what in self.PATTERNS:
                if rx.search(text):
                    problems.append(f"{rel.as_posix()}: {what}")
        self.assertEqual(problems, [])

    def test_no_dataset_model_or_environment_files(self):
        bad = [rel.as_posix() for p, rel in self._files()
               if p.suffix.lower() in {".pkl", ".joblib", ".ubj", ".env"} or p.name == "india_crop_production_district.csv"]
        self.assertEqual(bad, [])

    def test_installed_versions_match_lock(self):
        lock = (ROOT / "requirements.lock.txt").read_text(encoding="utf-8")
        pins = dict(re.findall(r"^([A-Za-z0-9_.\-]+)==(\S+)", lock, re.M))
        self.assertEqual(pins.get("numpy"), np.__version__)
        self.assertEqual(pins.get("pandas"), pd.__version__)


if __name__ == "__main__":
    unittest.main()
