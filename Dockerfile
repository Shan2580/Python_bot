FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Finalhost.py .

CMD ["python", "Finalhost.py"]
