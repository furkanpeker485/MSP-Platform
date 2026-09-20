# Sır yönetimi

Kaynak koda parola yazılmaz. İstisna yoktur.

| Çalışan | Kasa | Nasıl okunur |
|---------|------|--------------|
| `agent/` (Python) ve makinedeki script'ler | `.env` | `hragent.secrets.load()` |
| `relay/ansible/` playbook'ları | `ansible-vault` | `group_vars/all/vault.yml` |
| `orchestrator/` iş akışları | n8n credentials | akış içinde `credentials` referansı |
| `platform/` arka ucu | ortam değişkeni / harici kasa | `app/config.py` → `Settings` |

## Devreye almanın ilk adımı

Her hizmetin görev listesindeki ilk madde, erişim bilgilerinin kasaya yazılmasıdır
(`catalog/services/*.yaml` → `tasks[0]`). Kasaya yazılmamış bir yetkiyle hiçbir hizmet
başlatılmaz: `spec_compiler.compile()` eksik sır referansı bulursa `MissingSecret` fırlatır.

## CI koruması

`.github/workflows/ci.yml` içindeki `secret-scan` işi şunları reddeder:

* şifrelenmemiş `vault.yml` (`$ANSIBLE_VAULT;` başlığı yoksa)
* depoya girmiş `.env` dosyası (yalnız `.env.example` serbest)
* kaynak kodda açık metin parola/anahtar kalıpları
