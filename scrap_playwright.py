import re

from playwright.sync_api import sync_playwright

URL_BASE = "https://treball.barcelonactiva.cat/porta22/cat/assetsocupacio/ofertesfeina/sectors.jsp?sector=SECTOR&idioma=cat"
SECTORS = [
    "40271",
    "83689",
    "40279",
    "106360",
    "83686",
    "83688",
    "40272",
    "120662"
]
KEYWORDS = [
    "v[íi]deo",
    "audiovisual",
    "producci[óo]",
    "editor",
    "m[uo]ntador",
    "cam[ea]r[òo]graf"
]
KEYWORDS_PATTERNS = "(" + ")|(".join(KEYWORDS) + ")"

def obtenir_dades_sectors(url):
    with sync_playwright() as p:
        # Obre el navegador
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()
        pagina.goto(url)

        # Dona temps perquè es carregui el contingut dinàmic
        pagina.wait_for_selector(".tc-job-position")

        # Extreu els elements amb les ofertes
        ofertes = pagina.query_selector_all(".tc-job-link")

        # Llista per guardar les dades
        dades = []
        for oferta in ofertes:
            titol = oferta.inner_text()
            # descripcio = oferta.query_selector(".tc-job-listing-item-description").inner_text()
            link = oferta.get_attribute("href")
            if check_key_words(titol):
                dades.append({
                    "titol": titol,
                    # "descripcio": descripcio,
                    "link": link
                })

        navegador.close()
        return dades
    
def check_key_words(job): 
    return re.search(KEYWORDS_PATTERNS, job, re.I)

# Obté les ofertes i mostra-les
for sector in SECTORS:
    ofertes = obtenir_dades_sectors(URL_BASE.replace("SECTOR", sector))
    print(f"Scraping {URL_BASE.replace('SECTOR', sector)}...")
    for oferta in ofertes:
        print(oferta)
