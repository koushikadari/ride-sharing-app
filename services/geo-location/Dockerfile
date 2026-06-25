FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY ../shared /app/shared

EXPOSE 5007

CMD ["python", "app.py"]
