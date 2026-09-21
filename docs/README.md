# Belgeler

Bu klasör, platformun tasarım ve mimari belgelerini taşır. Kod ile aynı depoda
sürümlenirler; kod değiştiğinde belge de güncellenir.

## Yazılı belgeler

| Dosya | İçerik |
|-------|--------|
| [`architecture.md`](architecture.md) | Kontrol düzlemi / yürütme düzlemi ayrımı, relay'in neden n8n worker'ı olmadığı, görev grafiği |
| [`secrets.md`](secrets.md) | Hangi çalışanın hangi kasayı kullandığı ve sürekli tümleştirme korumaları |

## Hizmet Şeritleri — teslim mimarisi

Yayındaki 39 hizmetin, o işi fiilen yapan altı yürütme şeridine eşlendiği harita.
Her hizmet için sade açıklama, akış şeması, ilk gün adımları, gereken yetkiler ve
sağlık kontrolü. Sorunların yanında çözümleri, beş aşamalı kurulum sırası ve sözlük.

| Dosya | Ne için |
|-------|---------|
| `hizmet-seritleri/hizmet-seritleri.html` | Tarayıcıda açılır, süzülebilir harita |
| `hizmet-seritleri/hizmet-seritleri-animasyonlu.html` | Aynı içeriğin hareketli sürümü; sunum için |
| `hizmet-seritleri/hizmet-seritleri.pdf` | Baskı ve paylaşım (45 sayfa) |
| `hizmet-seritleri/baski-kaynagi.html` | PDF'in üretildiği kaynak |
| `hizmet-seritleri/build.py` | Baskı kaynağını `data.json`'dan yeniden üretir |
| `hizmet-seritleri/animate.py` | Hareketli sürümü haritadan yeniden üretir |
| `hizmet-seritleri/data.json` | Belgenin veri kaynağı: 39 hizmet, çözümler, sözlük |
| `hizmet-seritleri/abbr.py` | Kısaltma → günlük Türkçe karşılık eşlemesi (180 terim) |
| `hizmet-seritleri/assets/` | Baskı stili ve şema dosyaları |

### Belgeyi güncellemek

İçerik `data.json` içinde durur; HTML ve PDF ondan üretilir. Bir hizmetin açıklaması
veya bir çözüm değişecekse önce `data.json` güncellenir, sonra:

```bash
python3 docs/hizmet-seritleri/build.py      # baski-kaynagi.html
python3 docs/hizmet-seritleri/animate.py    # hareketli sürüm
```

`animate.py`, `hizmet-seritleri.html` dosyasına hareket katmanını ekler; giriş
animasyonları opaklık değil yalnızca konum değiştirir, böylece animasyon hiç
çalışmasa bile içerik tam görünür kalır.

## Kod Haritası — bu deponun topolojisi

Beş bileşenin kaynak kodu tek haritada. Bileşene tıklanınca dosyalar, dosyaya
tıklanınca kodun tamamı açılır; şerit düğmeleri o şeride hizmet eden dosyaları
canlı çizgilerle işaretler.

| Dosya | Ne için |
|-------|---------|
| `kod-haritasi/kod-haritasi.html` | Etkileşimli harita |
| `kod-haritasi/kod-haritasi.pdf` | 49 dosyanın kodunun tamamı (58 sayfa) |
| `kod-haritasi/build.py` | Haritayı depodaki gerçek koddan yeniden üretir |
| `kod-haritasi/build_print.py` | Baskı kaynağını `codemap.json`'dan yeniden üretir |
| `kod-haritasi/template.html` | Harita şablonu (`__DATA__` yer tutuculu) |
| `kod-haritasi/codemap.json` | Üretilen veri: dosya içerikleri ve şerit eşlemesi |

### Önemli: harita bir anlık görüntüdür

`kod-haritasi.html`, kaynak kodun **o andaki kopyasını içinde taşır**. Kod değişince
harita eskir. Güncellemek için depo kökünden:

```bash
python3 docs/kod-haritasi/build.py
```

Betik, listelediği bir dosya depoda yoksa uyarır ve sıfırdan farklı çıkış kodu döner;
böylece bir dosya taşındığında harita sessizce eskimez. Haritaya yeni dosya eklemek
için `build.py` içindeki `FILES` listesine bir satır yazmak yeterlidir.


## Emülasyon Demosu — topolojinin tamamı ayakta

Platformun beş bileşeni, altı ağ bacağı ve 19 düğümü gerçek konteynerler ve gerçek ağ
cihazlarıyla ayağa kaldırılır. Kutuların içinde deponun **gerçek kodu** koşar: platform
39 hizmetlik kataloğu yükler, ajan relay'in iş kuyruğuna bağlanır, güvenlik duvarına
kural basılır.

| Dosya | Ne için |
|-------|---------|
| `demo/emulasyon.html` | Görsel demonstrasyon: topoloji şeması, bacak tabloları, ölçüm sonuçları |
| `demo/emulasyon.pdf` | Aynı belgenin baskı sürümü |
| `demo/build.py` | Belgeyi son koşunun çıktısından yeniden üretir |
| `../demo/` | Emülasyon ortamının kendisi: topoloji, imajlar, betikler |

### Üç komutla çalıştırma

```bash
cd demo
./scripts/up.sh              # imajları derler, topolojiyi kurar
./scripts/ag-dogrula.sh      # altı ağ bacağını kanıtlar
./scripts/demo-uctan-uca.sh  # sözleşmeden çalışan hizmete senaryo
```

### Ölçülen sonuçlar

Son koşuda **33 kontrolün 33'ü geçti, 0'ı düştü**. Öne çıkanlar:

* Altı ağ bacağı da ayrı yayın alanı: aynı VLAN'da TTL 64, farklı VLAN'da 63, WAN ötesinde 61.
* Yön kuralı ölçüldü: relay → HR platformu **HTTP 200**, HR → relay **engellendi**.
* Receptor mesh dışa doğru kuruldu: `relay-acme ↔ hr-awx-hop`.
* Kasa kiracı sınırını korudu: başka kiracının alanı istendiğinde **403**.
* Ajan çalıştıramayan düğümlerde ajan bulunmadığı ayrıca denetlendi.

Ayrıntı: [`../demo/README.md`](../demo/README.md)

## PDF'leri yeniden üretmek

```bash
# Hizmet Şeritleri
chrome --headless=new --no-pdf-header-footer --virtual-time-budget=15000 \
  --print-to-pdf=docs/hizmet-seritleri/hizmet-seritleri.pdf \
  file://$PWD/docs/hizmet-seritleri/baski-kaynagi.html

# Kod Haritası
chrome --headless=new --no-pdf-header-footer --virtual-time-budget=20000 \
  --print-to-pdf=docs/kod-haritasi/kod-haritasi.pdf \
  file://$PWD/docs/kod-haritasi/baski-kaynagi.html

# Emülasyon Demosu
python3 docs/demo/build.py
chrome --headless=new --no-pdf-header-footer --virtual-time-budget=20000 \
  --print-to-pdf=docs/demo/emulasyon.pdf \
  file://$PWD/docs/demo/baski-kaynagi.html
```
