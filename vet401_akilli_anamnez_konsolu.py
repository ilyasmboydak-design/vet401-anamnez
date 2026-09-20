import streamlit as st
import re
import os

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
        font-size: 14px;
        color: #262626;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    .badge-category {
        background-color: #D9E1F2;
        color: #1F4E79;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to find images in gorseller/ directory robustly
def find_gorsel_path(target_filename):
    if not target_filename:
        return None
    if os.path.exists(target_filename):
        return target_filename
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidate1 = os.path.join(base_dir, target_filename)
    if os.path.exists(candidate1):
        return candidate1
    gorseller_dir = os.path.join(base_dir, "gorseller")
    if os.path.exists(gorseller_dir):
        target_base = os.path.basename(target_filename).split('.')[0].lower()
        for f in os.listdir(gorseller_dir):
            if f.lower().split('.')[0] == target_base:
                return os.path.join(gorseller_dir, f)
    return None

# FULL 12 CASES EXHAUSTIVE KNOWLEDGE BASE
CASES = {
    "Vaka A (Papatya)": {
        "kod": "VAKA_A",
        "sikayet": "Gerdan ve çene altında soğuk hamur ödem, iştahsızlık, belirgin süt verimi düşüşü, halsizlik ve duruş bozukluğu.",
        "tanı": "Traumatik Retikuloperikarditis (TRP / Çamaşır Makinesi Üfürümü)",
        "categories": {
            "ANAMNEZ_BESLEME": {
                "name": "🌾 Yetiştirici Anamnezi, Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "mısır", "arpa", "ot", "mera", "silaj", "balya", "saman", "tel", "çivi", "yabancı cisim", "inşaat"],
                "content": "4 yaşında Holstein ırkı inek (540 kg). İşletmede kaba/yoğun yem karma rasyonu (TMR) uygulanmaktadır. Balya parçalama esnasında saman balya tellerinin ve inşaat çivilerinin rasyona karışmış olabileceği belirtilmektedir. İnek 2 aydır sağmal olup son 3 gündür yem yemeyi reddetmektedir."
            },
            "LOKASYON_CEVRE": {
                "name": "📍 Lokasyon, Coğrafya & Barınak Şartları",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil", "coğrafya", "yükseklik", "dağ", "ova", "barınak", "zemin", "beton"],
                "content": "Ceyhan Ovası'nda (rakım ~50m) entansif süt tesisinde doğup büyümüştür. Yüksek rakım veya yayla nakli öyküsü yoktur. Barınak zemini betondur, durak altlıkları serttir."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "mastitis", "doğum", "öykü", "aşı", "parazit"],
                "content": "Geçmişinde kronik mastitis veya metritis kaydı yoktur. 2 ay önce sorunsuz doğum yapmıştır. Aşıları ve ektoparazit ilaçlamaları tamdır."
            },
            "ISTAH_SINDIRIM": {
                "name": "🍽️ İştah, Geviş Getirme & Dışkı Karakteri",
                "keywords": ["iştah", "yem tüketimi", "geviş", "anoreksi", "dışkı", "ishal", "kabız", "rumen", "motilite"],
                "content": "İştah tamamen kesilmiştir (Tam Anoreksi). Geviş getirme durmuştur (Atony). Rumen hareketleri 5 dakikada 1 kez, çok zayıf ve hipomotildir. Dışkı miktarı azalmış, koyu renkli ve kurudur."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Fiziksel Muayene & Vital Parametreler",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "ödem", "gerdan", "jugular", "staz", "dolgunluk"],
                "content": "Vücut Sıcaklığı: 39.8 °C (Subfebril/Ateş) | Kalp Frekansı: 104 atım/dk (Taşikardi) | Solunum Sayısı: 44 nefes/dk (Takipne) | Mukoza: Soluk-çivit siyanotik | CRT: 3.2 saniye | Dehidrasyon: %8 | Submandibuler bölge ve gerdanda (brisket) diz kapağına kadar uzanan soğuk, ağrısız hamur ödemi (Brisket Edema) | Vena jugularis stazı ++, belirgin yalancı jugular nabız (+)."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "rall", "akciğer", "perikard"],
                "content": "Kalp Oskültasyonu: Perikard kasesinde sıvı ve gaz birikimine bağlı klasik 'Çamaşır Makinesi' / Su Çalkantı (Splashing/Muffled) sesi duyulmaktadır. Kalp sesleri derinden ve boğuk gelmektedir. Akciğer Oskültasyonu: Ventro-lateral akciğer sahalarında solunum sesleri hafif azalmıştır."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Provokasyon & Ağrı Deneyleri",
                "keywords": ["sopa", "kama", "withers", "cidago", "ağrı", "pinch", "retikulum", "ferroskop", "mıknatıs", "kalp vurumu"],
                "content": "Cidago Sıkıştırma (Withers Pinch) Testi: POZİTİF (Hayvan belini aşağı bükmez, şiddetli inleme ve diş gıcırdatma gösterir). Sopa/Kama Testi: POZİTİF (Retikulum bölgesine kaldırıldığında inler). Ferroskop Muayenesi: Retikulum bölgesinde metalik yabancı cisim tespiti POZİTİF."
            },
            "HEMOGRAM_FULL": {
                "name": "🩸 TAM HEMOGRAM (CBC) ANALİZ PANELİ",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "lökosit", "rbc", "eritrosit", "pcv", "hematokrit", "hb", "hemoglobin", "mcv", "mch", "mchc", "rdw", "trombosit", "plt", "nötrofil", "lenfosit", "monosit", "eozinofil", "bazofil", "fibrinojen", "pp/f"],
                "content": """================ TAM HEMOGRAM (CBC) PANELİ ================
• Eritrosit (RBC): 5.1 x10⁶/µL  (Referans: 5.0 - 10.0)
• Hemoglobin (Hb): 9.2 g/dL  (Referans: 8.0 - 15.0)
• Hematokrit (PCV): %28.5  (Referans: 24 - 46)
• MCV: 55.8 fL  (Referans: 40 - 60)
• MCH: 18.0 pg  (Referans: 11 - 17)
• MCHC: 32.2 g/dL  (Referans: 30 - 36)
• RDW: %16.2  (Referans: 14 - 18)
• Trombosit (PLT): 280 x10³/µL  (Referans: 100 - 800)
• Lökosit (WBC): 22.4 x10³/µL  [ŞİDDETLİ LÖKOSİTOZ] (Referans: 4.0 - 12.0)
  - Çomak Nötrofil (Band): %14  [Sola Kayma / Regenerative Left Shift]
  - Segmenter Nötrofil: %68  [Lökositozis & Nötrofili]
  - Lenfosit: %14  [Lenfopeni]
  - Monosit: %3.5
  - Eozinofil: %0.5
  - Bazofil: %0.0
• Plazma Fibrinojeni: 1250 mg/dL  [AŞIRI YÜKSEK FİBRİNOJEN] (Referans: 200 - 600)
• Plazma Proteini / Fibrinojen Oranı (PP/F): 6.3  [<10 = Şiddetli Aktif Fibrinöz Yangı]
==========================================================="""
            },
            "FULL_BIOCHEMISTRY": {
                "name": "🧪 FULL BİYOKİMYA, ENZİM, MİKRO ELEMAN & ELEKTROLİT PANELİ",
                "keywords": ["biyokimya", "biyokimyasal", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "üre", "kreatinin", "glikoz", "bilirubin", "albümin", "globülin", "total protein", "tp", "glutaraldehit", "saa", "sodyum", "na", "potasyum", "k", "klor", "cl", "kalsiyum", "ca", "fosfor", "p", "magnezyum", "mg", "bakır", "cu", "çinko", "zn", "demir", "fe", "selenyum", "se"],
                "content": """======= FULL BİYOKİMYA, ENZİM, ELEKTROLİT & İZ ELEMAN PANELİ =======
[Organ Enzimleri & Kardiyak Hasar]
• AST (Aspartat Aminotransferaz): 142 U/L  (Referans: 40 - 125)
• GGT (Gamma-Glutamil Transferaz): 38 U/L  (Referans: 15 - 40)
• ALT (Alanin Aminotransferaz): 28 U/L  (Referans: 11 - 40)
• ALP (Alkalen Fosfataz): 82 U/L  (Referans: 0 - 150)
• CK (Kreatin Kinaz): 310 U/L  (Referans: 35 - 280)
• LDH (Laktat Dehidrogenaz): 1450 U/L  (Referans: 600 - 1400)
• Kardiyak Troponin I (cTnI): 2.85 ng/mL  [MİYOKARD HASARI / PERİKARDİT] (Referans: <0.05)

[Böbrek Fonksiyon & Metabolitler]
• BUN (Kan Üre Azotu): 48 mg/dL  [Pre-renal Azotemi] (Referans: 10 - 25)
• Serum Kreatinin: 2.1 mg/dL  (Referans: 0.5 - 1.5)
• Kan Glikozu: 88 mg/dL  (Referans: 45 - 75)
• Total Bilirubin: 1.8 mg/dL  (Referans: 0.1 - 0.5)

[Serum Proteinleri & Akut Faz Reaktanları]
• Total Protein (TP): 9.2 g/dL  (Referans: 6.7 - 7.5)
• Albümin: 2.1 g/dL  [Hipoalbüminemi / Ödem Kaçışı] (Referans: 3.0 - 3.6)
• Globülin: 7.1 g/dL  [Aşırı Hipergamaglobülinemi] (Referans: 3.0 - 4.2)
• Albümin/Globülin (A/G) Oranı: 0.29  (Referans: 0.8 - 0.9)
• Glutaraldehit Pıhtılaşma Testi: 1.5 dakika  [<3 dk = Şiddetli Yangı]
• Serum Amyloid A (SAA): 180 µg/mL  (Referans: <10)

[Serum Elektrolitleri]
• Sodyum (Na⁺): 132 mmol/L  (Referans: 135 - 148)
• Potasyum (K⁺): 3.1 mmol/L  [Hipokalemi - Anoreksiye Bağlı] (Referans: 3.9 - 5.8)
• Klor (Cl⁻): 88 mmol/L  [Hipokloremik Metabolik Alkaloz/Atony] (Referans: 95 - 110)
• Kalsiyum (Ca²⁺): 7.8 mg/dL  (Referans: 8.5 - 10.5)
• İnorganik Fosfor (P): 4.8 mg/dL  (Referans: 4.0 - 7.0)
• Magnezyum (Mg²⁺): 2.1 mg/dL  (Referans: 1.8 - 2.4)

[İz / Mikro Elemanlar]
• Serum Demir (Fe): 42 µg/dL  [Yangısal Sequestration] (Referans: 80 - 180)
• Serum Bakır (Cu): 88 µg/dL  (Referans: 70 - 120)
• Serum Çinko (Zn): 92 µg/dL  (Referans: 80 - 140)
• Serum Selenyum (Se): 70 µg/L  (Referans: 60 - 120)
==================================================================="""
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "oksijen"],
                "content": "Kan pH: 7.48  [Metabolik Alkaloz] | pO₂: 54 mmHg  [Hipoksi] | pCO₂: 46 mmHg | HCO₃⁻: 34.2 mmol/L  [Yüksek Bikarbonat] | Baz Açığı (BE): +8.5 mmol/L | Kan Laktatı: 3.8 mmol/L  [Doku Hipoperfüzyonu]."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "idrar tahlili", "dansite", "spesifik gravite", "proteinüri", "glikozüri", "sediment", "üronil"],
                "content": "İdrar Dansitesi: 1.028 | İdrar pH: 8.5 | Proteinüri: Trace (+1) | Glikoz: Negatif | Keton: Negatif | Bilirubin: Negatif | İdrar Sedimantasyonu: Hiyalin silindirler, nadir epitel hücresi, lökosit <2/HPF."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Ultrasonografi, Perikardiyosentez & Kültür",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "röntgen", "radiografi", "perikardiyosentez", "kültür", "bakteri", "sıvı", "ponksiyon"],
                "content": "Ekokardiyografi/USG: Perikard yaprakları arasında 6.5 cm genişliğinde fibrin bantları içeren hiperekojenik pürülan sıvı birikimi. Perikardiyosentez: Kokulu, bulanık, pürülan vasıfta perikard sıvısı. Perikard Sıvısı Kültürü: Trueperella pyogenes ve Escherichia coli izolasyonu."
            }
        }
    },
    "Vaka B (Yonca)": {
        "kod": "VAKA_B",
        "sikayet": "Dirençli yüksek ateş (40.8 °C), iştahsızlık, belirgin kilo kaybı, halsizlik ve sistolik kalp üfürümü.",
        "tanı": "Vejetatif Valvüler Endokarditis (Arcanobacterium / Trueperella pyogenes)",
        "categories": {
            "ANAMNEZ_BESLEME": {
                "name": "🌾 Yetiştirici Anamnezi, Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "mısır", "arpa", "ot", "mera", "silaj", "balya", "saman", "tel", "çivi"],
                "content": "3 yaşında Alaca sığır (480 kg). Standart mer'a ve karma rasyonla beslenmektedir. Rasyonda yabancı cisim öyküsü bulunmamaktadır. Son 2 haftadır giderek artan halsizlik ve iştahsızlık şikayeti vardır."
            },
            "LOKASYON_CEVRE": {
                "name": "📍 Lokasyon, Coğrafya & Barınak Şartları",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil", "coğrafya", "yükseklik"],
                "content": "Çukurova bölgesinde açık sistem yarı entansif çiftlikte barınmaktadır. Rakım değişikliği veya nakil yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "ayak", "tırnak", "apse"],
                "content": "Yaklaşık 1 ay önce şiddetli septik pododermatit (ökçe apsesi / tırnak çürüğü) ve akut puerperal metritis tedavisi görmüştür. Bakteriyemi odağı bu enfeksiyonlardır."
            },
            "ISTAH_SINDIRIM": {
                "name": "🍽️ İştah, Geviş Getirme & Dışkı Karakteri",
                "keywords": ["iştah", "yem tüketimi", "geviş", "anoreksi", "dışkı"],
                "content": "İştah %70 oranında azalmıştır (Hiporeksi). Dışkı cıvık ve az miktardadır."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Fiziksel Muayene & Vital Parametreler",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "ödem", "remittent"],
                "content": "Vücut Sıcaklığı: 40.8 °C (Sürekli İnişli Çıkışlı Remittent Ateş) | Kalp Frekansı: 118 atım/dk (Şiddetli Taşikardi) | Solunum Sayısı: 38 nefes/dk | Mukoza: İkterik ve peteşiyel kanamalı | CRT: 2.8 saniye | Dehidrasyon: %6 | Bacaklarda ve eklemlerde gezgin ağrılı şişlikler (Septik Emboli)."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "sistolik", "triküspit", "akciğer"],
                "content": "Kalp Oskültasyonu: Triküspit kapak odakında (sağ 4. interkostal aralık) Grade 4/6 şiddetinde holosistolik sert üfürüm duyulmaktadır. Akciğer Oskültasyonu: Her iki tarafta veziküler solunum sesleri sertleşmiştir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Provokasyon & Ağrı Deneyleri",
                "keywords": ["sopa", "kama", "withers", "cidago", "ağrı", "pinch", "retikulum", "ferroskop"],
                "content": "Cidago Sıkıştırma (Withers Pinch) ve Sopa Testi: NEGATİF. Ferroskop Muayenesi: NEGATİF."
            },
            "HEMOGRAM_FULL": {
                "name": "🩸 TAM HEMOGRAM (CBC) ANALİZ PANELİ",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "lökosit", "rbc", "eritrosit", "pcv", "hematokrit", "hb", "hemoglobin", "mcv", "mch", "mchc", "rdw", "trombosit", "plt", "nötrofil", "lenfosit", "monosit", "eozinofil", "bazofil", "fibrinojen", "pp/f"],
                "content": """================ TAM HEMOGRAM (CBC) PANELİ ================
• Eritrosit (RBC): 4.2 x10⁶/µL  [Normositik Normokromik Anemi] (Referans: 5.0 - 10.0)
• Hemoglobin (Hb): 7.1 g/dL  (Referans: 8.0 - 15.0)
• Hematokrit (PCV): %22.0  (Referans: 24 - 46)
• MCV: 52.3 fL  (Referans: 40 - 60)
• MCH: 16.9 pg  (Referans: 11 - 17)
• MCHC: 32.2 g/dL  (Referans: 30 - 36)
• RDW: %17.1  (Referans: 14 - 18)
• Trombosit (PLT): 85 x10³/µL  [TROMBOSİTOPENİ] (Referans: 100 - 800)
• Lökosit (WBC): 31.8 x10³/µL  [AŞIRI LÖKOSİTOZ] (Referans: 4.0 - 12.0)
  - Çomak Nötrofil (Band): %18  [Sola Kayma / Regenerative Left Shift]
  - Segmenter Nötrofil: %65  [Nötrofili]
  - Lenfosit: %12  [Lenfopeni]
  - Monosit: %4.0
  - Eozinofil: %1.0
  - Bazofil: %0.0
• Plazma Fibrinojeni: 1100 mg/dL  [AŞIRI YÜKSEK] (Referans: 200 - 600)
• Plazma Proteini / Fibrinojen Oranı (PP/F): 7.8  [<10 = Şiddetli Kronik Enfeksiyon]
==========================================================="""
            },
            "FULL_BIOCHEMISTRY": {
                "name": "🧪 FULL BİYOKİMYA, ENZİM, MİKRO ELEMAN & ELEKTROLİT PANELİ",
                "keywords": ["biyokimya", "biyokimyasal", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "üre", "kreatinin", "glikoz", "bilirubin", "albümin", "globülin", "total protein", "tp", "glutaraldehit", "saa", "sodyum", "na", "potasyum", "k", "klor", "cl", "kalsiyum", "ca", "fosfor", "p", "magnezyum", "mg", "bakır", "cu", "çinko", "zn", "demir", "fe", "selenyum", "se"],
                "content": """======= FULL BİYOKİMYA, ENZİM, ELEKTROLİT & İZ ELEMAN PANELİ =======
[Organ Enzimleri & Kardiyak Hasar]
• AST (Aspartat Aminotransferaz): 185 U/L  (Referans: 40 - 125)
• GGT (Gamma-Glutamil Transferaz): 52 U/L  (Referans: 15 - 40)
• ALT (Alanin Aminotransferaz): 32 U/L  (Referans: 11 - 40)
• ALP (Alkalen Fosfataz): 110 U/L  (Referans: 0 - 150)
• CK (Kreatin Kinaz): 420 U/L  (Referans: 35 - 280)
• LDH (Laktat Dehidrogenaz): 1680 U/L  (Referans: 600 - 1400)
• Kardiyak Troponin I (cTnI): 4.10 ng/mL  [AŞIRI MİYOKARD/VALVÜLER HASAR] (Referans: <0.05)

[Böbrek Fonksiyon & Metabolitler]
• BUN (Kan Üre Azotu): 54 mg/dL  [Septik Embolik Glomerulonefrit] (Referans: 10 - 25)
• Serum Kreatinin: 2.6 mg/dL  (Referans: 0.5 - 1.5)
• Kan Glikozu: 62 mg/dL  (Referans: 45 - 75)
• Total Bilirubin: 2.4 mg/dL  [İkterik] (Referans: 0.1 - 0.5)

[Serum Proteinleri & Akut Faz Reaktanları]
• Total Protein (TP): 8.6 g/dL  (Referans: 6.7 - 7.5)
• Albümin: 2.3 g/dL  [Hipoalbüminemi] (Referans: 3.0 - 3.6)
• Globülin: 6.3 g/dL  [Hipergamaglobülinemi] (Referans: 3.0 - 4.2)
• Albümin/Globülin (A/G) Oranı: 0.36  (Referans: 0.8 - 0.9)
• Glutaraldehit Pıhtılaşma Testi: 1.0 dakika  [Şiddetli Yangı]
• Serum Amyloid A (SAA): 240 µg/mL  (Referans: <10)

[Serum Elektrolitleri]
• Sodyum (Na⁺): 134 mmol/L  (Referans: 135 - 148)
• Potasyum (K⁺): 3.4 mmol/L  (Referans: 3.9 - 5.8)
• Klor (Cl⁻): 96 mmol/L  (Referans: 95 - 110)
• Kalsiyum (Ca²⁺): 7.9 mg/dL  (Referans: 8.5 - 10.5)
• İnorganik Fosfor (P): 4.2 mg/dL  (Referans: 4.0 - 7.0)
• Magnezyum (Mg²⁺): 2.0 mg/dL  (Referans: 1.8 - 2.4)

[İz / Mikro Elemanlar]
• Serum Demir (Fe): 35 µg/dL  [Ağır Enfeksiyon Anemisi] (Referans: 80 - 180)
• Serum Bakır (Cu): 95 µg/dL  (Referans: 70 - 120)
• Serum Çinko (Zn): 75 µg/dL  (Referans: 80 - 140)
• Serum Selenyum (Se): 82 µg/L  (Referans: 60 - 120)
==================================================================="""
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.31  [Hafif Metabolik Asidoz] | pO₂: 48 mmHg | pCO₂: 38 mmHg | HCO₃⁻: 18.2 mmol/L | Baz Açığı (BE): -5.8 mmol/L | Kan Laktatı: 4.2 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "idrar tahlili", "dansite", "proteinüri", "sediment", "hematüri"],
                "content": "İdrar Dansitesi: 1.022 | İdrar pH: 7.0 | Proteinüri: +3 (Şiddetli Proteinüri) | Mikrohematüri: +2 | İdrar Sedimantasyonu: Eritrosit silindirleri, lökositler (Septik Nefritis)."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Ekokardiyografi & Kan Kültürü",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "kan kültürü", "triküspit", "vejetasyon"],
                "content": "Ekokardiyografi: Triküspit kapak üzerinde 3.8 cm çapında 'Karnabahar' görünümünde hareketli hiperekojenik vejetasyon (kitle) tespiti. Seri Kan Kültürleri: Trueperella pyogenes (3 ayrı kan kültüründe pozitif üreme)."
            }
        }
    },
    "Vaka C (Zümrüt)": {
        "kod": "VAKA_C",
        "sikayet": "Yüksek rakımlı yaylaya nakil sonrası gerdan ödemi, şiddetli nefes darlığı, siyanoz ve çabuk yorulma.",
        "tanı": "Yüksek Yayla Hastalığı / Cor Pulmonale (Bovine High Altitude Disease)",
        "categories": {
            "ANAMNEZ_BESLEME": {
                "name": "🌾 Yetiştirici Anamnezi, Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "mısır", "ot", "mera"],
                "content": "2.5 yaşında Simental ırkı düve (510 kg). Mer'a otlamaktadır. Rasyonda yabancı cisim veya toksin öyküsü yoktur."
            },
            "LOKASYON_CEVRE": {
                "name": "📍 Lokasyon, Coğrafya & Barınak Şartları",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil", "coğrafya", "yükseklik", "dağ", "pozantı", "2400"],
                "content": "Hayvan 10 gün önce Ceyhan ovasından Pozantı / Toros yaylasına (rakım: 2400 metre) nakledilmiştir. Yüksek rakımda hipobarik hipoksiye maruz kalmıştır."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Geçmişinde kaydedilmiş enfeksiyöz veya metabolik bir hastalık öyküsü bulunmamaktadır."
            },
            "ISTAH_SINDIRIM": {
                "name": "🍽️ İştah, Geviş Getirme & Dışkı Karakteri",
                "keywords": ["iştah", "yem tüketimi", "geviş", "dışkı"],
                "content": "İştah azalmıştır (%50). Dışkılama normaldir."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Fiziksel Muayene & Vital Parametreler",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "ödem", "gerdan", "jugular", "siyanoz"],
                "content": "Vücut Sıcaklığı: 38.6 °C (TAMAMEN NORMAL / ATEŞ YOK) | Kalp Frekansı: 98 atım/dk | Solunum Sayısı: 48 nefes/dk | Mukoza: Şiddetli Siyanotik (Mavi-Mor) | CRT: 3.5 saniye | Dehidrasyon: %0 | Gerdanda geniş alana yayılmış soğuk hamur ödem | Vena jugularis dolgun ve belirgin yalancı nabız."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "pulmoner", "akciğer"],
                "content": "Kalp Oskültasyonu: Sağ ventrikül vurumu şiddetlenmiştir (Hiperdinamik). Su çalkantı sesi veya üfürüm YOKTUR. Pulmoner kapak odağında 2. kalp sesi (S2) belirgin olarak şiddetlenmiştir (Acentuated S2). Akciğer Oskültasyonu: Veziküler sesler hafif sertleşmiştir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Provokasyon & Ağrı Deneyleri",
                "keywords": ["sopa", "kama", "withers", "cidago", "ağrı", "pinch", "retikulum", "ferroskop"],
                "content": "Retikulum Ağrı Testlerinin tamamı ve Ferroskop Muayenesi: NEGATİF."
            },
            "HEMOGRAM_FULL": {
                "name": "🩸 TAM HEMOGRAM (CBC) ANALİZ PANELİ",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "lökosit", "rbc", "eritrosit", "pcv", "hematokrit", "hb", "hemoglobin", "mcv", "mch", "mchc", "rdw", "trombosit", "plt", "nötrofil", "lenfosit", "monosit", "eozinofil", "bazofil", "fibrinojen", "pp/f"],
                "content": """================ TAM HEMOGRAM (CBC) PANELİ ================
• Eritrosit (RBC): 10.8 x10⁶/µL  [KOMPENZATUVAR POLİSİTEMİ] (Referans: 5.0 - 10.0)
• Hemoglobin (Hb): 17.2 g/dL  [AŞIRI YÜKSEK] (Referans: 8.0 - 15.0)
• Hematokrit (PCV): %54.0  [HİPERVİSKOZİTE / POLİSİTEMİ] (Referans: 24 - 46)
• MCV: 50.0 fL  (Referans: 40 - 60)
• MCH: 15.9 pg  (Referans: 11 - 17)
• MCHC: 31.8 g/dL  (Referans: 30 - 36)
• RDW: %15.0  (Referans: 14 - 18)
• Trombosit (PLT): 320 x10³/µL  (Referans: 100 - 800)
• Lökosit (WBC): 7.2 x10³/µL  [TAMAMEN NORMAL / YANGI YOK] (Referans: 4.0 - 12.0)
  - Çomak Nötrofil (Band): %1
  - Segmenter Nötrofil: %52
  - Lenfosit: %42
  - Monosit: %3.0
  - Eozinofil: %2.0
  - Bazofil: %0.0
• Plazma Fibrinojeni: 320 mg/dL  [NORMAL] (Referans: 200 - 600)
• Plazma Proteini / Fibrinojen Oranı (PP/F): 22.8  [Normal]
==========================================================="""
            },
            "FULL_BIOCHEMISTRY": {
                "name": "🧪 FULL BİYOKİMYA, ENZİM, MİKRO ELEMAN & ELEKTROLİT PANELİ",
                "keywords": ["biyokimya", "biyokimyasal", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "üre", "kreatinin", "glikoz", "bilirubin", "albümin", "globülin", "total protein", "tp", "glutaraldehit", "saa", "sodyum", "na", "potasyum", "k", "klor", "cl", "kalsiyum", "ca", "fosfor", "p", "magnezyum", "mg", "bakır", "cu", "çinko", "zn", "demir", "fe", "selenyum", "se"],
                "content": """======= FULL BİYOKİMYA, ENZİM, ELEKTROLİT & İZ ELEMAN PANELİ =======
[Organ Enzimleri & Kardiyak Hasar]
• AST: 68 U/L  (Referans: 40 - 125)
• GGT: 18 U/L  (Referans: 15 - 40)
• ALT: 22 U/L  (Referans: 11 - 40)
• ALP: 75 U/L  (Referans: 0 - 150)
• CK: 180 U/L  (Referans: 35 - 280)
• LDH: 820 U/L  (Referans: 600 - 1400)
• Kardiyak Troponin I (cTnI): 0.12 ng/mL  (Referans: <0.05)

[Böbrek Fonksiyon & Metabolitler]
• BUN: 18 mg/dL  (Referans: 10 - 25)
• Serum Kreatinin: 0.9 mg/dL  (Referans: 0.5 - 1.5)
• Kan Glikozu: 72 mg/dL  (Referans: 45 - 75)
• Total Bilirubin: 0.4 mg/dL  (Referans: 0.1 - 0.5)

[Serum Proteinleri & Akut Faz Reaktanları]
• Total Protein (TP): 7.3 g/dL  (Referans: 6.7 - 7.5)
• Albümin: 3.2 g/dL  (Referans: 3.0 - 3.6)
• Globülin: 4.1 g/dL  (Referans: 3.0 - 4.2)
• Albümin/Globülin (A/G) Oranı: 0.78  (Referans: 0.8 - 0.9)
• Glutaraldehit Pıhtılaşma Testi: >15 dakika  [Normal / Yangı Yok]
• Serum Amyloid A (SAA): 4.2 µg/mL  (Referans: <10)

[Serum Elektrolitleri]
• Sodyum (Na⁺): 140 mmol/L  (Referans: 135 - 148)
• Potasyum (K⁺): 4.2 mmol/L  (Referans: 3.9 - 5.8)
• Klor (Cl⁻): 102 mmol/L  (Referans: 95 - 110)
• Kalsiyum (Ca²⁺): 9.2 mg/dL  (Referans: 8.5 - 10.5)
• İnorganik Fosfor (P): 5.1 mg/dL  (Referans: 4.0 - 7.0)
• Magnezyum (Mg²⁺): 2.1 mg/dL  (Referans: 1.8 - 2.4)

[İz / Mikro Elemanlar]
• Serum Demir (Fe): 110 µg/dL  (Referans: 80 - 180)
• Serum Bakır (Cu): 90 µg/dL  (Referans: 70 - 120)
• Serum Çinko (Zn): 105 µg/dL  (Referans: 80 - 140)
• Serum Selenyum (Se): 88 µg/L  (Referans: 60 - 120)
==================================================================="""
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "oksijen", "hipoksi"],
                "content": "Kan pH: 7.36 | pO₂: 42 mmHg  [AĞIR ARTERİYEL HİPOKSİ] | pCO₂: 48 mmHg | HCO₃⁻: 23.5 mmol/L | Baz Açığı: -0.8 mmol/L | Kan Laktatı: 1.8 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "idrar tahlili", "dansite", "proteinüri"],
                "content": "İdrar Dansitesi: 1.025 | İdrar pH: 8.0 | Proteinüri: Negatif | İdrar Sedimantasyonu: Temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Ekokardiyografi, USG & Ölçümler",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "sağ ventrikül", "pulmoner arter", "pap", "kültür"],
                "content": "Ekokardiyografi / USG: Sağ ventrikül serbest duvar kalınlığında aşırı artış (Sağ Ventrikül Dilatasyon ve Hipertrofisi). Pulmoner Arter Basıncı (PAP): 68 mmHg (Pulmoner Hipertansiyon >45 mmHg). Perikard Sıvısı ve Kan Kültürü: STERİL (Bakteri üremesi YOK)."
            }
        }
    },
    "Vaka D (Yiğit)": {
        "kod": "VAKA_D",
        "sikayet": "Ağız ve burun deliklerinden fışkırır tarzda köpüklü taze kan gelmesi (hemoptizi) ve katran gibi siyah dışkı yapma (melena).",
        "tanı": "Kaudal Vena Kava Trombozu Sendromu (CVCT / Pulmoner Anevrizma Ruptürü)",
        "categories": {
            "ANAMNEZ_BESLEME": {
                "name": "🌾 Yetiştirici Anamnezi, Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "mısır", "arpa", "asidoz", "yem çarpması", "nişasta"],
                "content": "18 aylık besi danası (580 kg). Yoğun arpa kırması ve mısır ağırlıklı, kaba yemi yetersiz yüksek nişastalı besi rasyonu verilmektedir."
            },
            "LOKASYON_CEVRE": {
                "name": "📍 Lokasyon, Coğrafya & Barınak Şartları",
                "keywords": ["rakım", "yayla", "nereden", "yer", "besi"],
                "content": "Besi padoğunda barındırılmaktadır. Rakım değişikliği yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "asidoz", "rumenitis", "karaciğer", "apse"],
                "content": "Geçmişinde tekrarlayan subakut rumen asidozu (SARA / Yem Çarpması) ve rumenitis öyküsü mevcuttur."
            },
            "ISTAH_SINDIRIM": {
                "name": "🍽️ İştah, Geviş Getirme & Dışkı Karakteri",
                "keywords": ["iştah", "dışkı", "melena", "siyah", "katran"],
                "content": "İştah tamamen kesilmiştir. Dışkı katran gibi siyah, yapışkan ve kokuludur (Melena / Yutulan Kan)."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Fiziksel Muayene & Vital Parametreler",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "kan", "hemoptizi", "ağız", "burun"],
                "content": "Vücut Sıcaklığı: 39.2 °C | Kalp Frekansı: 124 atım/dk (Şiddetli Taşikardi) | Solunum Sayısı: 56 nefes/dk (Polipne) | Ağız/Burun: Fışkırır tarzda köpüklü taze kan fışkırması (Hemoptizi) | Mukoza: Bembeyaz (Ağır Anemi) | CRT: 4.0 saniye."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "rall", "akciğer", "hışırtı"],
                "content": "Kalp Oskültasyonu: Taşikardik, zayıf düştü sesleri. Akciğer Oskültasyonu: Her iki akciğer sahasında yaygın kaba nemli raller ve hışırtı sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Provokasyon & Ağrı Deneyleri",
                "keywords": ["sopa", "kama", "withers", "cidago", "ağrı", "pinch"],
                "content": "Retikulum ağrı testleri NEGATİF."
            },
            "HEMOGRAM_FULL": {
                "name": "🩸 TAM HEMOGRAM (CBC) ANALİZ PANELİ",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "lökosit", "rbc", "eritrosit", "pcv", "hematokrit", "hb", "hemoglobin", "mcv", "mch", "mchc", "rdw", "trombosit", "plt", "nötrofil", "lenfosit", "monosit", "eozinofil", "bazofil", "fibrinojen", "pp/f"],
                "content": """================ TAM HEMOGRAM (CBC) PANELİ ================
• Eritrosit (RBC): 2.1 x10⁶/µL  [AĞIR AKUT KAN KAYBI ANEMİSİ] (Referans: 5.0 - 10.0)
• Hemoglobin (Hb): 4.2 g/dL  (Referans: 8.0 - 15.0)
• Hematokrit (PCV): %12.0  [KRİTİK ACİL TRANSFÜZYON EŞİĞİ] (Referans: 24 - 46)
• MCV: 57.1 fL  (Referans: 40 - 60)
• MCH: 20.0 pg  (Referans: 11 - 17)
• MCHC: 35.0 g/dL  (Referans: 30 - 36)
• RDW: %18.8  (Referans: 14 - 18)
• Trombosit (PLT): 110 x10³/µL  (Referans: 100 - 800)
• Lökosit (WBC): 21.5 x10³/µL  [LÖKOSİTOZ] (Referans: 4.0 - 12.0)
  - Çomak Nötrofil (Band): %12
  - Segmenter Nötrofil: %70
  - Lenfosit: %15
  - Monosit: %3.0
  - Eozinofil: %0.0
• Plazma Fibrinojeni: 1050 mg/dL  [AŞIRI YÜKSEK] (Referans: 200 - 600)
• Plazma Proteini / Fibrinojen Oranı (PP/F): 7.2  [<10 = Şiddetli Fibrinöz Yangı]
==========================================================="""
            },
            "FULL_BIOCHEMISTRY": {
                "name": "🧪 FULL BİYOKİMYA, ENZİM, MİKRO ELEMAN & ELEKTROLİT PANELİ",
                "keywords": ["biyokimya", "biyokimyasal", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "üre", "kreatinin", "glikoz", "bilirubin", "albümin", "globülin", "total protein", "tp", "glutaraldehit", "saa", "sodyum", "na", "potasyum", "k", "klor", "cl", "kalsiyum", "ca", "fosfor", "p", "magnezyum", "mg", "bakır", "cu", "çinko", "zn", "demir", "fe", "selenyum", "se"],
                "content": """======= FULL BİYOKİMYA, ENZİM, ELEKTROLİT & İZ ELEMAN PANELİ =======
[Organ Enzimleri & Karaciğer Hasarı]
• AST: 210 U/L  [Karaciğer Parankim Hasarı] (Referans: 40 - 125)
• GGT: 68 U/L  [Safra Yolu / Karaciğer Apse Çevresi] (Referans: 15 - 40)
• ALT: 35 U/L  (Referans: 11 - 40)
• ALP: 130 U/L  (Referans: 0 - 150)
• CK: 240 U/L  (Referans: 35 - 280)
• LDH: 1520 U/L  (Referans: 600 - 1400)
• Kardiyak Troponin I (cTnI): 0.08 ng/mL  (Referans: <0.05)

[Böbrek Fonksiyon & Metabolitler]
• BUN: 42 mg/dL  (Referans: 10 - 25)
• Serum Kreatinin: 1.6 mg/dL  (Referans: 0.5 - 1.5)
• Kan Glikozu: 88 mg/dL  (Referans: 45 - 75)
• Total Bilirubin: 1.2 mg/dL  (Referans: 0.1 - 0.5)

[Serum Proteinleri & Akut Faz Reaktanları]
• Total Protein (TP): 7.6 g/dL  (Referans: 6.7 - 7.5)
• Albümin: 2.4 g/dL  [Kayıp Anemisine Bağlı Hipoalbüminemi] (Referans: 3.0 - 3.6)
• Globülin: 5.2 g/dL  (Referans: 3.0 - 4.2)
• Albümin/Globülin (A/G) Oranı: 0.46  (Referans: 0.8 - 0.9)
• Glutaraldehit Pıhtılaşma Testi: 1.8 dakika  [Ağır Yangı]
• Serum Amyloid A (SAA): 160 µg/mL  (Referans: <10)

[Serum Elektrolitleri]
• Sodyum (Na⁺): 136 mmol/L  (Referans: 135 - 148)
• Potasyum (K⁺): 3.6 mmol/L  (Referans: 3.9 - 5.8)
• Klor (Cl⁻): 98 mmol/L  (Referans: 95 - 110)
• Kalsiyum (Ca²⁺): 8.0 mg/dL  (Referans: 8.5 - 10.5)
• İnorganik Fosfor (P): 4.5 mg/dL  (Referans: 4.0 - 7.0)
• Magnezyum (Mg²⁺): 2.0 mg/dL  (Referans: 1.8 - 2.4)

[İz / Mikro Elemanlar]
• Serum Demir (Fe): 28 µg/dL  [Ağır Kan Kaybı Hipoferremisi] (Referans: 80 - 180)
• Serum Bakır (Cu): 85 µg/dL  (Referans: 70 - 120)
• Serum Çinko (Zn): 80 µg/dL  (Referans: 80 - 140)
• Serum Selenyum (Se): 75 µg/L  (Referans: 60 - 120)
==================================================================="""
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "laktat"],
                "content": "Kan pH: 7.24  [Metabolik Asidoz] | pO₂: 52 mmHg | pCO₂: 50 mmHg | HCO₃⁻: 18.5 mmol/L | Baz Açığı: -6.2 mmol/L | Kan Laktatı: 4.2 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "idrar tahlili"],
                "content": "İdrar Dansitesi: 1.020 | İdrar pH: 7.5 | Proteinüri: Trace | İdrar Sedimantasyonu: Temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Ultrasonografi, Karaciğer Apse & Vena Cava Trombüs",
                "keywords": ["ultrason", "usg", "karaciğer", "apse", "vena cava", "trombüs", "pulmoner", "anevrizma"],
                "content": "Abdominal Ultrasonografi: Karaciğer parankiminde 6.5 cm çapında kılıflı apse odağı (Hepatic Abscess), Vena Cava Caudalis lümeninde tıkayıcı hiperekojenik trombüs kütlesi. Torakal USG/Röntgen: Pulmoner arter çevresinde hematom ve anevrizma odağı."
            }
        }
    },
    "Vaka E (Kudret)": {
        "kod": "VAKA_E",
        "sikayet": "Baş, göz çevresi, kulak ve boyun bölgesinde dairesel, grimsi-beyaz kireç benzeri kabarık kabuklanmalar, kaşıntı ve tüy dökülmesi.",
        "tanı": "Trikofiti / Dermatofitoz (Trichophyton verrucosum)",
        "makroskopik_gorsel": {
            "fig": "Figure 1.2-1",
            "title": "Klinik Mantar Lezyonu (Baş ve Göz Çevresi)",
            "file": "gorseller/figure_1_2_1.jpg",
            "desc": "Baş, göz çevresi ve yüzde dairesel, grimsi-beyaz kireç benzeri kabarık kabuklanma ve alopezi."
        },
        "categories": {
            "ANAMNEZ_BESLEME": {
                "name": "🌾 Yetiştirici Anamnezi, Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "rutubet", "karanlık", "ışık", "a vitamini"],
                "content": "8 aylık dana (220 kg). Kapalı, nemli, yetersiz havalandırmalı ve güneş görmeyen ahırda barındırılmaktadır. A ve E vitamini yönünden yetersiz beslenme öyküsü vardır."
            },
            "LOKASYON_CEVRE": {
                "name": "📍 Lokasyon, Coğrafya & Barınak Şartları",
                "keywords": ["rakım", "yayla", "barınak", "rutubet", "kalabalık"],
                "content": "Sıkışık ve kalabalık genç hayvan padoğu. Ahşap çitlere sürtünme öyküsü mevcuttur."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık"],
                "content": "Geçmişinde pnömoni tedavisi görmüştür."
            },
            "ISTAH_SINDIRIM": {
                "name": "🍽️ İştah, Geviş Getirme & Dışkı Karakteri",
                "keywords": ["iştah", "dışkı"],
                "content": "İştah ve geviş getirme normaldir."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Fiziksel Muayene & Vital Parametreler",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "deri", "kabuk", "alopezi"],
                "content": "Vücut Sıcaklığı: 38.8 °C (Normal) | Kalp Frekansı: 78 atım/dk | Solunum Sayısı: 24 nefes/dk | Mukozalar: Pembe | Deri: Baş, göz çevresi, kulak tabanı ve boyunda dairesel 2-5 cm çaplı, gri-beyaz kireçimsi kabuklarla kaplı tüysüz lezyonlar."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme"],
                "content": "Kalp ve akciğer oskültasyonu tamamen normaldir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum & Deri Hassasiyet Deneyleri",
                "keywords": ["sopa", "kama", "withers", "kaşıntı", "wood"],
                "content": "Kaşıntı (Pruritus) hafiftir. Wood Lambası Muayenesi: T. verrucosum genellikle floresan vermez (Negatif)."
            },
            "HEMOGRAM_FULL": {
                "name": "🩸 TAM HEMOGRAM (CBC) ANALİZ PANELİ",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "lökosit", "rbc", "eritrosit", "pcv", "hematokrit", "hb", "hemoglobin", "eozinofil", "fibrinojen"],
                "content": """================ TAM HEMOGRAM (CBC) PANELİ ================
• Eritrosit (RBC): 6.8 x10⁶/µL  (Referans: 5.0 - 10.0)
• Hemoglobin (Hb): 11.2 g/dL  (Referans: 8.0 - 15.0)
• Hematokrit (PCV): %34.0  (Referans: 24 - 46)
• MCV: 50.0 fL  (Referans: 40 - 60)
• MCH: 16.5 pg  (Referans: 11 - 17)
• MCHC: 32.9 g/dL  (Referans: 30 - 36)
• RDW: %15.2  (Referans: 14 - 18)
• Trombosit (PLT): 340 x10³/µL  (Referans: 100 - 800)
• Lökosit (WBC): 8.4 x10³/µL  [NORMAL] (Referans: 4.0 - 12.0)
  - Çomak Nötrofil (Band): %1
  - Segmenter Nötrofil: %48
  - Lenfosit: %45
  - Monosit: %3.0
  - Eozinofil: %3.0  (Referans: 0 - 24)
  - Bazofil: %0.0
• Plazma Fibrinojeni: 280 mg/dL  (Referans: 200 - 600)
• Plazma Proteini / Fibrinojen Oranı (PP/F): 25.0  [Normal]
==========================================================="""
            },
            "FULL_BIOCHEMISTRY": {
                "name": "🧪 FULL BİYOKİMYA, ENZİM, MİKRO ELEMAN & ELEKTROLİT PANELİ",
                "keywords": ["biyokimya", "biyokimyasal", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "üre", "kreatinin", "glikoz", "bilirubin", "albümin", "globülin", "total protein", "tp", "sodyum", "na", "potasyum", "k", "klor", "cl", "kalsiyum", "ca", "fosfor", "p", "magnezyum", "mg", "bakır", "cu", "çinko", "zn", "demir", "fe", "selenyum", "se", "a vitamini"],
                "content": """======= FULL BİYOKİMYA, ENZİM, ELEKTROLİT & İZ ELEMAN PANELİ =======
[Organ Enzimleri & Metabolitler]
• AST: 72 U/L  |  GGT: 22 U/L  |  ALT: 18 U/L  |  ALP: 95 U/L
• BUN: 14 mg/dL  |  Serum Kreatinin: 0.8 mg/dL  |  Glikoz: 68 mg/dL

[Serum Proteinleri]
• Total Protein (TP): 7.0 g/dL  |  Albümin: 3.3 g/dL  |  Globülin: 3.7 g/dL

[Serum Elektrolitleri]
• Na⁺: 141 mmol/L  |  K⁺: 4.5 mmol/L  |  Cl⁻: 101 mmol/L  |  Ca²⁺: 9.4 mg/dL  |  P: 5.8 mg/dL

[İz Elemanlar & Vitamin Düzeyi]
• Serum A Vitamini: 18 µg/dL  [DÜŞÜK / EPİTEL ZAYIFLIĞI] (Referans: 25 - 60)
• Serum Çinko (Zn): 68 µg/dL  [Düşük / Deri Bütünlüğü] (Referans: 80 - 140)
• Serum Bakır (Cu): 88 µg/dL  |  Serum Selenyum (Se): 80 µg/L
==================================================================="""
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2"],
                "content": "Kan pH: 7.39 | pO₂: 58 mmHg | pCO₂: 40 mmHg | HCO₃⁻: 24.0 mmol/L (Normal)."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "idrar tahlili"],
                "content": "İdrar Dansitesi: 1.022 | İdrar pH: 8.0 | Tüm parametreler normal."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "🔬 Deri Kazıntısı & Mikroskopik Mantar Teşhisi",
                "keywords": ["mikroskop", "kazıntı", "deri kazıntısı", "koh", "mantar", "artrospor", "lam", "trichophyton"],
                "gorsel": {
                    "fig": "Figure 1.2-11",
                    "title": "Mikroskopik Mantar Sporu (%10 KOH Hazırlığı)",
                    "file": "gorseller/figure_1_2_11.jpg",
                    "desc": "%10 KOH ile muamele edilmiş deri kazıntısında kıl şaftını saran küresel Trichophyton verrucosum ektotriks artrospor dizilimi (40x)."
                },
                "content": "%10 KOH hazırlığı altında kıl etrafında ektotriks artrospor zincirleri (Trichophyton verrucosum) kesin olarak teşhis edilmiştir."
            }
        }
    },
    "Vaka F (Nazar)": {
        "kod": "VAKA_F",
        "sikayet": "Kulak kepçesi, boyun, sırt ve boynuz tabanında şiddetli kaşıntı, deride fil derisi gibi kalınlaşma (likenifikasyon), kıvrımlaşma ve kanamalı döküntüler.",
        "tanı": "Sarkoptik Uyuz (Sarcoptic Mange / Sarcoptes scabiei var. bovis)",
        "makroskopik_gorsel": {
            "fig": "Figure 1.3-13",
            "title": "Klinik Uyuz Lezyonu (Likenifikasyon ve Kaşıntı)",
            "file": "gorseller/figure_1_3_13.jpg",
            "desc": "Kulak kepçesi, boyun ve sırtta derinin fil derisi gibi kalınlaşması, kaşıntı eksforyasyonları ve kepeklenme."
        },
        "categories": {
            "ANAMNEZ_BESLEME": {
                "name": "🌾 Yetiştirici Anamnezi, Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "kaşıntı", "sürtünme", "sürü"],
                "content": "2 yaşında inek (430 kg). Sürüye yeni katılan hayvanlarda da benzer kaşıntı ve deri kalınlaşması başladığı bildirilmektedir."
            },
            "LOKASYON_CEVRE": {
                "name": "📍 Lokasyon, Coğrafya & Barınak Şartları",
                "keywords": ["barınak", "çit", "sürtünme"],
                "content": "Sürekli ahır içi ahşap direklere ve yemlik kenarlarına hırsla sürtünmektedir."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden"],
                "content": "Öz geçmişinde başka bir kronik hastalık yoktur."
            },
            "ISTAH_SINDIRIM": {
                "name": "🍽️ İştah, Geviş Getirme & Dışkı Karakteri",
                "keywords": ["iştah", "dışkı"],
                "content": "Şiddetli kaşıntı nedeniyle huzursuzdur, yem tüketimi %30 düşmüştür."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Fiziksel Muayene & Vital Parametreler",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "deri", "kaşıntı", "likenifikasyon", "alopezi"],
                "content": "Vücut Sıcaklığı: 39.1 °C | Kalp Frekansı: 88 atım/dk | Solunum Sayısı: 28 nefes/dk | Mukoza: Pembe | Deri: Baş, kulak, boyun ve sırt hattında ağır tüy dökülmesi, deride aşırı kalınlaşma, sertleşme, kıvrımlaşma (Likenifikasyon) ve tırnaklanma kanama izleri (Eksforyasyon)."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp ve akciğer sesleri normaldir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum & Deri Hassasiyet Deneyleri",
                "keywords": ["sopa", "kama", "kaşıntı", "refleks"],
                "content": "Deriden tutulup sıkıldığında şiddetli kaşınma refleksi (Reflex pruritus) verir."
            },
            "HEMOGRAM_FULL": {
                "name": "🩸 TAM HEMOGRAM (CBC) ANALİZ PANELİ",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "lökosit", "rbc", "eritrosit", "pcv", "hematokrit", "hb", "hemoglobin", "eozinofil", "fibrinojen"],
                "content": """================ TAM HEMOGRAM (CBC) PANELİ ================
• Eritrosit (RBC): 6.2 x10⁶/µL  (Referans: 5.0 - 10.0)
• Hemoglobin (Hb): 10.5 g/dL  (Referans: 8.0 - 15.0)
• Hematokrit (PCV): %31.0  (Referans: 24 - 46)
• MCV: 50.0 fL  |  MCH: 16.9 pg  |  MCHC: 33.8 g/dL
• Trombosit (PLT): 380 x10³/µL  (Referans: 100 - 800)
• Lökosit (WBC): 14.8 x10³/µL  [HAFİF LÖKOSİTOZ] (Referans: 4.0 - 12.0)
  - Çomak Nötrofil (Band): %2
  - Segmenter Nötrofil: %42
  - Lenfosit: %38
  - Monosit: %3.0
  - Eozinofil: %15.0  [BELİRGİN EOZİNOFİLİ / PARAZİTER HİPERSENSİTİVİTE] (Referans: 0 - 24)
  - Bazofil: %0.0
• Plazma Fibrinojeni: 420 mg/dL  (Referans: 200 - 600)
• Plazma Proteini / Fibrinojen Oranı (PP/F): 17.1  [Normal]
==========================================================="""
            },
            "FULL_BIOCHEMISTRY": {
                "name": "🧪 FULL BİYOKİMYA, ENZİM, MİKRO ELEMAN & ELEKTROLİT PANELİ",
                "keywords": ["biyokimya", "biyokimyasal", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "üre", "kreatinin", "glikoz", "bilirubin", "albümin", "globülin", "total protein", "tp", "sodyum", "na", "potasyum", "k", "klor", "cl", "kalsiyum", "ca", "fosfor", "p", "magnezyum", "mg", "bakır", "cu", "çinko", "zn", "demir", "fe", "selenyum", "se"],
                "content": """======= FULL BİYOKİMYA, ENZİM, ELEKTROLİT & İZ ELEMAN PANELİ =======
[Organ Enzimleri & Metabolitler]
• AST: 65 U/L  |  GGT: 20 U/L  |  ALT: 16 U/L  |  ALP: 88 U/L
• BUN: 16 mg/dL  |  Serum Kreatinin: 0.9 mg/dL  |  Glikoz: 64 mg/dL

[Serum Proteinleri]
• Total Protein (TP): 7.2 g/dL  |  Albümin: 3.1 g/dL  |  Globülin: 4.1 g/dL

[Serum Elektrolitleri & İz Elemanlar]
• Na⁺: 139 mmol/L  |  K⁺: 4.4 mmol/L  |  Cl⁻: 100 mmol/L  |  Ca²⁺: 9.2 mg/dL  |  P: 5.2 mg/dL
• Serum Bakır (Cu): 88 µg/dL  |  Serum Çinko (Zn): 85 µg/dL  |  Serum Selenyum (Se): 78 µg/L
==================================================================="""
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2"],
                "content": "Kan pH: 7.40 | pO₂: 56 mmHg | pCO₂: 41 mmHg | HCO₃⁻: 24.2 mmol/L (Normal)."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "idrar tahlili"],
                "content": "İdrar Dansitesi: 1.024 | İdrar pH: 8.0 | Tüm parametreler normal."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "🔬 Derin Deri Kazıntısı & Akar Mikroskopisi",
                "keywords": ["mikroskop", "kazıntı", "deri kazıntısı", "akar", "uyuz", "mineral yağ", "sarcoptes"],
                "gorsel": {
                    "fig": "Figure 1.3-18",
                    "title": "Mikroskopik Sarcoptes Scabiei Akari",
                    "file": "gorseller/figure_1_3_18.jpg",
                    "desc": "Derin deri kazıntısında mineral yağ altında tespit edilen canlı ergin Sarcoptes scabiei akarı."
                },
                "content": "Kapiller kanama görülünceye kadar alınan derin deri kazıntısında canlı Sarcoptes scabiei var. bovis ergin akarları ve karakteristik dışkı peletleri tespit edilmiştir."
            }
        }
    },
    "Vaka G (Çiçek)": {
        "kod": "VAKA_G",
        "sikayet": "Boyun, omuz ve sırt bölgesindeki pigmentsiz (beyaz) deride eritem, hamur ödemi, tabaka halinde soyulma (sloughing/nekroz) ve dokunmaya karşı aşırı ağrı/hipersensitivite.",
        "tanı": "Hepatojen (Sekonder) Fotosensitizasyon (Lantana / Filloeritrin Akümülasyonu)",
        "makroskopik_gorsel": {
            "fig": "Figure 1.7-35",
            "title": "Hepatojen Fotosensitizasyon (Pigmentsiz Deri Nekrozu)",
            "file": "gorseller/figure_1_7_35.jpg",
            "desc": "Yalnızca beyaz (pigmentsiz) deri alanlarında soyulma, hamur ödemi ve nekroz; siyah pigmentli derinin tamamen sağlam kalması."
        },
        "categories": {
            "ANAMNEZ_BESLEME": {
                "name": "🌾 Yetiştirici Anamnezi, Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "mera", "yeşil", "klorofil", "otlama", "lantana", "toksik ot"],
                "content": "3 yaşında Simental melezi inek (500 kg). Taze klorofilden zengin otlarla otlatılmak üzere mer'aya çıkarılmıştır. Mer'ada toksik bitki (Lantana camara / Tribulus) tüketimi öyküsü vardır."
            },
            "LOKASYON_CEVRE": {
                "name": "📍 Lokasyon, Coğrafya & Barınak Şartları",
                "keywords": ["güneş", "ışık", "mera", "açık alanda"],
                "content": "Açık mer'ada doğrudan güneş ışığına (UV) maruz kalmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "karaciğer"],
                "content": "Geçmişinde kronik karaciğer ve safra yolu toksikasyonu öyküsü vardır."
            },
            "ISTAH_SINDIRIM": {
                "name": "🍽️ İştah, Geviş Getirme & Dışkı Karakteri",
                "keywords": ["iştah", "dışkı", "sarılık"],
                "content": "İştah %60 azalmıştır. Dışkı cıvık, ikterik (sarı-yeşil) renklidir."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Fiziksel Muayene & Vital Parametreler",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "ikter", "sarılık", "deri", "boyun", "ödem", "hipersensitivite", "soyulma"],
                "content": "Vücut Sıcaklığı: 39.6 °C | Kalp Frekansı: 92 atım/dk | Solunum Sayısı: 36 nefes/dk | Mukozalar: Belirgin İkterik (Parlak Sarı) | Deri: Boyun, omuz ve sırt hattındaki YALNIZCA PİGMENTSIZ (BEYAZ) deri alanlarında eritem, hamur ödemi, tabaka tabaka soyulma (nekroz/sloughing) ve dokunmaya karşı aşırı ağrı/hipersensitivite. Siyah deri alanları tamamen SAĞLAMDIR."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp ve akciğer oskültasyonu normaldir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum & Deri Hassasiyet Deneyleri",
                "keywords": ["sopa", "kama", "güneş", "ağrı", "dokunma"],
                "content": "Beyaz deri bölgelerine dokunulduğunda hayvan şiddetli ağrı ve kaçınma tepkisi (Hipersensitivite) verir."
            },
            "HEMOGRAM_FULL": {
                "name": "🩸 TAM HEMOGRAM (CBC) ANALİZ PANELİ",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "lökosit", "rbc", "eritrosit", "pcv", "hematokrit", "hb", "hemoglobin", "fibrinojen"],
                "content": """================ TAM HEMOGRAM (CBC) PANELİ ================
• Eritrosit (RBC): 6.0 x10⁶/µL  (Referans: 5.0 - 10.0)
• Hemoglobin (Hb): 10.8 g/dL  (Referans: 8.0 - 15.0)
• Hematokrit (PCV): %32.0  (Referans: 24 - 46)
• MCV: 53.3 fL  |  MCH: 18.0 pg  |  MCHC: 33.7 g/dL
• Trombosit (PLT): 290 x10³/µL  (Referans: 100 - 800)
• Lökosit (WBC): 16.2 x10³/µL  [LÖKOSİTOZ] (Referans: 4.0 - 12.0)
  - Çomak Nötrofil (Band): %6
  - Segmenter Nötrofil: %62
  - Lenfosit: %28
  - Monosit: %4.0
  - Eozinofil: %0.0
• Plazma Fibrinojeni: 680 mg/dL  [YÜKSEK] (Referans: 200 - 600)
• Plazma Proteini / Fibrinojen Oranı (PP/F): 11.2  [Hafif Yangı]
==========================================================="""
            },
            "FULL_BIOCHEMISTRY": {
                "name": "🧪 FULL BİYOKİMYA, ENZİM, MİKRO ELEMAN & ELEKTROLİT PANELİ",
                "keywords": ["biyokimya", "biyokimyasal", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "üre", "kreatinin", "glikoz", "bilirubin", "albümin", "globülin", "total protein", "tp", "sodyum", "na", "potasyum", "k", "klor", "cl", "kalsiyum", "ca", "fosfor", "p", "magnezyum", "mg", "bakır", "cu", "çinko", "zn", "demir", "fe", "selenyum", "se", "filloeritrin"],
                "content": """======= FULL BİYOKİMYA, ENZİM, ELEKTROLİT & İZ ELEMAN PANELİ =======
[Karaciğer & Safra Yolu Hasar Enzimleri]
• GGT (Gamma-Glutamil Transferaz): 185 U/L  [AŞIRI KOLANJİOTOKSİK YÜKSEKLİK] (Referans: 15 - 40)
• AST (Aspartat Aminotransferaz): 280 U/L  [AĞIR PARANKİMAL HASAR] (Referans: 40 - 125)
• ALT: 48 U/L  |  ALP: 310 U/L  [Safra Yolu Tıkanıklığı] (Referans: 0 - 150)
• LDH: 1850 U/L  (Referans: 600 - 1400)
• Kardiyak Troponin I: 0.04 ng/mL  (Normal)

[Böbrek Fonksiyon & Metabolitler]
• BUN: 32 mg/dL  |  Serum Kreatinin: 1.3 mg/dL  |  Glikoz: 58 mg/dL
• Total Bilirubin: 4.8 mg/dL  [AŞIRI İKTER] (Referans: 0.1 - 0.5)
• Direkt Bilirubin: 3.2 mg/dL  [Post-hepatik / Kolestaz]
• Serum Filloeritrin Düzeyi: 0.82 µg/mL  [AŞIRI FOTODİNAMİK TOKSİN AKÜMÜLASYONU] (Referans: <0.05)

[Serum Proteinleri]
• Total Protein (TP): 7.8 g/dL  |  Albümin: 2.6 g/dL  [Hipoalbüminemi]  |  Globülin: 5.2 g/dL

[Serum Elektrolitleri & İz Elemanlar]
• Na⁺: 136 mmol/L  |  K⁺: 3.5 mmol/L  |  Cl⁻: 96 mmol/L  |  Ca²⁺: 8.2 mg/dL  |  P: 4.8 mg/dL
• Serum Bakır (Cu): 140 µg/dL  [Karaciğer Hasarında Yükselme] (Referans: 70 - 120)
• Serum Çinko (Zn): 72 µg/dL  |  Serum Selenyum (Se): 80 µg/L
==================================================================="""
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2"],
                "content": "Kan pH: 7.34 | pO₂: 52 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 21.0 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "idrar tahlili", "bilirubinüri", "çay", "bira"],
                "content": "İdrar Dansitesi: 1.026 | İdrar pH: 7.5 | Bilirubinüri: +3 (İdrar Rengi Koyu Çay / Bira Rengi) | Proteinüri: Trace."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Ultrasonografi & Karaciğer Biyopsisi",
                "keywords": ["ultrason", "usg", "karaciğer", "biyopsi", "safra"],
                "content": "Abdominal Ultrasonografi: Karaciğer parankiminde heterojen ekojenite artışı, safra kesesinde genişleme ve safra çamuru. Histopatoloji: Sentrilobüler hepatosellüler nekroz ve kolanjitis."
            }
        }
    },
    "Vaka H (Ateş)": {
        "kod": "VAKA_H",
        "sikayet": "İlaç/Aşı uygulaması sonrası gövde, boyun ve omuzlarda aniden beliren ödemli kabarık plaklar (urtica) ve huzursuzluk.",
        "tanı": "Akut Ürtiker / Kurdeşen (Allerjik Dermatitis)",
        "makroskopik_gorsel": {
            "fig": "Figure 1.5-1",
            "title": "Akut Ürtiker (Ödem Plakları)",
            "file": "gorseller/figure_1_5_1.jpg",
            "desc": "Gövde ve boyun derisinde aniden beliren dairesel ödemli kabarık ürtiker plakları."
        },
        "categories": {
            "ANAMNEZ_BESLEME": {
                "name": "🌾 Yetiştirici Anamnezi, Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "aşı", "enjeksiyon", "ilaç", "alerji"],
                "content": "2 yaşında düve (380 kg). Yaklaşık 2 saat önce paraziter veya enfeksiyöz parenteral enjeksiyon / aşı uygulaması yapılmıştır."
            },
            "LOKASYON_CEVRE": {
                "name": "📍 Lokasyon, Coğrafya & Barınak Şartları",
                "keywords": ["barınak"],
                "content": "Ahır içerisinde kapalı alandadır."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden"],
                "content": "Daha önce herhangi bir alerjik reaksiyon kaydı yoktur."
            },
            "ISTAH_SINDIRIM": {
                "name": "🍽️ İştah, Geviş Getirme & Dışkı Karakteri",
                "keywords": ["iştah", "dışkı"],
                "content": "Aniden gelişen huzursuzluk nedeniyle yem yemeyi bırakmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Fiziksel Muayene & Vital Parametreler",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "urtica", "plak", "ödem"],
                "content": "Vücut Sıcaklığı: 38.9 °C (Normal) | Kalp Frekansı: 96 atım/dk | Solunum Sayısı: 34 nefes/dk | Mukozalar: Hiperemik (Kızarık) | Deri: Gövde, boyun ve omuz bölgesinde 2-8 cm çaplı, basmakla düzleşen, ödemli, kabarık plaklar (Urtica / Wheals)."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp ve akciğer sesleri normaldir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum & Deri Hassasiyet Deneyleri",
                "keywords": ["sopa", "kama", "plak"],
                "content": "Plakların üzerine parmakla basıldığında geçici çukurlaşma (pitting) gözlenir."
            },
            "HEMOGRAM_FULL": {
                "name": "🩸 TAM HEMOGRAM (CBC) ANALİZ PANELİ",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "lökosit", "rbc", "eritrosit", "pcv", "hematokrit", "hb", "hemoglobin", "eozinofil", "fibrinojen"],
                "content": """================ TAM HEMOGRAM (CBC) PANELİ ================
• Eritrosit (RBC): 6.5 x10⁶/µL  (Referans: 5.0 - 10.0)
• Hemoglobin (Hb): 11.0 g/dL  (Referans: 8.0 - 15.0)
• Hematokrit (PCV): %33.0  (Referans: 24 - 46)
• Lökosit (WBC): 11.2 x10³/µL  (Referans: 4.0 - 12.0)
  - Segmenter Nötrofil: %45
  - Lenfosit: %38
  - Monosit: %3.0
  - Eozinofil: %14.0  [AĞIR EOZİNOFİLİ / İLAÇ ALERJİSİ] (Referans: 0 - 24)
  - Bazofil: %0.0
• Plazma Fibrinojeni: 260 mg/dL  (Referans: 200 - 600)
• Plazma Proteini / Fibrinojen Oranı (PP/F): 26.1  [Normal]
==========================================================="""
            },
            "FULL_BIOCHEMISTRY": {
                "name": "🧪 FULL BİYOKİMYA, ENZİM, MİKRO ELEMAN & ELEKTROLİT PANELİ",
                "keywords": ["biyokimya", "biyokimyasal", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "üre", "kreatinin", "glikoz", "bilirubin", "albümin", "globülin", "total protein", "tp", "sodyum", "na", "potasyum", "k", "klor", "cl", "kalsiyum", "ca", "fosfor", "p", "magnezyum", "mg", "bakır", "cu", "çinko", "zn", "demir", "fe", "selenyum", "se", "histamin"],
                "content": """======= FULL BİYOKİMYA, ENZİM, ELEKTROLİT & İZ ELEMAN PANELİ =======
[Organ Enzimleri & Metabolitler]
• AST: 62 U/L  |  GGT: 18 U/L  |  ALT: 15 U/L  |  ALP: 80 U/L
• BUN: 14 mg/dL  |  Serum Kreatinin: 0.8 mg/dL  |  Glikoz: 70 mg/dL
• Serum Histamin Düzeyi: 420 ng/mL  [AŞIRI SALINIM] (Referans: <50)

[Serum Proteinleri & Elektrolitler]
• Total Protein (TP): 6.8 g/dL  |  Albümin: 3.2 g/dL  |  Globülin: 3.6 g/dL
• Na⁺: 140 mmol/L  |  K⁺: 4.2 mmol/L  |  Cl⁻: 100 mmol/L  |  Ca²⁺: 9.4 mg/dL  |  P: 5.0 mg/dL
==================================================================="""
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2"],
                "content": "Kan pH: 7.41 | pO₂: 58 mmHg | pCO₂: 39 mmHg | HCO₃⁻: 24.5 mmol/L (Normal)."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "idrar tahlili"],
                "content": "İdrar Dansitesi: 1.022 | İdrar pH: 8.0 | Tüm parametreler normal."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Biyopsi & Allerji Paneli",
                "keywords": ["ultrason", "usg", "biyopsi"],
                "content": "Deri Biyopsisi: Dermis tabakasında mast hücre degranülasyonu ve eozinofilik ödem."
            }
        }
    },
    "Vaka I (Fırtına)": {
        "kod": "VAKA_I",
        "sikayet": "Nefes alırken ıslık benzeri yüksek tonlu ses (İnspiratorik Stridor), ağızdan köpüklü salya akması ve baş-boyun eksfonsiyonu.",
        "tanı": "Akut Larenjit ve Larenks Ödemi (Acute Laryngeal Edema)",
        "categories": {
            "ANAMNEZ_BESLEME": {
                "name": "🌾 Yetiştirici Anamnezi, Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "toz", "kaba yem", "yutma"],
                "content": "1.5 yaşında dana (320 kg). Tozlu kaba yem yedikten sonra aniden öksürük ve hırıltılı nefes darlığı başlamıştır."
            },
            "LOKASYON_CEVRE": {
                "name": "📍 Lokasyon, Coğrafya & Barınak Şartları",
                "keywords": ["barınak", "toz"],
                "content": "Kuru ve aşırı tozlu kapalı padoık."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş"],
                "content": "Geçmiş öyküsü temizdir."
            },
            "ISTAH_SINDIRIM": {
                "name": "🍽️ İştah, Geviş Getirme & Dışkı Karakteri",
                "keywords": ["iştah", "yutma", "dysphagia"],
                "content": "Yutma ağrısı (Dysphagia) nedeniyle su içmeyi ve yem yemeyi reddetmektedir."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Fiziksel Muayene & Vital Parametreler",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "stridor", "larenks", "mukoza"],
                "content": "Vücut Sıcaklığı: 39.4 °C | Kalp Frekansı: 102 atım/dk | Solunum Sayısı: 46 nefes/dk (Nefes alma güçlüğü / İnspiratorik Dispne) | Mukozalar: Siyanotik | Baş ve boyun uzatılmış durumdadır."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Larenks & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "stridor", "ıslık", "larenks", "akciğer"],
                "content": "Larenks Muayenesi: Larenks üzerine dinleme koyulduğunda çok şiddetli ıslık benzeri İnspiratorik Stridor sesi duyulmaktadır. Akciğer Oskültasyonu: Akciğer parankim sesleri NORMALDİR (Enfeksiyon akciğere inmemiştir)."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum & Trakeal Hassasiyet Deneyleri",
                "keywords": ["trakea", "larenks", "refleks", "sıkma"],
                "content": "Larenks ve Trakeal Refleks Testi: POZİTİF (Larenks kıkırdakları hafifçe sıkıldığında şiddetli inleme ve boğulurcasına öksürük krizi)."
            },
            "HEMOGRAM_FULL": {
                "name": "🩸 TAM HEMOGRAM (CBC) ANALİZ PANELİ",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "lökosit", "rbc", "eritrosit", "pcv", "hematokrit", "hb", "hemoglobin", "fibrinojen"],
                "content": """================ TAM HEMOGRAM (CBC) PANELİ ================
• Eritrosit (RBC): 6.8 x10⁶/µL  (Referans: 5.0 - 10.0)
• Hemoglobin (Hb): 11.5 g/dL  (Referans: 8.0 - 15.0)
• Hematokrit (PCV): %35.0  (Referans: 24 - 46)
• Lökosit (WBC): 12.8 x10³/µL  [HAFİF YÜKSEK] (Referans: 4.0 - 12.0)
  - Segmenter Nötrofil: %58
  - Lenfosit: %36
  - Monosit: %3.0
  - Eozinofil: %3.0
• Plazma Fibrinojeni: 380 mg/dL  (Referans: 200 - 600)
• Plazma Proteini / Fibrinojen Oranı (PP/F): 18.9  [Normal]
==========================================================="""
            },
            "FULL_BIOCHEMISTRY": {
                "name": "🧪 FULL BİYOKİMYA, ENZİM, MİKRO ELEMAN & ELEKTROLİT PANELİ",
                "keywords": ["biyokimya", "biyokimyasal", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "üre", "kreatinin", "glikoz", "bilirubin", "albümin", "globülin", "total protein", "tp", "sodyum", "na", "potasyum", "k", "klor", "cl", "kalsiyum", "ca", "fosfor", "p", "magnezyum", "mg", "bakır", "cu", "çinko", "zn", "demir", "fe", "selenyum", "se"],
                "content": """======= FULL BİYOKİMYA, ENZİM, ELEKTROLİT & İZ ELEMAN PANELİ =======
[Organ Enzimleri & Metabolitler]
• AST: 68 U/L  |  GGT: 21 U/L  |  ALT: 17 U/L  |  ALP: 85 U/L
• BUN: 15 mg/dL  |  Serum Kreatinin: 0.9 mg/dL  |  Glikoz: 72 mg/dL

[Serum Proteinleri & Elektrolitler]
• Total Protein (TP): 7.2 g/dL  |  Albümin: 3.3 g/dL  |  Globülin: 3.9 g/dL
• Na⁺: 140 mmol/L  |  K⁺: 4.3 mmol/L  |  Cl⁻: 101 mmol/L  |  Ca²⁺: 9.3 mg/dL  |  P: 5.2 mg/dL
==================================================================="""
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2"],
                "content": "Kan pH: 7.32 | pO₂: 92 mmHg  [AKCİĞERLER SAĞLAM OLDUĞU İÇİN OKSİJENASYON NORMAL] | pCO₂: 48 mmHg | HCO₃⁻: 23.0 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "idrar tahlili"],
                "content": "İdrar Dansitesi: 1.024 | İdrar pH: 8.0 | Tüm parametreler normal."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Laringoskopi & Endoskopi Muayenesi",
                "keywords": ["ultrason", "usg", "endoskopi", "laringoskopi", "larenks"],
                "content": "Endoskopi / Laringoskopi: Larenks mukoza ve plika vokalislerde şiddetli ödem, hiperemi ve lümen darlığı (%70 tıkanma)."
            }
        }
    },
    "Vaka J (Şahin)": {
        "kod": "VAKA_J",
        "sikayet": "Tek taraflı mukopürülan (irinli) burun akıntısı, yüzde asimetri ve frontal kemik üzerine vurulduğunda mat ses (tok ses) alınması.",
        "tanı": "Frontal Sinüzit (Chronic Frontal Sinusitis / Dehorning Komplikasyonu)",
        "categories": {
            "ANAMNEZ_BESLEME": {
                "name": "🌾 Yetiştirici Anamnezi, Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "dehorning", "boynuz", "kesim"],
                "content": "2 yaşında tosun (450 kg). Yaklaşık 1 ay önce açık yöntemle (testere ile) boynuz kesimi (dehorning) yapılmıştır."
            },
            "LOKASYON_CEVRE": {
                "name": "📍 Lokasyon, Coğrafya & Barınak Şartları",
                "keywords": ["barınak"],
                "content": "Açık besi padoğunda barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "boynuz"],
                "content": "Boynuz kesimi sonrası yara yeri enfekte olmuştur."
            },
            "ISTAH_SINDIRIM": {
                "name": "🍽️ İştah, Geviş Getirme & Dışkı Karakteri",
                "keywords": ["iştah", "dışkı"],
                "content": "Baş ağrısı nedeniyle isteksizdir."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Fiziksel Muayene & Vital Parametreler",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "burun", "akıntı", "pürülan", "sinüs"],
                "content": "Vücut Sıcaklığı: 39.2 °C | Kalp Frekansı: 84 atım/dk | Solunum Sayısı: 28 nefes/dk | Burun: Sol burun deliğinden tek taraflı kötü kokulu mukopürülan (irinli) akıntı gelmektedir."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp ve akciğer oskültasyonu normaldir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Sinüs Perküsyonu & Ağrı Deneyleri",
                "keywords": ["perküsyon", "sinüs", "matite", "tok", "ağrı", "vuruk"],
                "content": "Sinüs Perküsyonu (Vuruk Muayenesi): Sol frontal sinüs üzerine perküsyon yapıldığında normal rezonant boş kütük sesi yerine **MAT / TOK SES (Dullness)** alınmakta ve hayvan şiddetli ağrı reaksiyonu gösterip başını kaçırmaktadır."
            },
            "HEMOGRAM_FULL": {
                "name": "🩸 TAM HEMOGRAM (CBC) ANALİZ PANELİ",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "lökosit", "rbc", "eritrosit", "pcv", "hematokrit", "hb", "hemoglobin", "fibrinojen"],
                "content": """================ TAM HEMOGRAM (CBC) PANELİ ================
• Eritrosit (RBC): 6.4 x10⁶/µL  (Referans: 5.0 - 10.0)
• Hemoglobin (Hb): 10.8 g/dL  (Referans: 8.0 - 15.0)
• Hematokrit (PCV): %32.0  (Referans: 24 - 46)
• Lökosit (WBC): 16.8 x10³/µL  [LÖKOSİTOZ] (Referans: 4.0 - 12.0)
  - Çomak Nötrofil (Band): %8
  - Segmenter Nötrofil: %64
  - Lenfosit: %24
  - Monosit: %4.0
• Plazma Fibrinojeni: 720 mg/dL  [YÜKSEK] (Referans: 200 - 600)
• Plazma Proteini / Fibrinojen Oranı (PP/F): 11.1  [Fibrinöz Yangı]
==========================================================="""
            },
            "FULL_BIOCHEMISTRY": {
                "name": "🧪 FULL BİYOKİMYA, ENZİM, MİKRO ELEMAN & ELEKTROLİT PANELİ",
                "keywords": ["biyokimya", "biyokimyasal", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "üre", "kreatinin", "glikoz", "bilirubin", "albümin", "globülin", "total protein", "tp", "sodyum", "na", "potasyum", "k", "klor", "cl", "kalsiyum", "ca", "fosfor", "p", "magnezyum", "mg", "bakır", "cu", "çinko", "zn", "demir", "fe", "selenyum", "se"],
                "content": """======= FULL BİYOKİMYA, ENZİM, ELEKTROLİT & İZ ELEMAN PANELİ =======
[Organ Enzimleri & Metabolitler]
• AST: 74 U/L  |  GGT: 22 U/L  |  ALT: 18 U/L  |  ALP: 90 U/L
• BUN: 16 mg/dL  |  Serum Kreatinin: 0.9 mg/dL  |  Glikoz: 68 mg/dL

[Serum Proteinleri & Elektrolitler]
• Total Protein (TP): 8.0 g/dL  |  Albümin: 3.1 g/dL  |  Globülin: 4.9 g/dL  [Hipergamaglobülinemi]
• Na⁺: 139 mmol/L  |  K⁺: 4.4 mmol/L  |  Cl⁻: 100 mmol/L  |  Ca²⁺: 9.2 mg/dL  |  P: 5.0 mg/dL
==================================================================="""
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2"],
                "content": "Kan pH: 7.39 | pO₂: 56 mmHg | pCO₂: 40 mmHg | HCO₃⁻: 24.0 mmol/L (Normal)."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "idrar tahlili"],
                "content": "İdrar Dansitesi: 1.024 | İdrar pH: 8.0 | Tüm parametreler normal."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Radyografi (Röntgen), Sinüs Trepanasyonu & Kültür",
                "keywords": ["ultrason", "usg", "röntgen", "radiografi", "sinüs", "trepanasyon", "kültür", "pürülan"],
                "content": "Frontal Röntgen (Grafi): Sol frontal sinüs boşluğunda opasite artışı (irin birikimi). Sinüs Ponksiyonu / Trepanasyon: Koyu pürülan kokulu sıvı gelişi. İrin Kültürü: Trueperella pyogenes ve Pseudomonas aeruginosa izolasyonu."
            }
        }
    },
    "Vaka K (Rüzgar)": {
        "kod": "VAKA_K",
        "sikayet": "Atın tek taraflı burun deliğinden kötü kokulu kanlı-irinli akıntı gelmesi, parotis bölgesinde ağrılı şişlik ve yutma zorluğu.",
        "tanı": "Hava Kesesi Mikozu (Guttural Pouch Mycosis / Aspergillus fumigatus)",
        "categories": {
            "ANAMNEZ_BESLEME": {
                "name": "🌾 Yetiştirici Anamnezi, Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "at", "küf", "küflü", "saman", "ot"],
                "content": "6 yaşında İngiliz Atı (520 kg). Küflü ve nemli depolanmış ot/saman tüketimi öyküsü bulunmaktadır."
            },
            "LOKASYON_CEVRE": {
                "name": "📍 Lokasyon, Coğrafya & Barınak Şartları",
                "keywords": ["harman", "tavla", "haras"],
                "content": "Tavla içerisinde nemli boksta barınmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "kanama", "epistaksis"],
                "content": "Geçmişinde 1 hafta önce dinlenme halindeyken burundan kendiliğinden duran kanama (Epistaksis) öyküsü mevcuttur."
            },
            "ISTAH_SINDIRIM": {
                "name": "🍽️ İştah, Geviş Getirme & Dışkı Karakteri",
                "keywords": ["iştah", "yutma"],
                "content": "Yutma sinirlerinin (N. glossopharyngeus / N. vagus) felcine bağlı Yutma Güçlüğü (Dysphagia) mevcuttur."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Fiziksel Muayene & Vital Parametreler",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "burun", "kan", "epistaksis", "parotis"],
                "content": "Vücut Sıcaklığı: 38.6 °C | Kalp Frekansı: 54 atım/dk | Solunum Sayısı: 18 nefes/dk | Burun: Sol burun deliğinden pas renkli kanlı-irinli ve kötü kokulu akıntı | Parotis bölgesi ağrılı ve sıcak."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp ve akciğer oskültasyonu normaldir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Parotis & Baş Hassasiyet Deneyleri",
                "keywords": ["parotis", "baskı", "yutma"],
                "content": "Parotis üzerine basıldığında ağrı ve öksürük tepkisi."
            },
            "HEMOGRAM_FULL": {
                "name": "🩸 TAM HEMOGRAM (CBC) ANALİZ PANELİ",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "lökosit", "rbc", "eritrosit", "pcv", "hematokrit", "hb", "hemoglobin", "fibrinojen"],
                "content": """================ TAM HEMOGRAM (CBC) PANELİ ================
• Eritrosit (RBC): 5.8 x10⁶/µL  (Referans: 6.5 - 12.5)
• Hemoglobin (Hb): 9.2 g/dL  [Kanamaya Bağlı Anemi] (Referans: 11 - 19)
• Hematokrit (PCV): %27.0  (Referans: 32 - 52)
• Lökosit (WBC): 14.2 x10³/µL  [LÖKOSİTOZ] (Referans: 5.5 - 12.5)
  - Segmenter Nötrofil: %68
  - Lenfosit: %26
  - Monosit: %4.0
  - Eozinofil: %2.0
• Plazma Fibrinojeni: 620 mg/dL  (Referans: 100 - 400)
==========================================================="""
            },
            "FULL_BIOCHEMISTRY": {
                "name": "🧪 FULL BİYOKİMYA, ENZİM, MİKRO ELEMAN & ELEKTROLİT PANELİ",
                "keywords": ["biyokimya", "biyokimyasal", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "üre", "kreatinin", "glikoz", "bilirubin", "albümin", "globülin", "total protein", "tp", "sodyum", "na", "potasyum", "k", "klor", "cl", "kalsiyum", "ca", "fosfor", "p", "magnezyum", "mg", "bakır", "cu", "çinko", "zn", "demir", "fe", "selenyum", "se"],
                "content": """======= FULL BİYOKİMYA, ENZİM, ELEKTROLİT & İZ ELEMAN PANELİ =======
[Organ Enzimleri & Metabolitler]
• AST: 280 U/L  |  GGT: 24 U/L  |  CK: 310 U/L
• BUN: 22 mg/dL  |  Serum Kreatinin: 1.2 mg/dL  |  Glikoz: 85 mg/dL

[Serum Proteinleri & Elektrolitler]
• Total Protein (TP): 7.4 g/dL  |  Albümin: 3.0 g/dL  |  Globülin: 4.4 g/dL
• Na⁺: 138 mmol/L  |  K⁺: 4.0 mmol/L  |  Cl⁻: 99 mmol/L  |  Ca²⁺: 11.2 mg/dL  |  P: 3.8 mg/dL
==================================================================="""
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2"],
                "content": "Kan pH: 7.38 | pO₂: 88 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 24.8 mmol/L (Normal)."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "idrar tahlili"],
                "content": "İdrar Dansitesi: 1.030 | İdrar pH: 7.5 | Tüm parametreler normal."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Endoskopi (Hava Kesesi) & Mantar Kültürü",
                "keywords": ["ultrason", "usg", "endoskopi", "hava kesesi", "karotid", "arter", "aspergillus", "kültür"],
                "content": "Hava Kesesi Endoskopisi: İç Karotid Arter (A. carotis interna) üzerinde siyah-yeşil renkli difteroid Dumanlı Mantar Plağı (Mycrotic plaque) ve erozyon. Mantar Kültürü: Aspergillus fumigatus üretilmiştir."
            }
        }
    },
    "Vaka L (Poyraz)": {
        "kod": "VAKA_L",
        "sikayet": "Gurme enfeksiyonu geçiren tayda parotis bölgesinde aşırı şişlik, başı dik tutma ve çift taraflı mukopürülan burun akıntısı.",
        "tanı": "Hava Kesesi Empiyemi (Guttural Pouch Empyema / Streptococcus equi)",
        "categories": {
            "ANAMNEZ_BESLEME": {
                "name": "🌾 Yetiştirici Anamnezi, Rasyon & Besleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "gurm", "tay", "boğaz"],
                "content": "1 yaşında tay (280 kg). Yaklaşık 3 hafta önce Gurm (Streptococcus equi subsp. equi) enfeksiyonu geçirmiştir."
            },
            "LOKASYON_CEVRE": {
                "name": "📍 Lokasyon, Coğrafya & Barınak Şartları",
                "keywords": ["barınak"],
                "content": "Harada tay padoğunda kalmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "gurm"],
                "content": "Geçirilmiş Gurm enfeksiyonu ve retrofaringeal lenf yumrusu apsesi."
            },
            "ISTAH_SINDIRIM": {
                "name": "🍽️ İştah, Geviş Getirme & Dışkı Karakteri",
                "keywords": ["iştah", "yutma"],
                "content": "Boğaz ağrısı nedeniyle yem yemesi güçleşmiştir."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Fiziksel Muayene & Vital Parametreler",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "burun", "akıntı", "pürülan", "parotis"],
                "content": "Vücut Sıcaklığı: 39.8 °C (Ateş) | Kalp Frekansı: 68 atım/dk | Solunum Sayısı: 28 nefes/dk | Burun: Çift taraflı koyu sarı-yeşil pürülan (irinli) akıntı | Parotis bölgesi iki taraflı şiş ve gergindir."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon"],
                "content": "Kalp ve akciğer oskültasyonu normaldir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Parotis & Baş Hassasiyet Deneyleri",
                "keywords": ["parotis", "baskı"],
                "content": "Viborg üçgeni ve parotis üzerine basıldığında fluktuasyon ve ağrı."
            },
            "HEMOGRAM_FULL": {
                "name": "🩸 TAM HEMOGRAM (CBC) ANALİZ PANELİ",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "lökosit", "rbc", "eritrosit", "pcv", "hematokrit", "hb", "hemoglobin", "fibrinojen"],
                "content": """================ TAM HEMOGRAM (CBC) PANELİ ================
• Eritrosit (RBC): 7.2 x10⁶/µL  (Referans: 6.5 - 12.5)
• Hemoglobin (Hb): 12.0 g/dL  (Referans: 11 - 19)
• Hematokrit (PCV): %36.0  (Referans: 32 - 52)
• Lökosit (WBC): 24.8 x10³/µL  [ŞİDDETLİ LÖKOSİTOZ] (Referans: 5.5 - 12.5)
  - Çomak Nötrofil (Band): %12
  - Segmenter Nötrofil: %72  [Nötrofili]
  - Lenfosit: %14
  - Monosit: %2.0
• Plazma Fibrinojeni: 880 mg/dL  [AŞIRI YÜKSEK] (Referans: 100 - 400)
==========================================================="""
            },
            "FULL_BIOCHEMISTRY": {
                "name": "🧪 FULL BİYOKİMYA, ENZİM, MİKRO ELEMAN & ELEKTROLİT PANELİ",
                "keywords": ["biyokimya", "biyokimyasal", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "üre", "kreatinin", "glikoz", "bilirubin", "albümin", "globülin", "total protein", "tp", "sodyum", "na", "potasyum", "k", "klor", "cl", "kalsiyum", "ca", "fosfor", "p", "magnezyum", "mg", "bakır", "cu", "çinko", "zn", "demir", "fe", "selenyum", "se"],
                "content": """======= FULL BİYOKİMYA, ENZİM, ELEKTROLİT & İZ ELEMAN PANELİ =======
[Organ Enzimleri & Metabolitler]
• AST: 110 U/L  |  GGT: 22 U/L  |  CK: 220 U/L
• BUN: 20 mg/dL  |  Serum Kreatinin: 1.0 mg/dL  |  Glikoz: 78 mg/dL

[Serum Proteinleri & Elektrolitler]
• Total Protein (TP): 8.8 g/dL  |  Albümin: 2.8 g/dL  |  Globülin: 6.0 g/dL  [Hipergamaglobülinemi]
• Na⁺: 137 mmol/L  |  K⁺: 4.1 mmol/L  |  Cl⁻: 98 mmol/L  |  Ca²⁺: 10.8 mg/dL  |  P: 4.2 mg/dL
==================================================================="""
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2"],
                "content": "Kan pH: 7.36 | pO₂: 82 mmHg | pCO₂: 44 mmHg | HCO₃⁻: 23.5 mmol/L (Normal)."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "idrar tahlili"],
                "content": "İdrar Dansitesi: 1.028 | İdrar pH: 7.5 | Tüm parametreler normal."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Hava Kesesi Endoskopisi, Lavaj & Bakteri Kültürü",
                "keywords": ["ultrason", "usg", "endoskopi", "hava kesesi", "kondroit", "taş", "pürülan", "streptococcus", "kültür"],
                "content": "Hava Kesesi Endoskopisi: Hava kesesi içinde birikmiş sıvı pürülan eksudat ve kurumuş taşlaşmış irin yumakları (Kondroit / Chondroids). Bakteri Kültürü: Streptococcus equi subsp. equi üretilmiştir."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Master Akıllı Anamnez & Bulgu Sorgulama Konsolu (12 Vaka Full Tahlil & Biyokimya Veri Tabanı)</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde hazır cevap şıkları yoktur. 
        Klinik şüphenize göre merak ettiğiniz konuları <b>kendi cümlenizle</b> arama kutusuna yazınız 
        (Örn: <i>"Rasyon bilgisi nedir?"</i>, <i>"Ateşi kaç derece?"</i>, <i>"Kalp ve akciğer sesleri nasıl?"</i>, <i>"Tam Hemogram kan sayımı"</i>, <i>"Biyokimya, organ enzim kalıbı, elektrolitler ve iz elemanlar"</i>, <i>"Kan gazı analizi"</i>, <i>"İdrar tahlili"</i>, <i>"Ultrason ve röntgen"</i>).
    </div>
""", unsafe_allow_html=True)

# Select Case
selected_case_name = st.selectbox(
    "🔍 İncelemek İstediğiniz Vakayı Seçiniz:",
    options=list(CASES.keys()),
    index=0
)

active_case = CASES[selected_case_name]

# Reset history if case changes
if "last_case" not in st.session_state:
    st.session_state.last_case = selected_case_name

if st.session_state.last_case != selected_case_name:
    st.session_state.history = []
    st.session_state.last_case = selected_case_name

if "history" not in st.session_state:
    st.session_state.history = []

st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — İlk Başvuru Şikayeti</div>", unsafe_allow_html=True)
st.info(f"**Hastanın Başvuru Şikayeti:** {active_case['sikayet']}")

# AUTOMATIC DISPLAY OF MACROSCOPIC CLINICAL IMAGES UPON CASE SELECTION
if "makroskopik_gorsel" in active_case:
    mg = active_case["makroskopik_gorsel"]
    st.markdown("### 📸 Klinik Makroskopik Lezyon Görseli")
    real_path = find_gorsel_path(mg["file"])
    if real_path and os.path.exists(real_path):
        st.image(real_path, use_container_width=True)
    else:
        uploaded_img = st.file_uploader(
            "📷 Klinik Görsel Yükleyiniz (.jpg / .png):",
            type=["jpg", "jpeg", "png"],
            key=f"up_macro_{active_case['kod']}"
        )
        if uploaded_img is not None:
            st.image(uploaded_img, use_container_width=True)

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
        "Sorunuzu Buraya Yazınız:",
        key="query_input",
        placeholder="Örn: İştah durumu nasıl?, Hemogram sonuçları?, Full Biyokimya ve elektrolitler, Kan gazı..."
    )

with col_button:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    submit_btn = st.button("🔎 Sor ve Sorgula", type="primary", use_container_width=True)

if submit_btn and user_query:
    matches = match_query(user_query, active_case["categories"])
    if matches:
        new_disc = 0
        for cat_key in matches:
            cat_data = active_case["categories"][cat_key]
            already_in = any(item["cat_key"] == cat_key for item in st.session_state.history)
            if not already_in:
                item_dict = {
                    "cat_key": cat_key,
                    "query": user_query,
                    "title": cat_data["name"],
                    "content": cat_data["content"]
                }
                if "gorsel" in cat_data:
                    item_dict["gorsel"] = cat_data["gorsel"]
                st.session_state.history.append(item_dict)
                new_disc += 1
        if new_disc > 0:
            st.success(f"🎉 {new_disc} yeni klinik bulgu / bilgi açığa çıkarıldı!")
    else:
        st.warning("⚠️ Eşleşen bilgi bulunamadı. Lütfen sorunuzu farklı kelimelerle yazınız (Örn: 'rasyon', 'ateş', 'hemogram', 'biyokimya', 'kan gazı', 'idrar', 'ultrason').")

# Display Discovered Information
st.markdown("---")
st.markdown(f"### 📂 Keşfedilen Klinik İpuçları ve Muayene Bulguları ({len(st.session_state.history)} Bilgi Açıldı)")

if st.session_state.history:
    for item in reversed(st.session_state.history):
        st.markdown(f"""
            <div class='card-found'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                    <span class='badge-category'>{item['title']}</span>
                    <span style='font-size:12px; color:#7F7F7F;'>Sorulan Soru: "{item['query']}"</span>
                </div>
                <div class='card-content'><b>🩺 Bulgu / Öykü / Tahlil Sonucu:</b>
{item['content']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # MICROSCOPIC IMAGES DISPLAYED ONLY AFTER BEING QUERY-TRIGGERED
        if "gorsel" in item:
            g = item["gorsel"]
            st.markdown("#### 🔬 Mikroskopik Teşhis Görseli")
            m_path = find_gorsel_path(g["file"])
            if m_path and os.path.exists(m_path):
                st.image(m_path, use_container_width=True)
            else:
                up_micro = st.file_uploader(
                    "📷 Mikroskopik Görsel Yükleyiniz (.jpg / .png):",
                    type=["jpg", "jpeg", "png"],
                    key=f"up_micro_{item['cat_key']}"
                )
                if up_micro is not None:
                    st.image(up_micro, use_container_width=True)

# Teacher Portal
with st.sidebar:
    st.markdown("### 🏛️ ÇU Veteriner Fakültesi")
    st.markdown("**VET401 İç Hastalıkları I**")
    st.markdown("---")
    st.markdown("### 🔒 Eğitmen Portalı (Hoca Paneli)")
    teacher_login = st.checkbox("Eğitmen Anahtar Paneli")
    if teacher_login:
        pass_code = st.text_input("Giriş Şifresi:", type="password")
        if pass_code == "vet401":
            st.success("Eğitmen Erişimi Onaylandı!")
            st.markdown(f"### 🔑 {selected_case_name} Cevap Anahtarı")
            if "tanı" in active_case:
                st.info(f"**Kesin Tanı:** {active_case['tanı']}")
            
            if st.button("🔓 Tüm Tahlil ve Bulguları Sınıf Ekranda Aç"):
                for ck, cv in active_case["categories"].items():
                    already_in = any(item["cat_key"] == ck for item in st.session_state.history)
                    if not already_in:
                        item_dict = {
                            "cat_key": ck,
                            "query": "Eğitmen Tarafından Tüm Bilgiler Açıldı",
                            "title": cv["name"],
                            "content": cv["content"]
                        }
                        if "gorsel" in cv:
                            item_dict["gorsel"] = cv["gorsel"]
                        st.session_state.history.append(item_dict)
                st.rerun()
                
            st.markdown("#### 📚 Vakanın Tam Laboratuvar & Muayene Özeti:")
            for ck, cv in active_case["categories"].items():
                with st.expander(f"• {cv['name']}"):
                    st.write(cv["content"])
        elif pass_code:
            st.error("Hatalı Şifre!")
