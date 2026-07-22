FROM python:3.9-slim

WORKDIR /app

COPY geo-location/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY geo-location/ .

COPY shared/ ./shared/

EXPOSE 5004

CMD ["python", "app.py"]
