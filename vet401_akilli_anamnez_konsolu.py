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
        "sikayet": "Gerdan ve çene altında soğuk ödem, iştahsızlık, belirgin süt verimi düşüşü ve durgunluk.",
        "categories": {
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
                "content": "Geçmişinde kaydedilmiş kronik bir mastitis, metritis veya metabolik hastalık öyküsü bulunmamaktadır. 2 ay önce sorunsuz doğum yapmıştır."
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
            "BIYOKIMYA_ALT": {
                "name": "ALT (Alanin Aminotransferaz)",
                "keywords": ["alt"],
                "content": "ALT: 22 U/L"
            },
            "BIYOKIMYA_AST": {
                "name": "AST (Aspartat Aminotransferaz)",
                "keywords": ["ast"],
                "content": "AST: 118 U/L"
            },
            "BIYOKIMYA_GGT": {
                "name": "GGT (Gama Glutamil Transferaz)",
                "keywords": ["ggt"],
                "content": "GGT: 24 U/L"
            },
            "BIYOKIMYA_ALP": {
                "name": "ALP (Alkalen Fosfataz)",
                "keywords": ["alp"],
                "content": "ALP: 88 U/L"
            },
            "BIYOKIMYA_CK": {
                "name": "CK (Kreatin Kinaz)",
                "keywords": ["ck"],
                "content": "CK: 142 U/L"
            },
            "BIYOKIMYA_LDH": {
                "name": "LDH (Laktat Dehidrogenaz)",
                "keywords": ["ldh"],
                "content": "LDH: 980 U/L"
            },
            "BIYOKIMYA_BUN": {
                "name": "BUN (Kan Üre Azotu)",
                "keywords": ["bun", "üre", "ure"],
                "content": "BUN: 28 mg/dL"
            },
            "BIYOKIMYA_KREATININ": {
                "name": "Kreatinin",
                "keywords": ["kreatinin"],
                "content": "Kreatinin: 1.2 mg/dL"
            },
            "BIYOKIMYA_TROPONIN": {
                "name": "Kardiyak Troponin I (cTnI)",
                "keywords": ["troponin", "ctni"],
                "content": "Kardiyak Troponin I (cTnI): 0.85 ng/mL"
            },
            "BIYOKIMYA_ALBUMIN": {
                "name": "Serum Albümin (ALB)",
                "keywords": ["albümin", "albumin", "alb"],
                "content": "Serum Albümin (ALB): 2.4 g/dL"
            },
            "BIYOKIMYA_GLOBULIN": {
                "name": "Serum Globülin",
                "keywords": ["globülin", "globulin"],
                "content": "Serum Globülin: 5.5 g/dL"
            },
            "BIYOKIMYA_TP": {
                "name": "Serum Total Protein (TP)",
                "keywords": ["total protein", "tp"],
                "content": "Serum Total Protein (TP): 7.9 g/dL"
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
        "sikayet": "Halsizlik, ciddi süt verimi düşüşü, bacak eklemlerinde şişlik ve belirgin topallık.",
        "categories": {
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
            "BIYOKIMYA_ALT": {
                "name": "ALT (Alanin Aminotransferaz)",
                "keywords": ["alt"],
                "content": "ALT: 28 U/L"
            },
            "BIYOKIMYA_AST": {
                "name": "AST (Aspartat Aminotransferaz)",
                "keywords": ["ast"],
                "content": "AST: 145 U/L"
            },
            "BIYOKIMYA_GGT": {
                "name": "GGT (Gama Glutamil Transferaz)",
                "keywords": ["ggt"],
                "content": "GGT: 28 U/L"
            },
            "BIYOKIMYA_BUN": {
                "name": "BUN (Kan Üre Azotu)",
                "keywords": ["bun", "üre", "ure"],
                "content": "BUN: 34 mg/dL"
            },
            "BIYOKIMYA_KREATININ": {
                "name": "Kreatinin",
                "keywords": ["kreatinin"],
                "content": "Kreatinin: 1.5 mg/dL"
            },
            "BIYOKIMYA_TROPONIN": {
                "name": "Kardiyak Troponin I (cTnI)",
                "keywords": ["troponin", "ctni"],
                "content": "Kardiyak Troponin I (cTnI): 1.20 ng/mL"
            },
            "BIYOKIMYA_ALBUMIN": {
                "name": "Serum Albümin (ALB)",
                "keywords": ["albümin", "albumin", "alb"],
                "content": "Serum Albümin (ALB): 2.3 g/dL"
            },
            "BIYOKIMYA_GLOBULIN": {
                "name": "Serum Globülin",
                "keywords": ["globülin", "globulin"],
                "content": "Serum Globülin: 6.5 g/dL"
            },
            "BIYOKIMYA_TP": {
                "name": "Serum Total Protein (TP)",
                "keywords": ["total protein", "tp"],
                "content": "Serum Total Protein (TP): 8.8 g/dL"
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
        "sikayet": "Göğüs önü ve gerdanda yaygın belirgin şişlik, çabuk yorulma ve hareket etmede isteksizlik.",
        "categories": {
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
            "BIYOKIMYA_ALT": {
                "name": "ALT (Alanin Aminotransferaz)",
                "keywords": ["alt"],
                "content": "ALT: 18 U/L"
            },
            "BIYOKIMYA_AST": {
                "name": "AST (Aspartat Aminotransferaz)",
                "keywords": ["ast"],
                "content": "AST: 68 U/L"
            },
            "BIYOKIMYA_GGT": {
                "name": "GGT (Gama Glutamil Transferaz)",
                "keywords": ["ggt"],
                "content": "GGT: 18 U/L"
            },
            "BIYOKIMYA_BUN": {
                "name": "BUN (Kan Üre Azotu)",
                "keywords": ["bun", "üre", "ure"],
                "content": "BUN: 18 mg/dL"
            },
            "BIYOKIMYA_KREATININ": {
                "name": "Kreatinin",
                "keywords": ["kreatinin"],
                "content": "Kreatinin: 0.9 mg/dL"
            },
            "BIYOKIMYA_TROPONIN": {
                "name": "Kardiyak Troponin I (cTnI)",
                "keywords": ["troponin", "ctni"],
                "content": "Kardiyak Troponin I: 0.12 ng/mL"
            },
            "BIYOKIMYA_ALBUMIN": {
                "name": "Serum Albümin (ALB)",
                "keywords": ["albümin", "albumin", "alb"],
                "content": "Serum Albümin (ALB): 3.2 g/dL"
            },
            "BIYOKIMYA_GLOBULIN": {
                "name": "Serum Globülin",
                "keywords": ["globülin", "globulin"],
                "content": "Serum Globülin: 4.1 g/dL"
            },
            "BIYOKIMYA_TP": {
                "name": "Serum Total Protein (TP)",
                "keywords": ["total protein", "tp"],
                "content": "Serum Total Protein (TP): 7.3 g/dL"
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
        "sikayet": "Burun deliklerinden ve ağızdan fışkırır tarzda taze parlak kırmızı kan gelmesi (hemoptizi) ve katran gibi siyah dışkı yapma.",
        "categories": {
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
            "BIYOKIMYA_ALT": {
                "name": "ALT (Alanin Aminotransferaz)",
                "keywords": ["alt"],
                "content": "ALT: 32 U/L"
            },
            "BIYOKIMYA_AST": {
                "name": "AST (Aspartat Aminotransferaz)",
                "keywords": ["ast"],
                "content": "AST: 210 U/L"
            },
            "BIYOKIMYA_GGT": {
                "name": "GGT (Gama Glutamil Transferaz)",
                "keywords": ["ggt"],
                "content": "GGT: 68 U/L"
            },
            "BIYOKIMYA_BUN": {
                "name": "BUN (Kan Üre Azotu)",
                "keywords": ["bun", "üre", "ure"],
                "content": "BUN: 42 mg/dL"
            },
            "BIYOKIMYA_KREATININ": {
                "name": "Kreatinin",
                "keywords": ["kreatinin"],
                "content": "Kreatinin: 1.6 mg/dL"
            },
            "BIYOKIMYA_BILIRUBIN": {
                "name": "Bilirubin",
                "keywords": ["bilirubin"],
                "content": "Total Bilirubin: 1.2 mg/dL | İndirekt Bilirubin: 0.8 mg/dL"
            },
            "BIYOKIMYA_GLIKOZ": {
                "name": "Glikoz",
                "keywords": ["glikoz", "seker"],
                "content": "Glikoz: 88 mg/dL"
            },
            "BIYOKIMYA_ALBUMIN": {
                "name": "Serum Albümin (ALB)",
                "keywords": ["albümin", "albumin", "alb"],
                "content": "Serum Albümin (ALB): 2.5 g/dL"
            },
            "BIYOKIMYA_GLOBULIN": {
                "name": "Serum Globülin",
                "keywords": ["globülin", "globulin"],
                "content": "Serum Globülin: 5.1 g/dL"
            },
            "BIYOKIMYA_TP": {
                "name": "Serum Total Protein (TP)",
                "keywords": ["total protein", "tp"],
                "content": "Serum Total Protein (TP): 7.6 g/dL"
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
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnezi & Bulgu Sorgulama Konsolu (Serbest Metin Sorgulama)</h3>", unsafe_allow_html=True)

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
        "Sorunuzu Buraya Yazınız (Örn: Rasyon?, Ateş?, ALT?, Monosit?, Dedektör?):",
        key="query_input",
        placeholder="Örn: Rasyon?, Ateş?, Hemogram?, Dedektör?, ALT?..."
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
            st.success(f"🎉 Teşekkürler! Sorunuzla ilişkili {new_discoveries} yeni klinik bulgu / bilgi açığa çıkarıldı!")
        else:
            st.info("Bu soruyla ilgili bilgi zaten daha önce açığa çıkarılmıştı. Aşağıdaki keşifler listenizden okuyabilirsiniz.")
    else:
        st.warning("⚠️ Girdiğiniz soru veya kelimelerle eşleşen bir bilgi bulunamadı. Lütfen sorunuzu farklı anahtar kelimelerle yazınız (Örn: 'rasyon', 'rakım', 'ateş', 'kalp sesleri', 'hemogram', 'dedektör', 'alt').")

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
