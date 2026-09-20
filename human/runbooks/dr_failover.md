# Felaket Kurtarma — Devir Runbook'u

**Failover'ı ilan etmeye yetkili kişi burada isimle yazılıdır.** Yetki nesnesi
tanımlı değilse otomasyon bekler; bu bilinçli bir tasarım kararıdır.

| Rol | İsim | İletişim |
|-----|------|----------|
| Failover ilan yetkisi | {{ yetkili }} | {{ iletisim }} |
| Müşteri onayı | {{ musteri_yetkili }} | {{ musteri_iletisim }} |

## Sıra
1. Olayı doğrula — izleme ve saha teyidi
2. Yetkili failover ilan eder (sözlü yeterli değil, kayıt açılır)
3. Adres değişikliği ve alan adı süreleri: kesimden **önce** düşürülmüş olmalı
4. Replikaları etkinleştir, açılış sırasını envanterden oku
5. Güvenlik duvarı kurallarını uygulanmamış şablondan aç
6. Uygulama seviyesinde kabul testi
7. Müşteriye bildir, kaydı kapat

> Süreyi replikasyon değil adres değişikliği, alan adı süresi ve lisans yeniden
> aktivasyonu belirler. Tatbikatta bunlar ölçülür.
