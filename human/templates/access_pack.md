# 0. Gün Erişim Paketi — {{ musteri }}

Bu liste **otomatik üretilmiştir**: yalnız `{{ paket }}` paketinin gerektirdiği erişimler
istenir. Gereksiz hiçbir yetki talep edilmez, gereken hiçbir yetki unutulmaz.

Her kalem alındığı anda kendi kasasına yazılır ve bir daha açık metin olarak durmaz.

| # | Erişim | Nereye yazılır | Kaç hizmet buna bağlı | Teslim alındı |
|---|--------|----------------|----------------------|---------------|
{% for item in erisimler %}| {{ loop.index }} | {{ item.ad }} | `{{ item.kasa }}` | {{ item.bagimli_hizmet }} | ☐ |
{% endfor %}

## Saha erişimi

- [ ] Lokasyon listesi ve adresler
- [ ] Bina giriş izni / kart veya refakat düzeni
- [ ] Kabinet anahtarı
- [ ] Site relay için rack veya sanal makine kapasitesi, yönetim ağı ve giden 443 izni

## Kapanış

Paket tamamlanmadan hiçbir hizmet başlatılmaz. Her kalem kasaya yazıldıktan sonra
otomatik kanarya testi koşar; **yeşil dönmeden hizmet başlatılmış sayılmaz.**

İmza (müşteri yetkilisi): ____________________   Tarih: __________
