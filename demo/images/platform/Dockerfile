# HR Platformu — kontrol düzlemi.
# Taban imaj önbellekten gelir; Docker Hub anonim çekim sınırına takılmayız.
FROM debian:12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip python3-venv iproute2 iputils-ping curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv PATH=/opt/venv/bin:$PATH
RUN python3 -m venv $VIRTUAL_ENV

COPY platform/ /app/platform/
WORKDIR /app/platform
RUN pip install --no-cache-dir \
      fastapi uvicorn[standard] pydantic pydantic-settings pyyaml httpx structlog \
      "sqlalchemy[asyncio]"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
