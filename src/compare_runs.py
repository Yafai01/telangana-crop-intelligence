"""Compare two experiment runs file-by-file (by name and SHA-256 of content).

Only files listed in config.output.nondeterministic_files are excluded from the
content comparison, and they are excluded identically for both runs.

    python -I -B src/compare_runs.py --config configs/tg_baselines_v1.json \
        --run-a runs/run_a --run-b runs/run_b --report runs/reproducibility_report

Exit codes: 0 = all substantive files identical, 3 = differences found.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(cfg: dict, run_a: Path, run_b: Path) -> dict:
    expected = sorted(cfg["output"]["files"])
    excluded = sorted(cfg["output"]["nondeterministic_files"])
    names_a = sorted(p.name for p in run_a.iterdir() if p.is_file())
    names_b = sorted(p.name for p in run_b.iterdir() if p.is_file())
    files = []
    for name in expected:
        rec = {"file": name, "in_run_a": name in names_a, "in_run_b": name in names_b}
        if name in excluded:
            rec["status"] = "EXCLUDED_NONDETERMINISTIC"
        elif rec["in_run_a"] and rec["in_run_b"]:
            rec["sha256_a"] = sha256(run_a / name)
            rec["sha256_b"] = sha256(run_b / name)
            rec["bytes"] = (run_a / name).stat().st_size
            rec["status"] = "MATCH" if rec["sha256_a"] == rec["sha256_b"] else "MISMATCH"
        else:
            rec["status"] = "MISSING"
        files.append(rec)
    result = {
        "run_a": str(run_a), "run_b": str(run_b),
        "expected_files": expected, "excluded_nondeterministic_files": excluded,
        "file_set_a_equals_expected": names_a == expected, "file_set_b_equals_expected": names_b == expected,
        "unexpected_in_a": sorted(set(names_a) - set(expected)), "unexpected_in_b": sorted(set(names_b) - set(expected)),
        "files": files,
        "n_compared": sum(f["status"] in ("MATCH", "MISMATCH") for f in files),
        "n_match": sum(f["status"] == "MATCH" for f in files),
        "n_mismatch": sum(f["status"] == "MISMATCH" for f in files),
        "n_missing": sum(f["status"] == "MISSING" for f in files),
    }
    result["reproducible"] = (result["file_set_a_equals_expected"] and result["file_set_b_equals_expected"]
                              and result["n_mismatch"] == 0 and result["n_missing"] == 0
                              and result["n_compared"] == len(expected) - len(excluded))
    return result


def to_markdown(r: dict) -> str:
    lines = ["# Reproducibility comparison", "",
             f"- Run A: `{r['run_a']}`", f"- Run B: `{r['run_b']}`",
             f"- File sets equal expected list: A={r['file_set_a_equals_expected']}, B={r['file_set_b_equals_expected']}",
             f"- Excluded (non-deterministic, identically for both runs): {', '.join(r['excluded_nondeterministic_files'])}",
             f"- Compared: {r['n_compared']}; match: {r['n_match']}; mismatch: {r['n_mismatch']}; missing: {r['n_missing']}",
             f"- **Reproducible: {r['reproducible']}**", "",
             "| File | Status | Bytes | SHA-256 (run A) | SHA-256 (run B) |", "|---|---|---:|---|---|"]
    for f in r["files"]:
        lines.append(f"| {f['file']} | {f['status']} | {f.get('bytes', '')} | `{f.get('sha256_a', '')}` | `{f.get('sha256_b', '')}` |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--run-a", required=True, type=Path)
    ap.add_argument("--run-b", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path, help="report path without extension (.json and .md written)")
    args = ap.parse_args(argv)
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    r = compare(cfg, args.run_a.resolve(), args.run_b.resolve())
    r["run_a"], r["run_b"] = args.run_a.as_posix(), args.run_b.as_posix()  # record paths as given, not absolute
    for suffix in (".json", ".md"):
        if args.report.with_suffix(suffix).exists():
            print(f"refusing to overwrite {args.report.with_suffix(suffix)}", file=sys.stderr)
            return 4
    args.report.with_suffix(".json").write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    args.report.with_suffix(".md").write_text(to_markdown(r), encoding="utf-8", newline="\n")
    for f in r["files"]:
        print(f"{f['status']:<26} {f['file']}")
    print(f"reproducible={r['reproducible']} compared={r['n_compared']} match={r['n_match']} mismatch={r['n_mismatch']}")
    return 0 if r["reproducible"] else 3


if __name__ == "__main__":
    sys.exit(main())
