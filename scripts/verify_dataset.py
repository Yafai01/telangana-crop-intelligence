"""Verify that a local copy of the source dataset is exactly the file this experiment expects.

    python -I -B scripts/verify_dataset.py                      # uses dataset.path from the config
    python -I -B scripts/verify_dataset.py --data D:/data/x.csv  # any other location

Checks the SHA-256, column names and row count, and reports the Telangana years present.
Read-only: the dataset is never modified. Exit code 0 = verified, 2 = mismatch or missing file.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import tg_baselines as tb  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    root = Path(__file__).resolve().parents[1]
    ap.add_argument("--config", type=Path, default=root / "configs" / "tg_baselines_v1.json")
    ap.add_argument("--data", type=Path, default=None, help="dataset CSV; overrides dataset.path in the config")
    args = ap.parse_args(argv)
    cfg = tb.load_config(args.config)
    path = tb.resolve_data_path(cfg, args.config, args.data)
    print(f"dataset file : {path}")
    print(f"expected     : sha256 {cfg['dataset']['sha256']}, {cfg['dataset']['expected_rows']} rows")
    try:
        df, digest = tb.load_dataset(cfg, path)
    except tb.IntegrityError as exc:
        print(f"NOT VERIFIED : {exc}", file=sys.stderr)
        return 2
    tg = df[df["State_Name"] == cfg["scope"]["state"]]
    years = sorted(int(y) for y in tg["Crop_Year"].unique())
    print(f"sha256       : {digest}  (match)")
    print(f"rows/columns : {len(df)} rows; {', '.join(cfg['dataset']['expected_columns'])}")
    print(f"{cfg['scope']['state']} rows : {len(tg)}; years {years[0]}-{years[-1]}, "
          f"absent: {[y for y in range(years[0], years[-1] + 1) if y not in years]}")
    print("VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
