![Repo Banner](https://i.imgur.com/I6zFXds.png)

<div align="center">

<h1 style="border-bottom: none">
    <b><a href="#">Codigo Facilito Downloader</a></b>
</h1>

Descarga automatizada de los cursos de `Codigo Facilito `con un script creado en `Python` utilizando `yt-dlp` como un subproceso.

![GitHub repo size](https://img.shields.io/github/repo-size/ivansaul/codigo_facilito_downloader)
![GitHub stars](https://img.shields.io/github/stars/ivansaul/codigo_facilito_downloader)
![GitHub forks](https://img.shields.io/github/forks/ivansaul/codigo_facilito_downloader)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 
[![Discord](https://img.shields.io/badge/-Discord-424549?style=social&logo=discord)](https://discord.gg/tDvybtJ7y9)

</div>

---

## Instalación

El script utiliza **Playwright & Firefox**, así que asegúrate de tener instalado **Firefox browser** en tu ordenador.

```bash
git clone https://github.com/ivansaul/codigo_facilito_downloader.git
cd codigo_facilito_downloader
pip install -r requirements.txt
playwright install-deps
playwright install firefox 
```

### **Linux**

**En Ubuntu:**

```bash
sudo apt update -y
sudo apt install firefox ffmpeg aria2 -y
pip install -U yt-dlp
```

**En Archlinux:**

```bash
sudo pacman -Syu
sudo pacman -S firefox ffmpeg aria2  yt-dlp 
```

### **Windows**

> [!IMPORTANT]
> Asegurate de tener instalados [Python][python], [Firefox][firefox] , [yt-dlp][yt-dlp] y [ffmpeg][ffmpeg].

```bash
# Install Python ...
# Install ffmpeg ...
# Install Firefox ...
pip install -U yt-dlp
```

## Instrucciones

1. Inicia sesión en la plataforma, ve a cualquier video y copia las cookies que te proporciona la siguiente extensión de Chrome, [Get cookies][cookies]. Pégalas en el archivo `cookies.txt`, ubicado en el directorio raíz del script.

```notepad
# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

codigofacilito.com	FALSE	/	TRUE	1699756451	ahoy_visitor	7bd1d2a
.codigofacilito.com	TRUE	/	TRUE	1686280291	__stripe_mid	58110a2
.
.
.
```

2. Ejecuta el script `facilito.py` para obtener las url de los videos. 

```bash
python facilito.py
```

El script te pedira tu correo y contraseña y la url del curso a descargar (la url debe ser de cualquier video del curso)

```bash
Ingresa tus credenciales de Codigo Facilito
Ingresa tu e-mail: tu@email.com
Ingresa tu contraseña: tu_comtraseña
Ingresa la URL del curso a descargar: https://codigofacilito.com/videos/introduccion-al-curso-profesional-de-backend
.
.
.
```

> [!IMPORTANT]
> La url debe ser de un video cualquiera del curso, como se muestra en el ejemplo `https:.../videos/...`

3. Finalmente para descargar los vídeos ejecute.

```bash
python downloader.py
```

Por defecto, los videos se descargarán automáticamente en una carpeta con el mismo nombre del curso, con la mejor calidad existente(`best`) y usando `yt-dlp` como gestor de descargas. Para personalizar la descarga puedes usar las siguientes opciones.

```bash
Usage: python downloader.py [OPTIONS]

Options:
  -d [yt-dlp|wget|aria2]      Select the external downloader (yt-dlp, or aria2). Default: yt-dlp.
  -q [360|480|720|1080|best]  Select the video quality (360, 480, 720, 1080 or best). Default: best
  --help                      Show this message and exit.

Examples: 
  python downloader.py -q 1080
  python downloader.py -d aria2
  python downloader.py -d yt-dlp -q 720
  python downloader.py --help
```

> [!CAUTION]
> Se recomienda utilizar `yt-dlp` en lugar de `aria2` debido a problemas experimentados con este último.

> [!TIP]
> Si por algun motivo se cancela la descarga. Solo actuliza las `cookies.txt` y vuelve a ejecutar `python downloader.py [OPTIONS]` para que retome la descarga.

## Descargas en Lote
Para descargar en lote debes generar el archivo `data.json` siguiendo el paso 2 de las instrucciones, luego debes copiar el archivo data.json a la carpeta data (si no existe creala). 
El formato seria el siguiente:
```
.
└── codigo-facilito-downloader/
    ├── facilito.py
    ├── bulk-downloader.py
    ├── data.json <-- Generado por facilito.py
    └── data <-- Carpeta para descargar en lote/
        ├── 1. data.json <-- Taller para crear un chat con Flutter y Firebase
        ├── 2. data.json <-- Taller de introducción a Jetpack compose
        └── 3. data.json <-- Taller Práctico - Clases del Bootcamp Next.js
```
Utiliza el formato numerado para dar prioridad al curso  que deseas bajar primero. El script buscará la carpeta "data" y recorrerá todos los archivos `.json` que se encuentren en el.
###  Ejecutando Bulk Downloader
Para descargar solo debes ejecutar el comando:
```bash
Usage: python bulk-downloader.py [OPTIONS]

Options:
  -d [yt-dlp|wget|aria2]      Select the external downloader (yt-dlp, or aria2). Default: yt-dlp.
  -q [360|480|720|1080|best]  Select the video quality (360, 480, 720, 1080 or best). Default: best
  --help                      Show this message and exit.

Examples: 
  python bulk-downloader.py -q 1080
  python bulk-downloader.py -d aria2
  python bulk-downloader.py -d yt-dlp -q 720
  python bulk-downloader.py --help
```

## Bootcamp (Improve)
Ejecutar el script `bootcamp.py` para obtener la información del bootcamp.
Se guardara en el archivo `bootcamp.json` luego puedes descargarlas siguiendo los pasos de la sección anterior.
```bash
python bootcamp.py
Enter bootcamp url ex: https://codigofacilito.com/programas/python-avanzado
```

# **Aviso de Uso**

Este proyecto se realiza con fines exclusivamente educativos y de aprendizaje. El código proporcionado se ofrece "tal cual" sin ninguna garantía de su funcionamiento o idoneidad para ningún propósito específico.

No me hago responsable por cualquier mal uso, daño o consecuencia que pueda surgir del uso de este proyecto. Es responsabilidad del usuario utilizarlo de manera adecuada y dentro de los límites legales y éticos.

# Descubre Más

Aquí tienes una lista de algunos de mis otros repositorios. ¡Échales un vistazo!

[![Bookmark Style Card](https://svg.bookmark.style/api?url=https://github.com/ivansaul/codigo_facilito_downloader&mode=light&style=horizontal)](https://github.com/ivansaul/codigo_facilito_downloader)
[![Bookmark Style Card](https://svg.bookmark.style/api?url=https://github.com/ivansaul/platzi-downloader&mode=light&style=horizontal)](https://github.com/ivansaul/platzi-downloader)
[![Bookmark Style Card](https://svg.bookmark.style/api?url=https://github.com/ivansaul/terabox_downloader&mode=light&style=horizontal)](https://github.com/ivansaul/terabox_downloader)
[![Bookmark Style Card](https://svg.bookmark.style/api?url=https://github.com/ivansaul/personal-portfolio&mode=light&style=horizontal)](https://github.com/ivansaul/personal-portfolio)
[![Bookmark Style Card](https://svg.bookmark.style/api?url=https://github.com/ivansaul/flutter_todo_app&mode=light&style=horizontal)](https://github.com/ivansaul/flutter_todo_app)
[![Bookmark Style Card](https://svg.bookmark.style/api?url=https://github.com/ivansaul/Flutter-UI-Kit&mode=light&style=horizontal)](https://github.com/ivansaul/Flutter-UI-Kit)


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
[cloudflare-branch]:https://github.com/ivansaul/codigo_facilito_downloader/tree/feature/cloudflare
