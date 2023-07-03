import os
import json
import click
import subprocess
import utils
from cookies import FacilitoCookies

class Downloader:
    
    def __init__(self, external_downloader: str, quality: str):
        self.external_downloader = external_downloader
        self.quality = quality
        self.cookies = 'cookies.txt'
        self.data_path  = 'data.json'

    def load_data(self):
        with open(self.data_path, 'r', encoding = 'utf-8') as f:
            self.data = json.load(f)

    def m3u8_downloader(self, file_name, url, dest, ext_dwl):
        """
        external_downloader: str <- 'yt-dlp', 'wget', 'aria2'
        format_selection: str <- 'bv[height<=quality]+ba/b[height<=quality]'
        """
        if (self.quality == 'best'):
            self.format_selection = 'bv+ba/b'
        else:
            self.format_selection = f'bv[height<={self.quality}]+ba/b[height<={self.quality}]'
        
        if (ext_dwl =='yt-dlp'):
            command = ['yt-dlp', '-f', self.format_selection, '--cookies', self.cookies, '-o', f'{dest}/{file_name}.%(ext)s', url]
        elif (ext_dwl =='wget'):
            command = ['yt-dlp', '-f', self.format_selection, '--cookies', self.cookies, '-o', f'{dest}/{file_name}.%(ext)s', '--external-downloader', 'wget', url]
        elif (ext_dwl =='aria2'):
            command = ['yt-dlp', '-f', self.format_selection, '--cookies', self.cookies, '-o', f'{dest}/{file_name}.%(ext)s', '--external-downloader', 'aria2c', '--external-downloader-args', '-s 10 -x 10 -k 1M', url]
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

            m  = 1
            for video in module:
                title = video[0]
                url = video[1]
                print(f'[{j} / {k}] {title}')
                self.m3u8_downloader(file_name=f'{m}-{title}', url=url, dest=dest, ext_dwl=self.external_downloader)
                j = j + 1
                m = m + 1
        
        os.rename(src='tmp', dst=self.data['course_name'])


    def make_zip_file(self):
        course_name = self.data['course_name']
        command = ['zip', '-r', f'{course_name}.zip', f'{course_name}']
        subprocess.run(command, check=True)


downloaders = ['yt-dlp', 'wget', 'aria2']
qualities = ['360', '480', '720', '1080', 'best']
help_d = 'Select the external downloader (yt-dlp, wget, or aria2). Default: aria2. ' 
help_q = 'Select the video quality (360, 480, 720, 1080 or best). Default: best'

@click.command()
@click.option('-d', type=click.Choice(downloaders), default='aria2', prompt=False, help=help_d)
@click.option('-q', type=click.Choice(qualities), default='best', prompt=False, help=help_q)
def main(d, q):
    utils.check_aria2()
    FacilitoCookies().get_cookies()
    dl = Downloader(external_downloader=d, quality=q)
    dl.load_data()
    dl.dl_course()

if __name__ == "__main__":
    main()
