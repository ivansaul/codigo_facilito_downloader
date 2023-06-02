# Descarga automatizada de Codigo Facilito

Descarga automática de los cursos de Codigo Facilito con un script creado en Python utilizando `yt-dlp` como un subproceso. Abajo dejo ejemplos de cómo se debe utilizar y las herramientas necesarias. 

## Instalación

El script utiliza **Selenium & Firefox (Gecko driver)**, así que asegúrate de tener instalado **Firefox browser** en tu ordenador.

```bash
git clone https://github.com/ivansaul/codigo_facilito_downloader.git
cd codigo_facilito_downloader
pip install -r requirements.txt
```

### **Linux**

**En Ubuntu:**

```bash
sudo apt update -y
sudo apt install firefox firefox-geckodriver ffmpeg aria2 -y
pip install -U yt-dlp
```

**En Archlinux:**

```bash
sudo pacman -Syu
sudo pacman -S firefox geckodriver ffmpeg aria2  yt-dlp 
```

## Instrucciones [[ver demo]][demo]

1. Inicia sesion en la plataforma y copia las cookies que te propociona la siguiente extension de Chrome [Get cookies][cookies] y pegalos en archivo `cookies.txt` que se encuentra en el directorio de raiz del script.

```notepad
# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

codigofacilito.com	FALSE	/	TRUE	1699756451	
.
.
.
```

2. Ejecuta el script `facilito.py` para obtener las url de los vides. 

```bash
python facilito.py
```

El script te pedira tu correo y contraseña y la url del curso a descargar (la url puede ser de cualquier video del curso)

```bash
Ingresa tus credenciales de Codigo Facilito
Ingresa tu e-mail: tu@email.com
Ingresa tu contraseña: tu_comtraseña
Ingresa la URL del curso a descargar: https://codigofacilito.com/videos/introduccion-al-curso-profesional-de-backend
.
.
.
```

3. Finalmente para descargar los vídeos ejecute.

```bash
python downloader.py
```

> **Nota:** Si por algun motivo se cancela la descarga actuliza las `cookies.txt` y vuelve a ejecutar `python downloader.py` para que retome la descarga.

Los videos se descargarán automáticamente en una carpeta con el mismo nombre del curso.


# **Nota**:

### **En Windows:** [[ver demo]][demo]

Los scripts faltan optimizar para que funcionen correctamente. Por lo que se recomienda usar [Github Codespace][codespace] para primero scrapear las url de los videos y para finalmente descargarlas desde windows con [yt-dlp][yt-dlp]. 

1. Crea un fork y en ella un codespace
2. Ejecuta `sh autorun.sh` te creará un archivo json `data.json`, descargalo en la carpeta raiz.
3. Copias y pega las cookies en `cookies.txt`
4. Finalmente ejecuta `python downloader.py`

Asegurate de tener instalados [Python][python] , [yt-dlp][yt-dlp] y [ffmpeg][ffmpeg].


# **Aviso de Uso**

Este proyecto se realiza con fines exclusivamente educativos y de aprendizaje. El código proporcionado se ofrece "tal cual" sin ninguna garantía de su funcionamiento o idoneidad para ningún propósito específico.

No me hago responsable por cualquier mal uso, daño o consecuencia que pueda surgir del uso de este proyecto. Es responsabilidad del usuario utilizarlo de manera adecuada y dentro de los límites legales y éticos.



[cookies]: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc/related
[python]: https://www.python.org/downloads/
[ffmpeg]: https://ffmpeg.org
[firefox]: https://www.mozilla.org/en-US/firefox/new/
[geckodriver]: https://github.com/mozilla/geckodriver/releases
[yt-dlp]: https://github.com/yt-dlp/yt-dlp/wiki/Installation
[aria2]: https://github.com/aria2/aria2/releases/tag/release-1.36.0
[codespace]: https://github.com/codespaces
[demo]: https://youtu.be/GbQwB0hYvQU
[ffmpeg-win]:https://youtu.be/0zN9oZ98ZgE
