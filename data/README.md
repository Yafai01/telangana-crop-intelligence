# Data

This repository does **not** include the source dataset. Its redistribution rights have not been verified, so it must be obtained separately.

## Required file

| Property | Expected value |
|---|---|
| File name | `india_crop_production_district.csv` |
| Default location | `data/raw/india_crop_production_district.csv` (relative to the project root) |
| SHA-256 | `af4d84ed95ca0cf4ae823a332189ae79fd773531e1effc44163fe2e6b4ddbedd` |
| Size | 13,878,894 bytes |
| Rows | 246,091 data rows (plus header) |
| Columns | `State_Name, District_Name, Crop_Year, Season, Crop, Area, Production` |

The experiment refuses to run on any file whose SHA-256 differs. Copies of "the same" dataset from different sources or dates can differ in content, encoding or line endings. Only the exact file above reproduces the published results.

## Provenance (as far as it is known)

- The file used for this experiment was taken from the public GitHub repository [`AmiNilay/Crop-Yield-Prediction-System`](https://github.com/AmiNilay/Crop-Yield-Prediction-System), path `data/raw/india_crop_production_district.csv`, at commit `9895341`. That repository has **no licence file**.
- That repository's README attributes its *"district-level crop production (50K rows)"* data to the Kaggle dataset *Crop Production in India* (user `abhinand05`) and labels it "CC0". It does not separately document the 246,091-row file used here, and the CC0 label has not been checked against the Kaggle page. The statistics appear to originate from Government of India agricultural publications.
- **Neither the exact provenance of this file nor its licence has been verified.** Do not assume that public availability grants reuse rights.

## How to obtain it

1. Obtain the file from a source whose terms permit your intended use. Check those terms yourself.
2. Place it at `data/raw/india_crop_production_district.csv`, or keep it anywhere else and pass `--data PATH` to the scripts (or set `TCI_DATA` for the tests).
3. Verify it:

   ```bash
   python -I -B scripts/verify_dataset.py                    # default location
   python -I -B scripts/verify_dataset.py --data path/to/file.csv
   ```

   Expected output ends with `VERIFIED` and reports Telangana rows `5649`, years `1997-2014`, absent `[2012]`.

`data/raw/` is ignored by git. Never commit the dataset or any record-level output derived from it.

## Known characteristics (verified on the expected file)

- No unit column. Production units are inferred: tonnes for most crops, bales for `Cotton(lint)`, nuts for coconut.
- Labels carry padding whitespace (e.g. `'Telangana '`, `'Kharif     '`). The code strips it in memory only.
- Telangana records cover the 10 pre-2016 districts, 1997–2014, with **2012 missing**. Hyderabad has records only for 1997–2000.
- There are no duplicate (state, district, year, season, crop) keys.
