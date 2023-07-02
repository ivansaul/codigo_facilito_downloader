import os
import sys
import json
import shutil
import tarfile
import zipfile
import requests
from typing import Dict, List, Any

def read_json(file_path) -> Dict[Any, Any]:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = json.load(file)
    return content


def write_json(data:Dict[Any, Any], file_path:str) -> None:
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent = 4, ensure_ascii = True)


def input_credentials() -> List[str]:

    # Check if the credentials file exists
    if not os.path.exists("credentials.json"):
        print('Ingresa tus credenciales de Codigo Facilito')
        while True:
            username = input('Ingresa tu e-mail: ')
            confirm_username = input('Confirma tu e-mail: ')
            
            password = input('Ingresa tu contraseña: ')
            confirm_password = input('Confirma tu contraseña: ')

            if username == confirm_username and password == confirm_password:
                credentials = {
                    "username": username,
                    "password": password
                }
                
                write_json(data=credentials, file_path='credentials.json')

                print("Las credenciales se han guardado exitosamente en 'credentials.json'")
                return list(credentials.values())
            else:
                print("Las credenciales no coinciden. Por favor, intenta nuevamente.")
    else:
        print("Leyendo las credenciales ...")
        saved_credentials = read_json('credentials.json')
        return list(saved_credentials.values())


def check_gecko_driver():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bin_dir = os.path.join(script_dir, 'bin') 
    release = 'v0.33.0'
    if sys.platform.startswith('linux'):
        platform = 'linux'
        url = f'https://github.com/mozilla/geckodriver/releases/download/{release}/geckodriver-{release}-linux64.tar.gz'
        local_platform_path = os.path.join(bin_dir, platform)
        local_driver_path = os.path.join(local_platform_path, 'geckodriver')
        var_separator = ':'
    elif sys.platform == 'darwin':
        platform = 'mac'
        url = f'https://github.com/mozilla/geckodriver/releases/download/{release}/geckodriver-{release}-macos.tar.gz'
        local_platform_path = os.path.join(bin_dir, platform)
        local_driver_path = os.path.join(local_platform_path, 'geckodriver')
        var_separator = ':'
    elif sys.platform.startswith('win'):
        platform = 'win'
        url = f'https://github.com/mozilla/geckodriver/releases/download/{release}/geckodriver-{release}-win64.zip'
        local_platform_path = os.path.join(bin_dir, platform)
        local_driver_path = os.path.join(local_platform_path, 'geckodriver.exe')
        var_separator = ';'
    else:
        raise RuntimeError('Could not determine your OS')
    if not os.path.isdir(bin_dir):
        os.mkdir(bin_dir)
    if not os.path.isdir(local_platform_path):
        os.mkdir(local_platform_path)
    if not os.path.isfile(local_driver_path):
        print('Downloading gecko driver...', file=sys.stderr)
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
        if not os.access(local_driver_path, os.X_OK):
            os.chmod(local_driver_path, 0o744)
        os.remove(tgt_file)
    
    if 'PATH' not in os.environ:
        os.environ['PATH'] = local_platform_path
    elif local_driver_path not in os.environ['PATH']:
        os.environ['PATH'] = local_platform_path + var_separator + os.environ['PATH']


def check_aria2():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bin_dir = os.path.join(script_dir, 'bin') 
    release = '1.36.0'
    if sys.platform.startswith('linux'):
        platform = 'linux'
        url = f'https://github.com/aria2/aria2/releases/download/release-{release}/aria2-{release}-aarch64-linux-android-build1.zip'
        local_platform_path = os.path.join(bin_dir, platform)
        local_driver_path = os.path.join(local_platform_path, 'aria2c')
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
        local_driver_path = os.path.join(local_platform_path, 'aria2c')
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


# if __name__ == "__main__":
#     input_credentials()
    