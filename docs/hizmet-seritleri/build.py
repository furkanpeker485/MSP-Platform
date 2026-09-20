#!/usr/bin/env python3
"""Hizmet Şeritleri belgesinin baskı kaynağını data.json'dan yeniden üretir.

    python3 docs/hizmet-seritleri/build.py

Çıktı: baski-kaynagi.html — PDF bundan basılır (bkz. docs/README.md).
"""
# -*- coding: utf-8 -*-
import json, html, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sp = str(HERE)
d=json.load(open(sp+'/data.json',encoding='utf-8')); items=d['items']; c=d['critique']
L={'A':('Aracı yazılım (agent)','#2F6FED','Bilgisayara kurulan program, ayarını merkezden çeker'),
   'B':('Uzaktan ayar basma (Ansible)','#7A4CD0','Üzerine program kurulamayan cihazlara uzaktan bağlanıp ayar yazma'),
   'C':('Sağlayıcı sistemleri (API)','#0C8F84','Ayar müşteride değil, Amazon/Microsoft/HRC gibi sağlayıcıda'),
   'D':('Kendi sistemlerinizde kurulum','#AD6A0C','İzleme, envanter, destek kuyruğu ve raporların sizde oluşturulması'),
   'E':('Takvimli tekrar eden işler (n8n)','#B93B74','Aylık rapor, yedek testi, tarama — kendi takviminde çalışır'),
   'F':('İnsan işi','#657279','Sahaya giden teknisyen, nöbetçi ekip, danışman')}
ORDER=list('ABCDEF'); GR={'FULL':'İNSANSIZ','ASSISTED':'ONAY GEREKİR','HUMAN':'İNSAN İŞİ'}
e=lambda s: html.escape(str(s))
n=len(items); lc={k:sum(1 for x in items if x['primary_lane']==k) for k in ORDER}; gc=c['grade_counts']
areas=[]; [areas.append(x['area']) for x in items if x['area'] not in areas]

def flow_svg(f,hex):
    if not f or len(f)!=5: return ''
    N=[f[0],f[2],f[4]]; E=[f[1],f[3]]
    X=[2,218,434]; W=168; AR=[(174,212),(390,428)]
    o=[]
    for k,(a,b) in enumerate(AR):
        o.append(f'<line x1="{a}" y1="35" x2="{b-6}" y2="35" stroke="#8A9A9E" stroke-width="1.2"/>')
        o.append(f'<polygon points="{b-6},31.5 {b},35 {b-6},38.5" fill="#8A9A9E"/>')
        o.append(f'<text x="{(a+b)/2}" y="12" text-anchor="middle" class="fe">{e(E[k])}</text>')
    for i in range(3):
        mid=f' style="stroke:{hex};stroke-width:1.6"' if i==1 else ''
        cls=' ft-mid' if i==1 else ''
        o.append(f'<rect x="{X[i]}" y="20" width="{W}" height="30" rx="5" fill="#F2F5F5" stroke="#C2CFCF" stroke-width="1"{mid}/>')
        o.append(f'<text x="{X[i]+W/2}" y="39" text-anchor="middle" class="ft{cls}">{e(N[i])}</text>')
    return '<svg class="flow" viewBox="0 0 604 58">'+''.join(o)+'</svg>'

def lane_block(k):
    mine=[x for x in items if x['primary_lane']==k]; nm,col,ex=L[k]
    s=f'<section class="lane-sec"><div class="lane-head" style="border-left-color:{col}">'
    s+=f'<div class="lh-code" style="background:{col}">{k}</div><div><h3>{k} şeridi — {e(nm)}</h3><p class="lh-ex">{e(ex)} · <b>{len(mine)} hizmet</b></p></div></div>'
    for x in mine:
        also=[l for l in x['all_lanes'] if l!=k]
        extra=' · ayrıca '+', '.join(also)+' şeridi' if also else ''
        tier="Proje bazlı" if x['tier']=="Proje" else e(x['tier'])
        s+=f'''<article class="svc">
  <div class="svc-h"><h4>{e(x['name'])}</h4>
    <span class="meta">{e(x['area'])} · {tier} · <span class="gr gr-{x['automation_grade']}">{GR[x['automation_grade']]}</span>{extra}</span></div>
  <p class="plain">{e(x['plain'])}</p>
  <p class="ex"><b>Bu işi kim yapıyor?</b> {e(x['executor'])}</p>
  {flow_svg(x.get('flow'), col)}
  <div class="cols">
    <div><h5>İlk gün çalıştırılan adımlar — teknik detay</h5><ul>{''.join(f'<li>{e(t)}</li>' for t in x['day0_tasks'])}</ul></div>
    <div><h5>Müşteriden gereken yetki</h5><p>{e(x['credential_needed'])}</p>
         <h5>Çalıştığı nasıl kanıtlanıyor</h5><p>{e(x['health_check'])}</p></div>
  </div>
  <p class="go"><b>Dikkat.</b> {e(x['gotcha'])}</p>
</article>'''
    return s+'</section>'

def pc_list(arr):
    out=[]
    for o in arr:
        pr = o if isinstance(o,str) else o.get('p','')
        so = '' if isinstance(o,str) else o.get('c','')
        blk=f'<div class="pc"><p class="pc-p">{e(pr)}</p>'
        if so: blk+=f'<p class="pc-c"><b>Çözüm</b>{e(so)}</p>'
        out.append(blk+'</div>')
    return ''.join(out)

ROADMAP_SVG = open(HERE/"assets/roadmap.svg", encoding="utf-8").read()
ACCESS_SVG  = open(HERE/"assets/access.svg", encoding="utf-8").read()

bar=''.join(f'<span style="flex:{lc[k]};background:{L[k][1]}"><i>{k}</i>{lc[k]}</span>' for k in ORDER if lc[k])
glos=''.join(f'<div class="gl"><b>{e(a)}</b><span>{e(b)}</span></div>' for a,b in d['glossary'])
CSS = open(HERE/"assets/print.css", encoding="utf-8").read()

doc=f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>Hisar Hizmet Şeritleri</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>{CSS}</style></head><body>
<div class="cover">
 <div>
  <p class="eyebrow">Hisar Research · Hizmet Teslim Mimarisi</p>
  <h1>Altı şerit, tek katalog, sahada kimse yok.</h1>
  <p class="lead">Hisar Research'ün sattığı her hizmeti, müşterinin sistemleri üzerinde birilerinin kurması gerekir. Bu rapor kataloğunuzda şu an yayında olan {n} hizmetin tamamını, o işi fiilen yapan şeye eşliyor — ve çalışanların bilgisayarına kurulan aracı yazılımın (agent) tek başına neden bunların yalnızca ikisini teslim edebildiğini gösteriyor.</p>
  <p class="lead" style="font-size:9pt;color:#5E7075;margin-top:3mm">Her hizmetin altında, o işin hangi adımlardan geçtiğini gösteren bir akış şeması var. Teknik terimlerin günlük Türkçe karşılıkları raporun sonundaki sözlükte.</p>
  <div class="facts">
   <div><b>{n}</b><span>yayındaki hizmet</span></div><div><b>{len(areas)}</b><span>çözüm alanı</span></div>
   <div><b>6</b><span>yürütme şeridi</span></div><div><b>%{round(gc['FULL']/n*100)}</b><span>hiç insan gerekmeyen</span></div>
  </div>
 </div>
 <div>
  <h2>Ağırlık merkezi nerede, yatırım nereye</h2>
  <p class="sub">Yayındaki her hizmete tek tek "bu işi fiilen kim yapacak?" diye sorduğunuzda katalog şöyle bölünüyor.</p>
  <div class="bar">{bar}</div>
  <p class="barcap">A şeridi {n} hizmetin yalnızca {lc['A']} tanesini taşıyor: Windows ve Linux Server Yönetimi. Kataloğun ağırlık merkezi, uzaktan ayar basılan cihazlar (B) ve insan işleri (F) tarafında.</p>
  <div class="callout"><h3>Aracı yazılım fikri yanlış değil, kapsamı yanlış anlaşıldı</h3>
  <p>Paket karşılaştırma tablosundaki 83 satır (yama yönetimi, antivirüs, uç nokta güvenliği, bilgisayar envanteri…) aracı yazılımı çok daha büyük gösteriyor; ama bunların hiçbiri şu an yayında bir hizmet değil. Aracı yazılım, bugün sattığınızın değil, satmayı planladığınızın altyapısı.</p></div>
 </div>
 <p class="foot">Kapsam: pre-sales.hisarresearch.com/services üzerinde yayında olan {len(areas)} çözüm alanındaki {n} hizmet. Paket karşılaştırma tablosundaki, henüz yayında hizmet olarak bulunmayan özellik satırları ve Microsoft 365 Management kapsam dışıdır.</p>
</div>
<h2>Altı şerit</h2>
<p class="sub">Katalogdaki bir hizmet tek bir işlem değil, bir görev listesidir ve bu görevlerin her biri farklı bir şeride düşer. Müşteri tek bir kutucuğu işaretler; arka planda aşağıdakilerin hepsi çalışır.</p>
{''.join(lane_block(k) for k in ORDER if lc[k])}
<section style="page-break-before:always">
<h2>Çözüm sırası</h2>
<p class="sub">Otuz dokuz hizmeti aynı anda kurmaya çalışmak, hiçbirini bitirememenin en hızlı yolu. Sıralama kataloğun kendi ağırlığından çıkıyor: önce her şeyin dayandığı omurga, sonra en çok hizmet taşıyan şerit, en son insan işlerinin devri. Her aşama, bir öncekinin sağlık kontrolü yeşile döndüğünde başlar.</p>
{ROADMAP_SVG}
</section>
<section style="page-break-before:always">
<h2>İlk gün: erişimleri tek seferde toplamak</h2>
<p class="sub">Devreye almanın hızını, üzerine program kurulamayan her şeyin şifrelerinin ve binanın kapısının size ne zaman açıldığı belirler. Bunu kovalanacak bir iş olmaktan çıkarmanın yolu, erişim listesini müşterinin aldığı paketten otomatik üretip tek formda toplamak: aşağıdaki akış bunu yapar, ardından gelen liste de o formun içeriğidir.</p>
{ACCESS_SVG}
<ol class="creds">{''.join(f'<li>{e(x)}</li>' for x in c['day0_credentials'])}</ol>
</section>
<section style="page-break-before:always">
<h2>Zor kalemler ve çözümleri</h2>
<p class="sub">Her maddenin altında ne yapılacağı yazıyor. Önce otomasyona direnen dokuz hizmet, sonra tek tek bakınca görünmeyip bütüne bakınca ortaya çıkan on iki eksik — hepsi kapatılabilir işlere çevrildi.</p>
<h3 class="grp">Otomasyona direnen dokuz hizmet</h3>
{pc_list(c['hardest_to_automate'])}
<h3 class="grp" style="page-break-before:always">Bütünde görünen on iki eksik</h3>
{pc_list(c['cross_cutting_gaps'])}
</section>
<section style="page-break-before:always">
<h2>Tek kural ve nereden başlamalı</h2>
<div class="callout"><h3>Tek katalog, iki yüz</h3>
<p>Sitedeki her hizmetin bir kimlik numarası olmalı ve otomasyon sisteminiz aynı numarayı kullanmalı. “Firewall Management” sitede bir pazarlama başlığı, otomasyonda bambaşka bir isim olarak durduğu anda satılan ile teslim edilen birbirinden ayrışır. Bu tür platformları teknoloji değil, tam olarak bu ayrışma batırır. Satış yüzü sitede durur, teslim yüzü otomasyonda: görev listesi, o işi yapan şerit, gereken şifreler, sağlık kontrolü. Aynı kaydın iki yüzü, kimlik numarasıyla birbirine bağlı.</p></div>
<h3 style="margin:6mm 0 2mm;font-size:11.5pt">Önce tek bir hizmeti uçtan uca kurun</h3>
<p style="font-size:8.8pt;color:#37474A;margin:0">{e(c['first_service_to_build'])}</p>
</section>
<section style="page-break-before:always">
<h2>Sözlük</h2>
<p class="sub">Bu raporda geçen kısaltmaların ve yabancı kökenli terimlerin günlük Türkçe karşılıkları. Ürün adları (Zabbix, Ansible, Veeam gibi) marka olduğu için çevrilmemiştir.</p>
<div class="glos">{glos}</div>
<p class="foot">Şerit atamaları bir tasarım önerisidir, üretici taahhüdü değildir. Hizmet adları, kategoriler ve paket içerikleri pre-sales.hisarresearch.com üzerinden okunmuştur.</p>
</section>
</body></html>'''
open(HERE/"baski-kaynagi.html", "w", encoding="utf-8").write(doc)
print('baskı sürümü:',len(doc),'bayt | şema:',doc.count('class="flow"'))
