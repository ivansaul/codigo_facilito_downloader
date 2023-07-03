import requests
import http.cookiejar
from utils import input_credentials

class FacilitoCookies:
    def __init__(self):
        self.base_url = 'https://codigofacilito.com'
        self.auth_url = '/users/sign_in'
        self.course_url = '/cursos/tareas-django'
        self.cookies_path = 'cookies.txt'

    def get_cookies(self):
        """
        Authenticates a user and saves the obtained cookies to a file in Netscape format.

        This method performs the authentication process for a user by sending their credentials to the
        CodigoFacilito website. After a successful login, it saves the obtained cookies to a file in
        Netscape format, allowing future use for authorized requests.

        Returns:
            None. The method saves the cookies to a file but does not return any value.

        Raises:
            None.
        """
        username, password = input_credentials()

        payload = {'user[email]': username, 'user[password]': password}
        session = requests.Session()
        session.post(self.base_url + self.auth_url, data=payload)
        response = requests.get(self.base_url + self.course_url)

        # Create a MozillaCookieJar object to store cookies in Netscape format
        cookie_jar = http.cookiejar.MozillaCookieJar('cookies.txt')
        cookie_jar._cookies = response.cookies._cookies

        # Save the cookies to the file in Netscape format
        cookie_jar.save(ignore_discard=True)
        print("Getting cookies.txt ...")