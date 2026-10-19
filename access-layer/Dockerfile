FROM python:3.12-slim
WORKDIR /app/access-layer
COPY access-layer/requirements-access-layer.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY access-layer/ /app/access-layer/
COPY ontology/ /app/ontology/
ENV HOST=0.0.0.0 PORT=8000
EXPOSE 8000
CMD ["python", "serve.py"]
