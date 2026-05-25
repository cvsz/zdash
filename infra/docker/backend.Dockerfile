FROM python:3.11-slim
WORKDIR /app
RUN useradd -m appuser
COPY backend /app/backend
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
USER appuser
WORKDIR /app/backend
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
