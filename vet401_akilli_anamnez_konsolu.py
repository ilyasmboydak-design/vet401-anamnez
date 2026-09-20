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

# Helper function to find images safely (case-insensitive & extension-insensitive)
def find_gorsel_path(base_path):
    if not base_path:
        return None
    if os.path.exists(base_path):
        return base_path
    
    # Extract directory and filename
    dirname = os.path.dirname(base_path) or '.'
    filename = os.path.basename(base_path)
    name_no_ext, _ = os.path.splitext(filename)
    
    if os.path.exists(dirname):
        for f in os.listdir(dirname):
            f_no_ext, _ = os.path.splitext(f)
            if f_no_ext.lower() == name_no_ext.lower():
                full_p = os.path.join(dirname, f)
                if os.path.isfile(full_p):
                    return full_p
    return None

# Cases Knowledge Base (12 Cases with 15 Complete Categories Each)
CASES = {
    "Vaka A (Papatya)": {
        "kod": "VAKA_A",
        "sikayet": "Gerdan ve çene altında soğuk ödem, iştahsızlık, belirgin süt verimi düşüşü, kambur duruş ve inleme.",
        "makroskopik_gorsel": {"fig": "TRP", "title": "Gerdan Ödemi & Jugular Staz", "file": "gorseller/trp_gerdan_odemi.jpg"},
        "kesin_tani": "Traumatik Retikuloperikarditis (TRP / Septik Perikarditis)",
        "ayirici_tani": "Miyokardiyal Lenfosarkom (Ağrı testleri - ferroskop -), Cor Pulmonale (Rakım öyküsü +, kültür steril), Vena Cava Caudalis Trombozu (Hemoptizi +).",
        "tedavi": "Sütü sağılan ineğe parenteral Geniş Spektrumlu Antibiyotik (Ceftiofur 2.2 mg/kg IV veya Penisilin-Streptomisin), Furosemid (0.5-1 mg/kg IV ödem çözücü), Rumen mıknatısı yutturulması, Göğüs eğimli padokta istirahat. İleri vakada Perikardiyosentez ve drenaj.",
        "kontrendike": "Şiddetli venöz dolgunluk varken HIZLI IZOTONIK SIVI YÜKLEMESİ (Akut sağ kalp yetmezliğini tetikler!). Agresif hareket ettirme.",
        "categories": {
            "RASYON_YEM": {
                "name": "🌾 Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "mısır", "arpa", "silaj", "balya", "saman", "tel", "çivi", "yabancı cisim"],
                "content": "İşletmede karma kaba/yoğun rasyon uygulanmaktadır. Balya parçalama esnasında kaba yeme inşaat tellerinin ve çivilerin karışmış olabileceği şüphelenilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "📍 Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil", "coğrafya", "yükseklik"],
                "content": "Hayvan Ceyhan ovasındaki (rakım ~50m) sabit süt tesisinde doğup büyümüştür. Herhangi bir yüksek rakım veya yayla nakli öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "mastitis", "öykü"],
                "content": "2 ay önce sorunsuz doğum yapmıştır. Geçmişinde kronik mastitis veya metritis kaydı bulunmamaktadır."
            },
            "ISTAH_DURUMU": {
                "name": "🍽️ İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yiyor mu", "su", "yutma", "geviş", "anoreksi"],
                "content": "Komple Anoreksi (Ağrı ve perikardiyal baskı nedeniyle yem ve su tüketimini tamamen kesmiştir, geviş getirme durmuştur)."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "ödem", "jugular"],
                "content": "Vücut Sıcaklığı: 39.8 °C | Kalp Frekansı: 102 atım/dk | Solunum Frekansı: 42 nefes/dk | Mukozalar: Soluk pembe | CRT: 2.5 saniye | Gerdan ve submandibuler bölgede hamur kıvamında soğuk ödem | Vena jugularis stazı +, yalancı jugular nabız +."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "boğuk"],
                "content": "Kalp Oskültasyonu: Gaz ve pürülan sıvının çalkalanmasına bağlı çamaşır makinesi / su şılpırtısı (splashing) sesi ve boğuk kalp sesleri. Akciğer Oskültasyonu: Ventro-lateral alanlarda solunum sesleri hafif azalmış."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "ferroskop"],
                "content": "Withers pinch (cidago sıkıştırma) testi (+), sopa/kama testi (+), retikulum bölgesinde ferroskop pozitif sinyal vermektedir."
            },
            "HEMOGRAM": {
                "name": "🩸 Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lökosit", "rbc", "pcv", "hematokrit", "fibrinojen", "pp/f"],
                "content": "RBC: 5.2 x10⁶/µL | Hb: 8.5 g/dL | PCV: %26 | WBC: 22.4 x10³/µL (Sola kaymalı rejenere nötrofili) | Plazma Fibrinojeni: 1250 mg/dL (Aşırı yüksek) | PP/F Oranı: 6.3 (<10: Şiddetli aktif fibrinöz yangı)."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "🧪 Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "enzim"],
                "content": "AST: 145 U/L | GGT: 42 U/L | ALT: 28 U/L | ALP: 85 U/L | CK: 180 U/L | LDH: 1150 U/L | Kardiyak Troponin I: 1.85 ng/mL (Miyokardiyal parietal yangı / harabiyet)."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "🧬 Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["bun", "üre", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 32 mg/dL | Serum Kreatinin: 1.8 mg/dL | Kan Glikozu: 72 mg/dL | Total Bilirubin: 1.1 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "🛡️ Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["protein", "albümin", "globülin", "glutaraldehit", "saa", "yangı"],
                "content": "Total Protein: 92 g/L (Hiperproteinemi) | Albümin: 2.8 g/dL | Globülin: 6.4 g/dL | Glutaraldehit Pıhtılaşma Süresi: 1.5 dakika (<3 dk: Ağır hipergamaglobülinemi) | Serum Amyloid A (SAA): 480 µg/mL."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "⚡ Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "elektrolit"],
                "content": "Na⁺: 132 mmol/L | K⁺: 3.8 mmol/L | Cl⁻: 92 mmol/L (Hafif hipokloremik alkaloz) | Ca²⁺: 8.2 mg/dL | İnk. Fosfor: 4.5 mg/dL."
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.48 | pO₂: 62 mmHg | pCO₂: 46 mmHg | HCO₃⁻: 32.5 mmol/L | Baz Açığı (BE): +7.8 mmol/L (Metabolik Alkaloz) | Laktat: 2.8 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "sediment", "idrar ph"],
                "content": "İdrar Spesifik Gravite: 1.022 | İdrar pH: 8.0 | Proteinüri: (+2) | Glikoz: (-) | Keton: (-) | Bilirubin: (-) | Sediment: Nadir yassı epitel, eritrosit negatif."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "kültür", "ponksiyon", "perikardiyosentez"],
                "content": "Ultrasonografi: Perikard kasesinde 8 cm genişliğinde hiperekojenik fibrin bantları ve hipoekojenik sıvı birikimi. Perikardiyosentez: Kirli sarı-yeşil renkli fetid eksudat; kültürde Trueperella pyogenes ve anaerobik bakteriler."
            }
        }
    },
    "Vaka B (Yonca)": {
        "kod": "VAKA_B",
        "sikayet": "Tekrarlayan fluktuan ateş, topallık, çabuk yorulma, zayıflama ve süt verimi düşüşü.",
        "makroskopik_gorsel": {"fig": "Endokardit", "title": "Bacak Eklem Şişliği & Topallık", "file": "gorseller/endokardit_topallik.jpg"},
        "kesin_tani": "Valvüler Endokarditis (Vejetatif Endokardit)",
        "ayirici_tani": "TRP (Kalp sesleri boğuk değil, çalkantı sesi yok, endokarditte sistolik üfürüm var), Ağrı testleri (-).",
        "tedavi": "Uzun süreli (En az 3-4 hafta) yüksek doz parenteral Antibiyotik (Penisilin G + Gentamisin veya Ceftiofur), Aspirin (100 mg/kg 48 saatte bir antiagregan), Düşük doz Heparin, Mutlak istirahat.",
        "kontrendike": "Ağır egzersiz ve nakil (Vejetatif kitleden septik emboli kopma ve ani ölüm riski!).",
        "categories": {
            "RASYON_YEM": {
                "name": "🌾 Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "mısır", "arpa", "ot", "silaj"],
                "content": "Standart süt sığırı rasyonu verilmektedir. Yem değişikliği veya rasyon krizi yoktur."
            },
            "LOKASYON_RAKIM": {
                "name": "📍 Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil"],
                "content": "Çukurova bölgesinde açık serbest duraklı tesiste barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "mastitis", "öykü"],
                "content": "1 ay önce şiddetli puerperal metritis ve kronik mastitis tedavisi görmüştür (Bakteriyemi kaynağı!)."
            },
            "ISTAH_DURUMU": {
                "name": "🍽️ İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yiyor mu", "su", "hiporeksi"],
                "content": "Fluktuan ateşe bağlı dalgalı iştah (Hiporeksi), kilo kaybı belirgin."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "topallık"],
                "content": "Vücut Sıcaklığı: 40.2 °C (Alevli tekrarlayan ateş) | Kalp Frekansı: 112 atım/dk | Solunum Frekansı: 38 nefes/dk | Mukozalar: Soluk / peteşili | CRT: 3.0 saniye | Sağ ön bacak karpal ekleminde sıcak ağrılı şişlik ve topallık."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "sistolik", "akciğer"],
                "content": "Kalp Oskültasyonu: Sol/sağ AV kapak odağında sistol ile eş zamanlı holosistolik pürüzlü üfürüm (Grade 4/6). Çalkantı sesi YOKTUR. Akciğer oskültasyonunda vesiküler sesler sertleşmiş."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "retikulum"],
                "content": "Retikulum ağrı testlerinin tamamı NEGATİF (-). Eklem palpasyonunda sıcaklık ve ağrı (+)."
            },
            "HEMOGRAM": {
                "name": "🩸 Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lökosit", "rbc", "pcv", "fibrinojen"],
                "content": "RBC: 4.1 x10⁶/µL | Hb: 7.2 g/dL | PCV: %22 (Rejeneratif olmayan anemi) | WBC: 28.6 x10³/µL (Şiddetli nötrofili ve sola kayma) | Plazma Fibrinojeni: 980 mg/dL | PP/F: 8.1."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "🧪 Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["ast", "ggt", "alt", "alp", "ck", "ldh", "troponin"],
                "content": "AST: 110 U/L | GGT: 35 U/L | CK: 240 U/L | LDH: 890 U/L | Kardiyak Troponin I: 2.45 ng/mL (Yüksek endokardit/miyokardit hasarı)."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "🧬 Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["bun", "üre", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 45 mg/dL | Serum Kreatinin: 2.1 mg/dL (Septik mikrotrombüslere bağlı sekonder renal azotemi) | Glikoz: 68 mg/dL | Total Bilirubin: 0.9 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "🛡️ Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["protein", "albümin", "globülin", "glutaraldehit", "saa"],
                "content": "Total Protein: 88 g/L | Albümin: 2.4 g/dL | Globülin: 6.4 g/dL | Glutaraldehit Pıhtılaşma Süresi: 2.0 dakika | SAA: 620 µg/mL."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "⚡ Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "Na⁺: 135 mmol/L | K⁺: 4.1 mmol/L | Cl⁻: 98 mmol/L | Ca²⁺: 8.0 mg/dL | İnk. Fosfor: 5.1 mg/dL."
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "Kan pH: 7.34 | pO₂: 68 mmHg | pCO₂: 38 mmHg | HCO₃⁻: 20.1 mmol/L | Baz Açığı (BE): -4.5 mmol/L (Metabolik Asidoz) | Laktat: 3.4 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "mikrohematüri", "sediment"],
                "content": "İdrar pH: 6.5 | Proteinüri: (+3) | Mikrohematüri: (+2) | İdrar sedimentinde bozulmamış eritrositler ve lökosit silindirleri."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["ultrason", "ekokardiyografi", "kültür", "bakteri"],
                "content": "Ekokardiyografi: Trikuspid ve mitral kapak yaprakçıklarında 2.5 cm çapında karnabahar görünümünde vejetatif nodüler vejetasyonlar. Tekrarlayan Kan Kültürü: Trueperella pyogenes üremesi."
            }
        }
    },
    "Vaka C (Zümrüt)": {
        "kod": "VAKA_C",
        "sikayet": "Gerdan bölgesinde soğuk hamur ödem, çabuk tıkanma, efor dispnesi ve siyanoz.",
        "makroskopik_gorsel": {"fig": "CorPulmonale", "title": "Gerdan Ödemi & Siyanoz", "file": "gorseller/cor_pulmonale_odemi.jpg"},
        "kesin_tani": "Cor Pulmonale (Yüksek Rakım Hastalığı / High Altitude Disease / Brisket Disease)",
        "ayirici_tani": "TRP (Ağrı testleri - , su çalkantı sesi - , ateş - , lökositoz - , yüksek rakım sevk öyküsü +).",
        "tedavi": "Hayvanın anında düşük rakıma (ovaya) nakledilmesi, Oksijen desteği, Furosemid (0.5-1 mg/kg IV), Düşük sodyumlu rasyon. Nakil imkanı yoksa Terapötik Flebotomi (Kan alma).",
        "kontrendike": "Rakımda tutmaya devam etmek ve HAYVANI SIKIŞTIRIP KOŞTURMAK (Akut sağ kalp kollapsı ve ani ölüm!).",
        "categories": {
            "RASYON_YEM": {
                "name": "🌾 Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "mera", "ot"],
                "content": "Yayla merasında otlatılmaktadır. Toksik bitki öyküsü belirlenmemiştir."
            },
            "LOKASYON_RAKIM": {
                "name": "📍 Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil", "dağ", "yükseklik"],
                "content": "Toros Dağları Pozantı yaylasına (rakım 2400 metre) 3 hafta önce sevk edilmiştir (Hipobarik hipoksi ortamı!)."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Geçmişinde kaydedilmiş kardiyovasküler veya solunumsal enfeksiyon öyküsü yoktur."
            },
            "ISTAH_DURUMU": {
                "name": "🍽️ İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yiyor mu", "su", "hiporeksi"],
                "content": "İştah hafif azalmış (Hiporeksi), efor sarf ettiğinde çabuk tıkanmaktadır."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "siyanoz", "ödem", "jugular"],
                "content": "Vücut Sıcaklığı: 38.6 °C (TAMAMEN NORMAL) | Kalp Frekansı: 96 atım/dk | Solunum Frekansı: 48 nefes/dk (Takipne) | Mukozalar: Siyanotik (Morumsu) | CRT: 2.8 saniye | Gerdan ve göğüs altında soğuk hamur ödem | Vena jugularis stazı +."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "akciğer"],
                "content": "Kalp Oskültasyonu: Hiperdinamik güçlü kalp sesleri duyulmaktadır. Üfürüm veya su çalkantı sesi YOKTUR. Akciğer oskültasyonunda ventral veziküler seslerde hafif artış."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "retikulum"],
                "content": "Retikulum ağrı testlerinin tamamı NEGATİF (-)."
            },
            "HEMOGRAM": {
                "name": "🩸 Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lökosit", "rbc", "pcv", "polisitemi", "fibrinojen"],
                "content": "RBC: 10.8 x10⁶/µL (Sekonder Mutlak Polisitemi!) | Hb: 17.2 g/dL | PCV: %54 (Aşırı polisitrik) | WBC: 7.2 x10³/µL (Yangı yok, tamamen normal) | Plazma Fibrinojeni: 320 mg/dL (Normal) | PP/F Oranı: 22.8."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "🧪 Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["ast", "ggt", "alt", "alp", "ck", "ldh", "troponin"],
                "content": "AST: 68 U/L | GGT: 22 U/L | ALT: 18 U/L | CK: 95 U/L | LDH: 450 U/L | Kardiyak Troponin I: 0.12 ng/mL."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "🧬 Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["bun", "üre", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 18 mg/dL | Serum Kreatinin: 0.9 mg/dL | Kan Glikozu: 75 mg/dL | Total Bilirubin: 0.6 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "🛡️ Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["protein", "albümin", "globülin", "glutaraldehit", "saa"],
                "content": "Total Protein: 74 g/L | Albümin: 3.3 g/dL | Globülin: 4.1 g/dL | Glutaraldehit Pıhtılaşma Süresi: >15 dakika (Normal) | SAA: 12 µg/mL."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "⚡ Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "Na⁺: 138 mmol/L | K⁺: 4.2 mmol/L | Cl⁻: 102 mmol/L | Ca²⁺: 9.2 mg/dL | İnk. Fosfor: 4.8 mg/dL."
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat", "hipoksi"],
                "content": "Kan pH: 7.36 | pO₂: 48 mmHg (Şiddetli Doku Hipoksisi / Hipobarik hipoksi!) | pCO₂: 42 mmHg | HCO₃⁻: 23.5 mmol/L | Baz Açığı (BE): -0.8 mmol/L | Laktat: 1.8 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "sediment"],
                "content": "İdrar Spesifik Gravite: 1.018 | İdrar pH: 7.5 | Protein: (-) | Glikoz: (-) | Keton: (-) | Bilirubin: (-) | Sediment temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri"],
                "content": "Ekokardiyografi: Sağ ventrikül serbest duvar kalınlığında belirgin artış (Sağ Kalp Hipertrofisi), pulmoner arter çapında genişleme. Perikardiyosentez: Berrak steril sıvı, kültür negatif."
            }
        }
    },
    "Vaka D (Yiğit)": {
        "kod": "VAKA_D",
        "sikayet": "Burun deliklerinden ve ağızdan fışkırır tarzda taze parlak kırmızı kan gelmesi (hemoptizi) ve katran gibi siyah dışkı yapma (melena).",
        "makroskopik_gorsel": {"fig": "VCCT", "title": "Burundan Ağızdan Fışkıran Kan & Hemoptizi", "file": "gorseller/vcct_hemoptizi.jpg"},
        "kesin_tani": "Vena Cava Caudalis Trombozu (VCCT / Hepatik Apse & Pulmoner Anevrizma Ruptürü)",
        "ayirici_tani": "TRP ve Endokardit (VCCT'de fışkırır tarzda hemoptizi ve melena patognomoniktir).",
        "tedavi": "Prognozu son derece kötüdür (Prognozu infaust). Acil insani kesim veya kan transfüzyonu, destekleyici hemostatik tedavi (K3 vitamini, Traneksamik asit). Korumada Rumen Asidozu önlenmelidir.",
        "kontrendike": "Kanamayı artıran damar genişletici ve antikoagülan ilaçlar.",
        "categories": {
            "RASYON_YEM": {
                "name": "🌾 Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "mısır", "arpa", "nişasta", "asidoz"],
                "content": "18 aylık besi danasıdır. Yoğun mısır ve arpa kırması ağırlıklı, kaba yemi yetersiz yüksek nişastalı besi rasyonu verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "📍 Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil"],
                "content": "Besi padoğunda barındırılmaktadır. Coğrafi nakil öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "asidoz", "şişkinlik", "sara", "rüminitis"],
                "content": "Geçmişinde tekrarlayan subakut rumen asidozu (SARA), yem çarpması ve rüminitis öyküsü mevcuttur."
            },
            "ISTAH_DURUMU": {
                "name": "🍽️ İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yiyor mu", "su", "anoreksi"],
                "content": "Şiddetli kan kaybı ve halsizliğe bağlı komple anoreksi, çökme."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "hemoptizi", "melena"],
                "content": "Vücut Sıcaklığı: 39.2 °C | Kalp Frekansı: 118 atım/dk | Solunum Frekansı: 52 nefes/dk | Mukozalar: Bembeyaz (Ağır kan kaybı anemisi!) | CRT: 4.0 saniye | Ağız ve burundan köpüklü taze kan fışkırması (Hemoptizi) | Dışkı: Siyah katran kıvamında (Melena)."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Taşikardik zayıf düştü sesleri. Akciğer Oskültasyonu: Bilateral yaygın kaba raller ve hışırtı sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "retikulum"],
                "content": "Retikulum ağrı testleri NEGATİF (-)."
            },
            "HEMOGRAM": {
                "name": "🩸 Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lökosit", "rbc", "pcv", "anemi", "fibrinojen"],
                "content": "RBC: 2.1 x10⁶/µL (Kritik Kan Kaybı Anemisi!) | Hb: 4.2 g/dL | PCV: %12 (Acil Transfüzyon Eşiği!) | WBC: 21.5 x10³/µL | Plazma Fibrinojeni: 1050 mg/dL | PP/F: 7.23."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "🧪 Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["ast", "ggt", "alt", "alp", "ck", "ldh", "troponin"],
                "content": "AST: 210 U/L (Karaciğer parankim hasarı) | GGT: 68 U/L | ALT: 45 U/L | ALP: 120 U/L | CK: 130 U/L | LDH: 980 U/L | Troponin I: 0.28 ng/mL."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "🧬 Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["bun", "üre", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 42 mg/dL | Serum Kreatinin: 1.6 mg/dL | Kan Glikozu: 88 mg/dL | Total Bilirubin: 1.2 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "🛡️ Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["protein", "albümin", "globülin", "glutaraldehit", "saa"],
                "content": "Total Protein: 76 g/L | Albümin: 2.2 g/dL | Globülin: 5.4 g/dL | Glutaraldehit Pıhtılaşma Süresi: 3.0 dakika | SAA: 380 µg/mL."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "⚡ Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "Na⁺: 134 mmol/L | K⁺: 3.6 mmol/L | Cl⁻: 96 mmol/L | Ca²⁺: 7.8 mg/dL | İnk. Fosfor: 4.2 mg/dL."
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "Kan pH: 7.24 | pO₂: 52 mmHg | pCO₂: 50 mmHg | HCO₃⁻: 18.5 mmol/L | Baz Açığı (BE): -6.2 mmol/L (Metabolik Asidoz) | Laktat: 4.2 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "sediment"],
                "content": "İdrar pH: 6.8 | Proteinüri: (+1) | Ürobilinojen hafif pozitif | Sedimentte renal silindir yok."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["ultrason", "usg", "karaciğer", "apse", "vena cava", "trombüs"],
                "content": "Abdominal Ultrasonografi: Karaciğer parankiminde 6 cm çapında kılıflı apse odağı (Hepatik Apse) ve Vena Cava Caudalis lümeninde tıkayıcı ekojenik trombüs kütlesi. Torakal USG: Pulmoner arter çevresinde hematom ve anevrizma alanları."
            }
        }
    },
    "Vaka E (Kudret)": {
        "kod": "VAKA_E",
        "sikayet": "Baş, göz çevresi, kulak kaidesi ve boyunda dairesel, kepekli, gri-beyaz kireçimsi kabuklanma ve alopezi (tüy dökülmesi).",
        "makroskopik_gorsel": {"fig": "Figure 1.2-1", "title": "Klinik Mantar Lezyonu", "file": "gorseller/figure_1_2_1.jpg"},
        "kesin_tani": "Trikofiti (Dermatophytosis / Ringworm – Trichophyton verrucosum)",
        "ayirici_tani": "Sarkoptik Uyuz (Trikofitide kaşıntı yoktur/azdır, lezyonlar dairesel kireçimsi kabukludur; uyuzda şiddetli kaşıntı ve deride kalınlaşma vardır).",
        "tedavi": "Lokal %2-4 Tropikal Antifungal (Enilkonazol / Mikonazol solüsyonu ile banyo/püskürtme), Sistemik Vitamin A-D3-E ve Çinko takviyesi, Barınak dezenfeksiyonu ve güneşlendirme.",
        "kontrendike": "Sistemik Kortikosteroid kullanımı (Fungal enfeksiyonun tüm sürüye yayılmasına neden olur!). Kabukları kuru kuru kazımak (Zoonoz bulaş riski!).",
        "categories": {
            "RASYON_YEM": {
                "name": "🌾 Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "vitamin", "çinko"],
                "content": "Standart besi rasyonu verilmektedir. A vitamini ve minerallerce zenginleştirilmemiştir."
            },
            "LOKASYON_RAKIM": {
                "name": "📍 Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil"],
                "content": "Nemli, havalandırması yetersiz kapalı dana padoğunda barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Sürüdeki diğer 5 danada benzer dairesel tüy dökülmeleri başlamıştır (Bulaşıcı temas öyküsü!)."
            },
            "ISTAH_DURUMU": {
                "name": "🍽️ İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yiyor mu", "su"],
                "content": "İştah ve genel durum tamamen normaldir."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "kabuk", "döküntü"],
                "content": "Vücut Sıcaklığı: 38.5 °C (Normal) | Kalp Frekansı: 72 atım/dk | Solunum Frekansı: 24 nefes/dk | Mukozalar: Pembe | CRT: 1.5 saniye | Baş, göz çevresi ve boyunda dairesel, grimsi-beyaz kireçimsi kabuklanma ve alopezi. Kaşıntı yok."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve akciğer oskültasyon sesleri tamamen normaldir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "retikulum"],
                "content": "Ağrı veya duyarlılık tespit edilmemiştir."
            },
            "HEMOGRAM": {
                "name": "🩸 Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lökosit", "rbc", "pcv", "fibrinojen"],
                "content": "RBC: 6.8 x10⁶/µL | Hb: 11.5 g/dL | PCV: %35 | WBC: 8.4 x10³/µL (Normal) | Eozinofil: %2 (Normal) | Plazma Fibrinojeni: 280 mg/dL."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "🧪 Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["ast", "ggt", "alt", "alp", "ck", "ldh", "troponin"],
                "content": "AST: 48 U/L | GGT: 18 U/L | ALT: 15 U/L | CK: 70 U/L | LDH: 380 U/L | Troponin I: <0.01 ng/mL."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "🧬 Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["bun", "üre", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 15 mg/dL | Serum Kreatinin: 0.8 mg/dL | Kan Glikozu: 78 mg/dL | Total Bilirubin: 0.3 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "🛡️ Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["protein", "albümin", "globülin", "glutaraldehit", "saa"],
                "content": "Total Protein: 72 g/L | Albümin: 3.5 g/dL | Globülin: 3.7 g/dL | Glutaraldehit: >15 dakika | SAA: 8 µg/mL."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "⚡ Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "Na⁺: 140 mmol/L | K⁺: 4.4 mmol/L | Cl⁻: 101 mmol/L | Ca²⁺: 9.5 mg/dL | İnk. Fosfor: 5.2 mg/dL."
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "Kan pH: 7.40 | pO₂: 88 mmHg | pCO₂: 40 mmHg | HCO₃⁻: 24.2 mmol/L | Baz Açığı (BE): +0.2 mmol/L | Laktat: 1.0 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "sediment"],
                "content": "İdrar Spesifik Gravite: 1.020 | pH: 7.8 | Protein: (-) | Glikoz: (-) | Keton: (-) | Bilirubin: (-) | Sediment temiz."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "🔬 Deri Kazıntısı & Mikroskopik Mantar Teşhisi",
                "keywords": ["mikroskop", "kazıntı", "deri kazıntısı", "koh", "mantar", "artrospor", "lam"],
                "gorsel": {"fig": "Figure 1.2-11", "title": "Mikroskopik Mantar Sporu (%10 KOH Hazırlığı)", "file": "gorseller/figure_1_2_11.jpg"},
                "content": "%10 KOH ile hazırlanan deri kazıntısında kıl şaftını dıştan zırh gibi saran küresel Trichophyton verrucosum ektotriks artrospor zincirleri belirgin olarak izlenmiştir."
            }
        }
    },
    "Vaka F (Nazar)": {
        "kod": "VAKA_F",
        "sikayet": "Kulak kepçesi, boyun, sırt ve göğüs derisinde şiddetli kaşıntı, deride kalınlaşma, kıvrımlaşma (likenifikasyon) ve tüy kaybı.",
        "makroskopik_gorsel": {"fig": "Figure 1.3-13 & 1.3-15", "title": "Klinik Uyuz Lezyonu", "file": "gorseller/figure_1_3_13.jpg"},
        "kesin_tani": "Sarkoptik Uyuz (Sarcoptic Mange / Scabies – Sarcoptes scabiei var. bovis)",
        "ayirici_tani": "Trikofiti (Mantarda kaşıntı yoktur, uyuzda şiddetli pruritus ve likenifikasyon vardır), Psoroptik Uyuz (Kulak dışı gövde odağı).",
        "tedavi": "Parenteral İvermektin / Doramektin (0.2 mg/kg SC, 14 gün arayla 2 doz) veya Acaricide banyosu (Amitraz), Sürüdeki tüm temaslı hayvanların eş zamanlı tedavisi.",
        "kontrendike": "Tek doz enjeksiyon yapıp bırakmak (Yumurtadan çıkan yeni akarlar hastalığı nüksettirir!).",
        "categories": {
            "RASYON_YEM": {
                "name": "🌾 Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "mera"],
                "content": "Saman ve yetersiz mera ağırlıklı besleme yapılmaktadır."
            },
            "LOKASYON_RAKIM": {
                "name": "📍 Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil"],
                "content": "Hijyeni zayıf, kalabalık kapalı barınakta barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Sürekli duvarlara ve demirlere kaşınma öyküsü vardır."
            },
            "ISTAH_DURUMU": {
                "name": "🍽️ İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yiyor mu", "su", "hiporeksi"],
                "content": "Sürekli kaşınma huzursuzluğuna bağlı iştah dalgalı (Hiporeksi), zayıflama."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "kaşıntı", "likenifikasyon"],
                "content": "Vücut Sıcaklığı: 38.8 °C | Kalp Frekansı: 84 atım/dk | Solunum Frekansı: 28 nefes/dk | Mukozalar: Pembe | CRT: 1.8 saniye | Deride şiddetli kalınlaşma, kıvrımlaşma (likenifikasyon), eksforyasyon kanamaları ve döküntü."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve akciğer oskültasyon sesleri normaldir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "retikulum"],
                "content": "Palpasyonda şiddetli kaşınma refleksi ve huzursuzluk (+)."
            },
            "HEMOGRAM": {
                "name": "🩸 Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lökosit", "rbc", "pcv", "eozinofil"],
                "content": "RBC: 5.8 x10⁶/µL | Hb: 9.8 g/dL | PCV: %30 | WBC: 14.8 x10³/µL | Eozinofil: %14 (Belirgin Eozinofili - Paraziter/alerjik deri yanıtı!) | Fibrinojen: 420 mg/dL."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "🧪 Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["ast", "ggt", "alt", "alp", "ck", "ldh", "troponin"],
                "content": "AST: 55 U/L | GGT: 22 U/L | ALT: 18 U/L | CK: 110 U/L | LDH: 420 U/L | Troponin I: <0.01 ng/mL."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "🧬 Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["bun", "üre", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 18 mg/dL | Serum Kreatinin: 0.9 mg/dL | Kan Glikozu: 70 mg/dL | Total Bilirubin: 0.4 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "🛡️ Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["protein", "albümin", "globülin", "glutaraldehit", "saa"],
                "content": "Total Protein: 78 g/L | Albümin: 3.1 g/dL | Globülin: 4.7 g/dL | Glutaraldehit: 8 dakika | SAA: 45 µg/mL."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "⚡ Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "Na⁺: 139 mmol/L | K⁺: 4.2 mmol/L | Cl⁻: 100 mmol/L | Ca²⁺: 9.1 mg/dL | İnk. Fosfor: 4.9 mg/dL."
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "Kan pH: 7.39 | pO₂: 85 mmHg | pCO₂: 41 mmHg | HCO₃⁻: 23.8 mmol/L | Baz Açığı (BE): -0.4 mmol/L | Laktat: 1.2 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "sediment"],
                "content": "İdrar Spesifik Gravite: 1.022 | pH: 7.6 | Protein: (-) | Glikoz: (-) | Keton: (-) | Bilirubin: (-) | Sediment temiz."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "🔬 Derin Deri Kazıntısı & Akar Mikroskopisi",
                "keywords": ["mikroskop", "kazıntı", "deri kazıntısı", "akar", "uyuz", "mineral yağ", "sarcoptes"],
                "gorsel": {"fig": "Figure 1.3-18", "title": "Mikroskopik Sarcoptes Scabiei Akari", "file": "gorseller/figure_1_3_18.jpg"},
                "content": "Kapiller kanama görülünceye kadar alınan derin deri kazıntısında mineral yağ altında tespit edilen canlı ergin Sarcoptes scabiei akarları, yumurtaları ve siyah oval dışkı peletleri (scybala)."
            }
        }
    },
    "Vaka G (Çiçek)": {
        "kod": "VAKA_G",
        "sikayet": "Yalnızca boyun, omuz ve sırt bölgesindeki beyaz (pigmentsiz) deri alanlarında eritem, hamur ödemi, derinin tabaka halinde soyulması (nekroz/sloughing) ve dokunmaya karşı şiddetli aşırı duyarlılık/ağrı (hipersensitivite).",
        "makroskopik_gorsel": {"fig": "Figure 1.7-35", "title": "Hepatojen Fotosensitizasyon (Boyun & Sırt Deri Nekrozu)", "file": "gorseller/figure_1_7_35.jpg"},
        "kesin_tani": "Hepatojen Fotosensitizasyon (Sekonder Güneş Yanığı / Hepatik Kolestaz & Filloeritrin Akümülasyonu)",
        "ayirici_tani": "Primer Fotosensitizasyon (Karaciğer enzimleri AST/GGT ve bilirubin normaldir; hepatojende AST, GGT ve bilirubin aşırı yüksektir, idrar koyu bira rengindedir).",
        "tedavi": "Hayvanın derhal KARANLIK / GÖLGE ahıra çekilmesi, Karaciğer koruyucu tedavi (B kompleksi, Metiyonin, Kolin, Dekstroz), Analjezik/Antiinflamatuvar (Flunixin Meglumine 2.2 mg/kg), Klorofil içeren yeşil mera otunun kesilip kuru saman verilmesi.",
        "kontrendike": "GÜNEŞ IŞIĞINA ÇIKARMAK ve Hepatotoksik ilaçların kullanımı.",
        "categories": {
            "RASYON_YEM": {
                "name": "🌾 Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "mera", "klorofil", "lantana", "küf"],
                "content": "Yeşil ot ve klorofilden zengin mera otlatması yapılmıştır. Toksik ot ve mantar sporu şüphesi vardır."
            },
            "LOKASYON_RAKIM": {
                "name": "📍 Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil", "güneş"],
                "content": "Güneş ışığına dik maruz kalan Ceyhan mera padoğu."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "1 hafta önce meraya çıkarıldıktan sonra güneş temasıyla semptomlar aniden şekillenmiştir."
            },
            "ISTAH_DURUMU": {
                "name": "🍽️ İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yiyor mu", "su", "anoreksi"],
                "content": "Şiddetli boyun/omuz derisi ağrısı ve huzursuzluk nedeniyle Anoreksi, gölgeden çıkmak istememe."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "ikter", "ödem", "hipersensitivite"],
                "content": "Vücut Sıcaklığı: 39.5 °C | Kalp Frekansı: 98 atım/dk | Solunum Frekansı: 36 nefes/dk | Mukozalar: Belirgin İkterik (Sarı) | CRT: 2.2 saniye | Boyun, omuz ve sırtın pigmentsiz beyaz derisinde dokunmakla aşırı ağrı (hipersensitivite), hamur ödemi, çatlama ve nekrotik soyulma. Siyah deriler sağlam."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp sesleri normofonik, akciğer sesleri hafif veziküler."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "retikulum", "palpasyon"],
                "content": "Boyun, omuz ve sırt derisine temas edildiğinde hayvan şiddetle tepki verir, tepinir (Kutane hipersensitivite +)."
            },
            "HEMOGRAM": {
                "name": "🩸 Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lökosit", "rbc", "pcv", "fibrinojen"],
                "content": "RBC: 6.2 x10⁶/µL | Hb: 10.5 g/dL | PCV: %32 | WBC: 18.2 x10³/µL (Nötrofili) | Plazma Fibrinojeni: 650 mg/dL | PP/F: 11.2."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "🧪 Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["ast", "ggt", "alt", "alp", "ck", "ldh", "troponin", "karaciğer"],
                "content": "AST: 280 U/L (Yüksek) | GGT: 185 U/L (Aşırı yüksek - Şiddetli Hepatik Kolestaz!) | ALT: 52 U/L | ALP: 310 U/L | CK: 140 U/L | LDH: 820 U/L | Troponin I: 0.02 ng/mL."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "🧬 Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["bun", "üre", "kreatinin", "glikoz", "bilirubin", "filloeritrin"],
                "content": "BUN: 28 mg/dL | Serum Kreatinin: 1.2 mg/dL | Kan Glikozu: 65 mg/dL | Total Bilirubin: 4.8 mg/dL (Aşırı Yüksek - Şiddetli İkter!) | Direkt Bilirubin: 3.1 mg/dL | Plazma Filloeritrin Düzeyi: Aşırı Yüksek."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "🛡️ Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["protein", "albümin", "globülin", "glutaraldehit", "saa"],
                "content": "Total Protein: 82 g/L | Albümin: 2.7 g/dL | Globülin: 5.5 g/dL | Glutaraldehit: 4 dakika | SAA: 210 µg/mL."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "⚡ Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "Na⁺: 136 mmol/L | K⁺: 3.9 mmol/L | Cl⁻: 98 mmol/L | Ca²⁺: 8.5 mg/dL | İnk. Fosfor: 4.6 mg/dL."
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "Kan pH: 7.37 | pO₂: 82 mmHg | pCO₂: 39 mmHg | HCO₃⁻: 22.1 mmol/L | Baz Açığı (BE): -1.5 mmol/L | Laktat: 1.9 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "bilirubinüri", "çay rengi", "sediment"],
                "content": "İdrar Rengi: Koyu çay / bira renginde | Bilirubinüri: (+3) | Spesifik Gravite: 1.025 | pH: 7.2 | Protein: (+1) | Sedimentte bilirubin kristalleri."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["ultrason", "usg", "karaciğer", "safra"],
                "content": "Abdominal Ultrasonografi: Karaciğer parankiminde difüz ekojenite artışı (Hepatik steatoz/nekroz) ve safra kanallarında belirgin genişleme."
            }
        }
    },
    "Vaka H (Ateş)": {
        "kod": "VAKA_H",
        "sikayet": "Gövde, boyun ve omuz derisinde aniden beliren, parmakla basıldığında çukurlaşan (pitting edema), ödemli, kabarık, dairesel/plak benzeri ürtiker lezyonları (urtica/wheals).",
        "makroskopik_gorsel": {"fig": "Figure 1.5-1", "title": "Akut Ürtiker Ödem Plakları", "file": "gorseller/figure_1_5_1.jpg"},
        "kesin_tani": "Akut Ürtiker (Kurdeşen / Allerjik Dermatitis / Tip I Hipersensitivite)",
        "ayirici_tani": "Fotosensitizasyon (Fotosensitizasyonda sadece beyaz deri soyulur ve ikter vardır; ürtikerde tüm vücutta geçici ödem plakları belirir).",
        "tedavi": "Antihistaminik (Pheniramine Maleate / Tripelennamine 1 mg/kg IM), Ağır vakada Hızlı Etkili Kortikosteroid (Deksametazon 0.1 mg/kg IV/IM), Alerjen etkenin (ilaç/yem) derhal kesilmesi.",
        "kontrendike": "Gebe hayvanlarda yüksek doz Deksametazon kullanımı (Abortus riski!).",
        "categories": {
            "RASYON_YEM": {
                "name": "🌾 Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "alerji", "aşı", "enjeksiyon"],
                "content": "2 saat önce yeni meraya çıkış, ot değişikliği veya parenteral ilaç/aşı enjeksiyonu öyküsü."
            },
            "LOKASYON_RAKIM": {
                "name": "📍 Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil"],
                "content": "Çukurova açık süt tesisi."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Daha önce bilinen kronik deri hastalığı öyküsü yoktur."
            },
            "ISTAH_DURUMU": {
                "name": "🍽️ İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yiyor mu", "su"],
                "content": "Hafif huzursuzluk dışında iştah korunmuştur."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "urtica", "plak"],
                "content": "Vücut Sıcaklığı: 38.6 °C (Normal) | Kalp Frekansı: 88 atım/dk | Solunum Frekansı: 32 nefes/dk | Mukozalar: Pembe / hafif ödemli | CRT: 1.6 saniye | Gövde ve boyun derisinde parmakla basılınca çukurlaşan ödemli kabarık plaklar (Urtica)."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve akciğer oskültasyonu normal, üst solunum yolunda hafif hırıltı."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "retikulum"],
                "content": "Plaklara basıldığında çukurlaşır (ödem +), şiddetli ağrı yoktur."
            },
            "HEMOGRAM": {
                "name": "🩸 Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lökosit", "rbc", "pcv", "eozinofil"],
                "content": "RBC: 6.5 x10⁶/µL | Hb: 11.2 g/dL | PCV: %34 | WBC: 12.5 x10³/µL | Eozinofil: %12 (Eozinofili - Akut Tip 1 Alerjik Yanıt!) | Fibrinojen: 310 mg/dL."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "🧪 Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["ast", "ggt", "alt", "alp", "ck", "ldh", "troponin"],
                "content": "AST: 45 U/L | GGT: 19 U/L | ALT: 14 U/L | CK: 80 U/L | LDH: 350 U/L | Troponin I: <0.01 ng/mL."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "🧬 Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["bun", "üre", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 16 mg/dL | Serum Kreatinin: 0.8 mg/dL | Kan Glikozu: 82 mg/dL | Total Bilirubin: 0.4 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "🛡️ Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["protein", "albümin", "globülin", "glutaraldehit", "saa"],
                "content": "Total Protein: 70 g/L | Albümin: 3.4 g/dL | Globülin: 3.6 g/dL | Glutaraldehit: >15 dakika | SAA: 15 µg/mL."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "⚡ Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "Na⁺: 141 mmol/L | K⁺: 4.3 mmol/L | Cl⁻: 102 mmol/L | Ca²⁺: 9.4 mg/dL | İnk. Fosfor: 5.0 mg/dL."
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "Kan pH: 7.41 | pO₂: 86 mmHg | pCO₂: 38 mmHg | HCO₃⁻: 24.0 mmol/L | Baz Açığı (BE): +0.5 mmol/L | Laktat: 1.1 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "sediment"],
                "content": "İdrar Spesifik Gravite: 1.020 | pH: 7.7 | Protein: (-) | Glikoz: (-) | Keton: (-) | Bilirubin: (-) | Sediment temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["histopatoloji", "biyopsi", "alerji"],
                "content": "Kutane Histopatoloji: Dermis tabakasında belirgin perivasküler eozinofil ve mast hücresi infiltrasyonu, dermal ödem."
            }
        }
    },
    "Vaka I (Fırtına)": {
        "kod": "VAKA_I",
        "sikayet": "Şiddetli inspiratorik hırıltı/ıslık sesi (stridor), ağzı açık nefes alma, öksürük ve boynu ileri uzatarak nefes alma.",
        "makroskopik_gorsel": {"fig": "Larenjit", "title": "Ağzı Açık Nefes Alma & Dispne", "file": "gorseller/larenjit_dispne.jpg"},
        "kesin_tani": "Akut Larenjit & Larenks Ödemi",
        "ayirici_tani": "Bronkopnömoni (Pnömonide akciğer alt sahalarında yaş rall/krepitasyon vardır; larenjitte akciğer temizdir, üst yolda stridor vardır).",
        "tedavi": "Hızlı etkili Kortikosteroid (Deksametazon 0.1-0.2 mg/kg IV larenks ödemini çözmek için), NSAID (Flunixin Meglumine), Soğuk buhar uygulaması, İleri asphyxia vakasında acil Trakeotomi.",
        "kontrendike": "Hayvanı yakalamak için boğazını sıkmak veya ağızdan zorla sıvı/ilaç içirmek (Drenching / Asfiksi riski!).",
        "categories": {
            "RASYON_YEM": {
                "name": "🌾 Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "toz", "saman", "drenching"],
                "content": "Kuru tozlu saman yemleme veya ağızdan zorla sıvı içirme (drenching) öyküsü."
            },
            "LOKASYON_RAKIM": {
                "name": "📍 Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil"],
                "content": "Kapalı havalandırması zayıf dana padoğu."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "1 gün önce dehorning (boynuz kesme) ve ağızdan ilaç içirme uygulaması yapılmıştır."
            },
            "ISTAH_DURUMU": {
                "name": "🍽️ İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yiyor mu", "su", "yutma", "dysphagia"],
                "content": "Dysphagia (Şiddetli yutma ağrısı) nedeniyle yem ve su yemeyi tamamen reddetme."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "stridor", "öksürük"],
                "content": "Vücut Sıcaklığı: 39.6 °C | Kalp Frekansı: 104 atım/dk | Solunum Frekansı: 46 nefes/dk (İnspiratorik Dispne) | Mukozalar: Siyanotik | CRT: 2.5 saniye | Larenks palpasyonunda şiddetli öksürük ve nefes darlığı krizi."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "stridor", "akciğer"],
                "content": "Kalp sesleri taşikardik. Üst solunum yolunda ve trakeada belirgin ıslık/hırıltı sesi (İnspiratorik Stridor). Akciğer parankimi temizdir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "retikulum", "trakea"],
                "content": "Larenks kıkırdaklarına hafif basıda hayvan başını sallar, şiddetli öksürük krizine girer (+)."
            },
            "HEMOGRAM": {
                "name": "🩸 Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lökosit", "rbc", "pcv", "fibrinojen"],
                "content": "RBC: 6.0 x10⁶/µL | Hb: 10.8 g/dL | PCV: %33 | WBC: 16.5 x10³/µL (Nötrofili) | Plazma Fibrinojeni: 580 mg/dL | PP/F: 12.1."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "🧪 Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["ast", "ggt", "alt", "alp", "ck", "ldh", "troponin"],
                "content": "AST: 62 U/L | GGT: 20 U/L | ALT: 16 U/L | CK: 105 U/L | LDH: 410 U/L | Troponin I: 0.01 ng/mL."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "🧬 Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["bun", "üre", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 20 mg/dL | Serum Kreatinin: 1.0 mg/dL | Kan Glikozu: 95 mg/dL (Stres hiperglisemisi) | Total Bilirubin: 0.5 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "🛡️ Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["protein", "albümin", "globülin", "glutaraldehit", "saa"],
                "content": "Total Protein: 74 g/L | Albümin: 3.2 g/dL | Globülin: 4.2 g/dL | Glutaraldehit: 6 dakika | SAA: 110 µg/mL."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "⚡ Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "Na⁺: 138 mmol/L | K⁺: 4.0 mmol/L | Cl⁻: 99 mmol/L | Ca²⁺: 9.0 mg/dL | İnk. Fosfor: 4.8 mg/dL."
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "Kan pH: 7.31 (Solunumsal Asidoz başlangıcı) | pO₂: 64 mmHg | pCO₂: 52 mmHg (Karbondioksit retansiyonu!) | HCO₃⁻: 25.5 mmol/L | Baz Açığı (BE): -1.0 mmol/L | Laktat: 2.4 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "sediment"],
                "content": "İdrar Spesifik Gravite: 1.021 | pH: 7.5 | Protein: (-) | Glikoz: (-) | Keton: (-) | Bilirubin: (-) | Sediment temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["endoskopi", "laringoskopi", "röntgen"],
                "content": "Endoskopi / Laringoskopi: Larenks mukozasında ve arytenoid kıkırdaklarda şiddetli hiperemi, ödem ve lümen darlığı. Akciğer radyografisinde parankim temizdir."
            }
        }
    },
    "Vaka J (Şahin)": {
        "kod": "VAKA_J",
        "sikayet": "Tek taraflı mukopürülan sarı-yeşil burun akıntısı, boynuz kaidesinde şişlik, başı duvara dayama ve baş ağrısı depresyonu.",
        "makroskopik_gorsel": {"fig": "Sinüzit", "title": "Tek Taraflı Pürülan Burun Akıntısı", "file": "gorseller/sinuzit_burun_akintisi.jpg"},
        "kesin_tani": "Frontal Sinüzit (Boynuz Kesimi / Dehorning Sekonder Bakteriyel Sinüzit)",
        "ayirici_tani": "Bronkopnömoni ve Plevritis (Sinüzitte burun akıntısı tek taraflıdır ve boynuz kaidesinde perküsyon matitesi vardır; pnömonide akıntı çift taraflı olup akciğer oskültasyon bulgusu vardır).",
        "tedavi": "Sinüs Trepanasyonu (Sinüs delinip pürülan eksudatın %0.9 NaCl ve Antiseptik solüsyonla yıkanması), Sistemik Parenteral Antibiyotik (Procaine Penicillin / Ceftiofur), NSAID (Meloksikam 0.5 mg/kg).",
        "kontrendike": "Tıkalı sinüs boşluğunu yıkamadan sadece yüzeysel antibiyotik vermek.",
        "categories": {
            "RASYON_YEM": {
                "name": "🌾 Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle"],
                "content": "Standart besi ve süt rasyonu verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "📍 Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "nakil"],
                "content": "Besi tesisi padoğunda barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "dehorning", "boynuz"],
                "content": "3 hafta önce açık yöntemle (testereyle) dehorning / boynuz kesimi yapılmıştır."
            },
            "ISTAH_DURUMU": {
                "name": "🍽️ İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yiyor mu", "su", "hiporeksi"],
                "content": "Şiddetli baş ağrısına bağlı iştahsızlık (Hiporeksi), başı duvara dayama."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "burun akıntısı", "boynuz"],
                "content": "Vücut Sıcaklığı: 39.4 °C | Kalp Frekansı: 86 atım/dk | Solunum Frekansı: 30 nefes/dk | Mukozalar: Pembe / hafif hiperemik | CRT: 1.8 saniye | Sağ burun deliğinden tek taraflı koyu sarı-yeşil kötü kokulu pürülan akıntı."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve akciğer oskültasyonu normaldir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "perküsyon", "matite", "sinüs"],
                "content": "Frontal sinüs bölgesi ve boynuz kaidesine perküsyon uygulandığında matite (tok ses) duyulur ve hayvan başını kaçırır (Ağrı +)."
            },
            "HEMOGRAM": {
                "name": "🩸 Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lökosit", "rbc", "pcv", "fibrinojen"],
                "content": "RBC: 5.9 x10⁶/µL | Hb: 10.2 g/dL | PCV: %31 | WBC: 18.8 x10³/µL (Sola kaymalı lökositoz) | Plazma Fibrinojeni: 620 mg/dL | PP/F: 11.5."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "🧪 Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["ast", "ggt", "alt", "alp", "ck", "ldh", "troponin"],
                "content": "AST: 58 U/L | GGT: 21 U/L | ALT: 17 U/L | CK: 90 U/L | LDH: 440 U/L | Troponin I: <0.01 ng/mL."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "🧬 Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["bun", "üre", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 17 mg/dL | Serum Kreatinin: 0.9 mg/dL | Kan Glikozu: 76 mg/dL | Total Bilirubin: 0.4 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "🛡️ Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["protein", "albümin", "globülin", "glutaraldehit", "saa"],
                "content": "Total Protein: 76 g/L | Albümin: 3.1 g/dL | Globülin: 4.5 g/dL | Glutaraldehit: 5 dakika | SAA: 180 µg/mL."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "⚡ Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "Na⁺: 139 mmol/L | K⁺: 4.1 mmol/L | Cl⁻: 101 mmol/L | Ca²⁺: 9.1 mg/dL | İnk. Fosfor: 4.7 mg/dL."
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "Kan pH: 7.39 | pO₂: 84 mmHg | pCO₂: 40 mmHg | HCO₃⁻: 23.9 mmol/L | Baz Açığı (BE): -0.2 mmol/L | Laktat: 1.3 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "sediment"],
                "content": "İdrar Spesifik Gravite: 1.022 | pH: 7.6 | Protein: (-) | Glikoz: (-) | Keton: (-) | Bilirubin: (-) | Sediment temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["röntgen", "radyografi", "kültür", "sinüs"],
                "content": "Kafatası Radyografisi (Röntgen): Frontal sinüs boşluğunda radyoopak pürülan sıvı seviyesi (Sıvı-gaz seviyesi). Sinüs Ponksiyon Kültürü: Trueperella pyogenes ve Pasteurella multocida üremesi."
            }
        }
    },
    "Vaka K (Rüzgar)": {
        "kod": "VAKA_K",
        "sikayet": "At hastada dinlenme halindeyken kendiliğinden (spontan) başlayan şiddetli burun kanaması (epistaksis), yutma zorluğu (dysphagia) ve Horner sendromu.",
        "makroskopik_gorsel": {"fig": "HavaKesesiMikozu", "title": "Spontan Burun Kanaması (Epistaksis)", "file": "gorseller/hava_kesesi_epistaksis.jpg"},
        "kesin_tani": "Hava Kesesi Mikozu (Guttural Pouch Mycosis – Aspergillus fumigatus)",
        "ayirici_tani": "Hava Kesesi Empiyemi (Empiyemde pürülan irinli akıntı vardır, epizodik fışkırır tarzda arteriyel epistaksis yoktur; mikozda damar erimesine bağlı şiddetli kanama vardır).",
        "tedavi": "Cerrahi Müdahale: İç Karotid Arter Transarteriyel Embolizasyonu (Coiling / Ligation), Sistemik ve Lokal Antifungal (İtrakonazol / Vorikonazol).",
        "kontrendike": "Cerrahi damar oklüzyonu yapmadan sadece tampon koymak (Arter eridiği için fatal iç kanamaya yol açar!).",
        "categories": {
            "RASYON_YEM": {
                "name": "🌾 Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "küf", "saman", "yulaf"],
                "content": "Küflü, nemli ortamda depolanmış yulaf ve tozlu kaba yem tüketim öyküsü."
            },
            "LOKASYON_RAKIM": {
                "name": "📍 Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "hara", "tavla"],
                "content": "Kapalı at harası / tavlası."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "2 haftadır devam eden hafif mukoz burun akıntısı sonrası aniden şiddetli kanama başlamıştır."
            },
            "ISTAH_DURUMU": {
                "name": "🍽️ İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yiyor mu", "su", "dysphagia", "regürjitasyon"],
                "content": "Dysphagia ve sinir felcine bağlı suyun ve yemin burundan geri gelmesi (Regürjitasyon), iştahsızlık."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "epistaksis", "kanama"],
                "content": "Vücut Sıcaklığı: 38.2 °C (At normali) | Kalp Frekansı: 68 atım/dk (Taşikardik) | Solunum Frekansı: 22 nefes/dk | Mukozalar: Soluk / anemi | CRT: 2.5 saniye | Burundan spontan taze kan gelmesi (Epistaksis), Horner sendromu."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp sesleri taşikardik. Akciğerlerde kan aspirasyonu riski nedeniyle alt sahalarda veziküler sesler artmış."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "viborg", "parotis"],
                "content": "Parotis bölgesi ve Viborg üçgeni hassas ve ağrılıdır."
            },
            "HEMOGRAM": {
                "name": "🩸 Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lökosit", "rbc", "pcv", "anemi", "fibrinojen"],
                "content": "RBC: 3.8 x10⁶/µL (Kan kaybı anemisi) | Hb: 7.5 g/dL | PCV: %23 | WBC: 14.2 x10³/µL | Plazma Fibrinojeni: 510 mg/dL."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "🧪 Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["ast", "ggt", "alt", "alp", "ck", "ldh", "troponin"],
                "content": "AST: 180 U/L | GGT: 28 U/L | ALT: 12 U/L | CK: 210 U/L | LDH: 620 U/L | Troponin I: 0.01 ng/mL."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "🧬 Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["bun", "üre", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 24 mg/dL | Serum Kreatinin: 1.2 mg/dL | Kan Glikozu: 90 mg/dL | Total Bilirubin: 0.8 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "🛡️ Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["protein", "albümin", "globülin", "glutaraldehit", "saa"],
                "content": "Total Protein: 62 g/L (Hipoproteinemi) | Albümin: 2.5 g/dL | Globülin: 3.7 g/dL | SAA: 140 µg/mL."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "⚡ Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "Na⁺: 137 mmol/L | K⁺: 3.7 mmol/L | Cl⁻: 98 mmol/L | Ca²⁺: 11.2 mg/dL (At için normal) | İnk. Fosfor: 3.5 mg/dL."
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "Kan pH: 7.36 | pO₂: 78 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 23.0 mmol/L | Baz Açığı (BE): -1.0 mmol/L | Laktat: 2.1 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "sediment"],
                "content": "İdrar Spesifik Gravite: 1.025 | pH: 7.5 | Protein: (-) | Glikoz: (-) | Keton: (-) | Bilirubin: (-) | Sediment temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["endoskopi", "guttural", "hava kesesi", "kültür", "aspergillus"],
                "content": "Guttural Pouch Endoskopisi: Hava kesesi çatı duvarında İç Karotid Arter üzerinde siyah-yeşil mantar plağı (Diphtheritic plaque) ve damar lümen erimesi. Kültür/Mantar İzolasyonu: Aspergillus fumigatus tespiti."
            }
        }
    },
    "Vaka L (Poyraz)": {
        "kod": "VAKA_L",
        "sikayet": "At hastada başı öne eğerken her iki burun deliğinden bol miktarda koyu pürülan (irinli) akıntı gelmesi ve Viborg üçgeninde ağrılı şişlik.",
        "makroskopik_gorsel": {"fig": "HavaKesesiEmpiyemi", "title": "İrinli Burun Akıntısı & Parotis Şişliği", "file": "gorseller/hava_kesesi_empiyem.jpg"},
        "kesin_tani": "Hava Kesesi Empiyemi (Guttural Pouch Empyema – Streptococcus equi subsp. equi)",
        "ayirici_tani": "Hava Kesesi Mikozu (Mikozda arterial kanama vardır; empiyemde koyu irinli akıntı ve kondroid pürülan taşlar vardır).",
        "tedavi": "Hava kesesi kateterizasyonu ve antiseptik solüsyonlarla lavajı, Kondroid pürülan taşlaşmış kitlelerin endoskopik/cerrahi çıkarılması, Sistemik Penisilin G tedavisi.",
        "kontrendike": "İrinli eksudatı drenaj yapmadan sadece semptomatik tedavi uygulamak.",
        "categories": {
            "RASYON_YEM": {
                "name": "🌾 Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle"],
                "content": "Standart at binek rasyonu verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "📍 Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "yer", "sevk", "hara"],
                "content": "Toplu barındırılan binek atı ahırı."
            },
            "GECMIS_HASTALIK": {
                "name": "📜 Geçmiş Hastalık & Sağlık Geçmişi",
                "keywords": ["geçmiş", "önceden", "hastalık", "gurm", "streptococcus"],
                "content": "1 ay önce geçirilmiş Gurm (Streptococcus equi) enfeksiyonu ve lenf yumrusu patlama öyküsü."
            },
            "ISTAH_DURUMU": {
                "name": "🍽️ İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yiyor mu", "su", "yutma", "dysphagia"],
                "content": "Dysphagia ve yutma ağrısı nedeniyle iştahsızlık, yem çiğnemede isteksizlik."
            },
            "VITAL_BULGULAR": {
                "name": "🩺 Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "pürülan", "akıntı", "viborg"],
                "content": "Vücut Sıcaklığı: 39.5 °C (Yüksek ateş) | Kalp Frekansı: 58 atım/dk | Solunum Frekansı: 20 nefes/dk | Mukozalar: Hiperemik | CRT: 2.0 saniye | Başı öne eğerken çift taraflı kremsi pürülan burun akıntısı, Viborg üçgeninde ağrılı şişlik."
            },
            "OSKULTASYON": {
                "name": "🎧 Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve akciğer oskültasyonu normaldir."
            },
            "AGRI_TESTLERI": {
                "name": "🔨 Retikulum, Perküsyon & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "parotis", "viborg"],
                "content": "Parotis ve Viborg üçgeni palpasyonunda ağrı ve fluktuasyon (+)."
            },
            "HEMOGRAM": {
                "name": "🩸 Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "cbc", "wbc", "lökosit", "rbc", "pcv", "fibrinojen"],
                "content": "RBC: 6.8 x10⁶/µL | Hb: 11.8 g/dL | PCV: %36 | WBC: 24.5 x10³/µL (Şiddetli Lökositoz) | Plazma Fibrinojeni: 780 mg/dL."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "🧪 Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["ast", "ggt", "alt", "alp", "ck", "ldh", "troponin"],
                "content": "AST: 95 U/L | GGT: 24 U/L | ALT: 15 U/L | CK: 120 U/L | LDH: 480 U/L | Troponin I: <0.01 ng/mL."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "🧬 Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["bun", "üre", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 21 mg/dL | Serum Kreatinin: 1.1 mg/dL | Kan Glikozu: 85 mg/dL | Total Bilirubin: 0.6 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "🛡️ Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["protein", "albümin", "globülin", "glutaraldehit", "saa"],
                "content": "Total Protein: 84 g/L | Albümin: 2.8 g/dL | Globülin: 5.6 g/dL | SAA: 420 µg/mL."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "⚡ Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor"],
                "content": "Na⁺: 138 mmol/L | K⁺: 4.0 mmol/L | Cl⁻: 100 mmol/L | Ca²⁺: 11.5 mg/dL | İnk. Fosfor: 3.8 mg/dL."
            },
            "KAN_GAZI": {
                "name": "🫁 Venöz / Arteriyel Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "hco3", "be", "laktat"],
                "content": "Kan pH: 7.38 | pO₂: 82 mmHg | pCO₂: 40 mmHg | HCO₃⁻: 23.5 mmol/L | Baz Açığı (BE): -0.5 mmol/L | Laktat: 1.4 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "🚽 Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "sediment"],
                "content": "İdrar Spesifik Gravite: 1.024 | pH: 7.6 | Protein: (-) | Glikoz: (-) | Keton: (-) | Bilirubin: (-) | Sediment temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "🔬 Görüntüleme, Mikrobiyoloji & Kültür",
                "keywords": ["endoskopi", "guttural", "kültür", "streptococcus"],
                "content": "Guttural Pouch Endoskopisi: Hava kesesi tabanında birikmiş pürülan eksudat kütlesi ve taşlaşmış katı irin konglomeratları (Chondroids). Bakteri Kültürü: Streptococcus equi subsp. equi üremesi."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnez & Bulgu Sorgulama Konsolu (Serbest Metin Sorgulama)</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde hazır şıklar <u>yoktur</u>. 
        Klinik şüphenize göre ne öğrenmek istiyorsanız kutucuğa <b>kendi cümlenizle veya kelimelerinizle</b> yazınız 
        (Örn: <i>"Rasyon bilgisi nedir?"</i>, <i>"Kalp sesleri nasıl?"</i>, <i>"Ateşi kaç derece?"</i>, <i>"Hemogram ve biyokimya sonuçları"</i>, <i>"Kan gazı analizi"</i>, <i>"Deri kazıntısı yapalım"</i>).
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

# AUTOMATIC DISPLAY OF CLEAN MACROSCOPIC CLINICAL IMAGES UPON CASE SELECTION
if "makroskopik_gorsel" in active_case:
    mg = active_case["makroskopik_gorsel"]
    img_p = find_gorsel_path(mg["file"])
    if img_p and os.path.exists(img_p):
        st.image(img_p, use_container_width=True)
    else:
        uploaded_img = st.file_uploader(
            f"📷 Klinik Görselini Yükleyiniz (.jpg / .png):",
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
        placeholder="Örn: Rasyon nedir?, Ateşi kaç?, Kalp sesleri nasıl?, Hemogram/biyokimya tahlilleri, Deri kazıntısı..."
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
        st.warning("⚠️ Eşleşen bilgi bulunamadı. Lütfen sorunuzu farklı kelimelerle yazınız.")

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
                <div class='card-content'><b>🩺 Bulgu / Öykü:</b> {item['content']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # CLEAN MICROSCOPIC IMAGES DISPLAYED ONLY AFTER BEING QUERY-TRIGGERED
        if "gorsel" in item:
            g = item["gorsel"]
            img_p = find_gorsel_path(g["file"])
            if img_p and os.path.exists(img_p):
                st.image(img_p, use_container_width=True)
            else:
                up_micro = st.file_uploader(
                    f"📷 Mikroskopik Görsel Yükleyiniz (.jpg / .png):",
                    type=["jpg", "jpeg", "png"],
                    key=f"up_micro_{item['cat_key']}"
                )
                if up_micro is not None:
                    st.image(up_micro, use_container_width=True)
else:
    st.info("Henüz bu vaka için soru sormadınız. Yukarıdaki arama kutusuna merak ettiğiniz soruyu yazarak muayeneye başlayınız.")

# Teacher Portal in Sidebar
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
            st.markdown(f"#### 🔑 {selected_case_name} Cevap Anahtarı")
            st.markdown(f"**• Kesin Tanı:** {active_case.get('kesin_tani', 'Belirtilmedi')}")
            st.markdown(f"**• Ayırıcı Tanı Kriteri:** {active_case.get('ayirici_tani', 'Belirtilmedi')}")
            st.markdown(f"**• Tedavi Protokolü:** {active_case.get('tedavi', 'Belirtilmedi')}")
            st.markdown(f"**• Kontrendike Müdahaleler:** {active_case.get('kontrendike', 'Belirtilmedi')}")
            
            st.markdown("---")
            if st.button("🔓 Tüm İpuçlarını Sınıf İçin Ekranda Aç"):
                st.session_state.history = []
                for ck, cv in active_case["categories"].items():
                    item_dict = {
                        "cat_key": ck,
                        "query": "Eğitmen Toplu Açımı",
                        "title": cv["name"],
                        "content": cv["content"]
                    }
                    if "gorsel" in cv:
                        item_dict["gorsel"] = cv["gorsel"]
                    st.session_state.history.append(item_dict)
                st.rerun()
        elif pass_code:
            st.error("Hatalı Şifre!")
