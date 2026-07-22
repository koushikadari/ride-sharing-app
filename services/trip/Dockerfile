FROM python:3.9-slim

WORKDIR /app

COPY trip/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY trip/ .

COPY shared/ ./shared/

EXPOSE 5005

CMD ["python", "app.py"]
