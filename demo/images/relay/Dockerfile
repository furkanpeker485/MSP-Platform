# Site Relay — müşteri sahasındaki aracı düğüm.
# İş kuyruğu (Redis), relay API, paket önbelleği ve Ansible yürütme ortamı tek düğümde.
FROM alpine:3

RUN apk add --no-cache \
      python3 py3-pip redis openssh-client ansible-core \
      iproute2 iputils curl bash tini

ENV VIRTUAL_ENV=/opt/venv PATH=/opt/venv/bin:$PATH
RUN python3 -m venv $VIRTUAL_ENV \
    && pip install --no-cache-dir fastapi "uvicorn[standard]" redis structlog httpx

COPY relay/relay_api/ /app/relay_api/
COPY relay/ansible/   /app/ansible/
WORKDIR /app/relay_api

EXPOSE 8080 6379
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/bin/sh", "-c", "redis-server --daemonize yes --bind 127.0.0.1 && uvicorn main:app --host 0.0.0.0 --port 8080"]
