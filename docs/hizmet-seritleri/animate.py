#!/usr/bin/env python3
"""Hizmet Şeritleri haritasının hareketli sürümünü üretir.

    python3 docs/hizmet-seritleri/animate.py

Girdi: hizmet-seritleri.html · Çıktı: hizmet-seritleri-animasyonlu.html
"""
# -*- coding: utf-8 -*-
from pathlib import Path

HERE = Path(__file__).resolve().parent
h=open(HERE/"hizmet-seritleri.html", encoding="utf-8").read()
h=h.replace('<title>Hisar Hizmet Şeritleri</title>','<title>Hisar Şerit Akışı</title>',1)
ANIM='''
/* ---- hareket katmanı ---- */
@keyframes barIn{from{flex-grow:.0001}}
@keyframes riseIn{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
/* şeritler: opaklık YOK — animasyon hiç çalışmasa bile kart görünür kalır */
@keyframes laneIn{from{transform:translateY(14px)}to{transform:none}}
@keyframes railPulse{0%,100%{box-shadow:inset 0 0 0 0 rgba(255,255,255,0)}50%{box-shadow:inset 0 0 0 2px rgba(255,255,255,.35)}}
@keyframes dashFlow{to{stroke-dashoffset:-18}}
@keyframes cursorBlink{0%,100%{opacity:1}50%{opacity:0}}
.dist-bar.intro .dist-seg{animation:barIn .9s cubic-bezier(.22,.8,.25,1) both}
.dist-bar.intro .dist-seg:nth-child(1){animation-delay:.05s}
.dist-bar.intro .dist-seg:nth-child(2){animation-delay:.13s}
.dist-bar.intro .dist-seg:nth-child(3){animation-delay:.21s}
.dist-bar.intro .dist-seg:nth-child(4){animation-delay:.29s}
.dist-bar.intro .dist-seg:nth-child(5){animation-delay:.37s}
.dist-bar.intro .dist-seg:nth-child(6){animation-delay:.45s}
.dist-seg{transition:flex-grow .5s cubic-bezier(.22,.8,.25,1), filter .2s}
.dist-seg:hover{filter:brightness(1.12)}
html.anim .hero h1,html.anim .hero .lead,html.anim .facts{animation:riseIn .75s cubic-bezier(.22,.8,.25,1) both}
html.anim .hero h1{animation-delay:.06s}
html.anim .hero .lead{animation-delay:.16s}
html.anim .facts{animation-delay:.26s}
html.anim .reveal{opacity:0;transform:translateY(18px)}
html.anim .reveal.in{opacity:1;transform:none;transition:opacity .65s cubic-bezier(.22,.8,.25,1),transform .65s cubic-bezier(.22,.8,.25,1)}
html.anim #board .lane{animation:laneIn .5s cubic-bezier(.22,.8,.25,1) both}
html.anim #board .lane:nth-child(1){animation-delay:.03s}
html.anim #board .lane:nth-child(2){animation-delay:.10s}
html.anim #board .lane:nth-child(3){animation-delay:.17s}
html.anim #board .lane:nth-child(4){animation-delay:.24s}
html.anim #board .lane:nth-child(5){animation-delay:.31s}
html.anim #board .lane:nth-child(6){animation-delay:.38s}
.lane{transition:box-shadow .25s,transform .25s}
.lane:hover{transform:translateX(3px);box-shadow:0 2px 4px rgba(15,23,24,.06),0 14px 34px -18px rgba(15,23,24,.3)}
.lane:hover .lane-rail{animation:railPulse 1.6s ease-in-out infinite}
.chip{transition:background .18s,border-color .18s,transform .18s}
.chip:hover{transform:translateY(-1px);background:var(--surface-3)}
tbody tr.row{transition:background .15s}
.lanepill{transition:transform .18s}
tbody tr.row:hover .lanepill{transform:scale(1.08)}
.task{animation:laneIn .45s cubic-bezier(.22,.8,.25,1) both}
.cred{transition:transform .2s,border-left-width .2s}
.cred:hover{transform:translateX(3px);border-left-width:4px}
.tool,.gl{transition:transform .25s,box-shadow .25s,background .2s}
.tool:hover{transform:translateY(-3px);box-shadow:0 2px 4px rgba(15,23,24,.06),0 16px 36px -20px rgba(15,23,24,.35)}
.gl:hover{background:var(--surface-2)}
.flowdot{filter:drop-shadow(0 0 3px currentColor)}
.dashflow{animation:dashFlow 1.1s linear infinite}
.tally::after{content:"_";animation:cursorBlink 1.1s step-end infinite;margin-left:1px}
@media (prefers-reduced-motion:reduce){
  html.anim .reveal{opacity:1!important;transform:none!important}
  html.anim #board .lane{animation:none!important;opacity:1!important;transform:none!important}
  .dist-bar.intro .dist-seg,html.anim .hero h1,html.anim .hero .lead,html.anim .facts,.task{animation:none!important;opacity:1!important;transform:none!important}
  .dashflow,.tally::after{animation:none!important}
  circle.flowdot{display:none}
}
'''
h=h.replace('@media (max-width:760px){', ANIM+'\n@media (max-width:760px){',1)
a1='<line x1="143" y1="248" x2="143" y2="316" stroke="currentColor" stroke-width="1.6" marker-end="url(#ar)"/>'
f1=a1+'''
        <g>
          <circle class="flowdot" r="4.5" fill="#0B6970" color="#0B6970">
            <animateMotion dur="1.9s" repeatCount="indefinite" path="M484,226 L484,152"/>
            <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.8;1" dur="1.9s" repeatCount="indefinite"/>
          </circle>
          <circle class="flowdot" r="4.5" fill="#0B6970" color="#0B6970">
            <animateMotion dur="1.9s" begin="0.95s" repeatCount="indefinite" path="M378,100 L276,139"/>
            <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.8;1" dur="1.9s" begin="0.95s" repeatCount="indefinite"/>
          </circle>
          <circle class="flowdot" r="4" fill="currentColor">
            <animateMotion dur="2.6s" begin="0.4s" repeatCount="indefinite" path="M610,110 C690,110 700,170 726,218"/>
            <animate attributeName="opacity" values="0;.9;.9;0" keyTimes="0;0.15;0.8;1" dur="2.6s" begin="0.4s" repeatCount="indefinite"/>
          </circle>
          <circle class="flowdot" r="4" fill="currentColor">
            <animateMotion dur="2.6s" begin="1.6s" repeatCount="indefinite" path="M143,250 L143,314"/>
            <animate attributeName="opacity" values="0;.9;.9;0" keyTimes="0;0.15;0.8;1" dur="2.6s" begin="1.6s" repeatCount="indefinite"/>
          </circle>
        </g>'''
assert a1 in h; h=h.replace(a1,f1,1)
a2='<path d="M576,294 L576,258" fill="none" stroke="#0B6970" stroke-width="1.4"/>'
f2=a2+'''
        </g>
        <g>
          <circle class="flowdot" r="4.5" fill="#0B6970" color="#0B6970">
            <animateMotion dur="5.6s" repeatCount="indefinite"
              path="M20,60 L806,60 L747,60 L747,116 L60,116 L60,140 L60,206 L824,229 L866,229 L866,14 L577,14 L577,32"
              keyPoints="0;0.34;0.42;0.5;0.62;0.68;0.78;0.9;1" keyTimes="0;0.3;0.38;0.46;0.6;0.68;0.8;0.92;1" calcMode="linear"/>
            <animate attributeName="opacity" values="0;1;1;1;0" keyTimes="0;0.06;0.75;0.95;1" dur="5.6s" repeatCount="indefinite"/>
          </circle>
        </g>
        <g>'''
assert a2 in h; h=h.replace(a2,f2,1)
h=h.replace('<path d="M824,229 L866,229 L866,14 L577,14 L577,30" fill="none" stroke="#0B6970" stroke-width="1.6" stroke-dasharray="5 4"',
            '<path class="dashflow" d="M824,229 L866,229 L866,14 L577,14 L577,30" fill="none" stroke="#0B6970" stroke-width="1.6" stroke-dasharray="5 4"',1)
JS='''
(function(){
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.documentElement.classList.add('anim');
  const rev=[...document.querySelectorAll('section > .sec-head, section > .sec-sub, figure, .decomp, .tbl-wrap, .creds, .tools, .callout, .gaps, .glos, #dist .prose, #decompose .prose, #bootstrap .prose, #start .prose')];
  rev.forEach(el=>el.classList.add('reveal'));
  const showAll=()=>{rev.forEach(el=>el.classList.add('in'));};
  if(reduce){showAll();}
  else{
    const io=new IntersectionObserver((es,o)=>{es.forEach(en=>{if(en.isIntersecting){en.target.classList.add('in');o.unobserve(en.target);}});},{rootMargin:'0px 0px -8% 0px',threshold:.06});
    rev.forEach(el=>io.observe(el));
    setTimeout(showAll,2200);
  }
  if(!reduce){
    document.querySelectorAll('.fact b').forEach((el,i)=>{
      const m=el.textContent.trim().match(/^(%?)(\\d+)$/); if(!m) return;
      const pre=m[1],end=+m[2],dur=900+i*90; let t0=null; el.textContent=pre+'0';
      const step=(t)=>{if(!t0)t0=t;const p=Math.min(1,(t-t0)/dur);
        el.textContent=pre+Math.round(end*(1-Math.pow(1-p,3))); if(p<1)requestAnimationFrame(step);};
      setTimeout(()=>requestAnimationFrame(step),260+i*90);
    });
  }
})();
'''
h=h.replace('renderStatic();\nrenderAll();','renderStatic();\nrenderAll();\n'+JS+
  "\n(function(){var b=document.getElementById('distBar'); if(b){b.classList.add('intro'); setTimeout(()=>b.classList.remove('intro'),1400);}})();",1)
h=h.replace("(ex.day0_tasks||[]).map(t=>{","(ex.day0_tasks||[]).map((t,i)=>{",1)
h=h.replace("return `<div class=\"task\"><span class=\"lm\"","return `<div class=\"task\" style=\"animation-delay:${0.06*i+0.1}s\"><span class=\"lm\"",1)
h=h.replace("`<div class=\"task\" style=\"border-top:1px solid var(--rule);margin-top:6px;padding-top:12px\">",
            "`<div class=\"task\" style=\"border-top:1px solid var(--rule);margin-top:6px;padding-top:12px;animation-delay:.6s\">",1)
open(HERE/"hizmet-seritleri-animasyonlu.html", "w", encoding="utf-8").write(h)
print('animasyonlu sürüm yenilendi:',len(h),'bayt')
