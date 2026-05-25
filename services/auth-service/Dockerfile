# ============================================================
# BankFlow — Auth Service
# ============================================================
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl openssl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create entrypoint script that generates RSA keys at runtime
# (so they persist in the Docker volume, not the image layer)
RUN echo '#!/bin/bash\n\
set -e\n\
mkdir -p /app/keys\n\
if [ ! -f /app/keys/private.pem ]; then\n\
    echo "Generating RSA key pair..."\n\
    openssl genrsa -out /app/keys/private.pem 2048\n\
    openssl rsa -in /app/keys/private.pem -pubout -out /app/keys/public.pem\n\
    echo "RSA keys generated."\n\
fi\n\
exec "$@"' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
