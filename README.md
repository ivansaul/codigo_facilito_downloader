![Repo Banner](https://i.imgur.com/8mIVJuc.png)

# Descarga automatizada de Codigo Facilito

Descarga automática de los cursos de Codigo Facilito con un script creado en Python utilizando `yt-dlp` como un subproceso. Abajo dejo ejemplos de cómo se debe utilizar y las herramientas necesarias.

![GitHub repo size](https://img.shields.io/github/repo-size/ivansaul/codigo_facilito_downloader)
![GitHub stars](https://img.shields.io/github/stars/ivansaul/codigo_facilito_downloader)
![GitHub forks](https://img.shields.io/github/forks/ivansaul/codigo_facilito_downloader)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 
[![Discord](https://img.shields.io/badge/-Discord-424549?style=social&logo=discord)](https://discord.gg/b72uAVBz6b)

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

### **Windows**

> **Nota:** Asegurate de tener instalados [Python][python], [Firefox][firefox] , [yt-dlp][yt-dlp] y [ffmpeg][ffmpeg].

```bash
pip install -U yt-dlp
```

## Instrucciones [[ver demo]][demo]

1. Ejecuta el script `facilito.py` para obtener las url de los videos. 

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

2. Finalmente para descargar los vídeos ejecute.

```bash
python downloader.py
```

Por defecto, los videos se descargarán automáticamente en una carpeta con el mismo nombre del curso, con la mejor calidad existente(`best`) y usando `aria2` como gestor de descargas. Para personalizar la descarga puedes usar las siguientes opciones.

```bash
Usage: python downloader.py [OPTIONS]

Options:
  -d [yt-dlp|wget|aria2]      Select the external downloader (yt-dlp, wget, or
                              aria2). Default: aria2.
  -q [360|480|720|1080|best]  Select the video quality (360, 480, 720, 1080 or
                              best). Default: best
  --help                      Show this message and exit.

Examples: 
  python downloader.py -q 1080
  python downloader.py -d yt-dlp
  python downloader.py -d yt-dlp -q 720
  python downloader.py --help
```

> **Nota:** Si por algun motivo se cancela la descarga, vuelve a ejecutar `python downloader.py [OPTIONS]` para que retome la descarga.


Prueba JJ para github a repo ivan

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
