#!/usr/bin/env bash
# Uçtan uca senaryo: sözleşmeden çalışan hizmete.
# Her adım gerçek kodu gerçek ağ üzerinde çalıştırır — ekran çıktısı belgeye alınır.
source "$(dirname "${BASH_SOURCE[0]}")/_ortak.sh"

baslik "1 · Kontrol düzlemi ayakta mı"
kod=$(dugum hr-platform curl -s -m 5 -o /dev/null -w '%{http_code}' http://10.10.0.10:8000/healthz || echo 000)
[[ "$kod" == "200" ]] && yesil "   HR Platformu yanıt veriyor (HTTP $kod)" || { kirmizi "   Platform yanıt vermiyor"; exit 1; }
adet=$(dugum hr-platform curl -s http://10.10.0.10:8000/catalog | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))' 2>/dev/null || echo "?")
yesil "   Katalogda $adet hizmet yüklü"

baslik "2 · Müşteri sahasından kontrol düzlemine erişim (içeriden dışarı)"
mavi "   Relay, HR'a kendisi bağlanır. Güvenlik duvarında gelen kural yoktur."
kod=$(dugum relay curl -s -m 8 -o /dev/null -w '%{http_code}' http://10.10.0.10:8000/healthz || echo 000)
[[ "$kod" == "200" ]] && yesil "   relay → HR platformu: HTTP $kod (dört bacak üzerinden)" || kirmizi "   relay erişemedi"

baslik "3 · Ters yön kapalı mı"
if dugum hr-platform curl -s -m 4 -o /dev/null http://192.168.10.10:8080/healthz 2>/dev/null; then
  kirmizi "   HR → relay bağlantısı AÇIK — tasarım ihlali"
else
  yesil "   HR → relay bağlantısı engellendi (beklenen)"
fi

baslik "4 · Orkestratör: sözleşme → tanım → kasa → dağıtım"
dugum hr-n8n env HR_PLATFORM_URL=http://10.10.0.10:8000 HR_VAULT_URL=http://10.10.0.15:8200 \
  python3 /app/orchestrator.py 2>&1 | sed 's/^/   /'

baslik "5 · B şeridi: ajan çalıştıramayan cihaza uzaktan yapılandırma"
mavi "   Güvenlik duvarına ajan kurulamaz; kural yalnız SSH ile basılır."
dugum relay sh -c 'command -v ansible >/dev/null && ansible --version | head -1' 2>/dev/null | sed 's/^/   /' || true
onceki=$(dugum cust-fw nft list ruleset 2>/dev/null | grep -c 'accept' || echo 0)
mavi "   basımdan önce kural sayısı: $onceki"
dugum cust-fw nft add rule inet filter forward ip saddr 192.168.20.0/24 ip daddr 10.10.0.13 tcp dport 10051 accept comment \"izleme vekili trafigi\" 2>/dev/null \
  && yesil "   yeni kural basıldı (izleme trafiğine izin)" || sari "   kural basılamadı"
sonraki=$(dugum cust-fw nft list ruleset 2>/dev/null | grep -c 'accept' || echo 0)
mavi "   basımdan sonra kural sayısı: $sonraki"

baslik "6 · A şeridi: ajan çalıştıran düğümler"
for d in srv-01 srv-02 pc-01 pc-02; do
  ip=$(dugum "$d" ip -4 -br addr show eth1 2>/dev/null | awk '{print $3}')
  kod=$(dugum "$d" curl -s -m 5 -o /dev/null -w '%{http_code}' http://192.168.10.10:8080/healthz 2>/dev/null || echo 000)
  if [[ "$kod" == "200" ]]; then
    yesil "   $d ($ip) → relay iş kuyruğu: HTTP $kod"
  else
    sari "   $d ($ip) → relay: HTTP $kod"
  fi
done

baslik "7 · Receptor mesh: yürütme düğümü dışa doğru bağlandı mı"
dugum relay-receptor sh -c 'receptorctl --socket /tmp/receptor.sock status 2>/dev/null | head -12' 2>/dev/null | sed 's/^/   /' \
  || sari "   receptorctl soketi henüz hazır değil"

baslik "8 · İzleme vekili merkeze bağlanıyor mu"
dugum relay-zbxproxy sh -c 'grep -aiE "connect|proxy" /var/lib/zabbix/*.log 2>/dev/null | tail -3' 2>/dev/null | sed 's/^/   /' \
  || mavi "   (vekil günlüğü henüz oluşmadı)"

baslik "Senaryo tamamlandı"
