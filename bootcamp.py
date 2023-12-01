from time import sleep
from playwright.sync_api import sync_playwright, Playwright
import json
from utils import remove_special_characters

class Bootcamp:
    def __init__(self, url_bootcamp: str, playwright: Playwright, headless = False):
        self.url_bootcamp = url_bootcamp
        self.headless = headless
        self.playwright = playwright
        self.browser = None
        self.page = None
        self.timeout = 10000
    
    def init_playwright(self):
        self.browser = self.playwright.firefox.launch(headless = self.headless)
        self.page = self.browser.new_page()
    def close(self):
        self.page.close()
    def goto(self, url):
        self.page.goto(url)
    def remover_tildes(self,cadena):        
        return cadena.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    def get_bootcamp_videos(self):
        titulo_bootcamp = self.page.locator('//h1').text_content().strip()
        enlaces_clases =  self.page.locator('//ul/li/div/ul/a').all()
        titulos_clases = self.page.locator('//div/div/p[2]').all()
        links = []
        counter = 0
        for enlace in enlaces_clases:
            href = enlace.get_attribute('href')
            # Crea un path con el número de curso y el nombre del curso
            label=self.remover_tildes(titulos_clases[counter].text_content().strip())
            link = f'https://codigofacilito.com{href}'
            link_info = {"titulo":label,"href": link}
            links.append(link_info)
            counter += 1
        sleep(5)
        with open("bootcamp.json", "w") as file:
            data = {
                "titulo":titulo_bootcamp,
                "clases": links
            }
            json.dump(data, file,indent=4, sort_keys=False)
        
        print("Se guardaron los enlaces en el archivo 'bootcamp.json'")
        self.browser.close()
        
if __name__ == "__main__":
    url_bootcamp = input('Ingresa la URL del bootcamp:')
    with sync_playwright() as playwright:
        bootcamp = Bootcamp(url_bootcamp, playwright, headless = False)
        bootcamp.init_playwright()
        print("Obteniendo información del bootcamp")
        bootcamp.goto(url_bootcamp)
        bootcamp.get_bootcamp_videos()