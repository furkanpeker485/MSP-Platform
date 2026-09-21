# Agent ÇALIŞTIRAMAYAN cihaz: güvenlik duvarı / erişim anahtarı.
# Üzerine program kurulmaz; yalnız SSH ile dışarıdan yapılandırılır — yani B şeridi.
FROM alpine:3

RUN apk add --no-cache \
      openssh nftables iproute2 iputils tcpdump bash \
      python3 conntrack-tools

RUN ssh-keygen -A \
    && echo 'root:hisar-demo' | chpasswd \
    && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && mkdir -p /run/sshd /etc/hisar

# Bilinçli olarak ajan YOK: bu düğüm yalnız uzaktan yapılandırılabilir.
CMD ["/bin/sh", "-c", "/usr/sbin/sshd -D -e"]
