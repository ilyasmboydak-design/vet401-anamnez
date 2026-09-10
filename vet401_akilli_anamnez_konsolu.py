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

# Complete Cases Database with Zero Omission
CASES = {
    "Vaka A (Papatya)": {
        "kod": "VAKA_A",
        "sikayet": "Gerdan ve çene altında soğuk ödem, iştahsızlık, belirgin süt verimi düşüşü ve durgunluk.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba", "tel", "çivi", "yabancı"],
                "content": "Günlük rasyonda: 10 kg mısır silajı, 6 kg yonca kuru otu, 4 kg saman ve 8 kg fabrika kesif yemi verilmektedir. Balya parçalama esnasında kaba yeme inşaat tellerinin ve çivilerin karışmış olabileceği belirtilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik", "dağ", "ova", "metre"],
                "content": "Ceyhan ovasındaki (rakım ~50 metre) sabit süt tesisinde barındırılmaktadır. Yayla veya yüksek rakım nakli öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce"],
                "content": "Geçmişinde kaydedilmiş kronik bir mastitis, metritis veya metabolik hastalık öyküsü yoktur. 2 ay önce sorunsuz doğum yapmıştır."
            },
            "FIZIKSEL_MUAYENE_TAM": {
                "name": "Eksiksiz Tam Fiziksel Muayene Bulguları",
                "keywords": ["fiziksel muayene", "genel muayene", "tam muayene", "muayene bulguları", "fiziksel"],
                "content": "Vücut Sıcaklığı: 39.8 °C | Kalp Frekansı: 102 atım/dk | Solunum Frekansı: 42 nefes/dk | Mukoza Rengi ve Nemliliği: Soluk pembe, nemli | CRT: 2.5 saniye | Dehidrasyon Derecesi: %6 (Deri kıvrım kalıcılık süresi: 6 saniye, Göz küresi çökmüşlük: 3 mm) | Yüzeysel Lenf Yumruları: Lnn. submandibularis, Lnn. prescapularis ve Lnn. prefemoralis boyutları ve kıvamı normal, ağrısız | Rumen Hareketleri ve Tonusu: 5 dakikada 1 kez (hipomotil), kontraksiyon gücü zayıf | İştah ve Ruminasyon: İştah tamamen kayıp (anoreksi), geviş getirme durmuş | Postür ve Mizaç: Durgun, depresif, sırtını kamburlaştırarak durma (kifoz), dirsekleri dışa açarak durma | Gerdan, Çene Altı ve Göğüs Ödemi: Gerdan ve submandibuler bölgede soğuk, ağrısız, bastırılınca iz bırakan hamur kıvamında ödem | Vena Jugularis Muayenesi: Çene açısına kadar belirgin venöz dolgunluk (stazis) +, yalancı jugular nabız (pulsasyon) + | Dışkı ve İdrar Muayenesi: Dışkı miktarı azalmış, koyu kıvamlı ve pelet benzeri. İdrar miktarı ve rengi normal | Retikulum Ağrı Testleri: Sopa testi Pozitif (+), Kama testi Pozitif (+), Withers pinch Pozitif (+)."
            },
            "VITAL_ATEŞ": {
                "name": "Vücut Sıcaklığı (Ateş)",
                "keywords": ["ateş", "sıcaklık", "derece"],
                "content": "Vücut Sıcaklığı: 39.8 °C"
            },
            "VITAL_NABIZ": {
                "name": "Kalp Frekansı (Nabız)",
                "keywords": ["nabız", "kalp frekansı", "hr"],
                "content": "Kalp Frekansı: 102 atım/dakika"
            },
            "VITAL_SOLUNUM": {
                "name": "Solunum Frekansı",
                "keywords": ["solunum", "solunum frekansı", "rr", "nefes"],
                "content": "Solunum Frekansı: 42 nefes/dakika"
            },
            "VITAL_DEHIDRASYON": {
                "name": "Dehidrasyon Derecesi & Deri Turgoru",
                "keywords": ["dehidrasyon", "deri", "göz küresi", "turgor", "elastikiyet"],
                "content": "Dehidrasyon Derecesi: %6 (Deri kıvrım kalıcılık süresi: 6 saniye, Göz küresi çökmüşlük: 3 mm)"
            },
            "VITAL_MUKOZA": {
                "name": "Mukoza Rengi ve Nemliliği",
                "keywords": ["mukoza", "ağız mukozası", "göz mukozası"],
                "content": "Mukoza Rengi ve Nemliliği: Soluk pembe, nemli"
            },
            "VITAL_CRT": {
                "name": "Kılcal Damar Dolum Süresi (CRT)",
                "keywords": ["crt", "kılcal damar", "dolum süresi"],
                "content": "Kılcal Damar Dolum Süresi (CRT): 2.5 saniye"
            },
            "VITAL_LENF": {
                "name": "Yüzeysel Lenf Yumruları",
                "keywords": ["lenf", "lenf nodu", "lenf yumrusu", "lnn"],
                "content": "Yüzeysel Lenf Yumruları: Lnn. submandibularis, Lnn. prescapularis ve Lnn. prefemoralis boyutları ve kıvamı normal, ağrısız"
            },
            "VITAL_RUMEN": {
                "name": "Rumen Hareketleri ve Tonusu",
                "keywords": ["rumen", "rumen hareketi", "tonus", "kontraksiyon"],
                "content": "Rumen Hareketleri ve Tonusu: 5 dakikada 1 kez (hipomotil), kontraksiyon gücü zayıf"
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Gaz ve pürülan sıvının çalkalanmasına bağlı çamaşır makinesi / su şılpırtısı (splashing) sesi ve boğuk kalp sesleri. Akciğer Oskültasyonu: Ventro-lateral alanlarda solunum sesleri azalmış."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "hassasiyet"],
                "content": "Sopa testi Pozitif (+), Kama testi Pozitif (+), Withers pinch (cidago sıkma) Pozitif (+)."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma", "pıhtı"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 2.5 dakikada pıhtılaşma"
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayımı", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "cbc", "nötrofil"],
                "content": "Lökosit (WBC): 22.4 x10³/µL | Eritrosit (RBC): 5.4 x10⁶/µL | Hemoglobin (Hb): 9.2 g/dL | Hematokrit (PCV): %28 | Band Nötrofil: %12 | Segmenter Nötrofil: %62 | Lenfosit: %20 | Monosit: %4 | Eozinofil: %2 | Plazma Fibrinojeni: 1250 mg/dL | Total Protein: 7.9 g/dL | PP/F Oranı: 6.3."
            },
            "BIO_ALT": { "name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 22 U/L" },
            "BIO_AST": { "name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 118 U/L" },
            "BIO_GGT": { "name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 24 U/L" },
            "BIO_ALP": { "name": "ALP (Alkalen Fosfataz)", "keywords": ["alp"], "content": "ALP: 75 U/L" },
            "BIO_CK":  { "name": "CK (Kreatin Kinaz)", "keywords": ["ck"], "content": "CK: 180 U/L" },
            "BIO_LDH": { "name": "LDH (Laktat Dehidrogenaz)", "keywords": ["ldh"], "content": "LDH: 360 U/L" },
            "BIO_BUN": { "name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre"], "content": "BUN: 28 mg/dL" },
            "BIO_KREATININ": { "name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 1.2 mg/dL" },
            "BIO_TROPONIN": { "name": "Kardiyak Troponin I", "keywords": ["troponin"], "content": "Kardiyak Troponin I (cTnI): 0.85 ng/mL" },
            "BIO_ALBUMIN": { "name": "Albümin", "keywords": ["albümin", "albumin"], "content": "Albümin: 2.8 g/dL" },
            "BIO_GLOBULIN": { "name": "Globülin", "keywords": ["globülin", "globulin"], "content": "Globülin: 5.1 g/dL" },
            "BIO_BILIRUBIN": { "name": "Bilirubin", "keywords": ["bilirubin"], "content": "Total Bilirubin: 0.4 mg/dL | İndirekt Bilirubin: 0.2 mg/dL" },
            "BIO_GLIKOZ": { "name": "Glikoz", "keywords": ["glikoz", "seker"], "content": "Glikoz: 68 mg/dL" },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "laktat"],
                "content": "Kan pH: 7.32 | pO₂: 72 mmHg | pCO₂: 48 mmHg | HCO₃⁻: 20.2 mmol/L | Baz Açığı: -4.1 mmol/L | Laktat: 2.8 mmol/L."
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG) Bulgusu",
                "keywords": ["ultrason", "usg"],
                "content": "Ultrasonografi: Perikardiyal boşlukta 4 cm kalınlığında sıvı birikimi, fibrin bantları ve hiperekojen gaz noktaları. Retikulum çevresinde yapışıklıklar."
            },
            "EKOKARDIYOGRAFI": {
                "name": "Ekokardiyografi Bulgusu",
                "keywords": ["eko", "ekokardiyografi"],
                "content": "Ekokardiyografi: Perikardiyal kesede sıvı ve fibrin birikimi, ventrikül dolumunda kısıtlanma."
            },
            "PERIKARDIYOSENTEZ": {
                "name": "Perikardiyosentez Bulgusu",
                "keywords": ["perikardiyosentez", "ponksiyon", "delme"],
                "content": "Perikardiyosentez: Kirli sarı-yeşil, pis kokulu pürülan eksuda, protein miktarı 4.8 g/dL."
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
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya"],
                "content": "Sabit süt işletmesinde barındırılmaktadır. Rakım değişikliği veya nakil öyküsü bulunmamaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce"],
                "content": "Yaklaşık 3 hafta önce doğum sonrası pürülan metritis ve klinik mastitis tedavisi görmüştür."
            },
            "FIZIKSEL_MUAYENE_TAM": {
                "name": "Eksiksiz Tam Fiziksel Muayene Bulguları",
                "keywords": ["fiziksel muayene", "genel muayene", "tam muayene", "muayene bulguları", "fiziksel"],
                "content": "Vücut Sıcaklığı: 40.2 °C | Kalp Frekansı: 110 atım/dk | Solunum Frekansı: 38 nefes/dk | Mukoza Rengi ve Nemliliği: Soluk, hafif kuru | CRT: 3.0 saniye | Dehidrasyon Derecesi: %5 (Deri kıvrım kalıcılık süresi: 5 saniye, Göz küresi çökmüşlük: 2 mm) | Yüzeysel Lenf Yumruları: Lnn. prescapularis ve Lnn. prefemoralis hafif büyümüş ve simetrik | Rumen Hareketleri ve Tonusu: 5 dakikada 2 kez | İştah ve Ruminasyon: İştah azalmış, geviş getirme düzensiz | Postür, Mizaç ve Eklem Bulguları: Sol carpus ve tarsus eklemlerinde sıcaklık, şişlik ve ağrı, belirgin topallık | Gerdan, Çene Altı Ödemi: Gerdan bölgesinde ödem mevcut | Vena Jugularis Muayenesi: Jugular ven dolgun, pulsasyon yok | Dışkı ve İdrar Muayenesi: Dışkı miktarı hafif azalmış, idrar bulanık ve koyu sarı | Retikulum Ağrı Testleri: Sopa testi Negatif (-), Kama testi Negatif (-)."
            },
            "VITAL_ATEŞ": { "name": "Vücut Sıcaklığı (Ateş)", "keywords": ["ateş", "sıcaklık", "derece"], "content": "Vücut Sıcaklığı: 40.2 °C" },
            "VITAL_NABIZ": { "name": "Kalp Frekansı (Nabız)", "keywords": ["nabız", "kalp frekansı", "hr"], "content": "Kalp Frekansı: 110 atım/dakika" },
            "VITAL_SOLUNUM": { "name": "Solunum Frekansı", "keywords": ["solunum", "solunum frekansı", "rr", "nefes"], "content": "Solunum Frekansı: 38 nefes/dakika" },
            "VITAL_DEHIDRASYON": { "name": "Dehidrasyon Derecesi & Deri Turgoru", "keywords": ["dehidrasyon", "deri", "göz küresi", "turgor", "elastikiyet"], "content": "Dehidrasyon Derecesi: %5 (Deri kıvrım kalıcılık süresi: 5 saniye, Göz küresi çökmüşlük: 2 mm)" },
            "VITAL_MUKOZA": { "name": "Mukoza Rengi ve Nemliliği", "keywords": ["mukoza", "ağız mukozası", "göz mukozası"], "content": "Mukoza Rengi ve Nemliliği: Soluk, hafif kuru" },
            "VITAL_CRT": { "name": "Kılcal Damar Dolum Süresi (CRT)", "keywords": ["crt", "kılcal damar", "dolum süresi"], "content": "Kılcal Damar Dolum Süresi (CRT): 3.0 saniye" },
            "VITAL_LENF": { "name": "Yüzeysel Lenf Yumruları", "keywords": ["lenf", "lenf nodu", "lenf yumrusu", "lnn"], "content": "Yüzeysel Lenf Yumruları: Lnn. prescapularis ve Lnn. prefemoralis hafif büyümüş ve simetrik" },
            "VITAL_RUMEN": { "name": "Rumen Hareketleri ve Tonusu", "keywords": ["rumen", "rumen hareketi", "tonus"], "content": "Rumen Hareketleri ve Tonusu: 5 dakikada 2 kez" },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "boğuk", "rall", "akciğer", "triküspid"],
                "content": "Kalp Oskültasyonu: Triküspid kapak odak sahası üzerinde Grade IV/VI holosistolik üfürüm. Su çalkantı sesi yok. Akciğer Oskültasyonu: Normal veziküler sesler."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Sopa testi Negatif (-), Kama testi Negatif (-)."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma", "pıhtı"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 4.0 dakikada pıhtılaşma"
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayımı", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "cbc"],
                "content": "Lökosit (WBC): 26.8 x10³/µL | Eritrosit (RBC): 4.2 x10⁶/µL | Hemoglobin (Hb): 7.2 g/dL | Hematokrit (PCV): %22 | Band Nötrofil: %15 | Segmenter Nötrofil: %65 | Lenfosit: %15 | Monosit: %4 | Eozinofil: %1 | Plazma Fibrinojeni: 980 mg/dL | Total Protein: 8.8 g/dL | PP/F Oranı: 8.98."
            },
            "BIO_ALT": { "name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 25 U/L" },
            "BIO_AST": { "name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 145 U/L" },
            "BIO_GGT": { "name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 28 U/L" },
            "BIO_ALP": { "name": "ALP (Alkalen Fosfataz)", "keywords": ["alp"], "content": "ALP: 82 U/L" },
            "BIO_CK":  { "name": "CK (Kreatin Kinaz)", "keywords": ["ck"], "content": "CK: 210 U/L" },
            "BIO_LDH": { "name": "LDH (Laktat Dehidrogenaz)", "keywords": ["ldh"], "content": "LDH: 390 U/L" },
            "BIO_BUN": { "name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre"], "content": "BUN: 34 mg/dL" },
            "BIO_KREATININ": { "name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 1.5 mg/dL" },
            "BIO_TROPONIN": { "name": "Kardiyak Troponin I", "keywords": ["troponin"], "content": "Kardiyak Troponin I (cTnI): 1.20 ng/mL" },
            "BIO_ALBUMIN": { "name": "Albümin", "keywords": ["albümin", "albumin"], "content": "Albümin: 2.3 g/dL" },
            "BIO_GLOBULIN": { "name": "Globülin", "keywords": ["globülin", "globulin"], "content": "Globülin: 6.5 g/dL" },
            "BIO_BILIRUBIN": { "name": "Bilirubin", "keywords": ["bilirubin"], "content": "Total Bilirubin: 0.5 mg/dL | İndirekt Bilirubin: 0.3 mg/dL" },
            "BIO_GLIKOZ": { "name": "Glikoz", "keywords": ["glikoz", "seker"], "content": "Glikoz: 62 mg/dL" },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "laktat"],
                "content": "Kan pH: 7.30 | pO₂: 68 mmHg | pCO₂: 52 mmHg | HCO₃⁻: 18.8 mmol/L | Baz Açığı: -5.2 mmol/L | Laktat: 3.1 mmol/L."
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG) Bulgusu",
                "keywords": ["ultrason", "usg"],
                "content": "Ultrasonografi: Perikardiyumda sıvı yok. Sol carpus eklem boşluğunda genişleme ve eklem sıvısında artış."
            },
            "EKOKARDIYOGRAFI": {
                "name": "Ekokardiyografi Bulgusu",
                "keywords": ["eko", "ekokardiyografi"],
                "content": "Ekokardiyografi: Triküspid kapak üzerinde 3.5 cm çapında pürüzlü hiperekojen kitle (vejetasyon)."
            },
            "PERIKARDIYOSENTEZ": {
                "name": "Perikardiyosentez Bulgusu",
                "keywords": ["perikardiyosentez", "ponksiyon", "delme"],
                "content": "Perikardiyosentez: Sıvı alınamadı (Efüzyon yok)."
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
                "content": "3 hafta önce alçak rakımlı kıyı tesisinden Doğu Anadolu'daki 1900 metre rakımlı yüksek dağ yaylasına nakledilmiştir."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce"],
                "content": "Geçmişinde kaydedilmiş hiçbir sistemik, metabolik veya enfeksiyöz hastalık öyküsü yoktur."
            },
            "FIZIKSEL_MUAYENE_TAM": {
                "name": "Eksiksiz Tam Fiziksel Muayene Bulguları",
                "keywords": ["fiziksel muayene", "genel muayene", "tam muayene", "muayene bulguları", "fiziksel"],
                "content": "Vücut Sıcaklığı: 38.6 °C | Kalp Frekansı: 96 atım/dk | Solunum Frekansı: 46 nefes/dk | Mukoza Rengi ve Nemliliği: Pembe, nemli | CRT: 1.8 saniye | Dehidrasyon Derecesi: %0 (Deri kıvrım kalıcılık süresi: 1 saniye, Göz küresi çöküklüğü yok) | Yüzeysel Lenf Yumruları: Tüm yüzeysel lenf yumruları normal büyüklükte ve yapıda | Rumen Hareketleri ve Tonusu: 5 dakikada 3 kez, normal tonusta | İştah ve Ruminasyon: İştah hafif azalmış, geviş getirme var | Postür ve Dış Görünüm: Hareket etmede isteksizlik, çabuk yorulma, yokuş yukarı yürürken nefes darlığı | Gerdan, Çene Altı ve Göğüs Ödemi: Gerdan ve göğüs önünde geniş alana yayılmış soğuk, hamur kıvamında ödem | Vena Jugularis Muayenesi: Çene açısına kadar V. jugularis dolgun, pulsasyon yok | Dışkı ve İdrar Muayenesi: Dışkı ve idrar miktar ve kıvamı tamamen normal | Retikulum Ağrı Testleri: Sopa testi Negatif (-), Kama testi Negatif (-)."
            },
            "VITAL_ATEŞ": { "name": "Vücut Sıcaklığı (Ateş)", "keywords": ["ateş", "sıcaklık", "derece"], "content": "Vücut Sıcaklığı: 38.6 °C" },
            "VITAL_NABIZ": { "name": "Kalp Frekansı (Nabız)", "keywords": ["nabız", "kalp frekansı", "hr"], "content": "Kalp Frekansı: 96 atım/dakika" },
            "VITAL_SOLUNUM": { "name": "Solunum Frekansı", "keywords": ["solunum", "solunum frekansı", "rr", "nefes"], "content": "Solunum Frekansı: 46 nefes/dakika" },
            "VITAL_DEHIDRASYON": { "name": "Dehidrasyon Derecesi & Deri Turgoru", "keywords": ["dehidrasyon", "deri", "göz küresi", "turgor", "elastikiyet"], "content": "Dehidrasyon Derecesi: %0 (Deri kıvrım kalıcılık süresi: 1 saniye, Göz küresi çöküklüğü yok)" },
            "VITAL_MUKOZA": { "name": "Mukoza Rengi ve Nemliliği", "keywords": ["mukoza", "ağız mukozası", "göz mukozası"], "content": "Mukoza Rengi ve Nemliliği: Pembe, nemli" },
            "VITAL_CRT": { "name": "Kılcal Damar Dolum Süresi (CRT)", "keywords": ["crt", "kılcal damar", "dolum süresi"], "content": "Kılcal Damar Dolum Süresi (CRT): 1.8 saniye" },
            "VITAL_LENF": { "name": "Yüzeysel Lenf Yumruları", "keywords": ["lenf", "lenf nodu", "lenf yumrusu", "lnn"], "content": "Yüzeysel Lenf Yumruları: Tüm yüzeysel lenf yumruları normal büyüklükte ve yapıda" },
            "VITAL_RUMEN": { "name": "Rumen Hareketleri ve Tonusu", "keywords": ["rumen", "rumen hareketi", "tonus"], "content": "Rumen Hareketleri ve Tonusu: 5 dakikada 3 kez, normal tonusta" },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Hiperdinamik güçlü kalp sesleri. Üfürüm veya su çalkantı sesi yok. Akciğer Oskültasyonu: Hafifleşmiş veziküler sesler."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Sopa testi Negatif (-), Kama testi Negatif (-)."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma", "pıhtı"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 12 dakikadan uzun (Negatif / Pıhtılaşma yok)"
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayımı", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "cbc", "polisitemi"],
                "content": "Eritrosit (RBC): 10.8 x10⁶/µL | Hemoglobin (Hb): 17.2 g/dL | Hematokrit (PCV): %54 | Lökosit (WBC): 7.2 x10³/µL | Band Nötrofil: %1 | Segmenter Nötrofil: %35 | Lenfosit: %58 | Monosit: %2 | Eozinofil: %4 | Plazma Fibrinojeni: 320 mg/dL | Total Protein: 7.3 g/dL | PP/F Oranı: 22.8."
            },
            "BIO_ALT": { "name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 18 U/L" },
            "BIO_AST": { "name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 68 U/L" },
            "BIO_GGT": { "name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 18 U/L" },
            "BIO_ALP": { "name": "ALP (Alkalen Fosfataz)", "keywords": ["alp"], "content": "ALP: 62 U/L" },
            "BIO_CK":  { "name": "CK (Kreatin Kinaz)", "keywords": ["ck"], "content": "CK: 110 U/L" },
            "BIO_LDH": { "name": "LDH (Laktat Dehidrogenaz)", "keywords": ["ldh"], "content": "LDH: 280 U/L" },
            "BIO_BUN": { "name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre"], "content": "BUN: 18 mg/dL" },
            "BIO_KREATININ": { "name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 0.9 mg/dL" },
            "BIO_TROPONIN": { "name": "Kardiyak Troponin I", "keywords": ["troponin"], "content": "Kardiyak Troponin I (cTnI): 0.12 ng/mL" },
            "BIO_ALBUMIN": { "name": "Albümin", "keywords": ["albümin", "albumin"], "content": "Albümin: 3.2 g/dL" },
            "BIO_GLOBULIN": { "name": "Globülin", "keywords": ["globülin", "globulin"], "content": "Globülin: 4.1 g/dL" },
            "BIO_BILIRUBIN": { "name": "Bilirubin", "keywords": ["bilirubin"], "content": "Total Bilirubin: 0.3 mg/dL | İndirekt Bilirubin: 0.2 mg/dL" },
            "BIO_GLIKOZ": { "name": "Glikoz", "keywords": ["glikoz", "seker"], "content": "Glikoz: 74 mg/dL" },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "laktat"],
                "content": "Kan pH: 7.36 | pO₂: 48 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 23.5 mmol/L | Baz Açığı: -0.8 mmol/L | Laktat: 1.5 mmol/L."
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG) Bulgusu",
                "keywords": ["ultrason", "usg"],
                "content": "Thorakal Ultrasonografi: Pulmoner arter çapında genişleme."
            },
            "EKOKARDIYOGRAFI": {
                "name": "Ekokardiyografi Bulgusu",
                "keywords": ["eko", "ekokardiyografi"],
                "content": "Ekokardiyografi: Sağ ventrikül serbest duvar kalınlığında artış (Sağ Ventrikül Hipertrofisi), pulmoner arter genişlemesi."
            },
            "PERIKARDIYOSENTEZ": {
                "name": "Perikardiyosentez Bulgusu",
                "keywords": ["perikardiyosentez", "ponksiyon", "delme"],
                "content": "Perikardiyosentez: Sıvı alınamadı (Efüzyon yok)."
            },
            "KULTUR": {
                "name": "Mikrobiyolojik Kültür",
                "keywords": ["kültür", "bakteri"],
                "content": "Kan ve perikard sıvısında bakteri üremesi yoktur (Steril)."
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
                "content": "Günlük rasyonda: 10 kg mısır kırması, 10 kg arpa kırması, 5 kg yonca kuru otu ve 2 kg saman verilmektedir. Yoğun yem oranı %80 seviyesindedir."
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
            "FIZIKSEL_MUAYENE_TAM": {
                "name": "Eksiksiz Tam Fiziksel Muayene Bulguları",
                "keywords": ["fiziksel muayene", "genel muayene", "tam muayene", "muayene bulguları", "fiziksel"],
                "content": "Vücut Sıcaklığı: 39.2 °C | Kalp Frekansı: 118 atım/dk | Solunum Frekansı: 52 nefes/dk | Mukoza Rengi ve Nemliliği: Bembeyaz, kuru | CRT: 4.0 saniye | Dehidrasyon Derecesi: %7 (Deri kıvrım kalıcılık süresi: 8 saniye, Göz küresi çökmüşlük: 4 mm) | Yüzeysel Lenf Yumruları: Lnn. prescapularis ve Lnn. prefemoralis boyutları ve yapısı normal | Rumen Hareketleri ve Tonusu: 5 dakikada 1 kez (atoniye yakın) | İştah ve Ruminasyon: İştah tamamen durmuş, geviş getirme yok | Burun ve Ağız Muayenesi: Ağız ve burun deliklerinden köpüklü, taze, parlak kırmızı kan fışkırması (hemoptizi) | Postür ve Genel Durum: Aşırı halsiz, yatma eğiliminde, sık ve yüzeysel solunum | Dışkı ve İdrar Muayenesi: Dışkı katran gibi simsiyah, yapışkan ve kötü kokulu (melena). İdrar miktarı azalmış | Vena Jugularis Muayenesi: Jugular ven hafif dolgun | Retikulum Ağrı Testleri: Sopa testi Negatif (-), Kama testi Negatif (-)."
            },
            "VITAL_ATEŞ": { "name": "Vücut Sıcaklığı (Ateş)", "keywords": ["ateş", "sıcaklık", "derece"], "content": "Vücut Sıcaklığı: 39.2 °C" },
            "VITAL_NABIZ": { "name": "Kalp Frekansı (Nabız)", "keywords": ["nabız", "kalp frekansı", "hr"], "content": "Kalp Frekansı: 118 atım/dakika" },
            "VITAL_SOLUNUM": { "name": "Solunum Frekansı", "keywords": ["solunum", "solunum frekansı", "rr", "nefes"], "content": "Solunum Frekansı: 52 nefes/dakika" },
            "VITAL_DEHIDRASYON": { "name": "Dehidrasyon Derecesi & Deri Turgoru", "keywords": ["dehidrasyon", "deri", "göz küresi", "turgor", "elastikiyet"], "content": "Dehidrasyon Derecesi: %7 (Deri kıvrım kalıcılık süresi: 8 saniye, Göz küresi çökmüşlük: 4 mm)" },
            "VITAL_MUKOZA": { "name": "Mukoza Rengi ve Nemliliği", "keywords": ["mukoza", "ağız mukozası", "göz mukozası"], "content": "Mukoza Rengi ve Nemliliği: Bembeyaz, kuru" },
            "VITAL_CRT": { "name": "Kılcal Damar Dolum Süresi (CRT)", "keywords": ["crt", "kılcal damar", "dolum süresi"], "content": "Kılcal Damar Dolum Süresi (CRT): 4.0 saniye" },
            "VITAL_LENF": { "name": "Yüzeysel Lenf Yumruları", "keywords": ["lenf", "lenf nodu", "lenf yumrusu", "lnn"], "content": "Yüzeysel Lenf Yumruları: Lnn. prescapularis ve Lnn. prefemoralis boyutları ve yapısı normal" },
            "VITAL_RUMEN": { "name": "Rumen Hareketleri ve Tonusu", "keywords": ["rumen", "rumen hareketi", "tonus"], "content": "Rumen Hareketleri ve Tonusu: 5 dakikada 1 kez (atoniye yakın)" },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Taşikardik, zayıf düştü sesleri. Akciğer Oskültasyonu: Bilateral yaygın kaba raller ve hışırtı sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Sopa testi Negatif (-), Kama testi Negatif (-)."
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma", "pıhtı"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 3.5 dakikada pıhtılaşma"
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayımı", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "cbc", "anemi"],
                "content": "Eritrosit (RBC): 2.1 x10⁶/µL | Hemoglobin (Hb): 4.2 g/dL | Hematokrit (PCV): %12 | Lökosit (WBC): 21.5 x10³/µL | Band Nötrofil: %18 | Segmenter Nötrofil: %60 | Lenfosit: %18 | Monosit: %3 | Eozinofil: %1 | Plazma Fibrinojeni: 1050 mg/dL | Total Protein: 7.6 g/dL | PP/F Oranı: 7.23."
            },
            "BIO_ALT": { "name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 45 U/L" },
            "BIO_AST": { "name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 210 U/L" },
            "BIO_GGT": { "name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 68 U/L" },
            "BIO_ALP": { "name": "ALP (Alkalen Fosfataz)", "keywords": ["alp"], "content": "ALP: 110 U/L" },
            "BIO_CK":  { "name": "CK (Kreatin Kinaz)", "keywords": ["ck"], "content": "CK: 190 U/L" },
            "BIO_LDH": { "name": "LDH (Laktat Dehidrogenaz)", "keywords": ["ldh"], "content": "LDH: 410 U/L" },
            "BIO_BUN": { "name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre"], "content": "BUN: 42 mg/dL" },
            "BIO_KREATININ": { "name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 1.6 mg/dL" },
            "BIO_TROPONIN": { "name": "Kardiyak Troponin I", "keywords": ["troponin"], "content": "Kardiyak Troponin I (cTnI): 0.45 ng/mL" },
            "BIO_ALBUMIN": { "name": "Albümin", "keywords": ["albümin", "albumin"], "content": "Albümin: 2.6 g/dL" },
            "BIO_GLOBULIN": { "name": "Globülin", "keywords": ["globülin", "globulin"], "content": "Globülin: 5.0 g/dL" },
            "BIO_BILIRUBIN": { "name": "Bilirubin", "keywords": ["bilirubin"], "content": "Total Bilirubin: 1.2 mg/dL | İndirekt Bilirubin: 0.8 mg/dL" },
            "BIO_GLIKOZ": { "name": "Glikoz", "keywords": ["glikoz", "seker"], "content": "Glikoz: 88 mg/dL" },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "laktat"],
                "content": "Kan pH: 7.24 | pO₂: 52 mmHg | pCO₂: 50 mmHg | HCO₃⁻: 18.5 mmol/L | Baz Açığı: -6.2 mmol/L | Laktat: 4.2 mmol/L."
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG) Bulgusu",
                "keywords": ["ultrason", "usg"],
                "content": "Abdominal Ultrasonografi: Karaciğer parankiminde 6 cm çapında kılıflı apse odağı, Vena Cava Caudalis lümeninde tıkayıcı trombüs ekojenitesi. Torakal USG: Pulmoner arter çevresinde hematom ve anevrizma."
            },
            "EKOKARDIYOGRAFI": {
                "name": "Ekokardiyografi Bulgusu",
                "keywords": ["eko", "ekokardiyografi"],
                "content": "Ekokardiyografi: Kalp kapakları ve perikard normal."
            },
            "PERIKARDIYOSENTEZ": {
                "name": "Perikardiyosentez Bulgusu",
                "keywords": ["perikardiyosentez", "ponksiyon", "delme"],
                "content": "Perikardiyosentez: Sıvı alınamadı (Efüzyon yok)."
            },
            "KULTUR": {
                "name": "Mikrobiyolojik Kültür",
                "keywords": ["kültür", "bakteri"],
                "content": "Karaciğer Apse İspirasyonu Kültürü: Trueperella pyogenes ve Fusobacterium necrophorum üremesi."
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
def match_query(user_text, categories_dict):
    text_clean = user_text.lower().strip()
    text_clean = text_clean.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    
    matched_cats = []
    
    for cat_key, cat_info in categories_dict.items():
        for kw in cat_info["keywords"]:
            kw_clean = kw.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
            if re.search(r'\b' + re.escape(kw_clean) + r'\b', text_clean) or (len(kw_clean) >= 4 and kw_clean in text_clean):
                matched_cats.append(cat_key)
                break
                
    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız (Örn: Rasyon?, Ateş?, ALT?, AST?):",
        key="query_input",
        placeholder="Örn: Rasyon?, Ateş?, Dehidrasyon?, ALT?, AST?, Hemogram?..."
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
        st.warning("⚠️ Girdiğiniz soru veya kelimelerle eşleşen bir bilgi bulunamadı. Lütfen sorunuzu farklı anahtar kelimelerle yazınız (Örn: 'Rasyon', 'Ateş', 'Dehidrasyon', 'Hemogram', 'ALT', 'AST', 'Ultrason').")

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
