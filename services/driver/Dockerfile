FROM python:3.9-slim

WORKDIR /app

COPY driver/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY driver/ .

COPY shared/ ./shared/

EXPOSE 5007

CMD ["python", "app.py"]
