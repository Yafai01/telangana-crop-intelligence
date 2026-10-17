# Security and data handling

This project processes a public agricultural statistics file. It has no server, no network calls, no authentication and no user data. The realistic risks are about **data handling and integrity**, not remote exploitation.

## Reporting a problem

Open a GitHub issue for anything non-sensitive. For something you would rather not post publicly — for example a secret or personal path that reached this repository — use GitHub's **private vulnerability reporting** on the Security tab instead of a public issue.

Please include the affected files or commits and, where relevant, the steps to reproduce.

## What this project does and does not do

- **No network access at run time.** The scripts read a local CSV, compute, and write files. Nothing is uploaded, and no telemetry is sent.
- **No code is downloaded or executed from the data.** The CSV is parsed as data.
- **No pickles or model artifacts are loaded.** Everything is CSV, JSON and plain Python, so there is no deserialisation of untrusted objects.
- **Dependencies are hash-locked.** `requirements.lock.txt` pins the full graph with SHA-256 hashes; install with `--require-hashes --only-binary :all:` so no wheel is substituted and nothing is built from source.
- **The dataset is verified before use.** Every entry point checks the file's SHA-256 and refuses to run on a different file, which guards against silent substitution or corruption.
- **The source dataset is never modified.** It is opened read-only, and output goes only to a new directory you name.

## Data handling rules

- The dataset is **not** redistributed here; its licence is unverified (see `data/README.md`). Do not commit it.
- Record-level outputs (`predictions.csv`, `exclusions.csv`, `outlier_flags.csv`) contain values derived from that dataset and are **not** published. `data/raw/` and `runs/` are git-ignored.
- `tests/test_tg_baselines.py::TestRepositoryHygiene` scans the tree on every test run for private key blocks, GitHub and AWS token patterns, personal e-mail addresses, home-directory paths, `.env` files, pickles and the dataset itself. Treat a failure there as a release blocker.

## Supported versions

Only the current `main` branch is maintained. The published results correspond to experiment id `tg_baselines_v1`; its integrity is anchored by the SHA-256 values in `results/tg_baselines_v1/run_manifest.json`.
