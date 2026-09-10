import streamlit as st
import re

# Page Config
st.set_page_config(
    page_title="VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu",
    page_icon="🐄",
    layout="wide",
)

# Custom Styling
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

# Complete Cases Knowledge Base
CASES = {
    "Vaka A (Papatya)": {
        "kod": "VAKA_A",
        "sikayet": "Gerdan ve çene altında soğuk ödem, iştahsızlık, belirgin süt verimi düşüşü ve durgunluk.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba yem"],
                "content": "Günlük rasyonda: 10 kg mısır silajı, 6 kg yonca kuru otu, 4 kg saman ve 8 kg fabrika kesif yemi verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik", "dağ", "ova"],
                "content": "Ceyhan Ovası (rakım ~50 metre). Sabit süt tesisi, rakım/yayla nakil öyküsü yok."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Anamnez",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi"],
                "content": "Geçmişinde kronik hastalık kaydı yoktur. 2 ay önce sorunsuz doğum yapmıştır."
            },
            "DEHIDRASYON": {
                "name": "Dehidrasyon & Deri Turgoru",
                "keywords": ["dehidrasyon", "deri kıvrımı", "deri turgoru", "göz çöküklüğü", "turgor"],
                "content": "Dehidrasyon: %6 | Deri kıvrım kalıcılık süresi: 6 saniye | Göz küresi çöküklüğü: 3 mm."
            },
            "ATES": {
                "name": "Vücut Sıcaklığı (Ateş)",
                "keywords": ["ateş", "sıcaklık", "derece", "rektal derece", "vücut sıcaklığı"],
                "content": "Vücut Sıcaklığı (T): 39.8 °C"
            },
            "NABIZ": {
                "name": "Kalp Frekansı (Nabız)",
                "keywords": ["nabız", "kalp frekansı", "atım"],
                "content": "Kalp Frekansı (HR): 102 atım/dakika"
            },
            "SOLUNUM": {
                "name": "Solunum Frekansı",
                "keywords": ["solunum", "solunum frekansı", "nefes"],
                "content": "Solunum Frekansı (RR): 42 nefes/dakika"
            },
            "MUKOZA_CRT": {
                "name": "Mukoza & CRT",
                "keywords": ["mukoza", "crt", "kılcal damar", "dolum süresi"],
                "content": "Mukoza: Soluk pembe | CRT (Kılcal Damar Dolum Süresi): 2.5 saniye"
            },
            "LENF_NODLARI": {
                "name": "Yüzeysel Lenf Yumruları",
                "keywords": ["lenf", "lenf nodu", "lenf yumrusu", "lnn", "prescapularis", "submandibularis", "prefemoralis"],
                "content": "Lnn. submandibularis, Lnn. prescapularis ve Lnn. prefemoralis simetrik, normal büyüklükte, ağrısız."
            },
            "RUMEN_ISTAH": {
                "name": "Rumen Motilitesi & İştah & Geviş",
                "keywords": ["rumen", "motilite", "iştah", "geviş", "ruminasyon", "kontraksiyon"],
                "content": "Rumen hareketi: 5 dakikada 1 kez (zayıf kontraksiyon) | İştah: Anoreksik | Geviş getirme: Yok."
            },
            "POSTUR_MIZAC": {
                "name": "Postür & Mizaç & Duruş",
                "keywords": ["postür", "duruş", "mizaç", "kambur", "durgunluk", "kifoz", "dirsek"],
                "content": "Duruş: Sırt kamburlaşmış (kifoz), dirsekler dışa açılmış, mizaç durgun, isteksiz."
            },
            "ODEM_JUGULARIS": {
                "name": "Ödem & Vena Jugularis",
                "keywords": ["ödem", "gerdan", "submandibuler", "jugularis", "staz", "boyun damarı"],
                "content": "Gerdan ve çene altında soğuk, hamur kıvamında ödem | Vena jugularis stazı (+), çene açısına kadar gergin, yalancı jugular nabız (+)."
            },
            "DISKI_IDRAR": {
                "name": "Dışkı ve İdrar Muayenesi",
                "keywords": ["dışkı", "idrar", "gaita", "melena"],
                "content": "Dışkı: Miktarı azalmış, koyu kıvamlı. İdrar: Normal görünümde."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı testleri", "retikulum ağrı", "pinch"],
                "content": "Sopa testi: Pozitif (+) | Kama testi: Pozitif (+) | Withers pinch (cidago sıkma) testi: Pozitif (+)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp sesleri", "oskültasyon", "üfürüm", "şılpırtı", "splashing", "boğuk", "akciğer sesleri"],
                "content": "Kalp Oskültasyonu: Su çalkantı (splashing) sesi ve boğuk kalp sesleri. Akciğer Oskültasyonu: Ventro-lateral alanlarda sesler hafif azalmış."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma süresi"],
                "content": "Glutaraldehit Testi: 2.5 dakikada pıhtılaşma (Pozitif)"
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "lökosit", "wbc", "kan sayımı", "fibrinojen", "pcv", "hematokrit", "eritrosit", "rbc", "pp/f"],
                "content": "Lökosit (WBC): 22.4 x10³/µL | Eritrosit (RBC): 5.4 x10⁶/µL | Hemoglobin (Hb): 9.2 g/dL | Hematokrit (PCV): %28 | Plazma Fibrinojeni: 1250 mg/dL | Total Protein: 7.9 g/dL | PP/F Oranı: 6.3 | Nötrofil: %74 | Lenfosit: %20."
            },
            "ALT": {"name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 22 U/L"},
            "AST": {"name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 118 U/L"},
            "GGT": {"name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 24 U/L"},
            "ALP": {"name": "ALP (Alkalen Fosfataz)", "keywords": ["alp"], "content": "ALP: 75 U/L"},
            "CK": {"name": "CK (Kreatin Kinaz)", "keywords": ["ck"], "content": "CK: 180 U/L"},
            "LDH": {"name": "LDH (Laktat Dehidrogenaz)", "keywords": ["ldh"], "content": "LDH: 360 U/L"},
            "BUN": {"name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre"], "content": "BUN: 28 mg/dL"},
            "KREATININ": {"name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 1.2 mg/dL"},
            "TROPONIN": {"name": "Kardiyak Troponin I", "keywords": ["troponin"], "content": "Kardiyak Troponin I (cTnI): 0.85 ng/mL"},
            "ALBUMIN": {"name": "Albümin", "keywords": ["albümin", "albumin"], "content": "Albümin: 2.8 g/dL"},
            "GLOBULIN": {"name": "Globülin", "keywords": ["globülin", "globulin"], "content": "Globülin: 5.1 g/dL"},
            "BILIRUBIN": {"name": "Bilirubin", "keywords": ["bilirubin"], "content": "Total Bilirubin: 0.4 mg/dL | İndirekt Bilirubin: 0.2 mg/dL"},
            "GLIKOZ": {"name": "Glikoz", "keywords": ["glikoz", "seker"], "content": "Glikoz: 68 mg/dL"},
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "laktat"],
                "content": "Kan pH: 7.32 | pO₂: 72 mmHg | pCO₂: 48 mmHg | HCO₃⁻: 20.2 mmol/L | Baz Açığı: -4.1 mmol/L | Laktat: 2.8 mmol/L"
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG)",
                "keywords": ["ultrason", "usg"],
                "content": "Ultrasonografi: Perikardiyal boşlukta fibrin bantları, gaz ekojeniteleri ve 4 cm sıvı birikimi. Retikulum çevresinde yapışıklıklar."
            },
            "PERIKARDIYOSENTEZ": {
                "name": "Perikardiyosentez",
                "keywords": ["perikardiyosentez", "ponksiyon", "delme"],
                "content": "Perikardiyosentez: Kirli sarı-yeşil, pürülan eksuda. Protein: 4.8 g/dL."
            },
            "KULTUR": {
                "name": "Mikrobiyolojik Kültür",
                "keywords": ["kültür", "bakteri", "mikrobiyoloji"],
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
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "süt yem"],
                "content": "Günlük rasyonda: 12 kg mısır silajı, 7 kg yonca kuru otu, 3 kg saman ve 9 kg süt yemi verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya"],
                "content": "Ceyhan Ovası (rakım ~50 metre). Sabit süt tesisi, rakım/yayla nakil öyküsü yok."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Anamnez",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi"],
                "content": "3 hafta önce doğum sonrası metritis ve klinik mastitis tedavisi görmüştür."
            },
            "DEHIDRASYON": {
                "name": "Dehidrasyon & Deri Turgoru",
                "keywords": ["dehidrasyon", "deri kıvrımı", "deri turgoru", "göz çöküklüğü", "turgor"],
                "content": "Dehidrasyon: %5 | Deri kıvrım kalıcılık süresi: 5 saniye | Göz küresi çöküklüğü: 2 mm."
            },
            "ATES": {
                "name": "Vücut Sıcaklığı (Ateş)",
                "keywords": ["ateş", "sıcaklık", "derece", "rektal derece", "vücut sıcaklığı"],
                "content": "Vücut Sıcaklığı (T): 40.2 °C"
            },
            "NABIZ": {
                "name": "Kalp Frekansı (Nabız)",
                "keywords": ["nabız", "kalp frekansı", "atım"],
                "content": "Kalp Frekansı (HR): 110 atım/dakika"
            },
            "SOLUNUM": {
                "name": "Solunum Frekansı",
                "keywords": ["solunum", "solunum frekansı", "nefes"],
                "content": "Solunum Frekansı (RR): 38 nefes/dakika"
            },
            "MUKOZA_CRT": {
                "name": "Mukoza & CRT",
                "keywords": ["mukoza", "crt", "kılcal damar", "dolum süresi"],
                "content": "Mukoza: Soluk | CRT: 3.0 saniye"
            },
            "LENF_NODLARI": {
                "name": "Yüzeysel Lenf Yumruları",
                "keywords": ["lenf", "lenf nodu", "lenf yumrusu", "lnn", "prescapularis", "submandibularis", "prefemoralis"],
                "content": "Lnn. prescapularis ve Lnn. prefemoralis hafif büyümüş, ağrısız."
            },
            "RUMEN_ISTAH": {
                "name": "Rumen Motilitesi & İştah & Geviş",
                "keywords": ["rumen", "motilite", "iştah", "geviş", "ruminasyon", "kontraksiyon"],
                "content": "Rumen hareketi: 5 dakikada 2 kez | İştah: İştahsız | Geviş getirme: Azalmış."
            },
            "POSTUR_MIZAC": {
                "name": "Postür & Mizaç & Duruş",
                "keywords": ["postür", "duruş", "mizaç", "kambur", "durgunluk", "topallık", "bacak"],
                "content": "Duruş: Sol ön ve arka bacağa yük vermekten kaçınıyor (topallık), mizaç düşkün."
            },
            "ODEM_JUGULARIS": {
                "name": "Ödem & Vena Jugularis",
                "keywords": ["ödem", "gerdan", "submandibuler", "jugularis", "staz", "boyun damarı"],
                "content": "Gerdan bölgesinde soğuk ödem | Vena jugularis dolgun, nabız yok."
            },
            "DISKI_IDRAR": {
                "name": "Dışkı ve İdrar Muayenesi",
                "keywords": ["dışkı", "idrar", "gaita", "melena"],
                "content": "Dışkı: Normal kıvam ve miktarda. İdrar: Normal görünümde."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı testleri", "retikulum ağrı", "pinch"],
                "content": "Sopa testi: Negatif (-) | Kama testi: Negatif (-) | Withers pinch testi: Negatif (-)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp sesleri", "oskültasyon", "üfürüm", "şılpırtı", "splashing", "boğuk", "akciğer sesleri"],
                "content": "Kalp Oskültasyonu: Triküspid kapak odağında Grade IV/VI holosistolik üfürüm. Akciğer Oskültasyonu: Normal veziküler sesler."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma süresi"],
                "content": "Glutaraldehit Testi: 4.0 dakikada pıhtılaşma (Pozitif)"
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "lökosit", "wbc", "kan sayımı", "fibrinojen", "pcv", "hematokrit", "eritrosit", "rbc", "pp/f"],
                "content": "Lökosit (WBC): 26.8 x10³/µL | Eritrosit (RBC): 4.2 x10⁶/µL | Hemoglobin (Hb): 7.2 g/dL | Hematokrit (PCV): %22 | Plazma Fibrinojeni: 980 mg/dL | Total Protein: 8.8 g/dL | PP/F Oranı: 8.98 | Nötrofil: %80 | Lenfosit: %15."
            },
            "ALT": {"name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 25 U/L"},
            "AST": {"name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 145 U/L"},
            "GGT": {"name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 28 U/L"},
            "ALP": {"name": "ALP (Alkalen Fosfataz)", "keywords": ["alp"], "content": "ALP: 82 U/L"},
            "CK": {"name": "CK (Kreatin Kinaz)", "keywords": ["ck"], "content": "CK: 210 U/L"},
            "LDH": {"name": "LDH (Laktat Dehidrogenaz)", "keywords": ["ldh"], "content": "LDH: 390 U/L"},
            "BUN": {"name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre"], "content": "BUN: 34 mg/dL"},
            "KREATININ": {"name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 1.5 mg/dL"},
            "TROPONIN": {"name": "Kardiyak Troponin I", "keywords": ["troponin"], "content": "Kardiyak Troponin I (cTnI): 1.20 ng/mL"},
            "ALBUMIN": {"name": "Albümin", "keywords": ["albümin", "albumin"], "content": "Albümin: 2.3 g/dL"},
            "GLOBULIN": {"name": "Globülin", "keywords": ["globülin", "globulin"], "content": "Globülin: 6.5 g/dL"},
            "BILIRUBIN": {"name": "Bilirubin", "keywords": ["bilirubin"], "content": "Total Bilirubin: 0.5 mg/dL | İndirekt Bilirubin: 0.3 mg/dL"},
            "GLIKOZ": {"name": "Glikoz", "keywords": ["glikoz", "seker"], "content": "Glikoz: 62 mg/dL"},
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "laktat"],
                "content": "Kan pH: 7.30 | pO₂: 68 mmHg | pCO₂: 52 mmHg | HCO₃⁻: 18.8 mmol/L | Baz Açığı: -5.2 mmol/L | Laktat: 3.1 mmol/L"
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG)",
                "keywords": ["ultrason", "usg"],
                "content": "Ultrasonografi: Triküspid kapak üzerinde 3.5 cm çapında pürüzlü hiperekojen kitle."
            },
            "EKOKARDIYOGRAFI": {
                "name": "Ekokardiyografi",
                "keywords": ["ekokardiyografi", "eko"],
                "content": "Ekokardiyografi: Triküspid kapak üzerinde 3.5 cm çapında kitle (vejetasyon)."
            },
            "PERIKARDIYOSENTEZ": {
                "name": "Perikardiyosentez",
                "keywords": ["perikardiyosentez", "ponksiyon", "delme"],
                "content": "Perikardiyosentez: Uygulanmadı / Sıvı birikimi yok."
            },
            "KULTUR": {
                "name": "Mikrobiyolojik Kültür",
                "keywords": ["kültür", "bakteri", "mikrobiyoloji"],
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
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik", "dağ"],
                "content": "3 hafta önce alçak rakımlı tesisten Doğu Anadolu'daki 1900 metre rakımlı yaylaya nakledilmiştir."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Anamnez",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi"],
                "content": "Geçmişinde kaydedilmiş herhangi bir hastalık öyküsü yoktur."
            },
            "DEHIDRASYON": {
                "name": "Dehidrasyon & Deri Turgoru",
                "keywords": ["dehidrasyon", "deri kıvrımı", "deri turgoru", "göz çöküklüğü", "turgor"],
                "content": "Dehidrasyon: %0 | Deri kıvrım kalıcılık süresi: 1 saniye | Göz küresi çöküklüğü: 0 mm."
            },
            "ATES": {
                "name": "Vücut Sıcaklığı (Ateş)",
                "keywords": ["ateş", "sıcaklık", "derece", "rektal derece", "vücut sıcaklığı"],
                "content": "Vücut Sıcaklığı (T): 38.6 °C"
            },
            "NABIZ": {
                "name": "Kalp Frekansı (Nabız)",
                "keywords": ["nabız", "kalp frekansı", "atım"],
                "content": "Kalp Frekansı (HR): 96 atım/dakika"
            },
            "SOLUNUM": {
                "name": "Solunum Frekansı",
                "keywords": ["solunum", "solunum frekansı", "nefes"],
                "content": "Solunum Frekansı (RR): 46 nefes/dakika"
            },
            "MUKOZA_CRT": {
                "name": "Mukoza & CRT",
                "keywords": ["mukoza", "crt", "kılcal damar", "dolum süresi"],
                "content": "Mukoza: Pembe | CRT: 1.8 saniye"
            },
            "LENF_NODLARI": {
                "name": "Yüzeysel Lenf Yumruları",
                "keywords": ["lenf", "lenf nodu", "lenf yumrusu", "lnn", "prescapularis", "submandibularis", "prefemoralis"],
                "content": "Tüm yüzeysel lenf düğümleri simetrik, normal büyüklükte ve ağrısız."
            },
            "RUMEN_ISTAH": {
                "name": "Rumen Motilitesi & İştah & Geviş",
                "keywords": ["rumen", "motilite", "iştah", "geviş", "ruminasyon", "kontraksiyon"],
                "content": "Rumen hareketi: 5 dakikada 3 kez | İştah: Azalmış | Geviş getirme: Var."
            },
            "POSTUR_MIZAC": {
                "name": "Postür & Mizaç & Duruş",
                "keywords": ["postür", "duruş", "mizaç", "kambur", "durgunluk"],
                "content": "Duruş: Normal, çabuk yorulma ve isteksizlik mevcut."
            },
            "ODEM_JUGULARIS": {
                "name": "Ödem & Vena Jugularis",
                "keywords": ["ödem", "gerdan", "submandibuler", "jugularis", "staz", "boyun damarı"],
                "content": "Göğüs önü ve gerdanda geniş alana yayılmış soğuk hamur ödem | Vena jugularis dolgun, nabız yok."
            },
            "DISKI_IDRAR": {
                "name": "Dışkı ve İdrar Muayenesi",
                "keywords": ["dışkı", "idrar", "gaita", "melena"],
                "content": "Dışkı ve İdrar: Normal miktar ve görünümde."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı testleri", "retikulum ağrı", "pinch"],
                "content": "Sopa testi: Negatif (-) | Kama testi: Negatif (-) | Withers pinch testi: Negatif (-)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp sesleri", "oskültasyon", "üfürüm", "şılpırtı", "splashing", "boğuk", "akciğer sesleri"],
                "content": "Kalp Oskültasyonu: Hiperdinamik güçlü kalp sesleri, üfürüm yok. Akciğer Oskültasyonu: Hafifletilmiş veziküler sesler."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma süresi"],
                "content": "Glutaraldehit Testi: 12 dakikadan uzun (Negatif / Pıhtılaşma yok)"
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "lökosit", "wbc", "kan sayımı", "fibrinojen", "pcv", "hematokrit", "eritrosit", "rbc", "pp/f"],
                "content": "Eritrosit (RBC): 10.8 x10⁶/µL | Hemoglobin (Hb): 17.2 g/dL | Hematokrit (PCV): %54 | Lökosit (WBC): 7.2 x10³/µL | Plazma Fibrinojeni: 320 mg/dL | Total Protein: 7.3 g/dL | PP/F Oranı: 22.8 | Nötrofil: %36 | Lenfosit: %58."
            },
            "ALT": {"name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 18 U/L"},
            "AST": {"name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 68 U/L"},
            "GGT": {"name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 18 U/L"},
            "ALP": {"name": "ALP (Alkalen Fosfataz)", "keywords": ["alp"], "content": "ALP: 62 U/L"},
            "CK": {"name": "CK (Kreatin Kinaz)", "keywords": ["ck"], "content": "CK: 110 U/L"},
            "LDH": {"name": "LDH (Laktat Dehidrogenaz)", "keywords": ["ldh"], "content": "LDH: 280 U/L"},
            "BUN": {"name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre"], "content": "BUN: 18 mg/dL"},
            "KREATININ": {"name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 0.9 mg/dL"},
            "TROPONIN": {"name": "Kardiyak Troponin I", "keywords": ["troponin"], "content": "Kardiyak Troponin I (cTnI): 0.12 ng/mL"},
            "ALBUMIN": {"name": "Albümin", "keywords": ["albümin", "albumin"], "content": "Albümin: 3.2 g/dL"},
            "GLOBULIN": {"name": "Globülin", "keywords": ["globülin", "globulin"], "content": "Globülin: 4.1 g/dL"},
            "BILIRUBIN": {"name": "Bilirubin", "keywords": ["bilirubin"], "content": "Total Bilirubin: 0.3 mg/dL | İndirekt Bilirubin: 0.2 mg/dL"},
            "GLIKOZ": {"name": "Glikoz", "keywords": ["glikoz", "seker"], "content": "Glikoz: 74 mg/dL"},
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "laktat"],
                "content": "Kan pH: 7.36 | pO₂: 48 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 23.5 mmol/L | Baz Açığı: -0.8 mmol/L | Laktat: 1.5 mmol/L"
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG)",
                "keywords": ["ultrason", "usg"],
                "content": "Ultrasonografi: Sağ ventrikül serbest duvarında kalınlaşma, pulmoner arter çapında genişleme."
            },
            "EKOKARDIYOGRAFI": {
                "name": "Ekokardiyografi",
                "keywords": ["ekokardiyografi", "eko"],
                "content": "Ekokardiyografi: Sağ ventrikül serbest duvar kalınlaşması."
            },
            "PERIKARDIYOSENTEZ": {
                "name": "Perikardiyosentez",
                "keywords": ["perikardiyosentez", "ponksiyon", "delme"],
                "content": "Perikardiyosentez: Seröz berrak sıvı. Protein: 1.2 g/dL."
            },
            "KULTUR": {
                "name": "Mikrobiyolojik Kültür",
                "keywords": ["kültür", "bakteri", "mikrobiyoloji"],
                "content": "Kan ve Sıvı Kültürü: Üreme yok (Steril)."
            }
        }
    },
    "Vaka D (Yiğit)": {
        "kod": "VAKA_D",
        "sikayet": "Burun deliklerinden ve ağızdan fışkırır tarzda taze parlak kırmızı kan gelmesi (hemoptizi) ve katran gibi siyah dışkı yapma.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "besi"],
                "content": "Günlük rasyonda: 10 kg mısır kırması, 10 kg arpa kırması, 5 kg yonca kuru otu ve 2 kg saman verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya"],
                "content": "Ceyhan Ovası (rakım ~50 metre). Sabit besi tesisi, rakım/yayla nakil öyküsü yok."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Anamnez",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "asidoz", "timpani"],
                "content": "Geçmişinde tekrarlayan akut/subakut rumen asidozu ve hafif timpani öyküsü vardır."
            },
            "DEHIDRASYON": {
                "name": "Dehidrasyon & Deri Turgoru",
                "keywords": ["dehidrasyon", "deri kıvrımı", "deri turgoru", "göz çöküklüğü", "turgor"],
                "content": "Dehidrasyon: %7 | Deri kıvrım kalıcılık süresi: 7 saniye | Göz küresi çöküklüğü: 4 mm."
            },
            "ATES": {
                "name": "Vücut Sıcaklığı (Ateş)",
                "keywords": ["ateş", "sıcaklık", "derece", "rektal derece", "vücut sıcaklığı"],
                "content": "Vücut Sıcaklığı (T): 39.2 °C"
            },
            "NABIZ": {
                "name": "Kalp Frekansı (Nabız)",
                "keywords": ["nabız", "kalp frekansı", "atım"],
                "content": "Kalp Frekansı (HR): 118 atım/dakika"
            },
            "SOLUNUM": {
                "name": "Solunum Frekansı",
                "keywords": ["solunum", "solunum frekansı", "nefes"],
                "content": "Solunum Frekansı (RR): 52 nefes/dakika"
            },
            "MUKOZA_CRT": {
                "name": "Mukoza & CRT",
                "keywords": ["mukoza", "crt", "kılcal damar", "dolum süresi"],
                "content": "Mukoza: Bembeyaz (soluk) | CRT: 4.0 saniye"
            },
            "LENF_NODLARI": {
                "name": "Yüzeysel Lenf Yumruları",
                "keywords": ["lenf", "lenf nodu", "lenf yumrusu", "lnn", "prescapularis", "submandibularis", "prefemoralis"],
                "content": "Tüm yüzeysel lenf düğümleri simetrik, normal büyüklükte ve ağrısız."
            },
            "RUMEN_ISTAH": {
                "name": "Rumen Motilitesi & İştah & Geviş",
                "keywords": ["rumen", "motilite", "iştah", "geviş", "ruminasyon", "kontraksiyon"],
                "content": "Rumen hareketi: 5 dakikada 1 kez | İştah: Anoreksik | Geviş getirme: Yok."
            },
            "POSTUR_MIZAC": {
                "name": "Postür & Mizaç & Duruş",
                "keywords": ["postür", "duruş", "mizaç", "kambur", "durgunluk"],
                "content": "Duruş: Baş aşağıda, düşkün mizaç, halsizlik."
            },
            "ODEM_JUGULARIS": {
                "name": "Ödem & Vena Jugularis",
                "keywords": ["ödem", "gerdan", "submandibuler", "jugularis", "staz", "boyun damarı"],
                "content": "Ödem yok | Vena jugularis hafif dolgun, nabız yok."
            },
            "DISKI_IDRAR": {
                "name": "Dışkı ve İdrar Muayenesi",
                "keywords": ["dışkı", "idrar", "gaita", "melena"],
                "content": "Dışkı: Siyah, katran kıvamında (melena). İdrar: Normal görünümde."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı testleri", "retikulum ağrı", "pinch"],
                "content": "Sopa testi: Negatif (-) | Kama testi: Negatif (-) | Withers pinch testi: Negatif (-)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp sesleri", "oskültasyon", "üfürüm", "şılpırtı", "splashing", "boğuk", "akciğer sesleri"],
                "content": "Kalp Oskültasyonu: Taşikardik zayıf düştü sesleri. Akciğer Oskültasyonu: Bilateral yaygın kaba raller ve hışırtı sesleri."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma süresi"],
                "content": "Glutaraldehit Testi: 3.5 dakikada pıhtılaşma (Pozitif)"
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "lökosit", "wbc", "kan sayımı", "fibrinojen", "pcv", "hematokrit", "eritrosit", "rbc", "pp/f"],
                "content": "Eritrosit (RBC): 2.1 x10⁶/µL | Hemoglobin (Hb): 4.2 g/dL | Hematokrit (PCV): %12 | Lökosit (WBC): 21.5 x10³/µL | Plazma Fibrinojeni: 1050 mg/dL | Total Protein: 7.6 g/dL | PP/F Oranı: 7.23 | Nötrofil: %78 | Lenfosit: %18."
            },
            "ALT": {"name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 45 U/L"},
            "AST": {"name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 210 U/L"},
            "GGT": {"name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 68 U/L"},
            "ALP": {"name": "ALP (Alkalen Fosfataz)", "keywords": ["alp"], "content": "ALP: 110 U/L"},
            "CK": {"name": "CK (Kreatin Kinaz)", "keywords": ["ck"], "content": "CK: 190 U/L"},
            "LDH": {"name": "LDH (Laktat Dehidrogenaz)", "keywords": ["ldh"], "content": "LDH: 410 U/L"},
            "BUN": {"name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre"], "content": "BUN: 42 mg/dL"},
            "KREATININ": {"name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 1.6 mg/dL"},
            "TROPONIN": {"name": "Kardiyak Troponin I", "keywords": ["troponin"], "content": "Kardiyak Troponin I (cTnI): 0.45 ng/mL"},
            "ALBUMIN": {"name": "Albümin", "keywords": ["albümin", "albumin"], "content": "Albümin: 2.6 g/dL"},
            "GLOBULIN": {"name": "Globülin", "keywords": ["globülin", "globulin"], "content": "Globülin: 5.0 g/dL"},
            "BILIRUBIN": {"name": "Bilirubin", "keywords": ["bilirubin"], "content": "Total Bilirubin: 1.2 mg/dL | İndirekt Bilirubin: 0.8 mg/dL"},
            "GLIKOZ": {"name": "Glikoz", "keywords": ["glikoz", "seker"], "content": "Glikoz: 88 mg/dL"},
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "laktat"],
                "content": "Kan pH: 7.24 | pO₂: 52 mmHg | pCO₂: 50 mmHg | HCO₃⁻: 18.5 mmol/L | Baz Açığı: -6.2 mmol/L | Laktat: 4.2 mmol/L"
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG)",
                "keywords": ["ultrason", "usg"],
                "content": "Abdominal Ultrasonografi: Karaciğer parankiminde 6 cm çapında kılıflı apse odağı, Vena Cava Caudalis lümeninde tıkayıcı trombüs ekojenitesi. Torakal USG: Pulmoner arter çevresinde hematom ve anevrizma alanları."
            },
            "PERIKARDIYOSENTEZ": {
                "name": "Perikardiyosentez",
                "keywords": ["perikardiyosentez", "ponksiyon", "delme"],
                "content": "Perikardiyosentez: Uygulanmadı / Sıvı birikimi yok."
            },
            "KULTUR": {
                "name": "Mikrobiyolojik Kültür",
                "keywords": ["kültür", "bakteri", "mikrobiyoloji"],
                "content": "Kan Kültürü: Üreme yok."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnezi & Bulgu Sorgulama Konsolu</h3>", unsafe_allow_html=True)

# Select Case
selected_case_name = st.selectbox(
    "🔍 İncelemek İstediğiniz Vakayı Seçiniz:",
    options=list(CASES.keys()),
    index=0
)

active_case = CASES[selected_case_name]

st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — İlk Başvuru Şikayeti</div>", unsafe_allow_html=True)
st.info(f"**Hastanın Başvuru Şikayeti:** {active_case['sikayet']}")

# Session State for History
if "history" not in st.session_state:
    st.session_state.history = {}

if selected_case_name not in st.session_state.history:
    st.session_state.history[selected_case_name] = []

# Exact Word Boundary Query Matcher
def match_query(user_text, categories_dict):
    text_clean = user_text.lower().strip()
    text_clean = text_clean.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    
    matched_cats = []
    
    for cat_key, cat_info in categories_dict.items():
        for kw in cat_info["keywords"]:
            kw_clean = kw.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
            pattern = r'\b' + re.escape(kw_clean) + r'\b'
            if re.search(pattern, text_clean):
                matched_cats.append(cat_key)
                break
                
    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız (Örn: Rasyon?, Ateş?, ALT?, AST?):",
        key="query_input",
        placeholder="Örn: Rasyon?, Ateş?, Dehidrasyon?, Hemogram?, ALT?..."
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
            st.success(f"🎉 {new_discoveries} yeni klinik bulgu / bilgi açığa çıkarıldı!")
        else:
            st.info("Bu bilgi zaten açığa çıkarılmıştı. Aşağıdaki listeden okuyabilirsiniz.")
    else:
        st.warning("⚠️ Eşleşen bir bilgi bulunamadı. Lütfen aradığınız kelimeyi doğrudan yazınız (Örn: 'Rasyon', 'Ateş', 'Dehidrasyon', 'Hemogram', 'ALT').")

# Display Discovered Items
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
    st.info("Henüz bu vaka için soru sormadınız. Arama kutusuna merak ettiğiniz kelimeyi yazarak muayeneye başlayınız.")

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
