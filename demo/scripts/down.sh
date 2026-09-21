#!/usr/bin/env bash
# Emülasyon ortamını kaldırır.
source "$(dirname "${BASH_SOURCE[0]}")/_ortak.sh"
baslik "Topoloji kaldırılıyor"
vm_sudo containerlab destroy -t "$LAB" --cleanup || true
yesil "Kaldırıldı. Colima'yı da durdurmak için: colima stop"
