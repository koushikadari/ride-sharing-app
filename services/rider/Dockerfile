FROM python:3.11-slim

WORKDIR /app

COPY services/rider/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/rider .

COPY shared /app/shared

EXPOSE 5002

CMD ["python", "app.py"]
