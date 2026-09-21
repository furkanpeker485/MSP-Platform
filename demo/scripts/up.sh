#!/usr/bin/env bash
# Emülasyon ortamını ayağa kaldırır.
source "$(dirname "${BASH_SOURCE[0]}")/_ortak.sh"

baslik "Ortam kontrolü"
ortam_kontrol
yesil "Docker: $(docker version --format '{{.Server.Version}} ({{.Server.Os}}/{{.Server.Arch}})')"
yesil "containerlab: $(vm containerlab version 2>/dev/null | grep -o 'version:.*' | head -1)"

baslik "İmajlar derleniyor"
for t in platform agent relay appliance; do
  ctx="$REPO_DIR"; [[ "$t" == "appliance" ]] && ctx="$DEMO_DIR/images/appliance"
  printf '  %-10s ' "$t"
  if docker build -q -t "hisar/$t:demo" -f "$DEMO_DIR/images/$t/Dockerfile" "$ctx" >/dev/null 2>&1; then
    yesil "✓"
  else
    kirmizi "✗ derlenemedi"; exit 1
  fi
done

baslik "Topoloji kuruluyor"
vm_sudo containerlab deploy -t "$LAB" --reconfigure

baslik "Anahtar portları onarılıyor"
# Bir düğüm yeniden yaratıldığında sanal kablo yenilenir ve karşı uçtaki
# anahtar portu köprüden düşer; bu adım üyeliği yeniden uygular.
"$DEMO_DIR/scripts/ag-onar.sh" || true

baslik "Hazır"
"$DEMO_DIR/scripts/harita.sh" || true
