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

# Helper function to locate image files flexibly
def find_gorsel_path(rel_path):
    if not rel_path:
        return None
    if os.path.exists(rel_path):
        return rel_path
    
    filename = os.path.basename(rel_path)
    base_no_ext, _ = os.path.splitext(filename)
    
    search_dirs = [
        ".", 
        "gorseller", 
        "/mount/src/vet401-anamnez/gorseller", 
        "/mount/src/vet401-anamnez",
        os.path.join(os.path.dirname(__file__), "gorseller") if '__file__' in globals() else "gorseller"
    ]
    for s_dir in search_dirs:
        if os.path.exists(s_dir):
            try:
                for f in os.listdir(s_dir):
                    f_no_ext, _ = os.path.splitext(f)
                    if f_no_ext.lower() == base_no_ext.lower():
                        full_p = os.path.join(s_dir, f)
                        if os.path.isfile(full_p):
                            return full_p
            except Exception:
                pass
    return None

# Cases Knowledge Base
CASES = {
    "Vaka A (Papatya)": {
        "kod": "VAKA_A",
        "sikayet": "Çene altında ve gerdanda soğuk, hamur kıvamında ödem şişliği, iştahın tamamen kesilmesi, süt veriminin bıçak gibi düşmesi ve belirgin durgunluk.",
        "categories": {
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem", "yiyor", "su", "içiyor", "iştahsız", "yememe", "samana", "yemlik"],
                "content": "Anoreksi mevcut. Hayvan önündeki samana ve yoğun yeme hiç dokunmamaktadır. Su içimi de oldukça azalmıştır."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis) Sonucu",
                "keywords": ["idrar", "tahlil", "dansite", "ph", "protein", "glikoz", "keton", "sediment", "hematüri"],
                "content": "Dansite: 1.025 | pH: 7.8 | Proteinüri: +1 | Glikozüri: Negatif | Ketonüri: Eser | Sediment: Nadir epitel hücresi, eritrosit veya lökosit yok."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yemleme", "besle", "mısır", "arpa", "silaj", "balya", "saman", "tel", "çivi", "inşaat"],
                "content": "İşletmede kaba/yoğun yem karma rasyonu uygulanmaktadır. Balya parçalama esnasında inşaat teli veya çivi karışmış olabileceği belirtilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "coğrafya", "yer", "nakil", "sevk", "ovada", "dağ"],
                "content": "Ceyhan ovasındaki (rakım ~50 m) tesiste doğup büyümüştür. Yayla veya yüksek rakım öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "doğum", "mastitis", "metritis"],
                "content": "Kronik bir hastalık öyküsü yoktur. 2 ay önce sorunsuz doğum yapmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "derece", "sıcaklık", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "ödem", "jugular"],
                "content": "Ateş: 39.8 °C | Kalp Frekansı: 102 atım/dk | Solunum: 42 nefes/dk | Mukoza: Soluk pembe | CRT: 2.5 sn | Gerdan ve çene altında soğuk hamur ödemi, Vena jugularis stazı ve yalancı nabız +."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "çalkantı", "şılpırtı", "splashing", "boğuk", "rall"],
                "content": "Kalp Oskültasyonu: Gaz ve sıvının çalkalanmasına bağlı çamaşır makinesi / su şılpırtısı (splashing) ve boğuk kalp sesleri. Akciğer: Ventral alanlarda solunum sesleri hafif azalmış."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Withers (cidago) çimdikleme testinde inleme ve kaçınma +, Sopa muayenesinde retikulum bölgesinde belirgin ağrı reaksiyonu +."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "pp/f", "lökositoz"],
                "content": "Lökosit (WBC): 22.4 x10³/µL (Rejeneratif sola kayma) | Plazma Fibrinojeni: 1250 mg/dL (Aşırı yüksek) | PP/F Oranı: 6.3 (<10, Şiddetli aktif Fibrinöz Yangı)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "üre", "kreatinin", "troponin", "albümin", "globülin"],
                "content": "Albümin: 2.1 g/dL (Hipoalbüminemi) | Globülin: 5.8 g/dL (Hipergamaglobülinemi) | Kardiyak Troponin I: 2.8 ng/mL (Yüksek, miyokard Hasarı)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "laktat"],
                "content": "pH: 7.32 | pO₂: 38 mmHg (Doku hipoksisi) | pCO₂: 48 mmHg | HCO₃⁻: 20.2 mmol/L | Laktat: 3.8 mmol/L."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Perikardiyosentez",
                "keywords": ["ultrason", "usg", "perikardiyosentez", "delme", "sıvı", "kültür", "bakteri"],
                "content": "Torakal USG: Perikardiyal kesede genişleme, yoğun fibrin bantları ve anaerobik gaz kabarcıkları. Perikardiyosentez: Kötü kokulu pürülan-fibrinöz sıvı, lökosit infiltre."
            }
        }
    },
    "Vaka B (Yonca)": {
        "kod": "VAKA_B",
        "sikayet": "Sürekli tekrarlayan düzensiz yüksek ateş nöbetleri, zayıflama, çabuk yorulma ve solunum güçlüğü.",
        "categories": {
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem", "yiyor", "su", "içiyor", "iştahsız", "yememe", "durgun"],
                "content": "Hiporeksi (iştahsızlık). Ateşi yükseldiği nöbet dönemlerinde yemliği tamamen bırakmakta, ateş düştüğünde az miktarda kaba yem tüketmektedir."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis) Sonucu",
                "keywords": ["idrar", "tahlil", "dansite", "ph", "protein", "glikoz", "keton", "sediment", "hematüri"],
                "content": "Dansite: 1.022 | pH: 7.5 | Proteinüri: +2 (Aşırı yüksek, immün kompleks glomerülonefrit) | Sediment: Mikrohematüri (+1 eritrosit), granüler silindirler izlendi."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yemleme", "besle", "mısır", "arpa", "silaj"],
                "content": "Standart meraya dayalı ve akşamları kaba/yoğun yem takviyeli rasyon."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "coğrafya", "yer", "nakil"],
                "content": "Ova işletmesinde barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "mastitis", "rahim", "ayak", "tırnak", "apse"],
                "content": "Yaklaşık 1.5 ay önce tedavi edilmiş ağır pürülan kronik metritis ve kronik tırnak apsesi öyküsü mevcuttur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "derece", "sıcaklık", "nabız", "kalp frekans", "solunum", "mukoza", "crt"],
                "content": "Ateş: 40.5 °C (Ateş nöbeti esnasında) | Kalp Frekansı: 110 atım/dk | Solunum: 48 nefes/dk | Mukoza: İkterik ve soluk | Ekstremitelerde venöz dolgunluk."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "diastolik", "sistolik", "akciğer"],
                "content": "Kalp Oskültasyonu: Sol situsta 4.-5. kaburga arasında belirgin holosistolik ve diastolik yumuşak üfürüm (Murmur). Kalp sesleri kuvvetli fakat ritimsiz."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testlerinin tamamı NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "anemi"],
                "content": "Lökosit: 28.5 x10³/µL (Şiddetli lökositoz) | Fibrinojen: 980 mg/dL | RBC: 4.2 x10⁶/µL (Kronik hastalık anemisi)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "üre", "kreatinin", "troponin", "bilirubin"],
                "content": "Total Bilirubin: 2.4 mg/dL | AST: 140 U/L | Kardiyak Troponin I: 1.9 ng/mL | BUN: 34 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat"],
                "content": "pH: 7.38 | pO₂: 42 mmHg | pCO₂: 44 mmHg | HCO₃⁻: 22.0 mmol/L."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Bakteriyoloji",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "kapak", "vejetasyon"],
                "content": "Ekokardiyografi: Aort ve mitral kapakçıklar üzerinde karnabahar görünümünde vejetatif trombotik kitleler (Vegetative Endocarditis). Kan Kültürü: Trueperella pyogenes veya Streptococcus spp. üremesi +."
            }
        }
    },
    "Vaka C (Zümrüt)": {
        "kod": "VAKA_C",
        "sikayet": "Yayladan ovaya nakil sonrası gerdanda soğuk hamur ödem, aşırı solunum güçlüğü ve morarmış (siyanotik) mukozalar.",
        "categories": {
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem", "yiyor", "su", "içiyor", "iştahsız", "durgun"],
                "content": "Ağır dispneye bağlı iştahsızlık. Yem ve su tüketimi neredeyse durmuştur."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis) Sonucu",
                "keywords": ["idrar", "tahlil", "dansite", "ph", "protein", "glikoz", "keton", "sediment"],
                "content": "Dansite: 1.030 | pH: 7.2 | Proteinüri: Eser | Glikozüri: Negatif | Sediment: Normal."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yemleme", "besle", "mısır", "arpa", "ot", "yayla"],
                "content": "Mera ve mera dönüşü kaba yem rasyonu."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "coğrafya", "yer", "nakil", "sevk", "yükseklik", "dağ"],
                "content": "Pozantı Yaylasında (rakım ~2100 metre) 4 ay kaldıktan sonra aniden Ceyhan Ovasına nakledilmiştir (High Altitude Disease / Brisket Disease)."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık"],
                "content": "Öncül bir sistemik hastalık öyküsü yoktur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "derece", "sıcaklık", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "ödem", "siyanoz"],
                "content": "Ateş: 38.6 °C (Normal) | Kalp Frekansı: 96 atım/dk | Solunum: 46 nefes/dk | Mukoza: Siyanotik (Koyu mor/mavi) | Gerdanda yaygın soğuk hamur ödemi."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "akciğer"],
                "content": "Kalp Oskültasyonu: Hiperdinamik güçlü sağ ventrikül sesleri. Üfürüm veya su çalkantı sesi YOKTUR. Akciğer: Veziküler sesler hafif azalmış."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testleri NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "rbc", "pcv", "polisitemi"],
                "content": "RBC: 10.8 x10⁶/µL (Sekonder Polisitemi) | PCV: %54 (Aşırı yüksek) | Lökosit: 7.2 x10³/µL (Normal) | Fibrinojen: 320 mg/dL (Normal)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "üre", "kreatinin", "troponin"],
                "content": "AST: 68 U/L | GGT: 18 U/L | Kardiyak Troponin I: 0.12 ng/mL (Normal)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hipoksi"],
                "content": "pH: 7.36 | pO₂: 48 mmHg (Ağır kronik doku hipoksisi) | pCO₂: 42 mmHg | HCO₃⁻: 23.5 mmol/L."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Mikrobiyoloji",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "ventrikül", "pulmoner"],
                "content": "Ekokardiyografi: Sağ ventrikül serbest duvar kalınlığında artış (Sağ Ventrikül Hipertrofisi) ve pulmoner arter genişlemesi. Kültür: Bakteri üremesi yoktur (Steril)."
            }
        }
    },
    "Vaka D (Yiğit)": {
        "kod": "VAKA_D",
        "sikayet": "Ağız ve burundan fışkırır tarzda taze parlak kırmızı kan gelmesi (hemoptizi) ve katran gibi siyah dışkı yapma (melena).",
        "categories": {
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem", "yiyor", "su", "içiyor", "iştahsız", "durgun"],
                "content": "Anoreksi. Kan kaybına ve şoka bağlı olarak hayvan tamamen halsizdir ve yem yemeyi kesmiştir."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis) Sonucu",
                "keywords": ["idrar", "tahlil", "dansite", "ph", "protein", "glikoz", "keton", "sediment"],
                "content": "Dansite: 1.028 | pH: 6.8 (Hafif asidik) | Proteinüri: Eser | Sediment: Şok tablosuna bağlı seyrek hyalin silindirler."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yemleme", "besle", "mısır", "arpa", "besi", "nişasta"],
                "content": "18 aylık besi danasıdır. Mısır ve arpa ağırlıklı, kaba yemi yetersiz yüksek nişastalı besi rasyonu verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "coğrafya", "yer"],
                "content": "Besi padoğunda barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "asidoz", "rumenitis", "şişkinlik"],
                "content": "Tekrarlayan akut/subakut rumen asidozu (yem çarpması) öyküsü vardır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "derece", "sıcaklık", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "hemoptizi", "melena"],
                "content": "Ateş: 39.2 °C | Kalp Frekansı: 118 atım/dk | Solunum: 52 nefes/dk | Ağız/Burun: Köpüklü taze parlak kırmızı kan fışkırması (Hemoptizi) | Mukozalar: Bembeyaz | CRT: 4.0 sn | Dışkı: Siyah katran kıvamında (Melena)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Taşikardik, zayıf düştü sesleri. Akciğer: Bilateral yaygın kaba raller ve hışırtı sesleri."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testleri NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "anemi", "pcv"],
                "content": "RBC: 2.1 x10⁶/µL | PCV: %12 (Kritik Kan Kaybı Anemisi!) | Lökosit: 21.5 x10³/µL | Fibrinojen: 1050 mg/dL."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "üre", "kreatinin", "bilirubin"],
                "content": "AST: 210 U/L (Karaciğer hasarı) | GGT: 68 U/L | BUN: 42 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "laktat"],
                "content": "pH: 7.24 | pO₂: 52 mmHg | pCO₂: 50 mmHg | HCO₃⁻: 18.5 mmol/L | Laktat: 4.2 mmol/L."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Ultrasonografi",
                "keywords": ["ultrason", "usg", "karaciğer", "apse", "vena cava", "trombüs", "arter"],
                "content": "Abdominal USG: Karaciğerde 6 cm çapında apse odağı (Hepatic Abscess), Vena Cava Caudalis lümeninde tıkayıcı trombüs ekojenitesi (VCCT Sendromu). Torakal USG: Pulmoner arter çevresinde anevrizma ve hematom."
            }
        }
    },
    "Vaka E (Kudret)": {
        "kod": "VAKA_E",
        "sikayet": "Baş, göz çevresi ve boyun bölgesinde kaşıntısız dairesel döküntüler, kılların dökülmesi ve gri-beyaz kireçimsi kabuklanma.",
        "makroskopik_gorsel": {
            "fig": "Figure 1.2-1",
            "title": "Klinik Mantar Lezyonu (Baş ve Göz Çevresi)",
            "file": "gorseller/figure_1_2_1.jpg",
            "desc": "Göz çevresi ve yüzde dairesel, grimsi-beyaz kireç benzeri kabarık kabuklanma ve alopezi (tüy kaybı)."
        },
        "categories": {
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem", "yiyor", "su", "içiyor", "iştahsız"],
                "content": "İştah ve su içimi tamamen normaldir. Genel durumu iyidir."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis) Sonucu",
                "keywords": ["idrar", "tahlil", "dansite", "ph", "protein"],
                "content": "Dansite: 1.026 | pH: 7.8 | Protein/Glikoz: Negatif | Sediment: Tamamen normal."
            },
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yemleme", "besle", "rutubet", "ağıl", "karanlık"],
                "content": "Kapalı, nemli ve yetersiz havalandırmalı padokta yoğun dana büyütme yemi ve kuru ot ile beslenmektedir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "derece", "sıcaklık", "nabız", "solunum", "mukoza", "deri", "döküntü", "kabuk"],
                "content": "Ateş: 38.8 °C (Normal) | Kalp: 76 atım/dk | Solunum: 24 nefes/dk | Baş, göz çevresi ve boyunda dairesel, gri-kireçimsi kabuklu alopezi alanları. Kaşıntı YOKTUR."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen"],
                "content": "Lökosit: 8.2 x10³/µL (Normal) | Fibrinojen: 350 mg/dL (Normal) | Hemogram parametreleri fizyolojik sınırlardadır."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "Deri Kazıntısı & Mikroskopik Mantar Teşhisi",
                "keywords": ["mikroskop", "kazıntı", "deri kazıntısı", "koh", "mantar", "artrospor", "lam"],
                "gorsel": {
                    "fig": "Figure 1.2-11",
                    "title": "Mikroskopik Mantar Sporu (%10 KOH Hazırlığı)",
                    "file": "gorseller/figure_1_2_11.jpg",
                    "desc": "%10 KOH ile muamele edilmiş deri kazıntısında kıl şaftını saran küresel Trichophyton verrucosum ektotriks artrospor dizilimi (40x)."
                },
                "content": "%10 KOH ile hazırlanan yüzeysel deri ve kıl kazıntısında Trichophyton verrucosum ektotriks artrospor zincirleri belirgin olarak izlenmiştir."
            }
        }
    },
    "Vaka F (Nazar)": {
        "kod": "VAKA_F",
        "sikayet": "Şiddetli kaşıntı, huzursuzluk, derinin fil derisi gibi kalınlaşması (likenifikasyon) ve kıvrımlaşarak dökülmesi.",
        "makroskopik_gorsel": {
            "fig": "Figure 1.3-13 & 1.3-15",
            "title": "Klinik Uyuz Lezyonu (Deride Kalınlaşma ve Likenifikasyon)",
            "file": "gorseller/figure_1_3_13.jpg",
            "desc": "Kulak kepçesi, boyun ve sırtta derinin fil derisi gibi kalınlaşması (likenifikasyon), kaşıntı eksforyasyonları ve kepekli döküntü."
        },
        "categories": {
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem", "yiyor", "su", "içiyor", "iştahsız", "kaşıntı"],
                "content": "Sürekli kaşınmaktan ve duvarlara sürtünmekten yem yemeye fırsat bulamamaktadır. İştah orta derecede azalmıştır."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis) Sonucu",
                "keywords": ["idrar", "tahlil", "dansite", "ph", "protein"],
                "content": "Dansite: 1.024 | pH: 7.6 | Protein/Glikoz: Negatif | Sediment: Tamamen normal."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "derece", "sıcaklık", "nabız", "solunum", "deri", "kaşıntı", "likenifikasyon", "uyuz"],
                "content": "Ateş: 39.1 °C | Kalp: 88 atım/dk | Solunum: 30 nefes/dk | Kulak kepçesi, boyun, sırt ve omuzlarda deride fil derisi görünümünde kalınlaşma, kıvrımlaşma ve kanamalı kaşıntı izleri."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "eozinofil", "parazit"],
                "content": "Lökosit: 14.2 x10³/µL | Eozinofil: %14 (Belirgin Eozinofili - Paraziter/Alerjik reaksiyon) | PCV: %34."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "Derin Deri Kazıntısı & Akar Mikroskopisi",
                "keywords": ["mikroskop", "kazıntı", "deri kazıntısı", "akar", "uyuz", "mineral yağ", "sarcoptes"],
                "gorsel": {
                    "fig": "Figure 1.3-18",
                    "title": "Mikroskopik Sarcoptes Scabiei Akari",
                    "file": "gorseller/figure_1_3_18.jpg",
                    "desc": "Derin deri kazıntısında mineral yağ altında tespit edilen canlı ergin Sarcoptes scabiei akarı (10x-40x)."
                },
                "content": "Kapiller kanama görülünceye kadar alınan derin deri kazıntısında canlı Sarcoptes scabiei ergin akarları ve oval yumurtaları tespit edilmiştir."
            }
        }
    },
    "Vaka G (Çiçek)": {
        "kod": "VAKA_G",
        "sikayet": "Güneşe çıktıktan sonra sadece vücudun beyaz (pigmentsiz) deri bölgelerinde kızarıklık, hamur ödemi ve derinin tabaka halinde soyulması.",
        "makroskopik_gorsel": {
            "fig": "Figure 1.7-35",
            "title": "Hepatojen Fotosensitizasyon (Pigmentsiz Deri Nekrozu)",
            "file": "gorseller/figure_1_7_35.jpg",
            "desc": "Yalnızca beyaz (pigmentsiz) deri alanlarında soyulma, hamur ödemi ve nekroz; siyah pigmentli derinin tamamen sağlam kalması."
        },
        "categories": {
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem", "yiyor", "su", "içiyor", "iştahsız"],
                "content": "Ağrı ve huzursuzluğa bağlı hiporeksi. Gölgelik alana kaçmakta, yem yemeyi reddetmektedir."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis) Sonucu",
                "keywords": ["idrar", "tahlil", "dansite", "ph", "bilirubin", "ürobilinojen", "sarılık"],
                "content": "Dansite: 1.028 | pH: 7.4 | Bilirubinüri: +2 (Koyu çay rengi idrar) | Ürobilinojen: Artmış."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "derece", "sıcaklık", "nabız", "solunum", "deri", "beyaz", "güneş", "fotosensitizasyon", "ikter"],
                "content": "Ateş: 39.5 °C | Kalp: 92 atım/dk | Solunum: 36 nefes/dk | Mukozalar belirgin sarı (İkterik). Yalnızca beyaz post alanlarında sert ödem, nekroz ve deri soyulması. Siyah alanlar TAMAMEN NORMAL."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Karaciğer Enzimleri",
                "keywords": ["biyokimya", "ast", "ggt", "bilirubin", "filloeritrin", "karaciğer"],
                "content": "GGT: 180 U/L (Aşırı yüksek, kolestaz) | AST: 290 U/L | Total Bilirubin: 3.8 mg/dL | İndirekt Bilirubin: 2.1 mg/dL | Kanda Filloeritrin akümülasyonu +."
            }
        }
    },
    "Vaka H (Ateş)": {
        "kod": "VAKA_H",
        "sikayet": "Mera dönüşü vücutta aniden beliren dairesel ödemli kabarık plaklar (ürtiker), huzursuzluk ve hafif solunum hızlanması.",
        "makroskopik_gorsel": {
            "fig": "Figure 1.5-1",
            "title": "Akut Ürtiker (Ödem Plakları)",
            "file": "gorseller/figure_1_5_1.jpg",
            "desc": "Gövde ve boyun derisinde aniden beliren dairesel ödemli kabarık ürtiker plakları (urtica)."
        },
        "categories": {
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem", "yiyor", "su", "içiyor", "iştahsız"],
                "content": "Aniden gelişen alerjik reaksiyon nedeniyle huzursuzdur, yeme ilgisizdir."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis) Sonucu",
                "keywords": ["idrar", "tahlil", "dansite", "ph"],
                "content": "Dansite: 1.022 | pH: 7.8 | Tüm parametreler fizyolojik sınırlardadır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "derece", "sıcaklık", "nabız", "solunum", "ürtiker", "plak", "ödem", "alerji"],
                "content": "Ateş: 38.9 °C | Kalp: 84 atım/dk | Solunum: 32 nefes/dk | Boyun, omuz ve böğür bölgesinde basmakla çukurlaşan, aniden çıkmış ödemli dairesel plaklar (Urtica)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "eozinofil"],
                "content": "Lökosit: 11.2 x10³/µL | Eozinofil: %10 (Alerjik yanıt) | Fibrinojen: 300 mg/dL."
            }
        }
    },
    "Vaka I (Fırtına)": {
        "kod": "VAKA_I",
        "sikayet": "Gırtlağından ıslık/düdük sesi gibi (stridor) nefes alma, boynunu uzatma, gırtlağa dokununca öksürük ve yutma güçlüğü.",
        "categories": {
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem", "yiyor", "su", "içiyor", "yutma", "disfaji"],
                "content": "Yutma ağrısı (Disfaji) nedeniyle samanı ağzına alsa da yutamayıp düşürmektedir. Su içerken zorlanmaktadır."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis) Sonucu",
                "keywords": ["idrar", "tahlil", "dansite", "ph"],
                "content": "Dansite: 1.025 | pH: 7.6 | Tüm idrar tahlil parametreleri normaldir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "derece", "sıcaklık", "nabız", "solunum", "stridor", "gırtlak", "larenks", "öksürük"],
                "content": "Ateş: 40.1 °C | Kalp: 98 atım/dk | Solunum: 44 nefes/dk (İnspiratorik Dispne) | Gırtlak bölgesinde palpasyonda aşırı sıcaklık, ödem ve şiddetli ağrılı öksürük refleksi."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer", "stridor"],
                "content": "Kalp sesleri ritmik ve normal. Akciğer Oskültasyonu: Veziküler solunum sesleri tamamen SAĞLAMDIR. Üst solunum yolunda larengeal daralma gürültüsü duyulmaktadır."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2"],
                "content": "pH: 7.39 | pO₂: 92 mmHg (Akciğer alveol gaz değişimi tamamen SAĞLAMDIR) | pCO₂: 44 mmHg."
            }
        }
    },
    "Vaka J (Şahin)": {
        "kod": "VAKA_J",
        "sikayet": "Boynuz kesimi sonrası tek taraflı pis kokulu mukopürülan burun akıntısı, başı yana eğme ve sinüs üzerinde ağrı.",
        "categories": {
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem", "yiyor", "su", "içiyor", "baş ağrısı"],
                "content": "Ağrı nedeniyle iştah %50 azalmıştır."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis) Sonucu",
                "keywords": ["idrar", "tahlil", "dansite", "ph"],
                "content": "Dansite: 1.024 | pH: 7.8 | Normal."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "derece", "sıcaklık", "nabız", "solunum", "sinüs", "perküsyon", "matite", "burun akıntısı"],
                "content": "Ateş: 39.4 °C | Kalp: 82 atım/dk | Solunum: 28 nefes/dk | Sol burun deliğinden pis kokulu pürülan akıntı. Sol frontal sinüs perküsyonunda MATİTE (tok ses) ve ağrı."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Sinüs Grafisi & Trepanasyon",
                "keywords": ["rontgen", "grafi", "sinüs", "trepanasyon", "irin"],
                "content": "Röntgen: Sol frontal sinüs lümeninde sıvı-hava seviyesi ve radyoopak irin birikimi. Trepanasyonda kokuşmuş irin boşalmıştır."
            }
        }
    },
    "Vaka K (Rüzgar)": {
        "kod": "VAKA_K",
        "sikayet": "Atın burnundan durduğu yerde aniden başlayan bol miktarda parlak taze kırmızı kan gelmesi (epistaksis) ve yutma güçlüğü.",
        "categories": {
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem", "yiyor", "su", "içiyor", "disfaji", "burnundan"],
                "content": "Disfaji. İçtiği su ve lokmalar mantarın paralize ettiği N. glossopharyngeus nedeniyle burnundan geri gelmektedir."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis) Sonucu",
                "keywords": ["idrar", "tahlil", "dansite", "ph"],
                "content": "Dansite: 1.020 | pH: 7.2 | Normal."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "derece", "sıcaklık", "nabız", "solunum", "epistaksis", "kanama", "hava kesesi"],
                "content": "Ateş: 38.2 °C (Normal) | Kalp: 72 atım/dk (Anemiye bağlı hafif taşikardi) | Solunum: 22 nefes/dk | Tek taraflı masif taze burun kanaması (Epistaksis)."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Endoskopi & Mantar Teşhisi",
                "keywords": ["endoskopi", "hava kesesi", "mikoz", "aspergillus", "arter"],
                "content": "Endoskopi: Hava kesesi (Guttural pouch) lümeninde Arteria carotis interna üzerinde siyah/yeşilimsi Aspergillus fumigatus mantar plağı ve erode olmuş arter erozyonu."
            }
        }
    },
    "Vaka L (Poyraz)": {
        "kod": "VAKA_L",
        "sikayet": "Geçirilmiş Gurm hastalığı sonrası parotis bölgesinde ağrılı şişlik, çift taraflı koyu pürülan burun akıntısı ve başı uzatarak durma.",
        "categories": {
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem", "yiyor", "su", "içiyor", "parotis"],
                "content": "Boğaz ve parotis bölgesindeki ağrı nedeniyle başını bükememekte, yemliği reddetmektedir."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis) Sonucu",
                "keywords": ["idrar", "tahlil", "dansite", "ph"],
                "content": "Dansite: 1.022 | pH: 7.4 | Normal."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "derece", "sıcaklık", "nabız", "solunum", "gurm", "empiyem", "kondroit"],
                "content": "Ateş: 39.3 °C | Kalp: 68 atım/dk | Solunum: 20 nefes/dk | Parotis bölgesinde bilateral sıcak ağrılı şişlik, çift taraflı pürülan burun akıntısı."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Endoskopi & Rötngen",
                "keywords": ["endoskopi", "hava kesesi", "kondroit", "irin", "streptococcus"],
                "content": "Endoskopi: Hava kesesinde koyu kıvamlı irin birikimi ve taşlaşmış irin yumakları (Chondroid / Kondroitler). Kültür: Streptococcus equi subsp. equi üremesi +."
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
        (Örn: <i>"Hayvan ne ile besleniyor?"</i>, <i>"İştah durumu nasıl?"</i>, <i>"İdrar tahlili sonucu nedir?"</i>, <i>"Ateşi kaç derece?"</i>, <i>"Hemogram tahlili istiyorum"</i>).
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

# AUTOMATIC DISPLAY OF MACROSCOPIC CLINICAL IMAGES UPON CASE SELECTION (CLEAN DISPLAY)
if "makroskopik_gorsel" in active_case:
    mg = active_case["makroskopik_gorsel"]
    img_path = find_gorsel_path(mg["file"])
    if img_path:
        st.image(img_path, use_container_width=True)
    else:
        uploaded_img = st.file_uploader(
            f"📷 Görsel Yükleyiniz (.jpg / .png):",
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
        placeholder="Örn: İştah durumu nasıl?, İdrar tahlili sonucu nedir?, Deri kazıntısı yapalım..."
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
        
        # MICROSCOPIC IMAGES DISPLAYED ONLY AFTER BEING QUERY-TRIGGERED (CLEAN DISPLAY)
        if "gorsel" in item:
            g = item["gorsel"]
            img_path_m = find_gorsel_path(g["file"])
            if img_path_m:
                st.image(img_path_m, use_container_width=True)
            else:
                up_micro = st.file_uploader(
                    f"📷 Mikroskopik Görsel Yükleyiniz (.jpg / .png):",
                    type=["jpg", "jpeg", "png"],
                    key=f"up_micro_{item['cat_key']}"
                )
                if up_micro is not None:
                    st.image(up_micro, use_container_width=True)

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
            st.markdown("#### 🔑 Bu Vakanın Gizli Cevap Anahtarı & Tüm Bilgileri:")
            for ck, cv in active_case["categories"].items():
                st.markdown(f"**• {cv['name']}:** {cv['content']}")
        elif pass_code:
            st.error("Hatalı Şifre!")
