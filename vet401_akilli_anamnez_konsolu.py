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

# Granular Cases Knowledge Base
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
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik", "dağ", "ova", "kıyı", "şehir"],
                "content": "Ceyhan Ovası (~50 metre rakım) sabit süt tesisinde barındırılmaktadır. Herhangi bir yayla veya yüksek rakım nakli öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Anamnez",
                "keywords": ["geçmiş", "önceden", "öykü", "rahim", "metritis", "mastitis", "meme", "doğum", "geçirdi"],
                "content": "Geçmişinde kaydedilmiş kronik mastitis, metritis veya metabolik hastalık öyküsü yoktur. 2 ay önce sorunsuz doğum yapmıştır."
            },
            "VITAL_ATES": {
                "name": "Vücut Sıcaklığı (Ateş)",
                "keywords": ["ateş", "sıcaklık", "derece"],
                "content": "Vücut Sıcaklığı: 39.8 °C"
            },
            "VITAL_NABIZ": {
                "name": "Kalp Frekansı (Nabız)",
                "keywords": ["nabız", "kalp frekans", "nabız sayısı"],
                "content": "Kalp Frekansı: 102 atım/dakika"
            },
            "VITAL_SOLUNUM": {
                "name": "Solunum Frekansı",
                "keywords": ["solunum", "nefes", "solunum sayısı"],
                "content": "Solunum Frekansı: 42 nefes/dakika"
            },
            "VITAL_MUKOZA": {
                "name": "Mukoza & CRT & Dehidrasyon",
                "keywords": ["mukoza", "crt", "kılcal damar", "dolum", "dehidrasyon", "deri"],
                "content": "Mukoza Rengi: Soluk pembe | CRT: 2.5 saniye | Dehidrasyon: %6"
            },
            "VITAL_ODEM": {
                "name": "Ödem & Vena Jugularis Durumu",
                "keywords": ["ödem", "gerdan", "şişlik", "jugularis", "staz", "damar"],
                "content": "Gerdan ve submandibuler bölgede soğuk hamur kıvamında ödem | Vena jugularis stazı +, yalancı jugular nabız +"
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "boğuk", "rall"],
                "content": "Kalp Oskültasyonu: Çamaşır makinesi / su şılpırtısı (splashing) sesi ve boğuk kalp sesleri. Akciğer Oskültasyonu: Ventro-lateral alanlarda solunum sesleri azalmış."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı test", "pinch", "cidago"],
                "content": "Sopa testi: Pozitif (+) | Kama testi: Pozitif (+) | Withers pinch (cidago sıkma) testi: Pozitif (+)"
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "glutaraldehid", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 2.5 dakikada pıhtılaşma (Pozitif)"
            },
            "HEMOGRAM_GENEL": {
                "name": "Tam Hemogram (CBC) Paneli",
                "keywords": ["hemogram", "cbc", "kan sayım"],
                "content": "Lökosit (WBC): 22.4 x10³/µL | Eritrosit (RBC): 5.4 x10⁶/µL | Hematokrit (PCV): %28 | Plazma Fibrinojeni: 1250 mg/dL | Total Protein: 7.9 g/dL | PP/F Oranı: 6.3"
            },
            "WBC": {
                "name": "Lökosit (WBC) Sayımı",
                "keywords": ["wbc", "lökosit", "nötrofil", "lenfosit"],
                "content": "Lökosit (WBC): 22.4 x10³/µL (Segmenter Nötrofil: %62, Band Nötrofil: %12, Lenfosit: %20, Monosit: %4, Eozinofil: %2)"
            },
            "RBC": {
                "name": "Eritrosit (RBC) Sayımı",
                "keywords": ["rbc", "eritrosit", "alyuvar"],
                "content": "Eritrosit (RBC): 5.4 x10⁶/µL"
            },
            "PCV": {
                "name": "Hematokrit (PCV) & Hemoglobin",
                "keywords": ["pcv", "hematokrit", "hemoglobin", "hb"],
                "content": "Hematokrit (PCV): %28 | Hemoglobin (Hb): 9.2 g/dL"
            },
            "FIBRINOJEN": {
                "name": "Plazma Fibrinojeni & PP/F Oranı",
                "keywords": ["fibrinojen", "pp/f"],
                "content": "Plazma Fibrinojeni: 1250 mg/dL | PP/F Oranı: 6.3"
            },
            "BIYOKIMYA_GENEL": {
                "name": "Serum Biyokimyası Paneli",
                "keywords": ["biyokimya", "biyokimya paneli"],
                "content": "ALT: 22 U/L | AST: 118 U/L | GGT: 24 U/L | ALP: 75 U/L | CK: 180 U/L | LDH: 360 U/L | BUN: 28 mg/dL | Kreatinin: 1.2 mg/dL | Albümin: 2.8 g/dL | Globülin: 5.1 g/dL | Bilirubin: 0.4 mg/dL | Glikoz: 68 mg/dL | cTnI: 0.85 ng/mL"
            },
            "ALT": {
                "name": "ALT (Alanin Aminotransferaz)",
                "keywords": ["alt", "alanin aminotransferaz"],
                "content": "ALT (Alanin Aminotransferaz): 22 U/L"
            },
            "AST": {
                "name": "AST (Aspartat Aminotransferaz)",
                "keywords": ["ast", "aspartat aminotransferaz"],
                "content": "AST (Aspartat Aminotransferaz): 118 U/L"
            },
            "GGT": {
                "name": "GGT (Gama Glutamil Transferaz)",
                "keywords": ["ggt", "gama glutamil"],
                "content": "GGT (Gama Glutamil Transferaz): 24 U/L"
            },
            "ALP": {
                "name": "ALP (Alkalen Fosfataz)",
                "keywords": ["alp", "alkalen fosfataz"],
                "content": "ALP (Alkalen Fosfataz): 75 U/L"
            },
            "CK": {
                "name": "CK (Kreatin Kinaz)",
                "keywords": ["ck", "kreatin kinaz"],
                "content": "CK (Kreatin Kinaz): 180 U/L"
            },
            "LDH": {
                "name": "LDH (Laktat Dehidrogenaz)",
                "keywords": ["ldh", "laktat dehidrogenaz"],
                "content": "LDH (Laktat Dehidrogenaz): 360 U/L"
            },
            "BUN_URE": {
                "name": "BUN / Kan Üre Azotu",
                "keywords": ["bun", "üre", "kan üre"],
                "content": "BUN (Kan Üre Azotu): 28 mg/dL"
            },
            "KREATININ": {
                "name": "Kreatinin",
                "keywords": ["kreatinin"],
                "content": "Kreatinin: 1.2 mg/dL"
            },
            "ALBUMIN": {
                "name": "Albümin",
                "keywords": ["albümin", "albumin"],
                "content": "Albümin: 2.8 g/dL"
            },
            "GLOBULIN": {
                "name": "Globülin",
                "keywords": ["globülin", "globulin"],
                "content": "Globülin: 5.1 g/dL"
            },
            "BILIRUBIN": {
                "name": "Bilirubin (Total & İndirekt)",
                "keywords": ["bilirubin"],
                "content": "Total Bilirubin: 0.4 mg/dL | İndirekt Bilirubin: 0.2 mg/dL"
            },
            "GLIKOZ": {
                "name": "Glikoz (Kan Şekeri)",
                "keywords": ["glikoz", "glukoz", "şeker"],
                "content": "Glikoz: 68 mg/dL"
            },
            "TROPONIN": {
                "name": "Kardiyak Troponin I (cTnI)",
                "keywords": ["troponin", "ctni"],
                "content": "Kardiyak Troponin I (cTnI): 0.85 ng/mL"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.32 | pO₂: 72 mmHg | pCO₂: 48 mmHg | HCO₃⁻: 20.2 mmol/L | Baz Açığı (BE): -4.1 mmol/L | Laktat: 2.8 mmol/L"
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG) Bulguları",
                "keywords": ["ultrason", "usg", "ultrasonografi"],
                "content": "Ultrasonografi (USG): Perikardiyal boşlukta fibrin bantları, gaz ekojeniteleri ve 4 cm kalınlığında sıvı birikimi. Retikulum duvarında kalınlaşma ve periretiküler yapışıklıklar."
            },
            "EKOKARDIYOGRAFI": {
                "name": "Ekokardiyografi Bulguları",
                "keywords": ["ekokardiyografi", "echo", "eko"],
                "content": "Ekokardiyografi: Perikardiyal efüzyon ve perikard yapraklarında kalınlaşma tespit edildi. Kapaklarda vejetasyon görünümü yok."
            },
            "PERIKARDIYOSENTEZ": {
                "name": "Perikardiyosentez Sıvı Analizi",
                "keywords": ["perikardiyosentez", "ponksiyon", "sıvı delme", "perikard sıvı"],
                "content": "Perikardiyosentez Sıvısı: Kirli sarı-yeşil renkli, bulanık pürülan eksuda. Sıvı Total Protein Miktarı: 4.8 g/dL."
            },
            "KULTUR_MIKROBIYOLOJI": {
                "name": "Kültür & Mikrobiyoloji Sonucu",
                "keywords": ["kültür", "bakteri", "mikrobiyoloji"],
                "content": "Perikard Sıvısı Kültürü: Trueperella pyogenes üremesi saptandı."
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
                "name": "Geçmiş Hastalık & Anamnez",
                "keywords": ["geçmiş", "önceden", "öykü", "rahim", "metritis", "mastitis", "meme", "doğum", "geçirdi"],
                "content": "Yaklaşık 3 hafta önce doğum sonrası ağır pürülan metritis (rahim iltihabı) ve klinik mastitis tedavisi görmüştür."
            },
            "VITAL_ATES": {
                "name": "Vücut Sıcaklığı (Ateş)",
                "keywords": ["ateş", "sıcaklık", "derece"],
                "content": "Vücut Sıcaklığı: 40.2 °C (Dalgalı febril ateş)"
            },
            "VITAL_NABIZ": {
                "name": "Kalp Frekansı (Nabız)",
                "keywords": ["nabız", "kalp frekans", "nabız sayısı"],
                "content": "Kalp Frekansı: 110 atım/dakika"
            },
            "VITAL_SOLUNUM": {
                "name": "Solunum Frekansı",
                "keywords": ["solunum", "nefes", "solunum sayısı"],
                "content": "Solunum Frekansı: 38 nefes/dakika"
            },
            "VITAL_MUKOZA": {
                "name": "Mukoza & CRT",
                "keywords": ["mukoza", "crt", "kılcal damar", "dolum"],
                "content": "Mukoza Rengi: Soluk | CRT: 3.0 saniye"
            },
            "VITAL_ODEM": {
                "name": "Ödem & Eklem Muayenesi",
                "keywords": ["ödem", "gerdan", "şişlik", "jugularis", "eklem", "topallık", "bacak"],
                "content": "Gerdan bölgesi ödemli | Vena jugularis dolgun (pulsasyon yok) | Sol carpus ve tarsus eklemlerinde şişlik, sıcaklık ve ağrı"
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "boğuk", "rall"],
                "content": "Kalp Oskültasyonu: Triküspid kapak odak sahası üzerinde Grade IV/VI holosistolik üfürüm. Su çalkantısı (splashing) sesi yoktur."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı test", "pinch", "cidago"],
                "content": "Sopa testi: Negatif (-) | Kama testi: Negatif (-)"
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "glutaraldehid", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 4.0 dakikada pıhtılaşma (Pozitif)"
            },
            "HEMOGRAM_GENEL": {
                "name": "Tam Hemogram (CBC) Paneli",
                "keywords": ["hemogram", "cbc", "kan sayım"],
                "content": "Lökosit (WBC): 26.8 x10³/µL | Eritrosit (RBC): 4.2 x10⁶/µL | Hematokrit (PCV): %22 | Plazma Fibrinojeni: 980 mg/dL | Total Protein: 8.8 g/dL | Globülin: 6.5 g/dL | PP/F: 8.98"
            },
            "WBC": {
                "name": "Lökosit (WBC) Sayımı",
                "keywords": ["wbc", "lökosit", "nötrofil", "lenfosit"],
                "content": "Lökosit (WBC): 26.8 x10³/µL (Segmenter Nötrofil: %65, Band Nötrofil: %15, Lenfosit: %15, Monosit: %4, Eozinofil: %1)"
            },
            "RBC": {
                "name": "Eritrosit (RBC) Sayımı",
                "keywords": ["rbc", "eritrosit", "alyuvar"],
                "content": "Eritrosit (RBC): 4.2 x10⁶/µL"
            },
            "PCV": {
                "name": "Hematokrit (PCV) & Hemoglobin",
                "keywords": ["pcv", "hematokrit", "hemoglobin", "hb"],
                "content": "Hematokrit (PCV): %22 | Hemoglobin (Hb): 7.2 g/dL"
            },
            "FIBRINOJEN": {
                "name": "Plazma Fibrinojeni & PP/F Oranı",
                "keywords": ["fibrinojen", "pp/f"],
                "content": "Plazma Fibrinojeni: 980 mg/dL | PP/F Oranı: 8.98"
            },
            "BIYOKIMYA_GENEL": {
                "name": "Serum Biyokimyası Paneli",
                "keywords": ["biyokimya", "biyokimya paneli"],
                "content": "ALT: 25 U/L | AST: 145 U/L | GGT: 28 U/L | ALP: 82 U/L | CK: 210 U/L | LDH: 390 U/L | BUN: 34 mg/dL | Kreatinin: 1.5 mg/dL | Albümin: 2.3 g/dL | Globülin: 6.5 g/dL | Bilirubin: 0.5 mg/dL | Glikoz: 62 mg/dL | cTnI: 1.20 ng/mL"
            },
            "ALT": {
                "name": "ALT (Alanin Aminotransferaz)",
                "keywords": ["alt", "alanin aminotransferaz"],
                "content": "ALT (Alanin Aminotransferaz): 25 U/L"
            },
            "AST": {
                "name": "AST (Aspartat Aminotransferaz)",
                "keywords": ["ast", "aspartat aminotransferaz"],
                "content": "AST (Aspartat Aminotransferaz): 145 U/L"
            },
            "GGT": {
                "name": "GGT (Gama Glutamil Transferaz)",
                "keywords": ["ggt", "gama glutamil"],
                "content": "GGT (Gama Glutamil Transferaz): 28 U/L"
            },
            "ALP": {
                "name": "ALP (Alkalen Fosfataz)",
                "keywords": ["alp", "alkalen fosfataz"],
                "content": "ALP (Alkalen Fosfataz): 82 U/L"
            },
            "CK": {
                "name": "CK (Kreatin Kinaz)",
                "keywords": ["ck", "kreatin kinaz"],
                "content": "CK (Kreatin Kinaz): 210 U/L"
            },
            "LDH": {
                "name": "LDH (Laktat Dehidrogenaz)",
                "keywords": ["ldh", "laktat dehidrogenaz"],
                "content": "LDH (Laktat Dehidrogenaz): 390 U/L"
            },
            "BUN_URE": {
                "name": "BUN / Kan Üre Azotu",
                "keywords": ["bun", "üre", "kan üre"],
                "content": "BUN (Kan Üre Azotu): 34 mg/dL"
            },
            "KREATININ": {
                "name": "Kreatinin",
                "keywords": ["kreatinin"],
                "content": "Kreatinin: 1.5 mg/dL"
            },
            "ALBUMIN": {
                "name": "Albümin",
                "keywords": ["albümin", "albumin"],
                "content": "Albümin: 2.3 g/dL"
            },
            "GLOBULIN": {
                "name": "Globülin",
                "keywords": ["globülin", "globulin"],
                "content": "Globülin: 6.5 g/dL"
            },
            "BILIRUBIN": {
                "name": "Bilirubin (Total & İndirekt)",
                "keywords": ["bilirubin"],
                "content": "Total Bilirubin: 0.5 mg/dL | İndirekt Bilirubin: 0.3 mg/dL"
            },
            "GLIKOZ": {
                "name": "Glikoz (Kan Şekeri)",
                "keywords": ["glikoz", "glukoz", "şeker"],
                "content": "Glikoz: 62 mg/dL"
            },
            "TROPONIN": {
                "name": "Kardiyak Troponin I (cTnI)",
                "keywords": ["troponin", "ctni"],
                "content": "Kardiyak Troponin I (cTnI): 1.20 ng/mL"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.30 | pO₂: 68 mmHg | pCO₂: 52 mmHg | HCO₃⁻: 18.8 mmol/L | Baz Açığı (BE): -5.2 mmol/L | Laktat: 3.1 mmol/L"
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG) Bulguları",
                "keywords": ["ultrason", "usg", "ultrasonografi"],
                "content": "Abdominal USG: Karaciğer ve böbreklerde septik embolik odaklar izlendi. Perikardiyal efüzyon yok."
            },
            "EKOKARDIYOGRAFI": {
                "name": "Ekokardiyografi Bulguları",
                "keywords": ["ekokardiyografi", "echo", "eko"],
                "content": "Ekokardiyografi: Triküspid kapak üzerinde 3.5 cm çapında pürüzlü hiperekojen kitle (vejetasyon) tespit edildi."
            },
            "PERIKARDIYOSENTEZ": {
                "name": "Perikardiyosentez Sıvı Analizi",
                "keywords": ["perikardiyosentez", "ponksiyon", "sıvı delme", "perikard sıvı"],
                "content": "Perikardiyosentez: Perikardiyal efüzyon bulunmadığı için sıvı alınamadı."
            },
            "KULTUR_MIKROBIYOLOJI": {
                "name": "Kültür & Mikrobiyoloji Sonucu",
                "keywords": ["kültür", "bakteri", "mikrobiyoloji"],
                "content": "Kan Kültürü: Trueperella pyogenes üremesi saptandı | Eklem Sıvısı Kültürü: Trueperella pyogenes üremesi saptandı."
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
                "name": "Geçmiş Hastalık & Anamnez",
                "keywords": ["geçmiş", "önceden", "öykü", "rahim", "metritis", "mastitis", "meme", "doğum", "geçirdi"],
                "content": "Geçmişinde kaydedilmiş hiçbir sistemik, metabolik veya enfeksiyöz hastalık öyküsü yoktur."
            },
            "VITAL_ATES": {
                "name": "Vücut Sıcaklığı (Ateş)",
                "keywords": ["ateş", "sıcaklık", "derece"],
                "content": "Vücut Sıcaklığı: 38.6 °C"
            },
            "VITAL_NABIZ": {
                "name": "Kalp Frekansı (Nabız)",
                "keywords": ["nabız", "kalp frekans", "nabız sayısı"],
                "content": "Kalp Frekansı: 96 atım/dakika"
            },
            "VITAL_SOLUNUM": {
                "name": "Solunum Frekansı",
                "keywords": ["solunum", "nefes", "solunum sayısı"],
                "content": "Solunum Frekansı: 46 nefes/dakika"
            },
            "VITAL_MUKOZA": {
                "name": "Mukoza & CRT & Dehidrasyon",
                "keywords": ["mukoza", "crt", "kılcal damar", "dolum", "dehidrasyon"],
                "content": "Mukoza Rengi: Pembe | CRT: 1.8 saniye | Dehidrasyon: %0"
            },
            "VITAL_ODEM": {
                "name": "Ödem & Vena Jugularis Durumu",
                "keywords": ["ödem", "gerdan", "şişlik", "jugularis", "staz", "damar"],
                "content": "Gerdanda geniş alana yayılmış soğuk hamur kıvamında ödem | Vena jugularis dolgun"
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "boğuk", "rall"],
                "content": "Kalp Oskültasyonu: Hiperdinamik güçlü kalp sesleri. Üfürüm veya su çalkantı sesi yoktur. Akciğer Oskültasyonu: Hafif veziküler solunum sesi."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı test", "pinch", "cidago"],
                "content": "Sopa testi: Negatif (-) | Kama testi: Negatif (-)"
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "glutaraldehid", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 12 dakikadan uzun (Negatif / Pıhtılaşma yok)"
            },
            "HEMOGRAM_GENEL": {
                "name": "Tam Hemogram (CBC) Paneli",
                "keywords": ["hemogram", "cbc", "kan sayım"],
                "content": "Eritrosit (RBC): 10.8 x10⁶/µL | Hemoglobin (Hb): 17.2 g/dL | Hematokrit (PCV): %54 | Lökosit (WBC): 7.2 x10³/µL | Plazma Fibrinojeni: 320 mg/dL | Total Protein: 7.3 g/dL | PP/F: 22.8"
            },
            "WBC": {
                "name": "Lökosit (WBC) Sayımı",
                "keywords": ["wbc", "lökosit", "nötrofil", "lenfosit"],
                "content": "Lökosit (WBC): 7.2 x10³/µL (Segmenter Nötrofil: %35, Band Nötrofil: %1, Lenfosit: %58, Monosit: %2, Eozinofil: %4)"
            },
            "RBC": {
                "name": "Eritrosit (RBC) Sayımı",
                "keywords": ["rbc", "eritrosit", "alyuvar"],
                "content": "Eritrosit (RBC): 10.8 x10⁶/µL"
            },
            "PCV": {
                "name": "Hematokrit (PCV) & Hemoglobin",
                "keywords": ["pcv", "hematokrit", "hemoglobin", "hb"],
                "content": "Hematokrit (PCV): %54 | Hemoglobin (Hb): 17.2 g/dL"
            },
            "FIBRINOJEN": {
                "name": "Plazma Fibrinojeni & PP/F Oranı",
                "keywords": ["fibrinojen", "pp/f"],
                "content": "Plazma Fibrinojeni: 320 mg/dL | PP/F Oranı: 22.8"
            },
            "BIYOKIMYA_GENEL": {
                "name": "Serum Biyokimyası Paneli",
                "keywords": ["biyokimya", "biyokimya paneli"],
                "content": "ALT: 18 U/L | AST: 68 U/L | GGT: 18 U/L | ALP: 62 U/L | CK: 110 U/L | LDH: 280 U/L | BUN: 18 mg/dL | Kreatinin: 0.9 mg/dL | Albümin: 3.2 g/dL | Globülin: 4.1 g/dL | Bilirubin: 0.3 mg/dL | Glikoz: 74 mg/dL | cTnI: 0.12 ng/mL"
            },
            "ALT": {
                "name": "ALT (Alanin Aminotransferaz)",
                "keywords": ["alt", "alanin aminotransferaz"],
                "content": "ALT (Alanin Aminotransferaz): 18 U/L"
            },
            "AST": {
                "name": "AST (Aspartat Aminotransferaz)",
                "keywords": ["ast", "aspartat aminotransferaz"],
                "content": "AST (Aspartat Aminotransferaz): 68 U/L"
            },
            "GGT": {
                "name": "GGT (Gama Glutamil Transferaz)",
                "keywords": ["ggt", "gama glutamil"],
                "content": "GGT (Gama Glutamil Transferaz): 18 U/L"
            },
            "ALP": {
                "name": "ALP (Alkalen Fosfataz)",
                "keywords": ["alp", "alkalen fosfataz"],
                "content": "ALP (Alkalen Fosfataz): 62 U/L"
            },
            "CK": {
                "name": "CK (Kreatin Kinaz)",
                "keywords": ["ck", "kreatin kinaz"],
                "content": "CK (Kreatin Kinaz): 110 U/L"
            },
            "LDH": {
                "name": "LDH (Laktat Dehidrogenaz)",
                "keywords": ["ldh", "laktat dehidrogenaz"],
                "content": "LDH (Laktat Dehidrogenaz): 280 U/L"
            },
            "BUN_URE": {
                "name": "BUN / Kan Üre Azotu",
                "keywords": ["bun", "üre", "kan üre"],
                "content": "BUN (Kan Üre Azotu): 18 mg/dL"
            },
            "KREATININ": {
                "name": "Kreatinin",
                "keywords": ["kreatinin"],
                "content": "Kreatinin: 0.9 mg/dL"
            },
            "ALBUMIN": {
                "name": "Albümin",
                "keywords": ["albümin", "albumin"],
                "content": "Albümin: 3.2 g/dL"
            },
            "GLOBULIN": {
                "name": "Globülin",
                "keywords": ["globülin", "globulin"],
                "content": "Globülin: 4.1 g/dL"
            },
            "BILIRUBIN": {
                "name": "Bilirubin (Total & İndirekt)",
                "keywords": ["bilirubin"],
                "content": "Total Bilirubin: 0.3 mg/dL | İndirekt Bilirubin: 0.2 mg/dL"
            },
            "GLIKOZ": {
                "name": "Glikoz (Kan Şekeri)",
                "keywords": ["glikoz", "glukoz", "şeker"],
                "content": "Glikoz: 74 mg/dL"
            },
            "TROPONIN": {
                "name": "Kardiyak Troponin I (cTnI)",
                "keywords": ["troponin", "ctni"],
                "content": "Kardiyak Troponin I (cTnI): 0.12 ng/mL"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "hipoksi"],
                "content": "Kan pH: 7.36 | pO₂: 48 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 23.5 mmol/L | Baz Açığı (BE): -0.8 mmol/L | Laktat: 1.5 mmol/L"
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG) Bulguları",
                "keywords": ["ultrason", "usg", "ultrasonografi"],
                "content": "Torakal USG: Pulmoner arter çapında genişleme, plevral ve perikardiyal alanda sıvı artışı saptanmadı."
            },
            "EKOKARDIYOGRAFI": {
                "name": "Ekokardiyografi Bulguları",
                "keywords": ["ekokardiyografi", "echo", "eko"],
                "content": "Ekokardiyografi: Sağ ventrikül serbest duvar kalınlığında artış (Sağ Ventrikül Hipertrofisi) ve pulmoner arter çapında genişleme izlendi."
            },
            "PERIKARDIYOSENTEZ": {
                "name": "Perikardiyosentez Sıvı Analizi",
                "keywords": ["perikardiyosentez", "ponksiyon", "sıvı delme", "perikard sıvı"],
                "content": "Perikardiyosentez: Perikardiyal efüzyon bulunmadığı için sıvı toplanamadı."
            },
            "KULTUR_MIKROBIYOLOJI": {
                "name": "Kültür & Mikrobiyoloji Sonucu",
                "keywords": ["kültür", "bakteri", "mikrobiyoloji"],
                "content": "Kan Kültürü: Bakteri üremesi saptanmadı (Steril)."
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
                "content": "Besi padoğunda barındırılmaktadır. Rakım değişikliği veya nakil yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Anamnez",
                "keywords": ["geçmiş", "önceden", "öykü", "rahim", "metritis", "mastitis", "meme", "doğum", "geçirdi", "asidoz", "şişkinlik", "timpani", "rumenitis"],
                "content": "Geçmişinde tekrarlayan akut/subakut rumen asidozu (yem çarpması) ve kronik hafif rumen timpani (şişkinlik) öyküsü vardır."
            },
            "VITAL_ATES": {
                "name": "Vücut Sıcaklığı (Ateş)",
                "keywords": ["ateş", "sıcaklık", "derece"],
                "content": "Vücut Sıcaklığı: 39.2 °C"
            },
            "VITAL_NABIZ": {
                "name": "Kalp Frekansı (Nabız)",
                "keywords": ["nabız", "kalp frekans", "nabız sayısı"],
                "content": "Kalp Frekansı: 118 atım/dakika"
            },
            "VITAL_SOLUNUM": {
                "name": "Solunum Frekansı",
                "keywords": ["solunum", "nefes", "solunum sayısı"],
                "content": "Solunum Frekansı: 52 nefes/dakika"
            },
            "VITAL_MUKOZA": {
                "name": "Mukoza & CRT & Dışkı Muayenesi",
                "keywords": ["mukoza", "crt", "kılcal damar", "dolum", "hemoptizi", "melena", "dışkı", "kanama"],
                "content": "Ağız ve burun deliklerinden köpüklü taze parlak kırmızı kan fışkırması (Hemoptizi) | Mukoza Rengi: Bembeyaz | CRT: 4.0 saniye | Dışkı: Siyah katran kıvamında (Melena)"
            },
            "VITAL_ODEM": {
                "name": "Ödem & Vena Jugularis Durumu",
                "keywords": ["ödem", "gerdan", "şişlik", "jugularis", "staz", "damar"],
                "content": "Vena jugularis hafif dolgun."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "boğuk", "rall"],
                "content": "Kalp Oskültasyonu: Taşikardik, zayıf düştü sesleri. Akciğer Oskültasyonu: Bilateral yaygın kaba raller ve hışırtı sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı test", "pinch", "cidago"],
                "content": "Sopa testi: Negatif (-) | Kama testi: Negatif (-)"
            },
            "GLUTARALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "glutaraldehid", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 3.5 dakikada pıhtılaşma (Pozitif)"
            },
            "HEMOGRAM_GENEL": {
                "name": "Tam Hemogram (CBC) Paneli",
                "keywords": ["hemogram", "cbc", "kan sayım"],
                "content": "Eritrosit (RBC): 2.1 x10⁶/µL | Hemoglobin (Hb): 4.2 g/dL | Hematokrit (PCV): %12 | Lökosit (WBC): 21.5 x10³/µL | Plazma Fibrinojeni: 1050 mg/dL | PP/F: 7.23"
            },
            "WBC": {
                "name": "Lökosit (WBC) Sayımı",
                "keywords": ["wbc", "lökosit", "nötrofil", "lenfosit"],
                "content": "Lökosit (WBC): 21.5 x10³/µL (Segmenter Nötrofil: %60, Band Nötrofil: %18, Lenfosit: %18, Monosit: %3, Eozinofil: %1)"
            },
            "RBC": {
                "name": "Eritrosit (RBC) Sayımı",
                "keywords": ["rbc", "eritrosit", "alyuvar"],
                "content": "Eritrosit (RBC): 2.1 x10⁶/µL"
            },
            "PCV": {
                "name": "Hematokrit (PCV) & Hemoglobin",
                "keywords": ["pcv", "hematokrit", "hemoglobin", "hb"],
                "content": "Hematokrit (PCV): %12 | Hemoglobin (Hb): 4.2 g/dL"
            },
            "FIBRINOJEN": {
                "name": "Plazma Fibrinojeni & PP/F Oranı",
                "keywords": ["fibrinojen", "pp/f"],
                "content": "Plazma Fibrinojeni: 1050 mg/dL | PP/F Oranı: 7.23"
            },
            "BIYOKIMYA_GENEL": {
                "name": "Serum Biyokimyası Paneli",
                "keywords": ["biyokimya", "biyokimya paneli"],
                "content": "ALT: 45 U/L | AST: 210 U/L | GGT: 68 U/L | ALP: 110 U/L | CK: 190 U/L | LDH: 410 U/L | BUN: 42 mg/dL | Kreatinin: 1.6 mg/dL | Albümin: 2.6 g/dL | Globülin: 5.0 g/dL | Bilirubin: 1.2 mg/dL | Glikoz: 88 mg/dL | cTnI: 0.45 ng/mL"
            },
            "ALT": {
                "name": "ALT (Alanin Aminotransferaz)",
                "keywords": ["alt", "alanin aminotransferaz"],
                "content": "ALT (Alanin Aminotransferaz): 45 U/L"
            },
            "AST": {
                "name": "AST (Aspartat Aminotransferaz)",
                "keywords": ["ast", "aspartat aminotransferaz"],
                "content": "AST (Aspartat Aminotransferaz): 210 U/L"
            },
            "GGT": {
                "name": "GGT (Gama Glutamil Transferaz)",
                "keywords": ["ggt", "gama glutamil"],
                "content": "GGT (Gama Glutamil Transferaz): 68 U/L"
            },
            "ALP": {
                "name": "ALP (Alkalen Fosfataz)",
                "keywords": ["alp", "alkalen fosfataz"],
                "content": "ALP (Alkalen Fosfataz): 110 U/L"
            },
            "CK": {
                "name": "CK (Kreatin Kinaz)",
                "keywords": ["ck", "kreatin kinaz"],
                "content": "CK (Kreatin Kinaz): 190 U/L"
            },
            "LDH": {
                "name": "LDH (Laktat Dehidrogenaz)",
                "keywords": ["ldh", "laktat dehidrogenaz"],
                "content": "LDH (Laktat Dehidrogenaz): 410 U/L"
            },
            "BUN_URE": {
                "name": "BUN / Kan Üre Azotu",
                "keywords": ["bun", "üre", "kan üre"],
                "content": "BUN (Kan Üre Azotu): 42 mg/dL"
            },
            "KREATININ": {
                "name": "Kreatinin",
                "keywords": ["kreatinin"],
                "content": "Kreatinin: 1.6 mg/dL"
            },
            "ALBUMIN": {
                "name": "Albümin",
                "keywords": ["albümin", "albumin"],
                "content": "Albümin: 2.6 g/dL"
            },
            "GLOBULIN": {
                "name": "Globülin",
                "keywords": ["globülin", "globulin"],
                "content": "Globülin: 5.0 g/dL"
            },
            "BILIRUBIN": {
                "name": "Bilirubin (Total & İndirekt)",
                "keywords": ["bilirubin"],
                "content": "Total Bilirubin: 1.2 mg/dL | İndirekt Bilirubin: 0.8 mg/dL"
            },
            "GLIKOZ": {
                "name": "Glikoz (Kan Şekeri)",
                "keywords": ["glikoz", "glukoz", "şeker"],
                "content": "Glikoz: 88 mg/dL"
            },
            "TROPONIN": {
                "name": "Kardiyak Troponin I (cTnI)",
                "keywords": ["troponin", "ctni"],
                "content": "Kardiyak Troponin I (cTnI): 0.45 ng/mL"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.24 | pO₂: 52 mmHg | pCO₂: 50 mmHg | HCO₃⁻: 18.5 mmol/L | Baz Açığı (BE): -6.2 mmol/L | Laktat: 4.2 mmol/L"
            },
            "ULTRASON": {
                "name": "Ultrasonografi (USG) Bulguları",
                "keywords": ["ultrason", "usg", "ultrasonografi"],
                "content": "Abdominal USG: Karaciğer parankiminde 6 cm çapında kılıflı apse odağı, Vena Cava Caudalis lümeninde tıkayıcı trombüs ekojenitesi. Torakal USG: Pulmoner arter çevresinde hematom ve anevrizma alanları."
            },
            "EKOKARDIYOGRAFI": {
                "name": "Ekokardiyografi Bulguları",
                "keywords": ["ekokardiyografi", "echo", "eko"],
                "content": "Ekokardiyografi: Kalp kapakları ve perikard yapısı normal, sağ ventrikül hafif dilatasyonu izlendi."
            },
            "PERIKARDIYOSENTEZ": {
                "name": "Perikardiyosentez Sıvı Analizi",
                "keywords": ["perikardiyosentez", "ponksiyon", "sıvı delme", "perikard sıvı"],
                "content": "Perikardiyosentez: Uygulanmadı."
            },
            "KULTUR_MIKROBIYOLOJI": {
                "name": "Kültür & Mikrobiyoloji Sonucu",
                "keywords": ["kültür", "bakteri", "mikrobiyoloji"],
                "content": "Akciğer / Trombüs Biyopsi Kültürü: Fusobacterium necrophorum ve Trueperella pyogenes üremesi saptandı."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnezi & Bulgu Sorgulama Konsolu (Bireysel Parametre Sorgulama)</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde şıklar veya hazır butonlar <u>yoktur</u>. 
        Kafanızdaki klinik şüpheye göre ne öğrenmek istiyorsanız kutucuğa <b>kendi cümlenizle veya kelimelerinizle</b> yazınız. <br>
        Örnekler: <i>"Hayvan ne yiyor?"</i>, <i>"Ateşi kaç?"</i>, <i>"ALT kaç?"</i>, <i>"AST sonucu nedir?"</i>, <i>"Glutaraldehit testi?"</i>, <i>"USG bulgusu?"</i>, <i>"Perikardiyosentez sonucu?"</i>, <i>"BUN değeri?"</i>.
    </div>
""", unsafe_allow_html=True)

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
st.markdown("### 💬 Sorunuzu veya İncelemek İstediğiniz Parametreyi Yazınız:")

def match_query(user_text, categories_dict):
    text_clean = user_text.lower().strip()
    text_clean = (
        text_clean.replace("ı", "i")
        .replace("ğ", "g")
        .replace("ü", "u")
        .replace("ş", "s")
        .replace("ö", "o")
        .replace("ç", "c")
    )

    matched_cats = []

    for cat_key, cat_info in categories_dict.items():
        for kw in cat_info["keywords"]:
            kw_clean = (
                kw.lower()
                .replace("ı", "i")
                .replace("ğ", "g")
                .replace("ü", "u")
                .replace("ş", "s")
                .replace("ö", "o")
                .replace("ç", "c")
            )
            # Use strict word boundary for short terms (3 chars or fewer) to prevent false substring matches (e.g., 'alt' inside 'hastalık')
            if len(kw_clean) <= 3:
                pattern = r"\b" + re.escape(kw_clean) + r"\b"
                if re.search(pattern, text_clean):
                    matched_cats.append(cat_key)
                    break
            else:
                if kw_clean in text_clean:
                    matched_cats.append(cat_key)
                    break

    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız (Örn: Rasyon?, Ateş?, ALT?, AST?, USG?, Glutaraldehit?, Perikardiyosentez?):",
        key="query_input",
        placeholder="Örn: Hayvan ne yiyor?, Ateşi kaç?, ALT sonucu?, USG bulgusu?, Glutaraldehit testi?... "
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
            st.success(f"🎉 Teşekkürler! Sorunuzla ilişkili {new_discoveries} yeni klinik parametre / bulgu açığa çıkarıldı!")
        else:
            st.info("Bu parametre/bulgu zaten daha önce açığa çıkarılmıştı. Aşağıdaki keşifler listenizden okuyabilirsiniz.")
    else:
        st.warning("⚠️ Girdiğiniz soru veya kelimelerle eşleşen bir parametre bulunamadı. Lütfen aramanızı kontrol ediniz (Örn: 'rasyon', 'ateş', 'alt', 'ast', 'ggt', 'usg', 'perikardiyosentez', 'glutaraldehit', 'bun', 'üre').")

# Display Discovered Information
st.markdown("---")
st.markdown(f"### 📂 Keşfedilen Klinik İpuçları ve Ölçüm Sonuçları ({len(st.session_state.history[selected_case_name])} Parametre Açıldı)")

if st.session_state.history[selected_case_name]:
    for idx, item in enumerate(reversed(st.session_state.history[selected_case_name])):
        st.markdown(f"""
            <div class='card-found'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                    <span class='badge-category'>{item['title']}</span>
                    <span style='font-size:12px; color:#7F7F7F;'>Sorulan Soru: "{item['query']}"</span>
                </div>
                <div class='card-content'><b>🩺 Değer / Bulgu:</b> {item['content']}</div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Henüz bu vaka için sorgulama yapmadınız. Yukarıdaki arama kutusuna merak ettiğiniz parametreyi veya soruyu yazarak muayeneye başlayınız.")

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
            st.markdown("#### 🔑 Bu Vakanın Tüm Bireysel Parametreleri:")
            for ck, cv in active_case["categories"].items():
                st.markdown(f"**• {cv['name']}:** {cv['content']}")
        elif pass_code:
            st.error("Hatalı Şifre!")
