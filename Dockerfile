FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MONGO_HOST=MONGO_HOST
ENV MONGO_PORT=MONGO_PORT
ENV MONGO_DB=MONGO_DB
ENV TELEGRAM_BOT_TOKEN=$ELEGRAM_BOT_TOKEN

CMD ["python", "main.py"]
