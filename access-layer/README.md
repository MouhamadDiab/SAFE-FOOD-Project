# Natural-language access: two explicitly different modes

- `LLM_MODE=offline`: fixed deterministic demonstration for the six test questions. No Gemini key needed. This **is NOT an LLM score**; it simply proves the query contract, graph execution and schema checks work. Unsupported questions must refuse.
- `LLM_MODE=live`: actual Gemini call with `GOOGLE_API_KEY` in `.env`. Re-evaluate separately and record model, date, questions and scores.

From project root (after `python pipeline/run.py --no-load`):

```
$env:LLM_MODE="offline"
python access-layer/ask.py "How many packaged products declare the gluten allergen?"
python access-layer/ask.py "What is the safe medical dose of aspartame for a child eating this yogurt?"
cd access-layer
python evaluate.py --quiet
```

The `DATASET_ID` for the HTTP TEXT2SPARQL contract is `https://ul.edu.lb/kr/foodsafe/`. The default published service is bound to 127.0.0.1 on the Windows host by Docker Compose. See `START_HERE.md` for service checks.
