#!/usr/bin/env bash
# Ayakta olan düğümleri ağ bacaklarına göre listeler.
source "$(dirname "${BASH_SOURCE[0]}")/_ortak.sh"

printf '\n\033[1m%-18s %-16s %-22s %s\033[0m\n' "DÜĞÜM" "BACAK" "ADRES" "ROL"
printf '%s\n' "────────────────────────────────────────────────────────────────────────────────────────"

satir() { printf '%-18s %-16s %-22s %s\n' "$1" "$2" "$3" "$4"; }
satir "hr-sw"          "hr-core"    "10.10.0.1/24"     "HR çekirdek anahtarı"
satir "hr-platform"    "hr-core"    "10.10.0.10/24"    "2 · HR Platformu"
satir "hr-n8n"         "hr-core"    "10.10.0.11/24"    "1 · Orkestratör"
satir "hr-awx"         "hr-core"    "10.10.0.12/24"    "AWX hop düğümü"
satir "hr-zabbix"      "hr-core"    "10.10.0.13/24"    "İzleme sunucusu"
satir "hr-db"          "hr-core"    "10.10.0.14/24"    "Veritabanı"
satir "hr-vault"       "hr-core"    "10.10.0.15/24"    "Kasa"
satir "hr-edge"        "hr-core→wan" "10.10.0.254 · 100.64.0.1/30" "HR kenar yönlendiricisi"
satir "cust-fw"        "wan→dmz"    "100.64.0.2 · 172.31.0.1/29"  "Güvenlik duvarı (ajan YOK)"
satir "cust-core"      "dmz→VLAN"   "172.31.0.2 · .10.1 .20.1 .30.1" "Müşteri çekirdek anahtarı"
satir "cust-sw-access" "cust-mgmt"  "192.168.10.3/24"  "Erişim anahtarı (ajan YOK)"
satir "relay"          "cust-mgmt"  "192.168.10.10/24" "3 · Site Relay"
satir "relay-receptor" "cust-mgmt"  "192.168.10.11/24" "Yürütme düğümü"
satir "relay-zbxproxy" "cust-mgmt"  "192.168.10.12/24" "İzleme vekili"
satir "relay-cache"    "cust-mgmt"  "192.168.10.13/24" "Paket önbelleği"
satir "srv-01"         "cust-srv"   "192.168.20.21/24" "5 · Ajan çalıştıran sunucu"
satir "srv-02"         "cust-srv"   "192.168.20.22/24" "5 · Ajan çalıştıran sunucu"
satir "pc-01"          "cust-usr"   "192.168.30.31/24" "5 · Ajan çalıştıran uç cihaz"
satir "pc-02"          "cust-usr"   "192.168.30.32/24" "5 · Ajan çalıştıran uç cihaz"
echo
docker ps --filter "name=clab-${LAB_NAME}" --format '  {{.Names}}  {{.Status}}' | sort | head -25
