FROM python:3.9-slim

WORKDIR /app

COPY matching/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY matching/ .

COPY shared/ ./shared/

EXPOSE 5004

CMD ["python", "app.py"]
