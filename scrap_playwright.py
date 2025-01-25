import re

from playwright.sync_api import sync_playwright

import sheets_funcs
import sender

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

def get_new_jobs(jobs):
    df = sheets_funcs.get_sheet_as_df(sheets_funcs._worksheet)
    new_jobs = []
    for job in jobs:
        if sheets_funcs.check_if_job_exists(df, job["link"]):
            new_jobs.append(job)
    return new_jobs

def update_new_jobs(jobs):
    df = sheets_funcs.get_sheet_as_df(sheets_funcs._worksheet)
    for job in jobs:
        length = sheets_funcs.get_column_length(df)
        df.loc[length] = job
    sheets_funcs.update_sheets(sheets_funcs._worksheet, df)

def send_new_jobs(jobs):
    message = f"Hola Ivet!<br>Han publicat <b>{len(jobs)} noves ofertes de feina</b> a Barcelona Activa. Aquí sota les tens:<ul>"
    for job in jobs:
        message = message + f"<li><a href='{job['link']}'>{job['titol']}</a></li>"
    message = message + "</ul>Molta sort en la cerca!<br> <b>T'estim molt <3</b>"
    subject = "Nova oferta a Barcelona Activa!"
    sender.send_email(subject, message)

def main():
    feines = []
    feines_noves = []
    for sector in SECTORS:
        print(f"Scraping {URL_BASE.replace('SECTOR', sector)}...")
        jobs = obtenir_dades_sectors(URL_BASE.replace("SECTOR", sector))
        new_jobs = get_new_jobs(jobs)
        print(f"Hem trobat {len(jobs)} feines, de les quals {len(new_jobs)} són noves.")
        update_new_jobs(new_jobs)
        feines = feines + jobs
        feines_noves = feines_noves + new_jobs
    print(f"feines noves: {feines_noves}")
    print(f"fines antigues: {[feina for feina in feines if feina not in feines_noves]}")
    if len(feines_noves) > 0:
        send_new_jobs(feines_noves)

if __name__ == "__main__":
    main()