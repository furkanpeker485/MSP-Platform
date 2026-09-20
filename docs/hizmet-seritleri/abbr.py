# -*- coding: utf-8 -*-
import re
M={
"HR":"Hisar Research","HRC":"Hisar Research'ün kendi bulutu","API":"uygulama arayüzü",
"REST":"web tabanlı arayüz","SDK":"geliştirici kütüphanesi","VM":"sanal makine","DB":"veritabanı",
"SSH":"şifreli uzaktan bağlantı","WinRM":"Windows uzaktan yönetim","CLI":"komut satırı",
"NETCONF":"ağ cihazı yapılandırma protokolü","SIEM":"güvenlik kayıt merkezi",
"SLA":"hizmet seviyesi taahhüdü","RPO":"kabul edilebilir veri kaybı","RTO":"ayağa kalkma süresi",
"AD":"Active Directory kullanıcı sistemi","DC":"etki alanı denetleyicisi","OU":"kullanıcı klasörü",
"GPO":"merkezî Windows kuralı","GPP":"grup ilkesi tercihleri","SYSVOL":"etki alanı ortak klasörü",
"FSMO":"Active Directory özel rolleri","DFSR":"klasör çoğaltma servisi","DnsAdmins":"DNS yönetici grubu",
"AWS":"Amazon'un bulut platformu","IAM":"AWS yetki sistemi","ARN":"AWS kaynak kimliği",
"EC2":"AWS sanal sunucusu","EIP":"AWS sabit adresi","SSM":"AWS sistem yöneticisi","VPC":"bulut özel ağı",
"CUR":"AWS maliyet raporu","RI":"AWS rezerve kapasitesi","ARM":"Azure kaynak yönetimi",
"SPN":"Azure uygulama hesabı","AzSHCI":"Microsoft'un yerel bulut ürünü","IaaS":"hizmet olarak altyapı",
"SaaS":"hizmet olarak yazılım","FinOps":"bulut maliyet yönetimi",
"SNMPv3":"cihaz izleme protokolünün şifreli sürümü","SNMP":"cihaz izleme protokolü",
"LLDP":"komşu cihaz keşfi","LLD":"otomatik bileşen keşfi","OID":"izleme değeri numarası",
"NVPS":"saniyedeki izleme değeri","ICMP":"ping protokolü","NTP":"saat eşitleme",
"VLAN":"sanal ağ bölmesi","LAN":"yerel ağ","WAN":"internet hattı","NAT":"adres dönüştürme",
"BGP":"yönlendirme protokolü","STP":"ağ döngü koruması","PoE":"kablodan elektrik besleme",
"AAA":"kimlik doğrulama ve yetkilendirme","ACL":"erişim izin listesi","IP":"ağ adresi",
"IPAM":"ağ adres yönetimi","MAC":"ağ kartı kimliği","MTU":"paket boyutu","MSS":"paket boyutu sınırı",
"TCP":"bağlantı protokolü","HTTP":"web protokolü","TTL":"önbellek süresi","VIP":"sanal adres",
"DNS":"alan adı çözümleme","DHCP":"otomatik adres dağıtımı","DHCPDISCOVER":"adres isteği paketi",
"ISC":"açık kaynak DHCP yazılımı","MX":"e-posta yönlendirme kaydı","NS":"alan adı sunucusu kaydı",
"SOA":"alan adı ana kaydı","NXDOMAIN":"bulunamayan alan adı","SPF":"e-posta gönderici doğrulama",
"DKIM":"e-posta imzası","DMARC":"e-posta sahtecilik koruması",
"VPN":"şifreli uzaktan bağlantı","IPsec":"şifreli tünel protokolü","IKEv2":"tünel kurulum protokolü",
"SSL":"şifreli bağlantı","TLS":"şifreli bağlantı","SA":"tünel güvenlik ilişkisi",
"MFA":"çok adımlı doğrulama","RADIUS":"merkezî giriş doğrulama","NPS":"Windows giriş doğrulama sunucusu",
"LDAPS":"şifreli dizin sorgulama","LDAP":"dizin sorgulama","PKI":"sertifika altyapısı",
"SCEP":"otomatik sertifika dağıtımı","CA":"sertifika otoritesi","SSO":"tek oturum açma",
"SSID":"kablosuz ağ adı","PSK":"ortak kablosuz şifre","AP":"kablosuz erişim noktası",
"WLC":"kablosuz ağ kontrolcüsü","RF":"radyo frekansı","IoT":"internete bağlı cihazlar",
"HA":"yedekli çalışma","PSU":"güç kaynağı","RAID":"yedekli disk dizisi","RAM":"bellek","CPU":"işlemci",
"IOPS":"saniyedeki disk işlemi","BIOS":"anakart temel yazılımı","SMBIOS":"donanım kimlik bilgisi",
"UUID":"benzersiz kimlik","BMC":"sunucu uzaktan yönetim kartı","IPMI":"sunucu uzaktan yönetim protokolü",
"UPS":"kesintisiz güç kaynağı","OT":"endüstriyel kontrol cihazları","MFP":"çok fonksiyonlu yazıcı",
"CPE":"operatörün müşterideki cihazı","ISP":"internet servis sağlayıcısı","LTE":"mobil internet",
"VoIP":"internet üzerinden telefon","DID":"telefon numarası hattı","IVR":"sesli yanıt menüsü",
"OS":"işletim sistemi","MSI":"Windows kurulum paketi","DSC":"Windows ayar yönetimi",
"PsExec":"uzaktan komut çalıştırma aracı","NOPASSWD":"parolasız yetki","RDP":"uzak masaüstü protokolü",
"RD":"uzak masaüstü","RDS":"uzak masaüstü hizmetleri","NLA":"ağ seviyesinde kimlik doğrulama",
"IIS":"Windows web sunucusu","SMB":"Windows dosya paylaşımı","SMBv1":"eski dosya paylaşım sürümü",
"NTFS":"Windows dosya izinleri","DFS":"dağıtık dosya paylaşımı","VSS":"Windows anlık kopya",
"FSRM":"dosya sunucusu kota yöneticisi","OOM":"bellek yetersizliği","XFS":"Linux dosya sistemi",
"SQL":"veritabanı sorgu dili","MSSQL":"Microsoft SQL Server","ODBC":"veritabanı bağlantı arayüzü",
"DBCC":"SQL Server bakım komutu","LSN":"veritabanı kayıt sırası","RMAN":"Oracle yedekleme aracı",
"SAP":"kurumsal yazılım","HANA":"SAP veritabanı","REPLICATION":"çoğaltma yetkisi",
"ESXi":"VMware sanallaştırma işletim sistemi","VMFS":"VMware dosya sistemi","VMDK":"sanal disk dosyası",
"DRS":"kaynak dengeleme","SCVMM":"Microsoft sanal makine yöneticisi","PVE":"Proxmox sanallaştırma",
"CBT":"değişen blok takibi","GFS":"uzun vadeli yedek saklama düzeni","SOBR":"Veeam birleşik deposu",
"CMDB":"merkezî envanter veritabanı","KPI":"başarı göstergesi","CSAT":"müşteri memnuniyeti puanı",
"NOC":"7/24 izleme merkezi","SOC":"güvenlik operasyon merkezi","EDR":"uç nokta tespit ve müdahale",
"IPS":"saldırı engelleme","CVE":"bilinen güvenlik açığı kaydı","CVSS":"açık tehlike puanı",
"EOL":"kullanım ömrü sonu","CIS":"güvenlik sıkılaştırma standardı","ISO":"uluslararası standart",
"KVKK":"Kişisel Verileri Koruma Kanunu","RBAC":"rol bazlı yetkilendirme","PDF":"taşınabilir belge",
"IT":"bilgi teknolojileri","AI":"yapay zekâ","ID":"kimlik numarası","GVM":"Greenbone tarama motoru",
"GMP":"Greenbone yönetim protokolü","PrintNightmare":"yazıcı sürücüsü güvenlik açığı",
"AWX":"Ansible yönetim arayüzü","DMS":"veri taşıma servisi","PANOS":"Palo Alto güvenlik duvarı yazılımı",
"IOS":"Cisco cihaz işletim sistemi","HAProxy":"yük dağıtıcı","RHEL7":"eski bir Linux sürümü",
}
SKIP={'ORDER','LANES','DATA','GRADE','FULL','ASSISTED','HUMAN','AGENT','TAM','ONAYLI','İNSAN','AR','PS','TEK'}
KEYS=sorted((k for k in M if k not in SKIP), key=len, reverse=True)
SUF=r"(?:['’][A-Za-zÇĞİÖŞÜçğıöşü]+)?"
PATS=[(k, re.compile(r"(?<![0-9A-Za-zÇĞİÖŞÜçğıöşü./_-])"+re.escape(k)+SUF+r"(?![0-9A-Za-zÇĞİÖŞÜçğıöşü])")) for k in KEYS]

def expand(texts, seen=None):
    """Her metin listesi bir 'birim'. Kısaltma birim içinde ilk geçtiği yerde açılır."""
    seen = set() if seen is None else seen
    out=[]
    for t in texts:
        if not isinstance(t,str): out.append(t); continue
        for k,pat in PATS:
            if k in seen: continue
            m=pat.search(t)
            if not m: continue
            end=m.end()
            if t[end:end+2]==' (': seen.add(k); continue
            t = t[:end] + f" ({M[k]})" + t[end:]
            seen.add(k)
        out.append(t)
    return out
