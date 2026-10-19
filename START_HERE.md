# START HERE - Windows PowerShell (one short smoke test)

**Do not overwrite the original `SAFE-FOOD` clone or the course repo.** Unzip this package into a *new* folder named `SAFE-FOOD-REVIEWED` inside `C:\Users\Moudi\Desktop\M2\KRR`.

### A. No-Docker verification (using the course's already-installed Python environment)

**Simplest option:** Run `powershell -ExecutionPolicy Bypass -File .\run_local_demo.ps1` from the reviewed folder. The script is plain text and runs only the listed project programs locally; inspect it before execution. Or run the commands manually:

```powershell
cd "C:\Users\Moudi\Desktop\M2\KRR\SAFE-FOOD-REVIEWED"
$python = "..\course_knowledge_representation\demos\.venv\Scripts\python.exe"
& $python data/build_example_sql.py
& $python pipeline/run.py --no-load
& $python model/build_graph.py
& $python model/baseline.py
& $python model/gnn.py
& $python model/link_prediction.py
$env:LLM_MODE="offline"
& $python access-layer/ask.py "How many packaged products declare the gluten allergen?"
```

After that, `build/graph.nt` and `build/void.ttl` should exist. Expect 50 products; SHACL conforming and 0 violations on the current real sample (revalidate on your machine). For a deliberately invalid energy row, the gate **must fail** instead of silently removing it. `tests/` has a regression test for this.

### B. Docker services (if Docker Desktop is installed and running)

```powershell
Copy-Item .env.example .env
# Edit .env only if switching from offline demo to live Gemini.
docker compose up --build
```

From another terminal after pipeline says `done`:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/?question=How%20many%20packaged%20products%20declare%20the%20gluten%20allergen%3F&dataset=https%3A%2F%2Ful.edu.lb%2Fkr%2Ffoodsafe%2F"
```

Try also a refusal: `What is the safe medical dose of aspartame for a child eating this yogurt?`. In offline mode it is a scripted safety example, not a measurement of a live AI model.

### C. Submission conditions that remain open

1. Actually verify one-command Docker build + its endpoint on the computer intended for the defense.
2. Validate an *actual Morph-KGC/R2RML* execution against `mapping/mapping.ttl` and compare output with `mapping/materialize.py`, or clearly mark R2RML engine verification incomplete.
3. In live mode run `access-layer/evaluate.py --setting repair` and record date, model, each question and the final F1/refusal metrics.
4. Fill in actual team members, confirm dataset/data licence attribution and commit history/PR rules, then update the report's testing status.

Avoid presenting this review package as a final verified submission until A-C are complete.
