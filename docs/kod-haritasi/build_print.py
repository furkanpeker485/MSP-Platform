#!/usr/bin/env python3
"""Kod haritasının baskı kaynağını codemap.json'dan yeniden üretir.

    python3 docs/kod-haritasi/build_print.py

Önce `build.py` çalıştırılmalıdır: o, depodaki güncel dosyalardan codemap.json'u üretir.
Bu betik de o veriden baskıya dizilmiş HTML'i kurar; PDF bundan basılır.

Girdi : codemap.json · assets/print.css · assets/topoloji.svg
Çıktı : baski-kaynagi.html
"""
from __future__ import annotations

import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
e = html.escape

data = json.loads((HERE / "codemap.json").read_text(encoding="utf-8"))
files = data["files"]
CSS = (HERE / "assets/print.css").read_text(encoding="utf-8")
DIA = (HERE / "assets/topoloji.svg").read_text(encoding="utf-8")

HEX = {"A": "#2F6FED", "B": "#7A4CD0", "C": "#0C8F84",
       "D": "#AD6A0C", "E": "#B93B74", "F": "#657279"}
LN = {"A": "Aracı yazılım", "B": "Uzaktan ayar", "C": "Sağlayıcı arayüzü",
      "D": "Platform kurulumu", "E": "Takvimli iş", "F": "İnsan işi"}
COMP = [
    ("n8n", "1 · Orkestratör (n8n)", "#B93B74",
     "Sözleşmeden sonra ne olacağını sıraya koyan iş akışları"),
    ("platform", "2 · HR Platformu", "#AD6A0C",
     "Beyin: katalog, tanım derleyici, şerit dağıtıcısı, entegrasyonlar"),
    ("relay", "3 · Site Relay", "#7A4CD0",
     "Müşteri sahasındaki aracı düğüm: kuyruk, yürütme düğümü, izleme vekili"),
    ("human", "4 · İnsan", "#657279",
     "İş emri, yetki belgesi ve kabul formu şablonları"),
    ("agent", "5 · Uç Nokta Ajanı", "#2F6FED",
     "Uç cihazda koşan Python ajanı"),
]
byc = lambda k: [f for f in files if f["component"] == k]
toplam_satir = sum(f["lines"] for f in files)


def envanter() -> str:
    r = []
    for k, baslik, hexc, _ in COMP:
        r.append(f'<tr class="grp"><td colspan="4" style="border-left:3mm solid {hexc}">'
                 f'{e(baslik)} — {len(byc(k))} dosya</td></tr>')
        for f in byc(k):
            pills = "".join(f'<span class="lp" style="background:{HEX[l]}">{l}</span>'
                            for l in f["lanes"])
            r.append(f'<tr><td class="p">{e(f["path"])}</td><td>{e(f["role"])}</td>'
                     f'<td class="c">{pills}</td><td class="c n">{f["lines"]}</td></tr>')
    return "".join(r)


def kodlar() -> str:
    o = []
    for k, baslik, hexc, alt in COMP:
        o.append(f'<h2 style="border-top-color:{hexc}">{e(baslik)}</h2>'
                 f'<p class="sub">{e(alt)}</p>')
        for f in byc(k):
            serit = " · ".join(f"{l} — {LN[l]}" for l in f["lanes"])
            o.append(f'<section class="file"><h3>{e(f["path"])}</h3>'
                     f'<p class="role">{e(f["role"])}</p>'
                     f'<p class="meta">şerit: {e(serit)} · {f["lines"]} satır · {f["lang"]}</p>'
                     f'<pre>{e(f["code"])}</pre></section>')
    return "".join(o)


EMULASYON = """<section style="page-break-before:always">
<h2 style="border-top-color:#0C8F84">Emülasyon: bu haritadaki kod gerçekten koşuyor</h2>
<p class="sub">Bu belgedeki dosyalar <code>demo/</code> altındaki emülasyon ortamında, gerçek
konteynerler ve gerçek ağ cihazlarıyla kurulan 19 düğümlük bir topolojide çalıştırıldı.
Altı ağ bacağı ayrı ayrı emüle edildi: HR kontrol düzlemi (10.10.0.0/24), WAN geçişi
(100.64.0.0/30), müşteri DMZ'si (172.31.0.0/29) ve üç VLAN (yönetim 192.168.10.0/24,
sunucu 192.168.20.0/24, kullanıcı 192.168.30.0/24).</p>

<div class="pc"><p class="pc-p"><b>Son koşuda 33 kontrolün 33'ü geçti.</b> Platform 39 hizmetlik
kataloğu yükledi; site relay dört ağ bacağı üzerinden HR platformuna HTTP 200 aldı; ters yön
engellendi; receptor mesh relay-acme &harr; hr-awx-hop olarak kuruldu; kasa başka kiracının alanı
istendiğinde 403 döndü; ajan çalıştıramayan düğümlerde ajan bulunmadığı ayrıca denetlendi.</p>
<p class="pc-c"><b>Nerede</b>Görsel demonstrasyon docs/demo/emulasyon.pdf; ortamın kendisi
demo/README.md; çalıştırma: cd demo &amp;&amp; ./scripts/up.sh, ./scripts/ag-dogrula.sh,
./scripts/demo-uctan-uca.sh.</p></div>

<div class="pc"><p class="pc-p"><b>Emülasyon bir hata yakaladı.</b> relay/relay_api/ içindeki iş
kuyruğu modülü önce queue.py adındaydı ve Python'un standart kütüphanesindeki queue modülüyle
çakışıyordu. Konteynerde stdlib kazandı ve relay API'si 500 döndürdü.</p>
<p class="pc-c"><b>Düzeltme</b>Modül jobqueue.py olarak yeniden adlandırıldı. Bu hata yalnız kod
okunarak değil, çalıştırılarak görülebilirdi.</p></div>

<div class="pc"><p class="pc-p"><b>Emülasyonun kendi kırılganlığı.</b> Bir düğüm tek başına yeniden
yaratıldığında sanal kablo çifti yenilenir ve karşı uçtaki anahtar portu köprüden düşer.</p>
<p class="pc-c"><b>Çözüm</b>demo/scripts/ag-onar.sh köprü üyeliğini tekrar çalıştırılabilir biçimde
yeniden uygular ve kurulumun sonunda kendiliğinden koşar.</p></div>
</section>"""


doc = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>Kod Haritası</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>{CSS}</style></head><body>
<div class="cover">
 <div>
  <p class="eyebrow">MSP-Platform · kod topolojisi</p>
  <h1>Hangi kod, hangi bileşende, hangi şeritte.</h1>
  <p class="lead">Beş bileşenin kaynak kodu tek belgede. Önce topoloji, sonra dosya envanteri,
  ardından haritadaki her dosyanın kodunun tamamı. Bu belgedeki kod örnek değildir — deponun
  <code>main</code> dalındaki gerçek içeriktir ({e(data['commit'])}).</p>
  <div class="facts">
   <div><b>{data['total_tracked']}</b><span>depodaki dosya</span></div>
   <div><b>{len(files)}</b><span>belgede tam kod</span></div>
   <div><b>{toplam_satir:,}</b><span>satır</span></div>
   <div><b>5</b><span>bileşen</span></div>
   <div><b>6</b><span>şerit</span></div>
  </div>
 </div>
 <div>
  {DIA}
  <div class="callout"><h3>Bağlantı yönü tasarımın tamamıdır</h3>
  <p>Müşteri ağına giren her bağlantı içeriden başlatılır. Relay, AWX automation mesh'te
  <b>listener_port: null</b> ve <b>peers_from_control_nodes: false</b> ile yapılandırılmış bir yürütme
  düğümüdür; gelen bağlantı dinlemez. Ajan da aynı şekilde yalnız dışarı arar.</p></div>
 </div>
 <p class="foot">Sır yönetimi: makinede koşan script'ler <b>.env</b>, Ansible adımları <b>ansible-vault</b>,
 n8n iş akışları ve arayüz çağrıları <b>n8n credentials</b> kullanır. Hiçbir dosyada açık metin parola yoktur.</p>
</div>

<h2 style="border-top-color:#0B6970;page-break-before:auto">Dosya envanteri</h2>
<p class="sub">Her dosyanın hangi bileşende olduğu, ne işe yaradığı ve hangi şeritlere hizmet ettiği.</p>
<table><thead><tr><th>Dosya</th><th>Rol</th><th style="text-align:center">Şerit</th>
<th style="text-align:center">Satır</th></tr></thead><tbody>{envanter()}</tbody></table>

{kodlar()}
{EMULASYON}
<p class="foot">Şerit kısaltmaları: A — aracı yazılım · B — uzaktan ayar · C — sağlayıcı arayüzü ·
D — platform kurulumu · E — takvimli iş · F — insan işi.</p>
</body></html>"""

(HERE / "baski-kaynagi.html").write_text(doc, encoding="utf-8")
print(f"baski-kaynagi.html üretildi · {len(files)} dosya, {toplam_satir} satır, commit {data['commit']}")
