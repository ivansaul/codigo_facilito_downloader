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

El script utiliza **Playwright & Firefox & ffmpeg**, así que asegúrate de tener instalados previamente en tu ordenador.

### **Linux**

**En Ubuntu:**

```bash
# Actualiza los repositorios
sudo apt update -y
# Instalar firefox, ffmpeg y pipx
sudo apt install firefox ffmpeg pipx -y
# Agregar pipx al PATH
pipx ensurepath
```

**En Archlinux:**

```bash
# Actualiza los repositorios
sudo pacman -Syu
# Instalar firefox, ffmpeg y pipx
sudo pacman -S firefox ffmpeg python-pipx
# Agregar pipx al PATH
pipx ensurepath
```

### **Windows**

> [!IMPORTANT]
> Los pasos que se muestran, son a través de [Scoop][scoop].

```bash
# Instalar Python
scoop bucket add main
scoop install python
# Instalar Firefox
scoop bucket add extras
scoop install extras/firefox
# Instalar ffmpeg
scoop bucket add main
scoop install main/ffmpeg
# Instalar pipx
scoop bucket add main
scoop install main/pipx
# Agrega pipx al PATH
pipx ensurepath
```

### **MacOS**

```bash
# Actualiza los repositorios
brew update
# Instalar firefox, ffmpeg y pipx
brew install firefox ffmpeg pipx
# Agregar pipx al PATH
pipx ensurepath
```

## Instrucciones

1. Clona el repositorio

```bash
# Clone el repositorio
git clone https://github.com/ivansaul/codigo_facilito_downloader.git
# Ir al directorio
cd codigo_facilito_downloader
```

2. Instala sus dependencias y activa el entorno virtual

```bash
# Instala poetry
pipx install poetry
# Instala las dependencias
poetry install
# Activa el entorno virtual
poetry shell
```

3. Iniciar sesión a través de la consola con tus credenciales de Codigo Facilito.

```console
$ python coco.py login

What's your email?: test@email.com    
Confirm your email?: test@email.com
What's your password?: facilito123
Confirm your password?: facilito123
```

4. Descarga un video o un curso

```bash
$ python coco.py download

Url: https://codigofacilito.com/cursos/flutter-profesional
Quality (best, 1080, 720, 480, 360, worst) [best]: best
⠹ Processing...
⠹ Downloading...
✓ Done!
```

```bash
$ python coco.py download

Url: https://codigofacilito.com/videos/icon
Quality (best, 1080, 720, 480, 360, worst) [best]: 480
⠹ Processing...
⠹ Downloading...
⠹ Icon  ...
✓ Done!
```

> [!IMPORTANT]
> Por defecto, el script descarga los videos con la mejor calidad disponible(best), pero puedes elegir entre [worst, 360, 480, 720, 1080 o best].

> [!IMPORTANT]
> Revisa los logs(`cli.log`) de la consola para ver un registro de los videos que por algún motivo no se pudieron descargar.

> [!TIP]
> Si por algun motivo se cancela la descarga. Puedes retomarlo con el comando `python coco.py download`

## Contribuidores

<a href="https://github.com/ivansaul/codigo_facilito_downloader/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ivansaul/codigo_facilito_downloader" />
</a>

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
[scoop]:https://scoop.sh/
