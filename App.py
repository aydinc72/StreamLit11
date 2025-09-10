import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Türkiye Nöbetçi Eczaneler", layout="wide")
st.title("Türkiye Nöbetçi Eczaneler")

# -----------------------------
# Şehir ve İlçe Listeleri
# -----------------------------
ilceler_by_il = {
    "izmir": ["guzelbahce"],
    "istanbul": ["sariyer"]
}

sehirler = list(ilceler_by_il.keys())

# -----------------------------
# UI: Şehir ve İlçe Seçimi
# -----------------------------
selected_sehir = st.selectbox("Şehir seç", sehirler, index=sehirler.index("izmir"))

default_ilce = "guzelbahce" if selected_sehir == "izmir" else ilceler_by_il[selected_sehir][0]

selected_ilce = st.selectbox(
    "İlçe seç",
    ilceler_by_il[selected_sehir],
    index=ilceler_by_il[selected_sehir].index(default_ilce)
)

# -----------------------------
# URL oluştur ve buton ile aç
# -----------------------------
base_url = f"https://www.eczaneler.gen.tr/eczaneler/{selected_sehir.lower()}-{selected_ilce.lower()}"
st.markdown(f"Seçilen URL: [{base_url}]({base_url})")

if st.button("Yeni Sekmede Aç"):
    js = f"window.open('{base_url}')"
    components.html(f"<script>{js}</script>")

# -----------------------------
# Web Scraping (hiç BeautifulSoup ve re yok)
# -----------------------------
@st.cache_data(show_spinner=False)
def fetch_nobetci_eczaneler(sehir, ilce):
    url = f"https://www.eczaneler.gen.tr/eczaneler/{sehir.lower()}-{ilce.lower()}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text

        eczaneler = []
        # "Image: Eczane adı" ifadesine göre parçala
        parts = html.split("Image: Eczane adı")
        for part in parts[1:]:
            # Eczane Adı
            lines = part.splitlines()
            name = lines[1].strip() if len(lines) > 1 else ""

            # Adres
            address = ""
            if "Image: Eczane adresi" in part:
                addr_part = part.split("Image: Eczane adresi")
                addr_lines = addr_part[1].splitlines()
                address = addr_lines[1].strip() if len(addr_lines) > 1 else ""

            # Telefon
            phone = ""
            if "Image: Eczane telefonu" in part:
                phone_part = part.split("Image: Eczane telefonu")
                phone_lines = phone_part[1].splitlines()
                phone = phone_lines[1].strip() if len(phone_lines) > 1 else ""

            if name:
                eczaneler.append({
                    "Eczane": name,
                    "Adres": address,
                    "Telefon": phone
                })

        return pd.DataFrame(eczaneler)

    except Exception:
        return pd.DataFrame()

# -----------------------------
# Veri çek
# -----------------------------
df = fetch_nobetci_eczaneler(selected_sehir, selected_ilce)

# -----------------------------
# Tablo gösterimi
# -----------------------------
today_str = datetime.now().strftime("%d %B %Y")
st.subheader(f"{today_str} Tarihli Nöbetçi Eczaneler – {selected_ilce.capitalize()} / {selected_sehir.capitalize()}")

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Bu ilçe için eczane verisi bulunamadı.")
