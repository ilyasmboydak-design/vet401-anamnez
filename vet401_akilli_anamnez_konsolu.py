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

# Helper function to resolve image paths robustly regardless of case/extension
def find_gorsel_path(target_filename):
    if not target_filename:
        return None
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_dirs = [
        os.path.join(base_dir, "gorseller"),
        base_dir,
        os.path.join(base_dir, "..", "gorseller")
    ]
    clean_target = os.path.basename(target_filename).lower()
    name_no_ext = os.path.splitext(clean_target)[0]
    
    for pdir in possible_dirs:
        if os.path.exists(pdir) and os.path.isdir(pdir):
            for f in os.listdir(pdir):
                f_lower = f.lower()
                f_no_ext = os.path.splitext(f_lower)[0]
                if f_lower == clean_target or f_no_ext == name_no_ext:
                    return os.path.join(pdir, f)
    return None

# CASES KNOWLEDGE BASE - 12 CASES WITH FULL COMPREHENSIVE 15 CATEGORIES
CASES = {
    "Vaka A (Papatya)": {
        "kod": "VAKA_A",
        "sikayet": "Gerdan ve submandibuler bölgede soğuk hamur gibi ödem, sütten aniden kesilme, iştahsızlık ve belirgin durgunluk.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "mısır", "arpa", "silaj", "balya", "saman", "kaba", "tel", "çivi", "yabancı cisim"],
                "content": "İşletmede entansif kaba/yoğun yem karma rasyonu uygulanmaktadır. Balya parçalama esnasında kaba yeme inşaat tellerinin ve çivilerin karışmış olabileceği belirtilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil", "coğrafya", "yükseklik"],
                "content": "Ceyhan ovasında (rakım ~50 metre) sabit süt tesisinde doğup büyümüştür. Yayla veya yüksek rakım nakil öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "mastitis", "öykü"],
                "content": "Geçmişinde kronik mastitis veya metabolik hastalık yoktur. 2 ay önce sorunsuz doğum yapmıştır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yutma", "geviş", "yem yemiyor", "anoreksi"],
                "content": "Ağrı ve perikardiyal yangı nedeniyle tam anoreksi (komple yem ve su reddi) ve geviş getirme durması mevcuttur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "dehidrasyon", "ödem", "staz"],
                "content": "Vücut Sıcaklığı: 39.8 °C | Kalp Frekansı: 102 atım/dk | Solunum Frekansı: 42 nefes/dk | Mukozalar: Soluk pembe | CRT: 2.5 sn | Dehidrasyon: %6 | Gerdan ve submandibuler bölgede soğuk hamur ödem | Vena jugularis stazı +, yalancı jugular nabız +."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "akciğer"],
                "content": "Kalp Oskültasyonu: Gaz ve pürülan sıvının çalkalanmasına bağlı çamaşır makinesi / su şılpırtısı (splashing) sesi ve boğuk kalp sesleri. Akciğer Oskültasyonu: Ventro-lateral alanlarda solunum sesleri hafif azalmış."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "provokasyon"],
                "content": "Withers pinch (cidago sıkıştırma) testi POZİTİF (hayvan sırtını çökertmeyip inliyor). Sopa/kama testi POZİTİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Paneli (18 Parametre)",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "lökosit", "rbc", "eritrosit", "hb", "pcv", "hematokrit", "mcv", "mch", "mchc", "rdw", "plt", "trombosit", "nötrofil", "çomak", "lenfosit", "eozinofil", "bazofil", "fibrinojen", "pp/f"],
                "content": "RBC: 5.2 x10⁶/µL | Hb: 8.1 g/dL | PCV/HCT: %26 | MCV: 50 fL | MCH: 15.5 pg | MCHC: 31 g/dL | RDW: %16.2 | PLT: 320 x10³/µL | WBC: 22.8 x10³/µL (Şiddetli Lökositoz) | Çomak Nötrofil: %18 (Sola Kayma) | Segmenter Nötrofil: %62 | Lenfosit: %15 | Monosit: %3 | Eozinofil: %2 | Bazofil: %0 | Plazma Fibrinojeni: 1250 mg/dL (Aşırı Yüksek) | PP/F Oranı: 6.3 (<10 Ağır Fibrinöz Yangı)."
            },
            "BIYOKIMYA_FULL": {
                "name": "Full Biyokimya, Enzim, Elektrolit & İz Eleman Paneli",
                "keywords": ["biyokimya", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "kreatinin", "glikoz", "bilirubin", "protein", "albümin", "globülin", "glutaraldehit", "saa", "histamin", "sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "magnezyum", "iz eleman", "demir", "bakır", "çinko", "selenyum"],
                "content": "AST: 185 U/L | GGT: 42 U/L | ALT: 32 U/L | ALP: 110 U/L | CK: 210 U/L | LDH: 850 U/L | Kardiyak Troponin I (cTnI): 1.85 ng/mL (Ağır Miyokard Hasarı) | BUN: 38 mg/dL | Kreatinin: 1.4 mg/dL | Glikoz: 68 mg/dL | Total Bilirubin: 1.1 mg/dL | Total Protein: 9.2 g/dL | Albümin: 2.6 g/dL | Globülin: 6.6 g/dL (A/G: 0.39) | Glutaraldehit Pıhtılaşma Süresi: 1.5 dk (Aşırı Hızlı) | SAA: 420 µg/mL | Na⁺: 136 mEq/L | K⁺: 3.8 mEq/L | Cl⁻: 94 mEq/L | Ca²⁺: 8.2 mg/dL | İnorganik P: 5.1 mg/dL | Mg²⁺: 2.1 mg/dL | Se: 0.12 µg/mL | Cu: 0.85 µg/mL."
            },
            "KAN_GAZI": {
                "name": "Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat", "hipoksi"],
                "content": "Kan pH: 7.31 | pO₂: 58 mmHg (Doku Hipoksisi) | pCO₂: 46 mmHg | HCO₃⁻: 21.2 mmol/L | Baz Açığı (BE): -4.2 mmol/L | Kan Laktat: 3.8 mmol/L (Metabolik Asidoz)."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "idrar tahlili", "dansite", "proteinüri", "glikozüri", "ketonüri", "bilirubinüri", "mikrohematüri", "sediment"],
                "content": "Spesifik Gravite: 1.022 | pH: 7.2 | Proteinüri: ++ | Glikoz: Negatif | Keton: Negatif | Bilirubin: Negatif | Mikrohematüri: + | Mikroskopik Sediment: Hyalin silendirler ve nükleer debris."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["ultrason", "usg", "röntgen", "grafi", "kültür", "perikardiyosentez", "ferroskop"],
                "content": "Abdominal/Torakal USG: Perikard kasesinde 8 cm pürülan-fibrinöz sıvı ve gaz ekojenitesi. Ferroskop: POZİTİF (metalik cisim sinyali). Perikardiyosentez: Kokulu pürülan eksudat, kültürde Trueperella pyogenes üremesi."
            }
        }
    },
    "Vaka B (Yonca)": {
        "kod": "VAKA_B",
        "sikayet": "Tekrarlayan yüksek ateş, belirgin süt verimi düşüşü, sol ön bacakta intermittent topallık ve kilo kaybı.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "ot", "silaj", "mısır"],
                "content": "Standart süt sığırı karma rasyonu verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "yer"],
                "content": "Ova işletmesindedir, yayla nakli yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "metritis", "mastitis", "öykü"],
                "content": "3 hafta önce kronik purulent metritis ve mastitis tedavisi görmüştür."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "anoreksi"],
                "content": "Ateşli dönemlerde komple anoreksi."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "mukoza", "topallık"],
                "content": "Vücut Sıcaklığı: 40.2 °C | Kalp Frekansı: 108 atım/dk | Solunum: 38/dk | Mukozalar: Peteşiyal kanamalı soluk | Vena jugularis dolgun, presistolik yalancı jugular nabız +, sol ön bacakta septik embolik topallık."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "üfürüm", "oskültasyon", "çalkantı"],
                "content": "Kalp Oskültasyonu: Triküspit kapak odağında belirgin sistolik üfürüm (Grade 4/6). Çamaşır makinesi sesi veya su çalkantısı YOKTUR."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı"],
                "content": "Retikulum ağrı testlerinin tamamı NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Paneli (18 Parametre)",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "rbc", "hb", "pcv", "plt", "fibrinojen", "pp/f"],
                "content": "RBC: 4.8 x10⁶/µL | Hb: 7.8 g/dL | PCV: %24 | MCV: 50 fL | MCH: 16.2 pg | MCHC: 32 g/dL | RDW: %17.0 | PLT: 110 x10³/µL (Trombositopeni) | WBC: 26.5 x10³/µL (Şiddetli Lökositoz) | Çomak: %22 | Segmenter: %58 | Lenfosit: %16 | Monosit: %3 | Eozinofil: %1 | Fibrinojen: 1080 mg/dL | PP/F: 7.1."
            },
            "BIYOKIMYA_FULL": {
                "name": "Full Biyokimya, Enzim, Elektrolit & İz Eleman Paneli",
                "keywords": ["biyokimya", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "kreatinin", "glikoz", "protein", "albümin", "globülin", "glutaraldehit", "saa", "sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "AST: 160 U/L | GGT: 38 U/L | ALT: 28 U/L | ALP: 98 U/L | CK: 180 U/L | LDH: 720 U/L | cTnI: 2.40 ng/mL (Ağır Endokard Zedelenmesi) | BUN: 32 mg/dL | Kreatinin: 1.3 mg/dL | Glikoz: 72 mg/dL | Total Protein: 8.8 g/dL | Albümin: 2.4 g/dL | Globülin: 6.4 g/dL | Glutaraldehit: 2.0 dk | SAA: 380 µg/mL | Na⁺: 138 mEq/L | K⁺: 4.1 mEq/L | Cl⁻: 98 mEq/L | Ca²⁺: 8.4 mg/dL | P: 4.8 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "pH: 7.34 | pO₂: 62 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 22.0 mmol/L | BE: -2.8 mmol/L | Laktat: 2.6 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "mikrohematüri"],
                "content": "Spesifik Gravite: 1.020 | pH: 7.0 | Proteinüri: + | Mikrohematüri: ++ (Septik renal mikroemboli)."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["ekokardiyografi", "ultrason", "kültür", "bakteri"],
                "content": "Ekokardiyografi: Triküspit kapak üzerinde 3.5 cm vejetatif karnabahar kitle. Kan Kültürü: Trueperella pyogenes üremesi. Ferroskop: Negatif."
            }
        }
    },
    "Vaka C (Zümrüt)": {
        "kod": "VAKA_C",
        "sikayet": "Gerdan ve alt göğüste yaygın soğuk ödem, nefes darlığı, halsizlik. Ateş tamamen normaldir.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "ot"],
                "content": "Mera ve kaba yem ağırlıklı beslenmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "yükseklik", "dağ", "sevk"],
                "content": "3 hafta önce 2400 metre yükseklikteki dağ yaylasına sevk edilmiştir (Hipobarik Hipoksi öyküsü)."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "öykü"],
                "content": "Enfeksiyöz hastalık veya yangı öyküsü yoktur."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem"],
                "content": "Hiporeksi (durgunluk ve hipoksiye bağlı iştah azalması)."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "mukoza", "ödem"],
                "content": "Vücut Sıcaklığı: 38.5 °C (TAMAMEN NORMAL) | Kalp Frekansı: 96 atım/dk | Solunum: 46/dk | Mukozalar: Siyanotik mavitırak | Gerdanda yaygın soğuk hamur ödem."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "üfürüm", "çalkantı", "oskültasyon"],
                "content": "Kalp Oskültasyonu: Hiperdinamik güçlü kalp sesleri. Üfürüm veya su çalkantı sesi YOKTUR."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı"],
                "content": "Retikulum ağrı testleri NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Paneli (18 Parametre)",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "rbc", "hb", "pcv", "plt", "fibrinojen", "pp/f"],
                "content": "RBC: 10.8 x10⁶/µL (Aşırı Kompenzatuvar Polisitemi) | Hb: 17.5 g/dL | PCV: %54 (Aşırı Yüksek) | MCV: 50 fL | MCH: 16.2 pg | MCHC: 32.4 g/dL | RDW: %14.2 | PLT: 280 x10³/µL | WBC: 7.2 x10³/µL (TAMAMEN NORMAL, Lökositoz Yok!) | Çomak: %2 | Segmenter: %60 | Lenfosit: %32 | Monosit: %4 | Eozinofil: %2 | Fibrinojen: 310 mg/dL (NORMAL) | PP/F: 22.8 (Yangı Yok)."
            },
            "BIYOKIMYA_FULL": {
                "name": "Full Biyokimya, Enzim, Elektrolit & İz Eleman Paneli",
                "keywords": ["biyokimya", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "kreatinin", "glikoz", "protein", "albümin", "globülin", "glutaraldehit", "saa", "sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "AST: 68 U/L | GGT: 18 U/L | ALT: 19 U/L | ALP: 65 U/L | CK: 90 U/L | LDH: 380 U/L | cTnI: 0.12 ng/mL | BUN: 18 mg/dL | Kreatinin: 0.9 mg/dL | Glikoz: 65 mg/dL | Total Protein: 7.1 g/dL | Albümin: 3.2 g/dL | Globülin: 3.9 g/dL | Glutaraldehit: 12 dk (Pıhtılaşma yok/Normal) | SAA: 12 µg/mL | Na⁺: 140 mEq/L | K⁺: 4.2 mEq/L | Cl⁻: 102 mEq/L | Ca²⁺: 9.2 mg/dL | P: 5.4 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat", "hipoksi"],
                "content": "pH: 7.36 | pO₂: 48 mmHg (Şiddetli Doku Hipoksisi / Hipobarik Hipoksi) | pCO₂: 48 mmHg | HCO₃⁻: 25.5 mmol/L | BE: +0.5 mmol/L | Laktat: 2.1 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite"],
                "content": "Spesifik Gravite: 1.025 | pH: 7.5 | Protein: Negatif | Sediment temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["ekokardiyografi", "ultrason", "kültür"],
                "content": "Ekokardiyografi: Sağ ventrikül serbest duvar kalınlaşması (Sağ Ventrikül Hipertrofisi) ve pulmoner arter dilatasyonu. Perikardiyosentez: Steril."
            }
        }
    },
    "Vaka D (Yiğit)": {
        "kod": "VAKA_D",
        "sikayet": "Ağız ve burundan fışkırır tarzda taze parlak kırmızı kan gelmesi (hemoptizi) ve katran siyahı dışkı (melena).",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besi", "mısır", "arpa", "asidoz"],
                "content": "18 aylık besi danasıdır. Yoğun mısır/arpa kırması ağırlıklı kaba yemi yetersiz rasyon verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla"],
                "content": "Besi padoğunda barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "asidoz", "rumenitis", "şişkinlik"],
                "content": "Geçmişinde tekrarlayan akut/subakut rumen asidozu (yem çarpması) öyküsü vardır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "anoreksi"],
                "content": "Şok ve akut kan kaybı nedeniyle komplet anoreksi."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "mukoza", "hemoptizi", "melena"],
                "content": "Vücut Sıcaklığı: 39.2 °C | Kalp Frekansı: 118 atım/dk | Solunum: 52/dk | Ağız/Burun: Köpüklü taze kırmızı kan fışkırması (Hemoptizi) | Mukozalar: Bembeyaz | CRT: 4.0 sn | Dışkı: Katran siyahı (Melena)."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "akciğer", "rall"],
                "content": "Kalp: Taşikardik zayıf düştü sesleri. Akciğer: Yaygın kaba raller ve hışırtı."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı"],
                "content": "Retikulum ağrı testleri NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Paneli (18 Parametre)",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "rbc", "hb", "pcv", "plt", "fibrinojen", "pp/f", "anemi"],
                "content": "RBC: 2.1 x10⁶/µL (Kritik Kan Kaybı Anemisi) | Hb: 4.2 g/dL | PCV: %12 (Acil Transfüzyon Eşiği!) | MCV: 52 fL | MCH: 16.0 pg | MCHC: 30.8 g/dL | RDW: %18.5 | PLT: 85 x10³/µL | WBC: 21.5 x10³/µL | Çomak: %15 | Segmenter: %65 | Lenfosit: %15 | Monosit: %4 | Eozinofil: %1 | Fibrinojen: 1050 mg/dL | PP/F: 7.23."
            },
            "BIYOKIMYA_FULL": {
                "name": "Full Biyokimya, Enzim, Elektrolit & İz Eleman Paneli",
                "keywords": ["biyokimya", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "kreatinin", "glikoz", "bilirubin", "protein", "albümin", "globülin", "glutaraldehit", "saa", "sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "AST: 210 U/L (Karaciğer Hasarı) | GGT: 68 U/L | ALT: 45 U/L | ALP: 140 U/L | CK: 160 U/L | LDH: 920 U/L | cTnI: 0.28 ng/mL | BUN: 42 mg/dL | Kreatinin: 1.6 mg/dL | Glikoz: 88 mg/dL | Total Bilirubin: 1.8 mg/dL | Total Protein: 5.4 g/dL | Albümin: 1.8 g/dL (Hipoalbüminemi) | Globülin: 3.6 g/dL | Glutaraldehit: 2.5 dk | SAA: 310 µg/mL | Na⁺: 134 mEq/L | K⁺: 3.5 mEq/L | Cl⁻: 92 mEq/L | Ca²⁺: 7.8 mg/dL | P: 4.2 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "pH: 7.24 | pO₂: 52 mmHg | pCO₂: 50 mmHg | HCO₃⁻: 18.5 mmol/L | BE: -6.2 mmol/L | Laktat: 4.2 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "melena"],
                "content": "Spesifik Gravite: 1.018 | pH: 6.8 | Proteinüri: ++ | Dışkıda gizli kan +++."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["ultrason", "usg", "karaciğer", "apse", "trombüs", "arter"],
                "content": "Abdominal USG: Karaciğerde 6 cm kılıflı apse odağı ve Vena Cava Caudalis lümeninde lüminal trombüs ekojenitesi. Torakal USG: Pulmoner arter anevrizması."
            }
        }
    },
    "Vaka E (Kudret)": {
        "kod": "VAKA_E",
        "sikayet": "Baş, göz çevresi ve boyun bölgesinde dairesel, grimsi-beyaz kireçimsi kabuklanma ve tüy dökülmesi.",
        "makroskopik_gorsel": {"fig": "Figure 1.2-1", "title": "Klinik Mantar Lezyonu", "file": "gorseller/figure_1_2_1.jpg"},
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle"],
                "content": "Kalabalık ve nemli dana padoğunda standart buzağı büyütme yemi ile beslenmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "barınak"],
                "content": "Nemsiz ve güneş görmeyen kapalı ağıl ortamı."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "öykü"],
                "content": "Sistemik bir hastalık öyküsü yoktur."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem"],
                "content": "İştahı ve neşesi yerindedir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "mukoza", "deri", "kabuk"],
                "content": "Vücut Sıcaklığı: 38.8 °C | Kalp: 78/dk | Solunum: 24/dk | Mukozalar: Pembe | Baş, göz çevresi ve boyunda kaşıntısız dairesel kireçimsi gri kabuklu lezyonlar."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "akciğer"],
                "content": "Kalp ve akciğer sesleri tamamen normaldir."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers"],
                "content": "Ağrı testleri negatif."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Paneli (18 Parametre)",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "rbc", "hb", "pcv", "plt", "fibrinojen", "pp/f"],
                "content": "RBC: 6.2 x10⁶/µL | Hb: 11.2 g/dL | PCV: %34 | MCV: 52 fL | MCH: 16.5 pg | MCHC: 32.0 g/dL | RDW: %14.8 | PLT: 290 x10³/µL | WBC: 8.5 x10³/µL (NORMAL) | Çomak: %2 | Segmenter: %58 | Lenfosit: %34 | Monosit: %4 | Eozinofil: %2 | Fibrinojen: 340 mg/dL | PP/F: 18.2."
            },
            "BIYOKIMYA_FULL": {
                "name": "Full Biyokimya, Enzim, Elektrolit & İz Eleman Paneli",
                "keywords": ["biyokimya", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "kreatinin", "glikoz", "protein", "albümin", "globülin", "glutaraldehit", "saa", "sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "AST: 48 U/L | GGT: 22 U/L | ALT: 18 U/L | ALP: 80 U/L | CK: 95 U/L | LDH: 320 U/L | cTnI: 0.05 ng/mL | BUN: 16 mg/dL | Kreatinin: 0.8 mg/dL | Glikoz: 70 mg/dL | Total Protein: 6.8 g/dL | Albümin: 3.3 g/dL | Globülin: 3.5 g/dL | Glutaraldehit: 10 dk | SAA: 8 µg/mL | Na⁺: 139 mEq/L | K⁺: 4.4 mEq/L | Cl⁻: 101 mEq/L | Ca²⁺: 9.4 mg/dL | P: 5.8 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3"],
                "content": "pH: 7.40 | pO₂: 88 mmHg | pCO₂: 40 mmHg | HCO₃⁻: 24.0 mmol/L | BE: 0.0 mmol/L | Laktat: 1.0 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite"],
                "content": "Spesifik Gravite: 1.025 | pH: 7.8 | Protein: Negatif | Sediment temiz."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "Deri Kazıntısı & Mikroskopik İnceleme",
                "keywords": ["mikroskop", "mikroskopi", "kazıntı", "deri kazıntısı", "koh", "mantar", "artrospor", "lam"],
                "gorsel": {"fig": "Figure 1.2-11", "title": "Mikroskopik Mantar Sporu", "file": "gorseller/figure_1_2_11.jpg"},
                "content": "%10 KOH ile hazırlanan deri kazıntısında kıl etrafında küresel Trichophyton verrucosum ektotriks artrospor zincirleri belirgin olarak izlenmiştir."
            }
        }
    },
    "Vaka F (Nazar)": {
        "kod": "VAKA_F",
        "sikayet": "Kulak kepçesi, boyun ve sırtta şiddetli kaşıntı, derinin fil derisi gibi kalınlaşması (likenifikasyon) ve döküntü.",
        "makroskopik_gorsel": {"fig": "Figure 1.3-13", "title": "Klinik Uyuz Lezyonu", "file": "gorseller/figure_1_3_13.jpg"},
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem"],
                "content": "Kış döneminde yetersiz kaba yem ile besleme."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla"],
                "content": "Bakımsız ağıl ortamı."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş"],
                "content": "Geçmişinde paraziter ilaçlama yapılmamıştır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah"],
                "content": "Şiddetli kaşıntı ve huzursuzluk nedeniyle iştah azalmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "mukoza", "kaşıntı", "likenifikasyon"],
                "content": "Vücut Sıcaklığı: 39.0 °C | Kalp: 82/dk | Solunum: 28/dk | Kulak, boyun ve sırtta şiddetli pruritus (kaşıntı), eksforyasyon ve likenifikasyon."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "akciğer"],
                "content": "Kalp ve akciğer sesleri normal."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers"],
                "content": "Ağrı testleri negatif."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Paneli (18 Parametre)",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "rbc", "hb", "pcv", "plt", "eozinofil", "fibrinojen", "pp/f"],
                "content": "RBC: 5.8 x10⁶/µL | Hb: 10.4 g/dL | PCV: %31 | MCV: 51 fL | MCH: 16.0 pg | MCHC: 31.8 g/dL | RDW: %15.2 | PLT: 310 x10³/µL | WBC: 14.2 x10³/µL (Eozinofili %14) | Çomak: %4 | Segmenter: %50 | Lenfosit: %30 | Monosit: %2 | Eozinofil: %14 (Paraziter Reaksiyon) | Fibrinojen: 480 mg/dL | PP/F: 14.2."
            },
            "BIYOKIMYA_FULL": {
                "name": "Full Biyokimya, Enzim, Elektrolit & İz Eleman Paneli",
                "keywords": ["biyokimya", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "kreatinin", "glikoz", "protein", "albümin", "globülin", "glutaraldehit", "saa", "sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "AST: 52 U/L | GGT: 24 U/L | ALT: 21 U/L | ALP: 85 U/L | CK: 110 U/L | LDH: 360 U/L | cTnI: 0.06 ng/mL | BUN: 18 mg/dL | Kreatinin: 0.9 mg/dL | Glikoz: 68 mg/dL | Total Protein: 7.2 g/dL | Albümin: 3.1 g/dL | Globülin: 4.1 g/dL | Glutaraldehit: 7 dk | SAA: 45 µg/mL | Na⁺: 138 mEq/L | K⁺: 4.2 mEq/L | Cl⁻: 99 mEq/L | Ca²⁺: 9.0 mg/dL | P: 5.2 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3"],
                "content": "pH: 7.39 | pO₂: 85 mmHg | pCO₂: 41 mmHg | HCO₃⁻: 23.8 mmol/L | BE: -0.2 mmol/L | Laktat: 1.2 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite"],
                "content": "Spesifik Gravite: 1.022 | pH: 7.6 | Protein: Negatif | Sediment temiz."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "Derin Deri Kazıntısı & Akar Mikroskopisi",
                "keywords": ["mikroskop", "mikroskopi", "kazıntı", "deri kazıntısı", "akar", "uyuz", "mineral yağ", "sarcoptes", "lam"],
                "gorsel": {"fig": "Figure 1.3-18", "title": "Mikroskopik Sarcoptes Scabiei Akari", "file": "gorseller/figure_1_3_18.jpg"},
                "content": "Kapiller kanama görülünceye kadar alınan derin deri kazıntısında mineral yağ altında tespit edilen canlı ergin Sarcoptes scabiei var. bovis akarları ve oval yumurtaları izlenmiştir."
            }
        }
    },
    "Vaka G (Çiçek)": {
        "kod": "VAKA_G",
        "sikayet": "Güneşe çıkınca boyun, omuz ve sırt bölgesindeki beyaz (pigmentsiz) deride eritem, hamur ödemi, tabaka halinde soyulma ve dokunmaya karşı şiddetli hipersensitivite/ağrı.",
        "makroskopik_gorsel": {"fig": "Figure 1.7-35", "title": "Hepatojen Fotosensitizasyon (Pigmentsiz Deri Nekrozu)", "file": "gorseller/figure_1_7_35.jpg"},
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "ot", "mera", "klorofil", "toksik bitki"],
                "content": "Klorofilden zengin taze yeşil ot merasında otlatılmaktadır. Merada hepatotoksik bitkilerin bulunduğu bilinmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "güneş"],
                "content": "Güneş ışığına yoğun maruz kalınan açık mera ortamı."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "karaciğer", "fasiyoloz"],
                "content": "Geçmişinde kronik karaciğer kelebeği (Fasciola hepatica) öyküsü vardır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "ağrı"],
                "content": "Güneşte boyun ve sırt derisindeki ağrı nedeniyle merada otlamayı bırakıp gölgeye kaçmaktadır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "mukoza", "güneş", "boyun", "ödem", "nekroz", "hipersensitivite"],
                "content": "Vücut Sıcaklığı: 39.4 °C | Kalp: 88/dk | Solunum: 32/dk | Mukozalar: İkterik (sarılık +) | YALNIZCA BOYUN, OMUZ VE SIRT BÖLGESİNDEKİ PİGMENTSIZ (BEYAZ) DERİDE hamur ödemi, soyulma, nekroz ve dokunmaya karşı şiddetli hipersensitivite/ağrı. Siyah deriler tamamen sağlamdır!"
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "akciğer"],
                "content": "Kalp ve akciğer sesleri normal."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "dokunma"],
                "content": "Boyun ve sırt derisine temas edildiğinde şiddetli hiperestezi/ağrı reaksiyonu."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Paneli (18 Parametre)",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "rbc", "hb", "pcv", "plt", "fibrinojen", "pp/f"],
                "content": "RBC: 5.2 x10⁶/µL | Hb: 9.2 g/dL | PCV: %28 | MCV: 51 fL | MCH: 15.8 pg | MCHC: 31.0 g/dL | RDW: %16.0 | PLT: 260 x10³/µL | WBC: 16.8 x10³/µL (Lökositoz) | Çomak: %8 | Segmenter: %64 | Lenfosit: %22 | Monosit: %4 | Eozinofil: %2 | Fibrinojen: 620 mg/dL | PP/F: 11.2."
            },
            "BIYOKIMYA_FULL": {
                "name": "Full Biyokimya, Enzim, Elektrolit & İz Eleman Paneli",
                "keywords": ["biyokimya", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "kreatinin", "glikoz", "bilirubin", "filloeritrin", "protein", "albümin", "globülin", "glutaraldehit", "saa", "sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "AST: 280 U/L (Karaciğer Hasarı) | GGT: 185 U/L (Ağır Kolestaz!) | ALT: 58 U/L | ALP: 310 U/L | CK: 140 U/L | LDH: 950 U/L | cTnI: 0.10 ng/mL | BUN: 24 mg/dL | Kreatinin: 1.1 mg/dL | Glikoz: 62 mg/dL | Total Bilirubin: 4.8 mg/dL (Direkt 3.2 mg/dL) | Serum Filloeritrin Düzeyi: 0.82 µg/mL (Aşırı Yüksek Fotodinamik Ajan) | Total Protein: 6.2 g/dL | Albümin: 2.2 g/dL (Hipoalbüminemi) | Globülin: 4.0 g/dL | Glutaraldehit: 4 dk | SAA: 180 µg/mL | Na⁺: 135 mEq/L | K⁺: 3.6 mEq/L | Cl⁻: 95 mEq/L | Ca²⁺: 8.0 mg/dL | P: 4.5 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3"],
                "content": "pH: 7.33 | pO₂: 78 mmHg | pCO₂: 44 mmHg | HCO₃⁻: 20.5 mmol/L | BE: -4.0 mmol/L | Laktat: 2.8 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "bilirubinüri", "çay"],
                "content": "Spesifik Gravite: 1.030 | pH: 8.1 | Bilirubinüri: +++ (Koyu Çay / Bira Rengi İdrar!) | Proteinüri: + | Ürobilinojen: Yüksek."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["ultrason", "usg", "karaciğer", "safra"],
                "content": "Abdominal USG: Karaciğer parankiminde diffüz ekojenite artışı, safra kesesinde geniştetilmiş lümen ve duvar kalınlaşması."
            }
        }
    },
    "Vaka H (Ateş)": {
        "kod": "VAKA_H",
        "sikayet": "Gövde, boyun ve omuz derisinde aniden beliren ceviz büyüklüğünde kabarık ödemli plaklar ve huzursuzluk.",
        "makroskopik_gorsel": {"fig": "Figure 1.5-1", "title": "Akut Ürtiker (Ödem Plakları)", "file": "gorseller/figure_1_5_1.jpg"},
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "yem değişimi"],
                "content": "Aniden yeni bir protein yemi rasyona eklenmiştir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla"],
                "content": "Açık padok."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "enjeksiyon"],
                "content": "2 saat önce parenteral ilaç enjeksiyonu yapılmıştır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah"],
                "content": "Huzursuzluk nedeniyle yem yemeyi bırakmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "mukoza", "ürtiker", "plak", "ödem"],
                "content": "Vücut Sıcaklığı: 38.9 °C | Kalp: 86/dk | Solunum: 30/dk | Gövde ve boyunda aniden beliren basmakla çukurlaşan kabarık dairesel ödem plakları (urtica/wheals)."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "akciğer"],
                "content": "Kalp ve akciğer sesleri normal."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers"],
                "content": "Ağrı testleri negatif."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Paneli (18 Parametre)",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "rbc", "hb", "pcv", "plt", "eozinofil", "fibrinojen", "pp/f"],
                "content": "RBC: 6.4 x10⁶/µL | Hb: 11.8 g/dL | PCV: %35 | MCV: 50 fL | MCH: 16.2 pg | MCHC: 32.2 g/dL | RDW: %14.5 | PLT: 340 x10³/µL | WBC: 12.8 x10³/µL (Eozinofili %18) | Çomak: %2 | Segmenter: %48 | Lenfosit: %30 | Monosit: %2 | Eozinofil: %18 (Tip I Alerjik) | Fibrinojen: 380 mg/dL | PP/F: 16.8."
            },
            "BIYOKIMYA_FULL": {
                "name": "Full Biyokimya, Enzim, Elektrolit & İz Eleman Paneli",
                "keywords": ["biyokimya", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "kreatinin", "glikoz", "histamin", "protein", "albümin", "globülin", "glutaraldehit", "saa", "sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "AST: 50 U/L | GGT: 20 U/L | ALT: 18 U/L | ALP: 75 U/L | CK: 100 U/L | LDH: 340 U/L | cTnI: 0.04 ng/mL | BUN: 15 mg/dL | Kreatinin: 0.8 mg/dL | Glikoz: 78 mg/dL | Serum Histamin Düzeyi: 4.8 µg/mL (Aşırı Yüksek) | Total Protein: 7.0 g/dL | Albümin: 3.4 g/dL | Globülin: 3.6 g/dL | Glutaraldehit: 9 dk | SAA: 15 µg/mL | Na⁺: 139 mEq/L | K⁺: 4.3 mEq/L | Cl⁻: 100 mEq/L | Ca²⁺: 9.2 mg/dL | P: 5.5 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3"],
                "content": "pH: 7.41 | pO₂: 86 mmHg | pCO₂: 39 mmHg | HCO₃⁻: 24.5 mmol/L | BE: +0.5 mmol/L | Laktat: 1.1 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite"],
                "content": "Spesifik Gravite: 1.024 | pH: 7.6 | Protein: Negatif | Sediment temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["ultrason", "usg"],
                "content": "Deri USG'sinde dermiste subkutan kutanöz ödem birikimi."
            }
        }
    },
    "Vaka I (Fırtına)": {
        "kod": "VAKA_I",
        "sikayet": "Nefes alırken duyulan ıslık/düdük sesi (stridor), ağız açık soluma ve başı ileri uzatma.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem"],
                "content": "Standart besi rasyonu."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "nakil", "sevk"],
                "content": "2 gün önce tozlu kamyonla uzun yol nakli yapılmıştır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş"],
                "content": "Nakil öncesi sağlıklı."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yutma"],
                "content": "Solunum darlığı ve larenks ağrısı nedeniyle yem yemeyi reddediyor."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "stridor", "solunum"],
                "content": "Vücut Sıcaklığı: 39.5 °C | Kalp: 92/dk | Solunum: 40/dk | Belirgin inspiratorik stridor. Larenks üzerine dokunulduğunda şiddetli öksürük ve ağrı refleksi."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "akciğer"],
                "content": "Akciğer oskültasyonu TAMAMEN NORMAL veziküler sestir (akciğer parankimi sağlamdır)."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["larenks", "trakeal", "refleks"],
                "content": "Larenks ve trakea palpasyonunda şiddetli provokatif ağrı ve öksürük krizi."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Paneli (18 Parametre)",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "rbc", "hb", "pcv", "plt", "fibrinojen", "pp/f"],
                "content": "RBC: 6.1 x10⁶/µL | Hb: 11.0 g/dL | PCV: %33 | MCV: 51 fL | MCH: 16.2 pg | MCHC: 32.0 g/dL | RDW: %14.8 | PLT: 280 x10³/µL | WBC: 11.2 x10³/µL (Hafif Lökositoz) | Çomak: %4 | Segmenter: %60 | Lenfosit: %30 | Monosit: %4 | Eozinofil: %2 | Fibrinojen: 420 mg/dL | PP/F: 15.5."
            },
            "BIYOKIMYA_FULL": {
                "name": "Full Biyokimya, Enzim, Elektrolit & İz Eleman Paneli",
                "keywords": ["biyokimya", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "kreatinin", "glikoz", "protein", "albümin", "globülin", "glutaraldehit", "saa", "sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "AST: 55 U/L | GGT: 22 U/L | ALT: 20 U/L | ALP: 82 U/L | CK: 105 U/L | LDH: 350 U/L | cTnI: 0.05 ng/mL | BUN: 17 mg/dL | Kreatinin: 0.9 mg/dL | Glikoz: 74 mg/dL | Total Protein: 7.1 g/dL | Albümin: 3.3 g/dL | Globülin: 3.8 g/dL | Glutaraldehit: 8 dk | SAA: 25 µg/mL | Na⁺: 138 mEq/L | K⁺: 4.1 mEq/L | Cl⁻: 99 mEq/L | Ca²⁺: 9.1 mg/dL | P: 5.3 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3"],
                "content": "pH: 7.38 | pO₂: 82 mmHg (Akciğerler açık olduğu için gaz değişimi normal) | pCO₂: 42 mmHg | HCO₃⁻: 23.5 mmol/L | BE: -0.5 mmol/L | Laktat: 1.4 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite"],
                "content": "Spesifik Gravite: 1.022 | pH: 7.5 | Protein: Negatif | Sediment temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["laringoskopi", "endoskopi", "ultrason"],
                "content": "Laringoskopi: Larenks mukozasında ve arytenoid kıkırdaklarda şiddetli ödem ve hava yolu darlığı."
            }
        }
    },
    "Vaka J (Şahin)": {
        "kod": "VAKA_J",
        "sikayet": "Tek taraflı kötü kokulu pürülan burun akıntısı, başı yana eğme ve göz altında şişlik.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem"],
                "content": "Standart yemleme."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım"],
                "content": "Sabit işletme."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "dehorning", "boynuz"],
                "content": "1 ay önce acemi kişilerce boynuz kesme (dehorning) yapılmıştır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah"],
                "content": "Baş ağrısı nedeniyle iştah azalmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "burun akıntısı", "sinüs"],
                "content": "Vücut Sıcaklığı: 39.1 °C | Kalp: 84/dk | Solunum: 26/dk | Sol burun deliğinden purulent kokulu akıntı."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "akciğer"],
                "content": "Kalp ve akciğer sesleri normal."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sinüs", "perküsyon", "matite"],
                "content": "Frontal sinüs üzerine perküsyonda matite (dullness) ve ağrı reaksiyonu."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Paneli (18 Parametre)",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "rbc", "hb", "pcv", "plt", "fibrinojen", "pp/f"],
                "content": "RBC: 5.6 x10⁶/µL | Hb: 10.1 g/dL | PCV: %30 | MCV: 51 fL | MCH: 16.0 pg | MCHC: 31.5 g/dL | RDW: %15.5 | PLT: 320 x10³/µL | WBC: 18.5 x10³/µL (Kronik Lökositoz) | Çomak: %10 | Segmenter: %62 | Lenfosit: %22 | Monosit: %4 | Eozinofil: %2 | Fibrinojen: 780 mg/dL | PP/F: 9.8."
            },
            "BIYOKIMYA_FULL": {
                "name": "Full Biyokimya, Enzim, Elektrolit & İz Eleman Paneli",
                "keywords": ["biyokimya", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "kreatinin", "glikoz", "protein", "albümin", "globülin", "glutaraldehit", "saa", "sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "AST: 62 U/L | GGT: 25 U/L | ALT: 22 U/L | ALP: 88 U/L | CK: 115 U/L | LDH: 380 U/L | cTnI: 0.06 ng/mL | BUN: 20 mg/dL | Kreatinin: 1.0 mg/dL | Glikoz: 70 mg/dL | Total Protein: 8.2 g/dL | Albümin: 2.8 g/dL | Globülin: 5.4 g/dL (Hipergamaglobülinemi) | Glutaraldehit: 3 dk | SAA: 140 µg/mL | Na⁺: 137 mEq/L | K⁺: 4.0 mEq/L | Cl⁻: 97 mEq/L | Ca²⁺: 8.8 mg/dL | P: 5.0 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3"],
                "content": "pH: 7.37 | pO₂: 84 mmHg | pCO₂: 41 mmHg | HCO₃⁻: 23.0 mmol/L | BE: -1.0 mmol/L | Laktat: 1.3 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite"],
                "content": "Spesifik Gravite: 1.021 | pH: 7.4 | Protein: + | Sediment temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["röntgen", "grafi", "ultrason", "kültür"],
                "content": "Kranial Grafi: Frontal sinüs alanında opasite artışı ve boynuz kökü perfore kanalı. Kültür: Trueperella pyogenes üremesi."
            }
        }
    },
    "Vaka K (Rüzgar)": {
        "kod": "VAKA_K",
        "sikayet": "Atın baş öne eğildiğinde her iki burun deliğinden koyu irin akması, parotid bölgede şişlik ve yutma güçlüğü.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "yulaf", "ot"],
                "content": "Yulaf ve yonca otu ile beslenmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "tavla"],
                "content": "Harada barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "gurm", "boğaz"],
                "content": "1 ay önce Strep. equi enfeksiyonu (Gurm) geçirmiştir."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yutma", "disfaji"],
                "content": "Disfaji (yutma ağrısı ve güçlüğü) nedeniyle yem tüketememektedir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "burun akıntısı", "parotid"],
                "content": "Vücut Sıcaklığı: 39.3 °C | Kalp: 54/dk | Solunum: 20/dk | Mukozalar: Hiperemik | Parotid bölgede bilateral ağrılı şişlik, baş öne eğilince bilateral pürülan akıntı."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "akciğer"],
                "content": "Kalp ve akciğer oskültasyonu normal."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["parotid", "hava kesesi"],
                "content": "Hava kesesi bölgesi palpasyonunda şiddetli ağrı ve başı uzatma reaksiyonu."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Paneli (18 Parametre)",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "rbc", "hb", "pcv", "plt", "fibrinojen", "pp/f"],
                "content": "RBC: 7.2 x10⁶/µL | Hb: 12.4 g/dL | PCV: %36 | MCV: 48 fL | MCH: 16.5 pg | MCHC: 33.0 g/dL | RDW: %14.0 | PLT: 350 x10³/µL | WBC: 21.0 x10³/µL (Lökositoz) | Çomak: %12 | Segmenter: %65 | Lenfosit: %18 | Monosit: %3 | Eozinofil: %2 | Fibrinojen: 850 mg/dL | PP/F: 8.2."
            },
            "BIYOKIMYA_FULL": {
                "name": "Full Biyokimya, Enzim, Elektrolit & İz Eleman Paneli",
                "keywords": ["biyokimya", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "kreatinin", "glikoz", "protein", "albümin", "globülin", "glutaraldehit", "saa", "sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "AST: 110 U/L | GGT: 30 U/L | ALT: 25 U/L | ALP: 95 U/L | CK: 180 U/L | LDH: 450 U/L | cTnI: 0.08 ng/mL | BUN: 22 mg/dL | Kreatinin: 1.1 mg/dL | Glikoz: 82 mg/dL | Total Protein: 8.6 g/dL | Albümin: 2.7 g/dL | Globülin: 5.9 g/dL | Glutaraldehit: 2.5 dk | SAA: 260 µg/mL | Na⁺: 136 mEq/L | K⁺: 3.8 mEq/L | Cl⁻: 96 mEq/L | Ca²⁺: 9.0 mg/dL | P: 4.8 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3"],
                "content": "pH: 7.35 | pO₂: 80 mmHg | pCO₂: 43 mmHg | HCO₃⁻: 22.5 mmol/L | BE: -2.0 mmol/L | Laktat: 1.8 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite"],
                "content": "Spesifik Gravite: 1.028 | pH: 7.8 | Protein: + | Sediment temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["endoskopi", "kültür", "guttural"],
                "content": "Endoskopi: Hava kesesi ostiyumundan pürülan eksudat drenajı ve kese içinde taşlaşmış pürülan kitleler (Chondroids). Kültür: Streptococcus equi subsp. equi üremesi."
            }
        }
    },
    "Vaka L (Poyraz)": {
        "kod": "VAKA_L",
        "sikayet": "Atın dinlenme halindeyken aniden ağız ve burun deliklerinden taze parlak kırmızı kan gelmesi (epistaksis).",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "saman", "küf"],
                "content": "Nemli küflü saman balyası verilmiştir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım"],
                "content": "Kapalı hara padoğu."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "öksürük"],
                "content": "Geçmişinde hafif kronik öksürük ve burun kanaması damlaları görülmüştür."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "kan"],
                "content": "Hemorajik şok nedeniyle yem reddi."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "mukoza", "kan", "epistaksis"],
                "content": "Vücut Sıcaklığı: 38.6 °C | Kalp: 68/dk (Taşikardik zayıf) | Solunum: 24/dk | Mukozalar: Bembeyaz soluk | Ağız ve burundan spontan taze kırmızı kan gelmesi."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "akciğer"],
                "content": "Kalp sesleri hızlı ve zayıf. Akciğerlerde kan yutmaya bağlı hışırtı sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["hava kesesi"],
                "content": "Hava kesesi bölgesi palpasyonunda huzursuzluk."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Paneli (18 Parametre)",
                "keywords": ["hemogram", "cbc", "kan sayımı", "wbc", "rbc", "hb", "pcv", "plt", "fibrinojen", "pp/f", "anemi"],
                "content": "RBC: 3.8 x10⁶/µL (Şiddetli Akut Kan Kaybı Anemisi) | Hb: 6.5 g/dL | PCV: %20 (Acil Kan Nakli Adayı!) | MCV: 49 fL | MCH: 16.1 pg | MCHC: 32.5 g/dL | RDW: %16.8 | PLT: 140 x10³/µL | WBC: 15.8 x10³/µL | Çomak: %8 | Segmenter: %62 | Lenfosit: %24 | Monosit: %4 | Eozinofil: %2 | Fibrinojen: 620 mg/dL | PP/F: 11.0."
            },
            "BIYOKIMYA_FULL": {
                "name": "Full Biyokimya, Enzim, Elektrolit & İz Eleman Paneli",
                "keywords": ["biyokimya", "enzim", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "bun", "kreatinin", "glikoz", "protein", "albümin", "globülin", "glutaraldehit", "saa", "sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "AST: 95 U/L | GGT: 28 U/L | ALT: 22 U/L | ALP: 90 U/L | CK: 160 U/L | LDH: 410 U/L | cTnI: 0.12 ng/mL | BUN: 26 mg/dL | Kreatinin: 1.2 mg/dL | Glikoz: 90 mg/dL | Total Protein: 5.8 g/dL | Albümin: 2.1 g/dL | Globülin: 3.7 g/dL | Glutaraldehit: 4 dk | SAA: 120 µg/mL | Na⁺: 135 mEq/L | K⁺: 3.7 mEq/L | Cl⁻: 95 mEq/L | Ca²⁺: 8.5 mg/dL | P: 4.6 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3"],
                "content": "pH: 7.28 | pO₂: 65 mmHg | pCO₂: 47 mmHg | HCO₃⁻: 19.8 mmol/L | BE: -5.0 mmol/L | Laktat: 3.2 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite"],
                "content": "Spesifik Gravite: 1.020 | pH: 7.2 | Proteinüri: ++ | Gaitada gizli kan +++."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["endoskopi", "guttural", "mantar", "arter"],
                "content": "Endoskopi: Hava kesesi kubbesinde A. carotis interna üzerinde siyah/yeşilimsi mantar plağı (Aspergillus fumigatus) ve vasküler erozyon."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnez & Bulgu Sorgulama Konsolu (Serbest Metin Sorgulama)</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde şıklar veya hazır butonlar <u>yoktur</u>. 
        Kafanızdaki klinik şüpheye göre ne öğrenmek istiyorsanız kutucuğa <b>kendi cümlenizle veya kelimelerinizle</b> yazınız 
        (Örn: <i>"Hayvan ne ile besleniyor?"</i>, <i>"Ateşi kaç derece?"</i>, <i>"Hemogram kan tahlili sonuçları"</i>, <i>"Biyokimya ve enzim değerleri"</i>, <i>"Kan gazı analizi"</i>, <i>"Deri kazıntısı mikroskopisi"</i>).
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

# AUTOMATIC DISPLAY OF MACROSCOPIC CLINICAL IMAGES UPON CASE SELECTION (CLEAN - NO TEXT)
if "makroskopik_gorsel" in active_case:
    mg = active_case["makroskopik_gorsel"]
    img_path = find_gorsel_path(mg["file"])
    if img_path and os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        uploaded_img = st.file_uploader(
            f"📷 Klinik Makroskopik Görsel Yükleyiniz (.jpg / .png):",
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
    
    # Check if query is specifically asking for mikroskop / mikroskopi / kazıntı
    is_mikroskop_query = any(kw in text_clean for kw in ["mikroskop", "mikroskopi", "mikroskopik", "kazinti", "lam"])
    
    matched_cats = []
    for cat_key, cat_info in categories_dict.items():
        # IF query is specifically about mikroskop, DO NOT match BIYOKIMYA, HEMOGRAM, KAN_GAZI, IDRAR
        if is_mikroskop_query and cat_key in ["BIYOKIMYA_FULL", "HEMOGRAM", "KAN_GAZI", "IDRAR_TAHLILI"]:
            continue
            
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
        placeholder="Örn: İştah durumu nasıl?, Biyokimya sonuçları?, Hemogram tahlili?, Deri kazıntısı mikroskopisi..."
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
            st.info("Bu soruyla ilgili bilgi zaten aşağıda açılmıştı.")
    else:
        st.warning("⚠️ Eşleşen bilgi bulunamadı. Lütfen sorunuzu farklı kelimelerle yazınız (Örn: 'rasyon', 'ateş', 'hemogram', 'biyokimya', 'kan gazı', 'idrar', 'mikroskop').")

# Display Discovered Information
st.markdown("---")
st.markdown(f"### 📂 Keşfedilen Klinik İpuçları ve Muayene Bulguları ({len(st.session_state.history)} Bilgi Açıldı)")

if st.session_state.history:
    for item in reversed(st.session_state.history):
        is_micro_gorsel = ("gorsel" in item)
        has_file = False
        img_path = None
        
        if is_micro_gorsel:
            g = item["gorsel"]
            img_path = find_gorsel_path(g["file"])
            if img_path and os.path.exists(img_path):
                has_file = True

        # IF IT HAS A MICROSCOPIC IMAGE AND THE FILE EXISTS: SHOW ONLY THE PHOTO! NO TEXT CONTENT AT ALL!
        if is_micro_gorsel and has_file:
            st.markdown(f"""
                <div class='card-found'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                        <span class='badge-category'>{item['title']}</span>
                        <span style='font-size:12px; color:#7F7F7F;'>Sorulan Soru: "{item['query']}"</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.image(img_path, use_container_width=True)
        else:
            # SHOW STANDARD CARD WITH TEXT
            st.markdown(f"""
                <div class='card-found'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                        <span class='badge-category'>{item['title']}</span>
                        <span style='font-size:12px; color:#7F7F7F;'>Sorulan Soru: "{item['query']}"</span>
                    </div>
                    <div class='card-content'><b>🩺 Bulgu / Öykü:</b> {item['content']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # IF MICROSCOPIC GORSEL BUT FILE NOT FOUND: SHOW UPLOAD BUTTON
            if is_micro_gorsel and not has_file:
                up_micro = st.file_uploader(
                    f"📷 Mikroskopik Görsel Yükleyiniz (.jpg / .png):",
                    type=["jpg", "jpeg", "png"],
                    key=f"up_micro_{item['cat_key']}_{active_case['kod']}"
                )
                if up_micro is not None:
                    st.image(up_micro, use_container_width=True)

    if st.button("🗑️ Bu Vakanın Sorgu Geçmişini Temizle"):
        st.session_state.history = []
        st.rerun()

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
            st.markdown(f"#### 🔑 {selected_case_name} Cevap Anahtarı & Tüm Bilgiler:")
            
            if st.button("🔓 Tüm Tahlil ve Bulguları Sınıf Ekranda Aç"):
                for ck, cv in active_case["categories"].items():
                    already_in = any(item["cat_key"] == ck for item in st.session_state.history)
                    if not already_in:
                        item_dict = {
                            "cat_key": ck,
                            "query": "Eğitmen Kilidi Açıldı",
                            "title": cv["name"],
                            "content": cv["content"]
                        }
                        if "gorsel" in cv:
                            item_dict["gorsel"] = cv["gorsel"]
                        st.session_state.history.append(item_dict)
                st.rerun()

            for ck, cv in active_case["categories"].items():
                st.markdown(f"**• {cv['name']}:** {cv['content']}")
        elif pass_code:
            st.error("Hatalı Şifre!")
