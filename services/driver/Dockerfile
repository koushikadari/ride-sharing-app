FROM python:3.9-slim

WORKDIR /app

COPY services/driver/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/driver/ .

COPY shared/ ./shared/

EXPOSE 5003

CMD ["python", "app.py"]
