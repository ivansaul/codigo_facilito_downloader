import configparser
import os
import re
import sys
import json
import shutil
import tarfile
import zipfile
import requests
from typing import Dict, List, Any

def write_file(file_path: str, content: str) -> None:
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def read_json(file_path) -> Dict[Any, Any]:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = json.load(file)
    return content

def write_json(data:Dict[Any, Any], file_path:str) -> None:
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent = 4, ensure_ascii = False)

def remove_special_characters(input_string: str) -> str:
    """
    This function cleans the input string by removing special characters and leading/trailing white spaces.
    
    Args:
        input_string (str): The input string to be cleaned.

    Returns:
        str: The cleaned string.
    """
    return re.sub(r'[<>:"/\\|?!¡¿º%&~ª*+=!"#$%&?¿¡[\]{}@]', '', input_string).strip()

def move_folder(src: str, dst: str) -> None:
    check_path(dst)
    shutil.move(src, dst)

def copy_file(src: str, dst: str) -> None:
    shutil.copy(src, dst)

def remove_file(file_path: str) -> None:
    """
    Removes a file if it exists.

    Args:
        file_path (str): The path to the file to remove.

    Returns:
        None
    """
    if os.path.exists(file_path):
        os.remove(file_path)

def path_exists(path: str) -> bool:
    """
    Check if a path exists.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path exists, False otherwise.
    """
    return os.path.exists(path)

def check_path(path: str) -> None:
    """
    Check if a given path exists and create it if it does not.

    Args:
        path (str): The path to check and create if necessary.

    Returns:
        None
    """
    if(not os.path.exists(path)):
        os.makedirs(path, exist_ok=True)

def read_credentials() -> List[str]:
    """
    This function reads the user's email and password from a configuration file.
    
    The configuration file is expected to be in the following format:
    [user]
    email = user@example.com
    password = secret_password
    
    Returns:
        A list containing the email and password as strings.
    """
    config = configparser.ConfigParser()
    config.read('credentials.conf')
    email = config.get('user', 'email')
    password = config.get('user', 'password')
    print([email, password])
    return [email, password]

def check_credentials() -> List[str]:

    # Check if the credentials file exists
    if not os.path.exists("credentials.json"):
        print('Enter your credentials')
        while True:
            email = input('Enter your e-mail: ')
            confirm_email = input('Confirm your e-mail: ')
            
            password = input('Enter your password: ')
            confirm_password = input('Confirm your password: ')

            if email == confirm_email and password == confirm_password:
                credentials = {
                    "username": email,
                    "password": password
                }
                
                write_json(data=credentials, file_path='credentials.json')

                print("The credentials have been successfully saved in 'credentials.json'")
                
                return list(credentials.values())
            else:
                print("The credentials do not match. Please try again.")
    else:
        print("Reading credentials ...")
        saved_credentials = read_json('credentials.json')
        return list(saved_credentials.values())

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

def save_cookies(file_path: str, cookie_data: List[Dict[Any, Any]]) -> None:
    result = []
    for cookie in cookie_data:
        domain = cookie.get('domain', '')
        expiration_date = cookie.get('expires', None)
        path = cookie.get('path', '')
        secure = cookie.get('secure', False)
        name = cookie.get('name', '')
        value = cookie.get('value', '')
        include_sub_domain = domain.startswith('.') if domain else False
        expiry = str(int(expiration_date)) if expiration_date else '0'
        result.append([
            domain,
            str(include_sub_domain).upper(),
            path,
            str(secure).upper(),
            expiry,
            name,
            value
        ])
    netscape_string = "\n".join("\t".join(cookie_parts) for cookie_parts in result)
    write_file(file_path, netscape_string)
    
    
# if __name__ == "__main__":
#     read_credentials()
#     check_credentials()
    