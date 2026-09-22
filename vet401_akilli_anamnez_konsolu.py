import streamlit as st
import re
import os
import json

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
        margin-bottom: 6px;
    }
    .card-content {
        color: #262626;
        font-size: 14px;
        line-height: 1.5;
    }
    .teacher-box {
        background-color: #FFF2CC;
        border: 2px solid #D6B656;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Helper to find image path robustly
def find_gorsel_path(rel_path):
    if not rel_path:
        return None
    filename = os.path.basename(rel_path)
    possible_paths = [
        rel_path,
        os.path.join("gorseller", filename),
        os.path.join(os.path.dirname(__file__), "gorseller", filename),
        os.path.join(os.path.dirname(__file__), filename),
        filename
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return None

# Load JSON cases database
@st.cache_data
def load_cases_db():
    json_candidates = [
        os.path.join(os.path.dirname(__file__), "vaka_veritabani.json"),
        "vaka_veritabani.json",
        "/workspace/artifacts/vaka_veritabani.json"
    ]
    for j_path in json_candidates:
        if os.path.exists(j_path):
            try:
                with open(j_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                pass
    return {}

CASES = load_cases_db()

# Query Matching Engine
def match_query(query, categories):
    q = query.lower().strip()
    if not q:
        return []
    
    # Strict exclusion: "mikroskop" query MUST ONLY match MIKROSKOPI_KAZINTI / GORUNTULEME_MIKROBIYOLOJI
    micro_keywords = ["mikroskop", "mikroskopi", "mikroskopik", "kazıntı", "kazinti", "lam", "artrospor", "akar", "uyuz"]
    if any(mk in q for mk in micro_keywords):
        matched = []
        for cat_key, cat_data in categories.items():
            if cat_key in ["MIKROSKOPI_KAZINTI", "GORUNTULEME_MIKROBIYOLOJI"]:
                matched.append((cat_key, cat_data))
        return matched

    # Normal keyword search
    matched = []
    for cat_key, cat_data in categories.items():
        name_match = cat_data["name"].lower() in q or q in cat_data["name"].lower()
        keyword_match = any(kw.lower() in q or q in kw.lower() for kw in cat_data.get("keywords", []))
        
        # Don't match biochemistry if asking for micro
        if cat_key == "BIYOKIMYA_PANELI" and any(mk in q for mk in micro_keywords):
            continue
            
        if name_match or keyword_match:
            matched.append((cat_key, cat_data))
            
    return matched

# Header UI
st.markdown("<h1 class='main-title'>ÇUKUROVA ÜNİVERSİTESİ VETERİNER FAKÜLTESİ</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>VET401 İç Hastalıkları I — Akıllı Anamnez & Klinik Bulgu Sorgu Konsolu</h3>", unsafe_allow_html=True)

# Sidebar - Case Selection & Instructor Portal
st.sidebar.header("📋 Vaka Seçim Paneli")
selected_vaka_name = st.sidebar.selectbox("Lütfen Bir Vaka Seçiniz:", list(CASES.keys()) if CASES else ["Vaka Bulunamadı"])

st.sidebar.markdown("---")
st.sidebar.header("🔒 Eğitmen Portalı")
teacher_pass = st.sidebar.text_input("Eğitmen Şifresi:", type="password")
is_teacher = (teacher_pass == "vet401")

if is_teacher:
    st.sidebar.success("🔓 Eğitmen Girişi Doğrulandı!")
    open_all_class = st.sidebar.button("🔓 Tüm Tahlilleri Sınıf Ekranda Aç")
else:
    open_all_class = False

# Main Area
if selected_vaka_name in CASES:
    vaka = CASES[selected_vaka_name]
    
    # Vaka Header
    st.markdown(f"<div class='vaka-header'>📍 {selected_vaka_name} — İlk Başvuru Şikayeti</div>", unsafe_allow_html=True)
    st.info(f"**Yetiştirici Anamnezi / Hasta Şikayeti:** {vaka.get('sikayet', 'Şikayet bilgisi girilmemiştir.')}")
    
    # Show Makroskopik Image if present
    if "makroskopik_gorsel" in vaka:
        g = vaka["makroskopik_gorsel"]
        img_p = find_gorsel_path(g.get("file"))
        if img_p:
            st.image(img_p, caption=f"📷 {g.get('title', '')} ({g.get('fig', '')})", use_container_width=True)
        
        # Upload option for instructor/student if image file missing
        if not img_p and is_teacher:
            up_file = st.file_uploader(f"📷 {g.get('fig')} Makroskopik Görseli Yükle (.jpg/.png):", type=["jpg", "png", "jpeg"], key=f"up_makro_{selected_vaka_name}")
            if up_file:
                st.image(up_file, caption=f"Yüklenen Görsel: {g.get('fig')}", use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Klinik Sorgulama ve Tahlil Arama")
    st.caption("Öğrenci Arama İpucu: 'vital', 'ateş', 'oskültasyon', 'ağrı', 'hemogram', 'biyokimya', 'enzim', 'kan gazı', 'idrar', 'mikroskop' vb. yazarak sorgulama yapabilirsiniz.")
    
    search_q = st.text_input("Aramak istediğiniz muayene / tahlil parametresini giriniz:", placeholder="Örn: biyokimya, hemogram, vital, mikroskop...")
    
    # Check if open all pressed or matches found
    cats = vaka.get("categories", {})
    
    if open_all_class:
        st.markdown("### 🔓 EĞİTMEN YETKİSİ: Tüm Laboratuvar ve Klinik Bulgular Açılmıştır")
        for c_key, c_data in cats.items():
            st.markdown(f"""
            <div class='card-found'>
                <div class='card-title'>📌 {c_data['name']}</div>
                <div class='card-content'>{c_data['content']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # If there is a micro image inside category
            if "gorsel" in c_data:
                mg = c_data["gorsel"]
                m_img_p = find_gorsel_path(mg.get("file"))
                if m_img_p:
                    st.image(m_img_p, caption=f"📷 {mg.get('title', '')} ({mg.get('fig', '')})", use_container_width=True)
    elif search_q:
        matches = match_query(search_q, cats)
        if matches:
            st.success(f"🔍 '{search_q}' araması için {len(matches)} kategoride klinik bulgu tespit edildi:")
            for c_key, c_data in matches:
                
                # SPECIAL RULE FOR DERMA / MICROSCOPY:
                # If image exists, hide text content and display ONLY the image.
                has_micro_img = False
                if "gorsel" in c_data:
                    mg = c_data["gorsel"]
                    m_img_p = find_gorsel_path(mg.get("file"))
                    if m_img_p:
                        has_micro_img = True
                        st.markdown(f"<div class='card-title'>📷 {c_data['name']} (Mikroskopik Görsel)</div>", unsafe_allow_html=True)
                        st.image(m_img_p, caption=f"📷 {mg.get('title', '')} ({mg.get('fig', '')})", use_container_width=True)
                
                # If no image found or not a micro category with image, display text content
                if not has_micro_img:
                    st.markdown(f"""
                    <div class='card-found'>
                        <div class='card-title'>📌 {c_data['name']}</div>
                        <div class='card-content'>{c_data['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # File uploader if image missing in micro category
                    if "gorsel" in c_data and not find_gorsel_path(c_data["gorsel"].get("file")):
                        up_m = st.file_uploader(f"📷 {c_data['gorsel'].get('fig')} Mikroskopik Görseli Yükleyiniz:", type=["jpg", "png", "jpeg"], key=f"up_m_{c_key}_{selected_vaka_name}")
                        if up_m:
                            st.image(up_m, caption="Yüklenen Mikroskopik Görsel", use_container_width=True)
        else:
            st.warning(f"⚠️ '{search_q}' sorgusu için bu vakaya ait bir klinik bulgu veya tahlil bulunamadı. Lütfen terimi kontrol ediniz.")

    # Instructor Panel (At Bottom)
    if is_teacher and "egitmen_bilgisi" in vaka:
        st.markdown("<div class='teacher-box'>", unsafe_allow_html=True)
        st.markdown("### 🎓 Eğitmen Teşhis & Ayırıcı Tanı Kılavuzu")
        eb = vaka["egitmen_bilgisi"]
        st.markdown(f"**🎯 Kesin Tanı:** {eb.get('kesin_tani', '')}")
        st.markdown(f"**⚖️ Ayırıcı Tanı Kriterleri:** {eb.get('ayirici_tani', '')}")
        st.markdown(f"**💊 Tedavi & Sağaltım Protokolü:** {eb.get('tedavi_protokolu', '')}")
        st.markdown("</div>", unsafe_allow_html=True)
