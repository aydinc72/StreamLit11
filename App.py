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
base_url = f"https://www.eczaneler.gen.tr/nobetci-{selected_sehir.lower()}-{selected_ilce.lower()}"
st.markdown(f"Seçilen URL: [{base_url}]({base_url})")

if st.button("Yeni Sekmede Aç"):
    js = f"window.open('{base_url}')"
    components.html(f"<script>{js}</script>")

# -----------------------------
# Web Scraping (hiç re yok)
# -----------------------------
@st.cache_data(show_spinner=False)
def fetch_nobetci_eczaneler(sehir, ilce):
    url = f"https://www.eczaneler.gen.tr/nobetci-{sehir.lower()}-{ilce.lower()}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text

        eczaneler = []
        # tüm eczane bloklarını parçala
        blocks = html.split('<div class="eczane-content">')[1:]

        for block in blocks:
            # Eczane adı
            name = ""
            if "<h3" in block:
                start = block.find("<h3")
                start = block.find(">", start) + 1
                end = block.find("</h3>", start)
                name = block[start:end].strip()

            # Adres
            address = ""
            if '<div class="address' in block:
                start = block.find('<div class="address')
                start = block.find(">", start) + 1
                end = block.find("</div>", start)
                address = block[start:end].strip()

            # Telefon
            phone = ""
            if '<div class="phone' in block:
                start = block.find('<div class="phone')
                start = block.find(">", start) + 1
                end = block.find("</div>", start)
                phone = block[start:end].strip()

            if name:
                eczaneler.append({"Eczane": name, "Adres": address, "Telefon": phone})

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
    st.warning("Bu ilçe için veri bulunamadı.")
