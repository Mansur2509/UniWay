FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system eduverse && adduser --system --ingroup eduverse eduverse

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R eduverse:eduverse /app

USER eduverse
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

