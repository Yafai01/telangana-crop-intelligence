"""Render the README figures as static SVG from the published aggregate results.

    python -I -B scripts/make_figures.py [--results results/tg_baselines_v1] [--out docs/figures]

Uses only the standard library and pandas (no plotting dependency). Reads aggregate files only
(baseline_summary.csv, metrics_by_crop_season.csv, data_audit.json); it never reads the dataset.
Native-unit metrics are never drawn on a shared scale across crops: the figures use unit-free
WAPE, skill relative to B1, and observation counts.
"""
from __future__ import annotations

import argparse
import json
import sys
from html import escape
from pathlib import Path

import pandas as pd

# Reference palette (validated): categorical slots 1-2, diverging blue <-> red with a gray midpoint.
SURFACE, BORDER = "#fcfcfb", "#e1e0d9"
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834"]
DIV_NEG, DIV_MID, DIV_POS = "#e34948", "#f0efec", "#2a78d6"
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
BASELINE_NAMES = {"B0": "B0 crop-season mean", "B1": "B1 district mean", "B2": "B2 recent 5-yr mean",
                  "B3": "B3 last observed", "B4": "B4 mean + trend"}
DESIGN_NAMES = {"fixed_origin": "Fixed origin (primary)", "rolling_origin": "Rolling origin (secondary)"}


def _hex(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def _mix(a, b, t):
    ra, rb = _hex(a), _hex(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ra, rb))


def diverging(v, limit=1.0):
    t = max(-1.0, min(1.0, v / limit))
    return _mix(DIV_MID, DIV_POS, t) if t >= 0 else _mix(DIV_MID, DIV_NEG, -t)


def bar_path(x0, y, length, h, r=4):
    """Horizontal bar anchored at x0 (square) with a rounded data end."""
    if length <= 0:
        return ""
    r = min(r, length, h / 2)
    x1 = x0 + length
    return (f"M{x0:.1f},{y:.1f} H{x1 - r:.1f} Q{x1:.1f},{y:.1f} {x1:.1f},{y + r:.1f} "
            f"V{y + h - r:.1f} Q{x1:.1f},{y + h:.1f} {x1 - r:.1f},{y + h:.1f} H{x0:.1f} Z")


class Svg:
    def __init__(self, w, h, title, desc):
        self.w, self.h = w, h
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
                      f'role="img" aria-labelledby="t d" font-family="{FONT}">',
                      f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>',
                      f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="8" fill="{SURFACE}" stroke="{BORDER}"/>']

    def text(self, x, y, s, size=12, fill=INK2, anchor="start", weight="400"):
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
                          f'font-weight="{weight}">{escape(s)}</text>')

    def add(self, s):
        self.parts.append(s)

    def save(self, path: Path):
        path.write_text("\n".join(self.parts + ["</svg>"]) + "\n", encoding="utf-8", newline="\n")


def header(svg, title, subtitle, legend=None, x=24):
    svg.text(x, 32, title, size=15, fill=INK, weight="600")
    svg.text(x, 52, subtitle, size=12, fill=INK2)
    if legend:
        lx = x
        for label, color in legend:
            svg.add(f'<rect x="{lx}" y="64" width="12" height="12" rx="3" fill="{color}"/>')
            svg.text(lx + 18, 74.5, label, size=12, fill=INK2)
            lx += 24 + 7 * len(label)


def _median_wape(summary: pd.DataFrame, design: str, baseline: str) -> float:
    sel = summary[(summary["design"] == design) & (summary["baseline"] == baseline)]["median_wape"]
    if len(sel) != 1:
        raise ValueError(f"expected one row for {design}/{baseline}")
    return float(sel.iloc[0])


def fig_median_wape(summary: pd.DataFrame, path: Path):
    rows = list(BASELINE_NAMES)
    designs = ["fixed_origin", "rolling_origin"]
    left, top, plot_w, bar_h, gap, group_gap = 170, 100, 400, 12, 2, 18
    h = top + len(rows) * (2 * bar_h + gap + group_gap) + 56
    w = left + plot_w + 90
    xmax = 0.35
    desc = "; ".join(f"{b}: " + ", ".join(f"{DESIGN_NAMES[d]} {_median_wape(summary, d, b):.1%}" for d in designs)
                     for b in rows)
    svg = Svg(w, h, "Median WAPE by baseline", "Median across 12 crop-seasons. " + desc)
    header(svg, "Median WAPE across 12 crop-seasons (lower is better)",
           "Weighted absolute percentage error per crop-season, then the median; unit-free.",
           [(DESIGN_NAMES[d], SERIES[i]) for i, d in enumerate(designs)])
    for k in range(0, 36, 5):
        x = left + plot_w * (k / 100) / xmax
        svg.add(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{h - 42}" stroke="{GRID}" stroke-width="1"/>')
        svg.text(x, h - 22, f"{k}%", size=11, fill=MUTED, anchor="middle")
    y = top
    for b in rows:
        svg.text(left - 10, y + bar_h + 5, BASELINE_NAMES[b], size=12, fill=INK2, anchor="end")
        for i, d in enumerate(designs):
            v = _median_wape(summary, d, b)
            length = plot_w * v / xmax
            svg.add(f'<path d="{bar_path(left, y, length, bar_h)}" fill="{SERIES[i]}">'
                    f'<title>{escape(BASELINE_NAMES[b])} - {DESIGN_NAMES[d]}: {v:.1%}</title></path>')
            svg.text(left + length + 6, y + bar_h - 1.5, f"{v:.1%}", size=11, fill=INK2)
            y += bar_h + gap
        y += group_gap
    svg.add(f'<line x1="{left}" y1="{top - 8}" x2="{left}" y2="{h - 42}" stroke="{AXIS}" stroke-width="1"/>')
    svg.save(path)


def fig_skill_heatmap(metrics: pd.DataFrame, cfg: dict, design: str, path: Path):
    order = [(c["id"], f"{c['season']} · {c['crop']}") for c in cfg["scope"]["core_crop_seasons"]]
    cols = ["B0", "B2", "B3", "B4"]
    left, top, cw, ch = 210, 112, 92, 26
    w, h = left + cw * len(cols) + 30, top + ch * len(order) + 92
    s = metrics[metrics["design"] == design]
    val = {(r.crop_season_id, r.baseline): r.skill_vs_b1 for r in s.itertuples()}
    desc = "; ".join(f"{lab}: " + ", ".join(f"{b} {val[(cs, b)]:+.2f}" for b in cols) for cs, lab in order)
    svg = Svg(w, h, f"Skill relative to B1 - {DESIGN_NAMES[design]}", desc)
    header(svg, f"Skill relative to B1 — {DESIGN_NAMES[design].lower()}",
           "1 − MSE / MSE(B1) per crop-season. Positive (blue) = better than B1.")
    for j, b in enumerate(cols):
        svg.text(left + j * cw + cw / 2, top - 10, b, size=12, fill=INK2, anchor="middle", weight="600")
    for i, (cs, lab) in enumerate(order):
        y = top + i * ch
        svg.text(left - 10, y + ch / 2 + 4, lab, size=12, fill=INK2, anchor="end")
        for j, b in enumerate(cols):
            v = float(val[(cs, b)])
            x = left + j * cw
            svg.add(f'<rect x="{x + 1}" y="{y + 1}" width="{cw - 2}" height="{ch - 2}" rx="3" fill="{diverging(v)}">'
                    f'<title>{escape(lab)} - {b}: skill {v:+.3f}</title></rect>')
            svg.text(x + cw / 2, y + ch / 2 + 4, f"{v:+.2f}", size=11, fill=INK, anchor="middle")
    gy, gx, gw = top + ch * len(order) + 26, left, cw * len(cols)
    svg.add('<defs><linearGradient id="div" x1="0" x2="1" y1="0" y2="0">'
            f'<stop offset="0" stop-color="{DIV_NEG}"/><stop offset="0.5" stop-color="{DIV_MID}"/>'
            f'<stop offset="1" stop-color="{DIV_POS}"/></linearGradient></defs>')
    svg.add(f'<rect x="{gx}" y="{gy}" width="{gw}" height="10" rx="3" fill="url(#div)"/>')
    svg.text(gx, gy + 26, "−1 or worse", size=11, fill=MUTED)
    svg.text(gx + gw / 2, gy + 26, "0 = same as B1", size=11, fill=MUTED, anchor="middle")
    svg.text(gx + gw, gy + 26, "+1", size=11, fill=MUTED, anchor="end")
    svg.text(24, gy + 48, "Colour is clipped at ±1; the printed value is exact. B1 (skill 0) is the reference.",
             size=11, fill=MUTED)
    svg.save(path)


def fig_coverage(audit: dict, cfg: dict, path: Path):
    labels = {c["id"]: f"{c['season']} · {c['crop']}" for c in cfg["scope"]["core_crop_seasons"]}
    rows = audit["eligible_by_crop_season"]
    series = [("train_rows_le_2009", "Training rows, fixed origin (1997–2009)"), ("test_rows", "Test rows (2010, 2011, 2013, 2014)")]
    left, top, plot_w, bar_h, gap, group_gap = 210, 100, 360, 9, 2, 10
    h = top + len(rows) * (2 * bar_h + gap + group_gap) + 56
    w = left + plot_w + 70
    xmax = 120
    desc = "; ".join(f"{labels[r['crop_season_id']]}: {r['train_rows_le_2009']} training, {r['test_rows']} test"
                     for r in rows)
    svg = Svg(w, h, "Eligible observations per crop-season", desc)
    header(svg, "Eligible district-year observations per crop-season",
           "After exclusions; 9 districts. The same test rows are used by both evaluation designs.",
           [(lab, SERIES[i]) for i, (_, lab) in enumerate(series)])
    for k in range(0, 121, 20):
        x = left + plot_w * k / xmax
        svg.add(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{h - 42}" stroke="{GRID}" stroke-width="1"/>')
        svg.text(x, h - 22, str(k), size=11, fill=MUTED, anchor="middle")
    y = top
    for r in rows:
        svg.text(left - 10, y + bar_h + 5, labels[r["crop_season_id"]], size=12, fill=INK2, anchor="end")
        for i, (key, lab) in enumerate(series):
            v = int(r[key])
            length = plot_w * v / xmax
            svg.add(f'<path d="{bar_path(left, y, length, bar_h, r=3)}" fill="{SERIES[i]}">'
                    f'<title>{escape(labels[r["crop_season_id"]])} - {escape(lab)}: {v}</title></path>')
            svg.text(left + length + 5, y + bar_h - 0.5, str(v), size=10.5, fill=INK2)
            y += bar_h + gap
        y += group_gap
    svg.add(f'<line x1="{left}" y1="{top - 8}" x2="{left}" y2="{h - 42}" stroke="{AXIS}" stroke-width="1"/>')
    svg.save(path)


def main(argv=None) -> int:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path, default=root / "configs" / "tg_baselines_v1.json")
    ap.add_argument("--results", type=Path, default=root / "results" / "tg_baselines_v1")
    ap.add_argument("--out", type=Path, default=root / "docs" / "figures")
    args = ap.parse_args(argv)
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    summary = pd.read_csv(args.results / "baseline_summary.csv")
    metrics = pd.read_csv(args.results / "metrics_by_crop_season.csv")
    audit = json.loads((args.results / "data_audit.json").read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)
    fig_median_wape(summary, args.out / "median_wape_by_baseline.svg")
    fig_skill_heatmap(metrics, cfg, "fixed_origin", args.out / "skill_vs_b1_fixed_origin.svg")
    fig_skill_heatmap(metrics, cfg, "rolling_origin", args.out / "skill_vs_b1_rolling_origin.svg")
    fig_coverage(audit, cfg, args.out / "coverage_observations.svg")
    for p in sorted(args.out.glob("*.svg")):
        print(f"wrote {p.relative_to(root).as_posix() if p.is_relative_to(root) else p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
