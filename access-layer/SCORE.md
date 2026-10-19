# Access-layer evaluation log

- **2026-10-19, local run, `LLM_MODE=offline` (DETERMINISTIC, NOT Gemini):** 5 of 5 answerable test queries matched the corresponding gold result sets (mean F1 = 1.000 in schema/examples/repair modes); 1 of 1 medical-dose question refused. This score is tautological because queries are fixed templates; it **does not measure model generalization**.
- **Legacy 2026-10-18 Gemini run in the original teaching/synthetic version:** F1 0.688 on five answerable questions, refusal 1/1. This is **not transferable to the new 50-product real-data graph**. See the original report if you need the historical context.
- **Required before actual defense for the LLM points:** run `LLM_MODE=live python access-layer/evaluate.py --setting repair`, log exact Gemini model and UTC/local date, record query failures/refusals and save the command output. No live Gemini run was performed in this environment.
