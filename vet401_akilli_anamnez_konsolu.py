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

# Smart Image Resolution Function (Linux / Case-Insensitive / Format Agnostic)
def find_gorsel_path(base_file_path):
    if not base_file_path:
        return None
    clean_name = os.path.basename(base_file_path)
    clean_stem = os.path.splitext(clean_name)[0].lower()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_dirs = [
        os.path.join(script_dir, "gorseller"),
        os.path.join(os.getcwd(), "gorseller"),
        script_dir,
        os.getcwd()
    ]
    
    extensions = [".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG"]
    
    for s_dir in search_dirs:
        if not os.path.exists(s_dir):
            continue
        # 1. Direct extension match
        for ext in extensions:
            candidate = os.path.join(s_dir, f"{clean_stem}{ext}")
            if os.path.isfile(candidate):
                return candidate
        # 2. Case-insensitive / stem match scan
        try:
            for item in os.listdir(s_dir):
                item_stem = os.path.splitext(item)[0].lower()
                clean_stem_no_underscore = clean_stem.replace("_", "").replace("-", "")
                item_stem_no_underscore = item_stem.replace("_", "").replace("-", "")
                if item_stem == clean_stem or item_stem_no_underscore == clean_stem_no_underscore:
                    return os.path.join(s_dir, item)
        except Exception:
            pass
    return None

# Cases Knowledge Base
CASES = {
    "Vaka A (Papatya)": {
        "kod": "VAKA_A",
        "sikayet": "Gerdan ve çene altında soğuk ödem, iştahsızlık, belirgin süt verimi düşüşü ve durgunluk.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "karbonhidrat", "mısır", "arpa", "ot", "mera", "silaj", "balya", "saman", "kaba", "tel", "çivi", "yabancı"],
                "content": "İşletmede entansif kaba/yoğun yem karma rasyonu uygulanmaktadır. Balya parçalama esnasında kaba yeme inşaat tellerinin ve çivilerin karışmış olabileceği belirtilmektedir."
            },
            "ISTAH_DURUMU": {
                "name": "İştah ve Yem Tüketimi Durumu",
                "keywords": ["iştah", "yem yiyor mu", "anoreksi", "iştahsızlık", "yem tüketimi"],
                "content": "Ağır iştahsızlık (Anoreksi) mevcuttur. Hayvan önüne konulan kesif ve kaba yeme dokunmamaktadır."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "coğrafya", "yükseklik"],
                "content": "Hayvan Ceyhan ovasındaki (rakım ~50 metre) sabit tesiste doğup büyümüştür. Yüksek rakım nakli yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "mastitis", "öykü"],
                "content": "Geçmişinde kaydedilmiş kronik hastalık öyküsü yoktur. 2 ay önce sorunsuz doğum yapmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "nefes", "mukoza", "crt", "dehidrasyon", "ödem"],
                "content": "Vücut Sıcaklığı: 39.8 °C | Kalp Frekansı: 102 atım/dk | Solunum Frekansı: 42 nefes/dk | Mukoza: Soluk pembe | CRT: 2.5 sn | Dehidrasyon: %6 | Gerdan ve submandibuler ödem +, Vena jugularis stazı +."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "şılpırtı", "splashing", "muffled", "boğuk", "rall"],
                "content": "Kalp Oskültasyonu: Su çalkantı / şılpırtı (splashing) ve boğuk kalp sesleri. Akciğer Oskültasyonu: Ventro-lateral alanlarda solunum sesleri azalmış."
            },
            "AGRI_TESTLERI": {
                "name": "Retikulum Ağrı Testleri",
                "keywords": ["sopa", "kama", "withers", "ağrı", "pinch", "retikulum"],
                "content": "Sopa, kama ve Withers pinch retikulum ağrı testlerinin tamamı POZİTİF (+)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "kan sayım", "fibrinojen", "rbc", "pcv", "pp/f"],
                "content": "Eritrosit (RBC): 5.1 x10⁶/µL | Lökosit (WBC): 18.2 x10³/µL (Rejeneratif Sola Kayma) | Fibrinojen: 1250 mg/dL (Aşırı Yüksek) | PP/F Oranı: 6.3 (Suppüratif Yangı)."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "ck", "ldh", "üre", "bun", "kreatinin", "troponin"],
                "content": "AST: 185 U/L | GGT: 42 U/L | BUN: 32 mg/dL | Kardiyak Troponin I: 2.8 ng/mL (Yüksek - Miyokard Hasarı)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "ph", "po2", "pco2", "bikarbonat", "hco3", "laktat"],
                "content": "Kan pH: 7.28 | pO₂: 36 mmHg | pCO₂: 48 mmHg | HCO₃⁻: 17.2 mmol/L | Laktat: 3.8 mmol/L."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "glikozüri", "mikrohematüri", "sediment"],
                "content": "Spesifik Gravite: 1.022 | pH: 7.5 | Proteinüri: (+) Hafif | Glikoz: Negatif | Lökosit/Eritrosit: Nadir lökosit izlendi."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Görüntüleme & Perikardiyosentez",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "perikard"],
                "content": "USG: Perikardiyal kesede 4 cm kalınlığında fibrinli pürülan sıvı birikimi. Perikardiyosentez: Kötü kokulu kirli sarı-yeşil pürülan sıvı. Kültür: Trueperella pyogenes ve anaerob üreme."
            }
        }
    },
    "Vaka B (Yonca)": {
        "kod": "VAKA_B",
        "sikayet": "Düzensiz tekrarlayan yüksek ateş, zayıflama, çabuk yorulma ve süt veriminde kronik düşüş.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "ne yiyor", "mısır", "arpa", "ot", "mera", "silaj"],
                "content": "Standart süt rasyonu verilmektedir. Yem kalitesinde bozukluk veya yabancı cisim öyküsü bulunmamaktadır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu",
                "keywords": ["iştah", "yem yiyor mu", "hiporeksi"],
                "content": "İştah dalgalıdır (Hiporeksi). Ateş yükseldiğinde yem yemeyi tamamen kesmekte, ateş düştüğünde az miktarda kaba yem tüketmektedir."
            },
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil"],
                "content": "Ceyhan ovası işletmesidir. Nakil öyküsü yoktur."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "önceden", "hastalık", "metritis", "rahim", "mastitis", "meme"],
                "content": "3 ay önce doğum sonrası kronik purulent metritis (rahim iltihabı) tedavisi görmüştür."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "kalp frekans", "solunum", "mukoza", "crt", "peteşi"],
                "content": "Vücut Sıcaklığı: 40.2 °C (Tekrarlayan Ateş) | Kalp Frekansı: 110 atım/dk | Solunum Frekansı: 38 nefes/dk | Mukoza: Soluk ve konjonktivada peteşiyel kanamalar | CRT: 3.0 sn."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp & Akciğer Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "dinleme", "üfürüm", "systolic", "murmur", "endokardit"],
                "content": "Kalp Oskültasyonu: Sol sistolik odakta (mitral/triküspid kapak) holosistolik yumuşak üfürüm (systolic murmur). Akciğer sesleri normal."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram (CBC) Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "fibrinojen", "rbc", "anemi"],
                "content": "Eritrosit (RBC): 3.8 x10⁶/µL (Non-rejeneratif Anemi) | Lökosit (WBC): 24.5 x10³/µL (Şiddetli Lökositoz) | Fibrinojen: 980 mg/dL."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Enzimler",
                "keywords": ["biyokimya", "ast", "ggt", "bun", "kreatinin", "globülin", "troponin"],
                "content": "Globülin: 5.8 g/dL (Hipergamaglobulinemi) | AST: 110 U/L | Troponin I: 1.6 ng/mL."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili (Urinalysis)",
                "keywords": ["idrar", "dansite", "proteinüri", "mikrohematüri"],
                "content": "Spesifik Gravite: 1.018 | Mikrohematüri: (++) Pozitif | Proteinüri: (++) Orta derece protein varlığı."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Ekokardiyografi & Kan Kültürü",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "kültür", "vejetasyon", "kapak"],
                "content": "Ekokardiyografi: Triküspid ve mitral kapak yaprakçıklarında 1.5 cm çapında karnabahar karnı görünümünde hiperekojen vejetasyon kitleleri. Kan Kültürü: Trueperella pyogenes ve Streptococcus bovis pozitif."
            }
        }
    },
    "Vaka C (Zümrüt)": {
        "kod": "VAKA_C",
        "sikayet": "Gerdan ödemi, morarmış mukoza (siyanoz), nefes darlığı ve kıl örtüsünde matlaşma.",
        "categories": {
            "LOKASYON_RAKIM": {
                "name": "Lokasyon & Coğrafi Öykü",
                "keywords": ["rakım", "yayla", "nereden", "nereli", "yer", "sevk", "nakil", "kamyon", "dağ", "yükseklik"],
                "content": "Hayvan 2 hafta önce Pozantı Toros Dağları yüksek rakımlı yayla merasından (~2100 metre) nakledilerek gelmiştir."
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu",
                "keywords": ["iştah", "yem yiyor mu"],
                "content": "Egzersiz ve solunum güçlüğüne bağlı iştahsızlık mevcuttur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "derece", "nabız", "solunum", "mukoza", "siyanoz", "ödem"],
                "content": "Vücut Sıcaklığı: 38.6 °C (NORMAL) | Kalp Frekansı: 96 atım/dk | Solunum: 46 nefes/dk | Mukozalar: Siyanotik (Morarma) | Gerdan ödemi +, Jugular dolgunluk +."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Kalp Oskültasyonu",
                "keywords": ["kalp ses", "oskültasyon", "üfürüm"],
                "content": "Kalp Oskültasyonu: Hiperdinamik güçlü kalp sesleri. Üfürüm veya su çalkantı sesi YOKTUR."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram Tahlili",
                "keywords": ["hemogram", "wbc", "rbc", "pcv", "hematokrit", "polisitemi"],
                "content": "RBC: 10.8 x10⁶/µL | PCV: %54 (Aşırı Yüksek - Sekonder Polisitemi) | WBC: 7.2 x10³/µL (NORMAL) | Fibrinojen: 320 mg/dL (NORMAL)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "po2", "pco2", "hipoksi"],
                "content": "Kan pH: 7.36 | pO₂: 48 mmHg (Ağır Doku Hipoksisi) | pCO₂: 42 mmHg."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili",
                "keywords": ["idrar", "dansite", "proteinüri"],
                "content": "Spesifik Gravite: 1.025 | pH: 8.0 | Protein/Glikoz: Negatif."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Ekokardiyografi",
                "keywords": ["ultrason", "usg", "ekokardiyografi", "sağ ventrikül"],
                "content": "Ekokardiyografi: Sağ ventrikül serbest duvarında belirgin kalınlaşma (Sağ Ventrikül Hipertrofisi). Kültür: Steril (Üreme yok)."
            }
        }
    },
    "Vaka D (Yiğit)": {
        "kod": "VAKA_D",
        "sikayet": "Ağız ve burundan fışkırır tarzda taze parlak kırmızı kan gelmesi (hemoptizi) ve siyah katran gibi dışkı yapma.",
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon & Yemleme Öyküsü",
                "keywords": ["rasyon", "yem", "besle", "mısır", "arpa", "besi", "nişasta"],
                "content": "Yoğun mısır ve arpa kırması ağırlıklı, kaba yemi yetersiz yüksek nişastalı besi rasyonu verilmektedir."
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu",
                "keywords": ["iştah", "yem yiyor mu"],
                "content": "Kan kaybı ve şoka bağlı olarak iştah tamamen kapanmıştır."
            },
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["geçmiş", "asidoz", "şişkinlik", "timpani", "rumenitis"],
                "content": "Geçmişinde tekrarlayan akut/subakut rumen asidozu (yem çarpması) öyküsü mevcuttur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "hemoptizi", "melena", "anemi"],
                "content": "Vücut Sıcaklığı: 39.2 °C | Kalp Frekansı: 118 atım/dk | Solunum: 52 nefes/dk | Ağız/Burun: Taze kırmızı kan fışkırması (Hemoptizi) | Mukozalar: Bembeyaz (Ağır Anemi) | Dışkı: Siyah katran kıvamında (Melena)."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram Tahlili",
                "keywords": ["hemogram", "wbc", "rbc", "pcv", "anemi"],
                "content": "RBC: 2.1 x10⁶/µL | PCV: %12 (Acil Transfüzyon Eşiği!) | WBC: 21.5 x10³/µL | Fibrinojen: 1050 mg/dL."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili",
                "keywords": ["idrar", "dansite", "mikrohematüri"],
                "content": "Spesifik Gravite: 1.015 | Renk: Soluk sarı | Proteinüri: (+) | Eritrosit: Nadir."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Ultrasonografi",
                "keywords": ["ultrason", "usg", "karaciğer", "apse", "vena cava"],
                "content": "Abdominal USG: Karaciğerde 6 cm apse odağı, Vena Cava Caudalis lümeninde tıkayıcı trombüs ekojenitesi. Torakal USG: Pulmoner arter anevrizması ve rüptür hematomu."
            }
        }
    },
    "Vaka E (Kudret)": {
        "kod": "VAKA_E",
        "sikayet": "Baş, göz çevresi ve boyunda dairesel, kepekli, gri-beyaz kireçimsi kabuklu döküntüler ve tüy kaybı.",
        "makroskopik_gorsel": {
            "fig": "Figure 1.2-1",
            "title": "Klinik Mantar Lezyonu (Baş ve Göz Çevresi)",
            "file": "figure_1_2_1",
            "desc": "Göz çevresi ve yüzde dairesel, grimsi-beyaz kireç benzeri kabarık kabuklanma ve alopezi (tüy kaybı)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Rasyon ve Barınak Şartları",
                "keywords": ["barınak", "nem", "ışık", "güneş", "kalabalık", "rasyon", "besleme"],
                "content": "Karanlık, nemli ve havalandırması yetersiz kapalı buzağı bölmesinde barındırılmaktadır. Güneş ışığı almamaktadır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu",
                "keywords": ["iştah", "yem yiyor mu"],
                "content": "Genel iştah ve canlılık normaldir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "kaşıntı", "lezyon", "deri"],
                "content": "Vücut Sıcaklığı: 38.8 °C (NORMAL) | Kalp: 82 atım/dk | Solunum: 24 nefes/dk | Kaşıntı: YOK veya çok hafif. Deride dairesel kireçimsi kabuklar."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "Deri Kazıntısı & Mikroskopik Mantar Teşhisi",
                "keywords": ["mikroskop", "kazıntı", "deri kazıntısı", "koh", "mantar", "artrospor", "lam"],
                "gorsel": {
                    "fig": "Figure 1.2-11",
                    "title": "Mikroskopik Mantar Sporu (%10 KOH Hazırlığı)",
                    "file": "figure_1_2_11",
                    "desc": "%10 KOH ile muamele edilmiş deri kazıntısında kıl şaftını saran küresel Trichophyton verrucosum ektotriks artrospor dizilimi (40x)."
                },
                "content": "%10 KOH ile hazırlanan deri kazıntısında kıl etrafında ektotriks artrospor zincirleri belirgin olarak izlenmiştir."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram Tahlili",
                "keywords": ["hemogram", "wbc", "rbc"],
                "content": "Tüm kan parametreleri fizyolojik sınırlar içerisindedir."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili",
                "keywords": ["idrar"],
                "content": "İdrar bulguları tamamen normaldir."
            }
        }
    },
    "Vaka F (Nazar)": {
        "kod": "VAKA_F",
        "sikayet": "Şiddetli kaşıntı, deride kalınlaşma (likenifikasyon), kıvrımlaşma, sırt ve boyunda döküntü ve kabuklanma.",
        "makroskopik_gorsel": {
            "fig": "Figure 1.3-13 & 1.3-15",
            "title": "Klinik Uyuz Lezyonu (Deride Kalınlaşma ve Likenifikasyon)",
            "file": "figure_1_3_13",
            "desc": "Kulak kepçesi, boyun ve sırtta derinin fil derisi gibi kalınlaşması (likenifikasyon), kaşıntı eksforyasyonları ve kepekli döküntü."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Barınak Şartları",
                "keywords": ["barınak", "sürü", "temas", "uyuz"],
                "content": "Sürüye yeni katılan hayvanlardan sonra kaşıntının diğer ineklere de yayıldığı ifade edilmiştir."
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu",
                "keywords": ["iştah", "yem yiyor mu"],
                "content": "Şiddetli kaşıntı ve huzursuzluk nedeniyle yem tüketimi %30 azalmıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "kaşıntı", "deri", "likenifikasyon"],
                "content": "Vücut Sıcaklığı: 38.9 °C | Kalp: 88 atım/dk | Kaşıntı: AŞIRI ŞİDDETLİ. Deri kıvrımlaşmış, kalınlaşmış ve sertleşmiştir."
            },
            "MIKROSKOPI_KAZINTI": {
                "name": "Derin Deri Kazıntısı & Akar Mikroskopisi",
                "keywords": ["mikroskop", "kazıntı", "deri kazıntısı", "akar", "uyuz", "mineral yağ", "sarcoptes"],
                "gorsel": {
                    "fig": "Figure 1.3-18",
                    "title": "Mikroskopik Sarcoptes Scabiei Akari",
                    "file": "figure_1_3_18",
                    "desc": "Derin deri kazıntısında mineral yağ altında tespit edilen canlı ergin Sarcoptes scabiei akarı (10x-40x)."
                },
                "content": "Kapiller kanama görülünceye kadar alınan derin deri kazıntısında canlı Sarcoptes scabiei ergin akarları ve oval yumurtaları tespit edilmiştir."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram Tahlili",
                "keywords": ["hemogram", "wbc", "eozinofil"],
                "content": "Eozinofil oranı %14 (Eozinofili - Paraziter/Alerjik Yanıt). Diğer değerler normaldir."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili",
                "keywords": ["idrar"],
                "content": "İdrar tahlili normaldir."
            }
        }
    },
    "Vaka G (Çiçek)": {
        "kod": "VAKA_G",
        "sikayet": "Mera dönüşü sadece pigmentsiz (beyaz) deri bölgelerinde şiddetli kızarıklık, soyulma, ödem ve nekroz.",
        "makroskopik_gorsel": {
            "fig": "Figure 1.7-35",
            "title": "Hepatojen Fotosensitizasyon (Pigmentsiz Deri Nekrozu)",
            "file": "figure_1_7_35",
            "desc": "Yalnızca beyaz (pigmentsiz) deri alanlarında soyulma, hamur ödemi ve nekroz; siyah pigmentli derinin tamamen sağlam kalması."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Mera & Otlatma Öyküsü",
                "keywords": ["mera", "ot", "klorofil", "güneş", "bitki", "otlatma"],
                "content": "Bahar ayında taze otlu ve yabani otların (Lantana camara/Mantar toksinleri) bol olduğu merada otlatılmıştır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu",
                "keywords": ["iştah", "yem yiyor mu"],
                "content": "Ağrılı deri soyulmaları ve karaciğer yetmezliğine bağlı iştahsızlık mevcuttur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "sarılık", "ikter", "beyaz deri", "soyulma"],
                "content": "Vücut Sıcaklığı: 39.4 °C | Mukozalar: İkterik (Sarılık +) | Sadece beyaz deri alanlarında eritem, soyulma ve sızıntılı nekroz."
            },
            "BIYOKIMYA": {
                "name": "Serum Biyokimyası & Karaciğer Enzimleri",
                "keywords": ["biyokimya", "ast", "ggt", "alt", "alp", "bilirubin", "karaciğer", "filloeritrin"],
                "content": "GGT: 180 U/L (Aşırı Yüksek - Safra Yolu Hasarı) | AST: 290 U/L | İndirekt Bilirubin: 1.8 mg/dL | Kanda Filloeritrin Düzeyi Yüksek."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili",
                "keywords": ["idrar", "bilirubinüri"],
                "content": "İdrar Rengi: Koyu çay rengi | Bilirubinüri: (+++) Pozitif."
            }
        }
    },
    "Vaka H (Ateş)": {
        "kod": "VAKA_H",
        "sikayet": "Gövde ve boyun derisinde aniden beliren ödemli dairesel kabarık plaklar (ürtiker) ve huzursuzluk.",
        "makroskopik_gorsel": {
            "fig": "Figure 1.5-1",
            "title": "Akut Ürtiker (Ödem Plakları)",
            "file": "figure_1_5_1",
            "desc": "Gövde ve boyun derisinde aniden beliren dairesel ödemli kabarık ürtiker plakları (urtica)."
        },
        "categories": {
            "RASYON_YEM": {
                "name": "Aşı ve İlaç Öyküsü",
                "keywords": ["aşı", "sinek", "böcek", "enjeksiyon", "yem değişimi", "alerji"],
                "content": "2 saat önce yeni bir antibiyotik enjeksiyonu uygulanmış ve mera dönüşü böcek sokmasına maruz kalmıştır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu",
                "keywords": ["iştah", "yem yiyor mu"],
                "content": "Geçici huzursuzluk dışında iştah tam kapanmamıştır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "nabız", "solunum", "ürtiker", "plak", "ödem"],
                "content": "Vücut Sıcaklığı: 39.0 °C | Kalp: 92 atım/dk | Gövde derisinde parmakla basılınca çukurlaşan ödemli kabarık dairesel plaklar."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram Tahlili",
                "keywords": ["hemogram", "wbc", "eozinofil"],
                "content": "Eozinofil: %12 (Alerjik Tip I Aşırı Duyarlılık)."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili",
                "keywords": ["idrar"],
                "content": "İdrar tahlili tamamen normaldir."
            }
        }
    },
    "Vaka I (Fırtına)": {
        "kod": "VAKA_I",
        "sikayet": "Gırtlaktan ıslık/düdük sesi gibi hırıltı (stridor), belirgin nefes darlığı ve gırtlakta şiddetli ağrı/ödem.",
        "categories": {
            "RASYON_YEM": {
                "name": "Yutma ve Beslenme Öyküsü",
                "keywords": ["yem", "yutma", "disfaji", "gırtlak", "su"],
                "content": "Boğazındaki ödem ve ağrı nedeniyle yem yutarken zorlanmakta, lokmaları yere düşürmektedir."
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu",
                "keywords": ["iştah", "disfaji", "yutma"],
                "content": "Ağrılı yutma (Disfaji) nedeniyle yem tüketimi durmuştur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "sıcaklık", "stridor", "larenks", "ödem", "dispne", "trakea"],
                "content": "Vücut Sıcaklığı: 40.1 °C | Kalp: 108 atım/dk | Solunum: 48 nefes/dk (İnspiratorik Dispne) | Larenks palpasyonunda şiddetli ödem ve ağrı reaksiyonu."
            },
            "KALP_AKCIGER_SESLERI": {
                "name": "Akciğer Oskültasyonu",
                "keywords": ["akciğer", "oskültasyon", "ses"],
                "content": "Akciğer Oskültasyonu: Akciğer parankim vesiküler sesleri TAMAMEN NORMALdir. Ses üst solunum yolundan (larenks) kaynaklanmaktadır."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram Tahlili",
                "keywords": ["hemogram", "wbc", "lökosit", "fibrinojen"],
                "content": "WBC: 22.4 x10³/µL | Fibrinojen: 1100 mg/dL (Şiddetli Bakteriyel Yangı)."
            },
            "KAN_GAZI": {
                "name": "Venöz Kan Gazı Analizi",
                "keywords": ["kan gazı", "po2", "pco2"],
                "content": "pO₂: 92 mmHg (Normal) | pCO₂: 44 mmHg (Normal - Akciğer gaz alışverişi sağlam)."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili",
                "keywords": ["idrar"],
                "content": "İdrar bulguları normaldir."
            }
        }
    },
    "Vaka J (Şahin)": {
        "kod": "VAKA_J",
        "sikayet": "Tek taraflı pis kokulu (fetid) pürülan burun akıntısı, sinüs üzerinde vurukta matite ve başı eğik tutma.",
        "categories": {
            "GECMIS_HASTALIK": {
                "name": "Cerrahi & Boynuz Kesimi Öyküsü",
                "keywords": ["boynuz", "kesim", "dehorning", "sinüs", "ameliyat"],
                "content": "1 ay önce hijyenik olmayan şartlarda boynuz kesimi (dehorning) yapılmış ve frontal sinüs boşluğu açılmıştır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu",
                "keywords": ["iştah", "yem yiyor mu"],
                "content": "Baş ağrısı ve sinüs basıncına bağlı hafif iştahsızlık mevcuttur."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Perküsyon Bulguları",
                "keywords": ["ateş", "sinüs", "perküsyon", "matite", "akıntı", "koku"],
                "content": "Vücut Sıcaklığı: 39.3 °C | Sol taraf frontal sinüs üzerine perküsyon yapıldığında MAT SES (Matite) ve şiddetli ağrı. Sol burun deliğinden pis kokulu irin akıntısı."
            },
            "HEMOGRAM": {
                "name": "Tam Hemogram Tahlili",
                "keywords": ["hemogram", "wbc", "fibrinojen"],
                "content": "WBC: 16.8 x10³/µL | Fibrinojen: 780 mg/dL."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili",
                "keywords": ["idrar"],
                "content": "İdrar tahlili normaldir."
            }
        }
    },
    "Vaka K (Rüzgar)": {
        "kod": "VAKA_K",
        "sikayet": "Atın burnundan durduk yere spontan taze kırmızı kan gelmesi (epistaksis) ve yem yutma güçlüğü (disfaji).",
        "categories": {
            "GECMIS_HASTALIK": {
                "name": "Klinik Seyir Öyküsü",
                "keywords": ["kanama", "epistaksis", "at", "yutma", "su"],
                "content": "Son 3 gündür içtiği su ve yem lokmaları burnundan geri gelmekte, dinlenme anında burnundan fışkırır gibi taze kan akmaktadır."
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu",
                "keywords": ["iştah", "disfaji", "yutma"],
                "content": "N. glossopharyngeus ve N. vagus felcine bağlı şiddetli Yutma Güçlüğü (Disfaji) vardır."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "epistaksis", "kan", "mukoza"],
                "content": "Vücut Sıcaklığı: 38.2 °C (NORMAL) | Kalp: 64 atım/dk | Solunum: 22 nefes/dk | Tek taraflı aktif taze burun kanaması (Epistaksis). Mukozalar soluk."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Endoskopi Bulguları",
                "keywords": ["endoskopi", "hava kesesi", "mantar", "arter", "aspergillus"],
                "content": "Endoskopi: Hava kesesi (Guttural pouch) içinde Arteria carotis interna üzerinde siyah-yeşil mikotik plaklar (Aspergillus fumigatus) ve erozyon kanaması."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili",
                "keywords": ["idrar"],
                "content": "İdrar tahlili normaldir."
            }
        }
    },
    "Vaka L (Poyraz)": {
        "kod": "VAKA_L",
        "sikayet": "Geçirilmiş Gurm hastalığı sonrası parotis bölgesinde ağrılı şişlik ve çift taraflı koyu sarı irinli burun akıntısı.",
        "categories": {
            "GECMIS_HASTALIK": {
                "name": "Geçmiş Hastalık Öyküsü",
                "keywords": ["gurm", "streptococcus", "boğaz", "lenf"],
                "content": "1 ay önce boğaz bölgesinde apselerle seyreden Gurm (Streptococcus equi) hastalığı geçirmiştir."
            },
            "ISTAH_DURUMU": {
                "name": "İştah Durumu",
                "keywords": ["iştah", "yem yiyor mu"],
                "content": "Ağrılı baş duruşu ve yutma zorluğu nedeniyle hiporeksiktir."
            },
            "VITAL_BULGULAR": {
                "name": "Genel Muayene & Vital Bulgular",
                "keywords": ["ateş", "parotis", "hava kesesi", "akıntı", "irin"],
                "content": "Vücut Sıcaklığı: 39.1 °C | Parotis ve baş-boyun birleşiminde ağrılı şişlik. Çift taraflı kokuşmuş pürülan burun akıntısı."
            },
            "GORUNTULEME_PONKSIYON": {
                "name": "Endoskopi & Taşlaşmış İrin (Kondroit)",
                "keywords": ["endoskopi", "kondroit", "irin", "empiyem", "taş"],
                "content": "Endoskopi: Hava kesesi lümeninde yoğun pürülan eksudat ve taşlaşmış irin yumakları (Chondroids). Kültür: Streptococcus equi subsp. equi pozitif."
            },
            "IDRAR_TAHLILI": {
                "name": "İdrar Tahlili",
                "keywords": ["idrar"],
                "content": "İdrar tahlili normaldir."
            }
        }
    }
}

# Header UI
st.markdown("<h1 class='main-title'>🐄 VET401 İç Hastalıkları I</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Akıllı Anamnezi & Bulgu Sorgulama Konsolu (Serbest Metin Sorgulama)</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color:#EBF1F5; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:14px; border-left:5px solid #1F4E79;'>
        <b>📌 Öğrenci Talimatı:</b> Bu sistemde hazır butonlar <u>yoktur</u>. 
        Kafanızdaki klinik şüpheye göre ne öğrenmek istiyorsanız kutucuğa <b>kendi cümlenizle veya kelimelerinizle</b> yazınız 
        (Örn: <i>"Hayvan ne ile besleniyor?"</i>, <i>"İştahı nasıl?"</i>, <i>"Kalp sesleri nasıl?"</i>, <i>"Ateşi kaç derece?"</i>, <i>"Hemogram tahlili istiyorum"</i>, <i>"İdrar tahlili sonuçları nedir?"</i>).
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

# AUTOMATIC DISPLAY OF MACROSCOPIC CLINICAL IMAGES UPON CASE SELECTION
if "makroskopik_gorsel" in active_case:
    mg = active_case["makroskopik_gorsel"]
    st.markdown("### 📸 Klinik Makroskopik Lezyon Fotoğrafı")
    
    img_path = find_gorsel_path(mg["file"])
    
    if img_path and os.path.exists(img_path):
        st.image(img_path, caption=f"{mg['fig']} - {mg['title']}", use_column_width=True)
        st.caption(f"ℹ️ **Klinik Görsel Tanımı:** {mg['desc']}")
    else:
        st.warning(f"⚠️ **Klinik Görsel Dosyası Aratılıyor:** `{mg['file']}`\n\nResim `gorseller/` klasöründe bulunamadıysa aşağıdaki butondan doğrudan yükleyebilirsiniz:")
        uploaded_img = st.file_uploader(f"📸 {mg['fig']} için Fotoğraf Yükleyiniz (.jpg / .png):", type=["jpg", "jpeg", "png"], key=f"up_macro_{active_case['kod']}")
        if uploaded_img is not None:
            st.image(uploaded_img, caption=f"Yüklenen Klinik Görsel: {mg['fig']}", use_column_width=True)
            st.caption(f"ℹ️ **Klinik Görsel Tanımı:** {mg['desc']}")

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
        "Sorunuzu Buraya Yazınız (Örn: Rasyon bilgisi nedir?, İştahı nasıl?, Kalp sesleri?, Ateşi kaç?, İdrar tahlili?):",
        key="query_input",
        placeholder="Örn: Hayvan ne yiyor?, İştah durumu?, Ateş kaç?, Hemogram?, İdrar tahlili?..."
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
                item_dict = {
                    "cat_key": cat_key,
                    "query": user_query,
                    "title": cat_data["name"],
                    "content": cat_data["content"]
                }
                if "gorsel" in cat_data:
                    item_dict["gorsel"] = cat_data["gorsel"]
                st.session_state.history[selected_case_name].append(item_dict)
                new_discoveries += 1
        
        if new_discoveries > 0:
            st.success(f"🎉 Teşekkürler! Sorunuzla ilişkili {new_discoveries} yeni klinik bulgu / bilgi açığa çıkarıldı!")
        else:
            st.info("Bu soruyla ilgili bilgi zaten daha önce açığa çıkarılmıştı. Aşağıdaki keşifler listenizden okuyabilirsiniz.")
    else:
        st.warning("⚠️ Girdiğiniz soru veya kelimelerle eşleşen bir bilgi bulunamadı. Lütfen sorunuzu farklı anahtar kelimelerle yazınız.")

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
        
        # MICROSCOPIC IMAGES DISPLAYED ONLY AFTER BEING QUERY-TRIGGERED
        if "gorsel" in item:
            g = item["gorsel"]
            st.markdown(f"#### 🔬 {g['fig']} - {g['title']}")
            
            micro_path = find_gorsel_path(g["file"])
            
            if micro_path and os.path.exists(micro_path):
                st.image(micro_path, caption=f"{g['fig']} - {g['title']}", use_column_width=True)
                st.caption(f"ℹ️ **Mikroskopik Görsel Tanımı:** {g['desc']}")
            else:
                st.warning(f"⚠️ **Mikroskopik Görsel Dosyası Aratılıyor:** `{g['file']}`")
                up_micro = st.file_uploader(f"🔬 {g['fig']} için Mikroskopik Fotoğraf Yükleyiniz (.jpg / .png):", type=["jpg", "jpeg", "png"], key=f"up_micro_{item['cat_key']}")
                if up_micro is not None:
                    st.image(up_micro, caption=f"Yüklenen Mikroskopik Görsel: {g['fig']}", use_column_width=True)
                    st.caption(f"ℹ️ **Mikroskopik Görsel Tanımı:** {g['desc']}")
else:
    st.info("Henüz bu vaka için soru sormadınız. Yukarıdaki arama kutusuna merak ettiğiniz soruyu yazarak muayeneye başlayınız.")
