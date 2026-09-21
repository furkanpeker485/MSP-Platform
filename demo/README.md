# Emülasyon Demosu

Platformun tamamının — beş bileşen, altı ağ bacağı, ajan çalıştıran ve çalıştıramayan
cihazlar — gerçek konteynerler ve gerçek ağ cihazlarıyla ayağa kaldırıldığı ortam.

Bu bir çizim değil: kutuların içinde deponun **gerçek kodu** koşar. Platform gerçekten
39 hizmetlik kataloğu yükler, ajan gerçekten relay'e bağlanır, güvenlik duvarına gerçekten
kural basılır.

## Hızlı başlangıç

```bash
cd demo
./scripts/up.sh              # imajları derler, topolojiyi kurar
./scripts/ag-dogrula.sh      # altı ağ bacağını kanıtlar
./scripts/demo-uctan-uca.sh  # sözleşmeden çalışan hizmete senaryo
./scripts/down.sh            # kaldırır
```

## Neyi neyle emüle ediyoruz

| Katman | Araç | Neden |
|--------|------|-------|
| Topoloji ve ağ bacakları | **containerlab 0.79** | Düğümleri ve aralarındaki sanal kabloları bildirimsel tanımlar; her bağlantı gerçek bir veth çiftidir |
| Yönlendirici / L3 anahtar | **FRRouting 10.2.1** | Gerçek yönlendirme yazılımı; `vtysh` ile yapılandırılır |
| Güvenlik duvarı ve erişim anahtarı | **nftables + OpenSSH** (Alpine) | Üzerine ajan kurulamayan, yalnız uzaktan yapılandırılan cihazı temsil eder |
| Yürütme düğümü | **ansible/receptor 1.6.9** | AWX automation mesh'in gerçek bileşeni |
| İzleme | **Zabbix 7.4** sunucu + vekil | Gerçek izleme zinciri |
| Uygulama katmanı | **deponun kendi kodu** | `platform/`, `agent/`, `relay/` olduğu gibi çalışır |

Linux ana makinede containerlab doğrudan koşar. Apple Silicon macOS'ta **Colima**
(Lima sanal makinesi) içinde çalışır; betikler bu farkı kendileri halleder.

## Altı ağ bacağı

| # | Bacak | Adres bloğu | Ne var |
|---|-------|-------------|--------|
| 1 | `hr-core` | `10.10.0.0/24` | Platform, orkestratör, AWX hop düğümü, izleme, veritabanı, kasa |
| 2 | `wan` | `100.64.0.0/30` | HR kenarı ile müşteri arasındaki geçiş |
| 3 | `cust-dmz` | `172.31.0.0/29` | Güvenlik duvarının iç ayağı |
| 4 | `cust-mgmt` | `192.168.10.0/24` | Site relay, yürütme düğümü, izleme vekili, paket önbelleği |
| 5 | `cust-srv` | `192.168.20.0/24` | Ajan çalıştıran Linux sunucular |
| 6 | `cust-usr` | `192.168.30.0/24` | Ajan çalıştıran kullanıcı bilgisayarları |

VLAN'lar gerçekten ayrı yayın alanlarıdır: çekirdek anahtarda üç ayrı köprü arayüzü
(`br-mgmt`, `br-srv`, `br-usr`) vardır ve VLAN'lar arası trafik yönlendiriciden geçer.
`ag-dogrula.sh` bunu TTL farkıyla kanıtlar.

## Ajan çalıştıran ve çalıştıramayan düğümler

Tasarımın ayrımı emülasyonda da fiziksel:

* **Ajan çalıştıran (A şeridi):** `srv-01`, `srv-02`, `pc-01`, `pc-02` — üzerlerinde
  `agent/` kodu kuruludur, relay'in iş kuyruğuna kendileri bağlanır.
* **Ajan çalıştıramayan (B şeridi):** `cust-fw`, `cust-sw-access`, yönlendiriciler —
  bu imajlarda ajan **yoktur**; yalnız SSH ile dışarıdan yapılandırılırlar.

`ag-dogrula.sh` her iki durumu da ayrı ayrı denetler.

## Yön kuralı

Müşteri ağına giden her bağlantı **içeriden** başlatılır:

* relay → HR platformu: **açık** (giden 443/8000)
* receptor yürütme düğümü → hop düğümü: **açık** (giden 27199, `tcp-peer` ile)
* HR → relay veya sunucu VLAN'ı: **kapalı** — güvenlik duvarı `forward` zincirinde
  `policy drop` ve dışarıdan içeri tek bir kural yok

Bu, `relay/receptor/execution.conf` içindeki `listener_port` yokluğunun ağ üzerindeki
karşılığıdır ve emülasyonda ölçülerek doğrulanır.

## Dosya düzeni

```
demo/
├── topology/msp-platform.clab.yml   19 düğüm, 18 bağlantı, 6 bacak
├── images/                       platform · agent · relay · appliance imajları
├── nodes/
│   ├── router/                   FRR yapılandırmaları (hr-sw, hr-edge, cust-core)
│   ├── firewall/nftables.conf    yön kuralının kaynağı
│   ├── receptor/                 hop.conf (dinler) · execution.conf (dışarı bağlanır)
│   └── platform/                 kasa ve orkestratör yardımcıları
├── scripts/
│   ├── up.sh · down.sh           yaşam döngüsü
│   ├── harita.sh                 düğüm/bacak tablosu
│   ├── ag-dogrula.sh             altı bacağın kanıtı
│   ├── ag-onar.sh                köprü üyeliğini yeniden uygular
│   └── demo-uctan-uca.sh         uçtan uca senaryo
└── assets/kanit-cikti.txt        son koşunun çıktısı
```

## Bilinen tuzaklar

* **Docker Hub hız sınırı.** Anonim çekimler 429 döndürebilir. Demo bilerek
  `quay.io` ve `ghcr.io` imajlarını ve yerel önbellekteki tabanları kullanır.
* **Bir düğümü tek başına yeniden yaratmak köprü üyeliğini bozar.** Sanal kablo
  yenilenince karşı uçtaki anahtar portu köprüden düşer. `ag-onar.sh` bunu
  tekrar tekrar çalıştırılabilir biçimde düzeltir ve `up.sh` sonunda kendiliğinden koşar.
* **Adres çakışması.** Yönetim ağı `172.28.28.0/24` kullanır. Makinenizde başka bir
  Docker ağı bu bloğu tutuyorsa topolojideki `mgmt.ipv4-subnet` değerini değiştirin.
* **arm64.** Tüm imajlar arm64 üzerinde doğrulandı. Arista cEOS ve Nokia SR Linux gibi
  yalnız amd64 olan ağ işletim sistemleri bilinçli olarak kullanılmadı.
