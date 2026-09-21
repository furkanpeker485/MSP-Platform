#!/usr/bin/env python3
"""README'deki animasyonlu şemaları üretir.

    python3 docs/assets/build_svg.py

GitHub, Markdown içinde satır içi <svg> ve <script> kabul etmez; ancak <img> ile
gömülen bir SVG dosyasındaki SMIL animasyonları çalışır. Bu yüzden şemalar ayrı
dosyalar olarak üretilir ve README içinde <picture> ile açık/koyu temaya göre seçilir.

Çıktı: docs/assets/{seritler,kod-haritasi,topoloji}-{light,dark}.svg
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

# ── veriler depodan okunur, elle yazılmaz ────────────────────────────────────
serit = Counter(x["primary_lane"] for x in
                json.loads((ROOT / "docs/hizmet-seritleri/data.json").read_text("utf-8"))["items"])
codemap = json.loads((ROOT / "docs/kod-haritasi/codemap.json").read_text("utf-8"))
bilesen = Counter(f["component"] for f in codemap["files"])

TEMA = {
    "light": {"fg": "#1F2328", "mut": "#59636E", "kart": "#FFFFFF",
              "cizgi": "#D1D9E0", "yuzey": "#F6F8FA"},
    "dark":  {"fg": "#E6EDF3", "mut": "#8B949E", "kart": "#161B22",
              "cizgi": "#30363D", "yuzey": "#0D1117"},
}
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'

LANE = [
    ("A", "Aracı yazılım",       "#2F6FED", "uç cihaz ajanı"),
    ("B", "Uzaktan ayar",        "#8B5CF6", "Ansible · SSH/WinRM"),
    ("C", "Sağlayıcı arayüzü",   "#0F9B8E", "bulut ve üretici API'si"),
    ("D", "Platform kurulumu",   "#D08700", "Zabbix · NetBox · SIEM"),
    ("E", "Takvimli iş",         "#DB2777", "n8n zamanlanmış akış"),
    ("F", "İnsan işi",           "#6B7280", "saha · nöbet · danışman"),
]


def _bas(w: int, h: int, tema: str, baslik: str) -> list[str]:
    t = TEMA[tema]
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{baslik}">',
        f'<style>text{{font-family:{SANS}}} .m{{font-family:{MONO}}}</style>',
    ]


# ── 1) Hizmet şeritleri ──────────────────────────────────────────────────────
def seritler(tema: str) -> str:
    t = TEMA[tema]
    W, H = 880, 330
    toplam = sum(serit.values())
    o = _bas(W, H, tema, "Yayındaki 39 hizmetin altı yürütme şeridine dağılımı")
    o.append(f'<text x="0" y="16" font-size="13" font-weight="600" fill="{t["fg"]}">'
             f'Altı yürütme şeridi</text>')
    o.append(f'<text x="0" y="34" font-size="11" fill="{t["mut"]}" class="m">'
             f'yayındaki {toplam} hizmet · her biri onu fiilen yapan şeride bağlı</text>')

    enbuyuk = max(serit.values())
    y = 54
    for i, (kod, ad, renk, alt) in enumerate(LANE):
        n = serit.get(kod, 0)
        gen = int(560 * n / enbuyuk) if enbuyuk else 0
        gec = 0.12 * i
        o.append(f'<rect x="0" y="{y}" width="26" height="26" rx="5" fill="{renk}"/>')
        o.append(f'<text x="13" y="{y+18}" font-size="13" font-weight="700" fill="#fff" '
                 f'text-anchor="middle" class="m">{kod}</text>')
        o.append(f'<text x="36" y="{y+12}" font-size="12" font-weight="600" fill="{t["fg"]}">{ad}</text>')
        o.append(f'<text x="36" y="{y+25}" font-size="10" fill="{t["mut"]}" class="m">{alt}</text>')

        # çubuk: sıfırdan büyür ve öyle kalır
        bx = 210
        o.append(f'<rect x="{bx}" y="{y+5}" width="{max(gen,3)}" height="16" rx="8" '
                 f'fill="{renk}" opacity=".18"/>')
        # KURAL: içerik animasyona bağlı olmaz. Çubuk tam genişlikte doğar;
        # animasyon yalnız girişi süsler. SMIL çalışmazsa şema yine doğru okunur.
        o.append(f'<rect x="{bx}" y="{y+5}" width="{max(gen,3)}" height="16" rx="8" fill="{renk}">'
                 f'<animate attributeName="width" values="0;{max(gen,3)}" dur="0.9s" '
                 f'begin="{gec}s" fill="freeze" calcMode="spline" '
                 f'keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/></rect>')
        # akan sinyal: şeridin gerçekten çalıştığını gösterir
        if gen > 24:
            o.append(f'<circle r="3.2" fill="{renk}" opacity="0">'
                     f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.8;1" '
                     f'dur="2.6s" begin="{1 + gec}s" repeatCount="indefinite"/>'
                     f'<animateMotion dur="2.6s" begin="{1 + gec}s" repeatCount="indefinite" '
                     f'path="M{bx + 6},{y + 13} L{bx + gen - 6},{y + 13}"/></circle>')
        o.append(f'<text x="{bx + max(gen,3) + 10}" y="{y+18}" font-size="12" font-weight="700" '
                 f'fill="{t["fg"]}" class="m">{n}</text>')
        y += 42

    o.append(f'<text x="0" y="{H-8}" font-size="10" fill="{t["mut"]}" class="m">'
             f'A yalnız 2 hizmet taşır — ağırlık merkezi uzaktan ayar (B) ve insan işi (F) tarafında</text>')
    o.append("</svg>")
    return "\n".join(o)


# ── 2) Kod haritası ──────────────────────────────────────────────────────────
COMP = [
    ("n8n",      "1 · Orkestratör", "orchestrator/", "#DB2777"),
    ("platform", "2 · HR Platformu", "platform/",    "#D08700"),
    ("relay",    "3 · Site Relay",   "relay/",       "#8B5CF6"),
    ("human",    "4 · İnsan",        "human/",       "#6B7280"),
    ("agent",    "5 · Uç Nokta Ajanı", "agent/",     "#2F6FED"),
]


def kod_haritasi(tema: str) -> str:
    t = TEMA[tema]
    W, H = 880, 300
    o = _bas(W, H, tema, "Beş bileşenin kod topolojisi ve aralarındaki akış")
    o.append(f'<text x="0" y="16" font-size="13" font-weight="600" fill="{t["fg"]}">'
             f'Beş bileşen</text>')
    o.append(f'<text x="0" y="34" font-size="11" fill="{t["mut"]}" class="m">'
             f'depoda {codemap["total_tracked"]} dosya · haritada {len(codemap["files"])} tanesi açılabilir</text>')

    yer = {"n8n": (0, 58), "platform": (0, 130), "relay": (326, 130),
           "agent": (652, 130), "human": (326, 224)}
    gen = {"n8n": 284, "platform": 284, "relay": 284, "agent": 228, "human": 284}
    for i, (k, ad, klasor, renk) in enumerate(COMP):
        x, y = yer[k]; w = gen[k]; n = bilesen.get(k, 0)
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="52" rx="8" fill="{t["kart"]}" '
                 f'stroke="{renk}" stroke-width="1.6"/>')
        o.append(f'<rect x="{x}" y="{y}" width="4" height="52" rx="2" fill="{renk}"/>')
        o.append(f'<text x="{x+16}" y="{y+22}" font-size="12.5" font-weight="600" fill="{t["fg"]}">{ad}</text>')
        o.append(f'<text x="{x+16}" y="{y+39}" font-size="10.5" fill="{t["mut"]}" class="m">{klasor}</text>')
        o.append(f'<text x="{x+w-14}" y="{y+32}" font-size="12" font-weight="700" fill="{renk}" '
                 f'text-anchor="end" class="m">{n}</text>')

    def ok(d, renk, dur, begin, etiket=None, ex=0, ey=0):
        o.append(f'<path d="{d}" fill="none" stroke="{renk}" stroke-width="1.8" opacity=".55"/>')
        o.append(f'<circle r="3.6" fill="{renk}" opacity="0">'
                 f'<animateMotion dur="{dur}" begin="{begin}" repeatCount="indefinite" path="{d}"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.12;.85;1" '
                 f'dur="{dur}" begin="{begin}" repeatCount="indefinite"/></circle>')
        if etiket:
            o.append(f'<text x="{ex}" y="{ey}" font-size="9.5" fill="{t["mut"]}" class="m" text-anchor="middle">{etiket}</text>')

    ok("M142,110 L142,130", "#DB2777", "1.6s", "0s")
    ok("M284,156 L326,156", "#D08700", "2s", "0.3s", "görev", 305, 148)
    ok("M610,156 L652,156", "#8B5CF6", "2s", "0.9s", "kuyruk", 631, 148)
    ok("M468,182 L468,224", "#6B7280", "2.2s", "1.4s", "iş emri", 476, 207)

    o.append(f'<text x="0" y="{H-8}" font-size="10" fill="{t["mut"]}" class="m">'
             f'ok yönü iş akışıdır; ağ bağlantısı her zaman içeriden dışarı kurulur</text>')
    o.append("</svg>")
    return "\n".join(o)


# ── 3) Emülasyon topolojisi ──────────────────────────────────────────────────
BACAK = [
    ("1", "hr-core",   "10.10.0.0/24",    "#D08700", 0,   200, "HR kontrol düzlemi"),
    ("2", "wan",       "100.64.0.0/30",   "#0F9B8E", 216, 118, "WAN geçişi"),
    ("3", "cust-dmz",  "172.31.0.0/29",   "#DB2777", 350, 118, "güvenlik duvarı"),
    ("4", "cust-mgmt", "192.168.10.0/24", "#8B5CF6", 484, 190, "yönetim VLAN'ı"),
    ("5", "cust-srv",  "192.168.20.0/24", "#2F6FED", 690, 90,  "sunucu VLAN'ı"),
    ("6", "cust-usr",  "192.168.30.0/24", "#16A34A", 690, 90,  "kullanıcı VLAN'ı"),
]


def topoloji(tema: str) -> str:
    t = TEMA[tema]
    W, H = 880, 280
    o = _bas(W, H, tema, "Emülasyon topolojisi: altı ağ bacağı")
    o.append(f'<text x="0" y="16" font-size="13" font-weight="600" fill="{t["fg"]}">'
             f'Emüle edilen altı ağ bacağı</text>')
    o.append(f'<text x="0" y="34" font-size="11" fill="{t["mut"]}" class="m">'
             f'19 düğüm · 18 sanal kablo · 33 kontrolün 33\'ü geçti</text>')

    ust = [BACAK[0], BACAK[1], BACAK[2], BACAK[3]]
    x = 0; y = 52
    kutu = {}
    for no, ad, blok, renk, gx, gw, aciklama in ust:
        o.append(f'<rect x="{x}" y="{y}" width="{gw}" height="74" rx="8" fill="{t["kart"]}" '
                 f'stroke="{renk}" stroke-width="1.6" stroke-dasharray="5 4"/>')
        o.append(f'<text x="{x+12}" y="{y+19}" font-size="9.5" fill="{renk}" class="m" '
                 f'letter-spacing="1">BACAK {no}</text>')
        o.append(f'<text x="{x+12}" y="{y+38}" font-size="12" font-weight="600" fill="{t["fg"]}" '
                 f'class="m">{ad}</text>')
        o.append(f'<text x="{x+12}" y="{y+54}" font-size="10" fill="{t["mut"]}" class="m">{blok}</text>')
        o.append(f'<text x="{x+12}" y="{y+68}" font-size="9.5" fill="{t["mut"]}">{aciklama}</text>')
        kutu[ad] = (x, gw)
        x += gw + 18

    y2 = 152
    for no, ad, blok, renk, _, _, aciklama in (BACAK[4], BACAK[5]):
        gx = 466 if no == "5" else 672
        o.append(f'<rect x="{gx}" y="{y2}" width="190" height="74" rx="8" fill="{t["kart"]}" '
                 f'stroke="{renk}" stroke-width="1.6" stroke-dasharray="5 4"/>')
        o.append(f'<text x="{gx+12}" y="{y2+19}" font-size="9.5" fill="{renk}" class="m" '
                 f'letter-spacing="1">BACAK {no}</text>')
        o.append(f'<text x="{gx+12}" y="{y2+38}" font-size="12" font-weight="600" fill="{t["fg"]}" '
                 f'class="m">{ad}</text>')
        o.append(f'<text x="{gx+12}" y="{y2+54}" font-size="10" fill="{t["mut"]}" class="m">{blok}</text>')
        o.append(f'<text x="{gx+12}" y="{y2+68}" font-size="9.5" fill="{t["mut"]}">{aciklama}</text>')

    def akis(d, renk, dur, begin):
        o.append(f'<path d="{d}" fill="none" stroke="{renk}" stroke-width="1.6" opacity=".5"/>')
        o.append(f'<circle r="3.4" fill="{renk}" opacity="0">'
                 f'<animateMotion dur="{dur}" begin="{begin}" repeatCount="indefinite" path="{d}"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.12;.85;1" '
                 f'dur="{dur}" begin="{begin}" repeatCount="indefinite"/></circle>')

    akis("M200,89 L216,89", "#0F9B8E", "1.4s", "0s")
    akis("M334,89 L350,89", "#0F9B8E", "1.4s", "0.4s")
    akis("M468,89 L484,89", "#DB2777", "1.4s", "0.8s")
    akis("M561,126 L561,152", "#2F6FED", "1.6s", "1.2s")
    akis("M620,126 L767,152", "#16A34A", "1.8s", "1.5s")

    o.append(f'<text x="0" y="{H-8}" font-size="10" fill="{t["mut"]}" class="m">'
             f'VLAN\'lar ayrı yayın alanı: aynı VLAN TTL 64 · farklı VLAN 63 · WAN ötesi 61</text>')
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    uretilen = 0
    for ad, fn in (("seritler", seritler), ("kod-haritasi", kod_haritasi), ("topoloji", topoloji)):
        for tema in ("light", "dark"):
            (HERE / f"{ad}-{tema}.svg").write_text(fn(tema), encoding="utf-8")
            uretilen += 1
    print(f"{uretilen} SVG üretildi · şerit {dict(sorted(serit.items()))} · bileşen {dict(bilesen)}")
