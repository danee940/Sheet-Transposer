FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app.py src/transpose.py src/seo.py src/gunicorn.conf.py ./
COPY src/templates ./templates
COPY src/static ./static

RUN useradd --create-home appuser
USER appuser

EXPOSE 8080

CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
