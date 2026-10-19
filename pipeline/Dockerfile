# One-shot graph build + SHACL validation + VoID + Fuseki load
FROM python:3.12-slim
WORKDIR /work
COPY pipeline/requirements-pipeline.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
CMD ["python", "pipeline/run.py"]
