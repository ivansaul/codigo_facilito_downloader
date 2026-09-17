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

Descarga automatizada de los cursos de **_`Codigo Facilito`_**<br />
con un script creado con **_`Python`_** y **_`Playwright`_**.

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

## Instalación | Actualización

### Con **`poetry`** **(recomendado)**

<details>

<summary>Instrucciones</summary>

## Instalación

1. Instala `poetry` en tu sistema:

   ```console
   pip install poetry
   ```

2. Clona el repositorio:

   ```console
   git clone https://github.com/ivansaul/codigo_facilito_downloader.git
   ```

3. Entra al directorio del repositorio:

   ```console
   cd codigo_facilito_downloader
   ```

4. Instala el paquete:

   ```console
   poetry install
   ```

5. Instala las dependencias de `playwright`:

   ```console
   playwright install chromium
   ```

## Actualización

1. Entra al directorio del repositorio:

   ```console
   cd codigo_facilito_downloader
   ```

2. Actualiza el repositorio:

   ```console
   git reset --hard HEAD
   git pull
   ```

3. Actualiza el paquete:

   ```console
   poetry install
   ```

4. Actualiza las dependencias de `playwright`:

   ```console
   playwright install chromium
   ```

</details>

### Con **`pip`**

<details>

<summary>Instrucciones</summary>

## Instalación y actualización

1. Instala el paquete:

   ```console
   pip install -U git+https://github.com/ivansaul/codigo_facilito_downloader.git
   ```

2. Instala las dependencias de `playwright`:

   ```console
   playwright install chromium
   ```

</details>

<br>

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

1. Instala la extensión de Chrome [**_`GetCookies`_**][cookies-extension].
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

Descarga un bootcamp, curso, video o lección de Código Facilito.

```console
facilito download <url> [OPCIONES]
```

Opciones:

- `--quality`, `-q`: Especifica la calidad del video (por defecto: `max`). Opciones disponibles: `[max|1080p|720p|480p|360p|min]`.
- `--override`, `-w`: Sobrescribe el archivo existente si existe (por defecto: `False`).
- `--threads`, `-t`: Número de hilos a utilizar (por defecto: `10`).
- Opciones de rate limiting (`--request-delay`, `--request-jitter`, `--download-delay`, `--retry/--no-retry`, `--max-retries`, `--retry-base-delay`, `--retry-max-delay`, `--retry-after-max`, `--block-detection/--no-block-detection`, `--config`): ver [Rate limiting](#rate-limiting).
- `--browser`: Navegador a lanzar (`auto`, `chrome`, `msedge`, `chromium`); ver [Navegador](#navegador).
- `--window`: Modo de ventana (`offscreen`, `visible`, `headless`); ver [Navegador](#navegador).

> [!TIP]
> Para visualizar todas las opciones disponibles, ejecuta `facilito download --help`.

Ejemplos:

**Descargar un bootcamp completo:**

```console
facilito download https://codigofacilito.com/programas/ingles-conversacional
```

**Descargar un curso:**

```console
facilito download https://codigofacilito.com/cursos/docker
```

**Descargar con opciones personalizadas:**

```console
facilito download URL -q 720p -t 5
```

> [!IMPORTANT]
> Asegúrate de estar logueado antes de intentar descargar los cursos.

<br>

> [!IMPORTANT]
> El script utiliza **_`ffmpeg`_**, como un subproceso, así que asegúrate de tener instalado y actualizado.

<br>

> [!TIP]
> Si por algún motivo se cancela la descarga, vuelve a ejecutar `facilito download <url>` para retomar la descarga.

<br>

> [!NOTE]
> La versión actual es inestable y puede contener errores. Si necesitas una versión más estable, considera usar la versión anterior [**_[VER]_**][previous-version].

### Rate limiting

El downloader incluye protecciones para evitar ser bloqueado por el servidor (HTTP `429`, retos de Cloudflare, errores temporales de `vsd`). Por defecto el ritmo no cambia (`--request-delay 0`, `--download-delay 0`), pero los reintentos con backoff exponencial están activados.

Opciones:

- `--request-delay`: Retardo base en segundos entre peticiones de página (scraping/MHTML). `0` lo desactiva.
- `--request-jitter`: Jitter aleatorio en segundos que se suma a `--request-delay`; la espera real es `delay + U(0, jitter)`.
- `--download-delay`: Retardo en segundos entre descargas de video consecutivas. `0` lo desactiva.
- `--retry / --no-retry`: Activa o desactiva los reintentos con backoff exponencial (por defecto: activado).
- `--max-retries`: Número máximo de reintentos tras el primer intento (por defecto: `3`).
- `--retry-base-delay`: Espera base del primer reintento; se duplica por intento (por defecto: `1.0`).
- `--retry-max-delay`: Espera máxima de un backoff calculado (por defecto: `30.0`).
- `--retry-after-max`: Máximo a respetar de un `Retry-After` del servidor; si pide más, se limita y se avisa (por defecto: `60.0`).
- `--block-detection / --no-block-detection`: Detecta respuestas de rate limit/reto (HTTP `429`, Cloudflare `403`) y hace backoff (por defecto: activado).
- `--config`: Ruta al archivo de configuración JSON (por defecto: `Facilito/config.json`).

#### Archivo de configuración

Las mismas opciones se pueden fijar en `Facilito/config.json` (relativo al directorio actual). La precedencia es `CLI > archivo > valor por defecto`. También puedes indicar otra ruta con `--config` o la variable de entorno `FACILITO_CONFIG`.

```json
{
  "request_delay": 0.3,
  "request_jitter": 0.3,
  "download_delay": 1.5,
  "retry_enabled": true,
  "max_retries": 3,
  "retry_base_delay": 1.0,
  "retry_max_delay": 30.0,
  "retry_after_max": 60.0,
  "block_detection_enabled": true
}
```

Puedes partir del archivo de ejemplo [`config.example.json`](./config.example.json), que ya trae la configuración recomendada:

```console
mkdir -p Facilito
cp config.example.json Facilito/config.json
```

O indicar su ruta directamente:

```console
facilito download URL --config config.example.json
```

#### Configuración recomendada

Comando recomendado para un curso o bootcamp completo: espacia lo suficiente para no llamar la atención del servidor sin renunciar a buena velocidad. Los reintentos con backoff y la detección de bloqueos quedan activados por defecto.

```console
facilito download URL \
  --request-delay 0.3 \
  --request-jitter 0.3 \
  --download-delay 1.5
```

Valores recomendados:

| Opción | Valor | Motivo |
|--------|-------|--------|
| `--request-delay` | `0.3` | Separa las navegaciones de scraping sin penalizar mucho el tiempo total. |
| `--request-jitter` | `0.3` | Evita un patrón fijo; además añade aleatoriedad al `--download-delay`. |
| `--download-delay` | `1.5` | Separa descargas de video consecutivas. |
| `--max-retries` | `3` (default) | Suficiente para `429`/`5xx` puntuales. |
| `--retry-base-delay` / `--retry-max-delay` | `1` / `30` (default) | Backoff exponencial acotado. |
| `--retry-after-max` | `60` (default) | Respeta al servidor sin bloquearte horas. |
| `--threads` | `10` (default; usa `5`–`8` si te bloquean) | Controla el paralelismo interno de `vsd`. |

Si empiezas a recibir `429`/`403`, sube el espaciado y baja los hilos:

```console
facilito download URL \
  --request-delay 0.5 --request-jitter 0.5 \
  --download-delay 3 \
  --threads 6
```

Desactivar los reintentos:

```console
facilito download URL --no-retry
```

> [!IMPORTANT]
> Si se agotan los reintentos, la ejecución se detiene con un error (no se salta la unidad). `--threads` sigue controlando el paralelismo interno de `vsd` y puede provocar throttling por IP aunque el bucle externo esté regulado.

### Navegador

Por defecto se lanza **Google Chrome** (o Edge) si está instalado, porque el Chromium que incluye Playwright **no trae códecs propietarios (H.264/AAC)** y el reproductor muestra `No compatible source was found for this media.`. Si no encuentra Chrome/Edge, cae al Chromium incluido: la descarga con `vsd` sigue funcionando, pero la reproducción dentro del navegador automatizado puede fallar y, en algunos players, eso impide que se solicite el `.m3u8` y se capture la URL.

```console
facilito download URL --browser chrome
```

Valores: `auto` (por defecto), `chrome`, `msedge`, `chromium`. También puedes fijarlo con la variable de entorno `FACILITO_BROWSER`:

```console
FACILITO_BROWSER=chrome facilito download URL
```

Modo de ventana (`--window`, o `FACILITO_WINDOW`):

- `offscreen` (por defecto en `download`): abre Chrome headful pero **fuera de pantalla y minimizado**, así no aparece ni roba el foco. Mantiene la efectividad (Cloudflare y la captura del `.m3u8` siguen funcionando), a diferencia de `headless`.
- `visible`: ventana normal en pantalla (útil para depurar).
- `headless`: sin ventana, pero **Cloudflare suele bloquearlo**; no recomendado.

`facilito login` siempre abre una ventana visible para que puedas autenticarte.

Durante toda la ejecución se reutiliza **una única pestaña** en esa ventana (no se abre/cierra una por unidad), así que la ventana como mucho aparece una vez y puedes ignorarla.

```console
facilito download URL --window visible
FACILITO_WINDOW=visible facilito download URL
```

### YouTube

Algunas lecciones, en lugar del reproductor HLS, incrustan un video de YouTube (`youtube.com/embed/...`, `youtube-nocookie.com/embed/...`, `youtu.be/...` o `watch?v=...`). El downloader los **detecta automáticamente** y los descarga con [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) al mismo `.mp4` del resto de videos, respetando `--quality`, `--override` y los reintentos/pacing.

`yt-dlp` es una dependencia del proyecto; si instalaste con `poetry install` ya está disponible. Si no, instálalo con:

```console
pip install yt-dlp
```

Mapeo de calidad: `max` → la mejor disponible, `min` → la peor, y `1080p|720p|480p|360p` → la mejor que no supere esa altura (si no existe, la mejor disponible).

```console
facilito download https://codigofacilito.com/cursos/go-profesional -q 720p
```

> [!NOTE]
> No se descargan playlists, subtítulos ni metadatos de YouTube. Videos privados, eliminados, con embed deshabilitado o bloqueados por región fallan con un mensaje claro en el log. La ruta HLS (vídeos normales con `vsd`) no cambia.

## Reanudar y fallos

Cada curso/bootcamp guarda su progreso en `Facilito/<slug>/.facilito.json` (manifest por curso). Gracias a eso:

- Si el curso **ya se completó** y los archivos siguen ahí, volver a ejecutar `facilito download <url>` no vuelve a recorrerlo (ni descarga ni navega unidades). Usa `--override` para rehacerlo todo.
- Si hubo **fallos**, un re-run normal los **reintenta automáticamente** sin volver a navegar/descargar las unidades que ya estaban bien.
- `--retry-failed` reintenta **solo** los fallos registrados, sin recorrer el curso.
- `--status` muestra el estado (completado / en progreso) y los fallos pendientes.

```console
# Ver progreso y fallos
facilito download https://codigofacilito.com/cursos/go-profesional --status

# Reintentar solo lo que falló
facilito download https://codigofacilito.com/cursos/go-profesional --retry-failed

# Rehacer todo desde cero
facilito download https://codigofacilito.com/cursos/go-profesional --override
```

> [!NOTE]
> El estado es por curso y por máquina. Si borras los archivos de salida, el manifest se re-verifica y se vuelve a recorrer lo que falte. Si el curso añade unidades nuevas upstream, no se detectan con el manifest en `completed`; usa `--override` para refrescar.

## Cómo contribuir

¡Todas las contribuciones son bienvenidas!. Antes de enviar cambios, revisa la guía [CONTRIBUTING.md](./CONTRIBUTING.md) para conocer las pautas del proyecto.

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

[scoop]: https://scoop.sh/
[ffmpeg]: https://ffmpeg.org
[chocolatey]: https://community.chocolatey.org
[ffmpeg-youtube]: https://youtu.be/JR36oH35Fgg?si=Gerco7SP8WlZVaKM
[previous-version]: https://github.com/ivansaul/codigo_facilito_downloader/tree/e39524cf4a925fb036c903b5d82306f9e2088ca6
[cookies-extension]: https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
