import os
import sys

# Script to build the master 12-case app with comprehensive laboratory and diagnostic test categories for every single case (A to L)

app_code = '''import streamlit as st
import re
import os

# Page Config
st.set_page_config(
    page_title="VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu",
    page_icon="🐄",
    layout="wide",
)

# Helper function to find images regardless of case or extension
def find_gorsel_path(base_file_path):
    if not base_file_path:
        return None
    if os.path.exists(base_file_path):
        return base_file_path
    
    # Check in gorseller/ or root directory
    dir_name, file_name = os.path.split(base_file_path)
    if not dir_name:
        dir_name = "gorseller"
    
    name_no_ext, _ = os.path.splitext(file_name)
    
    search_dirs = [dir_name, "gorseller", "."]
    valid_exts = [".jpg", ".png", ".jpeg", ".JPG", ".PNG", ".JPEG", ".webp"]
    
    for d in search_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                f_name_no_ext, f_ext = os.path.splitext(f)
                if f_name_no_ext.lower() == name_no_ext.lower() and f_ext.lower() in valid_exts:
                    return os.path.join(d, f)
    return None

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
        "tanim": "Traumatik Retikuloperikarditis (TRP)",
        "sikayet": "Yetiştirici İfadesi: 'Hocam 540 kiloluk Papatya isimli ineğimiz 3 gündür yememeye başladı, sütü bıçak gibi kesildi. Çenesinin altı ve gerdanı su toplamış gibi şişti. Yürümek istemiyor, sırtını kamburlaştırıp dikiliyor. Göğsünü tutunca inliyor...'",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba", "tel", "çivi", "yabancı"],
                "content": "İşletmede entansif kaba/yoğun yem karma rasyonu uygulanmaktadır. Balya parçalama esnasında kaba yeme inşaat tellerinin ve çivilerin karışmış olabileceği belirtilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi / Sürü Öyküsü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik", "dağ", "ova", "sürü"],
                "content": "Ceyhan ovasında (rakım ~50 metre) sabit süt tesisinde barındırılmaktadır. Yüksek rakım nakli veya mera değişimi öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce", "doğum"],
                "content": "Geçmişinde kronik hastalık öyküsü yoktur. 2 ay önce sorunsuz doğum yapmıştır. Son 3 günde akut iştahsızlık ve süt veriminde %85 düşüş gelişmiştir."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yeme", "geviş", "yutma", "su içme", "anoreksi", "hiporeksi"],
                "content": "Tam anoreksi (iştah tamamen durmuş). Geviş getirme refleksleri durmuş, Rumen hareketleri yok denecek kadar zayıf (0-1 atım/3 dk)."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "ödem", "gerdan", "jugular"],
                "content": "Vücut Sıcaklığı: 39.8 °C (Subfebril/Yüksek) | Kalp Frekansı: 102 atım/dk (Taşikardi) | Solunum Frekansı: 42 nefes/dk (Yüzeyel kesik solunum) | Mukoza: Soluk pembe | CRT: 2.5 saniye | Dehidrasyon: %6 | Gerdan ve submandibuler bölgede soğuk hamur ödem | Vena jugularis stazı +, yalancı jugular nabız +."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Perikardiyal kese içinde gaz ve pürülan sıvının çalkalanmasına bağlı karakteristik çamaşır makinesi / su çalkantı sesi (splashing sound) ve boğuk kalp sesleri (muffled heart sounds) duyuluyor. Akciğer Oskültasyonu: Ventro-lateral alanlarda solunum sesleri hafif azalmış."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "kalp", "cidago"],
                "content": "Retikulum Ağrı Testleri: Cidago sıkıştırma (Withers pinch) +, Sopa/Kama muayenesi +, Kalp bölgesi perküsyonunda şiddetli inleme ve ağrı reaksiyonu +."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "nötrofil", "lökositoz"],
                "content": "Eritrosit (RBC): 5.8 x10⁶/µL | Hemoglobin (Hb): 9.8 g/dL | Hematokrit (PCV): %31 | Lökosit (WBC): 22.4 x10³/µL (Şiddetli Lökositoz, sola kayma) | Nötrofil: %78 | Lenfosit: %18 | Plazma Fibrinojeni: 1250 mg/dL (Aşırı Yüksek) | PP/F Oranı: 6.3 (<10 - Şiddetli Aktif Fibrinöz Yangı)."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "gldh"],
                "content": "AST: 185 U/L (Hafif yüksek - karaciğer pasif stazı) | GGT: 48 U/L | ALT: 32 U/L | ALP: 110 U/L | CK: 210 U/L | LDH: 480 U/L."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["üre", "bun", "kreatinin", "glikoz", "bilirubin", "trigliserid"],
                "content": "BUN (Üre): 38 mg/dL | Kreatinin: 1.4 mg/dL | Glikoz: 68 mg/dL | Total Bilirubin: 1.1 mg/dL | Direkt Bilirubin: 0.4 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["albümin", "globülin", "total protein", "tp", "glutaraldehit", "pıhtılaşma"],
                "content": "Total Protein: 8.2 g/dL | Albümin: 2.8 g/dL | Globülin: 5.4 g/dL (Hipergamaglobulinemi) | Glutaraldehit Pıhtılaşma Testi: 1.5 dakikada pozitif pıhtılaşma (<3 dk - Akut Şiddetli Yangı)."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "magnezyum", "na", "k", "cl", "ca"],
                "content": "Sodyum (Na⁺): 138 mmol/L | Potasyum (K⁺): 3.9 mmol/L | Klor (Cl⁻): 98 mmol/L | Kalsiyum (Ca²⁺): 8.8 mg/dL | İnorganik Fosfor: 4.5 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.32 | pO₂: 58 mmHg (Hafif Hipoksi) | pCO₂: 46 mmHg | HCO₃⁻: 20.2 mmol/L | Baz Açığı (BE): -4.5 mmol/L | Laktat: 2.8 mmol/L (Hafif Doku Hipoksisi)."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "ph", "proteinüri", "glikozüri", "ketonüri", "bilirubinüri", "hematüri", "sediment"],
                "content": "İdrar Dansitesi: 1.026 | İdrar pH: 7.5 | Proteinüri: +1 (Hafif) | Glikozüri: Negatif | Ketonüri: Negatif | Bilirubinüri: Negatif | Mikrohematüri: Negatif | Mikroskopik Sediment: İki üç lökosit, nadir yassı epitel hücreleri."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme & Mikrobiyoloji / Perikardiyosentez",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "perikardiyosentez", "röntgen"],
                "content": "Ultrasonografi (Torakal/Retiküler): Perikardiyal kese içinde 5 cm kalınlığında fibrin bantları ve hiperekojen gaz kabarcıkları içeren bol pürülan sıvı birikimi. Retikulum duvarında 4 cm'lik kılıflı yabancı cisim yolu. Perikardiyosentez: Kötü kokulu, bulanık, pürülan exsudat. Kültür: Trueperella pyogenes ve anaerob enfeksiyon üremesi."
            }
        }
    },
    "Vaka B (Yonca)": {
        "kod": "VAKA_B",
        "tanim": "Vejetatif Valvüler Endokardit (Triküspid Kapak)",
        "sikayet": "Yetiştirici İfadesi: 'Hocam 580 kiloluk Yonca isimli ineğimiz haftalardır bir iyileşip bir hastalanıyor. Antibiyotik yapıyoruz ateşi düşüyor, ilaç bitince tekrar 40 dereceye fırlıyor. Zayıfladı, bazen de ön bacağına basamayıp topallıyor...'",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "mısır", "arpa", "ot", "silaj", "balya", "saman"],
                "content": "Standart süt sığırı rasyonu verilmektedir. Yem kalitesi normaldir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi / Sürü Öyküsü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "sürü"],
                "content": "Sabit bağlı ahır işletmesidir. Rakım değişikliği yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "geçirdi", "önce", "ayak", "tırnak"],
                "content": "3 ay önce geçirilmiş ağır kronik purulent metritis ve kronik tırnak arası apse (interdigital phlegmon) öyküsü vardır. Tekrarlayan fluktuan ateş atakları görülmektedir."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yeme", "geviş", "anoreksi", "hiporeksi"],
                "content": "Değişken (ondülan) hiporeksi. Ateş yükseldiğinde yem yemeyi bırakıyor, ateş düşünce az az yiyor."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "ödem", "topallık", "eklem"],
                "content": "Vücut Sıcaklığı: 40.1 °C (Dirençli Fluktuan Ateş) | Kalp Frekansı: 110 atım/dk | Solunum Frekansı: 38 nefes/dk | Mukozalar: Soluk ve fokal peteşili | CRT: 2.8 saniye | Gerdanda ödem hafif, Vena jugularis dolgun, gerçek sistolik jugular nabız +, sol ön eklemde şişlik ve topallık +."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "systolic", "triküspid", "rall"],
                "content": "Kalp Oskültasyonu: Sağ 4. interkostal aralıkta (Triküspid kapak odağı) çok şiddetli (Grade 5/6) pansistolik üfürüm (systolic murmur) duyuluyor. Akciğer Oskültasyonu: Bilateral hafif sertleşmiş veziküler solunum sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testlerinin tamamı NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "anemi", "pp/f"],
                "content": "Eritrosit (RBC): 3.9 x10⁶/µL (Anemi) | Hemoglobin (Hb): 7.2 g/dL | Hematokrit (PCV): %22 | Lökosit (WBC): 26.8 x10³/µL (Şiddetli Lökositoz) | Nötrofil: %82 | Plazma Fibrinojeni: 1150 mg/dL | PP/F Oranı: 5.8 (<10 - Aktif Şiddetli Yangı)."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "troponin"],
                "content": "AST: 142 U/L | GGT: 38 U/L | ALT: 28 U/L | ALP: 160 U/L | CK: 180 U/L | Kardiyak Troponin I: 0.85 ng/mL (Yüksek - Miyokardiyal tutulum/hasar)."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["üre", "bun", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 42 mg/dL | Kreatinin: 1.6 mg/dL | Glikoz: 72 mg/dL | Total Bilirubin: 0.9 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["albümin", "globülin", "total protein", "tp", "glutaraldehit"],
                "content": "Total Protein: 8.8 g/dL | Albümin: 2.2 g/dL (Hipoalbüminei) | Globülin: 6.6 g/dL (Şiddetli Hipergamaglobulinemi) | Glutaraldehit Testi: 1 dakikada pozitif pıhtılaşma."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "na", "k", "cl"],
                "content": "Sodyum (Na⁺): 136 mmol/L | Potasyum (K⁺): 3.7 mmol/L | Klor (Cl⁻): 96 mmol/L | Kalsiyum (Ca²⁺): 8.2 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.34 | pO₂: 68 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 21.5 mmol/L | Baz Açığı: -3.2 mmol/L | Laktat: 3.1 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "ph", "proteinüri", "hematüri", "sediment", "böbrek", "emboli"],
                "content": "İdrar Dansitesi: 1.022 | İdrar pH: 7.0 | Proteinüri: +2 | Mikrohematüri: +2 (Aşırı eritrosit - Septik Emboli / Fokal Glomerulonefrit) | Mikroskopik Sediment: Bol taze eritrosit ve granüler silindirler."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme & Mikrobiyoloji / Ekokardiyografi",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "vejetasyon", "kapak"],
                "content": "Ekokardiyografi (Sağ Interkostal Pencere): Triküspid kapak yaprakçıkları üzerinde 3.5 cm çapında karnabahar görünümünde hiperekojen vejetatif kitle (vegetation). Kan Kültürü: Trueperella pyogenes / Streptococcus dysgalactiae üretilmiştir."
            }
        }
    },
    "Vaka C (Zümrüt)": {
        "kod": "VAKA_C",
        "tanim": "Cor Pulmonale / Yüksek Rakım Hastalığı (Brisket Disease)",
        "sikayet": "Yetiştirici İfadesi: 'Hocam 460 kiloluk Zümrüt isimli düvemizi 1 ay önce Toros dağlarındaki yüksek yaylaya (rakım 2400 m) çıkardık. Hayvanın gerdanı ve bacak arası su topladı, gözleri fırladı. Ateşi yok ama azıcık yürüyünce nefes nefese kalıyor...'",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "ot", "mera", "yayla"],
                "content": "Yayla merasında otlamaktadır. Ek yoğun yem verilmemektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi / Sürü Öyküsü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "yükseklik", "dağ"],
                "content": "1 ay önce Ceyhan ovasından (rakım 50 m) Toros dağlarındaki yüksek yaylaya (rakım 2400 m) nakledilmiştir. Yüksek hipobarik hipoksiye maruz kalmıştır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "geçirdi"],
                "content": "Geçmişinde enfeksiyöz veya mekanik hastalık kaydı yoktur."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yeme", "geviş", "anoreksi"],
                "content": "Efor sarf ettiğinde çabuk yoruluyor ve yemeyi bırakıyor. Dinlenirken az miktarda merada otluyor."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "ödem", "gerdan"],
                "content": "Vücut Sıcaklığı: 38.6 °C (TAMAMEN NORMAL) | Kalp Frekansı: 96 atım/dk | Solunum Frekansı: 46 nefes/dk (Dispneik) | Mukoza: Siyanotik/Koyu pembe | CRT: 2.2 saniye | Gerdan, göğüs altı ve ventral karın bölgesinde geniş soğuk hamur ödem, Vena jugularis aşırı dolgun ve stazlı."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "hiperdinamik", "rall"],
                "content": "Kalp Oskültasyonu: Hiperdinamik güçlü kalp sesleri. Herhangi bir perikardiyal çalkantı sesi veya endokardiyal üfürüm YOKTUR. Akciğer Oskültasyonu: Veziküler solunum sesleri hafif sertleşmiş."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testlerinin tamamı NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "polisitemi", "pp/f"],
                "content": "Eritrosit (RBC): 10.8 x10⁶/µL (Şiddetli Kompenzatuvar Polisitemi) | Hemoglobin (Hb): 17.2 g/dL | Hematokrit (PCV): %54 (Aşırı Yüksek) | Lökosit (WBC): 7.2 x10³/µL (TAMAMEN NORMAL) | Plazma Fibrinojeni: 320 mg/dL (NORMAL) | PP/F Oranı: 22.8 (>15 - Yangı Yoktur)."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh"],
                "content": "AST: 68 U/L (Normal) | GGT: 18 U/L (Normal) | ALT: 22 U/L | ALP: 95 U/L | CK: 110 U/L."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["üre", "bun", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 18 mg/dL | Kreatinin: 0.9 mg/dL | Glikoz: 64 mg/dL | Total Bilirubin: 0.6 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["albümin", "globülin", "total protein", "tp", "glutaraldehit"],
                "content": "Total Protein: 7.3 g/dL | Albümin: 3.2 g/dL | Globülin: 4.1 g/dL | Glutaraldehit Pıhtılaşma Testi: 12 dakikada NEGATİF (Yangı bulunmamaktadır)."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "na", "k", "cl"],
                "content": "Sodyum (Na⁺): 140 mmol/L | Potasyum (K⁺): 4.2 mmol/L | Klor (Cl⁻): 102 mmol/L | Kalsiyum (Ca²⁺): 9.4 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "hipoksi"],
                "content": "Kan pH: 7.36 | pO₂: 48 mmHg (Şiddetli Arteriyel/Venöz Hipoksi) | pCO₂: 42 mmHg | HCO₃⁻: 23.5 mmol/L | Baz Açığı: -0.8 mmol/L | Laktat: 1.5 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "ph", "proteinüri", "glikozüri", "ketonüri", "bilirubinüri", "hematüri", "sediment"],
                "content": "İdrar Dansitesi: 1.028 | İdrar pH: 8.0 | Proteinüri: Negatif | Glikozüri: Negatif | Ketonüri: Negatif | Bilirubinüri: Negatif | Mikrohematüri: Negatif | Mikroskopik Sediment: Temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme & Mikrobiyoloji / Ekokardiyografi",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "pulmoner", "sağ ventrikül"],
                "content": "Ekokardiyografi: Sağ ventrikül serbest duvar kalınlığında belirgin artış (Sağ Ventrikül Hipertrofisi), pulmoner arter çapında vazokonstriksiyona sekonder belirgin genişleme. Perikard ve kanda Bakteriyel Üreme YOKTUR (Steril)."
            }
        }
    },
    "Vaka D (Yiğit)": {
        "kod": "VAKA_D",
        "tanim": "Vena Cava Caudalis Trombozu Sendromu (VCCT)",
        "sikayet": "Yetiştirici İfadesi: 'Hocam 620 kiloluk Yiğit isimli besi tosunumuz padoğunda aniden ağzından ve burnundan foşur foşur fışkırır tarzda parlak kırmızı kan akıtmaya başladı! Hayvanın gözleri bembeyaz oldu, dışkısı da zift gibi simsiyah çıkıyor...'",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "besi", "kaba"],
                "content": "18 aylık besi danasıdır. Yoğun mısır ve arpa kırması ağırlıklı, kaba yemi aşırı yetersiz yüksek nişastalı besi rasyonu verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi / Sürü Öyküsü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "sürü"],
                "content": "Besi padoğunda barındırılmaktadır. Rakım değişikliği yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "geçirdi", "asidoz", "şişkinlik", "timpani", "rumenitis"],
                "content": "Geçmişinde tekrarlayan subakut rumen asidozu (SARA / yem çarpması) ve kronik hafif rumen timpani (şişkinlik) öyküsü vardır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yeme", "geviş", "anoreksi"],
                "content": "Akut kan krizinden sonra tam anoreksi ve halsizlik."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "hemoptizi", "melena", "kan"],
                "content": "Vücut Sıcaklığı: 39.2 °C | Kalp Frekansı: 118 atım/dk (Aşırı Taşikardi) | Solunum Frekansı: 52 nefes/dk | Ağız/Burun: Köpüklü taze parlak kırmızı kan fışkırması (Hemoptizi) | Mukozalar: Bembeyaz (Ağır Anemi) | CRT: 4.0 saniye | Dışkı: Siyah katran kıvamında (Melena)."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "rall", "hışırtı", "akciğer"],
                "content": "Kalp Oskültasyonu: Taşikardik, zayıf düşen kalp sesleri. Akciğer Oskültasyonu: Akciğer alanlarında yaygın kaba raller ve kan pıhtılarına sekonder hışırtı sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testleri NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "anemi", "pp/f"],
                "content": "Eritrosit (RBC): 2.1 x10⁶/µL (Kritik Masif Kan Kaybı Anemisi) | Hemoglobin (Hb): 4.2 g/dL | Hematokrit (PCV): %12 (Acil Transfüzyon Eşiği!) | Lökosit (WBC): 21.5 x10³/µL | Plazma Fibrinojeni: 1050 mg/dL | PP/F Oranı: 7.23."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh"],
                "content": "AST: 210 U/L (Karaciğer apsesine sekonder parankim hasarı) | GGT: 68 U/L (Safra kanalı/karaciğer) | ALT: 45 U/L | ALP: 210 U/L | CK: 160 U/L."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["üre", "bun", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 42 mg/dL | Kreatinin: 1.6 mg/dL | Glikoz: 88 mg/dL | Total Bilirubin: 1.2 mg/dL | Direkt Bilirubin: 0.5 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["albümin", "globülin", "total protein", "tp", "glutaraldehit"],
                "content": "Total Protein: 7.6 g/dL | Albümin: 2.6 g/dL | Globülin: 5.0 g/dL | Glutaraldehit Testi: 2 dakikada pozitif pıhtılaşma."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "na", "k", "cl"],
                "content": "Sodyum (Na⁺): 134 mmol/L | Potasyum (K⁺): 3.5 mmol/L | Klor (Cl⁻): 94 mmol/L | Kalsiyum (Ca²⁺): 7.9 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.24 (Metabolik Asidoz) | pO₂: 52 mmHg | pCO₂: 50 mmHg | HCO₃⁻: 18.5 mmol/L | Baz Açığı (BE): -6.2 mmol/L | Laktat: 4.2 mmol/L (Şiddetli Doku Perfüzyon Bozukluğu)."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "ph", "proteinüri", "hematüri", "sediment"],
                "content": "İdrar Dansitesi: 1.024 | İdrar pH: 6.5 | Proteinüri: +1 | Mikrohematüri: Negatif (Mikroskopik eritrosit yok - kanama böbrek/üriner sistemden değil, akciğer yırtılmasından kaynaklanıp yutularak dışkıya geçmiştir)."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme & Mikrobiyoloji / Ultrasonografi",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "karaciğer", "apse", "vena cava", "trombüs", "arter", "anevrizma"],
                "content": "Abdominal Ultrasonografi: Karaciğer parankiminde 6 cm çapında kılıflı apse odağı (Hepatic Abscess), Vena Cava Caudalis lümeninde tıkayıcı trombüs ekojenitesi. Torakal USG: Pulmoner arter çevresinde hematom ve anevrizma yırtılması alanları."
            }
        }
    },
    "Vaka E (Kudret)": {
        "kod": "VAKA_E",
        "tanim": "Trikofiti / Dermatophytosis (Trichophyton verrucosum)",
        "sikayet": "Yetiştirici İfadesi: 'Hocam 220 kiloluk Kudret isimli danamızın baş, göz çevresi ve boyun bölgesinde yuvarlak yuvarlak, gri kireç gibi kabuklar çıktı. Tüyleri döküldü ama hiç kaşınmıyor, ne bir ateş var ne keyifsizlik...'",
        "makroskopik_gorsel": {
            "fig": "Figure 1.2-1",
            "title": "Klinik Mantar Lezyonu (Baş ve Göz Çevresi)",
            "file": "gorseller/figure_1_2_1.jpg",
            "desc": "Göz çevresi, baş ve boyunda dairesel, grimsi-beyaz kireç benzeri kabarık kabuklanma ve alopezi (tüy kaybı)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "ot", "saman", "vitamin", "a vitamini"],
                "content": "A Vitamini ve mineral bakımından yetersiz, rutubetli ve güneş görmeyen kapalı pedokta beslenmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi / Sürü Öyküsü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sürü", "ahır", "kalabalık"],
                "content": "Kapalı, nemli ve kalabalık genç dana padoğunda barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Sütten kesim sonrası bağışıklık stresi yaşamıştır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yeme", "geviş"],
                "content": "İştah ve geviş getirme TAMAMEN NORMALdir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "deri", "kabuk", "kaşıntı"],
                "content": "Vücut Sıcaklığı: 38.7 °C (NORMAL) | Kalp Frekansı: 76 atım/dk | Solunum Frekansı: 24 nefes/dk | Mukozalar: Pembe | CRT: 1.5 saniye | Deri Muayenesi: Baş, göz çevresi ve boyunda dairesel, gri-beyaz kireçimsi kabuklu alopezik lezyonlar. Kaşıntı YOKtur veya minimaldir."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve akciğer oskültasyonu TAMAMEN NORMALdir."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testleri NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv"],
                "content": "Eritrosit (RBC): 6.8 x10⁶/µL | Hemoglobin (Hb): 11.2 g/dL | Hematokrit (PCV): %35 | Lökosit (WBC): 8.4 x10³/µL (NORMAL) | Plazma Fibrinojeni: 350 mg/dL (NORMAL)."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck"],
                "content": "AST: 62 U/L | GGT: 21 U/L | ALT: 25 U/L | ALP: 115 U/L | CK: 95 U/L (Tüm organ enzim değerleri normal sınırlardadır)."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["üre", "bun", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 15 mg/dL | Kreatinin: 0.8 mg/dL | Glikoz: 68 mg/dL | Total Bilirubin: 0.4 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["albümin", "globülin", "total protein", "tp", "glutaraldehit"],
                "content": "Total Protein: 6.8 g/dL | Albümin: 3.2 g/dL | Globülin: 3.6 g/dL | Glutaraldehit Testi: 15 dakikada NEGATİF."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "na", "k", "cl"],
                "content": "Sodyum (Na⁺): 139 mmol/L | Potasyum (K⁺): 4.4 mmol/L | Klor (Cl⁻): 101 mmol/L | Kalsiyum (Ca²⁺): 9.2 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be"],
                "content": "Kan pH: 7.38 | pO₂: 88 mmHg | pCO₂: 40 mmHg | HCO₃⁻: 24.2 mmol/L | Baz Açığı: +0.2 mmol/L (Tamamen normal)."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "ph", "proteinüri", "glikozüri", "sediment"],
                "content": "İdrar Dansitesi: 1.022 | İdrar pH: 8.0 | Proteinüri: Negatif | Glikozüri: Negatif | Mikroskopik Sediment: Temiz."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "Deri Kazıntısı & Mikroskopik Mantar Teşhisi",
                "keywords": ["mikroskop", "kazıntı", "deri kazıntısı", "koh", "mantar", "artrospor", "lam", "spor"],
                "gorsel": {
                    "fig": "Figure 1.2-11",
                    "title": "Mikroskopik Mantar Sporu (%10 KOH Hazırlığı)",
                    "file": "gorseller/figure_1_2_11.jpg",
                    "desc": "%10 KOH ile muamele edilmiş deri kazıntısında kıl şaftını saran küresel Trichophyton verrucosum ektotriks artrospor dizilimi (40x)."
                },
                "content": "%10 KOH ile hazırlanan deri kazıntısında kırık kıl şaftının etrafını zırh gibi saran küresel Trichophyton verrucosum ektotriks artrospor zincirleri belirgin olarak teşhis edilmiştir."
            }
        }
    },
    "Vaka F (Nazar)": {
        "kod": "VAKA_F",
        "tanim": "Sarkoptik Uyuz / Scabies (Sarcoptes scabiei var. bovis)",
        "sikayt": "Yetiştirici İfadesi: 'Hocam 380 kiloluk Nazar isimli ineğimiz dur durak bilmeden kendini demirlere, duvarlara sürtüyor! Boynu ve kulaklarının arkası fil derisi gibi kalınlaştı, kanatana kadar kaşıyor, kaşınmaktan yem yemeyi unuttu...'",
        "makroskopik_gorsel": {
            "fig": "Figure 1.3-13 & 1.3-15",
            "title": "Klinik Uyuz Lezyonu (Deride Kalınlaşma ve Likenifikasyon)",
            "file": "gorseller/figure_1_3_13.jpg",
            "desc": "Kulak kepçesi, boyun ve sırtta derinin fil derisi gibi kalınlaşması (likenifikasyon), kaşıntı ekskoryasyonları ve kepekli döküntü."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "ot", "saman"],
                "content": "Standart kaba ve kesif yem verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi / Sürü Öyküsü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sürü", "ahır", "bulaşma"],
                "content": "Sürüye yeni katılan dışarıdan gelme bir inekle temas öyküsü vardır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Geçmişinde kronik iç hastalık öyküsü yoktur. Şiddetli kaşıntı 2 hafta önce başlamıştır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yeme", "geviş", "anoreksi", "hiporeksi"],
                "content": "Huzursuzluk ve sürekli kaşınma nedeniyle belirgin hiporeksi (iştah azalması)."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "deri", "kaşıntı", "likenifikasyon"],
                "content": "Vücut Sıcaklığı: 38.9 °C | Kalp Frekansı: 82 atım/dk | Solunum Frekansı: 28 nefes/dk | Mukozalar: Pembe | CRT: 1.8 saniye | Deri Muayenesi: Baş, kulak, boyun ve sırtta derinin şiddetli kalınlaşması (likenifikasyon), oluklaşma, ekskoryasyon (kaşıntı tırnak izleri) ve kepeneklenme. ŞİDDETLİ KAŞINTI +."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve akciğer oskültasyonu NORMALdir."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testleri NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "eozinofil", "eozinofili"],
                "content": "Eritrosit (RBC): 6.2 x10⁶/µL | Hemoglobin (Hb): 10.8 g/dL | Hematokrit (PCV): %33 | Lökosit (WBC): 12.8 x10³/µL | Nötrofil: %52 | Eozinofil: %14 (Aşırı Eozinofili - Paraziter/Paraziter Allerjik Yanıt) | Plazma Fibrinojeni: 480 mg/dL."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck"],
                "content": "AST: 72 U/L | GGT: 24 U/L | ALT: 28 U/L | ALP: 120 U/L | CK: 130 U/L."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["üre", "bun", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 18 mg/dL | Kreatinin: 0.9 mg/dL | Glikoz: 62 mg/dL | Total Bilirubin: 0.5 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["albümin", "globülin", "total protein", "tp", "glutaraldehit"],
                "content": "Total Protein: 7.2 g/dL | Albümin: 3.1 g/dL | Globülin: 4.1 g/dL | Glutaraldehit Testi: 10 dakikada NEGATİF."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "na", "k", "cl"],
                "content": "Sodyum (Na⁺): 138 mmol/L | Potasyum (K⁺): 4.1 mmol/L | Klor (Cl⁻): 99 mmol/L | Kalsiyum (Ca²⁺): 9.0 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be"],
                "content": "Kan pH: 7.37 | pO₂: 86 mmHg | pCO₂: 41 mmHg | HCO₃⁻: 23.8 mmol/L | Baz Açığı: -0.2 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "ph", "proteinüri", "glikozüri", "sediment"],
                "content": "İdrar Dansitesi: 1.024 | İdrar pH: 8.0 | Proteinüri: Negatif | Glikozüri: Negatif | Mikroskopik Sediment: Temiz."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "Derin Deri Kazıntısı & Akar Mikroskopisi",
                "keywords": ["mikroskop", "kazıntı", "deri kazıntısı", "akar", "uyuz", "mineral yağ", "sarcoptes", "lam"],
                "gorsel": {
                    "fig": "Figure 1.3-18",
                    "title": "Mikroskopik Sarcoptes Scabiei Akari",
                    "file": "gorseller/figure_1_3_18.jpg",
                    "desc": "Derin deri kazıntısında mineral yağ altında tespit edilen canlı ergin Sarcoptes scabiei akarı (10x-40x)."
                },
                "content": "Kapiller kanama görülünceye kadar alınan derin deri kazıntısında mineral yağ altında canlı Sarcoptes scabiei var. bovis ergin akarları, oval yumurtalar ve karakteristik siyah dışkı peletleri (scybala) tespit edilmiştir."
            }
        }
    },
    "Vaka G (Çiçek)": {
        "kod": "VAKA_G",
        "tanim": "Hepatojen (Sekonder) Fotosensitizasyon",
        "sikayet": "Yetiştirici İfadesi: 'Hocam 450 kiloluk Çiçek isimli ineğimizi yeşil meraya çıkardık. Hayvanın YALNIZCA BEYAZ tüylü deri bölgelerinde, özellikle boyun, omuz ve sırtındaki beyaz alanlarda müthiş bir güneş yanığı ve hamur ödemi gelişti! Boyun bölgesindeki beyaz derisi tabaka tabaka soyuluyor, boynuna dokunmaya kalksak ağrıdan çıldırıyor, siyah derisine ise zerre kadar bir şey olmadı...'",
        "makroskopik_gorsel": {
            "fig": "Figure 1.7-35",
            "title": "Hepatojen Fotosensitizasyon (Boyun ve Beyaz Deri Nekrozu)",
            "file": "gorseller/figure_1_7_35.jpg",
            "desc": "Yalnızca boyun, omuz ve sırttaki beyaz (pigmentsiz) deri alanlarında soyulma, hamur ödemi, hipersensitivite ve nekroz; siyah pigmentli derinin tamamen sağlam kalması."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "klorofil", "yeşil ot", "mera", "zehirli ot", "lantana", "mantar"],
                "content": "Klorofil bakımından zengin taze taze yeşil ot ve otlatma merası tüketilmiştir. Merada sporidesmin veya hepatotoksik bitki içeriği öyküsü vardır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi / Sürü Öyküsü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sürü", "mera", "güneş"],
                "content": "Güneşli merada otlama öyküsü vardır. Dik güneş ışığına maruz kalmıştır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "karaciğer", "sarılık"],
                "content": "Geçmişte subklinik karaciğer/safra yolu stazı öyküsü bulunmaktadır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yeme", "geviş", "anoreksi", "hiporeksi"],
                "content": "Işıktan kaçma (fotofobi), huzursuzluk ve boyun bölgesindeki şiddetli hipersensitivite nedeniyle belirgin anoreksi."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "ikter", "sarılık", "crt", "deri", "boyun", "ödem", "hipersensitivite"],
                "content": "Vücut Sıcaklığı: 39.4 °C | Kalp Frekansı: 92 atım/dk | Solunum Frekansı: 36 nefes/dk | Mukozalar: Belirgin İkterik / Sarılık (Bilirubinüriye bağlı) | CRT: 2.2 saniye | Deri Muayenesi: YALNIZCA BEYAZ (pigmentsiz) deri alanlarında, özellikle boyun, omuz ve sırtta hamur ödemi, derinin sertleşip tabaka halinde soyulması (sloughing/nekroz) ve boyun bölgesinde ŞİDDETLİ HİPERSENSİTİVİTE / DOKUNMA AĞRISI. Siyah deri alanları tamamen NORMAL."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve akciğer oskültasyonu normal sınırlar içindedir."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "boyun"],
                "content": "Retikulum ağrı testleri NEGATİF. Ancak boyun ve sırt deri palpasyonunda aşırı ağrı ve refleks yanıtı (+)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv"],
                "content": "Eritrosit (RBC): 6.1 x10⁶/µL | Hemoglobin (Hb): 10.5 g/dL | Hematokrit (PCV): %32 | Lökosit (WBC): 14.2 x10³/µL (Ilımlı Lökositoz) | Plazma Fibrinojeni: 580 mg/dL."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "karaciğer", "safra"],
                "content": "AST: 280 U/L (Aşırı Yüksek - Karaciğer Parankim Hasarı) | GGT: 185 U/L (Aşırı Yüksek - Kolestaz / Safra Yolu Tıkanması) | ALP: 420 U/L (Yüksek) | ALT: 52 U/L | CK: 140 U/L."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["üre", "bun", "kreatinin", "glikoz", "bilirubin", "ikter", "filloeritrin"],
                "content": "Total Bilirubin: 3.8 mg/dL (Aşırı Yüksek - Şiddetli İkter) | Direkt Bilirubin: 1.7 mg/dL | İndirekt Bilirubin: 2.1 mg/dL | BUN: 22 mg/dL | Kreatinin: 1.0 mg/dL | Serum Filloeritrin Düzeyi: AŞIRI YÜKSEK (Safra yolu atılım bozukluğuna sekonder)."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["albümin", "globülin", "total protein", "tp", "glutaraldehit"],
                "content": "Total Protein: 6.2 g/dL | Albümin: 2.4 g/dL (Karaciğer sentez azalmasına sekonder Hipoalbüminemi) | Globülin: 3.8 g/dL | Glutaraldehit Testi: 6 dakikada pozitif."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "na", "k", "cl"],
                "content": "Sodyum (Na⁺): 137 mmol/L | Potasyum (K⁺): 3.8 mmol/L | Klor (Cl⁻): 97 mmol/L | Kalsiyum (Ca²⁺): 8.4 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be"],
                "content": "Kan pH: 7.36 | pO₂: 84 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 22.8 mmol/L | Baz Açığı: -1.2 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "ph", "proteinüri", "bilirubinüri", "çay rengi", "sediment"],
                "content": "İdrar Dansitesi: 1.022 | İdrar pH: 7.5 | Bilirubinüri: +3 (Koyu çay/bira rengi idrar - Patognomonik!) | Proteinüri: +1 | Glikozüri: Negatif | Mikroskopik Sediment: Nadir bilirubin kristalleri ve tübüler epitel hücreleri."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme & Mikrobiyoloji / Karaciğer Ultrasonu",
                "keywords": ["ultrason", "usg", "karaciğer", "safra", "biyopsi"],
                "content": "Abdominal Ultrasonografi: Karaciğer parankiminde heterojen ekojenite artışı, safra kanallarında dilatasyon ve çamur birikimi. Karaciğer Biyopsisi: Periportal fibrozis, safra kanalı hiperplazisi ve hepatoselüler nekroz."
            }
        }
    },
    "Vaka H (Ateş)": {
        "kod": "VAKA_H",
        "tanim": "Akut Allerjik Ürtiker (Kurdeşen)",
        "sikayet": "Yetiştirici İfadesi: 'Hocam 510 kiloluk Ateş isimli tosunumuza yeni bir yem rasyonu verdik ve parazit iğnesi yaptık. Aradan iki saat geçmeden tosunun gövdesi, boynu ve omuzları patır patır yuvarlak kabarık plaklarla doldu! Göz kapakları şişti, huzursuzca kıvranıyor...'",
        "makroskopik_gorsel": {
            "fig": "Figure 1.5-1",
            "title": "Akut Ürtiker (Ödem Plakları)",
            "file": "gorseller/figure_1_5_1.jpg",
            "desc": "Gövde, boyun ve omuz derisinde aniden beliren dairesel ödemli kabarık ürtiker plakları (urtica/wheal)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "allerji", "protein", "enjeksiyon", "ilaç"],
                "content": "2 saat önce yeni bir protein konsantresi verilmiş ve parenteral enjeksiyon yapılmıştır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi / Sürü Öyküsü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sürü"],
                "content": "Besi ahırında barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "allerji"],
                "content": "Atopik/allerjik reaksiyon geçmişi bulunmaktadır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yeme", "geviş", "anoreksi"],
                "content": "Akut gelişen huzursuzluk nedeniyle yem yemeyi geçici olarak durdurmuştur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "deri", "ürtiker", "plak", "anjiyoödem"],
                "content": "Vücut Sıcaklığı: 38.8 °C (NORMAL) | Kalp Frekansı: 88 atım/dk | Solunum Frekansı: 32 nefes/dk | Mukozalar: Hiperemik | CRT: 1.6 saniye | Deri Muayenesi: Gövde, boyun ve omuzlarda parmakla basıldığında çukurlaşan (pitting edema), kabarık, dairesel ödem plakları (urtica/wheal) ve göz kapaklarında anjiyoödem."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp sesleri normal. Akciğerlerde hafif taşipneye bağlı veziküler sesler duyuluyor."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testleri NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "eozinofil", "eozinofili"],
                "content": "Eritrosit (RBC): 6.5 x10⁶/µL | Hemoglobin (Hb): 11.4 g/dL | Hematokrit (PCV): %34 | Lökosit (WBC): 11.8 x10³/µL | Nötrofil: %48 | Eozinofil: %16 (Şiddetli Akut Eozinofili - Akut Tip I Hipersensitivite) | Plazma Fibrinojeni: 380 mg/dL."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck"],
                "content": "AST: 62 U/L | GGT: 19 U/L | ALT: 22 U/L | ALP: 105 U/L | CK: 110 U/L."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["üre", "bun", "kreatinin", "glikoz", "bilirubin", "histamin"],
                "content": "BUN: 14 mg/dL | Kreatinin: 0.8 mg/dL | Glikoz: 72 mg/dL | Total Bilirubin: 0.4 mg/dL | Plazma Histamin ve IgE Düzeyi: AŞIRI YÜKSEK."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["albümin", "globülin", "total protein", "tp", "glutaraldehit"],
                "content": "Total Protein: 6.9 g/dL | Albümin: 3.3 g/dL | Globülin: 3.6 g/dL | Glutaraldehit Testi: NEGATİF."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "na", "k", "cl"],
                "content": "Sodyum (Na⁺): 139 mmol/L | Potasyum (K⁺): 4.2 mmol/L | Klor (Cl⁻): 100 mmol/L | Kalsiyum (Ca²⁺): 9.1 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be"],
                "content": "Kan pH: 7.39 | pO₂: 88 mmHg | pCO₂: 39 mmHg | HCO₃⁻: 24.0 mmol/L | Baz Açığı: 0.0 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "ph", "proteinüri", "glikozüri", "sediment"],
                "content": "İdrar Dansitesi: 1.020 | İdrar pH: 8.0 | Proteinüri: Negatif | Glikozüri: Negatif | Mikroskopik Sediment: Temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme & Mikrobiyoloji / Dermato-Histopatoloji",
                "keywords": ["ultrason", "usg", "biyopsi", "histopatoloji", "ödem"],
                "content": "Deri Biyopsisi / Histopatoloji: Dermiste belirgin mast hücresi degranülasyonu, eozinofilik infiltrasyon ve interstisyel ödem odajları."
            }
        }
    },
    "Vaka I (Fırtına)": {
        "kod": "VAKA_I",
        "tanim": "Akut Larenjit ve Larenks Ödemi / Nekrotik Larenjit",
        "sikayet": "Yetiştirici İfadesi: 'Hocam 180 kiloluk Fırtına isimli buzağımız dün geceden beri gırtlağından hırıl hırıl, düdük sesi gibi ses çıkararak nefes alıyor! Boynunu uzatmış hırlıyor. Boğazını tutunca acıyla peş peşe öksürüyor, ağzına yem alsa da yutamayıp yere düşürüyor...'",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "saman", "toz", "kaba yem"],
                "content": "Tozlu kaba yem ve saman balyaları tüketilmektedir. Larenks mukozasında mekanik irritasyon riski mevcuttur."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi / Sürü Öyküsü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sürü", "buzağı"],
                "content": "Büyütme padoğunda barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "öksürük"],
                "content": "1 hafta önce geçirilmiş hafif üst solunum yolu irritasyonu öyküsü vardır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yeme", "geviş", "yutma", "dysphagia", "ağrı"],
                "content": "Şiddetli yutma ağrısı (dysphagia) nedeniyle lokmaları yutamıyor, ağzından geri düşürüyor (Anoreksi)."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "stridor", "larenks", "ödem", "öksürük"],
                "content": "Vücut Sıcaklığı: 40.2 °C (Yüksek Febril Ateş) | Kalp Frekansı: 108 atım/dk | Solunum Frekansı: 48 nefes/dk (İnspiratorik Stridor / Islık Sesi) | Mukozalar: Hiperemik/Siyanotik | CRT: 2.5 saniye | Larenks Palpasyonu: Şiddetli ağrı yanıtı ve uyarılan paroksizmal öksürük krizi."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer", "stridor", "trakea"],
                "content": "Larenks/Trakea Oskültasyonu: Yüksek tonlu inspiratorik stridor (ıslık/düdük sesi). Akciğer Oskültasyonu: Veziküler solunum sesleri NORMALdir (Patoloji akciğer alveollerinde değil, üst solunum yolundadır!)."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "larenks", "trakea"],
                "content": "Retikulum ağrı testleri NEGATİF. Larenks ve trakea üst kısmına bastırıldığında şiddetli ağrı reaksiyonu (+)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv"],
                "content": "Eritrosit (RBC): 6.8 x10⁶/µL | Hemoglobin (Hb): 11.5 g/dL | Hematokrit (PCV): %35 | Lökosit (WBC): 22.4 x10³/µL (Şiddetli Lökositoz, Sola Kayma) | Nötrofil: %80 | Plazma Fibrinojeni: 850 mg/dL."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck"],
                "content": "AST: 68 U/L | GGT: 22 U/L | ALT: 24 U/L | ALP: 140 U/L | CK: 120 U/L."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["üre", "bun", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 18 mg/dL | Kreatinin: 0.9 mg/dL | Glikoz: 82 mg/dL | Total Bilirubin: 0.5 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["albümin", "globülin", "total protein", "tp", "glutaraldehit"],
                "content": "Total Protein: 7.4 g/dL | Albümin: 3.2 g/dL | Globülin: 4.2 g/dL | Glutaraldehit Testi: 2.5 dakikada POZİTİF."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "na", "k", "cl"],
                "content": "Sodyum (Na⁺): 138 mmol/L | Potasyum (K⁺): 4.0 mmol/L | Klor (Cl⁻): 98 mmol/L | Kalsiyum (Ca²⁺): 9.0 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be"],
                "content": "Kan pH: 7.39 | pO₂: 92 mmHg (NORMAL - Akciğer alveollerinde gaz alışverişi sağlamdır!) | pCO₂: 44 mmHg | HCO₃⁻: 24.5 mmol/L | Baz Açığı: +0.5 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "ph", "proteinüri", "glikozüri", "sediment"],
                "content": "İdrar Dansitesi: 1.024 | İdrar pH: 7.0 | Proteinüri: Negatif | Glikozüri: Negatif | Mikroskopik Sediment: Temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme & Mikrobiyoloji / Endoskopi",
                "keywords": ["ultrason", "usg", "endoskopi", "laringoskopi", "kültür", "fusobacterium"],
                "content": "Endoskopi / Laringoskopi: Larenks aditusunda ve arytenoid kıkırdaklarda şiddetli ödem, mukoza hiperemisi ve daralma. Kültür: Fusobacterium necrophorum ve Trueperella pyogenes izole edilmiştir."
            }
        }
    },
    "Vaka J (Şahin)": {
        "kod": "VAKA_J",
        "tanim": "Kronik Frontal Sinüzit / Boynuz Kesimi Sekeli",
        "sikayet": "Yetiştirici İfadesi: 'Hocam 560 kiloluk Şahin isimli tosunumuzun 1 ay önce boynuzunu kestirmiştik. Son 1 haftadır kesilen boynuzun olduğu taraftaki burun deliğinden çok pis kokulu, iltihaplı sarı akıntı geliyor. Başını sola doğru eğip duruyor, boynuz köküne dokununca bağırıyor...'",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "besi"],
                "content": "Besi rasyonu ile beslenmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi / Sürü Öyküsü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sürü"],
                "content": "Besi işletmesinde barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "boynuz", "dehorning", "kesim"],
                "content": "1 ay önce Hijyenik olmayan koşullarda açık yöntemle boynuz kesimi (dehorning) yapılmıştır. Sinüs boşluğu dış ortama açık kalmıştır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yeme", "geviş", "anoreksi"],
                "content": "Baş ağrısı ve ağrı nedeniyle hafif hiporeksi."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "sinüs", "burun akıntısı", "fetid", "iltihap"],
                "content": "Vücut Sıcaklığı: 39.3 °C | Kalp Frekansı: 84 atım/dk | Solunum Frekansı: 26 nefes/dk | Mukozalar: Pembe | CRT: 1.8 saniye | Muayene: Tek taraflı, son derece pis kokulu (fetid), pürülan burun akıntısı. Başın etkilenen tarafa doğru eğilmesi. Frontal sinüs kemiği üzerinde basınçlı palpasyonda şiddetli ağrı."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve akciğer oskültasyonu TAMAMEN NORMALdir."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum, Sinüs Perküsyonu & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "perküsyon", "sinüs", "matite"],
                "content": "Retikulum ağrı testleri NEGATİF. Frontal Sinüs Perküsyonu (Vuruk Muayenesi): Etkilenen sinüs bölgesinde belirgin MAT SES (Matite) ve şiddetli ağrı reaksiyonu (+)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv"],
                "content": "Eritrosit (RBC): 6.4 x10⁶/µL | Hemoglobin (Hb): 11.0 g/dL | Hematokrit (PCV): %33 | Lökosit (WBC): 16.2 x10³/µL (Lökositoz) | Plazma Fibrinojeni: 720 mg/dL."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck"],
                "content": "AST: 64 U/L | GGT: 20 U/L | ALT: 22 U/L | ALP: 110 U/L | CK: 105 U/L."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["üre", "bun", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 16 mg/dL | Kreatinin: 0.9 mg/dL | Glikoz: 74 mg/dL | Total Bilirubin: 0.4 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["albümin", "globülin", "total protein", "tp", "glutaraldehit"],
                "content": "Total Protein: 7.2 g/dL | Albümin: 3.1 g/dL | Globülin: 4.1 g/dL | Glutaraldehit Testi: 4 dakikada POZİTİF."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "na", "k", "cl"],
                "content": "Sodyum (Na⁺): 139 mmol/L | Potasyum (K⁺): 4.1 mmol/L | Klor (Cl⁻): 99 mmol/L | Kalsiyum (Ca²⁺): 9.1 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be"],
                "content": "Kan pH: 7.38 | pO₂: 88 mmHg | pCO₂: 41 mmHg | HCO₃⁻: 24.1 mmol/L | Baz Açığı: +0.1 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "ph", "proteinüri", "glikozüri", "sediment"],
                "content": "İdrar Dansitesi: 1.022 | İdrar pH: 8.0 | Proteinüri: Negatif | Glikozüri: Negatif | Mikroskopik Sediment: Temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme & Mikrobiyoloji / Röntgen & Kültür",
                "keywords": ["ultrason", "usg", "röntgen", "grafi", "sinüs", "kültür", "eksudat"],
                "content": "Kafa / Sinüs Radyografisi (Röntgen): Frontal sinüs lümeninde homojen radyoopak eksudat birikimi ve sıvı-hava seviyesi. Sinüs Ponksiyonu & Kültür: Trueperella pyogenes ve anaerob bakteri kolonizasyonu."
            }
        }
    },
    "Vaka K (Rüzgar)": {
        "kod": "VAKA_K",
        "tanim": "Hava Kesesi Mikozu / Guttural Pouch Mycosis (Aspergillus fumigatus)",
        "sikayet": "Yetiştirici İfadesi: 'Hocam 480 kiloluk İngiliz atımız Rüzgar durduğu yerde aniden burnundan foşur foşur taze kan akıtmaya başladı! Hiçbir darbe almadı. Ayrıca iki gündür samanı ağzına alıyor ama yutamıyor, içtiği su ve yem lokmaları burnundan geri çıkıyor...'",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "yulaf", "saman", "küf", "mantar"],
                "content": "At harasında yulaf ve kuru ot ile beslenmektedir. Kalitesiz/küflü ot balyası maruziyeti mümkündür."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi / Sürü Öyküsü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "at", "hara"],
                "content": "At harasında boks içerisinde barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "epistaksis", "kanama"],
                "content": "1 hafta önce hafif spontan burun kanaması (epistaksis) uyarısı görülüp kendiliğinden durmuştur."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yeme", "geviş", "yutma", "dysphagia", "rejitasyon", "burundan yem"],
                "content": "9, 10 ve 12. kafa çifti sinir felçlerine sekonder ŞİDDETLİ YUTMA GÜÇLÜĞÜ (Dysphagia). İçilen su ve lokmalar burundan geri geliyor (Regürjitasyon)."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "epistaksis", "kanama", "horner"],
                "content": "Vücut Sıcaklığı: 38.2 °C (At için Normal) | Kalp Frekansı: 68 atım/dk (Kan kaybına sekonder Taşikardi) | Solunum Frekansı: 22 nefes/dk | Mukozalar: Soluk pembe | CRT: 2.5 saniye | Muayene: Tek/Çift taraflı fışkırır tarzda taze arteriyel burun kanaması (Epistaksis), kulak düşüklüğü ve miyozis (Horner Sendromu belirtileri)."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp sesleri taşikardik. Akciğer oskültasyonunda reaspirasyon kanamasına bağlı alt alanlarda ılımlı raller."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "hava kesesi", "parotis"],
                "content": "Parotis ve hava kesesi bölgesi palpasyonunda hafif duyarlılık."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "anemi"],
                "content": "Eritrosit (RBC): 4.2 x10⁶/µL (Akut Kan Kaybı Anemisi) | Hemoglobin (Hb): 7.8 g/dL | Hematokrit (PCV): %24 | Lökosit (WBC): 12.8 x10³/µL | Plazma Fibrinojeni: 420 mg/dL."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck"],
                "content": "AST: 180 U/L | GGT: 24 U/L | ALT: 18 U/L | ALP: 190 U/L | CK: 220 U/L."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["üre", "bun", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 22 mg/dL | Kreatinin: 1.1 mg/dL | Glikoz: 92 mg/dL | Total Bilirubin: 1.0 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["albümin", "globülin", "total protein", "tp", "glutaraldehit", "saa"],
                "content": "Total Protein: 6.0 g/dL | Albümin: 2.8 g/dL | Globülin: 3.2 g/dL | SAA (Serum Amyloid A): 180 µg/mL (Yüksek)."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "na", "k", "cl"],
                "content": "Sodyum (Na⁺): 136 mmol/L | Potasyum (K⁺): 3.6 mmol/L | Klor (Cl⁻): 95 mmol/L | Kalsiyum (Ca²⁺): 11.2 mg/dL (At için normal)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be"],
                "content": "Kan pH: 7.38 | pO₂: 88 mmHg | pCO₂: 40 mmHg | HCO₃⁻: 23.5 mmol/L | Baz Açığı: -0.5 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "ph", "proteinüri", "glikozüri", "sediment"],
                "content": "İdrar Dansitesi: 1.030 | İdrar pH: 7.5 | Proteinüri: Negatif | Mikrohematüri: Negatif (Kan üriner sistemden gelmemektedir)."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme & Mikrobiyoloji / Endoskopi",
                "keywords": ["ultrason", "usg", "endoskopi", "hava kesesi", "aspergillus", "carotis", "arter"],
                "content": "Guttural Pouch Endoskopisi: Hava kesesi dorsomedial bölmesinde Arteria carotis interna üzerinde siyah/yeşilimsi Aspergillus fumigatus fungal plağı (mantar plağı) ve eroze olmuş damar üzerinde taze pıhtı teşhisi."
            }
        }
    },
    "Vaka L (Poyraz)": {
        "kod": "VAKA_L",
        "tanim": "Hava Kesesi Empiyemi / Guttural Pouch Empyema & Kondroitler (Gurm Sekeli)",
        "sikayet": "Yetiştirici İfadesi: 'Hocam 520 kiloluk Poyraz isimli atımız 1 ay önce ağır bir boğaz iltihabı (gurm) geçirdi. Hastalık geçti derken şimdi boğazının altı, kulak arkası davul gibi şişti! Başını öne uzatıyor, eğemiyor. Burun deliklerinden katı koyu iltihap geliyor...'",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "saman", "yulaf"],
                "content": "Standart hara rasyonu verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi / Sürü Öyküsü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "at", "hara"],
                "content": "At harasında barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık & Sağlık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü", "gurm", "streptococcus", "boğaz"],
                "content": "1 ay önce geçirilmiş Streptococcus equi subsp. equi enfeksiyonu (Gurm hastalığı) öyküsü vardır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yutma / Çiğneme Durumu",
                "keywords": ["iştah", "yem yeme", "geviş", "yutma", "dysphagia"],
                "content": "Boğaz ve parotis bölgesindeki ağrılı mekanik baskı nedeniyle yutma güçlüğü ve yem yemede isteksizlik."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "şişlik", "parotis", "pürülan", "akıntı"],
                "content": "Vücut Sıcaklığı: 39.5 °C (Ateşli) | Kalp Frekansı: 72 atım/dk | Solunum Frekansı: 26 nefes/dk | Mukozalar: Hiperemik | CRT: 2.0 saniye | Muayene: Başın kafa kaidesinden öne doğru uzatılması. Parotis ve retrofaringeal bölgede bilateral sıcak, ağrılı ve fluktuan şişlik. Burun deliklerinden çift taraflı koyu pürülan akıntı."
            },
            "OSKULTASYON": {
                "name": "Kalp, Akciğer & Göğüs Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp sesleri normal. Akciğerlerde hafif sertleşmiş veziküler sesler."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum & Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum", "parotis", "boğaz"],
                "content": "Parotis ve hava kesesi bölgesine bastırıldığında şiddetli ağrı reaksiyonu (+)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv"],
                "content": "Eritrosit (RBC): 6.8 x10⁶/µL | Hemoglobin (Hb): 11.8 g/dL | Hematokrit (PCV): %36 | Lökosit (WBC): 22.4 x10³/µL (Şiddetli Lökositoz, Nötrofili) | Plazma Fibrinojeni: 920 mg/dL."
            },
            "BIYOKIMYA_ENZIMLER": {
                "name": "Serum Biyokimyası & Organ Enzim Paneli",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck"],
                "content": "AST: 78 U/L | GGT: 22 U/L | ALT: 20 U/L | ALP: 130 U/L | CK: 140 U/L."
            },
            "BIYOKIMYA_RENAL_METABOLIK": {
                "name": "Renal Fonksiyon & Metabolit Paneli",
                "keywords": ["üre", "bun", "kreatinin", "glikoz", "bilirubin"],
                "content": "BUN: 18 mg/dL | Kreatinin: 1.0 mg/dL | Glikoz: 85 mg/dL | Total Bilirubin: 0.6 mg/dL."
            },
            "BIYOKIMYA_PROTEIN_YANGI": {
                "name": "Serum Proteinleri & Akut Faz Yangı Paneli",
                "keywords": ["albümin", "globülin", "total protein", "tp", "glutaraldehit", "saa"],
                "content": "Total Protein: 8.4 g/dL | Albümin: 2.9 g/dL | Globülin: 5.5 g/dL (Hipergamaglobulinemi) | SAA (Serum Amyloid A): 450 µg/mL (Aşırı Yüksek Akut Faz Yanıtı)."
            },
            "ELEKTROLIT_MINERAL": {
                "name": "Serum Elektrolit & Mineral Paneli",
                "keywords": ["sodyum", "potasyum", "klor", "kalsiyum", "fosfor", "na", "k", "cl"],
                "content": "Sodyum (Na⁺): 137 mmol/L | Potasyum (K⁺): 3.9 mmol/L | Klor (Cl⁻): 97 mmol/L | Kalsiyum (Ca²⁺): 10.8 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı & Asit-Baz Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be"],
                "content": "Kan pH: 7.36 | pO₂: 86 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 22.8 mmol/L | Baz Açığı: -1.5 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "Tam İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "ph", "proteinüri", "glikozüri", "sediment"],
                "content": "İdrar Dansitesi: 1.026 | İdrar pH: 7.5 | Proteinüri: +1 | Glikozüri: Negatif | Mikroskopik Sediment: Temiz."
            },
            "GORUNTULEME_MIKROBIYOLOJI": {
                "name": "Görüntüleme & Mikrobiyoloji / Röntgen & Endoskopi",
                "keywords": ["ultrason", "usg", "röntgen", "endoskopi", "kondroit", "hava kesesi", "streptococcus"],
                "content": "Guttural Pouch Endoskopisi & Radyografi: Hava kesesi lümeninde birikmiş koyu pürülan eksudat ve taşlaşmış oval irin topçukları (Kondroit / Chondroid kitleleri). Kültür: Streptococcus equi subsp. equi üretilmiştir."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnez & Kapsamlı Klinik Bulgu Sorgu Konsolu</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde hazır şıklar veya butonlar <u>yoktur</u>. 
        Kafanızdaki klinik şüpheye ve hekimlik sorgulamanıza göre merak ettiğiniz parametreleri kutucuğa <b>kendi cümlelerinizle</b> yazınız 
        (Örn: <i>"Rasyon bilgisi nedir?"</i>, <i>"Ateşi kaç derece?"</i>, <i>"Kalp ve akciğer sesleri nasıl?"</i>, <i>"Hemogram ve fibrinojen kaç?"</i>, <i>"Serum AST, GGT, BUN tahlili istiyorum"</i>, <i>"Kan gazı pO2 ve laktat sonucu nedir?"</i>, <i>"İdrar tahlilinde bilirubin ve protein var mı?"</i>, <i>"Ultrason/Röntgen çekelim"</i>).
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
    img_path = find_gorsel_path(mg["file"])
    
    if img_path and os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        uploaded_img = st.file_uploader(
            f"📷 Klinik Görsel Yükleyiniz (.jpg / .png):",
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
            if re.search(r'\\b' + re.escape(kw_clean), text_clean) or kw_clean in text_clean:
                matched_cats.append(cat_key)
                break
    return matched_cats

col_input, col_button = st.columns([4, 1])

with col_input:
    user_query = st.text_input(
        "Sorunuzu Buraya Yazınız:",
        key="query_input",
        placeholder="Örn: İştah durumu nasıl?, AST/GGT kaç?, İdrar tahlili sonucu nedir?, Deri kazıntısı yapalım..."
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
            st.success(f"🎉 {new_disc} yeni klinik bulgu / detaylı tahlil bilgisi açığa çıkarıldı!")
    else:
        st.warning("⚠️ Eşleşen bilgi bulunamadı. Lütfen sorunuzu farklı tahlil/muayene kelimeleriyle yazınız (Örn: 'rasyon', 'ateş', 'hemogram', 'ast', 'biyokimya', 'idrar', 'kan gazı', 'ultrason').")

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
                <div class='card-content'><b>🩺 Bulgu / Tahlil Sonucu:</b> {item['content']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # MICROSCOPIC IMAGES DISPLAYED ONLY AFTER BEING QUERY-TRIGGERED
        if "gorsel" in item:
            g = item["gorsel"]
            micro_path = find_gorsel_path(g["file"])
            if micro_path and os.path.exists(micro_path):
                st.image(micro_path, use_container_width=True)
            else:
                up_micro = st.file_uploader(
                    f"📷 Mikroskopik Görsel Yükleyiniz (.jpg / .png):",
                    type=["jpg", "jpeg", "png"],
                    key=f"up_micro_{item['cat_key']}"
                )
                if up_micro is not None:
                    st.image(up_micro, use_container_width=True)

# Clear Button
if st.session_state.history:
    if st.button("🗑️ Bu Vakanın Sorgu Geçmişini Temizle"):
        st.session_state.history = []
        st.rerun()

# Teacher Portal (Hoca Paneli) in Sidebar
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
            st.markdown(f"#### 🔑 **{selected_case_name}** Cevap Anahtarı:")
            st.markdown(f"**• Tescilli Kesin Tanı:** `{active_case.get('tanim', 'Bilinmiyor')}`")
            st.markdown("---")
            if st.button("🔓 Tüm İpuçlarını ve Tahlilleri Sınıf İçin Ekranda Aç"):
                st.session_state.history = []
                for ck, cv in active_case["categories"].items():
                    item_dict = {
                        "cat_key": ck,
                        "query": "Eğitmen Tarafından Tüm İpuçları Açıldı",
                        "title": cv["name"],
                        "content": cv["content"]
                    }
                    if "gorsel" in cv:
                        item_dict["gorsel"] = cv["gorsel"]
                    st.session_state.history.append(item_dict)
                st.rerun()
            
            st.markdown("#### 📑 Gizli Tüm Kategori İçerikleri:")
            for ck, cv in active_case["categories"].items():
                with st.expander(f"📌 {cv['name']}"):
                    st.write(cv["content"])
        elif pass_code:
            st.error("Hatalı Şifre!")
'''

with open('/workspace/scratch/build_master_12_cases_comprehensive.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("Master script generator written successfully.")
