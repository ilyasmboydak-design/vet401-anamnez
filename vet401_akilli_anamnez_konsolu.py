import streamlit as st
import re
import os

# Page Config
st.set_page_config(
    page_title="VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu",
    page_icon="🐄",
    layout="wide",
)

# Custom CSS Styling
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
    .teacher-box {
        background-color: #FFF2CC;
        border-left: 6px solid #D66000;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to safely find image file regardless of extension case or path
def find_gorsel_path(target_filename):
    if not target_filename:
        return None
    
    # Direct check
    if os.path.exists(target_filename):
        return target_filename
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(base_dir, target_filename),
        os.path.join(base_dir, "gorseller", os.path.basename(target_filename)),
        os.path.join("/workspace/artifacts", os.path.basename(target_filename)),
        os.path.join("/workspace/artifacts", target_filename)
    ]
    
    for p in possible_paths:
        if os.path.exists(p):
            return p
            
    # Fuzzy match in gorseller directory
    gorseller_dir = os.path.join(base_dir, "gorseller")
    if os.path.exists(gorseller_dir):
        target_clean = os.path.splitext(os.path.basename(target_filename))[0].lower()
        for fname in os.listdir(gorseller_dir):
            fname_clean = os.path.splitext(fname)[0].lower()
            if fname_clean == target_clean:
                return os.path.join(gorseller_dir, fname)
                
    return None

# Cases Knowledge Base
CASES = {
    "Vaka A (Papatya)": {
        "kod": "VAKA_A",
        "sikayet": "Hocam, Papatya isimli ineğimiz iki gündür yem yemiyor, sütü tamamen kesildi. Gerdanının altı ve çene arası hamur gibi şişmiş, dokununca soğuk. Durduğu yerde çok durgun ve göğsünü öne doğru uzatıp duruyor...",
        "egitmen_paneli": {
            "kesin_tani": "Traumatik Retikuloperikarditis (TRP) / Fibrinöz-Pürülan Perikarditis",
            "ayirici_tani": "Vejetatif Valvüler Endokardit (çalkantı sesi yok, üfürüm var, retikulum ağrı testi -), Cor Pulmonale (ağrı testi -, polisitemi +, fibrinojen normal), VCCT (ağızdan hemoptizi fışkırması, melena).",
            "tedavi_protokolu": "Cerrahi (Rumenotomi + Magnet/Mıknatıs yutturma, Perikardiyosentez ve drenaj), Geniş spektrumlu parenteral antibiyotik (Seftiofur / Penisilin), Parenteral NSAID (Flunixin Meglumine).",
            "sakincali_ilaclar": "⚠️ Yüksek hacimli hızlı IV sıvı yüklemesi KONTRENDİKEDİR! (Kardiyak stazı olan hayvanda akut akciğer ödemi ve kardiyak arreste yol açar)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba", "tel", "çivi", "yabancı"],
                "content": "İşletmede entansif kaba/yoğun yem karma rasyonu uygulanmaktadır. Balya parçalama esnasında kaba yeme inşaat tellerinin ve çivilerin karışmış olabileceği belirtilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik"],
                "content": "Hayvan Ceyhan ovasındaki (rakım ~50 metre) tesisde doğup büyümüştür. Herhangi bir yayla veya yüksek rakım nakli öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü"],
                "content": "Geçmişinde kaydedilmiş kronik bir mastitis veya metritis öyküsü bulunmamaktadır. 2 ay önce sorunsuz doğum yapmıştır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketim Durumu",
                "keywords": ["iştah", "yem yeme", "yeme", "anoreksi", "hiporeksi", "yutma", "geviş"],
                "content": "Tam Anoreksi (İştah tamamen kapalı). Şiddetli retiküler/perikardiyal ağrı ve toksik durum nedeniyle yem ve kaba yem tüketimi sıfırlanmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "dehidrasyon", "ödem"],
                "content": "Vücut Sıcaklığı: 39.8 °C | Kalp Frekansı: 102 atım/dk | Solunum Frekansı: 42 nefes/dk | Mukoza: Soluk pembe | CRT: 2.5 saniye | Dehidrasyon: %6 | Gerdan ve çene altında soğuk hamur ödem | Vena jugularis stazı +, yalancı jugular nabız +."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "splashing", "muffled", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Gaz ve pürülan sıvının çalkalanmasına bağlı çamaşır makinesi / su şılpırtısı (splashing) sesi ve boğuk kalp sesleri duyuluyor. Akciğer Oskültasyonu: Ventro-lateral alanda sesler hafif azalmış."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Sopa Testi: +++ Şiddetli inleme | Withers Pinch (Cidago) Testi: +++ Çökme reddi ve inleme | Kalp arkası perküsyonda ağrı reaksiyonu POZİTİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f"],
                "content": "Eritrosit (RBC): 5.1 x10⁶/µL | Hemoglobin (Hb): 8.5 g/dL | Hematokrit (PCV): %26 | Lökosit (WBC): 18.5 x10³/µL (Şiddetli Lökositoz) | Plazma Fibrinojeni: 1250 mg/dL (Tavan) | PP/F Oranı: 6.3 (Yangısal)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "bilirubin", "albümin", "globülin", "troponin"],
                "content": "Total Protein: 9.2 g/dL | Albümin: 2.4 g/dL | Globülin: 6.8 g/dL (Hipergamaglobülinemi) | AST: 145 U/L | GGT: 32 U/L | BUN: 28 mg/dL | Kardiyak Troponin I: 1.85 ng/mL (Ağır Miyokard / Perikard Hasarı)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.31 | pO₂: 58 mmHg | pCO₂: 48 mmHg | HCO₃⁻: 19.2 mmol/L | Baz Açığı: -4.5 mmol/L | Laktat: 3.8 mmol/L (Doku hipoksisi)."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "ürin", "dansite", "ph idrar", "proteinüri", "glikozüri", "keton", "sediment", "hematüri"],
                "content": "İdrar Renk: Koyu sarı | Dansite: 1.022 | pH: 6.5 | Protein: ++ (2+) | Glikoz: Negatif | Keton: Negatif | Mikroskopik Sediment: Nadir lökosit, epitel hücresi, hematüri yok."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Perikardiyosentez",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "perikardiyosentez", "mıknatıs", "tel"],
                "content": "Ekokardiyografi: Perikardiyal kesede hiperekojen fibrin iplikçikleri ve yoğun pürülan sıvı birikimi (Pericardial Effusion). Retikulum USG: Retikulum duvarında yabancı cisim batma gölgesi. Perikardiyosentez: Pis kokulu pürülan eksudat, kültürde Trueperella pyogenes üremesi."
            }
        }
    },
    "Vaka B (Yonca)": {
        "kod": "VAKA_B",
        "sikayet": "Hocam, Yonca isimli ineğimiz haftalardır bir iyileşip bir hastalanıyor. Ateşi bir yükseliyor bir düşüyor. Zayıfladı, sol ön bacağında topallık başladı ve sütü yarı yarıya düştü...",
        "egitmen_paneli": {
            "kesin_tani": "Vejetatif Valvüler Endokardit (Triküspid Kapak Tutulumu)",
            "ayirici_tani": "TRP (su çalkantı sesi ve retikulum ağrı testleri yoktur, üfürüm vardır), Cor Pulmonale (bakteriyel yangı ve üfürüm yoktur).",
            "tedavi_protokolu": "Uzun süreli bakterisidal antibiyoterapi (Procaine Penicillin G + Gentamisin veya Seftiofur 3-4 hafta), Antikoagülan (Düşük doz Heparin / Aspirin), Flunixin meglumine.",
            "sakincali_ilaclar": "⚠️ Yüksek doz Kortikosteroid kullanımı KONTRENDİKEDİR! (Bakteriyemi ve vejetasyonu şiddetlendirir, septik emboli riskini artırır)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj"],
                "content": "Standart süt sığırı rasyonu verilmektedir. Yem kalitesi iyidir, taze ot ve silaj tüketmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil"],
                "content": "Ova işletmesinde barındırılmaktadır. Rakım değişimi yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme", "öykü", "ayak"],
                "content": "1.5 ay önce ağır bir septik metritis (rahim iltihabı) ve kronik ayak tabanı ülseri öyküsü mevcuttur."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketim Durumu",
                "keywords": ["iştah", "yem yeme", "yeme", "anoreksi", "hiporeksi", "seçici"],
                "content": "Hiporeksi (İştah dalgalı ve seçici). Ateş yükseldiğinde yem yemeyi bırakmakta, ateş düşünce sadece lezzetli kaba yemleri seçerek az miktarda tüketmektedir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "topallık", "eklem"],
                "content": "Vücut Sıcaklığı: 39.9 °C (Tekrarlayan dalgalı ateş) | Kalp Frekansı: 108 atım/dk | Solunum Frekansı: 38 nefes/dk | Mukoza: Soluk | CRT: 2.0 saniye | Sol ön carpal eklemde sıcak ödemli şişlik ve topallık | Vena jugularis nabzı POZİTİF."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "murmur", "boğuk", "akciğer"],
                "content": "Kalp Oskültasyonu: Sağ 3-4. interkostal aralıkta (Triküspid kapak odağında) belirgin yumuşak ve ıslık benzeri pan-sistolik üfürüm (systolic murmur) duyuluyor. Su çalkantı sesi YOKTUR. Akciğer oskültasyonu normal."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testleri (Sopa, Withers) tamamen NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "pp/f"],
                "content": "Eritrosit (RBC): 4.8 x10⁶/µL | Hematokrit (PCV): %24 (Anemi) | Lökosit (WBC): 22.4 x10³/µL (Sola kaymalı Nötrofili) | Plazma Fibrinojeni: 980 mg/dL | PP/F: 7.1."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "albümin", "globülin", "troponin"],
                "content": "Total Protein: 9.6 g/dL | Albümin: 2.1 g/dL | Globülin: 7.5 g/dL (Poliklonal Hipergamaglobülinemi) | AST: 110 U/L | BUN: 34 mg/dL | Kreatinin: 1.4 mg/dL | Troponin I: 0.82 ng/mL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı"],
                "content": "Kan pH: 7.34 | pO₂: 62 mmHg | pCO₂: 42 mmHg | HCO₃⁻: 21.0 mmol/L | BE: -3.1 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "ürin", "dansite", "ph idrar", "proteinüri", "sediment", "hematüri", "silindir"],
                "content": "İdrar Renk: Bulanık sarı | Dansite: 1.018 | pH: 7.0 | Protein: ++ (2+) | Mikroskopik Sediment: Bol eritrosit (Mikrohematüri +), lökositler ve lökosit silindirleri (Embolik glomerülonefrit sekeli)."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Kan Kültürü",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "triküspid", "vejetasyon"],
                "content": "Ekokardiyografi: Triküspid kapak yaprakçıklarında 2.5 cm çapında karnabahar benzeri hiperekojen vejetatif trombotik kitleler. Kan Kültürü: Trueperella pyogenes üremesi POZİTİF."
            }
        }
    },
    "Vaka C (Zümrüt)": {
        "kod": "VAKA_C",
        "sikayet": "Hocam, Zümrüt isimli düvemizi 3 ay önce Pozantı yaylasına çıkarmıştık. İki haftadır göğsünün altı ve gerdanı şişti, yürütürken hemen nefes nefese kalıyor ve olduğu yere çöküyor...",
        "egitmen_paneli": {
            "kesin_tani": "Cor Pulmonale / Yüksek Rakım Hastalığı (High Altitude / Brisket Disease)",
            "ayirici_tani": "TRP (Ateş, lökositoz, yüksek fibrinojen ve çalkantı sesi yoktur; PCV %54 polisitemi vardır), Vejetatif Endokardit (üfürüm ve lökositoz yoktur).",
            "tedavi_protokolu": "Hayvanın acilen düşük rakıma (~50-100 m) nakledilmesi (Temel Altın Standart), Oksijen desteği, Diüretik (Furosemid), İnotropik destek.",
            "sakincali_ilaclar": "⚠️ Yüksek rakımda tutmaya devam etmek ve IV sıvı yüklemesi yapmak KONTRENDİKEDİR! (Sağ kalp yükünü artırıp akut akciğer ödemine neden olur)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "ot", "mera", "yayla", "otlatma"],
                "content": "Yayla merasında otlatılmaktadır. Kaba yem zengindir, ek yoğun yem verilmemektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "dağ"],
                "content": "Hayvan 3 ay önce Ceyhan ovasından Toros Dağları Pozantı Yaylasına (~2100 metre rakım) çıkarılmıştır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Geçmişinde kaydedilmiş herhangi bir enfeksiyöz veya kardiyak hastalık öyküsü yoktur."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketim Durumu",
                "keywords": ["iştah", "yem yeme", "yeme", "anoreksi", "hiporeksi"],
                "content": "Hafif Hiporeksi. Hipoksi ve çabuk yorulma nedeniyle otlamayı erken bırakmakta, yem tüketimi yavaşlamaktadır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "ödem"],
                "content": "Vücut Sıcaklığı: 38.6 °C (TAMAMEN NORMAL) | Kalp Frekansı: 96 atım/dk | Solunum Frekansı: 46 nefes/dk | Mukoza: Pembe | CRT: 1.8 saniye | Dehidrasyon: %0 | Gerdanda ve göğüs altında geniş alana yayılmış soğuk hamur ödem | Vena jugularis dolgun."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "çalkantı", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Hiperdinamik güçlü kalp sesleri duyulmaktadır. Üfürüm veya su çalkantı sesi YOKTUR. Akciğer oskültasyonu hafife alınmış veziküler sestir."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testlerinin tamamı NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "hematokrit", "pp/f", "polisitemi"],
                "content": "Eritrosit (RBC): 10.8 x10⁶/µL (Polisitemi) | Hemoglobin (Hb): 17.2 g/dL | Hematokrit (PCV): %54 (Aşırı yüksek) | Lökosit (WBC): 7.2 x10³/µL (TAMAMEN NORMAL) | Plazma Fibrinojeni: 320 mg/dL (NORMAL) | PP/F Oranı: 22.8."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "bilirubin", "albümin", "globülin", "troponin"],
                "content": "Albümin: 3.2 g/dL | Globülin: 4.1 g/dL | AST: 68 U/L | GGT: 18 U/L | BUN: 18 mg/dL | Kreatinin: 0.9 mg/dL | Kardiyak Troponin I: 0.12 ng/mL (Normal)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "hipoksi"],
                "content": "Kan pH: 7.36 | pO₂: 48 mmHg (Ağır Doku Hipoksisi) | pCO₂: 42 mmHg | HCO₃⁻: 23.5 mmol/L | Baz Açığı: -0.8 mmol/L | Laktat: 1.5 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "ürin", "dansite", "ph idrar", "proteinüri", "sediment"],
                "content": "İdrar Renk: Berrak açık sarı | Dansite: 1.025 | pH: 7.5 | Protein: Negatif | Glikoz: Negatif | Mikroskopik Sediment: Temiz."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Mikrobiyoloji",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "pulmoner", "ventrikül"],
                "content": "Ekokardiyografi: Sağ ventrikül serbest duvar kalınlığında artış (Sağ Ventrikül Hipertrofisi), pulmoner arter çapında genişleme. Kültür: Kan ve perikard sıvısında bakteri üremesi YOKTUR (Steril)."
            }
        }
    },
    "Vaka D (Yiğit)": {
        "kod": "VAKA_D",
        "sikayet": "Hocam, Yiğit isimli besi tosunumuz durduğu yerde aniden ağzından ve burnundan fışkırır tarzda taze kan akıtmaya başladı! Dışkısı da zift gibi kapkara çıkıyor...",
        "egitmen_paneli": {
            "kesin_tani": "Vena Cava Caudalis Trombozu Sendromu (VCCT) & Pulmoner Arter Anevrizma Rüptürü",
            "ayirici_tani": "Epistaksis / Burun kanaması (akciğer orijinli değildir), TRP (ağızdan fışkıran hemoptizi ve karaciğer apsesi ilişkisi yoktur).",
            "tedavi_protokolu": "Semptomatik ve destekleyici (Acil Kan Transfüzyonu, Hemostatik agentler: Traneksamik asit / Vitamin K1, Geniş spektrumlu antibiyotik), Prognoz son derece olumsuzdur (Acil kesim önerilir).",
            "sakincali_ilaclar": "⚠️ Heparin / Aspirin veya diğer antikoagülanların verilmesi KONTRENDİKEDİR! (Anevrizma kanamasını durdurulamaz hale getirip anında ölüme yol açar)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "besi", "kaba", "nişasta"],
                "content": "18 aylık besi danasıdır. Yoğun mısır ve arpa kırması ağırlıklı, kaba yemi aşırı yetersiz yüksek nişastalı besi rasyonu verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil"],
                "content": "Besi padoğunda barındırılmaktadır. Rakım değişikliği yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "asidoz", "şişkinlik", "timpani", "rumenitis"],
                "content": "Geçmişinde tekrarlayan akut/subakut rumen asidozu (yem çarpması) ve kronik hafif rumen timpani (şişkinlik) öyküsü vardır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketim Durumu",
                "keywords": ["iştah", "yem yeme", "yeme", "anoreksi", "hiporeksi"],
                "content": "Tam Anoreksi. Masif kan kaybı şoku ve solunum güçlüğü nedeniyle yem tüketimi tamamen durmuştur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "dolum", "kan", "hemoptizi", "melena", "dışkı"],
                "content": "Vücut Sıcaklığı: 39.2 °C | Kalp Frekansı: 118 atım/dk | Solunum Frekansı: 52 nefes/dk | Ağız/Burun: Köpüklü taze parlak kırmızı kan fışkırması (Hemoptizi) | Mukozalar: Bembeyaz (Ağır anemi) | CRT: 4.0 saniye | Dışkı: Siyah katran kıvamında (Melena)."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "boğuk", "rall", "akciğer"],
                "content": "Kalp Oskültasyonu: Taşikardik, zayıf düştü sesleri. Akciğer Oskültasyonu: Bilateral yaygın kaba raller ve hışırtı sesleri duyuluyor."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Retikulum ağrı testleri NEGATİF."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "rbc", "pcv", "anemi"],
                "content": "Eritrosit (RBC): 2.1 x10⁶/µL (Kritik Kan Kaybı Anemisi) | Hemoglobin (Hb): 4.2 g/dL | Hematokrit (PCV): %12 (Acil Transfüzyon Eşiği!) | Lökosit (WBC): 21.5 x10³/µL | Plazma Fibrinojeni: 1050 mg/dL | PP/F: 7.23."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "bilirubin", "karaciğer"],
                "content": "AST: 210 U/L (Karaciğer hasarı) | GGT: 68 U/L (Karaciğer/safra yolu) | BUN: 42 mg/dL | Kreatinin: 1.6 mg/dL | Total Bilirubin: 1.2 mg/dL | İndirekt Bilirubin: 0.8 mg/dL."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "baz açığı", "be", "laktat"],
                "content": "Kan pH: 7.24 | pO₂: 52 mmHg | pCO₂: 50 mmHg | HCO₃⁻: 18.5 mmol/L | Baz Açığı (BE): -6.2 mmol/L | Laktat: 4.2 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "ürin", "dansite", "ph idrar", "proteinüri", "sediment", "ürobilinojen"],
                "content": "İdrar Renk: Koyu sarı | Dansite: 1.020 | pH: 6.8 | Protein: + (1+) | Ürobilinojen: Yüksek | Mikroskopik Sediment: Masif hematüri yok."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Mikrobiyoloji",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "bakteri", "karaciğer", "apse", "vena cava", "trombüs"],
                "content": "Abdominal Ultrasonografi: Karaciğer parankiminde 6 cm çapında kılıflı apse odağı (Hepatic Abscess), Vena Cava Caudalis lümeninde tıkayıcı trombüs ekojenitesi. Torakal USG: Pulmoner arter çevresinde hematom ve anevrizma alanları."
            }
        }
    },
    "Vaka E (Kudret)": {
        "kod": "VAKA_E",
        "sikayet": "Hocam, Kudret isimli danamızın gözlerinin etrafında ve boynunda dairesel, bozuk para gibi gri renkli kireç gibi kabuklar çıktı. Tüyü dökülüyor ama hiç kaşınmıyor...",
        "makroskopik_gorsel": {
            "fig": "Figure 1.2-1",
            "title": "Klinik Mantar Lezyonu (Baş ve Göz Çevresi)",
            "file": "figure_1_2_1.jpg",
            "desc": "Göz çevresi ve yüzde dairesel, grimsi-beyaz kireç benzeri kabarık kabuklanma ve alopezi (tüy kaybı)."
        },
        "egitmen_paneli": {
            "kesin_tani": "Dermatofitoz / Trikofiti (Trichophyton verrucosum)",
            "ayirici_tani": "Sarkoptik Uyuz (şiddetli kaşıntı, likenifikasyon ve akar var), Dermatofiloz (nemli fırça kabuklar, Dermatophilus congolensis bakterisi).",
            "tedavi_protokolu": "Lokal antifungal banyo/solüsyon (Enilkonazol / İyotlu solüsyonlar), Sistemik Vitamin A ve E desteği, Ahır dezenfeksiyonu ve güneş ışığı.",
            "sakincali_ilaclar": "⚠️ Sistemik veya lokal Kortikosteroid (Deksametazon) kullanımı KONTRENDİKEDİR! (Hücresel bağışıklığı baskılayarak mantarın tüm vücuda genelleşmesine neden olur)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "ot", "mera", "silaj"],
                "content": "Besi rasyonu ile beslenmektedir. Yem kalitesi normaldir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "ahır", "rutubet", "karanlık"],
                "content": "Karanlık, havasız ve rutubetli kapalı bir padokta barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Geçmişinde sistemik bir hastalık öyküsü bulunmamaktadır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketim Durumu",
                "keywords": ["iştah", "yem yeme", "yeme", "anoreksi", "hiporeksi"],
                "content": "İştah TAMAMEN NORMAL. Yemini ve suyunu iştahla tüketmektedir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "deri", "kabuk", "alopezi"],
                "content": "Vücut Sıcaklığı: 38.8 °C (NORMAL) | Kalp Frekansı: 76 atım/dk | Solunum Frekansı: 24 nefes/dk | Mukozalar: Pembe | Deri: Baş, göz çevresi ve boyunda dairesel, belirgin sınırlı, grimsi-beyaz kireçimsi kabuklanma ve alopezi. Kaşıntı reaksiyonu yok."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "pcv"],
                "content": "Eritrosit (RBC): 6.8 x10⁶/µL | Hematokrit (PCV): %34 | Lökosit (WBC): 8.1 x10³/µL (NORMAL) | Fibrinojen: 350 mg/dL (NORMAL)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "albümin", "globülin"],
                "content": "Total Protein: 7.1 g/dL | Albümin: 3.4 g/dL | Globülin: 3.7 g/dL | AST: 52 U/L | GGT: 16 U/L (Tüm karaciğer ve böbrek değerleri normal)."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "ürin", "dansite", "ph idrar", "proteinüri"],
                "content": "İdrar Renk: Berrak sarı | Dansite: 1.028 | pH: 7.8 | Protein: Negatif | Glikoz: Negatif | Sediment: Temiz."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "Deri Kazıntısı & Mikroskopik Mantar Teşhisi",
                "keywords": ["mikroskop", "kazıntı", "deri kazıntısı", "koh", "mantar", "artrospor", "lam"],
                "gorsel": {
                    "fig": "Figure 1.2-11",
                    "title": "Mikroskopik Mantar Sporu (%10 KOH Hazırlığı)",
                    "file": "figure_1_2_11.jpg",
                    "desc": "%10 KOH ile muamele edilmiş deri kazıntısında kıl şaftını saran küresel Trichophyton verrucosum ektotriks artrospor dizilimi (40x)."
                },
                "content": "%10 KOH ile hazırlanan deri kazıntısında kıl etrafında ektotriks artrospor zincirleri belirgin olarak izlenmiştir."
            }
        }
    },
    "Vaka F (Nazar)": {
        "kod": "VAKA_F",
        "sikayet": "Hocam, Nazar isimli ineğimiz boynunu, kulaklarını ve sırtını ahırın demirlerine sürtmekten kanatıyor! Derisi fil derisi gibi kalınlaştı, kıvrım kıvrım oldu...",
        "makroskopik_gorsel": {
            "fig": "Figure 1.3-13 & 1.3-15",
            "title": "Klinik Uyuz Lezyonu (Deride Kalınlaşma ve Likenifikasyon)",
            "file": "figure_1_3_13.jpg",
            "desc": "Kulak kepçesi, boyun ve sırtta derinin fil derisi gibi kalınlaşması (likenifikasyon), kaşıntı eksforyasyonları ve kepekli döküntü."
        },
        "egitmen_paneli": {
            "kesin_tani": "Sarkoptik Uyuz / Scabies (Sarcoptes scabiei var. bovis)",
            "ayirici_tani": "Trikofiti (kaşıntı yoktur, kireç kabuklar vardır), Psoroptik Uyuz (yüzde değil sırt ve crupta başlar), Ürtiker (geçici ödem plaklarıdır).",
            "tedavi_protokolu": "Sistemik Endektoparazitosit (Ivermectin / Doramectin SC 14 gün arayla 2 doz), Lokal Akarisit yıkama (Amitraz / Permethrin), Kaşıntı yatıştırıcılar.",
            "sakincali_ilaclar": "⚠️ Yüzeysel kazıntı almak yanlış negatifliğe yol açar! Kapiller kanama görülünceye kadar DERİN kazıntı zorunludur."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "ot", "mera"],
                "content": "Mera ve ahır karma besleme yapılmaktadır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sürü", "uyuz", "temas"],
                "content": "Sürüye yeni katılan dış kaynaklı hayvanlarla temas öyküsü mevcuttur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Geçmişinde alerjik veya dermatolojik hastalık öyküsü yoktur."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketim Durumu",
                "keywords": ["iştah", "yem yeme", "yeme", "anoreksi", "hiporeksi", "huzursuzluk"],
                "content": "Hiporeksi (İştah azlığı). Sürekli kaşınma ve huzursuzluk nedeniyle yem yemeyi yarıda bırakmaktadır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "deri", "kaşıntı", "likenifikasyon"],
                "content": "Vücut Sıcaklığı: 39.0 °C | Kalp Frekansı: 88 atım/dk | Solunum Frekansı: 30 nefes/dk | Mukozalar: Pembe | Deri: Kulak kepçesi, boyun ve sırtta derinin fil derisi gibi kalınlaşması (Likenifikasyon), tüy kaybı, kabuklanma ve kanamalı kaşıntı izleri (eksforyasyon)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eozinofil", "parazit"],
                "content": "Eritrosit (RBC): 6.2 x10⁶/µL | PCV: %31 | Lökosit (WBC): 14.5 x10³/µL | Eozinofil: %12 (Belirgin Eozinofili - Paraziter/Alerjik Yanıt) | Fibrinojen: 480 mg/dL."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "albümin", "globülin"],
                "content": "Total Protein: 8.2 g/dL | Albümin: 3.1 g/dL | Globülin: 5.1 g/dL (Hafif artış) | AST: 48 U/L | GGT: 18 U/L."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "ürin", "dansite", "ph idrar", "proteinüri"],
                "content": "İdrar Renk: Sarı | Dansite: 1.025 | pH: 7.6 | Protein: Negatif | Sediment: Temiz."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "Derin Deri Kazıntısı & Akar Mikroskopisi",
                "keywords": ["mikroskop", "kazıntı", "deri kazıntısı", "akar", "uyuz", "mineral yağ", "sarcoptes"],
                "gorsel": {
                    "fig": "Figure 1.3-18",
                    "title": "Mikroskopik Sarcoptes Scabiei Akari",
                    "file": "figure_1_3_18.jpg",
                    "desc": "Derin deri kazıntısında mineral yağ altında tespit edilen canlı ergin Sarcoptes scabiei akarı (10x-40x)."
                },
                "content": "Kapiller kanama görülünceye kadar alınan derin deri kazıntısında canlı Sarcoptes scabiei ergin akarları ve oval yumurtaları tespit edilmiştir."
            }
        }
    },
    "Vaka G (Çiçek)": {
        "kod": "VAKA_G",
        "sikayet": "Hocam, Çiçek isimli Alaca ineğimiz dün güneşte otladıktan sonra vücudundaki beyaz deri yerleri kabardı, su topladı ve tabaka halinde soyulmaya başladı! Siyah deri yerlerinde hiçbir şey yok...",
        "makroskopik_gorsel": {
            "fig": "Figure 1.7-35",
            "title": "Hepatojen Fotosensitizasyon (Pigmentsiz Deri Nekrozu)",
            "file": "figure_1_7_35.jpg",
            "desc": "Yalnızca beyaz (pigmentsiz) deri alanlarında soyulma, hamur ödemi ve nekroz; siyah pigmentli derinin tamamen sağlam kalması."
        },
        "egitmen_paneli": {
            "kesin_tani": "Hepatojen (Sekonder) Fotosensitizasyon / Filloeritrin Toksikasyonu",
            "ayirici_tani": "Primer Fotosensitizasyon (Karaciğer enzimleri AST/GGT normaldir, doğrudan bitkisel toksin alınmıştır), Ürtiker (deride soyulma/nekroz yoktur, geçici plaklardır).",
            "tedavi_protokolu": "Hayvanın derhal karanlık/gölgelik kapalı ahıra alınması (Zorunlu), Karaciğer koruyucu/destekleyici (B-kompleks, Metionin, Dextrose), Antihistaminik (Avil), Flunixin meglumine.",
            "sakincali_ilaclar": "⚠️ Hayvanı güneşte tutmaya devam etmek ve hepatotoksik ilaçlar vermek KONTRENDİKEDİR!"
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "ot", "mera", "lantana", "otlatma", "toksik"],
                "content": "Nemli merada yabani otların ve Lantana türü bitkilerin yoğun olduğu merada otlatılmıştır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "güneş", "otlak"],
                "content": "Açık merada dik güneş ışığına maruz kalmıştır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Geçmişinde karaciğer kelebeği (Fascioliasis) öyküsü bulunmaktadır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketim Durumu",
                "keywords": ["iştah", "yem yeme", "yeme", "anoreksi", "hiporeksi"],
                "content": "Şiddetli Anoreksi. Deri ağrısı, güneş hassasiyeti ve karaciğer yetmezliği nedeniyle yem yemeyi tamamen durdurmuştur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "ikter", "deri", "güneş", "soyulma", "pigment"],
                "content": "Vücut Sıcaklığı: 39.3 °C | Kalp Frekansı: 92 atım/dk | Solunum Frekansı: 36 nefes/dk | Mukozalar: Belirgin İkterik (Sarı) | Deri: YALNIZCA beyaz (pigmentsiz) deri bölgelerinde eritem, hamur ödemi, su toplaması ve deri tabakasının soyulması/nekrozu. Siyah deri alanları tamamen SAĞLAM."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "pcv"],
                "content": "Eritrosit (RBC): 5.8 x10⁶/µL | PCV: %32 | Lökosit (WBC): 14.2 x10³/µL (Lökositoz) | Fibrinojen: 650 mg/dL."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Karaciğer Enzimleri",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "bilirubin", "albümin", "karaciğer", "filloeritrin"],
                "content": "AST: 290 U/L (Ağır Karaciğer Parankim Hasarı) | GGT: 180 U/L (Ağır Safrayolu Kolestazı) | Total Bilirubin: 3.2 mg/dL | İndirekt Bilirubin: 1.8 mg/dL | Albümin: 2.6 g/dL | Kandaki Filloeritrin Düzeyi: TAVAN."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "ürin", "dansite", "ph idrar", "bilirubinüri", "çay"],
                "content": "İdrar Renk: Koyu çay / kahverengi | Dansite: 1.022 | pH: 7.2 | Bilirubinüri: +++ (3+) | Ürobilinojen: Şiddetli Yüksek | Protein: +."
            }
        }
    },
    "Vaka H (Ateş)": {
        "kod": "VAKA_H",
        "sikayet": "Hocam, Ateş isimli tosunumuzun böğründe ve boynunda yarım saat içinde bozuk para gibi kabarık kabarık ödemli şişlikler fışkırdı! Hayvan huzursuzca böğrünü yalıyor...",
        "makroskopik_gorsel": {
            "fig": "Figure 1.5-1",
            "title": "Akut Ürtiker (Ödem Plakları)",
            "file": "figure_1_5_1.jpg",
            "desc": "Gövde ve boyun derisinde aniden beliren dairesel ödemli kabarık ürtiker plakları (urtica)."
        },
        "egitmen_paneli": {
            "kesin_tani": "Akut Allerjik Ürtiker (Urticaria)",
            "ayirici_tani": "Fotosensitizasyon (deride soyulma/nekroz vardır ve sadece beyaz deridedir), Sığırların Yumrulu Deri Hastalığı / LSD (nodüller serttir, nekroze olur, yüksek ateş vardır).",
            "tedavi_protokolu": "Hızlı etkili Antihistaminik (Pheniramine Maleate - Avil), Kortikosteroid (Deksametazon), IV Kalsiyum Glukonat solüsyonu (damar geçirgenliğini azaltmak için).",
            "sakincali_ilaclar": "⚠️ Gebe hayvanlarda yüksek doz Deksametazon kullanımı KONTRENDİKEDİR! (Abortusa neden olur)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "alerjen", "değişiklik"],
                "content": "Yeni bir yem katkı maddesi ve rasyon değişikliği yapılmıştır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "böcek", "sinek"],
                "content": "Böcek/sinek sokması öyküsü mevcuttur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "aşı", "enjeksiyon"],
                "content": "1 saat önce yeni bir biyolojik aşı enjeksiyonu uygulanmıştır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketim Durumu",
                "keywords": ["iştah", "yem yeme", "yeme", "anoreksi", "hiporeksi"],
                "content": "İştah NORMAL, ancak huzursuzluk nedeniyle yem yemeyi ara sıra durdurmaktadır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "crt", "urtica", "örtiker", "plak", "ödem"],
                "content": "Vücut Sıcaklığı: 38.7 °C (NORMAL) | Kalp Frekansı: 82 atım/dk | Solunum Frekansı: 28 nefes/dk | Mukozalar: Pembe | Deri: Gövde, boyun ve omuz derisinde aniden beliren, parmakla basıldığında çukurlaşan (pitting edema), ödemli, kabarık dairesel ürtiker plakları (urtica/wheals)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eozinofil"],
                "content": "Eritrosit (RBC): 6.5 x10⁶/µL | PCV: %33 | Lökosit (WBC): 10.2 x10³/µL | Eozinofil: %9 (Alerjik Eozinofili) | Fibrinojen: 320 mg/dL."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "albümin"],
                "content": "Total Protein: 7.2 g/dL | Albümin: 3.5 g/dL | AST: 45 U/L | GGT: 15 U/L (Biyokimya tamamen normal)."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "ürin", "dansite", "ph idrar"],
                "content": "İdrar Renk: Berrak | Dansite: 1.026 | pH: 7.5 | Protein: Negatif | Sediment: Temiz."
            }
        }
    },
    "Vaka I (Fırtına)": {
        "kod": "VAKA_I",
        "sikayet": "Hocam, Fırtına isimli buzağımız dün geceden beri gırtlağından düdük sesi gibi hırıl hırıl ses çıkararak nefes alıyor! Boğazına dokununca öksürük krizine giriyor, yem yutamıyor...",
        "egitmen_paneli": {
            "kesin_tani": "Akut Larenjit ve Larenks Ödemi / Nekrotik Larenjit (Diphtheria)",
            "ayirici_tani": "Bronkopnömoni (akciğerde raller ve kan gazında hipoksi vardır), Trakeal kolaps (akciğer sesleri ve yaş farkı).",
            "tedavi_protokolu": "Ödem çözücü Kortikosteroid (Deksametazon 1-2 mg/kg - Hayat kurtarıcı), Geniş spektrumlu antibiyotik (Penicillin G / Seftiofur / Oxytetracycline), NSAID (Flunixin Meglumine), Gerekirse acil Trakeotomi.",
            "sakincali_ilaclar": "⚠️ Ağır larengeal darlık varken ağızdan zorla hap/likit içirmek KONTRENDİKEDİR! (Aspirasyon pnömonisine yol açar)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "süt", "buzağı", "kaba yem"],
                "content": "Buzağı büyütme yemi ve kuru ot verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "cereyan", "rüzgar", "soğuk"],
                "content": "Rüzgarlı ve cereyanlı bireysel buzağı kulübesinde barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Geçmişinde solunum yolu hastalığı öyküsü yoktur."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketim Durumu",
                "keywords": ["iştah", "yem yeme", "yeme", "anoreksi", "hiporeksi", "yutma", "dysphagia"],
                "content": "Dysphagia (Yutma Ağrısı). Gırtlaktaki ödem ve ağrı nedeniyle yem ve süt yutamamakta, ağzına aldığı yemi yere düşürmektedir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "stridor", "larenks", "ödem", "öksürük"],
                "content": "Vücut Sıcaklığı: 39.8 °C (Yüksek Ateş) | Kalp Frekansı: 110 atım/dk | Solunum Frekansı: 54 nefes/dk | Belirgin İnspiratorik Dispne ve Larengeal Stridor (Düdük sesi) | Larenks palpasyonunda şiddetli ağrı ve refleks öksürük."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "stridor", "rall", "akciğer"],
                "content": "Larenks Oskültasyonu: Şiddetli inspiratorik stridor (gürültülü darlık sesi). Akciğer Oskültasyonu: Akciğer parankim ve veziküler sesleri TAMAMEN NORMAL. Patoloji üst solunum yolundadır."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "pcv"],
                "content": "Eritrosit (RBC): 7.1 x10⁶/µL | PCV: %35 | Lökosit (WBC): 18.2 x10³/µL (Lökositoz) | Plazma Fibrinojeni: 950 mg/dL (Ateşli yangısal)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "albümin"],
                "content": "Total Protein: 7.0 g/dL | Albümin: 3.2 g/dL | AST: 55 U/L | GGT: 18 U/L (Organ biyokimyası normal)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "oksijen"],
                "content": "Kan pH: 7.38 | pO₂: 92 mmHg (NORMAL - Akciğer gaz değişimi sağlam) | pCO₂: 44 mmHg (NORMAL) | HCO₃⁻: 24.1 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "ürin", "dansite", "ph idrar"],
                "content": "İdrar Renk: Açık sarı | Dansite: 1.020 | pH: 7.2 | Protein: Negatif | Sediment: Temiz."
            }
        }
    },
    "Vaka J (Şahin)": {
        "kod": "VAKA_J",
        "sikayet": "Hocam, Şahin isimli tosunumuzun boynuzunu kestirmiştik. Sol burun deliğinden leş gibi pis kokulu sarı irin akıyor, sol gözünün üstüne dokununca tos vurmaya çalışıyor...",
        "egitmen_paneli": {
            "kesin_tani": "Kronik Frontal Sinüzit (Sinusitis Frontalis)",
            "ayirici_tani": "Akciğer enfeksiyonu (akıntı tek taraflı ve pis kokuludur, akciğer sesleri normaldir), Enzootik Nazal Tümör (kötü koku ve boynuz kesimi öyküsü farklıdır).",
            "tedavi_protokolu": "Sinüs Trepanasyonu (Cerrahi olarak delinme) + Ilık antiseptik solüsyonlarla günlük irrigasyon/yıkama, Sistemik antibiyotik (Penicillin G / Seftiofur), Parenteral NSAID.",
            "sakincali_ilaclar": "⚠️ Yıkama sıvısını yüksek basınçla sıkmak KONTRENDİKEDİR! (Cribriform tabakadan beyne enfeksiyon yayılma riski yaratır)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor"],
                "content": "Besi rasyonu ile beslenmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "boynuz", "dehorning", "kesim"],
                "content": "1 ay önce hijyenik olmayan şartlarda boynuz kesimi (dehorning) yapılmıştır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Geçmişinde solunum hastalığı yoktur."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketim Durumu",
                "keywords": ["iştah", "yem yeme", "yeme", "anoreksi", "hiporeksi", "baş ağrısı"],
                "content": "Hiporeksi (İştah azalması). Frontal sinüsteki basınç ve şiddetli baş ağrısı nedeniyle yem tüketimi yavaşlamıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "sinüs", "akıntı", "fetid", "perküsyon", "matite"],
                "content": "Vücut Sıcaklığı: 39.1 °C | Sol burun deliğinden tek taraflı, pis kokulu (fetid) koyu mukopürülan akıntı | Sol frontal sinüs üzerinde perküsyonda mat ses (matite) ve şiddetli ağrı reaksiyonu | Başını sola eğik tutma."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "akciğer"],
                "content": "Kalp ve Akciğer oskültasyonu TAMAMEN NORMAL. Patoloji sinüs boşluğundadır."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen"],
                "content": "Eritrosit: 6.5 x10⁶/µL | PCV: %32 | Lökosit (WBC): 15.8 x10³/µL | Fibrinojen: 820 mg/dL."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp"],
                "content": "Organ biyokimyası normal sınırlar içerisindedir."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "ürin", "dansite", "ph idrar"],
                "content": "İdrar tahlili tamamen normaldir."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Sinüs Grafisi",
                "keywords": ["ultrason", "radyografi", "röntgen", "sinüs", "eksudat", "sıvı"],
                "content": "Frontal Sinüs Radyografisi: Sol frontal sinüs lümeninde mat opak eksudatif sıvı-hava seviyesi ve kemik trabeküllerinde kronik yangı."
            }
        }
    },
    "Vaka K (Rüzgar)": {
        "kod": "VAKA_K",
        "sikayet": "Hocam, atımız Rüzgar durduğu yerde aniden burnundan foşur foşur taze kan akıtmaya başladı! Samanı ağzına alıyor ama yutamıyor, içtiği su burnundan geri çıkıyor...",
        "egitmen_paneli": {
            "kesin_tani": "Hava Kesesi Mikozu (Guttural Pouch Mycosis – Aspergillus fumigatus)",
            "ayirici_tani": "Hava Kesesi Empiyemi (kanama olmaz, irinli akıntı ve kondroitler vardır), Pulmoner Hemoraji (EIPH - egzersiz sonrası gelir).",
            "tedavi_protokolu": "Cerrahi Girişim (Arteria carotis interna'nın balon kateter veya ligasyon ile oklüzyonu - Masif kanamayı önlemek için Altın Standart), Sistemik/Lokal Antimikotik (Vorikonazol / İtrakonazol), Nazogastrik tüp ile besleme.",
            "sakincali_ilaclar": "⚠️ Hava kesesi içine kateterle yüksek basınçlı yıkama yapmak KONTRENDİKEDİR! (Eroze olmuş arter duvarını patlatarak saniyeler içinde masif fatal kanamaya yol açar)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "saman", "yulaf"],
                "content": "Kuru ot, saman ve yulaf verilmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "tavla", "ahır", "toz"],
                "content": "Nemli ve küflü samanların bulunduğu kapalı tavlada barındırılmaktadır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "öykü"],
                "content": "Geçmişinde travma öyküsü yoktur."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketim Durumu",
                "keywords": ["iştah", "yem yeme", "yeme", "anoreksi", "hiporeksi", "disfaji", "yutma"],
                "content": "Disfaji (Yutma Felci). N. glossopharyngeus ve N. vagus felci nedeniyle samanı çiğnese de yutamamakta, içtiği su ve lokmalar burnundan geri çıkmaktadır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "epistaksis", "kanama", "hava kesesi", "disfaji"],
                "content": "Vücut Sıcaklığı: 38.2 °C (NORMAL) | Kalp Frekansı: 68 atım/dk | Solunum Frekansı: 22 nefes/dk | Burun: Spontan, fışkırır tarzda taze kırmızı epizodik burun kanaması (Epistaksis) | Yutma felci (Disfaji) ve Horner sendromu belirtileri."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "eritrosit", "pcv", "anemi"],
                "content": "Eritrosit (RBC): 4.2 x10⁶/µL (Kan kaybına bağlı Anemi) | PCV: %22 | Lökosit (WBC): 11.2 x10³/µL | Fibrinojen: 420 mg/dL."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp"],
                "content": "Biyokimya parametreleri normal sınırlar içerisindedir."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "ürin", "dansite", "ph idrar"],
                "content": "İdrar Renk: Berrak sarı | Dansite: 1.030 | pH: 8.0 | Protein: Negatif | Sediment: Temiz."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Endoskopi & Mantar Teşhisi",
                "keywords": ["ultrason", "endoskopi", "hava kesesi", "mantar", "arter", "aspergillus"],
                "content": "Endoskopik Muayene: Hava kesesi lümeninde tavan bölgesinde siyah-yeşilimsi Aspergillus fumigatus mantar plakları, Arteria carotis interna üzerinde erozyon ve pıhtı odağı."
            }
        }
    },
    "Vaka L (Poyraz)": {
        "kod": "VAKA_L",
        "sikayet": "Hocam, atımız Poyraz 1 ay önce Gurm hastalığı geçirmişti. Şimdi kulak altı ve boğaz bölgesi sıcak ve ağrılı bir şekilde şişti. Burnundan koyu sarı irin akıyor...",
        "egitmen_paneli": {
            "kesin_tani": "Hava Kesesi Empiyemi (Guttural Pouch Empyema) ve Kondroit (Chondroid) Birikimi",
            "ayirici_tani": "Hava Kesesi Mikozu (kanama yoktur, irin taşları vardır), Hava Kesesi Timpanisi (taylarda görülür, içi havadır).",
            "tedavi_protokolu": "Endoskopik basket kateter ile kondroitlerin (irin taşlarının) çıkarılması veya Cerrahi Drenaj (Viborg üçgeninden), Hava kesesi irrigasyonu (Ilık izotonik + Penisilin), Sistemik Procaine Penicillin G.",
            "sakincali_ilaclar": "⚠️ Kondroitler (taşlaşmış irinler) çıkarılmadan sadece antibiyotik vermek KONTRENDİKEDİR! (Taşlar odağı koruduğu için iyileşme sağlanamaz)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor"],
                "content": "At rasyonu ile beslenmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "gurm", "hara"],
                "content": "Harada barındırılmaktadır. 1 ay önce sürüde Gurm salgını yaşanmıştır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "gurm", "streptococcus"],
                "content": "1 ay önce Streptococcus equi subsp. equi kaynaklı Gurm hastalığı geçirmiştir."
            },
            "ISTAH_DURUMU": {
                "name": "İştah & Yem Tüketim Durumu",
                "keywords": ["iştah", "yem yeme", "yeme", "anoreksi", "hiporeksi", "ağrı"],
                "content": "Hiporeksi (İştah azalması). Parotis bölgesindeki şişlik ve ağrı nedeniyle çiğneme yaparken zorlanmaktadır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "göz", "parotis", "irin", "akıntı", "kondroit", "hava kesesi"],
                "content": "Vücut Sıcaklığı: 39.2 °C | Kalp Frekansı: 72 atım/dk | Solunum Frekansı: 26 nefes/dk | Parotis bölgesinde bilateral sıcak, ağrılı şişlik | Çift taraflı koyu sarı pürülan burun akıntısı | Başı öne uzatarak durma duruşu."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen"],
                "content": "Eritrosit: 6.8 x10⁶/µL | PCV: %34 | Lökosit (WBC): 21.4 x10³/µL (Şiddetli Nötrofilik Lökositoz) | Fibrinojen: 780 mg/dL."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp"],
                "content": "Serum biyokimyası normal sınırlardadır."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "ürin", "dansite", "ph idrar"],
                "content": "İdrar tahlili tamamen normaldir."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Endoskopi & Radyografi (Kondroitler)",
                "keywords": ["ultrason", "endoskopi", "radyografi", "hava kesesi", "kondroit", "taş", "irin"],
                "content": "Radyografi & Endoskopi: Hava kesesi lümeninde taşlaşmış yumurta benzeri çok sayıda irin taşları (Chondroids) ve pürülan sıvı birikimi."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnezi & Bulgu Sorgulama Konsolu (Serbest Metin Sorgulama)</h3>", unsafe_allow_html=True)

# Sidebar - Instructor Portal (Eğitmen Konsolu)
with st.sidebar:
    st.markdown("### 🏛️ ÇU Veteriner Fakültesi")
    st.markdown("**VET401 İç Hastalıkları I**")
    st.markdown("---")
    st.markdown("### 🔒 Eğitmen Portalı (Hoca Paneli)")
    teacher_login = st.checkbox("Eğitmen Erişimi / Cevap Anahtarı", key="teacher_toggle")
    
    if teacher_login:
        pass_code = st.text_input("Giriş Şifresi:", type="password", key="teacher_pass_key")
        if pass_code == "vet401":
            st.success("✅ Eğitmen Erişimi Onaylandı!")
            st.markdown("---")
            st.markdown("#### 🔓 Hoca Hızlı Aksiyonları:")
            if st.button("🔓 Tüm İpuçlarını Sınıf İçin Ekranda Aç", use_container_width=True):
                st.session_state.open_all_trigger = True
                st.rerun()
        elif pass_code:
            st.error("❌ Hatalı Şifre!")

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde hazır butonlar <u>yoktur</u>. 
        Kafanızdaki klinik şüpheye göre ne öğrenmek istiyorsanız kutucuğa <b>kendi cümlenizle veya kelimelerinizle</b> yazınız 
        (Örn: <i>"Hayvan ne ile besleniyor?"</i>, <i>"Ateşi kaç derece?"</i>, <i>"İştahı nasıl?"</i>, <i>"İdrar tahlili sonucu nedir?"</i>, <i>"Hemogram ve kan gazı istiyorum"</i>, <i>"Deri kazıntısı yapalım..."</i>).
    </div>
""", unsafe_allow_html=True)

# Select Case
selected_case_name = st.selectbox(
    "🔍 İncelemek İstediğiniz Vakayı Seçiniz:",
    options=list(CASES.keys()),
    index=0
)

active_case = CASES[selected_case_name]

# Session State Initialization
if "last_case" not in st.session_state:
    st.session_state.last_case = selected_case_name

if st.session_state.last_case != selected_case_name:
    st.session_state.history = []
    st.session_state.last_case = selected_case_name

if "history" not in st.session_state:
    st.session_state.history = []

# Handle "Open All" Trigger from Teacher Portal
if st.session_state.get("open_all_trigger", False):
    st.session_state.history = []
    for c_key, c_val in active_case["categories"].items():
        item_dict = {
            "cat_key": c_key,
            "query": "Eğitmen Konsolu Otomatik Açma",
            "title": c_val["name"],
            "content": c_val["content"]
        }
        if "gorsel" in c_val:
            item_dict["gorsel"] = c_val["gorsel"]
        st.session_state.history.append(item_dict)
    st.session_state.open_all_trigger = False

st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — İlk Başvuru Şikayeti</div>", unsafe_allow_html=True)
st.info(f"**Hastanın Başvuru Şikayeti (Yetiştirici Anamnezi):** {active_case['sikayet']}")

# DISPLAY INSTRUCTOR PORTAL CONTENT IF LOGGED IN
if st.session_state.get("teacher_toggle", False) and st.session_state.get("teacher_pass_key", "") == "vet401":
    st.markdown("<div class='teacher-box'>", unsafe_allow_html=True)
    st.markdown(f"### 🔑 EĞİTMEN CEVAP ANAHTARI — {selected_case_name}")
    eg = active_case.get("egitmen_paneli", {})
    st.markdown(f"🎯 **Kesin Tanı:** `{eg.get('kesin_tani', 'Belirtilmedi')}`")
    st.markdown(f"⚖️ **Ayırıcı Tanı Kriterleri:** {eg.get('ayirici_tani', 'Belirtilmedi')}")
    st.markdown(f"💊 **Rasyonel Tedavi Protokolü:** {eg.get('tedavi_protokolu', 'Belirtilmedi')}")
    st.markdown(f"⚠️ **Sakıncalı / Kontrendike İlaçlar:** {eg.get('sakincali_ilaclar', 'Belirtilmedi')}")
    st.markdown("</div>", unsafe_allow_html=True)

# AUTOMATIC DISPLAY OF MACROSCOPIC CLINICAL IMAGES UPON CASE SELECTION
if "makroskopik_gorsel" in active_case:
    mg = active_case["makroskopik_gorsel"]
    st.markdown("### 📸 Klinik Makroskopik Lezyon Görseli")
    st.caption(f"**{mg['fig']} — {mg['title']}**")
    st.write(mg["desc"])
    
    img_path = find_gorsel_path(mg["file"])
    if img_path:
        st.image(img_path, caption=f"{mg['fig']} - {mg['title']}", use_container_width=True)
    else:
        uploaded_img = st.file_uploader(
            f"📷 {mg['fig']} Görselini Yükleyiniz (.jpg / .png):",
            type=["jpg", "jpeg", "png"],
            key=f"up_macro_{active_case['kod']}"
        )
        if uploaded_img is not None:
            st.image(uploaded_img, caption=f"Yüklenen Klinik Görsel: {mg['fig']}", use_container_width=True)

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
        placeholder="Örn: İştah durumu nasıl?, İdrar tahlili sonucu nedir?, Ateşi kaç?, Deri kazıntısı yapalım..."
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
        
        # MICROSCOPIC IMAGES DISPLAYED ONLY AFTER BEING QUERY-TRIGGERED
        if "gorsel" in item:
            g = item["gorsel"]
            st.markdown(f"#### 🔬 {g['title']} ({g['fig']})")
            st.write(g["desc"])
            
            micro_path = find_gorsel_path(g["file"])
            if micro_path:
                st.image(micro_path, caption=f"{g['fig']} - {g['title']}", use_container_width=True)
            else:
                up_micro = st.file_uploader(
                    f"📷 {g['fig']} Mikroskopik Görselini Yükleyiniz (.jpg / .png):",
                    type=["jpg", "jpeg", "png"],
                    key=f"up_micro_{item['cat_key']}"
                )
                if up_micro is not None:
                    st.image(up_micro, caption=f"Yüklenen Mikroskopik Görsel: {g['fig']}", use_container_width=True)
else:
    st.info("Henüz bu vaka için soru sormadınız. Yukarıdaki arama kutusuna merak ettiğiniz soruyu yazarak muayeneye başlayınız.")

