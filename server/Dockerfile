FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install torch --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt --no-cache-dir --verbose

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app"]