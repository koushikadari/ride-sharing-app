FROM python:3.9-slim

WORKDIR /app

COPY services/payment/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/payment/ .

COPY shared/ ./shared/

EXPOSE 5006

CMD ["python", "app.py"]
