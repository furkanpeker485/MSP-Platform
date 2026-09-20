# Kabul Formu — Proje'den Yönetilen Hizmete Devir

Kurulum işi, **devralacak hizmetin ilk sağlık kontrolü yeşile dönmeden kapanmaz.**
Bu form, "kuruldu ama izlenmiyor" ve "teslim edildi ama yedeği yok" boşluğunu kapatır.

| Alan | Değer |
|------|-------|
| Proje hizmeti | {{ proje_hizmeti }} |
| Devralan yönetilen hizmet | {{ yonetilen_hizmet }} |
| Devir tarihi | {{ tarih }} |

## Kapanış koşulları

- [ ] Envanter kaydı oluşturuldu ve doğrulandı
- [ ] İzleme host'u açıldı, şablonu bağlandı, ilk veri geldi
- [ ] Yedekleme kapsamına alındı ve ilk geri dönüş noktası oluştu
- [ ] Erişim bilgileri kasaya yazıldı, kanarya testi yeşil
- [ ] Sağlık kontrolü **yeşil** — ekran görüntüsü eklendi

Saha ekibi: ______________  Devralan: ______________  Müşteri: ______________
