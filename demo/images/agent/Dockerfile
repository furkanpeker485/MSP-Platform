# Uç nokta ajanı — Linux sunucu ve kullanıcı bilgisayarlarını temsil eder.
FROM debian:12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip python3-venv openssh-server sudo \
      iproute2 iputils-ping curl ca-certificates procps \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv PATH=/opt/venv/bin:$PATH
RUN python3 -m venv $VIRTUAL_ENV && pip install --no-cache-dir httpx structlog

COPY agent/ /app/agent/
WORKDIR /app/agent
RUN pip install --no-cache-dir -e . || true

# Ansible'ın B şeridinde bu makineye de ulaşabilmesi için SSH
RUN mkdir -p /run/sshd /etc/hragent \
    && ssh-keygen -A \
    && echo 'root:hisar-demo' | chpasswd \
    && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config

CMD ["/bin/sh", "-c", "/usr/sbin/sshd && sleep infinity"]
