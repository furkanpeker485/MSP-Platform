#!/usr/bin/env bash
# Ortak yardımcılar. Tüm demo betikleri bunu kaynak alır.
set -euo pipefail

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_DIR="$(cd "$DEMO_DIR/.." && pwd)"
LAB="$DEMO_DIR/topology/hisar-msp.clab.yml"
LAB_NAME="hisar-msp"

mavi()  { printf '\033[36m%s\033[0m\n' "$*"; }
yesil() { printf '\033[32m%s\033[0m\n' "$*"; }
sari()  { printf '\033[33m%s\033[0m\n' "$*"; }
kirmizi(){ printf '\033[31m%s\033[0m\n' "$*"; }
baslik(){ printf '\n\033[1;36m━━ %s\033[0m\n' "$*"; }

# containerlab Linux gerektirir. macOS'ta Colima sanal makinesi içinde koşar.
# Linux'ta doğrudan çalışır; bu sarmalayıcı iki durumu da kapsar.
vm() {
  if [[ "$(uname -s)" == "Darwin" ]]; then
    colima ssh -- "$@"
  else
    "$@"
  fi
}

vm_sudo() {
  if [[ "$(uname -s)" == "Darwin" ]]; then
    colima ssh -- sudo "$@"
  else
    sudo "$@"
  fi
}

# Bir düğümün içinde komut çalıştır
dugum() {
  local ad="$1"; shift
  docker exec "clab-${LAB_NAME}-${ad}" "$@"
}

ortam_kontrol() {
  command -v docker >/dev/null || { kirmizi "docker bulunamadı"; exit 1; }
  if ! docker info >/dev/null 2>&1; then
    sari "Docker motoru kapalı, Colima başlatılıyor…"
    colima start --cpu 4 --memory 8 --disk 40 --vm-type vz
  fi
  if ! vm bash -c 'command -v containerlab' >/dev/null 2>&1; then
    sari "containerlab kurulu değil, kuruluyor…"
    vm bash -c 'curl -sL https://get.containerlab.dev | sudo -E bash'
  fi
}
