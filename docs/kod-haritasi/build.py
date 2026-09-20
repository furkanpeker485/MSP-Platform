#!/usr/bin/env python3
"""Kod haritasını depodaki gerçek dosyalardan yeniden üretir.

Harita, kaynak kodun anlık bir kopyasını içinde taşır. Kod değişince harita eskir;
bu betik onu güncel koda göre yeniden kurar.

    python3 docs/kod-haritasi/build.py        # depo kökünden çalıştırılır

Çıktı: docs/kod-haritasi/{codemap.json, kod-haritasi.html}
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

# (yol, bileşen, şeritler, bir cümlelik rol)
FILES: list[tuple[str, str, list[str], str]] = [
    ("orchestrator/workflows/onboarding.json", "n8n", ["D"],
     "Sözleşme imzalanınca erişim listesini üretir, formu açar, kanarya testini koşar"),
    ("orchestrator/workflows/drift_reconcile.json", "n8n", ["E"],
     "15 dakikada bir sapmaları uzlaştırır; etki sınırı aşılırsa geri alır"),
    ("orchestrator/workflows/scheduled_monthly_report.json", "n8n", ["E"],
     "Ayın 1'i 06:00'da aylık raporu üretir"),
    ("orchestrator/README.md", "n8n", ["E"],
     "Akışların nasıl sürümlendiği ve sırların neden akışta durmadığı"),
    ("platform/app/main.py", "platform", ["D"], "Giriş noktası; katalog tutarsızsa açılışta patlar"),
    ("platform/app/config.py", "platform", ["D"], "Tüm sırlar ortam değişkeninden; kodda sabit değer yok"),
    ("platform/app/models.py", "platform", ["D"],
     "Kiracı, hak seti, cihaz, sürümlü tanım, görev koşusu, denetim kaydı"),
    ("platform/app/catalog/loader.py", "platform", ["D"],
     "Katalog yükleyici; 'ilk görev kasa olmalı' kuralını zorunlu kılar"),
    ("platform/app/services/task_graph.py", "platform", ["D"],
     "Ön koşullara göre sıralama; envanter her şeyden önce gelir"),
    ("platform/app/services/spec_compiler.py", "platform", ["D"],
     "Hak seti + cihaz rolü → arzu edilen durum; çıkarmalı çalışır"),
    ("platform/app/services/dispatcher.py", "platform", ["A", "B", "C", "D", "E", "F"],
     "Her görevi kendi şeridinin yürütücüsüne yollar — altı şeridin buluştuğu yer"),
    ("platform/app/services/agent_queue.py", "platform", ["A"],
     "A şeridi: görev relay kuyruğuna yazılır, ajan çeker"),
    ("platform/app/services/drift.py", "platform", ["A", "B", "C", "D"],
     "Sapma uzlaştırma ve etki sınırı koruması"),
    ("platform/app/security.py", "platform", ["A"], "Ajan kimliği ve kiracı sınırı"),
    ("platform/app/integrations/awx.py", "platform", ["B"],
     "B şeridinin yürütücüsü; relay'i dışa doğru eşleşen yürütme düğümü olarak kaydeder"),
    ("platform/app/integrations/vault.py", "platform", ["D"],
     "Kasa; kiracı ayrışması yol düzeyinde zorunlu"),
    ("platform/app/integrations/netbox.py", "platform", ["C", "D"],
     "Envanter; kimlik anahtarı ajan kimliği + seri no"),
    ("platform/app/integrations/zabbix.py", "platform", ["D"],
     "İzleme; satılan şey host kaydı ve uyarı kuralıdır"),
    ("platform/app/integrations/ticketing.py", "platform", ["F"],
     "F şeridinin arayüzü; kabul kriteri olmadan iş emri kapanmaz"),
    ("platform/app/api/routers/agents.py", "platform", ["A"],
     "Ajan uçları; bağlantıyı her zaman ajan kurar"),
    ("platform/app/api/routers/specs.py", "platform", ["D"],
     "Tanım derleme, kuru çalıştırma ve dağıtım"),
    ("platform/app/catalog/services/switch-management.yaml", "platform", ["B"],
     "Örnek katalog kaydı — 39 hizmetin her biri böyle tanımlı"),
    ("platform/tests/test_catalog.py", "platform", ["D"], "Tasarım kurallarını koda bağlayan testler"),
    ("platform/tests/test_spec_compiler.py", "platform", ["D"],
     "Ön koşul, söküm ve kasa kuralının testleri"),
    ("relay/docker-compose.yml", "relay", ["A", "B", "C"], "Relay yığını; hiçbiri internete açılmaz"),
    ("relay/receptor/receptor.conf", "relay", ["B"],
     "Yürütme düğümü: gelen bağlantı dinlemez, kendisi dışarı bağlanır"),
    ("relay/relay_api/main.py", "relay", ["A"], "Ajanların tek muhatabı"),
    ("relay/relay_api/queue.py", "relay", ["A"], "İş kuyruğu; cihaz kimliğine göre bölümlenir"),
    ("relay/ansible/ansible.cfg", "relay", ["B"], "Parolalar playbook'ta değil kasada"),
    ("relay/ansible/inventory/netbox.yml", "relay", ["B"],
     "Makine listesi elle tutulmaz; envanterden gelir"),
    ("relay/ansible/roles/switch_baseline/tasks/main.yml", "relay", ["B"],
     "Geri sayımlı yeniden başlatma ile korunan switch ayarı"),
    ("relay/ansible/roles/firewall_baseline/tasks/main.yml", "relay", ["B"],
     "HA sanal adresine değil birincil düğüme basar"),
    ("relay/ansible/playbooks/site.yml", "relay", ["B"],
     "Hangi rolün koşacağını envanterdeki cihaz rolü belirler"),
    ("relay/ansible/playbooks/teardown.yml", "relay", ["B", "D"],
     "Çıkış hattı: giriş hattının aynadaki hâli"),
    ("relay/ansible/group_vars/all/vault.yml", "relay", ["B"],
     "ansible-vault ile şifreli; şifresiz hâli CI tarafından reddedilir"),
    ("agent/hragent/__main__.py", "agent", ["A"], "Ajan döngüsü; ilk gün ile 400. gün aynı"),
    ("agent/hragent/client.py", "agent", ["A"], "Bağlantıyı her zaman ajan kurar: giden 443"),
    ("agent/hragent/runner.py", "agent", ["A"], "Yalnız A şeridini yürütür; Ansible işini reddeder"),
    ("agent/hragent/secrets.py", "agent", ["A"], "`.env` okur; fazla açık izinli dosyayı reddeder"),
    ("agent/hragent/inventory.py", "agent", ["A"],
     "Kimlik anahtarı kalıcı ajan kimliği — klon makineler için"),
    ("agent/hragent/apply/packages.py", "agent", ["A"],
     "Paketler relay önbelleğinden; kurulu ise dokunmaz"),
    ("agent/hragent/apply/files.py", "agent", ["A"], "Sır dosyaları daima 0600"),
    ("agent/tests/test_runner.py", "agent", ["A"], "Ajanın kendi şeridi dışına çıkmadığının testi"),
    ("human/templates/access_pack.md", "human", ["F"],
     "0. gün erişim paketi; liste paketten otomatik üretilir"),
    ("human/templates/acceptance.md", "human", ["F"],
     "Proje → yönetilen devri; sağlık yeşil olmadan kapanmaz"),
    ("human/templates/pentest_authorization.md", "human", ["F"], "İmzasız test başlamaz"),
    ("human/runbooks/dr_failover.md", "human", ["F"], "Failover'ı kimin ilan edeceği isimle yazılı"),
    (".github/workflows/ci.yml", "platform", ["D"],
     "Şifresiz kasa, depoya girmiş .env ve açık metin sır kalıbını reddeder"),
    ("README.md", "platform", ["D"], "Beş bileşen, şerit karşılıkları ve kasa tablosu"),
]

LANG = {".py": "python", ".yml": "yaml", ".yaml": "yaml", ".json": "json",
        ".md": "markdown", ".cfg": "ini", ".conf": "ini", ".toml": "ini"}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def build() -> int:
    entries, missing = [], []
    for path, component, lanes, role in FILES:
        target = ROOT / path
        if not target.is_file():
            missing.append(path)
            continue
        code = target.read_text(encoding="utf-8")
        entries.append({
            "path": path, "component": component, "lanes": lanes, "role": role,
            "lang": LANG.get(target.suffix, "plaintext"),
            "lines": code.count("\n") + 1, "bytes": len(code.encode()), "code": code,
        })

    if missing:
        print("UYARI — haritada listelenip depoda bulunmayan dosyalar:", file=sys.stderr)
        for path in missing:
            print("  ", path, file=sys.stderr)

    data = {
        "files": entries,
        "total_tracked": len(git("ls-files").splitlines()),
        "commit": git("rev-parse", "--short", "HEAD"),
    }
    (HERE / "codemap.json").write_text(json.dumps(data, ensure_ascii=False, indent=1),
                                       encoding="utf-8")

    template = (HERE / "template.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</script>", "<\\/script>")
    (HERE / "kod-haritasi.html").write_text(
        template.replace("__DATA__", payload), encoding="utf-8")

    print(f"kod-haritasi.html güncellendi — {len(entries)} dosya, "
          f"{sum(e['lines'] for e in entries)} satır, commit {data['commit']}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(build())
