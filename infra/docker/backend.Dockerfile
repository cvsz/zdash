FROM python:3.11.16-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app/backend

COPY backend/requirements.lock ./requirements.lock
RUN python -m pip install --upgrade pip 'setuptools>=83' wheel \
    && pip install -r requirements.lock

COPY backend/ /app/backend/
RUN chown -R app:app /app

USER app

EXPOSE 8005

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8005/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
