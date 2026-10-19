# Contents of this review package

- `README.md`: short project overview and evidence status.
- `START_HERE.md` + `run_local_demo.ps1`: Windows instructions, including the one-file no-Docker demonstration.
- `report/REPORT.md` and `report/SAFE_FOOD_Technical_Report.pdf`: revised technical report; the report explicitly identifies incomplete validation and final-defense obligations.
- `DEFENSE_GUIDE.md`, `TEST_STATUS.md`, `CHANGELOG_REVIEW.md`: defense notes, verification ledger, modifications from the uploaded ZIP.
- `data/`: the original user's real 50-row OFF enriched CSV, copied into the sample used to generate real-data SQL; original source metadata and licences documented. Empty USDA table is intentional.
- `ontology/`, `shapes/`, `mapping/`, `pipeline/`: domain ontology, validation and mapping design/implementation, data pipeline.
- `model/`: train-only preprocessing, brand-disjoint baseline vs graph network, exploratory link ranking, actual 3-seed result CSVs.
- `access-layer/`: schema-aware text-to-SPARQL layer, deterministic no-key demonstration + optional live Gemini, test questions and logs.
- `fuseki/`, `docker-compose.yml`, `.env.example`, `.github/workflows/`: missing-from-upload operational files restored/recreated for reproducible one-command service attempt.
- `tests/`: unit tests, including optional SHACL negative-injection test.

This ZIP does **not** include `.env`, secrets, Git history or an executed Docker image. It does **not** modify your remote GitHub project. You must test the completed stack on your Windows computer and commit changes under your own account.
