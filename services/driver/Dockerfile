FROM python:3.9-slim

WORKDIR /app

COPY rider/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY rider/ .

COPY shared/ ./shared/

EXPOSE 5003

CMD ["python", "app.py"]
