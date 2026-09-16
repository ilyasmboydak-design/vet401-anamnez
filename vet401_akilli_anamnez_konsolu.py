import streamlit as st
import re

# Page Config
st.set_page_config(
    page_title="VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu",
    page_icon="🐄",
    layout="wide",
)

# Styling
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
        margin-bottom: 15px;
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

# Cases Knowledge Base
CASES = {
    "Vaka A (Papatya)": {
        "kod": "VAKA_A",
        "sikayet": "Hocam, iki gündür Papatya aniden sütten kesildi. Göğsünün altı, gerdanı buz gibi hamur gibi şişti, elini sürünce çöküyor kalıyor. Öne doğru eğilip sırtını kamburlaştırıyor, yanına yaklaşınca derin derin inliyor. Yemliğe taze silaj koysak da yüzünü çeviriyor, gözlerinin feri söndü...",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Irk & Yaş",
                "keywords": ["ağırlık", "agirllik", "kilo", "kaç kg", "kilo", "yaş", "ırk", "irki"],
                "content": "Canlı Ağırlık: 540 kg | Irk: Holstein 🏛️ | Yaş: 4 Yaşında (2. Laktasyonda)"
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu & Yem Tüketimi",
                "keywords": ["iştah", "istah", "yem yemiyor", "yeme", "yem reddi", "anoreksi", "süt", "iştahsızlık"],
                "content": "İştah Durumu: Komple Anoreksi (Sert retiküler ve perikardiyal ağrı ile sistemik yangı nedeniyle yem ve su tüketimini tamamen kesmiştir)."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba"],
                "content": "Günlük rasyonda: 10 kg mısır silajı, 6 kg yonca kuru otu, 4 kg saman ve 8 kg fabrika kesif yemi verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik", "dağ", "ova"],
                "content": "Hayvan Ceyhan ovasındaki (rakım ~50 metre) sabit besi ve süt tesisinde doğup büyümüştür. Herhangi bir yayla veya yüksek rakım nakli öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce"],
                "content": "Geçmişinde kaydedilmiş kronik bir mastitis veya metritis öyküsü bulunmamaktadır. 2 ay önce sorunsuz doğum yapmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "deri", "vital"],
                "content": "Vücut Sıcaklığı: 39.8 °C | Kalp Frekansı: 102 atım/dk | Solunum Frekansı: 42 nefes/dk | Mukoza: Soluk pembe | CRT: 2.5 saniye | Dehidrasyon: %6 | Göz Küresi: Belirgin çökmüş | Gerdan ve submandibuler bölgede soğuk hamur ödem | Vena jugularis stazı +, yalancı jugular nabız +."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Gaz ve pürülan sıvının çalkalanmasına bağlı çamaşır makinesi / su şılpırtısı (splashing) sesi ve boğuk kalp sesleri duyuluyor. Akciğer Oskültasyonu: Ventro-lateral alanlarda solunum sesleri hafif azalmış."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "hassasiyet", "inleme"],
                "content": "Sopa testi, kama testi ve Withers pinch (cidago sıkma) ağrı testlerinin tamamı Pozitif (+). Hayvan sırtını kamburlaştırıp inlemektedir."
            },
            "DEDEKTOR_MUAYENESI": {
                "name": "Metal Dedektör / Ferroskop Muayenesi",
                "keywords": ["dedektör", "dedektor", "metal", "ferroskop", "hauptner", "mıknatıs", "yabancı cisim"],
                "content": "Metal Dedektör (Ferroskop) Muayenesi: Retikulum / Sifoid kıkırdak bölgesi üzerinde Pozitif (+) şiddetli metalik sinyal ve ses reaksiyonu alındı."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "kan sayımı", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "monosit", "rdw", "mcv", "mch", "mchc", "plt", "trombosit", "eozinofil", "bazofil", "cbc"],
                "content": "Lökosit (WBC): 22.4 x10³/µL | Eritrosit (RBC): 5.4 x10⁶/µL | Hemoglobin (Hb): 9.2 g/dL | Hematokrit (PCV): %28 | MCV: 51.8 fL | MCH: 17.0 pg | MCHC: 32.8 g/dL | RDW: %16.2 | Nötrofil: %68 (Çok çekirdekli: %60, Bant: %8) | Lenfosit: %22 | Monosit: %6 | Eozinofil: %3 | Bazofil: %1 | Trombosit (PLT): 380 x10³/µL | Plazma Fibrinojeni: 1250 mg/dL | Total Protein: 7.9 g/dL | PP/F Oranı: 6.3."
            },
            "BIYOKIMYA_ALT": {"name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 22 U/L"},
            "BIYOKIMYA_AST": {"name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 118 U/L"},
            "BIYOKIMYA_GGT": {"name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 24 U/L"},
            "BIYOKIMYA_ALP": {"name": "ALP (Alkalen Fosfataz)", "keywords": ["alp"], "content": "ALP: 88 U/L"},
            "BIYOKIMYA_CK": {"name": "CK (Kreatin Kinaz)", "keywords": ["ck"], "content": "CK: 142 U/L"},
            "BIYOKIMYA_LDH": {"name": "LDH (Laktat Dehidrogenaz)", "keywords": ["ldh"], "content": "LDH: 980 U/L"},
            "BIYOKIMYA_BUN": {"name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre", "ure"], "content": "BUN: 28 mg/dL"},
            "BIYOKIMYA_KREATININ": {"name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 1.2 mg/dL"},
            "BIYOKIMYA_TROPONIN": {"name": "Kardiyak Troponin I (cTnI)", "keywords": ["troponin", "ctni"], "content": "Kardiyak Troponin I (cTnI): 0.85 ng/mL"},
            "BIYOKIMYA_ALBUMIN": {"name": "Serum Albümin (ALB)", "keywords": ["albümin", "albumin", "alb"], "content": "Serum Albümin (ALB): 2.4 g/dL"},
            "BIYOKIMYA_GLOBULIN": {"name": "Serum Globülin", "keywords": ["globülin", "globulin"], "content": "Serum Globülin: 5.5 g/dL"},
            "BIYOKIMYA_TP": {"name": "Serum Total Protein (TP)", "keywords": ["total protein", "tp"], "content": "Serum Total Protein (TP): 7.9 g/dL"},
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "üriner", "idrar tahlili", "dansite", "ph", "proteinuria", "hematüri", "bilirubinüri", "keton", "sediment"],
                "content": "Spesifik Gravite (Dansite): 1.022 | pH: 7.5 | Protein: + (Eser) | Glikoz: Negatif | Keton: Negatif | Bilirubin: Negatif | Lökosit: 2-4/Saha | Sediment: Nadir hyalin silindirler, skuamöz epitel hücreleri."
            },
            "GLUTERALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "gluteraldehit", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 2.5 dakikada pıhtılaşma (Pozitif)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "oksijen"],
                "content": "Kan pH: 7.32 | pO₂: 72 mmHg | pCO₂: 48 mmHg | HCO₃⁻: 20.2 mmol/L | Baz Açığı (BE): -4.1 mmol/L | Laktat: 2.8 mmol/L."
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG) Bulguları",
                "keywords": ["ultrason", "usg"],
                "content": "Ultrasonografi: Perikardiyal boşlukta fibrin bantları, gaz ekojeniteleri ve 4 cm sıvı birikimi. Retikulum çevresinde yapışıklıklar."
            },
            "PERIKARDIYOSENTEZ": {
                "name": "Perikardiyosentez Bulguları",
                "keywords": ["perikardiyosentez", "ponksiyon", "delme"],
                "content": "Perikardiyosentez: Kirli sarı-yeşil, pis kokulu pürülan eksuda."
            },
            "KULTUR": {
                "name": "Mikrobiyolojik Kültür",
                "keywords": ["kültür", "bakteri"],
                "content": "Mikrobiyolojik Kültür: Trueperella pyogenes üremesi."
            }
        }
    },
    "Vaka B (Yonca)": {
        "kod": "VAKA_B",
        "sikayet": "Hocam, Yonca üç hafta önce doğum yapmıştı. Doğumdan sonra rahminde iltihap oldu, iğne yaptırdık geçti derken şimdi hayvan bir haftadır dökülüyor. Ön sol ayağının bileği ve arka diz kapağı davul gibi şişti, üstüne basamıyor, topallıyor. Ateşi var gibi durduğu yerde tir tir titriyor, memeden süt tamamen çekildi...",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Irk & Yaş",
                "keywords": ["ağırlık", "agirllik", "kilo", "kaç kg", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 580 kg | Irk: Simental 🐄 | Yaş: 5 Yaşında (3. Laktasyonda)"
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu & Yem Tüketimi",
                "keywords": ["iştah", "istah", "yem yemiyor", "yeme", "yem reddi", "anoreksi", "süt", "iştahsızlık", "hiporeksi"],
                "content": "İştah Durumu: Şiddetli Hiporeksi (Yüksek febril ateş ve bakteriyel toksemi nedeniyle fabrika kesif yemini tamamen reddetmekte, yalnızca çok az miktarda yonca otu kemirmektedir)."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "süt"],
                "content": "Günlük rasyonda: 12 kg mısır silajı, 7 kg yonca kuru otu, 3 kg saman ve 9 kg süt yemi verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik"],
                "content": "Sabit süt işletmesinde barındırılmaktadır. Rakım değişikliği veya nakil öyküsü bulunmamaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce"],
                "content": "Yaklaşık 3 hafta önce doğum sonrası metritis (rahim iltihabı) ve klinik mastitis tedavisi görmüştür."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "eklem", "topallık", "bacak", "dehidrasyon"],
                "content": "Vücut Sıcaklığı: 40.2 °C | Kalp Frekansı: 110 atım/dk | Solunum Frekansı: 38 nefes/dk | Mukoza: Soluk | CRT: 3.0 saniye | Dehidrasyon: %4 | Göz Küresi: Hafif çökmüş | Gerdan ödemli | Sol carpus ve tarsus eklemlerinde sıcak, şiş ve ağrılı yapı."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "rall", "akciğer", "triküspid"],
                "content": "Kalp Oskültasyonu: Triküspid kapak odak sahası üzerinde Grade IV/VI holosistolik üfürüm duyulmaktadır. Su çalkantı (splashing) sesi YOKTUR. Vena jugularis dolgun ancak pulsasyon yoktur."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testleri (Sopa ve Kama) NEGATİF. Ön karın veya retikulum bölgesinde ağrı reaksiyonu yoktur."
            },
            "DEDEKTOR_MUAYENESI": {
                "name": "Metal Dedektör / Ferroskop Muayenesi",
                "keywords": ["dedektör", "dedektor", "metal", "ferroskop", "hauptner", "mıknatıs", "yabancı cisim"],
                "content": "Metal Dedektör (Ferroskop) Muayenesi: Negatif (-), retikulum veya ön karın bölgesinde metalik sinyal saptanmadı."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "kan sayımı", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "monosit", "rdw", "mcv", "mch", "mchc", "plt", "trombosit", "eozinofil", "bazofil", "cbc"],
                "content": "Lökosit (WBC): 26.8 x10³/µL | Eritrosit (RBC): 4.2 x10⁶/µL | Hemoglobin (Hb): 7.5 g/dL | Hematokrit (PCV): %22 | MCV: 52.3 fL | MCH: 17.8 pg | MCHC: 34.0 g/dL | RDW: %17.5 | Nötrofil: %72 | Lenfosit: %18 | Monosit: %7 | Eozinofil: %2 | Bazofil: %1 | Trombosit (PLT): 420 x10³/µL | Plazma Fibrinojeni: 980 mg/dL | Total Protein: 8.8 g/dL | PP/F Oranı: 8.98."
            },
            "BIYOKIMYA_ALT": {"name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 28 U/L"},
            "BIYOKIMYA_AST": {"name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 145 U/L"},
            "BIYOKIMYA_GGT": {"name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 28 U/L"},
            "BIYOKIMYA_BUN": {"name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre", "ure"], "content": "BUN: 34 mg/dL"},
            "BIYOKIMYA_KREATININ": {"name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 1.5 mg/dL"},
            "BIYOKIMYA_TROPONIN": {"name": "Kardiyak Troponin I (cTnI)", "keywords": ["troponin", "ctni"], "content": "Kardiyak Troponin I (cTnI): 1.20 ng/mL"},
            "BIYOKIMYA_ALBUMIN": {"name": "Serum Albümin (ALB)", "keywords": ["albümin", "albumin", "alb"], "content": "Serum Albümin (ALB): 2.3 g/dL"},
            "BIYOKIMYA_GLOBULIN": {"name": "Serum Globülin", "keywords": ["globülin", "globulin"], "content": "Serum Globülin: 6.5 g/dL"},
            "BIYOKIMYA_TP": {"name": "Serum Total Protein (TP)", "keywords": ["total protein", "tp"], "content": "Serum Total Protein (TP): 8.8 g/dL"},
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "üriner", "idrar tahlili", "dansite", "ph", "proteinuria", "hematüri", "bilirubinüri", "sediment"],
                "content": "Spesifik Gravite (Dansite): 1.020 | pH: 7.0 | Protein: ++ (Septik embolilere bağlı glomerülonefrit) | Glikoz: Negatif | Keton: Negatif | Eritrosit: 5-8/Saha (Mikrohematüri) | Lökosit: 6-10/Saha | Sediment: Granüler ve lökosit silindirleri."
            },
            "GLUTERALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "gluteraldehit", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 4.0 dakikada pıhtılaşma (Pozitif)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.30 | pO₂: 68 mmHg | pCO₂: 52 mmHg | HCO₃⁻: 18.8 mmol/L | Baz Açığı (BE): -5.2 mmol/L | Laktat: 3.1 mmol/L."
            },
            "EKOKARDIYOGRAFI": {
                "name": "Ekokardiyografi Bulguları",
                "keywords": ["ekokardiyografi", "eko", "vejetasyon"],
                "content": "Ekokardiyografi: Triküspid kapak üzerinde 3.5 cm çapında pürüzlü hiperekojen kitle (vejetasyon)."
            },
            "KULTUR": {
                "name": "Mikrobiyolojik Kültür",
                "keywords": ["kültür", "bakteri"],
                "content": "Kan Kültürü & Eklem Sıvısı Kültürü: Trueperella pyogenes üremesi."
            }
        }
    },
    "Vaka C (Zümrüt)": {
        "kod": "VAKA_C",
        "sikayet": "Hocam, biz üç hafta önce ovasından aldığımız düveleri yaylaya çıkarttık. Sürüdeki diğer hayvanlar dağ havasına uyum sağladı ama Zümrüt adındaki kızımız yokuş yukarı yürürken hemen tıkanıyor, dili dışarı sarkıyor. İki gündür ön göğsünün arası ile gerdanı torba gibi sarkıp şişmeye başladı. Ateşi yok ama çok çabuk yorulup olduğu yere çöküyor...",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Irk & Yaş",
                "keywords": ["ağırlık", "agirllik", "kilo", "kaç kg", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 460 kg | Irk: Montofon / Esmer Melez 🐄 | Yaş: 2.5 Yaşında (Düve)"
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu & Yem Tüketimi",
                "keywords": ["iştah", "istah", "yem yemiyor", "yeme", "yem reddi", "anoreksi", "süt", "iştahsızlık", "hiporeksi"],
                "content": "İştah Durumu: Orta Derecede Hiporeksi (Nefes darlığı ve egzersiz intoleransı nedeniyle mera otlamasını ve yemlik ziyaretini yarıya indirmiştir)."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj"],
                "content": "Çayır otunca zengin 1900 metre rakımlı dağ merasında otlatılmaktadır. İlave fabrika yemi verilmemektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik", "dağ", "ova", "metre"],
                "content": "Hayvan 3 hafta önce alçak rakımlı kıyı tesisinden Doğu Anadolu'daki 1900 metre rakımlı yüksek dağ yaylasına otlatılmak üzere nakledilmiştir."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce"],
                "content": "Geçmişinde kaydedilmiş hiçbir sistemik, metabolik veya enfeksiyöz hastalık öyküsü yoktur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "ödem"],
                "content": "Vücut Sıcaklığı: 38.6 °C | Kalp Frekansı: 96 atım/dk | Solunum Frekansı: 46 nefes/dk | Mukoza: Pembe | CRT: 1.8 saniye | Dehidrasyon: %0 | Göz Küresi: Çöküklük yok | Gerdanda geniş alana yayılmış soğuk hamur ödem | Vena jugularis dolgun."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Hiperdinamik güçlü kalp sesleri duyulmaktadır. Üfürüm veya su çalkantı sesi YOKTUR. Akciğer oskültasyonu hafiflemiş veziküler sestir."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testlerinin tamamı NEGATİF."
            },
            "DEDEKTOR_MUAYENESI": {
                "name": "Metal Dedektör / Ferroskop Muayenesi",
                "keywords": ["dedektör", "dedektor", "metal", "ferroskop", "hauptner", "mıknatıs", "yabancı cisim"],
                "content": "Metal Dedektör (Ferroskop) Muayenesi: Negatif (-), metalik sinyal alınmadı."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "kan sayımı", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "monosit", "rdw", "mcv", "mch", "mchc", "plt", "trombosit", "eozinofil", "bazofil", "cbc"],
                "content": "Lökosit (WBC): 7.2 x10³/µL | Eritrosit (RBC): 10.8 x10⁶/µL | Hemoglobin (Hb): 17.2 g/dL | Hematokrit (PCV): %54 | MCV: 50.0 fL | MCH: 15.9 pg | MCHC: 31.8 g/dL | RDW: %18.1 | Nötrofil: %54 | Lenfosit: %38 | Monosit: %5 | Eozinofil: %2 | Bazofil: %1 | Trombosit (PLT): 290 x10³/µL | Plazma Fibrinojeni: 320 mg/dL | Total Protein: 7.3 g/dL | PP/F Oranı: 22.8."
            },
            "BIYOKIMYA_ALT": {"name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 18 U/L"},
            "BIYOKIMYA_AST": {"name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 68 U/L"},
            "BIYOKIMYA_GGT": {"name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 18 U/L"},
            "BIYOKIMYA_BUN": {"name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre", "ure"], "content": "BUN: 18 mg/dL"},
            "BIYOKIMYA_KREATININ": {"name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 0.9 mg/dL"},
            "BIYOKIMYA_TROPONIN": {"name": "Kardiyak Troponin I (cTnI)", "keywords": ["troponin", "ctni"], "content": "Kardiyak Troponin I: 0.12 ng/mL"},
            "BIYOKIMYA_ALBUMIN": {"name": "Serum Albümin (ALB)", "keywords": ["albümin", "albumin", "alb"], "content": "Serum Albümin (ALB): 3.2 g/dL"},
            "BIYOKIMYA_GLOBULIN": {"name": "Serum Globülin", "keywords": ["globülin", "globulin"], "content": "Serum Globülin: 4.1 g/dL"},
            "BIYOKIMYA_TP": {"name": "Serum Total Protein (TP)", "keywords": ["total protein", "tp"], "content": "Serum Total Protein (TP): 7.3 g/dL"},
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "üriner", "idrar tahlili", "dansite", "ph", "proteinuria", "sediment"],
                "content": "Spesifik Gravite (Dansite): 1.025 | pH: 8.0 | Protein: Eser | Glikoz: Negatif | Keton: Negatif | Bilirubin: Negatif | Sediment: Fizyolojik temiz."
            },
            "GLUTERALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "gluteraldehit", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 12 dakikada pıhtılaşma yok (Negatif)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "oksijen", "hipoksi"],
                "content": "Kan pH: 7.36 | Kısmi Oksijen Basıncı (pO₂): 48 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 23.5 mmol/L | Baz Açığı: -0.8 mmol/L | Laktat: 1.5 mmol/L."
            },
            "EKOKARDIYOGRAFI": {
                "name": "Ekokardiyografi Bulguları",
                "keywords": ["ekokardiyografi", "eko", "pulmoner", "ventrikül"],
                "content": "Ekokardiyografi: Sağ ventrikül serbest duvar kalınlığında artış (Sağ Ventrikül Hipertrofisi), pulmoner arter çapında genişleme."
            },
            "KULTUR": {
                "name": "Mikrobiyolojik Kültür",
                "keywords": ["kültür", "bakteri"],
                "content": "Kültür: Kan ve perikard sıvısında bakteri üremesi YOKTUR (Steril)."
            }
        }
    },
    "Vaka D (Yiğit)": {
        "kod": "VAKA_D",
        "sikayet": "Hocam çabuk olun, besi padoğundaki Yiğit adındaki tosuna bir şeyler oldu! Ağzından burnundan fışkırır gibi taze kıpkırmızı kan geldi, ahırın duvarları kan içinde kaldı. Hayvanın gözlerinin akı bembeyaz kesildi, dışkısı da zift gibi simsiyah çıkıyor. Yemlikteki yeme hiç dokunmadı, olduğu yerde sendeleyip düşecek gibi duruyor...",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Irk & Yaş",
                "keywords": ["ağırlık", "agirllik", "kilo", "kaç kg", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 620 kg | Irk: Simental Besi Tosunu 🐂 | Yaş: 18 Aylık"
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu & Yem Tüketimi",
                "keywords": ["iştah", "istah", "yem yemiyor", "yeme", "yem reddi", "anoreksi", "süt", "iştahsızlık"],
                "content": "İştah Durumu: Komple Anoreksi (Akut masif iç kanama, pulmoner erozyon ve hipovolemik şok nedeniyle tam yem reddi)."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "besi", "kaba", "nişasta"],
                "content": "Günlük rasyonda: 10 kg mısır kırması, 10 kg arpa kırması, 5 kg yonca kuru otu, 2 kg saman verilmektedir. Yoğun yem oranı %80 seviyesindedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya"],
                "content": "Besi padoğunda barındırılmaktadır. Rakım değişikliği yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce", "asidoz", "şişkinlik", "timpani", "rumenitis"],
                "content": "Geçmişinde tekrarlayan akut/subakut rumen asidozu (yem çarpması) ve kronik hafif rumen timpani (şişkinlik) öyküsü vardır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "kan", "hemoptizi", "melena", "dışkı", "dehidrasyon"],
                "content": "Vücut Sıcaklığı: 39.2 °C | Kalp Frekansı: 118 atım/dk | Solunum Frekansı: 52 nefes/dk | Ağız/Burun: Köpüklü taze parlak kırmızı kan fışkırması (Hemoptizi) | Mukozalar: Bembeyaz | CRT: 4.0 saniye | Dehidrasyon: %8 | Göz Küresi: Belirgin çökmüş | Dışkı: Siyah katran kıvamında (Melena)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Taşikardik, zayıf düştü sesleri. Akciğer Oskültasyonu: Bilateral yaygın kaba raller ve hışırtı sesleri duyuluyor."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testleri NEGATİF."
            },
            "DEDEKTOR_MUAYENESI": {
                "name": "Metal Dedektör / Ferroskop Muayenesi",
                "keywords": ["dedektör", "dedektor", "metal", "ferroskop", "hauptner", "mıknatıs", "yabancı cisim"],
                "content": "Metal Dedektör (Ferroskop) Muayenesi: Negatif (-), metalik sinyal alınmadı."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "kan sayımı", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lenfosit", "monosit", "rdw", "mcv", "mch", "mchc", "plt", "trombosit", "eozinofil", "bazofil", "cbc"],
                "content": "Lökosit (WBC): 21.5 x10³/µL | Eritrosit (RBC): 2.1 x10⁶/µL | Hemoglobin (Hb): 4.2 g/dL | Hematokrit (PCV): %12 | MCV: 57.1 fL | MCH: 20.0 pg | MCHC: 35.0 g/dL | RDW: %19.8 | Nötrofil: %70 | Lenfosit: %20 | Monosit: %6 | Eozinofil: %3 | Bazofil: %1 | Trombosit (PLT): 110 x10³/µL | Plazma Fibrinojeni: 1050 mg/dL | Total Protein: 7.6 g/dL | PP/F: 7.23."
            },
            "BIYOKIMYA_ALT": {"name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 32 U/L"},
            "BIYOKIMYA_AST": {"name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 210 U/L"},
            "BIYOKIMYA_GGT": {"name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 68 U/L"},
            "BIYOKIMYA_BUN": {"name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre", "ure"], "content": "BUN: 42 mg/dL"},
            "BIYOKIMYA_KREATININ": {"name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 1.6 mg/dL"},
            "BIYOKIMYA_BILIRUBIN": {"name": "Bilirubin", "keywords": ["bilirubin"], "content": "Total Bilirubin: 1.2 mg/dL | İndirekt Bilirubin: 0.8 mg/dL"},
            "BIYOKIMYA_GLIKOZ": {"name": "Glikoz", "keywords": ["glikoz", "seker"], "content": "Glikoz: 88 mg/dL"},
            "BIYOKIMYA_ALBUMIN": {"name": "Serum Albümin (ALB)", "keywords": ["albümin", "albumin", "alb"], "content": "Serum Albümin (ALB): 2.5 g/dL"},
            "BIYOKIMYA_GLOBULIN": {"name": "Serum Globülin", "keywords": ["globülin", "globulin"], "content": "Serum Globülin: 5.1 g/dL"},
            "BIYOKIMYA_TP": {"name": "Serum Total Protein (TP)", "keywords": ["total protein", "tp"], "content": "Serum Total Protein (TP): 7.6 g/dL"},
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "üriner", "idrar tahlili", "dansite", "ph", "proteinuria", "sediment"],
                "content": "Spesifik Gravite (Dansite): 1.028 | pH: 7.2 | Protein: ++ | Bilirubin: + | Eritrosit: Eser | Keton: Negatif | Sediment: Hücresel kalıntılar."
            },
            "GLUTERALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "gluteraldehit", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 3.5 dakikada pıhtılaşma (Pozitif)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.24 | pO₂: 52 mmHg | pCO₂: 50 mmHg | HCO₃⁻: 18.5 mmol/L | Baz Açığı (BE): -6.2 mmol/L | Laktat: 4.2 mmol/L."
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG) Bulguları",
                "keywords": ["ultrason", "usg", "karaciğer", "apse", "vena cava", "trombüs"],
                "content": "Abdominal Ultrasonografi: Karaciğer parankiminde 6 cm çapında kılıflı apse odağı (Hepatic Abscess), Vena Cava Caudalis lümeninde tıkayıcı trombüs ekojenitesi. Torakal USG: Pulmoner arter çevresinde hematom ve anevrizma alanları."
            }
        }
    },
    "Vaka E (Kudret)": {
        "kod": "VAKA_E",
        "sikayet": "Hocam, bizim Kudret adındaki dana iki haftadır gözlerinin etrafından ve boynundan tüy dökmeye başladı. Dökülen yerler bozuk para gibi yuvarlak yuvarlak, üzeri gri beyaz kireç gibi kabuk bağladı. Hayvan kaşınmıyor ama ahırdaki diğer iki dana da aynı şekilde dökülmeye başladı...",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Irk & Yaş",
                "keywords": ["ağırlık", "agirllik", "kilo", "kaç kg", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 220 kg | Irk: Simental Melez Dana 🐂 | Yaş: 7 Aylık"
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu & Yem Tüketimi",
                "keywords": ["iştah", "istah", "yem yemiyor", "yeme", "yem reddi", "anoreksi", "süt", "iştahsızlık"],
                "content": "İştah Durumu: İştah TAMAMEN NORMAL (Derideki mantar lezyonları sistemik tutulum yapmadığı için yem ve su tüketimi mükemmeldir)."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "nem", "ışık", "karanlık", "hijyen", "kalabalık"],
                "content": "Karanlık, güneş almayan, nem oranı yüksek, havalandırması yetersiz ve genç danaların sıkışık barındırıldığı ahır ortamı."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "deri", "kabuk", "döküntü"],
                "content": "Vücut Sıcaklığı: 38.8 °C (Normal) | Kalp Frekansı: 78 atım/dk | Solunum Frekansı: 26 nefes/dk | Baş, göz çevresi ve boyunda dairesel, sınırları belirgin, gri-beyaz kireçimsi kabuklu lezyonlar. Kaşıntı minimaldir."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "cbc"],
                "content": "Lökosit (WBC): 8.1 x10³/µL | Eritrosit (RBC): 6.8 x10⁶/µL | Hemoglobin (Hb): 11.2 g/dL | Hematokrit (PCV): %34 | Plazma Fibrinojeni: 310 mg/dL | Nötrofil: %38 | Lenfosit: %54 | Eozinofil: %4 (Fizyolojik normal sınırlarda)."
            },
            "BIYOKIMYA_SERUM": {
                "name": "Serum Biyokimya Enzimleri",
                "keywords": ["alt", "ast", "ggt", "bun", "kreatinin", "tp", "albümin"],
                "content": "ALT: 21 U/L | AST: 62 U/L | GGT: 16 U/L | BUN: 14 mg/dL | Kreatinin: 0.8 mg/dL | Total Protein: 6.8 g/dL | Albümin: 3.2 g/dL (Tüm organ fonksiyonları tamamen normaldir)."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "üriner", "idrar tahlili", "dansite", "ph", "proteinuria", "sediment"],
                "content": "Spesifik Gravite (Dansite): 1.024 | pH: 8.0 | Protein: Negatif | Glikoz: Negatif | Keton: Negatif | Bilirubin: Negatif | Sediment: Temiz."
            },
            "DERI_KAZINTISI": {
                "name": "Deri Kazıntısı & Mikroskopik Mantar Muayenesi",
                "keywords": ["kazıntı", "mikroskop", "mantar", "koh", "hif", "spor", "ektotriks"],
                "content": "%10 KOH preparatında 40x büyütmede: Kıl şaftının dışını zırh gibi saran küresel ektotriks artrospor zincirleri ve hyalin mantar hifleri saptandı."
            },
            "WOOD_LAMBASI": {
                "name": "Wood Lambası (UV) Muayenesi",
                "keywords": ["wood", "uv", "floresan", "ışık"],
                "content": "Wood Lambası Muayenesi: Trichophyton verrucosum sporu karakteristik olarak floresans vermedi (Negatif / Zayıf floresans)."
            },
            "KULTUR_MANTAR": {
                "name": "Mantar Kültürü (Sabouraud Dextrose Agar)",
                "keywords": ["kültür", "sabouraud", "sda", "koloni"],
                "content": "Sabouraud Dextrose Agar (SDA) Kültürü: 37 °C'de 12 günde gelişen mumu andıran kabarık krem renkli Trichophyton verrucosum kolonileri."
            }
        }
    },
    "Vaka F (Nazar)": {
        "kod": "VAKA_F",
        "sikayet": "Hocam, Nazar isimli ineğimiz kendisini ahırın direklerine, yemlik kenarlarına sürtmekten helak oldu! Özellikle geceleri hiç durmuyor, sürtünmekten boynunun ve kuyruk sokumunun derisi kayış gibi sertleşip kıvrım kıvrım oldu. Üzerinde yara bere açıldı, tüyünden çok kel derisi kaldı...",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Irk & Yaş",
                "keywords": ["ağırlık", "agirllik", "kilo", "kaç kg", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 380 kg | Irk: Yerli Kara / Melez İnek 🐄 | Yaş: 4 Yaşında"
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu & Yem Tüketimi",
                "keywords": ["iştah", "istah", "yem yemiyor", "yeme", "yem reddi", "anoreksi", "süt", "iştahsızlık"],
                "content": "İştah Durumu: İştah Düzensiz / Azalmış (Gece boyu şiddetli kaşıntı nedeniyle uyuyamadığı ve sürekli huzursuz olduğu için yemliğe gitmeyi aksatmaktadır)."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "sürtünme", "direk", "hijyen", "kuyruk"],
                "content": "Ahır ahşap direklerinde yoğun tüy yumakları ve kanlı deri sürtünme izleri mevcut. Sürüde diğer 2 hayvanda da benzer kaşıntı başlamış."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "deri", "kaşıntı", "likenifikasyon"],
                "content": "Vücut Sıcaklığı: 38.9 °C | Kalp Frekansı: 82 atım/dk | Solunum Frekansı: 28 nefes/dk | Boyun, cidago ve kuyruk sokumunda deride aşırı kalınlaşma (likenifikasyon), kıvrımlaşma, eksudatif yaralar ve şiddetli pruritus (kaşıntı)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eozinofil", "rbc", "pcv", "cbc"],
                "content": "Lökosit (WBC): 12.8 x10³/µL | Eritrosit (RBC): 5.9 x10⁶/µL | Hemoglobin (Hb): 10.4 g/dL | Hematokrit (PCV): %31 | Plazma Fibrinojeni: 420 mg/dL | Nötrofil: %36 | Lenfosit: %44 | Eozinofil: %16 (Şiddetli Doku Eozinofilisi - Paraziter/Akar Reaksiyonu) | Monosit: %4."
            },
            "BIYOKIMYA_SERUM": {
                "name": "Serum Biyokimya Enzimleri",
                "keywords": ["alt", "ast", "ggt", "bun", "kreatinin", "tp", "albümin"],
                "content": "ALT: 24 U/L | AST: 71 U/L | GGT: 18 U/L | BUN: 16 mg/dL | Kreatinin: 0.9 mg/dL | Total Protein: 7.2 g/dL | Albümin: 3.1 g/dL."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "üriner", "idrar tahlili", "dansite", "ph", "proteinuria", "sediment"],
                "content": "Spesifik Gravite (Dansite): 1.022 | pH: 7.8 | Protein: Negatif | Glikoz: Negatif | Keton: Negatif | Bilirubin: Negatif | Sediment: Temiz."
            },
            "DERIN_DERI_KAZINTISI": {
                "name": "Derin Deri Kazıntısı & Akar Mikroskopisi",
                "keywords": ["kazıntı", "akar", "uyuz", "sarcoptes", "psoroptes", "mineral yağ", "mikroskop"],
                "content": "Kapiller kanama şekilleninceye kadar alınan derin deri kazıntısının mineral yağ altında 10x mikroskopisinde: Yuvarlak gövdeli, kısa bacaklı, canlı Sarcoptes scabiei var. bovis akarları ve yumurtaları saptandı."
            }
        }
    },
    "Vaka G (Çiçek)": {
        "kod": "VAKA_G",
        "sikayet": "Hocam, Çiçek'in alacalı beyaz yerlerine bir hal oldu! Siyah yerlerinde tık yok ama vücudundaki bütün beyaz deriler, burun üstü ve memedeki beyaz yerler davul gibi şişti, çatladı, kayış gibi soyulup kanamaya başladı. Hayvan güneşe çıkmak istemiyor, gölgeye kaçıyor...",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Irk & Yaş",
                "keywords": ["ağırlık", "agirllik", "kilo", "kaç kg", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 450 kg | Irk: Holstein Süt İneği 🐄 | Yaş: 3 Yaşında"
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu & Yem Tüketimi",
                "keywords": ["iştah", "istah", "yem yemiyor", "yeme", "yem reddi", "anoreksi", "süt", "iştahsızlık"],
                "content": "İştah Durumu: Komple Anoreksi ve Rumen Atonisi (Ağır karaciğer harabiyeti, filloeritrin toksisitesi ve derideki yanık ödemi ağrısı nedeniyle tam yem reddi)."
            },
            "AHIR_MERA_SARTLARI": {
                "name": "Mera & Otlatma Öyküsü",
                "keywords": ["mera", "otlatma", "ot", "bitki", "güneş", "gölge", "toksik"],
                "content": "Lantana camara ve Hypericum perforatum (Sarı kantaron) açısından zengin merada otlama öyküsü. Güneşe maruz kalma sonrası akut yanık reaksiyonu."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "ikter", "sarılık", "deri", "fotosensitizasyon", "beyaz"],
                "content": "Vücut Sıcaklığı: 39.6 °C | Kalp Frekansı: 94 atım/dk | Mukoza ve Skleralar: Belirgin İkterik (Sarımsı) | Sadece pigmentsiz (beyaz) deri alanlarında hamur ödemi, eritem, nekroz ve tabaka halinde deri soyulması. Siyah deri bölgeleri tamamen sağlamdır."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "rbc", "pcv", "cbc"],
                "content": "Lökosit (WBC): 16.4 x10³/µL | Eritrosit (RBC): 5.1 x10⁶/µL | Hemoglobin (Hb): 9.8 g/dL | Hematokrit (PCV): %30 | Plazma Fibrinojeni: 680 mg/dL | Nötrofil: %62 | Lenfosit: %30 | Monosit: %6 | Eozinofil: %2."
            },
            "BIYOKIMYA_KARACIGER": {
                "name": "Karaciğer Enzimleri & Bilirubin Paneli",
                "keywords": ["ggt", "ast", "alp", "bilirubin", "ikter", "karaciğer", "safra"],
                "content": "GGT: 185 U/L (Çok Yüksek / Kolestaz!) | AST: 340 U/L (Yüksek / Hepatosellüler Hasar) | ALP: 210 U/L | Total Bilirubin: 4.8 mg/dL | İndirekt Bilirubin: 3.2 mg/dL | Direct Bilirubin: 1.6 mg/dL | BUN: 22 mg/dL | Kreatinin: 1.0 mg/dL."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "üriner", "idrar tahlili", "dansite", "ph", "proteinuria", "bilirubinüri", "sediment"],
                "content": "Spesifik Gravite (Dansite): 1.026 | pH: 7.4 | Bilirubin: +++ (Koyu çay/kahverengi idrar - Konjuge bilirubinüri) | Ürobilinojen: Artmış | Protein: + | Glikoz: Negatif | Keton: Negatif | Sediment: Bilirubin kristalleri ve tübüler epitel hücreleri."
            },
            "ULTRASON_KARACIGER": {
                "name": "Abdominal Karaciğer USG",
                "keywords": ["ultrason", "usg", "karaciğer", "safra"],
                "content": "Abdominal USG: Karaciğer parankiminde diffüz hiperekojenite (Hepatik Steatoz/Hasar) ve safra kanallarında genişleme/kolestaz."
            }
        }
    },
    "Vaka H (Ateş)": {
        "kod": "VAKA_H",
        "sikayet": "Hocam, Ateş meradan geldikten bir saat sonra birdenbire bütün vücudu kabardı! Boynunda, böğründe, sırtında bozuk para büyüklüğünde ceviz gibi yumrular fırladı. Hayvan huzursuzca böğürüyor, göz kapakları ve dudakları şişti...",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Irk & Yaş",
                "keywords": ["ağırlık", "agirllik", "kilo", "kaç kg", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 510 kg | Irk: Şarole Melez Besi Tosunu 🐂 | Yaş: 14 Aylık"
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu & Yem Tüketimi",
                "keywords": ["iştah", "istah", "yem yemiyor", "yeme", "yem reddi", "anoreksi", "süt", "iştahsızlık"],
                "content": "İştah Durumu: Geçici İştahsızlık (Akut anafilaktoid ürtiker krizi, kutanöz ödem ve sistemik ajitasyon nedeniyle o an yemlikten uzak durmaktadır)."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "ürtiker", "kabartı", "plak", "ödem"],
                "content": "Vücut Sıcaklığı: 39.1 °C | Kalp Frekansı: 92 atım/dk | Solunum Frekansı: 36 nefes/dk | Tüm vücut yüzeyinde, boyun ve böğürde 2-5 cm çaplı, basmakla çökebilen eritematöz ödemli dermal plaklar (urticaria). Göz kapaklarında angioödem."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "eozinofil", "fibrinojen", "cbc"],
                "content": "Lökosit (WBC): 11.2 x10³/µL | Eritrosit (RBC): 6.2 x10⁶/µL | Hemoglobin (Hb): 11.8 g/dL | Hematokrit (PCV): %35 | Plazma Fibrinojeni: 340 mg/dL | Nötrofil: %42 | Lenfosit: %44 | Eozinofil: %12 (Akut Allerjik / Histaminik Yükselme)."
            },
            "BIYOKIMYA_SERUM": {
                "name": "Serum Biyokimya Enzimleri",
                "keywords": ["alt", "ast", "ggt", "bun", "kreatinin", "tp", "albümin"],
                "content": "ALT: 22 U/L | AST: 65 U/L | GGT: 17 U/L | BUN: 15 mg/dL | Kreatinin: 0.9 mg/dL | Total Protein: 7.0 g/dL | Albümin: 3.3 g/dL."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "üriner", "idrar tahlili", "dansite", "ph", "proteinuria", "sediment"],
                "content": "Spesifik Gravite (Dansite): 1.020 | pH: 7.5 | Protein: Negatif | Glikoz: Negatif | Keton: Negatif | Bilirubin: Negatif | Sediment: Normal."
            }
        }
    },
    "Vaka I (Fırtına)": {
        "kod": "VAKA_I",
        "sikayet": "Hocam, Fırtına isimli buzağımız dün geceden beri gırtlağından hırıl hırıl, düdük sesi gibi ses çıkararak nefes alıyor! Boynunu uzatmış hırlıyor. Boğazını tutunca acıyla peş peşe öksürüyor, ağzına yem alsa da yutamayıp yere düşürüyor...",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Irk & Yaş",
                "keywords": ["ağırlık", "agirllik", "kilo", "kaç kg", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 180 kg | Irk: Holstein Erkek Buzağı 🐄 | Yaş: 5 Aylık"
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu & Yem Tüketimi",
                "keywords": ["iştah", "istah", "yem yemiyor", "yeme", "yem reddi", "anoreksi", "süt", "iştahsızlık", "yutma"],
                "content": "İştah Durumu: Yutma Güçlüğü (Dysphagia) ve İştahsızlık (Gırtlağın şişmesi ve ağrısı nedeniyle lokmayı yutmaya çalışırken ağzından düşürmektedir)."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "toz", "rüzgar", "nakil", "amonyak"],
                "content": "Açık kasa kamyonla nakil sonrası tozlu saman yataklıklı ve yüksek amonyak birikimli buzağı bölmesinde barındırılmaktadır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "stridor", "gırtlak", "larenks", "ödem"],
                "content": "Vücut Sıcaklığı: 39.9 °C | Kalp Frekansı: 98 atım/dk | Solunum Frekansı: 44 nefes/dk | Belirgin inspiratorik dispne ve larengeal stridor (ıslık/horlama sesi). Gırtlak ve trakea palpasyonunda şiddetli ağrı ve öksürük krizi."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer", "larenks", "stridor"],
                "content": "Akciğer Oskültasyonu: Her iki akciğer sahasında veziküler solunum sesleri normaldir; ralli veya sessiz alan yoktur. Patoloji tamamen larenks ve üst trakeaya lokalizedir."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "rbc", "pcv", "cbc"],
                "content": "Lökosit (WBC): 15.8 x10³/µL | Eritrosit (RBC): 6.4 x10⁶/µL | Hemoglobin (Hb): 10.8 g/dL | Hematokrit (PCV): %32 | Plazma Fibrinojeni: 620 mg/dL | Nötrofil: %64 (Lokal reaksiyona bağlı ılımlı nötrofili) | Lenfosit: %30."
            },
            "BIYOKIMYA_SERUM": {
                "name": "Serum Biyokimya Enzimleri",
                "keywords": ["alt", "ast", "ggt", "bun", "kreatinin", "tp", "albümin"],
                "content": "ALT: 20 U/L | AST: 68 U/L | GGT: 15 U/L | BUN: 15 mg/dL | Kreatinin: 0.8 mg/dL | Total Protein: 7.0 g/dL | Albümin: 3.3 g/dL."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "üriner", "idrar tahlili", "dansite", "ph", "proteinuria", "sediment"],
                "content": "Spesifik Gravite (Dansite): 1.022 | pH: 7.6 | Protein: Negatif | Glikoz: Negatif | Keton: Negatif | Bilirubin: Negatif | Sediment: Normal."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.35 | pO₂: 82 mmHg | pCO₂: 44 mmHg | HCO₃⁻: 22.8 mmol/L | Baz Açığı: -1.2 mmol/L | Laktat: 1.8 mmol/L (Gaz alışverişi alveollerde tamamen sağlamdır)."
            },
            "ENDOSKOPI_GORUNTULEME": {
                "name": "Üst Solunum Yolu Endoskopisi & USG",
                "keywords": ["endoskopi", "larenks", "ödem", "ultrason", "usg"],
                "content": "Larengeal Endoskopi: Arytenoid kıkırdaklar ve plica vocalis üzerinde şiddetli hiperemi, ödem ve lümeni %60 daraltan nekrotik eksuda (Nekrotik Larenjit)."
            }
        }
    },
    "Vaka J (Şahin)": {
        "kod": "VAKA_J",
        "sikayet": "Hocam, Şahin'e bir ay önce boynuz kesimi yaptırmıştık. Yara kapandı sanıyorduk ama bir haftadır sol burun deliğinden leş gibi kokan sarı yeşil irin akıyor. Kafasını sola eğik tutuyor, sol gözünün üstüne basınca kaçıyor, sert yemleri çiğneyemiyor...",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Irk & Yaş",
                "keywords": ["ağırlık", "agirllik", "kilo", "kaç kg", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 560 kg | Irk: Simental Besi Tosunu 🐂 | Yaş: 20 Aylık"
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu & Yem Tüketimi",
                "keywords": ["iştah", "istah", "yem yemiyor", "yeme", "yem reddi", "anoreksi", "süt", "iştahsızlık"],
                "content": "İştah Durumu: İştah Seçici / Azalmış (Çiğneme kaslarındaki sinüs içi basınç ağrısı ve pürülan akıntı nedeniyle sert kaba yemleri reddetmektedir)."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Öykü & Boynuz Kesimi",
                "keywords": ["geçmiş", "boynuz", "kesim", "operasyon", "dehorning", "yara"],
                "content": "Yaklaşık 35 gün önce açık yöntemle boynuz kesimi (dehorning) yapılmış, sonrasında hijyenik olmayan tozlu ahıra alınmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "sinüs", "irin", "akıntı", "perküsyon"],
                "content": "Vücut Sıcaklığı: 39.4 °C | Kalp Frekansı: 88 atım/dk | Solunum Frekansı: 32 nefes/dk | Sol burun deliğinden koyu, fetid (pis kokulu) mukopürülan akıntı. Sol os frontale üzerine yapılan perküsyonda matite (doluluk sesi) ve şiddetli ağrı reaksiyonu."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "rbc", "pcv", "cbc"],
                "content": "Lökosit (WBC): 18.2 x10³/µL | Eritrosit (RBC): 5.8 x10⁶/µL | Hemoglobin (Hb): 10.2 g/dL | Hematokrit (PCV): %31 | Plazma Fibrinojeni: 780 mg/dL | Nötrofil: %68 (Sola Kayma / %6 Bant) | Lenfosit: %24."
            },
            "BIYOKIMYA_SERUM": {
                "name": "Serum Biyokimya Enzimleri",
                "keywords": ["alt", "ast", "ggt", "bun", "kreatinin", "tp", "albümin"],
                "content": "ALT: 24 U/L | AST: 72 U/L | GGT: 18 U/L | BUN: 18 mg/dL | Kreatinin: 1.0 mg/dL | Total Protein: 7.6 g/dL | Globülin: 4.8 g/dL."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "üriner", "idrar tahlili", "dansite", "ph", "proteinuria", "sediment"],
                "content": "Spesifik Gravite (Dansite): 1.025 | pH: 7.8 | Protein: Eser | Glikoz: Negatif | Keton: Negatif | Bilirubin: Negatif | Sediment: Normal."
            },
            "RONTGEN_GORUNTULEME": {
                "name": "Sinüs Radyografisi (X-Ray) & Trepanasyon",
                "keywords": ["röntgen", "x-ray", "sinüs", "trepanasyon", "akıntı"],
                "content": "Sinüs Radyografisi: Sinus frontalis sol kompartımanında artmış radyoopasite (sıvı/irin birikimi). Trepanasyon deliğinden kokulu pürülan eksuda tespiti."
            }
        }
    },
    "Vaka K (Rüzgar)": {
        "kod": "VAKA_K",
        "sikayet": "Hocam atımız Rüzgar durduğu yerde aniden burnundan foşur foşur taze kan akıtmaya başladı! Hiçbir darbe almadı. İki gündür samanı ağzına alıyor ama yutamıyor, lokmalar ve içtiği su burnundan geri çıkıyor...",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Irk & Yaş",
                "keywords": ["ağırlık", "agirllik", "kilo", "kaç kg", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 480 kg | Irk: İngiliz Atı 🐎 | Yaş: 7 Yaşında"
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu & Yem Tüketimi",
                "keywords": ["iştah", "istah", "yem yemiyor", "yeme", "yem reddi", "anoreksi", "süt", "iştahsızlık", "disfaji", "yutma"],
                "content": "İştah Durumu: Yutma Güçlüğü (Dysphagia) ve Yem Reddi (N. glossopharyngeus ve N. vagus felcine bağlı yutkunamama; gıdalar ve su burnundan geri akmaktadır)."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "kanama", "epistaksis", "burun", "disfaji"],
                "content": "Vücut Sıcaklığı: 38.2 °C (Normal) | Kalp Frekansı: 72 atım/dk (Anemiye bağlı taşikardik) | Solunum Frekansı: 24 nefes/dk | Mukoza: Soluk | Tek taraflı spontan taze kırmızı kanama (Epistaksis) ve gıdaların buruna geri kaçması (Nasal regurgitation)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "rbc", "pcv", "cbc", "anemi"],
                "content": "Lökosit (WBC): 11.4 x10³/µL | Eritrosit (RBC): 3.8 x10⁶/µL (Normositer Normokrom Anemi) | Hemoglobin (Hb): 6.8 g/dL | Hematokrit (PCV): %20 | Plazma Fibrinojeni: 410 mg/dL | Trombosit: 220 x10³/µL."
            },
            "BIYOKIMYA_SERUM": {
                "name": "Serum Biyokimya Enzimleri",
                "keywords": ["alt", "ast", "ggt", "bun", "kreatinin", "tp", "albümin"],
                "content": "ALT: 18 U/L | AST: 180 U/L | GGT: 22 U/L | BUN: 18 mg/dL | Kreatinin: 1.1 mg/dL | Total Protein: 6.2 g/dL | Albümin: 2.6 g/dL."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "üriner", "idrar tahlili", "dansite", "ph", "proteinuria", "sediment"],
                "content": "Spesifik Gravite (Dansite): 1.035 | pH: 7.5 | Protein: Negatif | Glikoz: Negatif | Keton: Negatif | Bilirubin: Negatif | Sediment: Kalsiyum karbonat kristalleri (Aygır/At idrarı için fizyolojik normal)."
            },
            "ENDOSKOPI_HAVA_KESESI": {
                "name": "Endoskopi (Guttural Pouch Endoscopy)",
                "keywords": ["endoskopi", "hava kesesi", "guttural", "mikoz", "aspergillus", "arteria carotis"],
                "content": "Hava Kesesi Endoskopisi: Sol hava kesesi (Guttural pouch) membranında Arteria carotis interna üzerinde siyah/kahverengi mantar plağı (Aspergillus fumigatus) ve pıhtılaşmış masif kan odakları tespiti."
            }
        }
    },
    "Vaka L (Poyraz)": {
        "kod": "VAKA_L",
        "sikayet": "Hocam, Poyraz geçen ay boğaz iltihabı (Gurm) geçirmişti. İyileşti demiştik ama iki haftadır kulaklarının altı, çene kemiğinin arkası davul gibi şişti. İki burnundan birden koyu koyu sarı irin akıyor. Başını öne uzatarak duruyor...",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık, Irk & Yaş",
                "keywords": ["ağırlık", "agirllik", "kilo", "kaç kg", "yaş", "ırk"],
                "content": "Canlı Ağırlık: 520 kg | Irk: Arap Atı 🐎 | Yaş: 5 Yaşında"
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu & Yem Tüketimi",
                "keywords": ["iştah", "istah", "yem yemiyor", "yeme", "yem reddi", "anoreksi", "süt", "iştahsızlık"],
                "content": "İştah Durumu: Çiğneme ve Yutma Ağrısına Bağlı Azalmış İştah (Parotis ve çene bölgesindeki kitle basısı nedeniyle yem yemekte zorlanmaktadır)."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Öykü & Gurm Enfeksiyonu",
                "keywords": ["geçmiş", "gurm", "streptococcus", "lenf nodu", "boğaz"],
                "content": "Yaklaşık 4 hafta önce Streptococcus equi subsp. equi kaynaklı Gurm (Strangles) hastalığı atlatmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "akıntı", "irin", "hava kesesi", "parotis"],
                "content": "Vücut Sıcaklığı: 39.2 °C | Kalp Frekansı: 68 atım/dk | Solunum Frekansı: 22 nefes/dk | Bilateral parotis bölgesinde sıcak, ağrılı şişlik. İki burun deliğinden koyu sarı, kokusuz mukopürülan akıntı. Baş ve boyun ekstansiyonda tutulmaktadır."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "rbc", "pcv", "cbc"],
                "content": "Lökosit (WBC): 22.8 x10³/µL | Eritrosit (RBC): 6.8 x10⁶/µL | Hemoglobin (Hb): 11.5 g/dL | Hematokrit (PCV): %34 | Plazma Fibrinojeni: 820 mg/dL | Nötrofil: %74 (Belirgin Lökositoz)."
            },
            "BIYOKIMYA_SERUM": {
                "name": "Serum Biyokimya Enzimleri",
                "keywords": ["alt", "ast", "ggt", "bun", "kreatinin", "tp", "albümin"],
                "content": "ALT: 22 U/L | AST: 110 U/L | GGT: 20 U/L | BUN: 19 mg/dL | Kreatinin: 1.0 mg/dL | Total Protein: 8.2 g/dL | Globülin: 5.2 g/dL (Hiperglobulinemi)."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "üriner", "idrar tahlili", "dansite", "ph", "proteinuria", "sediment"],
                "content": "Spesifik Gravite (Dansite): 1.032 | pH: 7.2 | Protein: + | Glikoz: Negatif | Keton: Negatif | Bilirubin: Negatif | Sediment: Normal at idrarı sedimantasyonu."
            },
            "ENDOSKOPI_GORUNTULEME": {
                "name": "Hava Kesesi Endoskopisi & Röntgen",
                "keywords": ["endoskopi", "hava kesesi", "empiyem", "kondroit", "streptococcus"],
                "content": "Endoskopi & Radyografi: Hava kesesi içinde sıvı-gaz seviyesi, keseyi dolduran pürülan eksuda ve alt tabanda taşlaşmış pürülan yumaklar (Chondroid / Kondroitler) saptandı."
            },
            "KULTUR": {
                "name": "Mikrobiyolojik Kültür",
                "keywords": ["kültür", "bakteri", "streptococcus"],
                "content": "Hava Kesesi Sıvısı Kültürü: Streptococcus equi subsp. equi üremesi."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnez & Bulgu Sorgulama Konsolu (Serbest Metin Sorgulama)</h3>", unsafe_allow_html=True)

# Select Case
selected_case_name = st.selectbox(
    "🔍 İncelemek İstediğiniz Vakayı Seçiniz:",
    options=list(CASES.keys()),
    index=0
)

active_case = CASES[selected_case_name]

st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — İlk Başvuru Şikayeti</div>", unsafe_allow_html=True)
st.info(f"**Hastanın Başvuru Şikayeti:** {active_case['sikayet']}")

# Session State for Questions History
if "history" not in st.session_state:
    st.session_state.history = {}

if selected_case_name not in st.session_state.history:
    st.session_state.history[selected_case_name] = []

# Question Input Section
st.markdown("### 💬 Sorunuzu veya İncelemek İstediğiniz Muayeneyi Yazınız:")

def match_query(user_text, categories_dict):
    text_clean = user_text.lower().strip()
    text_clean = text_clean.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    
    matched_cats = []
    
    for cat_key, cat_info in categories_dict.items():
        for kw in cat_info["keywords"]:
            kw_clean = kw.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
            if re.search(r'\b' + re.escape(kw_clean) + r'\b', text_clean) or kw_clean in text_clean:
                matched_cats.append(cat_key)
                break
                
    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız (Örn: İştah?, Ağırlık?, Ateş?, İdrar?, Hemogram?, ALT?, USG?):",
        key="query_input",
        placeholder="Örn: İştah?, Ağırlık?, Ateş?, İdrar?, Hemogram?, Dedektör?, GGT?..."
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
            st.success(f"🎉 Teşekkürler! Sorunuzla ilişkili {new_discoveries} yeni klinik bulgu / bilgi açığa çıkarıldı!")
        else:
            st.info("Bu soruyla ilgili bilgi zaten daha önce açığa çıkarılmıştı. Aşağıdaki keşifler listenizden okuyabilirsiniz.")
    else:
        st.warning("⚠️ Girdiğiniz soru veya kelimelerle eşleşen bir bilgi bulunamadı. Lütfen sorunuzu farklı anahtar kelimelerle yazınız (Örn: 'iştah', 'ağırlık', 'ateş', 'idrar', 'hemogram', 'biyokimya', 'kültür').")

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
                <div class='card-content'><b>🩺 Bulgu / Öykü:</b> {item['content']}</div>
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
