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
        "sikayet": "Gerdan ve çene altında ödem, iştahsızlık, süt veriminde düşüş ve durgunluk.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon ve Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "neyle besleniyor", "karbonhidrat", "mısır", "arpa", "yonca", "saman", "silaj", "fabrika yemi", "kesif", "kaba", "ot", "mera", "balya", "tel", "çivi", "yabancı"],
                "content": "Günlük rasyonda: 10 kg mısır silajı, 6 kg yonca kuru otu, 4 kg saman ve 8 kg fabrika kesif yemi verilmektedir. Balya parçalama esnasında kaba yeme inşaat tellerinin ve çivilerin karışmış olabileceği belirtilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon ve Coğrafi Geçmiş",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik", "dağ", "ova", "metre"],
                "content": "Ceyhan ovasında (rakım 50 metre) sabit tesistedir. Nakil öyküsü bulunmamaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce"],
                "content": "Geçmişinde kaydedilmiş hastalık öyküsü bulunmamaktadır. 2 ay önce sorunsuz doğum yapmıştır."
            },
            "ATES": {
                "name": "Vücut Sıcaklığı (Ateş)",
                "keywords": ["ateş", "sıcaklık", "derece", "febril"],
                "content": "Vücut Sıcaklığı: 39.8 °C"
            },
            "NABIZ": {
                "name": "Kalp Frekansı (Nabız)",
                "keywords": ["nabız", "kalp frekans", "atım"],
                "content": "Kalp Frekansı: 102 atım/dakika"
            },
            "SOLUNUM": {
                "name": "Solunum Frekansı",
                "keywords": ["solunum", "nefes", "dakikadaki solunum"],
                "content": "Solunum Frekansı: 42 nefes/dakika"
            },
            "MUKOZA_CRT": {
                "name": "Mukoza Rengi ve CRT",
                "keywords": ["mukoza", "crt", "kılcal damar", "renk"],
                "content": "Mukoza Rengi: Soluk pembe | Kılcal Damar Dolum Süresi (CRT): 2.5 saniye"
            },
            "ODEM_VENA_JUGULARIS": {
                "name": "Ödem ve Vena Jugularis Muayenesi",
                "keywords": ["ödem", "gerdan", "çene altı", "jugularis", "boyun damarı", "staz", "pulsasyon"],
                "content": "Gerdan ve submandibuler bölge: Soğuk, hamur kıvamında ödem | Vena Jugularis: Çene açısına kadar dolgun, yalancı jugular nabız mevcut"
            },
            "KALP_OSKULTASYONU": {
                "name": "Kalp Oskültasyonu (Kalp Sesleri)",
                "keywords": ["kalp ses", "oskültasyon", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "dinleme"],
                "content": "Kalp Oskültasyonu: Su çalkantı (splashing) sesi ve boğuk kalp sesleri"
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "inleme"],
                "content": "Sopa testi: Pozitif (+) | Kama testi: Pozitif (+) | Withers pinch testi: Pozitif (+)"
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "trombosit"],
                "content": "Lökosit (WBC): 22.4 x 10³/µL | Eritrosit (RBC): 5.4 x 10⁶/µL | Hematokrit (PCV): %28 | Hemoglobin (Hb): 9.2 g/dL | Plazma Fibrinojeni: 1250 mg/dL | Total Protein: 7.9 g/dL | Plazma Protein / Fibrinojen (PP/F) Oranı: 6.3 | Trombosit: 320 x 10³/µL"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası Sonuçları",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "bilirubin", "albümin", "globülin", "troponin"],
                "content": "Albümin: 2.8 g/dL | Globülin: 5.1 g/dL | AST: 118 U/L | GGT: 24 U/L | ALT: 22 U/L | ALP: 75 U/L | CK: 180 U/L | LDH: 360 U/L | BUN: 28 mg/dL | Kreatinin: 1.2 mg/dL | Total Bilirubin: 0.4 mg/dL | İndirekt Bilirubin: 0.2 mg/dL | Kardiyak Troponin I (cTnI): 0.85 ng/mL"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.32 | pO₂: 72 mmHg | pCO₂: 48 mmHg | HCO₃⁻: 20.2 mmol/L | Baz Açığı (BE): -4.1 mmol/L | Laktat: 2.8 mmol/L"
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme, Biyopsi ve Ponksiyon",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "perikardiyosentez", "ponksiyon", "sıvı", "vejetasyon", "apse", "trombüs"],
                "content": "Perikardiyosentez: Kirli sarı-yeşil, pürülan eksuda (Mikrobiyolojik kültürde Trueperella pyogenes). Ultrasonografi: Perikardiyal boşlukta fibrin bantları, gaz ekojeniteleri ve 4 cm kalınlığında sıvı. Retikulum çevresinde yapışıklıklar."
            }
        }
    },
    "Vaka B (Yonca)": {
        "kod": "VAKA_B",
        "sikayet": "Halsizlik, süt verimi düşüşü, bacak eklemlerinde şişlik ve topallık.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon ve Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "neyle besleniyor", "karbonhidrat", "mısır", "arpa", "yonca", "saman", "silaj", "fabrika yemi", "kesif", "kaba", "ot", "mera", "süt"],
                "content": "Günlük rasyonda: 12 kg mısır silajı, 7 kg yonca kuru otu, 3 kg saman ve 9 kg süt yemi verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon ve Coğrafi Geçmiş",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik"],
                "content": "Sabit süt tesisindedir. Rakım değişikliği veya nakil öyküsü bulunmamaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce", "iltihap"],
                "content": "3 hafta önce doğum sonrası metritis ve klinik mastitis tedavisi görmüştür."
            },
            "ATES": {
                "name": "Vücut Sıcaklığı (Ateş)",
                "keywords": ["ateş", "sıcaklık", "derece", "febril"],
                "content": "Vücut Sıcaklığı: 40.2 °C"
            },
            "NABIZ": {
                "name": "Kalp Frekansı (Nabız)",
                "keywords": ["nabız", "kalp frekans", "atım"],
                "content": "Kalp Frekansı: 110 atım/dakika"
            },
            "SOLUNUM": {
                "name": "Solunum Frekansı",
                "keywords": ["solunum", "nefes", "dakikadaki solunum"],
                "content": "Solunum Frekansı: 38 nefes/dakika"
            },
            "MUKOZA_CRT": {
                "name": "Mukoza Rengi ve CRT",
                "keywords": ["mukoza", "crt", "kılcal damar", "renk"],
                "content": "Mukoza Rengi: Soluk | Kılcal Damar Dolum Süresi (CRT): 3.0 saniye"
            },
            "ODEM_EKLEM": {
                "name": "Ödem, Eklem ve Vena Jugularis Muayenesi",
                "keywords": ["ödem", "gerdan", "eklem", "topallık", "bacak", "jugularis", "boyun damarı", "staz"],
                "content": "Gerdan bölgesi: Ödemli | Sol carpus ve tarsus eklemleri: Sıcak, şiş ve ağrılı | Vena Jugularis: Dolgun, jugular nabız yok"
            },
            "KALP_OSKULTASYONU": {
                "name": "Kalp Oskültasyonu (Kalp Sesleri)",
                "keywords": ["kalp ses", "oskültasyon", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "dinleme", "triküspid"],
                "content": "Kalp Oskültasyonu: Triküspid kapak odağında Grade IV/VI holosistolik üfürüm. Su çalkantı (splashing) sesi bulunmamaktadır"
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Sopa testi: Negatif (-) | Kama testi: Negatif (-) | Withers pinch testi: Negatif (-)"
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f"],
                "content": "Lökosit (WBC): 26.8 x 10³/µL | Eritrosit (RBC): 4.2 x 10⁶/µL | Hematokrit (PCV): %22 | Hemoglobin (Hb): 7.2 g/dL | Plazma Fibrinojeni: 980 mg/dL | Total Protein: 8.8 g/dL | Plazma Protein / Fibrinojen (PP/F) Oranı: 8.98 | Trombosit: 180 x 10³/µL"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası Sonuçları",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "bilirubin", "albümin", "globülin", "troponin"],
                "content": "Albümin: 2.3 g/dL | Globülin: 6.5 g/dL | AST: 145 U/L | GGT: 28 U/L | ALT: 25 U/L | ALP: 82 U/L | CK: 210 U/L | LDH: 390 U/L | BUN: 34 mg/dL | Kreatinin: 1.5 mg/dL | Total Bilirubin: 0.5 mg/dL | İndirekt Bilirubin: 0.3 mg/dL | Kardiyak Troponin I (cTnI): 1.20 ng/mL"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.30 | pO₂: 68 mmHg | pCO₂: 52 mmHg | HCO₃⁻: 18.8 mmol/L | Baz Açığı (BE): -5.2 mmol/L | Laktat: 3.1 mmol/L"
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme, Biyopsi ve Ponksiyon",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "eklem", "vejetasyon", "kitle"],
                "content": "Ekokardiyografi: Triküspid kapak üzerinde 3.5 cm çapında pürüzlü hiperekojen kitle (vejetasyon). Kan Kültürü & Eklem Sıvısı Kültürü: Trueperella pyogenes."
            }
        }
    },
    "Vaka C (Zümrüt)": {
        "kod": "VAKA_C",
        "sikayet": "Göğüs önü ve gerdanda yaygın şişlik, çabuk yorulma.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon ve Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "neyle besleniyor", "karbonhidrat", "mısır", "arpa", "yonca", "saman", "silaj", "ot", "mera"],
                "content": "Çayır otunca zengin 1900 metre rakımlı dağ merasında otlatılmaktadır. İlave fabrika yemi verilmemektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon ve Coğrafi Geçmiş",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik", "dağ", "ova", "metre"],
                "content": "3 hafta önce 50 metre rakımlı kıyı işletmesinden 1900 metre rakımlı yüksek dağ yaylasına nakledilmiştir."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce"],
                "content": "Geçmişinde kaydedilmiş hastalık öyküsü bulunmamaktadır."
            },
            "ATES": {
                "name": "Vücut Sıcaklığı (Ateş)",
                "keywords": ["ateş", "sıcaklık", "derece", "febril"],
                "content": "Vücut Sıcaklığı: 38.6 °C"
            },
            "NABIZ": {
                "name": "Kalp Frekansı (Nabız)",
                "keywords": ["nabız", "kalp frekans", "atım"],
                "content": "Kalp Frekansı: 96 atım/dakika"
            },
            "SOLUNUM": {
                "name": "Solunum Frekansı",
                "keywords": ["solunum", "nefes", "dakikadaki solunum"],
                "content": "Solunum Frekansı: 46 nefes/dakika"
            },
            "MUKOZA_CRT": {
                "name": "Mukoza Rengi ve CRT",
                "keywords": ["mukoza", "crt", "kılcal damar", "renk"],
                "content": "Mukoza Rengi: Pembe | Kılcal Damar Dolum Süresi (CRT): 1.8 saniye"
            },
            "ODEM_VENA_JUGULARIS": {
                "name": "Ödem ve Vena Jugularis Muayenesi",
                "keywords": ["ödem", "gerdan", "göğüs", "jugularis", "boyun damarı", "staz"],
                "content": "Gerdan ve göğüs önü: Geniş alana yayılmış soğuk hamur ödem | Vena Jugularis: Çene açısına kadar dolgun, jugular nabız yok"
            },
            "KALP_OSKULTASYONU": {
                "name": "Kalp Oskültasyonu (Kalp Sesleri)",
                "keywords": ["kalp ses", "oskültasyon", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "dinleme"],
                "content": "Kalp Oskültasyonu: Hiperdinamik güçlü kalp sesleri. Üfürüm veya su çalkantı sesi bulunmamaktadır"
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Sopa testi: Negatif (-) | Kama testi: Negatif (-) | Withers pinch testi: Negatif (-)"
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "polisitemi"],
                "content": "Lökosit (WBC): 7.2 x 10³/µL | Eritrosit (RBC): 10.8 x 10⁶/µL | Hematokrit (PCV): %54 | Hemoglobin (Hb): 17.2 g/dL | Plazma Fibrinojeni: 320 mg/dL | Total Protein: 7.3 g/dL | Plazma Protein / Fibrinojen (PP/F) Oranı: 22.8 | Trombosit: 410 x 10³/µL"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası Sonuçları",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "bilirubin", "albümin", "globülin", "troponin"],
                "content": "Albümin: 3.2 g/dL | Globülin: 4.1 g/dL | AST: 68 U/L | GGT: 18 U/L | ALT: 18 U/L | ALP: 62 U/L | CK: 110 U/L | LDH: 280 U/L | BUN: 18 mg/dL | Kreatinin: 0.9 mg/dL | Total Bilirubin: 0.3 mg/dL | İndirekt Bilirubin: 0.2 mg/dL | Kardiyak Troponin I (cTnI): 0.12 ng/mL"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "oksijen", "hipoksi"],
                "content": "Kan pH: 7.36 | pO₂: 48 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 23.5 mmol/L | Baz Açığı (BE): -0.8 mmol/L | Laktat: 1.5 mmol/L"
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme, Biyopsi ve Ponksiyon",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "pulmoner", "ventrikül"],
                "content": "Ekokardiyografi: Sağ ventrikül serbest duvar kalınlığında artış (sağ ventrikül hipertrofisi), pulmoner arter çapında genişleme. Kültür: Kan ve perikard sıvısında bakteri üremesi yok."
            }
        }
    },
    "Vaka D (Yiğit)": {
        "kod": "VAKA_D",
        "sikayet": "Ağız ve burundan parlak kırmızı taze kan gelmesi (hemoptizi) ve siyah dışkı yapma (melena).",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon ve Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "neyle besleniyor", "karbonhidrat", "mısır", "arpa", "yonca", "saman", "silaj", "besi", "kaba", "nişasta"],
                "content": "Günlük rasyonda: 10 kg mısır kırması, 10 kg arpa kırması, 5 kg yonca kuru otu, 2 kg saman verilmektedir. Yoğun yem oranı %80 seviyesindedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon ve Coğrafi Geçmiş",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya"],
                "content": "Besi padoğunda barındırılmaktadır. Rakım değişikliği bulunmamaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce", "asidoz", "şişkinlik", "timpani", "rumenitis"],
                "content": "Geçmişinde tekrarlayan akut/subakut rumen asidozu ve kronik hafif rumen timpani öyküsü mevcuttur."
            },
            "ATES": {
                "name": "Vücut Sıcaklığı (Ateş)",
                "keywords": ["ateş", "sıcaklık", "derece", "febril"],
                "content": "Vücut Sıcaklığı: 39.2 °C"
            },
            "NABIZ": {
                "name": "Kalp Frekansı (Nabız)",
                "keywords": ["nabız", "kalp frekans", "atım"],
                "content": "Kalp Frekansı: 118 atım/dakika"
            },
            "SOLUNUM": {
                "name": "Solunum Frekansı",
                "keywords": ["solunum", "nefes", "dakikadaki solunum"],
                "content": "Solunum Frekansı: 52 nefes/dakika"
            },
            "MUKOZA_CRT": {
                "name": "Mukoza Rengi ve CRT",
                "keywords": ["mukoza", "crt", "kılcal damar", "renk"],
                "content": "Mukoza Rengi: Beyaz | Kılcal Damar Dolum Süresi (CRT): 4.0 saniye"
            },
            "DISKI_KANAMA": {
                "name": "Ağız/Burun Akıntısı ve Dışkı Muayenesi",
                "keywords": ["kan", "hemoptizi", "melena", "dışkı", "ağız", "burun", "kırmızı", "siyah"],
                "content": "Ağız ve Burun Çıkışı: Köpüklü, taze parlak kırmızı kan (hemoptizi) | Dışkı Muayenesi: Siyah, katran kıvamında (melena)"
            },
            "ODEM_VENA_JUGULARIS": {
                "name": "Ödem ve Vena Jugularis Muayenesi",
                "keywords": ["ödem", "gerdan", "jugularis", "boyun damarı", "staz"],
                "content": "Gerdan bölgesi: Ödem yok | Vena Jugularis: Hafif dolgun"
            },
            "KALP_OSKULTASYONU": {
                "name": "Kalp Oskültasyonu (Kalp Sesleri)",
                "keywords": ["kalp ses", "oskültasyon", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "dinleme"],
                "content": "Kalp Oskültasyonu: Taşikardik kalp sesleri"
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Sopa testi: Negatif (-) | Kama testi: Negatif (-) | Withers pinch testi: Negatif (-)"
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "anemi"],
                "content": "Lökosit (WBC): 21.5 x 10³/µL | Eritrosit (RBC): 2.1 x 10⁶/µL | Hematokrit (PCV): %12 | Hemoglobin (Hb): 4.2 g/dL | Plazma Fibrinojeni: 1050 mg/dL | Total Protein: 7.6 g/dL | Plazma Protein / Fibrinojen (PP/F) Oranı: 7.23 | Trombosit: 140 x 10³/µL"
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası Sonuçları",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "bilirubin", "albümin", "globülin", "troponin", "karaciğer"],
                "content": "Albümin: 2.6 g/dL | Globülin: 5.0 g/dL | AST: 210 U/L | GGT: 68 U/L | ALT: 45 U/L | ALP: 110 U/L | CK: 190 U/L | LDH: 410 U/L | BUN: 42 mg/dL | Kreatinin: 1.6 mg/dL | Total Bilirubin: 1.2 mg/dL | İndirekt Bilirubin: 0.8 mg/dL | Kardiyak Troponin I (cTnI): 0.45 ng/mL"
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.24 | pO₂: 52 mmHg | pCO₂: 50 mmHg | HCO₃⁻: 18.5 mmol/L | Baz Açığı (BE): -6.2 mmol/L | Laktat: 4.2 mmol/L"
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme, Biyopsi ve Ponksiyon",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "karaciğer", "apse", "vena cava", "trombüs", "arter"],
                "content": "Abdominal Ultrasonografi: Karaciğer parankiminde 6 cm çapında kılıflı apse odağı, Vena Cava Caudalis lümeninde tıkayıcı trombüs ekojenitesi. Torakal Ultrasonografi: Pulmoner arter çevresinde hematom ve anevrizma alanları."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnezi & Bulgu Sorgulama Konsolu (Serbest Metin Sorgulama)</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde şıklar veya hazır butonlar <u>yoktur</u>. 
        Kafanızdaki klinik şüpheye göre ne öğrenmek istiyorsanız kutucuğa <b>kendi cümlenizle veya kelimelerinizle</b> yazınız 
        (Örn: <i>"Hayvan ne ile besleniyor?"</i>, <i>"Nereden satın alınmış?"</i>, <i>"Geçmişinde rahim iltihabı var mı?"</i>, <i>"Kalp sesleri nasıl?"</i>, <i>"Ateşi kaç derece?"</i>, <i>"Hemogram tahlili istiyorum"</i>).
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
st.markdown("### 💬 Sorunuzu veya İncelemek İstediğiniz Muayeneyi Yazınız:")

def match_query(user_text, categories_dict):
    text_clean = user_text.lower().strip()
    text_clean = text_clean.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    
    matched_cats = []
    
    for cat_key, cat_info in categories_dict.items():
        for kw in cat_info["keywords"]:
            kw_clean = kw.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
            if re.search(r'\b' + re.escape(kw_clean), text_clean) or kw_clean in text_clean:
                matched_cats.append(cat_key)
                break
                
    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız (Örn: Rasyon bilgisi nedir?, Kalp sesleri nasıl?, Ateşi kaç?):",
        key="query_input",
        placeholder="Örn: Hayvan ne yiyor?, Yayla öyküsü var mı?, Hemogram sonuçları nedir?..."
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
        st.warning("⚠️ Girdiğiniz soru veya kelimelerle eşleşen bir bilgi bulunamadı. Lütfen sorunuzu farklı anahtar kelimelerle yazınız (Örn: 'rasyon', 'rakım', 'ateş', 'kalp sesleri', 'geçmiş hastalık', 'hemogram', 'ultrason').")

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
