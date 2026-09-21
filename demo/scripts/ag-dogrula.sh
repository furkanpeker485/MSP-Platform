#!/usr/bin/env bash
# Altı ağ bacağının gerçekten ayrı ve doğru çalıştığını KANITLAR.
# Her kontrol ya geçer ya düşer; çıktı belgeye aynen alınabilir.
source "$(dirname "${BASH_SOURCE[0]}")/_ortak.sh"

GECEN=0; DUSEN=0
gecti() { yesil "   ✓ $*"; GECEN=$((GECEN+1)); }
dustu() { kirmizi "   ✗ $*"; DUSEN=$((DUSEN+1)); }

# beklenen_basari <açıklama> <düğüm> <komut...>
beklenen_basari() {
  local aciklama="$1" dgm="$2"; shift 2
  if dugum "$dgm" "$@" >/dev/null 2>&1; then gecti "$aciklama"; else dustu "$aciklama"; fi
}
# beklenen_basarisizlik: güvenlik kuralının gerçekten engellediğini kanıtlar
beklenen_basarisizlik() {
  local aciklama="$1" dgm="$2"; shift 2
  if dugum "$dgm" "$@" >/dev/null 2>&1; then dustu "$aciklama (ENGELLENMEDİ)"; else gecti "$aciklama"; fi
}

baslik "BACAK 1 — HR kontrol düzlemi (10.10.0.0/24)"
beklenen_basari "hr-platform → hr-sw ağ geçidi"      hr-platform ping -c2 -W2 10.10.0.1
beklenen_basari "hr-platform → hr-vault (kasa)"      hr-platform ping -c2 -W2 10.10.0.15
beklenen_basari "hr-platform → hr-awx (hop düğümü)"  hr-platform ping -c2 -W2 10.10.0.12
beklenen_basari "hr-n8n → hr-platform"               hr-n8n      ping -c2 -W2 10.10.0.10

baslik "BACAK 2 — WAN geçişi (100.64.0.0/30)"
beklenen_basari "hr-edge → cust-fw (WAN karşı ucu)"  hr-edge  ping -c2 -W2 100.64.0.2
beklenen_basari "cust-fw → hr-edge"                  cust-fw  ping -c2 -W2 100.64.0.1
mavi "   WAN bacağındaki adresler:"
dugum hr-edge ip -br addr show eth2 2>/dev/null | sed 's/^/     hr-edge  /'
dugum cust-fw ip -br addr show eth1 2>/dev/null | sed 's/^/     cust-fw  /'

baslik "BACAK 3 — müşteri DMZ (172.31.0.0/29)"
beklenen_basari "cust-fw → cust-core"                cust-fw   ping -c2 -W2 172.31.0.2
beklenen_basari "cust-core → cust-fw"                cust-core ping -c2 -W2 172.31.0.1

baslik "BACAK 4 — yönetim VLAN'ı (192.168.10.0/24)"
beklenen_basari "relay → ağ geçidi"                  relay ping -c2 -W2 192.168.10.1
beklenen_basari "relay → erişim anahtarı"            relay ping -c2 -W2 192.168.10.3
beklenen_basari "relay → izleme vekili"              relay ping -c2 -W2 192.168.10.12
beklenen_basari "relay → paket önbelleği"            relay ping -c2 -W2 192.168.10.13

baslik "BACAK 5 — sunucu VLAN'ı (192.168.20.0/24)"
beklenen_basari "srv-01 → ağ geçidi"                 srv-01 ping -c2 -W2 192.168.20.1
beklenen_basari "srv-01 → srv-02 (aynı yayın alanı)" srv-01 ping -c2 -W2 192.168.20.22
beklenen_basari "srv-01 → relay (VLAN'lar arası)"    srv-01 ping -c2 -W2 192.168.10.10

baslik "BACAK 6 — kullanıcı VLAN'ı (192.168.30.0/24)"
beklenen_basari "pc-01 → ağ geçidi"                  pc-01 ping -c2 -W2 192.168.30.1
beklenen_basari "pc-01 → pc-02 (aynı yayın alanı)"   pc-01 ping -c2 -W2 192.168.30.32
beklenen_basari "pc-01 → relay (VLAN'lar arası)"     pc-01 ping -c2 -W2 192.168.10.10

baslik "YAYIN ALANI AYRIMI — VLAN'lar gerçekten ayrı mı"
mavi "   Aynı VLAN doğrudan, farklı VLAN ağ geçidi üzerinden gider. TTL bunu kanıtlar."

yol_ayni=$(dugum pc-01 ip route get 192.168.30.32 2>/dev/null | head -1)
yol_farkli=$(dugum pc-01 ip route get 192.168.20.21 2>/dev/null | head -1)
if [[ "$yol_farkli" == *"via 192.168.30.1"* && "$yol_ayni" != *"via"* ]]; then
  gecti "pc-01 → pc-02 doğrudan, pc-01 → srv-01 ağ geçidi üzerinden"
  printf '     aynı VLAN : %s\n' "$yol_ayni"
  printf '     farklı VLAN: %s\n' "$yol_farkli"
else
  dustu "VLAN ayrımı yönlendirme tablosunda görülmedi"
fi

ttl() { dugum "$1" ping -c1 -W2 "$2" 2>/dev/null | grep -o 'ttl=[0-9]*' | head -1 | cut -d= -f2; }
t_ayni=$(ttl pc-01 192.168.30.32); t_farkli=$(ttl pc-01 192.168.20.21); t_wan=$(ttl relay 10.10.0.10)
mavi "   TTL: aynı VLAN=${t_ayni:-?}  farklı VLAN=${t_farkli:-?}  WAN ötesi=${t_wan:-?}"
if [[ -n "$t_ayni" && -n "$t_farkli" && "$t_farkli" -lt "$t_ayni" ]]; then
  gecti "farklı VLAN'a giden paket yönlendiriciden geçiyor (TTL düştü)"
else
  dustu "TTL farkı görülmedi — VLAN'lar aynı yayın alanında olabilir"
fi
if [[ -n "$t_wan" && -n "$t_farkli" && "$t_wan" -lt "$t_farkli" ]]; then
  gecti "WAN ötesine giden paket birden çok yönlendiriciden geçiyor"
else
  dustu "WAN geçişinde beklenen TTL düşüşü yok"
fi

mavi "   Çekirdek anahtardaki VLAN köprüleri:"
dugum cust-core ip -br addr show 2>/dev/null | grep -E '^br-' | sed 's/^/     /'

baslik "YÖN KURALI — dışarıdan içeri kapalı"
mavi "   Tasarımın özü: müşteri ağına giden her bağlantı içeriden başlatılır."
beklenen_basari        "içeriden dışarı: relay → HR platformu (izinli)" \
                       relay curl -s -m 5 -o /dev/null http://10.10.0.10:8000/healthz
beklenen_basarisizlik  "dışarıdan içeri: HR platformu → relay API'si (engellenmeli)" \
                       hr-platform curl -s -m 4 -o /dev/null http://192.168.10.10:8080/healthz
beklenen_basarisizlik  "dışarıdan içeri: HR platformu → sunucu VLAN'ı (engellenmeli)" \
                       hr-platform ping -c1 -W2 192.168.20.21

baslik "GÜVENLİK DUVARI KURAL SAYAÇLARI"
dugum cust-fw nft list ruleset 2>/dev/null | grep -E 'chain (input|forward)|policy|comment' | head -12 | sed 's/^/   /'

baslik "AJAN ÇALIŞTIRAMAYAN DÜĞÜMLER"
for d in cust-fw cust-sw-access; do
  if dugum "$d" test -d /app/agent 2>/dev/null; then
    dustu "$d üzerinde ajan bulundu — olmamalı"
  else
    gecti "$d üzerinde ajan yok (yalnız uzaktan yapılandırılır — B şeridi)"
  fi
done
for d in srv-01 pc-01; do
  if dugum "$d" test -d /app/agent 2>/dev/null; then
    gecti "$d üzerinde ajan var (A şeridi)"
  else
    dustu "$d üzerinde ajan yok — olmalıydı"
  fi
done

baslik "SONUÇ"
printf '   geçen: \033[32m%d\033[0m   düşen: \033[31m%d\033[0m\n' "$GECEN" "$DUSEN"
[[ "$DUSEN" -eq 0 ]] && { yesil "   Altı bacak da doğrulandı."; exit 0; } || { kirmizi "   Doğrulama düştü."; exit 1; }
