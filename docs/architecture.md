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

## Emülasyon: mimarinin ölçülmüş hâli

Yukarıdaki her iddia `demo/` altındaki emülasyon ortamında çalıştırılarak doğrulanır.
Topoloji containerlab ile kurulur; yönlendiriciler FRRouting, güvenlik duvarı ve erişim
anahtarı nftables, yürütme düğümü gerçek receptor'dür. Uygulama katmanında deponun kendi
kodu koşar.

### Emüle edilen ağ bacakları

| # | Bacak | Blok | Düğümler |
|---|-------|------|----------|
| 1 | hr-core | `10.10.0.0/24` | platform · orkestratör · hop düğümü · izleme · veritabanı · kasa |
| 2 | wan | `100.64.0.0/30` | HR kenarı ↔ müşteri güvenlik duvarı |
| 3 | cust-dmz | `172.31.0.0/29` | güvenlik duvarı ↔ çekirdek anahtar |
| 4 | cust-mgmt | `192.168.10.0/24` | site relay · yürütme düğümü · izleme vekili · önbellek |
| 5 | cust-srv | `192.168.20.0/24` | ajan çalıştıran sunucular |
| 6 | cust-usr | `192.168.30.0/24` | ajan çalıştıran uç cihazlar |

VLAN'lar çekirdek anahtarda ayrı köprü arayüzleridir (`br-mgmt`, `br-srv`, `br-usr`),
dolayısıyla gerçekten ayrı yayın alanlarıdır.

### Yön kuralının kanıtı

| Yön | Ölçüm | Sonuç |
|-----|-------|-------|
| içeriden dışarı | relay → HR platformu | HTTP 200 |
| içeriden dışarı | yürütme düğümü → hop düğümü | mesh kuruldu (`relay-acme ↔ hr-awx-hop`) |
| dışarıdan içeri | HR platformu → relay API'si | engellendi |
| dışarıdan içeri | HR platformu → sunucu VLAN'ı | engellendi |

Güvenlik duvarının `forward` zincirinde `policy drop` vardır ve dışarıdan içeri tek bir
kural yoktur. Bu, `relay/receptor/execution.conf` içinde `listener_port` bulunmamasının
ağ üzerindeki karşılığıdır.

### TTL ile yayın alanı kanıtı

| Durum | Ölçüm | TTL |
|-------|-------|-----|
| aynı VLAN | pc-01 → pc-02 | 64 (yönlendirici yok) |
| farklı VLAN | pc-01 → srv-01 | 63 (bir atlama) |
| WAN ötesi | relay → hr-platform | 61 (üç atlama) |

Görsel demonstrasyon: [`demo/emulasyon.html`](demo/emulasyon.html) ·
Ortamın kendisi: [`../demo/README.md`](../demo/README.md)
