<!-- markdownlint-disable MD033 MD036 MD041 MD045 MD046 -->
<div align="center">
    <img width="150" src="https://i.imgur.com/dca7pcI.png" alt="Coco Logo">
</div>
<div align="center">
    <img width="350" src="https://i.imgur.com/tZhUf6Y.png" alt="Coco Logo">
</div>
<div align="center">

<h1 style="border-bottom: none">
    <b><a href="https://github.com/ivansaul/codigo_facilito_downloader">Codigo Facilito Downloader</a></b>
</h1>

Descarga automatizada de los cursos de ***`Codigo Facilito`***<br />
con un script creado con ***`Python`*** y ***`Playwright`***.

![GitHub repo size](https://img.shields.io/github/repo-size/ivansaul/codigo_facilito_downloader)
![GitHub stars](https://img.shields.io/github/stars/ivansaul/codigo_facilito_downloader)
![GitHub forks](https://img.shields.io/github/forks/ivansaul/codigo_facilito_downloader)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<a href="https://discord.gg/tDvybtJ7y9">
    <img alt="Discord Server" height="50" src="https://cdn.jsdelivr.net/npm/@intergrav/devins-badges@3/assets/cozy/social/discord-plural_vector.svg">
</a>

</div>

---

![coco-demo](https://github.com/ivansaul/codigo_facilito_downloader/assets/15005581/b3029dda-c5ab-4cd9-97d3-acc61f3be3a0)

## TODO

¡Contribuciones son bienvenidas!

- [ ] Improve documentation
- [ ] Implement custom progress bar
- [ ] Improve error handling
- [ ] Write tests
- [ ] Add support for bootcamp

## Instalación | Actualización

Para [`instalar` | `actualizar` ], ejecuta el siguiente comando en tu terminal:

```console
pip install -U git+https://github.com/ivansaul/codigo_facilito_downloader.git
```

Instala las dependencias de `playwright`:

```console
playwright install chromium
```

> [!IMPORTANT]
> El script utiliza ***`ffmpeg`***, como un subproceso, así que asegúrate de tener instalado y actualizado.

<details>

<summary>Tips & Tricks</summary>

## FFmpeg Instalación

### Ubuntu / Debian

```console
sudo apt install ffmpeg -y
```

### Arch Linux

```console
sudo pacman -S ffmpeg
```

### Windows [[Tutorial]][ffmpeg-youtube]

Puedes descargar la versión de `ffmpeg` para Windows desde [aquí][ffmpeg]. o algún gestor de paquetes como [`Scoop`][scoop] o [`Chocolatey`][chocolatey].

```console
scoop install ffmpeg
```

</details>

## Guía de uso

El `CLI` proporciona los siguientes comandos:

### Login

Puedes iniciar sesión de dos formas:

#### Email | Facebook | Google

```console
facilito login
```

#### Cookies

Este método solo se recomienda si tienes problemas de autenticación mediante el método anterior.

```console
facilito set-cookies path/to/cookies.json
```

<details>

<summary>Tips & Tricks</summary>

## Exportar las cookies

1. Instala la extensión de Chrome [***`GetCookies`***][cookies-extension].
2. Inicia sesión en Código Facilito utilizando el navegador Chrome.
3. Recarga la página.
4. Exporta las cookies en formato `json` desde la extensión de Chrome.

</details>

### Logout

Elimina la sesión almacenada localmente de Código Facilito.

```console
facilito logout
```

### Descargar

Descarga un curso, video o lección de Código Facilito.

```console
facilito download <url> [OPCIONES]
```

Opciones:

- `--quality`, `-q`: Especifica la calidad del video (por defecto: `MAX`). Opciones disponibles: `[max|1080p|720p|480p|360p|min]`.
- `--override`, `-w`: Sobrescribe el archivo existente si existe (por defecto: `False`).
- `--threads`, `-t`: Número de hilos a utilizar (por defecto: `10`).

> [!TIP]
> Para visualizar todas las opciones disponibles, ejecuta `facilito download --help`.

Ejemplos:

```console
facilito download https://codigofacilito.com/cursos/docker
```

```console
facilito download URL -q 720p -t 5
```

> [!IMPORTANT]
> Asegúrate de estar logueado antes de intentar descargar los cursos.

<br>

> [!TIP]
> Si por algún motivo se cancela la descarga, vuelve a ejecutar `facilito download <url>` para retomar la descarga.

<br>

> [!NOTE]
> La versión actual es inestable y puede contener errores. Si necesitas una versión más estable, considera usar la versión anterior [***[VER]***][previous-version].

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

[scoop]:https://scoop.sh/
[ffmpeg]: https://ffmpeg.org
[chocolatey]: https://community.chocolatey.org
[ffmpeg-youtube]: https://youtu.be/JR36oH35Fgg?si=Gerco7SP8WlZVaKM
[previous-version]: https://github.com/ivansaul/codigo_facilito_downloader/tree/e39524cf4a925fb036c903b5d82306f9e2088ca6
[cookies-extension]: https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
