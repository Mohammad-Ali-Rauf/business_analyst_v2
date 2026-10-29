FROM python:3.12-slim

# ffmpeg is required by openai-whisper to decode audio files.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# CPU-only torch keeps the image several GB smaller. The `+cpu` local version
# must be pinned explicitly: a bare `torch` requirement resolves to the CUDA
# build on PyPI (2.15.0+cpu < 2.15.0 per PEP 440).
COPY requirements.txt .
RUN pip install --no-cache-dir torch==2.15.0+cpu --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
