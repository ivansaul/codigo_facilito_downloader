import json
import os
import subprocess

class Downloader:
    
    def __init__(self, external_downloader: str):
        self.external_downloader = external_downloader
        self.cookies = 'cookies.txt'
        self.data_path  = 'data.json'

    def load_data(self):
        with open(self.data_path, 'r') as f:
            self.data = json.load(f)

    def m3u8_downloader(self, file_name, url, dest, ext_dwl):
        """
        external_downloader: str <- 'yt-dlp', 'wget', 'aria2'
        """
        if ext_dwl =='yt-dlp':
            command = ['yt-dlp', '--cookies', self.cookies, '-o', f'{dest}/{file_name}.%(ext)s', url]
        elif ext_dwl =='wget':
            command = ['yt-dlp', '--cookies', self.cookies, '-o', f'{dest}/{file_name}.%(ext)s', '--external-downloader', 'wget', url]
        elif ext_dwl =='aria2':
            command = ['yt-dlp', '--cookies', self.cookies, '-o', f'{dest}/{file_name}.%(ext)s', '--external-downloader', 'aria2c', '--external-downloader-args', '-s 10 -x 10 -k 1M', url]
        subprocess.run(command, check=True)


    def dl_course(self):
       
        modules = self.data['modules']
        j, k = 1, sum(len(m) for m in modules)

        if not os.path.exists('tmp'):
            os.makedirs('tmp')

        for i, module in enumerate(modules):
            dest = f'tmp/modulo_{i+1}'
            if not os.path.exists(dest):
                os.makedirs(dest)

            for video in module:
                title = video[0]
                url = video[1]
                print(f'[{j} / {k}] {title}')
                self.m3u8_downloader(file_name=f'{i+1}-{title}', url=url, dest=dest, ext_dwl=self.external_downloader)
                j = j + 1
        
        os.rename(src='tmp', dst=self.data['course_name'])


    def make_zip_file(self):
        course_name = self.data['course_name']
        command = ['zip', '-r', f'{course_name}.zip', f'{course_name}']
        subprocess.run(command, check=True)


if __name__ == "__main__":

    dl = Downloader(external_downloader='aria2')
    dl.load_data()
    dl.dl_course()
    # dl.make_zip_file()