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

## Kod Haritası — bu deponun topolojisi

Beş bileşenin kaynak kodu tek haritada. Bileşene tıklanınca dosyalar, dosyaya
tıklanınca kodun tamamı açılır; şerit düğmeleri o şeride hizmet eden dosyaları
canlı çizgilerle işaretler.

| Dosya | Ne için |
|-------|---------|
| `kod-haritasi/kod-haritasi.html` | Etkileşimli harita |
| `kod-haritasi/kod-haritasi.pdf` | 49 dosyanın kodunun tamamı (58 sayfa) |
| `kod-haritasi/build.py` | Haritayı depodaki gerçek koddan yeniden üretir |
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
```
