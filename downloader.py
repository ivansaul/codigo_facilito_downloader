import os
import sys
import json
import shutil
import tarfile
import zipfile
import requests
import subprocess

class Downloader:
    
    def __init__(self, external_downloader: str):
        self.external_downloader = external_downloader
        self.cookies = 'cookies.txt'
        self.data_path  = 'data.json'

    def load_data(self):
        with open(self.data_path, 'r', encoding = 'utf-8') as f:
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


    def check_aria2(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bin_dir = os.path.join(script_dir, 'bin') 
        release = '1.36.0'

        if sys.platform.startswith('linux'):
            platform = 'linux'
            url = f'https://github.com/aria2/aria2/releases/download/release-{release}/aria2-{release}-aarch64-linux-android-build1.zip'
            local_platform_path = os.path.join(bin_dir, platform)
            local_driver_path = os.path.join(local_platform_path, 'geckodriver')
            var_separator = ':'
        elif sys.platform.startswith('win'):
            platform = 'win'
            url = f'https://github.com/aria2/aria2/releases/download/release-{release}/aria2-{release}-win-64bit-build1.zip'
            local_platform_path = os.path.join(bin_dir, platform)
            local_driver_path = os.path.join(local_platform_path, 'aria2c.exe')
            var_separator = ';'
        elif sys.platform == 'darwin':
            platform = 'mac'
            url = 'https://github.com/aria2/aria2/releases/download/release-1.35.0/aria2-1.35.0-osx-darwin.tar.bz2'
            local_platform_path = os.path.join(bin_dir, platform)
            local_driver_path = os.path.join(local_platform_path, 'geckodriver')
            var_separator = ':'
        else:
            raise RuntimeError('Could not determine your OS')

        if not os.path.isdir(bin_dir):
            os.mkdir(bin_dir)

        if not os.path.isdir(local_platform_path):
            os.mkdir(local_platform_path)

        if not os.path.isfile(local_driver_path):
            print('Downloading aria2 ...', file=sys.stderr)
            data_resp = requests.get(url, stream=True)
            file_name = url.split('/')[-1]
            tgt_file = os.path.join(local_platform_path, file_name)

            with open(tgt_file, 'wb') as f:
                for chunk in data_resp.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            if file_name.endswith('.zip'):
                with zipfile.ZipFile(tgt_file, 'r') as f_zip:
                    f_zip.extractall(local_platform_path)
            else:
                with tarfile.open(tgt_file, 'r') as f_gz:
                    f_gz.extractall(local_platform_path)
            
            # copy aria2c binary to bin/(win/linux/mac)folder
            for current_directory, subdirectories, files in os.walk(local_platform_path):
                for file_name in files:
                    if file_name.startswith('aria2c'):
                        file_path = os.path.join(current_directory, file_name)
                        shutil.copy2(file_path, local_platform_path)
                        # print(f"The file {file_name} has been copied to the parent folder.")


            if not os.access(local_driver_path, os.X_OK):
                os.chmod(local_driver_path, 0o744)

            os.remove(tgt_file)
        
        if 'PATH' not in os.environ:
            os.environ['PATH'] = local_platform_path
        elif local_driver_path not in os.environ['PATH']:
            os.environ['PATH'] = local_platform_path + var_separator + os.environ['PATH']


if __name__ == "__main__":
       
    dl = Downloader(external_downloader = 'aria2')
    dl.check_aria2()
    dl.load_data()
    dl.dl_course()
    # dl.make_zip_file()