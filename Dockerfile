FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# `manage.py` (migrate, test, verificar_vencimentos, etc.) fica disponível na imagem e no volume em dev.
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
