FROM python:3.11-slim

WORKDIR /app

COPY api-gateway/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY api-gateway/ .

COPY services/shared/ ./shared/

EXPOSE 8000

CMD ["python", "app.py"]
