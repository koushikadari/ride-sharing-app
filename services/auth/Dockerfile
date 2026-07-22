FROM python:3.11-slim

WORKDIR /app

COPY services/auth/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY services/auth/ .

COPY shared/ ./shared/

EXPOSE 5001

CMD ["python", "app.py"]
