# Orkestratör — n8n

İş akışları burada sürümlenir; n8n arayüzünden değil depodan yüklenir.

| Akış | Şerit | Ne yapar |
|------|-------|----------|
| `onboarding.json` | D | Sözleşme imzalanınca erişim listesini üretir, formu açar, kanarya testini koşar |
| `drift_reconcile.json` | E | 15 dakikada bir sapmaları uzlaştırır; etki sınırı aşılırsa geri alır |
| `scheduled_monthly_report.json` | E | Ayın 1'i 06:00 (Europe/Istanbul) aylık raporu üretir |

## Sırlar

Hiçbir akışta açık metin parola bulunmaz. Her düğüm **n8n credentials** kaydına
referans verir (`credentials` alanı). Dışa aktarırken bu alan yalnız kimlik ve ad taşır;
değerin kendisi n8n'in şifreli deposunda kalır.

```bash
# İçe aktarma
n8n import:workflow --separate --input=workflows/
```
