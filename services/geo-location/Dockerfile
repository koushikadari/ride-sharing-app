FROM python:3.9-slim

WORKDIR /app

COPY services/geo-location/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/geo-location/ .

COPY shared/ ./shared/

EXPOSE 5007

CMD ["python", "app.py"]
