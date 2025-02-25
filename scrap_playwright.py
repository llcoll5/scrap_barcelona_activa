import os
import re
import time

from playwright.sync_api import sync_playwright

import sender
import sheets_funcs

class JobScraper:
    def __init__(self):
        self.KEYWORDS_PATTERNS = ''
        self.worksheet = sheets_funcs.get_worksheet(os.getenv("WORKSHEET_KEY"))
        self.wait_selector = '.tc-job-position'
        self.query_selector = '.tc-job-link'
        self.job_scraper_name = type(self).__name__
        self.feines = []
        self.feines_noves = []

    def obtenir_dades_sectors(self, url):
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)
            self.pagina = navegador.new_page()
            self.pagina.goto(url)
            try:
                # self.pagina.wait_for_selector(self.wait_selector)
                locator = self.pagina.locator(self.wait_selector)
                locator.wait_for()
            except Exception as e:
                print(e)
            
            ofertes = self.pagina.query_selector_all(self.query_selector)
            dades = self.extreure_dades_ofertes(ofertes)
            
            return dades
    
    def extreure_dades_ofertes(self, ofertes):
        dades = []
        for oferta in ofertes:
            titol = oferta.inner_text()
            link = oferta.get_attribute("href")
            if self.check_key_words(titol):
                dades.append({
                    "titol": titol,
                    "link": link
                })
        return dades
        
    def check_key_words(self, job): 
        return re.search(self.KEYWORDS_PATTERNS, job, re.I)
    
    def get_new_jobs(self, jobs):
        self.df = sheets_funcs.get_sheet_as_df(self.worksheet)
        new_jobs = []
        for job in jobs:
            if sheets_funcs.check_if_job_exists(self.df, job["link"]):
                new_jobs.append(job)
        return new_jobs

    def update_new_jobs(self, jobs):
        self.df = sheets_funcs.get_sheet_as_df(self.worksheet)
        for job in jobs:
            length = sheets_funcs.get_column_length(self.df)
            self.df.loc[length] = job
        sheets_funcs.update_sheets(self.worksheet, self.df)
    
    def get_jobs_list(self):
        message = ""
        for job in self.feines_noves:
            message = message + f"<li><a href='{job['link']}'>{job['titol']}</a></li>"
        return message

    def send_new_jobs(self):
        message = f"Hola Ivet!<br>Han publicat <b>{len(self.feines_noves)} noves ofertes de feina</b> a {self.job_scraper_name}. Aquí sota les tens:<ul>"
        message = message + self.get_jobs_list()
        message = message + "</ul>Molta sort en la cerca!<br> <b>T'estim molt <3</b>"
        subject = f"Nova oferta a {self.job_scraper_name}!"
        sender.send_email(subject, message)


class BarcelonaActiva(JobScraper):
    def __init__(self):
        super().__init__()
        self.URL_BASE = "https://treball.barcelonactiva.cat/porta22/cat/assetsocupacio/ofertesfeina/sectors.jsp?sector=SECTOR&idioma=cat"
        self.SECTORS = [
            "40271",
            "83689",
            "40279",
            "106360",
            "83686",
            "83688",
            "40272",
            "120662"
        ]
        self.KEYWORDS = [
            "v[íi]deo",
            "audiovisual",
            "producci[óo]",
            "editor",
            "m[uo]ntador",
            "c[àa]m[ea]ra",
            "cam[ea]r[òo]graf"
        ]
        self.KEYWORDS_PATTERNS = "(" + ")|(".join(self.KEYWORDS) + ")"    
        self.worksheet = sheets_funcs.get_worksheet(os.getenv("WORKSHEET_KEY"), sheet_name="BarcelonaActiva") 
    
    def get_jobs(self):
        for sector in self.SECTORS:
            print(f"Scraping {self.URL_BASE.replace('SECTOR', sector)}...")
            jobs = self.obtenir_dades_sectors(self.URL_BASE.replace("SECTOR", sector))
            new_jobs = self.get_new_jobs(jobs)
            print(f"Hem trobat {len(jobs)} feines, de les quals {len(new_jobs)} són noves.")
            self.update_new_jobs(new_jobs)
            self.feines = self.feines + jobs
            self.feines_noves = self.feines_noves + new_jobs
        print(f"feines noves: {self.feines_noves}")
        print(f"feines antigues: {[feina for feina in self.feines if feina not in self.feines_noves]}")
        if len(self.feines_noves) > 0:
            self.send_new_jobs()

class CIDO_DIBA(JobScraper):
    def __init__(self):
        super().__init__()
        self.URL_BASE = "https://cido.diba.cat/oposicions?filtreParaulaClau%5Bkeyword%5D=KEYWORD&ordenacio=DATAPUBLICACIO&ordre=DESC&showAs=GRID&filtreProximitat%5Bpoblacio%5D=&filtreProximitat%5Bkm%5D=&filtreProximitat%5Blatitud%5D=&filtreProximitat%5Blongitud%5D=&filtreDataPublicacio%5Bde%5D=&filtreDataPublicacio%5BfinsA%5D=&filtreEstat%5BterminiObert%5D=1&filtreSeleccioTitulacio%5BtitulacioRequerida%5D%5Bkeyword%5D=&opcions-menu=&_token=Z8ljM6QCnPh-LB71yn1cFwfsBugo1fFuInHtUrcYFbM"
        self.KEYWORDS = [
            "video",
            "audiovisual",
            "produccio",
            "editor",
            "muntador",
            "montador",
            "camera",
            "camerograf"
        ]
        self.KEYWORDS_PATTERNS = "(" + ")|(".join(self.KEYWORDS) + ")"  
        self.worksheet = sheets_funcs.get_worksheet(os.getenv("WORKSHEET_KEY"), sheet_name="CIDO-DIBA") 
        self.wait_selector = '.panel-heading'
        self.query_selector = '.panel-resultat'

        self.URL_PATH="https://cido.diba.cat"

    def get_jobs_list(self):
        message = ""
        for job in self.feines_noves:
            message = message + f"<li><a href='{job['link']}'>{job['titol']}</a> - {job['lloc']}</li>"
        return message

    def extreure_dades_ofertes(self, ofertes):
        dades = []
        for oferta in ofertes:
            lloc = oferta.query_selector(".panel-heading").query_selector("p").inner_text()
            titol = oferta.query_selector("a").inner_text()
            link = self.transformar_link(oferta.query_selector("a").get_attribute("href"))
            if self.check_key_words(titol):
                dades.append({
                    "titol": titol,
                    "link": link,
                    "lloc": lloc
                })
        return dades
    
    def transformar_link(self, link):
        return self.URL_PATH + link
    
    def get_jobs(self):
        self.feines = []
        self.feines_noves = []
        for keyword in self.KEYWORDS:
            print(f"Scraping {self.URL_BASE.replace('KEYWORD', keyword)}...")
            jobs = self.obtenir_dades_sectors(self.URL_BASE.replace('KEYWORD', keyword))
            new_jobs = self.get_new_jobs(jobs)
            print(f"Hem trobat {len(jobs)} feines, de les quals {len(new_jobs)} són noves.")
            self.update_new_jobs(new_jobs)
            self.feines = self.feines + jobs
            self.feines_noves = self.feines_noves + new_jobs
        print(f"feines noves: {self.feines_noves}")
        print(f"feines antigues: {[feina for feina in self.feines if feina not in self.feines_noves]}")
        if len(self.feines_noves) > 0:
            self.send_new_jobs()

class TV3(JobScraper):
    def __init__(self):
        super().__init__()
        self.URL_BASE = "https://seleccio.ccma.cat/seleccio/processos.jsf"
        self.KEYWORDS = [
            "v[íi]deo",
            "audiovisual",
            "producci[óo]",
            "editor",
            "m[uo]ntador",
            "c[àa]m[ea]ra",
            "cam[ea]r[òo]graf",
            "documenta"
        ]
        self.KEYWORDS_PATTERNS = "(" + ")|(".join(self.KEYWORDS) + ")"  
        self.worksheet = sheets_funcs.get_worksheet(os.getenv("WORKSHEET_KEY"), sheet_name=self.job_scraper_name) 
        self.wait_selector = 'h3'
        self.query_selector = 'h3'

        self.URL_PATH="https://seleccio.ccma.cat/"


    def extreure_dades_ofertes(self, ofertes):
        dades = []
        for oferta in ofertes:
            titol = oferta.inner_text()
            oferta_locator = self.pagina.locator(f"text={titol}")  
            
            link_element = oferta_locator.locator("xpath=ancestor::a").first
            link = self.transformar_link(link_element.get_attribute("href"))
            if self.check_key_words(titol):
                dades.append({
                    "titol": titol,
                    "link": link
                })
        return dades

    def get_jobs(self):
        print(f"Scraping {self.URL_BASE}...")
        jobs = self.obtenir_dades_sectors(self.URL_BASE)
        new_jobs = self.get_new_jobs(jobs)
        print(f"Hem trobat {len(jobs)} feines, de les quals {len(new_jobs)} són noves.")
        self.update_new_jobs(new_jobs)
        self.feines = self.feines + jobs
        self.feines_noves = self.feines_noves + new_jobs
        print(f"feines noves: {self.feines_noves}")
        print(f"feines antigues: {[feina for feina in self.feines if feina not in self.feines_noves]}")
        if len(self.feines_noves) > 0:
            self.send_new_jobs()

    def transformar_link(self, link):
        return self.URL_PATH + link



if __name__ == "__main__":
    js = BarcelonaActiva()
    js.get_jobs()

    cido = CIDO_DIBA()
    cido.get_jobs()

    tv3 = TV3()
    tv3.get_jobs()
