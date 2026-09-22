import streamlit as st
import json
import os
import re

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu",
    page_icon="🐄",
    layout="wide",
)

# ---------------------------------------------------------
# Custom Styling
# ---------------------------------------------------------
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
    .vaka-box {
        background-color: #EBF1F5;
        border: 2px solid #1F4E79;
        padding: 15px 20px;
        border-radius: 10px;
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

# ---------------------------------------------------------
# Robust Visual Path Finder (Görsel Yolu Bulucu)
# ---------------------------------------------------------
def find_gorsel_path(file_path):
    if not file_path:
        return None
    if os.path.exists(file_path):
        return file_path
    
    filename = os.path.basename(file_path)
    name_without_ext, _ = os.path.splitext(filename)
    
    candidate_paths = [
        filename,
        f"{name_without_ext}.png",
        f"{name_without_ext}.jpg",
        f"{name_without_ext}.jpeg",
        os.path.join("gorseller", filename),
        os.path.join("gorseller", f"{name_without_ext}.png"),
        os.path.join("gorseller", f"{name_without_ext}.jpg"),
        os.path.join("/workspace/artifacts", filename),
        os.path.join("/workspace/artifacts", f"{name_without_ext}.png"),
        os.path.join("/workspace/artifacts", f"{name_without_ext}.jpg"),
    ]
    
    for p in candidate_paths:
        if os.path.exists(p):
            return p
            
    search_dirs = [".", "gorseller", "/workspace/artifacts"]
    for sdir in search_dirs:
        if os.path.exists(sdir):
            try:
                for fname in os.listdir(sdir):
                    if fname.lower() == filename.lower() or fname.lower() == f"{name_without_ext}.png".lower() or fname.lower() == f"{name_without_ext}.jpg".lower():
                        return os.path.join(sdir, fname)
            except Exception:
                pass
                
    return None

# ---------------------------------------------------------
# Load Database (vaka_veritabani.json or Fallback)
# ---------------------------------------------------------
@st.cache_data
def load_cases():
    db_path = "vaka_veritabani.json"
    if not os.path.exists(db_path):
        db_path = "/workspace/artifacts/vaka_veritabani.json"
        
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Veri tabanı yüklenemedi: {e}")
            
    return {}

CASES = load_cases()

# ---------------------------------------------------------
# Header & Title
# ---------------------------------------------------------
st.markdown("<h1 class='main-title'>🐄 VET401 Akıllı Anamnez & Bulgu Sorgu Konsolu</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Çukurova Üniversitesi Veteriner Fakültesi — İç Hastalıkları I Klinik Vaka Analiz Portalı</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. MAIN PAGE: CASE SELECTION PANEL (Vaka Seçim Alanı)
# ---------------------------------------------------------
st.markdown("<div class='vaka-box'>", unsafe_allow_html=True)
st.markdown("### 🔍 İncelemek İstediğiniz Vakayı Seçiniz:")

if CASES:
    selected_case_name = st.selectbox(
        "Sistemdeki 12 Klinik Vaka Listesi:",
        options=list(CASES.keys()),
        index=0,
        key="main_case_selector"
    )
    active_case = CASES[selected_case_name]
else:
    st.error("Lütfen vaka_veritabani.json dosyasının yüklü olduğunu kontrol edin.")
    st.stop()

st.markdown("</div>", unsafe_allow_html=True)

# Session state history reset when case changes
if "last_case" not in st.session_state:
    st.session_state.last_case = selected_case_name

if st.session_state.last_case != selected_case_name:
    st.session_state.history = []
    st.session_state.last_case = selected_case_name

if "history" not in st.session_state:
    st.session_state.history = []

# Display Active Case Header & Initial Complaint
st.markdown(f"<div class='vaka-header'>📋 {selected_case_name} — İlk Başvuru Şikayeti</div>", unsafe_allow_html=True)
st.info(f"**Hastanın Başvuru Şikayeti:** {active_case['sikayet']}")

# Macroscopic Image Display
if "makroskopik_gorsel" in active_case:
    mg = active_case["makroskopik_gorsel"]
    st.markdown("### 📸 Klinik Makroskopik Lezyon Görseli")
    g_path = find_gorsel_path(mg.get("file", ""))
    
    if g_path:
        st.image(g_path, caption=f"{mg.get('fig', '')} — {mg.get('title', '')}", use_container_width=True)
    else:
        st.caption(f"**{mg.get('fig', '')} — {mg.get('title', '')}**")
        st.write(mg.get("desc", ""))
        uploaded_img = st.file_uploader(
            f"📷 {mg.get('fig', '')} Görselini Yükleyiniz (.jpg / .png):",
            type=["jpg", "jpeg", "png"],
            key=f"up_macro_{active_case.get('kod', 'macro')}"
        )
        if uploaded_img is not None:
            st.image(uploaded_img, caption=f"Yüklenen Klinik Görsel: {mg.get('fig', '')}", use_container_width=True)

# ---------------------------------------------------------
# 2. SIDEBAR: INSTRUCTOR PORTAL ONLY (Sadece Eğitmen Portalı)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏛️ ÇU Veteriner Fakültesi")
    st.markdown("**VET401 İç Hastalıkları I**")
    st.markdown("---")
    st.markdown("### 🔒 Eğitmen Portalı (Sadece Öğretim Üyesi)")
    teacher_login = st.checkbox("Eğitmen Anahtar Paneli", key="sidebar_t_login")
    
    if teacher_login:
        pass_code = st.text_input("Giriş Şifresi:", type="password", key="sidebar_t_pass")
        if pass_code == "vet401":
            st.success("Eğitmen Erişimi Onaylandı!")
            st.markdown("#### 🔑 Bu Vakanın Tüm Gizli Bulguları:")
            for ck, cv in active_case["categories"].items():
                st.markdown(f"**• {cv['name']}:** {cv['content']}")
        elif pass_code:
            st.error("Hatalı Şifre!")

# ---------------------------------------------------------
# 3. QUESTION INPUT & MATCHING ENGINE
# ---------------------------------------------------------
st.markdown("### 💬 Sorunuzu veya İncelemek İstediğiniz Muayeneyi Yazınız:")

def match_query(user_text, categories_dict):
    text_clean = user_text.lower().strip()
    text_clean = text_clean.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    
    is_microscope_query = any(kw in text_clean for kw in ["mikroskop", "kazinti", "lam", "akar", "uyuz", "artrospor", "koh"])
    
    matched_cats = []
    for cat_key, cat_info in categories_dict.items():
        # If microscope is queried, prevent biochemistry/blood matching unless explicitly asked
        if is_microscope_query and cat_key in ["BIYOKIMYA_PANELI", "HEMOGRAM", "KAN_GAZI", "IDRAR_TAHLILI"]:
            continue
            
        for kw in cat_info.get("keywords", []):
            kw_clean = kw.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
            if re.search(r'' + re.escape(kw_clean) + r'', text_clean) or kw_clean in text_clean:
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

# ---------------------------------------------------------
# 4. DISCOVERED INFORMATION DISPLAY
# ---------------------------------------------------------
st.markdown("---")
st.markdown(f"### 📂 Keşfedilen Klinik İpuçları ve Muayene Bulguları ({len(st.session_state.history)} Bilgi Açıldı)")

if st.session_state.history:
    for item in reversed(st.session_state.history):
        # If there is a visual for dermatological/microscopic exam
        if "gorsel" in item:
            g = item["gorsel"]
            g_found = find_gorsel_path(g.get("file", ""))
            
            if g_found:
                # If image is available, display ONLY the photo (no extra text clutter per user rule)
                st.markdown(f"#### 🔬 {g.get('title', 'Mikroskopik Görsel')}")
                st.image(g_found, use_container_width=True)
            else:
                # If image file not loaded, display content and upload button
                st.markdown(f"""
                    <div class='card-found'>
                        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                            <span class='badge-category'>{item['title']}</span>
                            <span style='font-size:12px; color:#7F7F7F;'>Sorulan Soru: "{item['query']}"</span>
                        </div>
                        <div class='card-content'><b>🩺 Bulgu / Öykü:</b> {item['content']}</div>
                    </div>
                """, unsafe_allow_html=True)
                st.caption(f"**{g.get('fig', '')} — {g.get('title', '')}**")
                st.write(g.get("desc", ""))
                up_micro = st.file_uploader(
                    f"📷 {g.get('fig', '')} Mikroskopik Görselini Yükleyiniz (.jpg / .png):",
                    type=["jpg", "jpeg", "png"],
                    key=f"up_micro_{item['cat_key']}"
                )
                if up_micro is not None:
                    st.image(up_micro, use_container_width=True)
        else:
            st.markdown(f"""
                <div class='card-found'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                        <span class='badge-category'>{item['title']}</span>
                        <span style='font-size:12px; color:#7F7F7F;'>Sorulan Soru: "{item['query']}"</span>
                    </div>
                    <div class='card-content'><b>🩺 Bulgu / Öykü:</b> {item['content']}</div>
                </div>
            """, unsafe_allow_html=True)
