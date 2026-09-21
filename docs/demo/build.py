#!/usr/bin/env python3
"""Emülasyon demosunun görsel belgesini üretir.

    python3 docs/demo/build.py

Girdi : demo/assets/kanit-cikti.txt (son doğrulama koşusunun çıktısı)
Çıktı : docs/demo/emulasyon.html · docs/demo/baski-kaynagi.html
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
e = html.escape

veri = json.loads((HERE / "_veri.json").read_text(encoding="utf-8"))
LEG, NODES = veri["legs"], veri["nodes"]
GECEN, DUSEN, KANIT = veri["gecen"], veri["dusen"], veri["kanit"]
LEGHEX = {l[1]: l[3] for l in LEG}

# ── topoloji şeması: altı bacak, soldan sağa HR → WAN → müşteri ──────────────
def topoloji_svg(animasyonlu: bool) -> str:
    def dot(path, dur, begin, hexc):
        if not animasyonlu:
            return ""
        return (f'<circle r="4" fill="{hexc}" class="akis">'
                f'<animateMotion dur="{dur}" begin="{begin}" repeatCount="indefinite" path="{path}"/>'
                f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.12;.85;1" '
                f'dur="{dur}" begin="{begin}" repeatCount="indefinite"/></circle>')

    o = ['<svg viewBox="0 0 1180 700" role="img" aria-label="Emülasyon topolojisi: '
         'altı ağ bacağı, HR kontrol düzlemi, WAN geçişi, müşteri DMZ ve üç VLAN">']
    o.append('<defs><marker id="ok" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
             'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
             'fill="currentColor"/></marker></defs>')

    # bacak kutuları
    kutular = [
        ("hr-core",   20,  40, 300, 330),
        ("wan",      350, 150, 150, 110),
        ("cust-dmz", 530,  40, 150, 330),
        ("cust-mgmt",710,  40, 440, 150),
        ("cust-srv", 710, 210, 210, 160),
        ("cust-usr", 940, 210, 210, 160),
    ]
    for ad, x, y, w, h in kutular:
        hexc = LEGHEX[ad]
        no, _, blok, _, baslik, _ = next(l for l in LEG if l[1] == ad)
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="none" '
                 f'stroke="{hexc}" stroke-width="1.6" stroke-dasharray="6 5" opacity=".85"/>')
        o.append(f'<text x="{x+12}" y="{y+20}" font-size="10" font-family="var(--mono)" '
                 f'fill="{hexc}" letter-spacing="1.1">BACAK {no} · {e(ad.upper())}</text>')
        o.append(f'<text x="{x+12}" y="{y+34}" font-size="9.5" font-family="var(--mono)" '
                 f'fill="currentColor" opacity=".6">{e(blok)}</text>')

    # düğümler
    yer = {
        "hr-sw":(34,52),"hr-platform":(34,92),"hr-n8n":(34,124),"hr-awx":(34,156),
        "hr-zabbix":(34,188),"hr-db":(34,220),"hr-vault":(34,252),"hr-edge":(34,300),
        "cust-fw":(544,180),"cust-core":(724,300),
        "cust-sw-access":(724,52),"relay":(724,92),"relay-receptor":(724,124),
        "relay-zbxproxy":(950,92),"relay-cache":(950,124),
        "srv-01":(724,250),"srv-02":(724,282),"pc-01":(954,250),"pc-02":(954,282),
    }
    W = {"hr-sw":270,"hr-platform":270,"hr-n8n":270,"hr-awx":270,"hr-zabbix":270,
         "hr-db":270,"hr-vault":270,"hr-edge":270,"cust-fw":126,"cust-core":410,
         "cust-sw-access":200,"relay":200,"relay-receptor":200,"relay-zbxproxy":186,
         "relay-cache":186,"srv-01":180,"srv-02":180,"pc-01":180,"pc-02":180}
    for ad, bacak, adres, imaj, rol, tip in NODES:
        if ad not in yer: continue
        x, y = yer[ad]; w = W[ad]; hexc = LEGHEX[bacak]
        kesik = ' stroke-dasharray="4 3"' if tip == "cihaz" else ""
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="4" fill="var(--surface)" '
                 f'stroke="{hexc}" stroke-width="1.3"{kesik}/>')
        o.append(f'<rect x="{x}" y="{y}" width="3" height="26" rx="1.5" fill="{hexc}"/>')
        o.append(f'<text x="{x+10}" y="{y+17}" font-size="10.5" font-family="var(--mono)" '
                 f'fill="var(--ink)">{e(ad)}</text>')
        etiket = {"cihaz":"ajan YOK","ajan":"ajan VAR","kod":""}[tip]
        if etiket:
            renk = "var(--muted)" if tip == "cihaz" else hexc
            o.append(f'<text x="{x+w-8}" y="{y+17}" font-size="8.5" font-family="var(--mono)" '
                     f'text-anchor="end" fill="{renk}">{etiket}</text>')

    # bacaklar arası bağlantılar + akan sinyal
    baglar = [
        ("M304,313 L360,205", "hr-edge → WAN", "#0B6970", "3s", "0s"),
        ("M440,205 L544,193", "WAN → güvenlik duvarı", "#0B6970", "3s", "0.6s"),
        ("M606,206 L606,300 L724,313", "güvenlik duvarı → çekirdek anahtar", "#B93B74", "3s", "1.2s"),
        ("M800,300 L800,120", "çekirdek → yönetim VLAN'ı", "#7A4CD0", "2.4s", "0.3s"),
        ("M860,300 L860,278", "çekirdek → sunucu VLAN'ı", "#2F6FED", "2.4s", "0.9s"),
        ("M1040,300 L1040,278", "çekirdek → kullanıcı VLAN'ı", "#0C8F84", "2.4s", "1.5s"),
    ]
    for path, _, hexc, dur, begin in baglar:
        o.append(f'<path d="{path}" fill="none" stroke="{hexc}" stroke-width="1.8" '
                 f'marker-end="url(#ok)" opacity=".8"/>')
        o.append(dot(path, dur, begin, hexc))

    o.append('<text x="360" y="390" font-size="10.5" font-family="var(--mono)" '
             'fill="var(--muted)">kesikli çerçeve = ajan çalıştıramayan cihaz · '
             'düz çerçeve = deponun kodu koşuyor</text>')
    o.append('</svg>')
    return "".join(o)


def bacak_tablosu() -> str:
    r = []
    for no, ad, blok, hexc, baslik, icerik in LEG:
        r.append(f'<tr><td class="no" style="color:{hexc}">{no}</td>'
                 f'<td class="ad"><span class="pip" style="background:{hexc}"></span>{e(ad)}</td>'
                 f'<td class="blk">{e(blok)}</td><td>{e(baslik)}</td>'
                 f'<td class="ic">{e(icerik)}</td></tr>')
    return "".join(r)


def dugum_tablosu() -> str:
    r = []
    for ad, bacak, adres, imaj, rol, tip in NODES:
        hexc = LEGHEX[bacak]
        rozet = {"cihaz":'<span class="rz rz-c">ajan YOK</span>',
                 "ajan":'<span class="rz rz-a">ajan VAR</span>',
                 "kod":'<span class="rz rz-k">kod</span>'}[tip]
        r.append(f'<tr><td class="ad"><span class="pip" style="background:{hexc}"></span>{e(ad)}</td>'
                 f'<td class="blk">{e(bacak)}</td><td class="blk">{e(adres)}</td>'
                 f'<td class="blk">{e(imaj)}</td><td>{e(rol)}</td><td>{rozet}</td></tr>')
    return "".join(r)


def kanit_blok() -> str:
    satirlar = []
    for ln in KANIT.splitlines():
        cls = ""
        if "✓" in ln: cls = "ok"
        elif "✗" in ln: cls = "hata"
        elif ln.startswith("━━"): cls = "bas"
        satirlar.append(f'<span class="{cls}">{e(ln)}</span>')
    return "\n".join(satirlar)


TTL = [("aynı VLAN", "pc-01 → pc-02", "64", "doğrudan, yönlendirici yok"),
       ("farklı VLAN", "pc-01 → srv-01", "63", "bir yönlendirici atlaması"),
       ("WAN ötesi", "relay → hr-platform", "61", "üç yönlendirici atlaması")]

YON = [("içeriden dışarı", "relay → HR platformu", "HTTP 200", True),
       ("içeriden dışarı", "yürütme düğümü → hop düğümü", "mesh kuruldu", True),
       ("dışarıdan içeri", "HR platformu → relay API'si", "engellendi", False),
       ("dışarıdan içeri", "HR platformu → sunucu VLAN'ı", "engellendi", False)]


CSS = """
:root{--bg:#F1F4F4;--surface:#FFFFFF;--surface-2:#E8EDED;--surface-3:#DDE5E5;
--ink:#0F1718;--ink-2:#37474A;--muted:#5E7075;--rule:#D3DCDC;--rule-2:#BECCCC;
--accent:#0B6970;--accent-2:#0A585D;--accent-soft:#DAEDED;--ok:#1B7A46;--hata:#B23A2B;
--mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;
--body:'IBM Plex Sans',system-ui,sans-serif;--display:'Archivo',Arial,sans-serif;
--shadow:0 1px 2px rgba(15,23,24,.05),0 8px 24px -16px rgba(15,23,24,.22);
--grid:rgba(11,105,112,.07)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
--bg:#0C1213;--surface:#141C1E;--surface-2:#1B2528;--surface-3:#243033;
--ink:#E7EEEE;--ink-2:#C3D0D1;--muted:#8EA0A4;--rule:#24302F;--rule-2:#31403F;
--accent:#3FB5BB;--accent-2:#7ED3D7;--accent-soft:#0F2A2C;--ok:#46C67E;--hata:#F08070;
--grid:rgba(63,181,187,.09);--shadow:0 1px 2px rgba(0,0,0,.4),0 12px 32px -20px rgba(0,0,0,.8)}}
:root[data-theme="dark"]{--bg:#0C1213;--surface:#141C1E;--surface-2:#1B2528;--surface-3:#243033;
--ink:#E7EEEE;--ink-2:#C3D0D1;--muted:#8EA0A4;--rule:#24302F;--rule-2:#31403F;
--accent:#3FB5BB;--accent-2:#7ED3D7;--accent-soft:#0F2A2C;--ok:#46C67E;--hata:#F08070;
--grid:rgba(63,181,187,.09);--shadow:0 1px 2px rgba(0,0,0,.4),0 12px 32px -20px rgba(0,0,0,.8)}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin-inline:auto;padding-inline:20px}
h1,h2,h3{font-family:var(--display);margin:0;letter-spacing:-.018em;line-height:1.15;text-wrap:balance}
p{margin:0 0 1em}
header{padding-block:44px 20px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);margin:0 0 14px}
h1{font-size:clamp(30px,5vw,50px);font-weight:700}
.lead{font-size:clamp(15px,2vw,17.5px);color:var(--ink-2);max-width:74ch;margin-top:16px}
.facts{display:flex;gap:26px;flex-wrap:wrap;margin-top:24px;padding-top:20px;border-top:1px solid var(--rule)}
.fact b{font-family:var(--display);font-size:24px;font-weight:700;display:block;line-height:1;font-variant-numeric:tabular-nums}
.fact span{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
section{padding-block:38px;border-top:1px solid var(--rule)}
.sec-head{display:flex;align-items:baseline;gap:14px;margin-bottom:8px;flex-wrap:wrap}
.sec-num{font-family:var(--mono);font-size:11px;font-weight:600;color:var(--accent);letter-spacing:.1em}
h2{font-size:clamp(21px,3.2vw,28px);font-weight:600}
.sub{color:var(--muted);margin:0 0 24px;max-width:70ch}
figure{margin:0;padding:20px;background:var(--surface);border:1px solid var(--rule);border-radius:10px;box-shadow:var(--shadow);overflow-x:auto;
background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:26px 26px}
figure svg{display:block;width:100%;min-width:900px;height:auto;color:var(--ink-2)}
figcaption{margin-top:14px;padding-top:12px;border-top:1px solid var(--rule);font-size:13px;color:var(--muted);min-width:900px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
.tw{border:1px solid var(--rule);border-radius:9px;overflow:hidden;background:var(--surface);box-shadow:var(--shadow)}
.ts{overflow-x:auto}
th{font-family:var(--mono);font-size:10px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:500;text-align:left;padding:10px 13px;background:var(--surface-2);border-bottom:1px solid var(--rule);white-space:nowrap}
td{padding:9px 13px;border-bottom:1px solid var(--rule);vertical-align:top}
tr:last-child td{border-bottom:0}
td.no{font-family:var(--display);font-weight:700;font-size:16px;width:34px}
td.ad{font-family:var(--mono);font-size:12.5px;font-weight:600;white-space:nowrap}
td.blk{font-family:var(--mono);font-size:11.5px;color:var(--ink-2);white-space:nowrap}
td.ic{color:var(--muted);font-size:12.5px}
.pip{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:7px}
.rz{font-family:var(--mono);font-size:10px;font-weight:600;padding:2px 7px;border-radius:4px;border:1px solid;white-space:nowrap}
.rz-c{color:var(--muted);border-color:var(--rule-2);background:var(--surface-2)}
.rz-a{color:var(--ok);border-color:color-mix(in srgb,var(--ok) 35%,transparent);background:color-mix(in srgb,var(--ok) 9%,transparent)}
.rz-k{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 35%,transparent);background:var(--accent-soft)}
pre{margin:0;padding:18px 20px;font-family:var(--mono);font-size:12px;line-height:1.6;overflow-x:auto;background:var(--surface);border:1px solid var(--rule);border-radius:9px;box-shadow:var(--shadow);max-height:520px}
pre .ok{color:var(--ok)} pre .hata{color:var(--hata)} pre .bas{color:var(--accent);font-weight:600}
pre span{display:block}
.kutu{background:var(--surface);border:1px solid var(--rule);border-left:2px solid var(--accent);border-radius:0 9px 9px 0;padding:16px 18px;box-shadow:var(--shadow)}
.kutu h3{font-size:15px;font-weight:600;margin-bottom:7px}
.kutu p{font-size:13.5px;color:var(--ink-2);margin:0}
.grid2{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
code{font-family:var(--mono);font-size:.88em;background:var(--surface-2);padding:1.5px 5px;border-radius:3px;border:1px solid var(--rule)}
.akis{filter:drop-shadow(0 0 3px currentColor)}
footer{padding-block:26px 56px;border-top:1px solid var(--rule);color:var(--muted);font-size:12.5px}
@media (prefers-reduced-motion:reduce){circle.akis{display:none}}
"""

def sayfa(animasyonlu: bool) -> str:
    ttl = "".join(f'<tr><td class="ad">{e(a)}</td><td class="blk">{e(b)}</td>'
                  f'<td class="blk" style="color:var(--accent);font-weight:600">TTL {c}</td>'
                  f'<td class="ic">{e(d)}</td></tr>' for a, b, c, d in TTL)
    yon = "".join(f'<tr><td class="ad">{e(a)}</td><td class="blk">{e(b)}</td>'
                  f'<td><span class="rz {"rz-a" if ok else "rz-c"}">{e(c)}</span></td></tr>'
                  for a, b, c, ok in YON)
    baslik = "Hisar Emülasyon Akışı" if animasyonlu else "Hisar Emülasyon Demosu"
    return f"""<title>{baslik}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header>
  <p class="eyebrow">Hisar Delivery Platform · uçtan uca emülasyon</p>
  <h1>Topolojinin tamamı, gerçek cihazlarla ayakta.</h1>
  <p class="lead">Beş bileşen, altı ağ bacağı ve 19 düğüm containerlab ile kuruldu.
  Kutuların içinde deponun <strong>gerçek kodu</strong> koşuyor: platform 39 hizmetlik kataloğu
  yüklüyor, ajan relay'in iş kuyruğuna bağlanıyor, güvenlik duvarına kural basılıyor.
  Aşağıdaki her sayı ölçülmüş bir koşudan geliyor.</p>
  <div class="facts">
    <div class="fact"><b>19</b><span>düğüm</span></div>
    <div class="fact"><b>6</b><span>ağ bacağı</span></div>
    <div class="fact"><b>18</b><span>sanal kablo</span></div>
    <div class="fact"><b style="color:var(--ok)">{GECEN}</b><span>geçen kontrol</span></div>
    <div class="fact"><b>{DUSEN}</b><span>düşen kontrol</span></div>
  </div>
</header>

<section>
  <div class="sec-head"><span class="sec-num">01</span><h2>Topoloji</h2></div>
  <p class="sub">Soldan sağa: HR kontrol düzlemi, WAN geçişi, müşteri güvenlik duvarı ve üç VLAN.
  Kesikli çerçeveli düğümlere ajan kurulamaz — onlar yalnız uzaktan yapılandırılır.</p>
  <figure>{topoloji_svg(animasyonlu)}
  <figcaption>Her bağlantı gerçek bir sanal kablo çiftidir; VLAN'lar çekirdek anahtarda ayrı
  köprü arayüzleridir. Bu yüzden farklı VLAN'lar arasındaki trafik gerçekten yönlendiriciden geçer.</figcaption></figure>
</section>

<section>
  <div class="sec-head"><span class="sec-num">02</span><h2>Altı ağ bacağı</h2></div>
  <p class="sub">İstenen ayrım burada: her bacak kendi adres bloğuna ve kendi yayın alanına sahip.</p>
  <div class="tw"><div class="ts"><table>
  <thead><tr><th>#</th><th>Bacak</th><th>Adres bloğu</th><th>Ne</th><th>İçinde ne var</th></tr></thead>
  <tbody>{bacak_tablosu()}</tbody></table></div></div>
</section>

<section>
  <div class="sec-head"><span class="sec-num">03</span><h2>VLAN'lar gerçekten ayrı mı</h2></div>
  <p class="sub">İddia değil ölçüm: aynı VLAN'da paket yönlendiriciye uğramaz, farklı VLAN'da uğrar.
  Her atlama TTL değerini bir düşürür.</p>
  <div class="tw"><div class="ts"><table>
  <thead><tr><th>Durum</th><th>Ölçüm</th><th>Sonuç</th><th>Anlamı</th></tr></thead>
  <tbody>{ttl}</tbody></table></div></div>
</section>

<section>
  <div class="sec-head"><span class="sec-num">04</span><h2>Yön kuralı</h2></div>
  <p class="sub">Tasarımın özü: müşteri ağına giden her bağlantı içeriden başlatılır.
  Güvenlik duvarında dışarıdan içeri tek bir kural yoktur — ve bu ölçülerek doğrulanır.</p>
  <div class="tw"><div class="ts"><table>
  <thead><tr><th>Yön</th><th>Ölçüm</th><th>Sonuç</th></tr></thead>
  <tbody>{yon}</tbody></table></div></div>
  <div class="grid2" style="margin-top:18px">
    <div class="kutu"><h3>Receptor mesh dışa doğru kuruldu</h3>
    <p>Yürütme düğümünde <code>listener_port</code> yoktur; bağlantıyı kendisi hop düğümüne kurar.
    Koşuda mesh <code>relay-acme ↔ hr-awx-hop</code> olarak göründü.</p></div>
    <div class="kutu"><h3>Kasa kiracı sınırını korudu</h3>
    <p>Bir kiracı için çalışan iş bilerek başka kiracının alanını istedi; kasa <code>403</code> döndü.
    Bu, <code>app/integrations/vault.py</code> kuralının ağ üzerindeki karşılığıdır.</p></div>
  </div>
</section>

<section>
  <div class="sec-head"><span class="sec-num">05</span><h2>Düğümler</h2></div>
  <p class="sub">Ajan çalıştıran ve çalıştıramayan düğümler emülasyonda da fiziksel olarak ayrıdır.</p>
  <div class="tw"><div class="ts"><table>
  <thead><tr><th>Düğüm</th><th>Bacak</th><th>Adres</th><th>İmaj</th><th>Rol</th><th>Ajan</th></tr></thead>
  <tbody>{dugum_tablosu()}</tbody></table></div></div>
</section>

<section>
  <div class="sec-head"><span class="sec-num">06</span><h2>Koşu çıktısı</h2></div>
  <p class="sub">Aşağısı <code>demo/scripts/ag-dogrula.sh</code> ve <code>demo/scripts/demo-uctan-uca.sh</code>
  betiklerinin gerçek çıktısıdır; düzenlenmemiştir.</p>
  <pre>{kanit_blok()}</pre>
</section>

<section>
  <div class="sec-head"><span class="sec-num">07</span><h2>Nasıl çalıştırılır</h2></div>
  <div class="grid2">
    <div class="kutu"><h3>Üç komut</h3><p><code>cd demo &amp;&amp; ./scripts/up.sh</code><br>
    <code>./scripts/ag-dogrula.sh</code><br><code>./scripts/demo-uctan-uca.sh</code></p></div>
    <div class="kutu"><h3>Gereken</h3><p>Docker ve containerlab. Apple Silicon macOS'ta
    containerlab Colima sanal makinesi içinde koşar; betikler bu farkı kendileri halleder.</p></div>
    <div class="kutu"><h3>Bilinen tuzak</h3><p>Bir düğümü tek başına yeniden yaratmak, karşı
    uçtaki anahtar portunu köprüden düşürür. <code>ag-onar.sh</code> bunu tekrar çalıştırılabilir
    biçimde düzeltir ve kurulumun sonunda kendiliğinden koşar.</p></div>
  </div>
</section>

<footer>Kapsam: containerlab 0.79 · FRRouting 10.2.1 · nftables 1.1.6 · receptor 1.6.9 ·
Zabbix 7.4 · tüm imajlar arm64 üzerinde doğrulandı. Ayrıntı: <code>demo/README.md</code>.</footer>
</div>"""


(HERE / "emulasyon.html").write_text(sayfa(animasyonlu=True), encoding="utf-8")
(HERE / "baski-kaynagi.html").write_text(
    "<!doctype html><html lang=\"tr\"><head><meta charset=\"utf-8\">"
    + sayfa(animasyonlu=False).replace(
        "pre{", "@page{size:A4;margin:14mm 12mm}\npre{").replace(
        "max-height:520px", "max-height:none")
    + "</body></html>", encoding="utf-8")
print(f"emulasyon.html ve baski-kaynagi.html üretildi · {GECEN} geçen, {DUSEN} düşen kontrol")
