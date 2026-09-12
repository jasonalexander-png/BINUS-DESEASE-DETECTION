# Dockerfile untuk deploy backend BINUS Disease Detection ke Hugging Face Spaces.
# Hugging Face Spaces (SDK: Docker) otomatis membangun image ini dan menjalankan
# container-nya, mengekspos port 7860 ke publik lewat URL *.hf.space.

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY outputs/ ./outputs/

WORKDIR /app/src

EXPOSE 7860

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
