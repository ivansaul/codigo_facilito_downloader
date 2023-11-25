from utils import *
from time import sleep
from playwright.sync_api import sync_playwright, Playwright

class Facilito:
    def __init__(self, email: str, password: str, url_course: str, playwright: Playwright, headless = False):
        """
        Initialize the Facilito class with the given parameters.

        Args:
            email (str): User email for login
            password (str): User password for login
            url_course (str): URL of the course
            headless (bool): Whether to launch the browser in headless mode
            playwright (Playwright): Playwright instance
        """
        self.email = email
        self.password = password
        self.url_course = url_course
        self.headless = headless
        self.playwright = playwright
        self.browser = None
        self.page = None
        self.timeout = 10000
        self.course_name = ''

        self.data = {}
        self.context = []
        self.url_login = "https://codigofacilito.com/users/sign_in"

    def init_playwright(self):
        self.browser = self.playwright.firefox.launch(headless = self.headless)
        self.page = self.browser.new_page()

    def close(self):
        self.page.close()

    def login(self):
        self.init_playwright()
        self.page.goto(self.url_login)
        self.page.wait_for_selector('//button[@type="submit"]', timeout = self.timeout)
        self.page.fill('#sign_in_email_field', self.email)
        self.page.fill('#sign_in_password_field', self.password)
        self.page.click('//button[@type="submit"]')
        self.page.wait_for_selector('//div[@class="users-nav"]', timeout = self.timeout)

    def goto(self, url):
        self.page.goto(url)
        
    def save_cookies(self):
        cookies = self.page.context.cookies()
        save_cookies('cookies.txt', cookies)

    def get_course_name(self):
        course_name =  self.page.locator('//a[@class="bold h5"]').inner_text()
        return remove_special_characters(course_name)

    def get_video_id(self):
        video_id = self.page.locator('//input[@name="video_id"]').first.get_attribute("value")
        return video_id

    def get_video_title(self):
        video_title = self.page.locator('//h1[@class="ibm bold-600 no-margin f-text-22" or @class="ibm bold-600 no-margin f-text-48"]').inner_text()
        return remove_special_characters(video_title)

    def get_course_id(self):
        course_id = self.page.locator('//input[@name="course_id"]').get_attribute("value")
        return course_id

    def get_course_content(self):        
        drop_down_selector = '//i[@class="f-normal-text material-icons bold"]'
        self.page.goto(self.url_course)
        try: # -> Find banner promo
            banner_promo = self.page.wait_for_selector('//div[@class="f-modal-close"]', timeout = self.timeout)
            banner_promo.click()
        except:
            pass 
        self.page.wait_for_selector(drop_down_selector, timeout = self.timeout)

        # Expand all drop downs
        drop_downs = self.page.query_selector_all(drop_down_selector)
        for drop in drop_downs:
            drop.click()
            sleep(3)
        
        module_boxes = self.page.query_selector_all('//div[@class="f-top-16"]')
        for index, box in enumerate(module_boxes, start = 1):
            group = box.query_selector('//h4').inner_text()
            group = remove_special_characters(group)
            group = f'{index}. {group}'
            group_info = box.query_selector('//span[@class="bold f-grey-tex"]').inner_text()
            print(f' - {group} [{group_info}]')

            a = box.query_selector_all('//a')
            a = [ i.get_attribute('href') for i in a ]
            a = [f'https://codigofacilito.com{i}' for i in a]
            
            self.context += [{"group": group, "url": url} for url in a]       

    def get_m3u8_url(self):
        base_m3u8_url = "https://video-storage.codigofacilito.com"
        self.course_name = self.get_course_name()
        
        j, k = 1, len(self.context)

        for item in self.context:
            url = item['url']
            self.page.goto(url)
            video_title = self.get_video_title()
            item['title'] = video_title

            if ('/videos/' in url):
                print(f'[{j} / {k}][streaming] {video_title}')
                item['m3u8'] = f'{base_m3u8_url}/hls/{self.get_course_id()}/{self.get_video_id()}/playlist.m3u8'

            if('/articulos/' in url):
                print(f'[{j} / {k}][reading] {video_title}')
                item['m3u8'] = None
                # Save reading as HTML file
                dir_path = f'{self.course_name}/{item["group"]}'
                file_path = f'{dir_path}/{j}. {item["title"]}.html'
                check_path(dir_path)
                write_file(file_path, self.page.content())

            j = j + 1

    def write_data(self, file_path = 'data.json'):
        self.data['name'] = self.course_name
        self.data['content'] = self.context
        write_json(data=self.data, file_path = file_path)


if __name__ == "__main__":

    email, password = check_credentials()
    url_course = input('Ingresa la URL del curso a descargar: ')
    with sync_playwright() as playwright:

        facilito = Facilito(email, password, url_course, playwright = playwright)
        print('Logging in ...', end = '\n\n')
        facilito.login()
        print('Getting course content ...', end = '\n\n')
        facilito.get_course_content()
        print('Getting download urls ...', end = '\n\n')
        facilito.get_m3u8_url()
        print('Writing json data ...', end = '\n\n')
        facilito.write_data()
        facilito.close()
