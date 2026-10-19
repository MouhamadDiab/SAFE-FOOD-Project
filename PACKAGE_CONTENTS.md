# Option A package contents

This is a standalone, ready-to-run project. Both synthetic datasets and raw originals are present. `data/quality/` provides an audit. `RUN_GUIDE_AR.md` contains commands and explanations. The GNN source code is **unchanged**. The old OFF50 report PDF is archived under `report/archive/` and **must not be submitted as the Option A report**. The Option A reports are `report/REPORT.md` and `report/SAFE_FOOD_Option_A_Technical_Report.pdf` (draft; fill team names before submission).

Run `python data/prepare_option_a.py` then `python data/build_example_sql.py` and `python pipeline/run.py --no-load` before model scripts. No Google API key, `.env` or private credentials are included.

Old Windows scripts moved under legacy_scripts_NOT_FOR_OPTION_A/ to prevent accidental 50-row expectations or wrong GitHub remote.
