import requests
import re

def bugunun_nobetci_eczaneleri(sehir, ilce):
    # URL oluştur
    url = f"https://www.eczaneler.gen.tr/nobetci-{sehir.lower()}-{ilce.lower()}"
    
    # Sayfayı çek
    response = requests.get(url)
    response.encoding = "utf-8"
    html = response.text

    # Bugünün tab-pane HTML bloğunu bul
    aktif_tab_match = re.search(
        r'<div class="tab-pane fade show active".*?</div>\s*</div>', 
        html, re.DOTALL
    )
    if not aktif_tab_match:
        return []

    aktif_tab_html = aktif_tab_match.group(0)

    # Eczane adı, adres ve telefon bilgilerini regex ile çek
    pattern = re.compile(
        r'<span class="isim">(.*?)</span>.*?'    # Eczane adı
        r"<div class='col-lg-6'>(.*?)</div>.*?"  # Adres
        r"<div class='col-lg-3 py-lg-2'>(.*?)</div>",  # Telefon
        re.DOTALL
    )

    eczaneler = []
    for match in pattern.finditer(aktif_tab_html):
        isim, adres, telefon = match.groups()
        eczaneler.append({
            "isim": isim.strip(),
            "adres": adres.strip(),
            "telefon": telefon.strip()
        })

    return eczaneler

# Örnek kullanım
eczaneler = bugunun_nobetci_eczaneleri("izmir", "guzelbahce")
for e in eczaneler:
    print(f"Eczane: {e['isim']}\nAdres: {e['adres']}\nTelefon: {e['telefon']}\n")
