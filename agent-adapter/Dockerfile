FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY agent-adapter/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY agent-adapter/app ./app

EXPOSE 8081
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
