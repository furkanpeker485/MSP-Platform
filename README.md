# HR-MSP-Platform

Hisar Research Managed Service Provider Platform

Hisar Research'ün yönetilen hizmet kataloğunu (yayında 39 hizmet) uçtan uca teslim eden
otomasyon platformunun kaynak kodu.

> **Durum:** Bu depo, `Hisar Hizmet Şeritleri` tasarım belgesinin koda dökülmüş hâlidir.
> Belgedeki altı yürütme şeridi (A–F) burada çalıştırılabilir bileşenlere karşılık gelir.

## Beş bileşen

| # | Bileşen | Klasör | Ne yapar |
|---|---------|--------|----------|
| 1 | **Orkestratör (n8n)** | `orchestrator/` | Sözleşme imzalanınca görev listesini derletir, işi şeritlere dağıtır, tekrar eden işleri takvimde koşturur |
| 2 | **HR Platformu** | `platform/` | Beyin: katalog, hak seti, tanım derleyici, denetim kaydı, Zabbix/NetBox/SIEM/ticket entegrasyonları |
| 3 | **Site Relay** | `relay/` | Müşteri sahasındaki aracı düğüm: iş kuyruğu, AWX yürütme düğümü, Zabbix proxy, paket önbelleği |
| 4 | **İnsan** | `human/` | İş emri şablonları, yetki belgeleri, kabul kriterleri, runbook'lar |
| 5 | **Aracı yazılım (agent)** | `agent/` | Uç cihaz ve sunucularda koşan Python ajanı: durum bildirir, tanımı çeker, uygular |

## Şeritler ve kod karşılıkları

| Şerit | Ne yürütür | Kod |
|-------|-----------|-----|
| **A** | Uç cihaz ajanı | `agent/` |
| **B** | Ansible ile uzaktan ayar | `relay/ansible/` + `platform/app/integrations/awx.py` |
| **C** | Sağlayıcı arayüzleri | `platform/app/integrations/` (netbox, zabbix, veeam, cloud) |
| **D** | HR platform kurulumu | `platform/app/services/` + `integrations/{zabbix,netbox,siem,ticketing}.py` |
| **E** | Takvimli işler | `orchestrator/workflows/scheduled_*.json` |
| **F** | İnsan iş emri | `human/` + `platform/app/integrations/ticketing.py` |

## Secret yönetimi — istisnasız

Hiçbir parola, anahtar veya sertifika kaynak koda yazılmaz.

| Nerede çalışıyor | Kasa |
|------------------|------|
| Agent ve makinede koşan script'ler | `.env` (bkz. `agent/.env.example`) |
| Ansible adımları | `ansible-vault` (bkz. `relay/ansible/group_vars/all/vault.yml`) |
| n8n iş akışları ve API çağrıları | n8n credentials |
| Platform arka ucu | ortam değişkeni → `platform/app/config.py` |

CI, `.env` ve vault dosyalarının şifresiz hâlde depoya girmesini engeller (`.github/workflows/ci.yml`).

## Hızlı başlangıç

```bash
# Platform
cd platform && python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]" && cp .env.example .env
uvicorn app.main:app --reload

# Agent (geliştirme)
cd agent && pip install -e ".[dev]" && cp .env.example .env
python -m hragent --once

# Relay (müşteri sahası)
cd relay && cp .env.example .env && docker compose up -d
```

## Belgeler

| Belge | İçerik |
|-------|--------|
| [`docs/architecture.md`](docs/architecture.md) | Kontrol düzlemi / yürütme düzlemi, relay'in neden n8n worker'ı olmadığı |
| [`docs/secrets.md`](docs/secrets.md) | Kasa kullanımı ve sürekli tümleştirme korumaları |
| [`docs/hizmet-seritleri/`](docs/hizmet-seritleri/) | Teslim mimarisi: 39 hizmetin altı şeride eşlenmesi (etkileşimli + PDF) |
| [`docs/kod-haritasi/`](docs/kod-haritasi/) | Bu deponun kod topolojisi; `build.py` ile yeniden üretilir |
