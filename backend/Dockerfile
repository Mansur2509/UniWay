FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system uniway && adduser --system --ingroup uniway uniway

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R uniway:uniway /app

USER uniway
EXPOSE 8000

# --timeout must stay above AI_ESSAY_REVIEW_MAX_WALL_SECONDS (see
# backend/config/settings.py) plus request parsing/DB overhead, or Gunicorn
# kills a slow-but-legitimate essay-review request before the app can return
# its own structured error response -- see docs/PRODUCTION_DEPLOYMENT_CHECKLIST.md,
# this same value must also be set in the Render dashboard's start command,
# which overrides this CMD in production.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "120", "--graceful-timeout", "30", "--access-logfile", "-", "--error-logfile", "-"]
