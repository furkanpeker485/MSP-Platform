#!/usr/bin/env bash
# Anahtar portlarının köprü üyeliğini yeniden uygular.
#
# Neden gerekli: containerlab bir düğümü yeniden yarattığında sanal kablo çifti de
# yenilenir ve karşı uçtaki anahtar portu köprüden düşer. Bu betik tekrar tekrar
# çalıştırılabilir; zaten doğru olan üyeliğe dokunmaz.
source "$(dirname "${BASH_SOURCE[0]}")/_ortak.sh"

onar() {
  local anahtar="$1" kopru="$2"; shift 2
  local degisen=0
  for p in "$@"; do
    mevcut=$(dugum "$anahtar" ip -d link show "$p" 2>/dev/null | grep -o 'master [a-z0-9-]*' | awk '{print $2}')
    if [[ "$mevcut" != "$kopru" ]]; then
      dugum "$anahtar" ip link set "$p" master "$kopru" 2>/dev/null || continue
      dugum "$anahtar" ip link set "$p" up 2>/dev/null || true
      printf '   %-16s %-8s → %s (onarıldı)\n' "$anahtar" "$p" "$kopru"
      degisen=$((degisen+1))
    fi
  done
  [[ "$degisen" -eq 0 ]] && printf '   %-16s %-8s zaten doğru\n' "$anahtar" "$kopru"
  return 0
}

baslik "Anahtar portları denetleniyor"
onar hr-sw          br-core  eth1 eth2 eth3 eth4 eth5 eth6 eth7
onar cust-sw-access br0      eth1 eth2 eth3 eth4 eth5
onar cust-core      br-mgmt  eth2
onar cust-core      br-srv   eth3 eth4
onar cust-core      br-usr   eth5 eth6

baslik "Köprü üyeliği"
for a in hr-sw cust-sw-access cust-core; do
  printf '   %s:\n' "$a"
  dugum "$a" sh -c 'for i in 1 2 3 4 5 6 7; do m=$(ip -d link show eth$i 2>/dev/null | grep -o "master [a-z0-9-]*"); [ -n "$m" ] && echo "     eth$i → ${m#master }"; done' 2>/dev/null
done
yesil "\n   Onarım tamam."
