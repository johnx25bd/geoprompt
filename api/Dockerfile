
# Use an official Python runtime as a parent image
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY services/gpt-prompt.md .

RUN pip install --no-cache-dir -r requirements.txt --verbose

COPY . .

EXPOSE 8000

ENV PYTHONDEVMODE=1
ENV UVICORN_LOG_LEVEL=debug
ENV OPENAI_API_KEY=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
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
