FROM python:3.11-slim

WORKDIR /app

# on installe les deps en premier pour profiter du cache docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
