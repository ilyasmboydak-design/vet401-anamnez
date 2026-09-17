import streamlit as st
import re

# Page Config
st.set_page_config(
    page_title="VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu",
    page_icon="🐄",
    layout="wide",
)

# Custom CSS Styling
st.markdown("""
    <style>
    .main-title {
        color: #1F4E79;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2px;
    }
    .sub-title {
        color: #595959;
        font-family: 'Arial', sans-serif;
        font-style: italic;
        text-align: center;
        font-size: 15px;
        margin-bottom: 20px;
    }
    .vaka-header {
        background: linear-gradient(90deg, #1F4E79 0%, #2F5597 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 12px;
    }
    .klinik-gorsel-box {
        background-color: #FFF9E6;
        border: 2px solid #FFE082;
        border-left: 6px solid #FFB300;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 18px;
    }
    .card-found {
        background-color: #F2F4F8;
        border-left: 6px solid #1F4E79;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 12px;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
    }
    .card-title {
        font-weight: bold;
        color: #1F4E79;
        font-size: 15px;
        margin-bottom: 4px;
    }
    .card-content {
        font-size: 15px;
        color: #262626;
        line-height: 1.5;
    }
    .badge-category {
        background-color: #D9E1F2;
        color: #1F4E79;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Cases Knowledge Base (12 Cases)
CASES = {
    "Vaka A (Papatya)": {
        "kod": "VAKA_A",
        "sikayet": "Hocam, Papatya isimli ineğimiz 3 gündür yemden kesildi, sütü bıçak gibi kesildi. Gerdanının altı ve çenesinin altı hamur gibi şişti, dokununca soğuk. Hayvan sürekli duruyor, kamburunu çıkarıp inliyor, yürütmek isteyince hiç oralı olmuyor...",
        "klinik_gorsel": None,
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Yaş & Irk",
                "keywords": ["ağırlık", "kilo", "kaç kg", "ağırlığı", "canlı ağırlık", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 540 kg | Yaş: 4.5 Yaşında | Irk: Siyah Alaca (Holstein) Süt İneği."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem yiyor mu", "iştahsızlık", "anoreksi", "su içiyor mu", "yem"],
                "content": "Şiddetli Anoreksi (Tam iştahsızlık). Hayvan kaba ve kesif yeme dokunmamaktadır, Rumen atozik durumdadır."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba", "tel", "çivi"],
                "content": "Günlük rasyonda mısır silajı, yonca otu ve fabrika yemi verilmektedir. Balya tel ve inşaat çivisi atıklarının kaba yeme karışmış olabileceği belirtilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik", "ova"],
                "content": "Ceyhan Ovası rakım ~50m sabit besi ve süt tesisinde doğup büyümüştür. Yayla sevk öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü"],
                "content": "Geçmişinde kronik metritis veya mastitis yoktur. 2 ay önce sorunsuz doğum yapmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "ödem", "vital"],
                "content": "Vücut Sıcaklığı: 39.8 °C | Kalp Frekansı: 102 atım/dk | Solunum Frekansı: 42 nefes/dk | Mukoza: Soluk pembe | CRT: 2.5 saniye | Gerdan ve submandibuler bölgede soğuk hamur ödem | Vena jugularis stazı +, yalancı jugular nabız +."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Gaz ve pürülan sıvının çalkalanmasına bağlı çamaşır makinesi / su şılpırtısı (splashing) sesi ve boğuk kalp sesleri duyuluyor. Akciğer: Ventro-lateral alanlarda solunum sesleri hafif azalmış."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri & Dedektör",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "dedektör", "metal", "mıknatıs"],
                "content": "Sopa testi, kama testi ve Withers pinch ağrı testlerinin tamamı Pozitif (+). Hayvan sırtını kamburlaştırıp inlemektedir. Ferroskop/Dedektör: Retikulum üzerinde Pozitif (+) metalik sinyal reaksiyonu."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f"],
                "content": "Lökosit (WBC): 22.4 x10³/µL | Eritrosit (RBC): 5.4 x10⁶/µL | PCV: %28 | Plazma Fibrinojeni: 1250 mg/dL (Aşırı yüksek yangı) | PP/F Oranı: 6.3 (Ağır aktif Fibrinöz Yangı Eşiği)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "bilirubin", "albümin", "globülin", "troponin"],
                "content": "Total Protein: 7.9 g/dL | Albümin: 2.4 g/dL | Globülin: 5.5 g/dL | AST: 118 U/L | GGT: 24 U/L | BUN: 28 mg/dL | Kreatinin: 1.2 mg/dL | Kardiyak Troponin I (cTnI): 0.85 ng/mL (Perikard/miyokard hasarı)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.32 | pO₂: 72 mmHg | pCO₂: 48 mmHg | HCO₃⁻: 20.2 mmol/L | Baz Açığı (BE): -4.1 mmol/L | Laktat: 2.8 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "ketonüri", "hematüri", "sediment", "idrar tahlili"],
                "content": "İdrar Dansitesi: 1.022 | pH: 7.8 | Protein: Trace (+) | Keton: Negatif | Glikoz: Negatif | Bilirubin: Negatif | Sediment: Nadir yassı epitel hücreleri, lökosit/eritrosit yok."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Ultrason, Perikardiyosentez & Kültür",
                "keywords": ["ultrason", "usg", "perikardiyosentez", "kültür", "bakteri", "ponksiyon", "sıvı"],
                "content": "USG: Perikardiyal boşlukta fibrin bantları ve 4 cm pürülan sıvı birikimi. Perikardiyosentez: Kirli sarı-yeşil pis kokulu eksuda. Kültür: Trueperella pyogenes üremesi."
            }
        }
    },

    "Vaka B (Yonca)": {
        "kod": "VAKA_B",
        "sikayet": "Hocam, Yonca adındaki süt ineğimiz 3 haftadır bir türlü toparlayamadı. Önce rahim iltihabı geçirdi, sonra memesi şişti. Şimdi de dizleri ve ayak eklemleri bilye gibi şişti, basamıyor. Sürekli yatıyor, ateşi düşmüyor...",
        "klinik_gorsel": None,
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Yaş & Irk",
                "keywords": ["ağırlık", "kilo", "kaç kg", "ağırlığı", "canlı ağırlık", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 580 kg | Yaş: 5 Yaşında | Irk: Siyah Alaca (Holstein)."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem yiyor mu", "iştahsızlık", "anoreksi", "yem"],
                "content": "Belirgin İştahsızlık (Hiporeksi). Günlük kesif yeminin sadece %20'sini tüketmektedir."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "silaj", "ot", "süt yemi"],
                "content": "Günlük rasyonda: 12 kg mısır silajı, 7 kg yonca otu ve 9 kg süt yemi verilmektedir."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü"],
                "content": "Yaklaşık 3 hafta önce doğum sonrası klinik metritis (rahim iltihabı) ve mastitis tedavisi görmüştür (Bakteriyemi kaynağı)."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "eklem", "topallık", "vital"],
                "content": "Vücut Sıcaklığı: 40.2 °C (Yüksek Ateş) | Kalp Frekansı: 110 atım/dk | Solunum Frekansı: 38 nefes/dk | Sol carpus ve tarsus eklemlerinde sıcak, şiş, ağrılı septik artrit odakları."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "boğuk", "triküspid"],
                "content": "Kalp Oskültasyonu: Triküspid kapak odak sahası üzerinde Grade IV/VI holosistolik üfürüm duyulmaktadır. Su çalkantı sesi YOKTUR."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri & Dedektör",
                "keywords": ["sopa", "kama", "withers", "ağrı", "retikulum", "dedektör"],
                "content": "Retikulum ağrı testleri (Sopa ve Kama) ve Metal Dedektörü NEGATİF (-)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "pp/f"],
                "content": "Lökosit (WBC): 26.8 x10³/µL (Şiddetli lökositoz) | Eritrosit (RBC): 4.2 x10⁶/µL | PCV: %22 | Plazma Fibrinojeni: 980 mg/dL | PP/F Oranı: 8.98."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "bun", "kreatinin", "albümin", "globülin", "troponin"],
                "content": "Serum Albümin: 2.3 g/dL | Serum Globülin: 6.5 g/dL (Hipergamaglobulinemi) | AST: 145 U/L | BUN: 34 mg/dL | Kardiyak Troponin I: 1.20 ng/mL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.30 | pO₂: 68 mmHg | pCO₂: 52 mmHg | HCO₃⁻: 18.8 mmol/L | Baz Açığı: -5.2 mmol/L | Laktat: 3.1 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "ketonüri", "hematüri", "sediment"],
                "content": "İdrar Dansitesi: 1.020 | pH: 7.5 | Protein: (+) | Keton: Negatif | Sediment: Bakteriyemiye bağlı 2-4 lökosit/Saha."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Ekokardiyografi & Kan Kültürü",
                "keywords": ["ekokardiyografi", "eko", "vejetasyon", "kültür", "bakteri", "kapak"],
                "content": "Ekokardiyografi: Triküspid kapak üzerinde 3.5 cm çapında pürüzlü hiperekojen kitle (vejetasyon). Kan & Eklem Kültürü: Trueperella pyogenes üremesi."
            }
        }
    },

    "Vaka C (Zümrüt)": {
        "kod": "VAKA_C",
        "sikayet": "Hocam, Zümrüt adındaki düvemizi 3 hafta önce Ceyhan'dan alıp Doğu Anadolu'daki 1900 metre yüksek yaylamıza çıkardık. Yaylaya çıktığından beri hayvanın göğsünün önü, döşü ve gerdanı torba gibi şişti. Yürütürken çabucak tıkanıyor, yürümek istemiyor...",
        "klinik_gorsel": None,
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Yaş & Irk",
                "keywords": ["ağırlık", "kilo", "kaç kg", "ağırlığı", "canlı ağırlık", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 460 kg | Yaş: 2 Yaşında Gebe Düve | Irk: Esmer (Simental Melezi)."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem yiyor mu", "mera", "iştahsızlık"],
                "content": "İştah hafif azalmıştır (Hiporeksi). Otlamaya isteksizdir, çabuk yorulmaktadır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik", "dağ", "metre"],
                "content": "3 hafta önce alçak rakımlı sahil ovasından (Ceyhan ~50m) Doğu Anadolu'daki 1900 metre rakımlı yüksek dağ yaylasına otlatılmak üzere nakledilmiştir (Yüksek Rakım / High Altitude)."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "ödem", "vital"],
                "content": "Vücut Sıcaklığı: 38.6 °C (NORMAL) | Kalp Frekansı: 96 atım/dk | Solunum Frekansı: 46 nefes/dk | Gerdan ve döş bölgesinde geniş alana yayılmış soğuk hamur ödem | Vena jugularis dolgun."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Hiperdinamik güçlü kalp sesleri duyulmaktadır. Üfürüm veya su çalkantı sesi YOKTUR."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri & Dedektör",
                "keywords": ["sopa", "kama", "withers", "ağrı", "retikulum", "dedektör"],
                "content": "Retikulum ağrı testleri ve Metal Dedektörü NEGATİF (-)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "polisitemi"],
                "content": "Eritrosit (RBC): 10.8 x10⁶/µL (Sekonder Polisitemi) | Hemoglobin (Hb): 17.2 g/dL | Hematokrit (PCV): %54 (Aşırı yüksek) | Lökosit (WBC): 7.2 x10³/µL (NORMAL) | Plazma Fibrinojeni: 320 mg/dL (NORMAL) | PP/F Oranı: 22.8."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "bun", "kreatinin", "albümin", "globülin", "troponin"],
                "content": "Albümin: 3.2 g/dL | Globülin: 4.1 g/dL | AST: 68 U/L | GGT: 18 U/L | BUN: 18 mg/dL | Kardiyak Troponin I: 0.12 ng/mL (Normal)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "oksijen", "hipoksi"],
                "content": "Kan pH: 7.36 | Kısmi Oksijen Basıncı (pO₂): 48 mmHg (Ağır Doku Hipoksisi / Yüksek Rakım) | pCO₂: 42 mmHg | HCO₃⁻: 23.5 mmol/L | Laktat: 1.5 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "ketonüri", "hematüri", "sediment"],
                "content": "İdrar Dansitesi: 1.025 | pH: 8.0 | Protein: Negatif | Keton: Negatif | Glikoz: Negatif | Sediment: Temiz."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Ekokardiyografi & Kültür",
                "keywords": ["ekokardiyografi", "eko", "pulmoner", "ventrikül", "kültür"],
                "content": "Ekokardiyografi: Sağ ventrikül serbest duvar kalınlığında artış (Sağ Ventrikül Hipertrofisi), pulmoner arter çapında genişleme. Kültür: Bakteri üremesi YOKTUR (Steril)."
            }
        }
    },

    "Vaka D (Yiğit)": {
        "kod": "VAKA_D",
        "sikayet": "Hocam, besi padoğundaki Yiğit isimli tosunsun ağzından ve burnundan fışkırır gibi taze kırmızı kan geldi! Yemliği kan kapladı. Dışkısı da zift gibi, katran gibi kapkara çıkıyor...",
        "klinik_gorsel": None,
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Yaş & Irk",
                "keywords": ["ağırlık", "kilo", "kaç kg", "ağırlığı", "canlı ağırlık", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 620 kg | Yaş: 18 Aylık Besi Tosunu | Irk: Simental."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem yiyor mu", "iştahsızlık", "anoreksi", "kan"],
                "content": "Anoreksi. Ağız ve burundan kan gelmesi (Hemoptizi) nedeniyle yem tüketimi tamamen durmuştur."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "besi", "nişasta"],
                "content": "Yoğun mısır kırması ve arpa kırması ağırlıklı, kaba yem oranı son derece yetersiz yüksek nişastalı besi rasyonu verilmektedir."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "asidoz", "şişkinlik", "timpani", "rumenitis", "yem çarpması"],
                "content": "Geçmişinde tekrarlayan akut/subakut rumen asidozu (yem çarpması) ve kronik hafif rumen timpani (şişkinlik) öyküsü vardır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "kan", "hemoptizi", "melena", "dışkı", "vital"],
                "content": "Vücut Sıcaklığı: 39.2 °C | Kalp Frekansı: 118 atım/dk | Solunum Frekansı: 52 nefes/dk | Ağız/Burun: Köpüklü taze parlak kırmızı kan fışkırması (Hemoptizi) | Mukozalar: Bembeyaz (Ağır anemi) | CRT: 4.0 saniye | Dışkı: Siyah katran kıvamında (Melena)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Taşikardik, zayıf düştü sesleri. Akciğer Oskültasyonu: Bilateral yaygın kaba raller ve hışırtı sesleri duyuluyor."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "anemi"],
                "content": "Eritrosit (RBC): 2.1 x10⁶/µL (Kritik Kan Kaybı Anemisi) | Hemoglobin (Hb): 4.2 g/dL | Hematokrit (PCV): %12 (Acil Transfüzyon Eşiği!) | Lökosit (WBC): 21.5 x10³/µL | Plazma Fibrinojeni: 1050 mg/dL | PP/F: 7.23."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "bun", "kreatinin", "bilirubin", "albümin", "globülin", "karaciğer"],
                "content": "AST: 210 U/L (Karaciğer parankim nekrozu) | GGT: 68 U/L (Safra yolu/apse) | BUN: 42 mg/dL | Kreatinin: 1.6 mg/dL | Total Bilirubin: 1.2 mg/dL | İndirekt Bilirubin: 0.8 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.24 | pO₂: 52 mmHg | pCO₂: 50 mmHg | HCO₃⁻: 18.5 mmol/L | Baz Açığı: -6.2 mmol/L | Laktat: 4.2 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "ketonüri", "hematüri", "sediment"],
                "content": "İdrar Dansitesi: 1.018 | pH: 7.2 | Protein: (+) | Keton: Negatif | Sediment: Ağır anemiye bağlı izole hyalin silindirler."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Abdominal & Torakal Ultrasonografi",
                "keywords": ["ultrason", "usg", "karaciğer", "apse", "vena cava", "trombüs", "arter", "anevrizma"],
                "content": "Abdominal USG: Karaciğer parankiminde 6 cm çapında kılıflı apse odağı (Hepatic Abscess), Vena Cava Caudalis lümeninde tıkayıcı trombüs ekojenitesi. Torakal USG: Pulmoner arter çevresinde hematom ve anevrizma erozyonu."
            }
        }
    },

    "Vaka E (Kudret)": {
        "kod": "VAKA_E",
        "sikayet": "Hocam, Kudret isimli danamızın kafasında, gözlerinin etrafında ve boynunda madeni para gibi yuvarlak döküntüler çıktı. Üstü kireç gibi beyaz beyaz kabuklandı, tüyleri döküldü. Yanındaki danalara da sıçramaya başladı...",
        "klinik_gorsel": [
            {
                "title": "📷 KLİNİK MAKROSKOPİK LEZYON (Figure 1.2-1)",
                "desc": "Baş, göz çevresi ve boyun bölgesinde dairesel, belirgin sınırlı, gri-beyaz kireçimsi kalın kabuklanma ve tüy dökülmesi (alopezi) lezyonları (Color Atlas of Farm Animal Dermatology - Scott, 2018)."
            }
        ],
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Yaş & Irk",
                "keywords": ["ağırlık", "kilo", "kaç kg", "ağırlığı", "canlı ağırlık", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 220 kg | Yaş: 7 Aylık Erkek Dana | Irk: Holstein."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem yiyor mu", "iştahsızlık"],
                "content": "İştah Normaldir. Genel durumu iyidir."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Hijyen Koşulları",
                "keywords": ["ahır", "barınak", "nem", "ışık", "karanlık", "kalabalık", "hijyen", "dezenfeksiyon", "yataklık"],
                "content": "Kapalı, nemli, güneş ışığı almayan ve havalandırması yetersiz kalabalık padokta barındırılmaktadır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "deri", "döküntü", "kabuk", "vital"],
                "content": "Vücut Sıcaklığı: 38.8 °C (NORMAL) | Kalp Frekansı: 78 atım/dk | Solunum Frekansı: 26 nefes/dk | Mukozalar: Pembe | Deri: Baş, göz çevresi ve boyunda dairesel, gri-beyaz kireçimsi kabuklu döküntüler."
            },
            "MIKROSKOPIK_MUAYENE": {
                "name": "🔬 Mikroskopik Tahlil & %10 KOH Testi (Figure 1.2-11)",
                "keywords": ["mikroskop", "mikroskopi", "koh", "kazıntı", "mantar tahlili", "lam", "artrospor", "spor", "deri kazıntısı"],
                "content": "🔬 MİKROSKOPİK BULGU (Figure 1.2-11): %10 KOH (Potasyum Hidroksit) ile muamele edilmiş yüzeysel deri kazıntısının 40x ışık mikroskobu incelemesinde; kırık kıl şaftının dış yüzeyini zırh gibi saran küresel Trichophyton verrucosum ektotriks artrospor zincirleri ve dallanan hyalin hifler tespit edilmiştir."
            },
            "PARAKLINIK_TESTLER": {
                "name": "Wood Lambası & Mantar Kültürü",
                "keywords": ["wood", "uv", "floresans", "kültür", "besiyeri", "sabouraud"],
                "content": "Wood Lambası (365 nm UV): Trichophyton verrucosum türü zayıf/negatif floresans vermiştir. Sabouraud Dextrose Agar Kültürü: 37°C'de 2 haftada mumu andıran kabarık krem renkli mantar kolonileri gelişmiştir."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv"],
                "content": "Lökosit (WBC): 8.4 x10³/µL (NORMAL) | Fibrinojen: 310 mg/dL (NORMAL) | Hematokrit: %34. Mantarın stratum corneum dışına inmemesi nedeniyle sistemik yangı yanıtı oluşmamıştır."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "bun", "kreatinin", "albümin", "globülin"],
                "content": "ALT: 24 U/L | AST: 72 U/L | GGT: 20 U/L | BUN: 16 mg/dL | Kreatinin: 0.9 mg/dL | Total Protein: 7.1 g/dL (Tüm organ enzimleri fizyolojik sınırlardadır)."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "ketonüri", "sediment"],
                "content": "İdrar Dansitesi: 1.022 | pH: 8.0 | Protein: Negatif | Keton: Negatif | Sediment: Temiz."
            }
        }
    },

    "Vaka F (Nazar)": {
        "kod": "VAKA_F",
        "sikayet": "Hocam, Nazar isimli ineğimiz çıldırmış gibi sürekli çitlere, demirlere sürtünüyor! Şiddetle kaşınıyor. Kulaklarının arkası, boynu ve sırtının derisi fil derisi gibi kalınlaştı, kıvrım kıvrım oldu, kanatana kadar kaşıyor...",
        "klinik_gorsel": [
            {
                "title": "📷 KLİNİK MAKROSKOPİK LEZYON 1 (Figure 1.3-13)",
                "desc": "Yüz, kulak kepçesi, boyun ve omuz bölgesinde şiddetli kaşıntı izleri (eksforyasyon), deride kalınlaşma, kıvrımlaşma (likenifikasyon) ve tüy kaybı."
            },
            {
                "title": "📷 KLİNİK MAKROSKOPİK LEZYON 2 (Figure 1.3-15)",
                "desc": "Gövde ve sırt hattında yer yer kanamalı, kabuklu ve kepekli kronik mikotik/paraziter dermatit alanları."
            }
        ],
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Yaş & Irk",
                "keywords": ["ağırlık", "kilo", "kaç kg", "ağırlığı", "canlı ağırlık", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 380 kg | Yaş: 3 Yaşında İnek | Irk: Yerli Kara / Melez."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem yiyor mu", "kaşıntı", "iştahsızlık"],
                "content": "Şiddetli kaşıntı huzursuzluğuna bağlı yem tüketimi azalmıştır (Hiporeksi)."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Hijyen Koşulları",
                "keywords": ["ahır", "barınak", "nem", "hijyen", "yataklık", "gübre", "kalabalık"],
                "content": "Kış döneminde kapalı, altlığı ıslak ve gübreli, uzun süre tımar yapılmamış bakımsız barınak koşulları."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "deri", "kaşıntı", "kabuk", "vital"],
                "content": "Vücut Sıcaklığı: 39.1 °C | Kalp Frekansı: 88 atım/dk | Solunum Frekansı: 30 nefes/dk | Deri: Boyun, omuz ve kuyruk sokumunda fil derisi gibi kalınlaşma (Likenifikasyon), kepeklenme ve kanamalı kaşıntı izleri."
            },
            "MIKROSKOPIK_MUAYENE": {
                "name": "🔬 Mikroskopik Derin Kazıntı & Akar Muayenesi (Figure 1.3-18)",
                "keywords": ["mikroskop", "mikroskopi", "derin kazıntı", "akar", "uyuz tahlili", "mineral yağ", "vazelin", "lamel", "scabies", "yumurta"],
                "content": "🔬 MİKROSKOPİK BULGU (Figure 1.3-18): Bistüriye mineral yağ damlatılarak kapiller kanama görülünceye kadar alınan derin deri kazıntısının 10x-40x mikroskopik incelemesinde; kısa bacaklı, yuvarlak gövdeli canlı ergin Sarcoptes scabiei var. bovis akarları, oval akar yumurtaları (eggs) ve karakteristik koyu renkli dışkı peletleri (scybala) izlenmiştir."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "eozinofil", "fibrinojen", "eritrosit", "rbc", "pcv"],
                "content": "Lökosit (WBC): 14.2 x10³/µL | Eozinofil: %16 (Şiddetli Paraziter Eozinofili) | Plazma Fibrinojeni: 420 mg/dL (Hafif sekonder yangı)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "bun", "kreatinin", "albümin", "globülin"],
                "content": "Serum Albümin: 3.1 g/dL | Serum Globülin: 4.8 g/dL (Hafif artış) | AST: 74 U/L | GGT: 22 U/L | BUN: 18 mg/dL | Kreatinin: 1.0 mg/dL."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "ketonüri", "sediment"],
                "content": "İdrar Dansitesi: 1.024 | pH: 8.1 | Protein: Negatif | Keton: Negatif | Sediment: Temiz."
            }
        }
    },

    "Vaka G (Çiçek)": {
        "kod": "VAKA_G",
        "sikayet": "Hocam, Çiçek isimli alaca ineğimizi güneşe çıkardıktan sonra ineğin vücudundaki BEYAZ tüylü deri bölgeleri torba gibi şişti, su topladı, kabuklanıp tabaka halinde soyulmaya başladı! Garip olan, siyah tüylü yerlerinde hiçbir şey yok, dipdiri duruyor...",
        "klinik_gorsel": [
            {
                "title": "📷 KLİNİK MAKROSKOPİK LEZYON (Figure 1.7-35)",
                "desc": "Karaciğer yetmezliğine bağlı kanda biriken filloeritrin nedeniyle YALNIZCA pigmentsiz (beyaz) deri bölgelerinde şekillenen eritem, hamur ödemi, derinin tabaka halinde soyulması (sloughing) ve nekroz; siyah pigmentli deri alanlarının tamamen sağlam kalması."
            }
        ],
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Yaş & Irk",
                "keywords": ["ağırlık", "kilo", "kaç kg", "ağırlığı", "canlı ağırlık", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 450 kg | Yaş: 4 Yaşında İnek | Irk: Siyah Alaca (Holstein)."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem yiyor mu", "güneş", "iştahsızlık"],
                "content": "Ağrı ve fotofobi (güneşten kaçma) nedeniyle anoreksi gelişmiştir."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Mera & Otlatma Öyküsü",
                "keywords": ["otlatma", "mera", "bitki", "toksik", "güneş", "ot", "küf"],
                "content": "Bahar döneminde yeşil otça zengin (klorofil yüksek) merada otlatılmıştır. Karaciğer hasarı oluşturan toksik bitkiler tespit edilmiştir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "ikter", "sarılık", "deri", "güneş yanığı", "vital"],
                "content": "Vücut Sıcaklığı: 39.6 °C | Kalp Frekansı: 92 atım/dk | Mukoza: Şiddetli İkterik (Sarılık +) | Deri: Sadece BEYAZ deri alanlarında eritem, nekroz, hamur ödemi ve deri soyulması. Siyah alanlar sağlam."
            },
            "MIKROSKOPIK_MUAYENE": {
                "name": "🔬 Deri Biyopsisi & Mikroskopik İnceleme",
                "keywords": ["mikroskop", "mikroskopi", "biyopsi", "patoloji", "histopatoloji"],
                "content": "🔬 MİKROSKOPİK HİSTOPATOLOJİ: Epidermal keratinositlerde koagülasyon nekrozu, koryumda şiddetli ödem, vaskülit ve fotodinamik doku harabiyeti."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv"],
                "content": "Lökosit (WBC): 16.8 x10³/µL | Nötrofil: %72 | Plazma Fibrinojeni: 680 mg/dL (Doku nekrozuna bağlı yüksek)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Karaciğer Enzimleri",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "bilirubin", "karaciğer", "sarılık", "kolestaz"],
                "content": "GGT: 180 U/L (Ağır Karaciğer/Safra Tıkanıklığı) | AST: 290 U/L | ALP: 340 U/L | Total Bilirubin: 4.2 mg/dL | İndirekt Bilirubin: 1.8 mg/dL (Hepatojen İkter)."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "ketonüri", "bilirubinüri", "hematüri", "sediment"],
                "content": "İdrar Dansitesi: 1.026 | pH: 7.4 | Bilirubinüri: (+++) Koyu çay/kehribar renkli idrar | Protein: (+) | Keton: Negatif."
            }
        }
    },

    "Vaka H (Ateş)": {
        "kod": "VAKA_H",
        "sikayet": "Hocam, Ateş isimli tosunumuz antibiyotik ve döl kontrol aşısı vurulduktan yarım saat sonra aniden her tarafı kabardı! Göğsünde, boynunda ve yanlarında el içi gibi kabarık plaklar oluştu. Hayvan hırıltılı nefes alıyor...",
        "klinik_gorsel": [
            {
                "title": "📷 KLİNİK MAKROSKOPİK LEZYON (Figure 1.5-1)",
                "desc": "Gövde, boyun ve omuzlarda aniden beliren, parmakla basıldığında çukurlaşan (pitting edema), ödemli, kabarık, dairesel/plak benzeri akut ürtiker lezyonları (wheals/urtica)."
            }
        ],
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Yaş & Irk",
                "keywords": ["ağırlık", "kilo", "kaç kg", "ağırlığı", "canlı ağırlık", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 510 kg | Yaş: 2 Yaşında Tosun | Irk: Simental."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem yiyor mu", "alerji", "iştahsızlık"],
                "content": "Akut huzursuzluk ve solunum güçlüğü nedeniyle yem yememektedir."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Öykü & İlaç/Aşı Enjeksiyonu",
                "keywords": ["aşı", "enjeksiyon", "ilaç", "antibiyotik", "serum", "sinek", "böcek", "alerji"],
                "content": "Olaydan 30 dakika önce parenteral penisilin ve aşı uygulaması yapılmıştır (Akut Tip I Aşırı Duyarlılık / Anafilaktoid)."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "ürtiker", "kabartı", "plak", "vital"],
                "content": "Vücut Sıcaklığı: 39.4 °C | Kalp Frekansı: 108 atım/dk | Solunum Frekansı: 48 nefes/dk (Hırıltılı) | Deri: Gövde ve boyunda parmakla basılınca çukurlaşan ödemli kabarık ürtiker plakları."
            },
            "MIKROSKOPIK_MUAYENE": {
                "name": "🔬 Biyopsi & Sitolojik Muayene",
                "keywords": ["mikroskop", "mikroskopi", "sitoloji", "biyopsi"],
                "content": "🔬 SİTOLOJİK BULGU: Dermis taze frotisinde yoğun degranüle mast hücreleri ve eozinofil lökosit infiltrasyonu."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "eozinofil", "fibrinojen", "eritrosit", "rbc", "pcv"],
                "content": "Lökosit (WBC): 12.8 x10³/µL | Eozinofil: %18 (Akut Alerjik Eozinofili) | Fibrinojen: 340 mg/dL (NORMAL)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "bun", "kreatinin", "albümin", "globülin"],
                "content": "Organ enzimleri ve böbrek değerleri tamamen fizyolojik sınırlar içerisindedir."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "ketonüri", "sediment"],
                "content": "İdrar Dansitesi: 1.022 | pH: 7.8 | Protein: Negatif | Keton: Negatif | Sediment: Temiz."
            }
        }
    },

    "Vaka I (Fırtına)": {
        "kod": "VAKA_I",
        "sikayet": "Hocam, Fırtına isimli buzağımız dün geceden beri gırtlağından hırıl hırıl, düdük sesi gibi ses çıkararak nefes alıyor! Boynunu uzatmış hırlıyor. Boğazını tutunca acıyla peş peşe öksürüyor, ağzına yem alsa da yutamayıp yere düşürüyor...",
        "klinik_gorsel": None,
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Yaş & Irk",
                "keywords": ["ağırlık", "kilo", "kaç kg", "ağırlığı", "canlı ağırlık", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 180 kg | Yaş: 5 Aylık Sütten Kesilmiş Buzağı | Irk: Simental."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem yiyor mu", "yutma", "disfaji", "iştahsızlık"],
                "content": "Gırtlaktaki şiddetli yangı ve ödem nedeniyle yutma ağrılıdır (Disfaji). Ağzına aldığı yemi düşürmektedir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "gırtlak", "larenks", "stridor", "vital"],
                "content": "Vücut Sıcaklığı: 40.4 °C (Yüksek Yüksek Yüksek Ateş) | Kalp Frekansı: 112 atım/dk | Solunum Frekansı: 50 nefes/dk | Solunumsal Düdük Sesi (Inspiratorik Stridor) +, Larenks bölgesine dokununca şiddetli öksürük ve ağrı."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer", "rall", "veziküler"],
                "content": "Kalp Oskültasyonu: Taşikardik ancak sesler temiz. Akciğer Oskültasyonu: Veziküler solunum sesleri tamamen NORMALDIR (Hastalık gırtlakta sınırlıdır)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv"],
                "content": "Lökosit (WBC): 22.4 x10³/µL | Nötrofil: %78 (Sola kayma +) | Plazma Fibrinojeni: 1100 mg/dL (Şiddetli Akut Yangı)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.38 | pO₂: 92 mmHg (NORMAL - Akciğer gaz alışverişi sağlam) | pCO₂: 44 mmHg | HCO₃⁻: 24.2 mmol/L | Baz Açığı: +0.5 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "ketonüri", "sediment"],
                "content": "İdrar Dansitesi: 1.022 | pH: 7.8 | Protein: Trace (+) | Keton: Negatif | Sediment: Temiz."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Endoskopi & Mikrobiyoloji",
                "keywords": ["endoskopi", "larenks", "laringoskop", "kültür", "bakteri", "fusobacterium"],
                "content": "Endoskopi/Laringoskopi: Larengeal arytenoid kıkırdaklarda şiddetli ödem, hiperemi ve yer yer nekrotik psödomembranlar. Kültür: Fusobacterium necrophorum üremesi."
            }
        }
    },

    "Vaka J (Şahin)": {
        "kod": "VAKA_J",
        "sikayet": "Hocam, Şahin adındaki tosunumuzun 1 ay önce boynuzunu kesmiştik. Boynuz kütüğünün olduğu yer kapanmadı, oradan ve burnunun tek tarafından leş gibi kokuşmuş sümük akıyor! Sol tarafına dokundurtmuyor, kafasını yan tutuyor...",
        "klinik_gorsel": None,
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Yaş & Irk",
                "keywords": ["ağırlık", "kilo", "kaç kg", "ağırlığı", "canlı ağırlık", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 560 kg | Yaş: 2.5 Yaşında Tosun | Irk: Simental."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem yiyor mu", "baş ağrısı", "iştahsızlık"],
                "content": "Şiddetli baş ağrısı ve lokomotor isteksizlik nedeniyle yem tüketimi %50 azalmıştır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Öykü & Boynuz Kesimi",
                "keywords": ["boynuz", "dehorning", "kesim", "diş", "ameliyat", "yaralanma"],
                "content": "Yaklaşık 1 ay önce açık ve steril olmayan koşullarda boynuz kesimi yapılmıştır (Sinüs enfeksiyonu sekeli)."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "sinüs", "akıntı", "perküsyon", "vital"],
                "content": "Vücut Sıcaklığı: 39.5 °C | Kalp Frekansı: 86 atım/dk | Solunum Frekansı: 28 nefes/dk | Sol frontal sinüs bölgesi üzerine yapılan Perküsyonda MAT SES (Matite) ve şiddetli ağrı reaksiyonu. Tek taraflı pürülan fetid burun akıntısı."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv"],
                "content": "Lökosit (WBC): 18.6 x10³/µL | Nötrofil: %74 | Plazma Fibrinojeni: 850 mg/dL (Kronik pürülan yangı)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "bun", "kreatinin", "albümin", "globülin"],
                "content": "Serum Albümin: 2.8 g/dL | Serum Globülin: 5.4 g/dL (Kronik hipergamaglobulinemi) | AST: 82 U/L | BUN: 22 mg/dL."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "ketonüri", "sediment"],
                "content": "İdrar Dansitesi: 1.025 | pH: 8.0 | Protein: Negatif | Keton: Negatif | Sediment: Temiz."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Radyografi, Trepanasyon & Kültür",
                "keywords": ["röntgen", "radyografi", "sinüs", "trepanasyon", "kültür", "bakteri"],
                "content": "Frontal Sinüs Radyografisi: Sinüs boşluğunda radyoopak sıvı-hava seviyesi ve kemik trabeküllerinde opasite artışı. Kültür: Trueperella pyogenes ve anaerob bakteriler."
            }
        }
    },

    "Vaka K (Rüzgar)": {
        "kod": "VAKA_K",
        "sikayet": "Hocam, Rüzgar isimli İngiliz atımız durduğu yerde aniden burnundan foşur foşur taze kırmızı kan akıtmaya başladı! Hiçbir darbe almadı. İki gündür samanı ağzına alıyor ama yutamıyor, lokmalar ve içtiği su burnundan geri çıkıyor...",
        "klinik_gorsel": None,
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Yaş & Irk",
                "keywords": ["ağırlık", "kilo", "kaç kg", "ağırlığı", "canlı ağırlık", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 480 kg | Yaş: 6 Yaşında Erkek Aygır | Irk: İngiliz Yarış Atı."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem yiyor mu", "su", "burun", "disfaji", "yutma"],
                "content": "Disfaji (Yutma Felci/Güçlüğü). İçtiği su ve yutmaya çalıştığı yemler sinir felci nedeniyle burun deliklerinden geri gelmektedir (Regürjitasyon)."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "kanama", "epistaksis", "vital"],
                "content": "Vücut Sıcaklığı: 38.2 °C (NORMAL) | Kalp Frekansı: 68 atım/dk (Kan kaybına bağlı hafif taşikardi) | Solunum Frekansı: 22 nefes/dk | Tek taraflı spontan taze kırmızı burun kanaması (Epistaksis) ve N. Glossopharyngeus / N. Vagus felci bulguları."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "anemi"],
                "content": "Eritrosit (RBC): 4.8 x10⁶/µL | PCV: %26 (Epizodik kanamaya bağlı anemi) | Lökosit (WBC): 11.2 x10³/µL | Fibrinojen: 480 mg/dL."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "bun", "kreatinin", "albümin", "globülin"],
                "content": "Organ enzimleri fizyolojik sınırlardadır."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "ketonüri", "sediment"],
                "content": "İdrar Dansitesi: 1.030 | pH: 7.5 | Protein: Negatif | Keton: Negatif | Sediment: Temiz."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Endoskopi & Mantar Teşhisi",
                "keywords": ["endoskopi", "hava kesesi", "guttural", "aspergillus", "arter", "mantar"],
                "content": "Endoskopi: Hava kesesi (Guttural Pouch) lümeninde Arteria carotis interna duvarı üzerinde siyah-gri-yeşil renkli mantar plağı (Aspergillus fumigatus) ve damar erozyonu."
            }
        }
    },

    "Vaka L (Poyraz)": {
        "kod": "VAKA_L",
        "sikayet": "Hocam, Poyraz adındaki atımız 1 ay önce ağır bir boğaz iltihabı (Gurm) geçirdi. Hastalık geçti derken şimdi kulaklarının altı, çenesinin arkası kafa gibi şişti! İki burun deliğinden de koyu sarı, iltihaplı akıntı geliyor, kafasını uzatarak duruyor...",
        "klinik_gorsel": None,
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Yaş & Irk",
                "keywords": ["ağırlık", "kilo", "kaç kg", "ağırlığı", "canlı ağırlık", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 520 kg | Yaş: 5 Yaşında At | Irk: Arap Atı."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem yiyor mu", "ağrı", "gurm", "iştahsızlık"],
                "content": "Ağrılı yutma nedeniyle iştah azalmıştır (Hiporeksi)."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Öykü & Gurm Hastalığı",
                "keywords": ["gurm", "streptococcus", "boğaz", "apse", "lenf nodu", "geçmiş"],
                "content": "Yaklaşık 1 ay önce klinik Gurm hastalığı (Streptococcus equi subsp. equi) geçirme öyküsü vardır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "hava kesesi", "parotis", "akıntı", "vital"],
                "content": "Vücut Sıcaklığı: 39.2 °C | Kalp Frekansı: 72 atım/dk | Parotis ve retrofaringeal bölgede bilateral sıcak, ağrılı, fluktuğan şişlik. Çift taraflı koyu sarı pürülan burun akıntısı. Hayvan başını öne uzatmaktadır."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv"],
                "content": "Lökosit (WBC): 24.8 x10³/µL (Şiddetli pürülan lökositoz) | Plazma Fibrinojeni: 920 mg/dL."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "bun", "kreatinin", "albümin", "globülin"],
                "content": "Serum Albümin: 2.6 g/dL | Serum Globülin: 5.8 g/dL (Hipergamaglobulinemi)."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "ketonüri", "sediment"],
                "content": "İdrar Dansitesi: 1.026 | pH: 7.8 | Protein: (+) | Keton: Negatif | Sediment: Temiz."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Endoskopi & Kondroit (Chondroid) Muayenesi",
                "keywords": ["endoskopi", "hava kesesi", "empiyem", "kondroit", "chondroid", "kültür", "streptococcus"],
                "content": "Endoskopi: Hava kesesi lümeninde yoğun irin birikimi ve kurumuş taşlaşmış irin yumakları (Chondroid / Kondroitler). Kültür: Streptococcus equi subsp. equi üremesi."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnezi & Bulgu Sorgulama Konsolu (Serbest Metin Sorgulama)</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:15px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde şıklar veya hazır butonlar <u>yoktur</u>. 
        Kafanızdaki klinik şüpheye göre ne öğrenmek istiyorsanız kutucuğa <b>kendi cümlenizle veya kelimelerinizle</b> yazınız 
        (Örn: <i>"Canlı ağırlığı kaç kg?"</i>, <i>"İştahı nasıl?"</i>, <i>"Rasyonu nedir?"</i>, <i>"Ateşi kaç derece?"</i>, <i>"Hemogram ve idrar tahlili istiyorum"</i>, <i>"Mikroskopta ne görüldü?"</i>).
    </div>
""", unsafe_allow_html=True)

# Select Case
selected_case_name = st.selectbox(
    "🔍 İncelemek İstediğiniz Vakayı Seçiniz:",
    options=list(CASES.keys()),
    index=0
)

# Session State Management for Case Switching Reset
if "current_selected_case" not in st.session_state:
    st.session_state.current_selected_case = selected_case_name

if "history" not in st.session_state:
    st.session_state.history = {}

# If user switches case from dropdown, reset history for fresh view
if st.session_state.current_selected_case != selected_case_name:
    st.session_state.current_selected_case = selected_case_name
    st.session_state.history[selected_case_name] = []

if selected_case_name not in st.session_state.history:
    st.session_state.history[selected_case_name] = []

active_case = CASES[selected_case_name]

# Header for Case Initial Complaint
st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — İlk Başvuru Şikayeti</div>", unsafe_allow_html=True)
st.info(f"**Hastanın Başvuru Şikayeti (Yetiştirici Anamnezi):** {active_case['sikayet']}")

# AUTOMATIC CLINICAL VISUAL DISPLAY (AUTOMATICALLY SHOWN WITHOUT ASKING ANY QUESTION)
if active_case.get("klinik_gorsel"):
    st.markdown("<div class='klinik-gorsel-box'>", unsafe_allow_html=True)
    st.markdown("### 📸 Klinik Makroskopik Görsel Bulgular (Vaka İnceleme Paneli)")
    st.markdown("*Aşağıdaki klinik lezyon fotoğrafları hasta başvurusu anında fiziki muayenede doğrudan gözlemlenmiştir:*")
    st.markdown("")
    for gorsel in active_case["klinik_gorsel"]:
        st.warning(f"**{gorsel['title']}**\n\n{gorsel['desc']}")
    st.markdown("</div>", unsafe_allow_html=True)

# Question Input Section
st.markdown("### 💬 Sorunuzu veya İncelemek İstediğiniz Muayeneyi Yazınız:")

def match_query(user_text, categories_dict):
    text_clean = user_text.lower().strip()
    text_clean = text_clean.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    
    matched_cats = []
    
    for cat_key, cat_info in categories_dict.items():
        for kw in cat_info["keywords"]:
            kw_clean = kw.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
            if re.search(r'\\b' + re.escape(kw_clean), text_clean) or kw_clean in text_clean:
                matched_cats.append(cat_key)
                break
                
    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız (Örn: Canlı ağırlığı?, Ateşi kaç?, İdrar tahlili?, Mikroskopta ne var?):",
        key="query_input",
        placeholder="Örn: Hayvan kaç kg?, Rasyonu ne?, Hemogram tahlili?, Mikroskopik inceleme?..."
    )

with col_button:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    submit_btn = st.button("🔎 Sor ve Sorgula", type="primary", use_container_width=True)

if submit_btn and user_query:
    matches = match_query(user_query, active_case["categories"])
    
    if matches:
        new_discoveries = 0
        for cat_key in matches:
            cat_data = active_case["categories"][cat_key]
            # Check if already in history
            already_in = any(item["cat_key"] == cat_key for item in st.session_state.history[selected_case_name])
            if not already_in:
                st.session_state.history[selected_case_name].append({
                    "cat_key": cat_key,
                    "query": user_query,
                    "title": cat_data["name"],
                    "content": cat_data["content"]
                })
                new_discoveries += 1
        
        if new_discoveries > 0:
            st.success(f"🎉 Teşekkürler! Sorunuzla ilişkili {new_discoveries} yeni klinik/laboratuvar bulgusu açığa çıkarıldı!")
        else:
            st.info("Bu soruyla ilgili bilgi zaten daha önce açığa çıkarılmıştı. Aşağıdaki keşifler listenizden okuyabilirsiniz.")
    else:
        st.warning("⚠️ Girdiğiniz soru veya kelimelerle eşleşen bir bilgi bulunamadı. Lütfen sorunuzu farklı anahtar kelimelerle yazınız (Örn: 'ağırlık', 'iştah', 'ateş', 'hemogram', 'idrar', 'mikroskop', 'ultrason').")

# Display Discovered Information
st.markdown("---")
st.markdown(f"### 📂 Keşfedilen Klinik İpuçları ve Muayene Bulguları ({len(st.session_state.history[selected_case_name])} Bilgi Açıldı)")

if st.session_state.history[selected_case_name]:
    for idx, item in enumerate(reversed(st.session_state.history[selected_case_name])):
        st.markdown(f"""
            <div class='card-found'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                    <span class='badge-category'>{item['title']}</span>
                    <span style='font-size:12px; color:#7F7F7F;'>Sorulan Soru: "{item['query']}"</span>
                </div>
                <div class='card-content'><b>🩺 Bulgu / Tahlil Sonucu:</b> {item['content']}</div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Henüz bu vaka için soru sormadınız. Yukarıdaki arama kutusuna merak ettiğiniz soruyu yazarak muayeneye başlayınız.")

# Reset History Button
if st.session_state.history[selected_case_name]:
    if st.button("🗑️ Bu Vakanın Sorgu Geçmişini Temizle"):
        st.session_state.history[selected_case_name] = []
        st.rerun()

# Teacher Portal
with st.sidebar:
    st.markdown("### 🏛️ ÇU Veteriner Fakültesi")
    st.markdown("**VET401 İç Hastalıkları I**")
    st.markdown("---")
    st.markdown("### 🔒 Eğitmen Portalı")
    teacher_login = st.checkbox("Eğitmen Anahtar Paneli")
    if teacher_login:
        pass_code = st.text_input("Giriş Şifresi:", type="password")
        if pass_code == "vet401":
            st.success("Eğitmen Erişimi Onaylandı!")
            st.markdown("#### 🔑 Bu Vakanın Gizli Tüm Bilgileri:")
            for ck, cv in active_case["categories"].items():
                st.markdown(f"**• {cv['name']}:** {cv['content']}")
        elif pass_code:
            st.error("Hatalı Şifre!")
