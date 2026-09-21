#!/usr/bin/env python3
"""Demo orkestratörü — n8n'in bu senaryodaki karşılığı.

Gerçek kurulumda `orchestrator/workflows/onboarding.json` akışı n8n içinde koşar.
Demoda aynı sırayı tek dosyada, görülebilir adımlarla yürütürüz:

    1) sözleşme imzalandı        → hak seti belirlenir
    2) erişim listesi üretilir   → platformdan tanım derletilir (kuru çalıştırma)
    3) erişimler kasaya yazılır  → her hizmetin ilk görevi
    4) tanım uygulanır           → görevler şeritlere dağıtılır
    5) sapma uzlaştırması        → aralıklarla tekrarlanır
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

PLATFORM = os.environ.get("HR_PLATFORM_URL", "http://10.10.0.10:8000")
VAULT = os.environ.get("HR_VAULT_URL", "http://10.10.0.15:8200")
TENANT = os.environ.get("HR_TENANT", "acme")
SERVICES = os.environ.get(
    "HR_ENTITLEMENTS",
    "envanter-yonetim-sistemi,switch-management,firewall-management,windows-server-yonetimi",
).split(",")


def http(method: str, url: str, body: dict | None = None, headers: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def adim(no: int, baslik: str) -> None:
    print(f"\n\033[36m── {no}. {baslik}\033[0m", flush=True)


def main() -> int:
    print(f"Orkestratör başlıyor · kiracı={TENANT} · platform={PLATFORM}", flush=True)

    adim(1, "Sözleşme imzalandı — hak seti")
    print(f"   {len(SERVICES)} hizmet: {', '.join(SERVICES)}", flush=True)

    adim(2, "Erişim listesi üretiliyor (kuru çalıştırma)")
    spec = http("POST", f"{PLATFORM}/specs/compile",
                {"tenant": TENANT, "entitlements": SERVICES, "dry_run": True})
    ozet = spec["summary"]
    print(f"   {ozet['services']} hizmet → {ozet['tasks']} görev", flush=True)
    print(f"   şeritlere dağılım: {ozet['by_lane']}", flush=True)

    adim(3, "Erişim bilgileri kasaya yazılıyor")
    kasa_gorevleri = [t for t in spec["spec"]["tasks"] if t["action"] == "vault.store_access"]
    for t in kasa_gorevleri:
        sonuc = http("POST", f"{VAULT}/v1/secret/data/tenants/{TENANT}/{t['service_id']}",
                     {"data": {"store": t["params"].get("store", []), "durum": "alindi"}},
                     {"X-Hisar-Tenant": TENANT})
        print(f"   ✓ {t['service_id']:<32} → {sonuc.get('kasa')}", flush=True)

    adim(4, "Kiracı sınırı sınanıyor (başka kiracının alanı isteniyor)")
    try:
        http("GET", f"{VAULT}/v1/secret/data/tenants/contoso/gizli",
             None, {"X-Hisar-Tenant": TENANT})
        print("   ✗ BEKLENMEYEN: kasa başka kiracının alanını verdi", flush=True)
        return 1
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("   ✓ kasa 403 döndü — kiracı ayrışması çalışıyor", flush=True)
        else:
            print(f"   ? beklenmeyen kod: {e.code}", flush=True)

    adim(5, "Tanım uygulanıyor — görevler şeritlere dağıtılıyor")
    sonuc = http("POST", f"{PLATFORM}/specs/apply",
                 {"tenant": TENANT, "entitlements": SERVICES, "dry_run": True})
    sayim: dict[str, int] = {}
    for r in sonuc["results"]:
        sayim[r["lane"]] = sayim.get(r["lane"], 0) + 1
    print(f"   {len(sonuc['results'])} görev dağıtıldı: {sayim}", flush=True)

    print("\n\033[32mOrkestrasyon tamamlandı.\033[0m", flush=True)
    return 0


if __name__ == "__main__":
    for deneme in range(30):
        try:
            http("GET", f"{PLATFORM}/healthz")
            break
        except Exception:
            time.sleep(2)
    else:
        print("Platform açılmadı, vazgeçildi", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main())
