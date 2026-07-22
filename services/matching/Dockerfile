FROM python:3.9-slim

WORKDIR /app

COPY services/matching/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/matching/ .

COPY shared/ ./shared/

EXPOSE 5004

CMD ["python", "app.py"]
