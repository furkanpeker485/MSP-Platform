# Site Relay — müşteri sahasındaki aracı düğüm

Müşterinin binasında duran tek kutu. Dört işi vardır:

1. **İş kuyruğu** (`relay_api/` + Redis) — platformdan gelen görevleri biriktirir; ajanlar
   bir sonraki yoklamalarında buradan çeker.
2. **AWX yürütme düğümü** (`receptor/`) — Ansible işleri burada koşar.
3. **Zabbix proxy** — izleme verisi önce burada toplanır, sonra merkeze gider.
4. **Paket önbelleği** — 300 makine aynı kurulum paketini geniş alan ağından çekmez.

## Bağlantı yönü

Relay **gelen bağlantı dinlemez**. Receptor `listener_port: null` ve
`peers_from_control_nodes: false` ile yapılandırılır; bağlantıyı kendisi dışarı doğru kurar.
Müşteri güvenlik duvarında HR için tek bir gelen kural açılmaz.

> Relay bir n8n worker'ı **değildir**. n8n worker'ları Redis'e ve n8n'in veritabanına
> doğrudan erişmek zorundadır; bunu her müşteri sahasına götürmek çok kiracılı bir ortamda
> kabul edilemez. Gerekçe: `../docs/architecture.md`

## Kurulum

```bash
cp .env.example .env     # değerler kasadan gelir, bu dosya depoya girmez
docker compose up -d
```
