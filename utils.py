import os
import json
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


# if __name__ == "__main__":
#     input_credentials()
    