FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY data ./data

RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/backend/database \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python -m backend.database.init_db --seed && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"]
