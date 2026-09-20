# Mimari

## Kontrol düzlemi / yürütme düzlemi

Bütün kararlar HR Platformu'nda alınır. Müşteri tarafındaki hiçbir parça karar vermez.

```
  HR PLATFORMU (kontrol)                 MÜŞTERİ AĞI (yürütme)
  ┌───────────────────────┐              ┌──────────────────────────────┐
  │ FastAPI  · katalog    │              │  SITE RELAY                  │
  │ n8n      · orkestra   │◄────443──────│  · relay_api (iş kuyruğu)    │
  │ AWX      · hop node   │◄──27199──────│  · receptor (yürütme düğümü) │
  │ Zabbix   · izleme     │◄────443──────│  · zabbix-proxy              │
  │ NetBox   · envanter   │              │  · paket önbelleği           │
  │ SIEM     · kayıt      │              └───────┬──────────────┬───────┘
  │ Vault    · kasa       │                      │              │
  └───────────────────────┘             agent pull(443)   Ansible push
                                                │         (SSH/WinRM/NETCONF)
                                          ┌─────▼─────┐  ┌──────▼──────┐
                                          │ Sunucular │  │  Cihazlar   │
                                          │  (agent)  │  │ (agent yok) │
                                          └───────────┘  └─────────────┘
```

**Kural:** Müşteri ağına giren her bağlantı içeriden başlatılır. Güvenlik duvarında
HR için tek bir gelen kural açılmaz.

## Relay neden n8n worker'ı değil?

Araştırma sonucu ve kararı:

* **n8n queue mode worker'ı olamaz.** n8n'in worker'ları Redis'e *ve* n8n'in Postgres
  veritabanına doğrudan erişmek zorundadır ([n8n queue mode dokümanı][n8n]). Bu, her
  müşteri sahasına orkestratörün veritabanı erişimini götürmek demektir — çok kiracılı
  bir ortamda kabul edilemez.
* **Bunun yerine AWX automation mesh yürütme düğümü.** AWX/AAP, uzak ağlardaki düğümleri
  receptor mesh üzerinden merkezî olarak yönetmek için tasarlanmıştır ([AWX instances][awx]).
  Yürütme düğümü `listener_port: null` ve `peers_from_control_nodes: false` ile
  yapılandırıldığında **bağlantıyı kendisi dışarı doğru kurar**; gelen trafik dinlemez.
  Bu, yukarıdaki kuralla birebir örtüşür.

Sonuç: n8n merkezde kalır ve AWX API'sini çağırır; AWX işi receptor üzerinden doğru
müşterinin yürütme düğümüne yönlendirir. Relay üzerindeki Redis **yereldir** — yalnız
ajan iş kuyruğu ve önbellek için; HR ile paylaşılmaz.

[n8n]: https://docs.n8n.io/hosting/scaling/queue-mode/
[awx]: https://docs.ansible.com/projects/awx/en/24.6.1/administration/instances.html

## Tek hizmet, tek işlem değildir

Katalogdaki her hizmet bir **görev listesi**dir; düğümleri farklı şeritlere düşer.
`platform/app/catalog/services/*.yaml` bu listeyi taşır, `services/task_graph.py`
bağımlılıklara göre sıralar, `services/dispatcher.py` her görevi kendi şeridine yollar.

## Devreye alma ile günlük işletme aynı döngüdür

`services/drift.py` belirli aralıklarla mevcut durumu derlenmiş tanımla karşılaştırır.
İlk gün ile 400. gün arasında fark yoktur: her ikisinde de aynı uzlaştırma çalışır.
