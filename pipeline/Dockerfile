# SAFE-FOOD pipeline + persistent ML dependencies
FROM python:3.12-slim

WORKDIR /work

COPY pipeline/requirements-pipeline.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

# ML and testing dependencies
RUN pip install --no-cache-dir numpy scikit-learn pytest \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

CMD ["python", "pipeline/run.py"]