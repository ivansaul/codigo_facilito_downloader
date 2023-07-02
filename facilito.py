import os
import json
from utils import *
from time import sleep
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
        self.course_name =  self.driver.find_element(By.XPATH, '//a[@class="bold h5"]').text
        return self.course_name


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
        try: # -> Find banner promo
            sleep(5)
            banner_promo = self.driver.find_element(By.XPATH, '//div[@class="f-modal-close"]')
            banner_promo.click()
        except:
            pass 
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
            a = [ i for i in a if i!='https://codigofacilito.com/videos/' ] # FIXME: remove empty video
            a = [ i for i in a if i!='https://codigofacilito.com/articulos/' ] # FIXME: remove empty article
            self.videos_url_by_modules.append(a)

        self.course_name = self.get_course_name()
        self.course_id = self.get_course_id()
        self.table_of_content['course_name'] = self.course_name
        self.table_of_content['course_id'] = self.course_id
        self.table_of_content['modules'] = self.videos_url_by_modules
        

    def get_m3u8_url(self):
        self.videos_m3u8_by_modules = []
        base_url = "https://video-storage.codigofacilito.com"
        
        j, k = 1, sum(len(m) for m in self.videos_url_by_modules)

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
                    print(f'[{j} / {k}][vid] {video_title}')
                    j = j + 1

                if('/articulos/' in url):
                    self.driver.get(url)
                    wait = WebDriverWait(self.driver, 10)
                    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="video_id"]')))
                    # TODO: IMPLEMENT get_article_title()
                    # article_title = self.get_article_title()
                    print(f'[{j} / {k}][doc] ...')
                    j = j + 1

            self.videos_m3u8_by_modules.append(tmp)
        self.table_of_content['modules'] = self.videos_m3u8_by_modules


    def write_data(self):    
        with open('data.json','w', encoding='utf-8') as file:
            json.dump(self.table_of_content, file, indent=4, ensure_ascii= False)


if __name__ == "__main__":

    username, password = input_credentials()
    url_course = input('Ingresa la URL del curso a descargar: ')
    check_gecko_driver()
    facilito = Facilito(username, password, url_course, headless = True)  
    facilito.login()
    facilito.get_course_content()
    facilito.get_m3u8_url()
    facilito.write_data()
    facilito.quit()