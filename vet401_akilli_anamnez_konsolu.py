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
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık & Yaş / Irk Bilgisi",
                "keywords": ["ağırlık", "kilo", "kg", "canlı ağırlık", "yaş", "ırk", "kaç kilo"],
                "content": "Canlı Ağırlık: 540 kg | Yaş: 5 Yaşlı | Irk: Siyah Alaca (Holstein) Süt Sığırı."
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
                "content": "Geçmişinde kaydedilmiş kronik bir mastitis, metritis veya metabolik hastalık öyküsü bulunmamaktadır. 2 ay önce sorunsuz doğum yapmıştır."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "amonyak", "altlık", "havalandırma", "zemin", "çit", "tel", "inşaat"],
                "content": "Yarı açık serbest duraklı ahır. Kaba yem hazırlama alanında son inşaat atıklarından kalma tel ve çivi parçalarının rasyona karışmış olabileceği bildirilmiştir."
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
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık & Yaş / Irk Bilgisi",
                "keywords": ["ağırlık", "kilo", "kg", "canlı ağırlık", "yaş", "ırk", "kaç kilo"],
                "content": "Canlı Ağırlık: 580 kg | Yaş: 4 Yaşlı | Irk: Siyah Alaca (Holstein) Süt Sığırı."
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
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "amonyak", "altlık", "havalandırma", "zemin", "nem"],
                "content": "Kapalı duraklı ahır. Altlık nemli ve havalandırma orta düzeydedir."
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
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık & Yaş / Irk Bilgisi",
                "keywords": ["ağırlık", "kilo", "kg", "canlı ağırlık", "yaş", "ırk", "kaç kilo"],
                "content": "Canlı Ağırlık: 460 kg | Yaş: 3 Yaşlı | Irk: Doğu Anadolu Kırmızı Melezi Düve."
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
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "mera", "yayla", "otlak", "geceleme"],
                "content": "Gündüzleri yüksek rakımlı otlakta serbest otlama, geceleri basit yarı açık ağılda barınma."
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
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık & Yaş / Irk Bilgisi",
                "keywords": ["ağırlık", "kilo", "kg", "canlı ağırlık", "yaş", "ırk", "kaç kilo"],
                "content": "Canlı Ağırlık: 620 kg | Yaş: 18 Aylık | Irk: Şarole Melezi Besi Danası."
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
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "besi", "padok", "zemin", "toz"],
                "content": "Yoğun besi padoğu. Izgaralı zemin, toz düzeyi ve amonyak yoğunluğu yüksektir."
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
        "sikayet": "Baş, boyun ve göz çevresinde dairesel, kepekli, kalın grimsi-beyaz kabuklu kıl dökülmeleri ve tüy kaybı.",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık & Yaş / Irk Bilgisi",
                "keywords": ["ağırlık", "kilo", "kg", "canlı ağırlık", "yaş", "ırk", "kaç kilo"],
                "content": "Canlı Ağırlık: 220 kg | Yaş: 8 Aylık | Irk: Holstein Melezi Düve."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "saman", "kaba", "kesif"],
                "content": "Günlük rasyonda: 4 kg saman, 2 kg yonca otu, 3 kg buzağı büyütme yemi verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "coğrafya"],
                "content": "Ceyhan ova padoğunda toplu genç hayvan padoğunda barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "aşı"],
                "content": "Sürüye yeni katılan genç hayvanlarla temas sonrası benzer lezyonlar 3 genç düvede daha başlamıştır."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "kalabalık", "ışık", "karanlık", "nem", "altlık", "sürtünme"],
                "content": "Kapalı, nemli ve yetersiz güneş ışığı alan kalabalık pedok. Ahır demirlerinde ve yemlik kenarlarında kıl yumakları yapışmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "vital"],
                "content": "Vücut Sıcaklığı: 38.7 °C | Kalp Frekansı: 78 atım/dk | Solunum Frekansı: 26 nefes/dk | Mukoza: Pembe | CRT: 1.5 saniye | Dehidrasyon: %0."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve akciğer oskültasyonu tamamen fizyolojik normal sınırlar içerisindedir."
            },
            "DERI_LEZYON_MUAYENESI": {
                "name": "Deri & Lezyon Muayenesi",
                "keywords": ["deri", "lezyon", "kabuk", "kıl", "dökülme", "kaşıntı", "pruritus", "alopesi", "daire", "ringworm", "yara"],
                "content": "Baş, gırtlak ve göz çevresinde 3–6 cm çapında dairesel, keskin sınırlı, gümüşi-gri kabukla kaplı alopesik (kılsız) odak lezyonları. Kaşıntı yok veya çok hafiftir (Pruritus negatif/hafif)."
            },
            "DERI_KAZINTISI_MIKROSKOPI": {
                "name": "Deri Kazıntısı & Mikroskopik İnceleme",
                "keywords": ["kazıntı", "mikroskop", "lam", "froti", "koh", "spor", "hif", "mantar"],
                "content": "%10 KOH (Potasyum Hidroksit) ile hazırlanan yüzeysel kabuk ve kıl kökü preparatında kıl şaftı etrafında dizilmiş belirgin ektoparaziter artrospor (arthrospore) zincirleri ve fungal hifler gözlendi."
            },
            "WOOD_LAMBASI_KULTUR": {
                "name": "Wood Lambası & Mantar Kültürü",
                "keywords": ["wood", "lamba", "floresan", "kültür", "trichophyton", "fungus"],
                "content": "Wood Lambası Muayenesi: Floresan ışıma vermedi (Trichophyton verrucosum için tipik Wood negatif reaksiyonu). Sabouraud Dextrose Agar (SDA) Mantar Kültürü: Trichophyton verrucosum üremesi doğrulandı."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "nötrofil", "lenfosit", "cbc"],
                "content": "Lökosit (WBC): 8.1 x10³/µL | Eritrosit (RBC): 6.8 x10⁶/µL | Hemoglobin (Hb): 11.2 g/dL | Hematokrit (PCV): %34 | Nötrofil: %48 | Lenfosit: %42 | Monosit: %5 | Eozinofil: %4 | Bazofil: %1 | Fibrinojen: 310 mg/dL (Tamamen normal)."
            },
            "BIYOKIMYA_ALT": {"name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 20 U/L"},
            "BIYOKIMYA_AST": {"name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 78 U/L"},
            "BIYOKIMYA_GGT": {"name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 16 U/L"},
            "BIYOKIMYA_BUN": {"name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre"], "content": "BUN: 15 mg/dL"},
            "BIYOKIMYA_KREATININ": {"name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 0.8 mg/dL"},
            "BIYOKIMYA_ALBUMIN": {"name": "Serum Albümin (ALB)", "keywords": ["albümin"], "content": "Serum Albümin: 3.3 g/dL"},
            "BIYOKIMYA_GLOBULIN": {"name": "Serum Globülin", "keywords": ["globülin"], "content": "Serum Globülin: 3.6 g/dL"},
            "BIYOKIMYA_TP": {"name": "Serum Total Protein (TP)", "keywords": ["total protein", "tp"], "content": "Serum Total Protein: 6.9 g/dL"},
            "GLUTERALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 18 dakikada pıhtılaşma (Negatif / Fizyolojik Normal)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "laktat"],
                "content": "Kan pH: 7.41 | pO₂: 88 mmHg | pCO₂: 40 mmHg | HCO₃⁻: 24.2 mmol/L | Baz Açığı: +0.5 mmol/L | Laktat: 1.1 mmol/L (Tamamen normal)."
            }
        }
    },
    "Vaka F (Nazar)": {
        "kod": "VAKA_F",
        "sikayet": "Şiddetli, durdurulamayan gece kaşıntısı, baş/boyun ve kuyruk sokumunda derinin kalınlaşması, kıvrımlaşması ve kepekli yaralar.",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık & Yaş / Irk Bilgisi",
                "keywords": ["ağırlık", "kilo", "kg", "canlı ağırlık", "yaş", "ırk", "kaç kilo"],
                "content": "Canlı Ağırlık: 380 kg | Yaş: 14 Aylık | Irk: Melez Besi Tosunu."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "saman", "kaba", "kesif"],
                "content": "Günlük rasyonda: 6 kg saman, 3 kg yonca kuru otu, 6 kg besi yemi verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk"],
                "content": "Kapalı besihane tesisi."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Aynı padoktaki 4 tosunda daha son 2 haftadır şiddetli duvarlara sürtünme ve kıllarda dökülme başlamıştır."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "karanlık", "nemli", "hijyen", "sürtünme", "duvar"],
                "content": "Karanlık, nemli, aşırı kalabalık ve hijyen koşulları zayıf besihane padoğu. Ahır direklerinde ve demirlerde yoğun kıl birikimi vardır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "vital"],
                "content": "Vücut Sıcaklığı: 38.9 °C | Kalp Frekansı: 84 atım/dk | Solunum Frekansı: 28 nefes/dk | Mukoza: Pembe | CRT: 1.6 saniye | Dehidrasyon: %0."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve akciğer oskültasyonu tamamen normaldir."
            },
            "DERI_LEZYON_MUAYENESI": {
                "name": "Deri & Lezyon Muayenesi",
                "keywords": ["deri", "lezyon", "kabuk", "kıl", "dökülme", "kaşıntı", "pruritus", "likenifikasyon", "kıvrım", "fil derisi", "uyuz", "yara"],
                "content": "Baş, gırtlak, boyun ve kuyruk sokumu çevresinde deride aşırı kalınlaşma, sertleşme (likenifikasyon / fil derisi görünümü), kıvrımlaşma, eksudatif kepekli kabuklanmalar. Şiddetli derecede Pozitif Pruritus (Hayvan durmaksızın duvarlara ve demirlere sürtünmektedir)."
            },
            "DERI_KAZINTISI_PARAZITOLOJI": {
                "name": "Derin Deri Kazıntısı & Parazitoloji",
                "keywords": ["kazıntı", "derin kazıntı", "parazit", "akar", "mite", "uyuz", "sarcoptes", "psoroptes", "mikroskop"],
                "content": "Lezyon kenarından kanatılacak şekilde alınan Derin Deri Kazıntısının mineral yağ altında mikroskopik muayenesinde: Yuvarlak gövdeli, kısa bacaklı canlı Sarcoptes scabiei var. bovis akarları (miteları) ve yumurtaları bol miktarda tespit edildi."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "eozinofil", "eozinofili", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "cbc"],
                "content": "Lökosit (WBC): 12.8 x10³/µL | Eritrosit (RBC): 6.2 x10⁶/µL | Hemoglobin (Hb): 10.8 g/dL | Hematokrit (PCV): %32 | Nötrofil: %42 | Lenfosit: %38 | Monosit: %4 | Eozinofil: %15 (Belirgin Eozinofili / Allerjik Parasiter Reaksiyon!) | Bazofil: %1 | Plazma Fibrinojeni: 340 mg/dL."
            },
            "BIYOKIMYA_ALT": {"name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 22 U/L"},
            "BIYOKIMYA_AST": {"name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 72 U/L"},
            "BIYOKIMYA_GGT": {"name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 18 U/L"},
            "BIYOKIMYA_BUN": {"name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre"], "content": "BUN: 16 mg/dL"},
            "BIYOKIMYA_KREATININ": {"name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 0.9 mg/dL"},
            "BIYOKIMYA_ALBUMIN": {"name": "Serum Albümin (ALB)", "keywords": ["albümin"], "content": "Serum Albümin: 3.2 g/dL"},
            "BIYOKIMYA_GLOBULIN": {"name": "Serum Globülin", "keywords": ["globülin"], "content": "Serum Globülin: 3.8 g/dL"},
            "BIYOKIMYA_TP": {"name": "Serum Total Protein (TP)", "keywords": ["total protein", "tp"], "content": "Serum Total Protein: 7.0 g/dL"},
            "GLUTERALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 16 dakikada pıhtılaşma (Negatif / Normal)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "laktat"],
                "content": "Kan pH: 7.39 | pO₂: 86 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 23.8 mmol/L | Baz Açığı: +0.2 mmol/L | Laktat: 1.3 mmol/L."
            }
        }
    },
    "Vaka G (Çiçek)": {
        "kod": "VAKA_G",
        "sikayet": "Merada otlama sonrası sadece vücudun beyaz deri alanlarında şiddetli ödem, kızarıklık, soyulma, çatlama ve ağrılı nekroz.",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık & Yaş / Irk Bilgisi",
                "keywords": ["ağırlık", "kilo", "kg", "canlı ağırlık", "yaş", "ırk", "kaç kilo"],
                "content": "Canlı Ağırlık: 450 kg | Yaş: 2 Yaşlı | Irk: Siyah Alaca (Holstein) Alacalı Düve."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "mera", "otlatma", "ot", "otlak", "bitki", "lantana", "sarı kantaron"],
                "content": "Son 3 haftadır yeşil ot ağırlıklı ıslak çayır merasında ve çalı çırpı yoğun merada serbest otlatılmaktadır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "mera", "güneş"],
                "content": "Açık merada yoğun doğrudan güneş ışığına maruz kalmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "sarılık", "ikter", "fasiolazis", "kelebek"],
                "content": "Geçmişinde kronik karaciğer kelebeği (Fasciola hepatica) öyküsü ve hafif sarılık kaydı mevcuttur."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "mera", "güneş", "gölge"],
                "content": "Gündüzleri gölgesiz açık merada otlama."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "ikter", "sarılık", "crt", "vital"],
                "content": "Vücut Sıcaklığı: 39.6 °C | Kalp Frekansı: 92 atım/dk | Solunum Frekansı: 36 nefes/dk | Mukoza: Belirgin İkterik (Sarımtırak) | CRT: 2.2 saniye | Dehidrasyon: %5 | Siyah deri bölgeleri tamamen normalken, BEYAZ pigmentsiz deri bölgelerinde sıcak, ödemli, çatlamış nekrotik alanlar."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve akciğer sesleri ritmik ve fizyolojiktir."
            },
            "DERI_LEZYON_MUAYENESI": {
                "name": "Deri & Lezyon Muayenesi (Fotosensitizasyon)",
                "keywords": ["deri", "lezyon", "güneş", "fotosensitizasyon", "beyaz deri", "pigmentsiz", "ödem", "nekroz", "soyulma", "yangı", "solar"],
                "content": "Hassas Güneş Yanığı Dermatitisi (Hepatojen Fotosensitizasyon): Yalnızca vücudun BEYAZ (pigmentsiz) kıllarla kaplı deri alanlarında eritromatöz şiddetli ödem, deri çatlamaları, serum sızması, kuruma ve tabaka halinde soyulan nekrotik kabuklar. Siyah pigmente deri alanları ise milimetrik olarak tamamen SAĞLAMDIR!"
            },
            "DERI_KAZINTISI_PARAZITOLOJI": {
                "name": "Deri Kazıntısı & Mikroskopik İnceleme",
                "keywords": ["kazıntı", "parazit", "akar", "mantar"],
                "content": "Deri kazıntısında ektoparazit veya fungal etken saptanmadı (Negatif)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "cbc"],
                "content": "Lökosit (WBC): 14.2 x10³/µL | Eritrosit (RBC): 5.8 x10⁶/µL | Hemoglobin (Hb): 10.2 g/dL | Hematokrit (PCV): %31 | Nötrofil: %62 | Lenfosit: %30 | Monosit: %5 | Eozinofil: %2 | Plazma Fibrinojeni: 620 mg/dL."
            },
            "BIYOKIMYA_ALT": {"name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 38 U/L"},
            "BIYOKIMYA_AST": {"name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast", "karaciğer"], "content": "AST: 280 U/L (Karaciğer parankim hasarı)"},
            "BIYOKIMYA_GGT": {"name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt", "safra", "karaciğer"], "content": "GGT: 145 U/L (Safra kanalı stazı / Filloeritrin atılım bozukluğu)"},
            "BIYOKIMYA_ALP": {"name": "ALP (Alkalen Fosfataz)", "keywords": ["alp"], "content": "ALP: 210 U/L"},
            "BIYOKIMYA_BILIRUBIN": {"name": "Bilirubin Fraksiyonları", "keywords": ["bilirubin", "sarılık", "ikter"], "content": "Total Bilirubin: 3.8 mg/dL | Direkt Bilirubin: 2.2 mg/dL | İndirekt Bilirubin: 1.6 mg/dL (Hepatojen İkter)"},
            "BIYOKIMYA_BUN": {"name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre"], "content": "BUN: 22 mg/dL"},
            "BIYOKIMYA_KREATININ": {"name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 1.1 mg/dL"},
            "BIYOKIMYA_ALBUMIN": {"name": "Serum Albümin (ALB)", "keywords": ["albümin"], "content": "Serum Albümin: 2.6 g/dL"},
            "BIYOKIMYA_GLOBULIN": {"name": "Serum Globülin", "keywords": ["globülin"], "content": "Serum Globülin: 4.8 g/dL"},
            "BIYOKIMYA_TP": {"name": "Serum Total Protein (TP)", "keywords": ["total protein", "tp"], "content": "Serum Total Protein: 7.4 g/dL"},
            "GLUTERALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 6.5 dakikada pıhtılaşma (Pozitif)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "laktat"],
                "content": "Kan pH: 7.34 | pO₂: 76 mmHg | pCO₂: 46 mmHg | HCO₃⁻: 21.0 mmol/L | Baz Açığı: -2.5 mmol/L | Laktat: 2.2 mmol/L."
            },
            "ULTRASON_KARACIGER": {
                "name": "Abdominal USG (Karaciğer / Safra)",
                "keywords": ["ultrason", "usg", "karaciğer", "safra"],
                "content": "Abdominal Ultrasonografi: Karaciğer parankiminde hiperekojenik fibrotik alanlar, safra kanallarında genişleme ve duvarda kalınlaşma."
            }
        }
    },
    "Vaka H (Ateş)": {
        "kod": "VAKA_H",
        "sikayet": "Tüm vücutta aniden beliren mercimek ile ceviz büyüklüğünde, ödemli, kabarık, kaşıntılı kurdeşen (urtikarya) plak lezyonları.",
        "categories": {
            "CANLI_AGIRLIK": {
                "name": "Canlı Ağırlık & Yaş / Irk Bilgisi",
                "keywords": ["ağırlık", "kilo", "kg", "canlı ağırlık", "yaş", "ırk", "kaç kilo"],
                "content": "Canlı Ağırlık: 510 kg | Yaş: 3 Yaşlı | Irk: Siyah Alaca (Holstein) Süt Sığırı."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "ilaç", "aşı", "enjeksiyon", "yeni yem"],
                "content": "2 saat önce yeni parti yüksek proteinli fabrika kesif yemi verilmiş ve eş zamanlı olarak parenteral penisilin-streptomisin uygulaması yapılmıştır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk"],
                "content": "Süt işletmesi barınağı."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Geçmiş Öykü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "alerji", "allerji"],
                "content": "Geçmişinde protein zengin yem değişikliği sonrası hafif kaşıntı öyküsü vardır."
            },
            "AHIR_BARINAK_SARTLARI": {
                "name": "Ahır Yapısı & Barınak Şartları",
                "keywords": ["ahır", "barınak", "sinek", "arı", "böcek"],
                "content": "Açık duraklı süt ahırı. Ahır çevresinde böcek/arı aktivitesi mevcuttur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "vital", "ödem"],
                "content": "Vücut Sıcaklığı: 39.1 °C | Kalp Frekansı: 98 atım/dk | Solunum Frekansı: 44 nefes/dk (Hafif hırıltılı) | Mukoza: Hiperemik (Kızarık) | CRT: 1.8 saniye | Dehidrasyon: %0 | Göz kapağı, anüs çevresi ve vulvada akut ödem."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer", "hırıltı"],
                "content": "Kalp sesleri taşikardik. Akciğer oskültasyonunda hafif üst solunum yolu bronşospazmına bağlı hışırtı sesleri."
            },
            "DERI_LEZYON_MUAYENESI": {
                "name": "Deri & Lezyon Muayenesi (Urtikarya)",
                "keywords": ["deri", "lezyon", "urtikarya", "kurdeşen", "plak", "kabarık", "ödem", "kaşıntı", "allerji", "alerji", "kızarıklık"],
                "content": "Akut Allerjik Urtikarya (Kurdeşen): Tüm vücut yüzeyinde, boyun, göğüs ve sağrı bölgesinde aniden şekillenen 1–5 cm çapında, dairesel/oval, üzeri kıllarla kaplı, düzgün kenarlı, basmakla çöküntü yapan akut eritematöz ödemli kabarık plak lezyonları (Wheals / Ürtiker plakları). Yoğun kaşıntı ve huzursuzluk mevcuttur."
            },
            "DERI_KAZINTISI_PARAZITOLOJI": {
                "name": "Deri Kazıntısı & Mikroskopik İnceleme",
                "keywords": ["kazıntı", "parazit", "akar", "mantar"],
                "content": "Deri kazıntısında akar veya mantar etkeni saptanmadı (Negatif)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "eozinofil", "eozinofili", "kan sayım", "fibrinojen", "cbc"],
                "content": "Lökosit (WBC): 11.2 x10³/µL | Eritrosit (RBC): 6.4 x10⁶/µL | Hemoglobin (Hb): 11.5 g/dL | Hematokrit (PCV): %33 | Nötrofil: %45 | Lenfosit: %38 | Monosit: %4 | Eozinofil: %12 (Allerjik Tip I Aşırı Duyarlılık Reaksiyonuna bağlı Eozinofili!) | Bazofil: %1 | Plazma Fibrinojeni: 320 mg/dL."
            },
            "BIYOKIMYA_ALT": {"name": "ALT (Alanin Aminotransferaz)", "keywords": ["alt"], "content": "ALT: 21 U/L"},
            "BIYOKIMYA_AST": {"name": "AST (Aspartat Aminotransferaz)", "keywords": ["ast"], "content": "AST: 74 U/L"},
            "BIYOKIMYA_GGT": {"name": "GGT (Gama Glutamil Transferaz)", "keywords": ["ggt"], "content": "GGT: 19 U/L"},
            "BIYOKIMYA_BUN": {"name": "BUN (Kan Üre Azotu)", "keywords": ["bun", "üre"], "content": "BUN: 17 mg/dL"},
            "BIYOKIMYA_KREATININ": {"name": "Kreatinin", "keywords": ["kreatinin"], "content": "Kreatinin: 0.9 mg/dL"},
            "BIYOKIMYA_ALBUMIN": {"name": "Serum Albümin (ALB)", "keywords": ["albümin"], "content": "Serum Albümin: 3.3 g/dL"},
            "BIYOKIMYA_GLOBULIN": {"name": "Serum Globülin", "keywords": ["globülin"], "content": "Serum Globülin: 3.7 g/dL"},
            "BIYOKIMYA_TP": {"name": "Serum Total Protein (TP)", "keywords": ["total protein", "tp"], "content": "Serum Total Protein: 7.0 g/dL"},
            "GLUTERALDEHIT": {
                "name": "Glutaraldehit Pıhtılaşma Testi",
                "keywords": ["glutaraldehit", "pıhtılaşma"],
                "content": "Glutaraldehit Pıhtılaşma Testi: 15 dakikada pıhtılaşma (Negatif / Normal)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "laktat"],
                "content": "Kan pH: 7.38 | pO₂: 82 mmHg | pCO₂: 43 mmHg | HCO₃⁻: 23.0 mmol/L | Baz Açığı: -0.5 mmol/L | Laktat: 1.4 mmol/L."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnezi & Bulgu Sorgulama Konsolu (Serbest Metin Sorgulama)</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde hazır şıklar yoktur. 
        Kafanızdaki klinik şüpheye göre ne öğrenmek istiyorsanız kutucuğa <b>kendi kelimelerinizle</b> yazınız 
        (Örn: <i>"Canlı ağırlığı kaç kg?"</i>, <i>"Hayvan ne yiyor?"</i>, <i>"Ateşi kaç derece?"</i>, <i>"Deri lezyonu var mı?"</i>, <i>"Deri kazıntısı mantar yönünden incelendi mi?"</i>, <i>"ALT, AST, GGT, Hemogram verileri nedir?"</i>).
    </div>
""", unsafe_allow_html=True)

# Select Case
selected_case_name = st.selectbox(
    "🔍 İncelemek İstediğiniz Vakayı Seçiniz:",
    options=list(CASES.keys()),
    index=0
)

# BUG FIX: Reset search history when switching cases so previous case results don't linger!
if "current_case_selection" not in st.session_state:
    st.session_state.current_case_selection = selected_case_name

if st.session_state.current_case_selection != selected_case_name:
    st.session_state.current_case_selection = selected_case_name
    if "query_input" in st.session_state:
        st.session_state["query_input"] = ""

active_case = CASES[selected_case_name]

st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — İlk Başvuru Şikayeti</div>", unsafe_allow_html=True)
st.info(f"**Hastanın Başvuru Şikayeti:** {active_case['sikayet']}")

# Session State for Questions History per Case
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
        "Sorunuzu Buraya Yazınız (Örn: Ağırlığı kaç?, Rasyon?, Ateş?, Lezyon var mı?, Deri kazıntısı?, AST?, ALT?):",
        key="query_input",
        placeholder="Örn: Canlı ağırlığı?, Ateşi?, Deri kazıntısı?, Hemogram?, ALT?..."
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
        st.warning("⚠️ Girdiğiniz soru veya kelimelerle eşleşen bir bilgi bulunamadı. Lütfen sorunuzu farklı anahtar kelimelerle yazınız (Örn: 'canlı ağırlık', 'rasyon', 'ateş', 'deri', 'kazıntı', 'hemogram', 'alt', 'ast').")

# Display Discovered Information ONLY for Current Active Case
st.markdown("---")
st.markdown(f"### 📂 {selected_case_name} — Keşfedilen Klinik İpuçları ve Muayene Bulguları ({len(st.session_state.history[selected_case_name])} Bilgi Açıldı)")

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
    st.info(f"Henüz {selected_case_name} için soru sormadınız. Yukarıdaki arama kutusuna merak ettiğiniz soruyu yazarak muayeneye başlayınız.")

# Reset History Button for Active Case
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
            st.markdown(f"#### 🔑 {selected_case_name} Gizli Tüm Bilgileri:")
            for ck, cv in active_case["categories"].items():
                st.markdown(f"**• {cv['name']}:** {cv['content']}")
        elif pass_code:
            st.error("Hatalı Şifre!")
