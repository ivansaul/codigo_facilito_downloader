import os
import re
import sys
import json
import shutil
import requests
import subprocess
from time import sleep
from pprint import pprint
from bs4 import BeautifulSoup


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FacilitoDL:
    """
    external_downloader: str <- 'yt-dlp', 'wget', 'aria2'
    """
    
    def __init__(self, table_of_content: dict, external_downloader: str):
        self.table_of_content = table_of_content
        self.external_downloader = external_downloader

    
    def m3u8_downloader(self, file_name, url, dest, ext_dwl):

        cookies = 'cookies.txt'

        if ext_dwl =='yt-dlp':
            command = ['yt-dlp', '--cookies', 'cookies.txt', '-o', f'{dest}/{file_name}.%(ext)s', url]
        elif ext_dwl =='wget':
            command = ['yt-dlp', '--cookies', 'cookies.txt', '-o', f'{dest}/{file_name}.%(ext)s', '--external-downloader', 'wget', url]
        elif ext_dwl =='aria2':
            command = ['yt-dlp', '--cookies', 'cookies.txt', '-o', f'{dest}/{file_name}.%(ext)s', '--external-downloader', 'aria2c', '--external-downloader-args', '-s 10 -x 10 -k 1M', url]
        subprocess.run(command, check=True)


    def dl_course(self):
       
        modules = self.table_of_content['modules']
        j, k = 1, sum(len(m) for m in modules)

        os.mkdir(path='tmp')

        for i, module in enumerate(modules):
            dest = f'tmp/modulo_{i+1}'
            os.mkdir(path = dest)
            for video in module:
                title = video[0]
                url = video[1]
                print(f'[{j} / {k}] {title}')
                self.m3u8_downloader(file_name=f'{i+1}-{title}', url=url, dest=dest, ext_dwl=self.external_downloader)
                j = j + 1
        
        os.rename(src='tmp', dst=self.table_of_content['course_name'])


    def make_zip_file(self):
        course_name = self.table_of_content['course_name']
        command = ['zip', '-r', f'{course_name}.zip', f'{course_name}']
        subprocess.run(command, check=True)


class Facilito:
    def __init__(self, email, password, url_course, headless):      
        self.email = email
        self.password = password
        self.url_course = url_course
        self.headless = headless

        self.table_of_content = {}
        self.url_login = "https://codigofacilito.com/users/sign_in"


    def quit(self):
        self.driver.quit()


    def login(self):
        if self.headless:
            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            self.driver = webdriver.Firefox(options = options)
        else:
            self.driver = webdriver.Firefox()
        
        self.driver.get(self.url_login) 
    
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//button[@type="submit"]')))
        self.driver.find_element(By.ID, 'sign_in_email_field').send_keys(self.email)
        self.driver.find_element(By.ID, 'sign_in_password_field').send_keys(self.password)
        self.driver.find_element(By.XPATH, '//button[@class="f-main-btn block full-width f-text-18"]').click()
        
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="users-nav"]')))


    def get_course_name(self):
        course_name = self.course_name =  self.driver.find_element(By.XPATH, '//a[@class="bold h5"]').text
        return course_name


    def get_video_id(self):
        video_id = self.driver.find_element(By.XPATH, '//input[@id="video_id"]').get_attribute("value")
        return video_id


    def get_video_title(self):
        video_title = self.driver.find_element(By.XPATH, '//h1[@class="ibm bold-600 no-margin f-text-22"]').text
        return video_title
    

    def get_course_id(self):
        course_id = self.driver.find_element(By.XPATH, '//input[@id="course_id"]').get_attribute("value")
        return course_id


    def get_course_content(self):        
        self.driver.get(self.url_course)
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//i[@class="f-normal-text material-icons bold"]')))
    
        drop_downs = self.driver.find_elements(By.XPATH, '//i[@class="f-normal-text material-icons bold"]')
        for drop in drop_downs: 
            drop.click()
            sleep(3)
        
        # //div[@class="f-top-16"][1->7]//a
        n_modules =  len(self.driver.find_elements(By.XPATH, '//div[@class="f-top-16"]'))
        self.videos_url_by_modules = []

        for i in range(1, n_modules + 1) :
            a = self.driver.find_elements(By.XPATH, f'//div[@class="f-top-16"][{i}]//a')
            a = [ i.get_attribute('href') for i in a ]
            self.videos_url_by_modules.append(a)

        self.course_name = self.get_course_name()
        self.course_id = self.get_course_id()
        self.table_of_content['course_name'] = self.course_name
        self.table_of_content['course_id'] = self.course_id
        self.table_of_content['modules'] = self.videos_url_by_modules
        

    def get_m3u8_url(self):
        self.videos_m3u8_by_modules = []
        base_url = "https://video-storage.codigofacilito.com"
        for videos in self.videos_url_by_modules:
            tmp = []
            for url in videos:
                if ('/videos/' in url):
                    self.driver.get(url)
                    wait = WebDriverWait(self.driver, 10)
                    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="video_id"]')))
                    video_title = self.get_video_title()
                    video_m3u8 = f'{base_url}/hls/{self.course_id}/{self.get_video_id()}/playlist.m3u8'
                    tmp.append((video_title, video_m3u8))
                    print(video_title)
                    print(video_m3u8)

            self.videos_m3u8_by_modules.append(tmp)
        self.table_of_content['modules'] = self.videos_m3u8_by_modules
        
        with open('data.json','w', encoding='utf-8') as file:
            json.dump(self.table_of_content, file, indent=4, ensure_ascii= False)


if __name__ == "__main__":

    # username = ' '
    # password = ' '
    # url_course = "https://codigofacilito.com/videos/introduccion-al-curso-6194a86b-4140-45a2-89e9-2fa9bcb03bf2"

    print('Ingresa tus credenciales de Codigo Facilito')
    username = input('Ingresa tu e-mail: ')
    password = input('Ingresa tu contraseña: ')
    url_course = input('Ingresa la URL del curso a descargar: ')
    
    facilito = Facilito(username, password, url_course, headless = True)    
    facilito.login()
    facilito.get_course_content()
    facilito.get_m3u8_url()
    facilito.quit()

    dl = FacilitoDL(facilito.table_of_content, external_downloader='aria2')
    dl.dl_course()
    dl.make_zip_file()