#import re
#
#from playwright.async_api import BrowserContext
#
#from ..constants import VIDEO_BASE_URL, VIDEO_M3U8_URL
#from ..errors import VideoError
#from ..models import Video
#from ..utils import is_video
#
#
#async def fetch_video(context: BrowserContext, url: str) -> Video:
#    VIDEO_ID_SELECTOR = "input[name='video_id']"
#    COURSE_ID_SELECTOR = "input[name='course_id']"
#    M3U8_PATTERN = r"\/hls\/.*?\.m3u8"
#
#    if not is_video(url):
#        raise VideoError()
#
#    try:
#        page = await context.new_page()
#        await page.goto(url)
#
#        if m3u8_urls := re.findall(M3U8_PATTERN, await page.content()):
#            url = VIDEO_BASE_URL + m3u8_urls[0]
#
#        else:
#            course_id = await page.locator(COURSE_ID_SELECTOR).first.get_attribute(
#                "value"
#            )
#            video_id = await page.locator(VIDEO_ID_SELECTOR).first.get_attribute(
#                "value"
#            )
#
#            if not video_id or not course_id:
#                raise VideoError()
#
#            url = VIDEO_M3U8_URL.format(course_id=course_id, video_id=video_id)
#
#    except Exception:
#        raise VideoError()
#
#    finally:
#        await page.close()
#
#    return Video(url=url)
#
#import re
#from playwright.async_api import BrowserContext
#from ..constants import VIDEO_BASE_URL, VIDEO_M3U8_URL
#from ..errors import VideoError
#from ..models import Video
#from ..utils import is_video
#
#async def fetch_video(context: BrowserContext, url: str) -> Video:
#    VIDEO_ID_SELECTOR = "input[name='video_id']"
#    COURSE_ID_SELECTOR = "input[name='course_id']"
#    
#    if not is_video(url):
#        raise VideoError()
#
#    page = await context.new_page()
#    bunny_url = None
#
#    # Escuchador de peticiones (Request) en lugar de Response para mayor rapidez
#    async def intercept_request(request):
#        nonlocal bunny_url
#        if ".m3u8" in request.url:
#            bunny_url = request.url
#            print(f"\n[DEBUG] ¡URL Cazada!: {bunny_url[:60]}...")
#
#    page.on("request", intercept_request)
#
#    try:
#        # 1. Navegamos
#        await page.goto(url, wait_until="networkidle")
#        
#        # 2. Forzamos un click en el centro de la página por si el reproductor 
#        # necesita una interacción para cargar el stream (Lazy Load)
#        try:
#            await page.mouse.click(500, 400)
#        except:
#            pass
#
#        # 3. Esperamos un poco más (6 segundos) para que BunnyCDN firme el token
#        await page.wait_for_timeout(6000)
#
#        # Si no cazamos nada por red, intentamos el método de los selectores (Fallback)
#        if not bunny_url:
#            try:
#                course_id = await page.locator(COURSE_ID_SELECTOR).first.get_attribute("value")
#                video_id = await page.locator(VIDEO_ID_SELECTOR).first.get_attribute("value")
#                final_url = VIDEO_M3U8_URL.format(course_id=course_id, video_id=video_id)
#            except:
#                final_url = url
#        else:
#            final_url = bunny_url
#
#    except Exception as e:
#        print(f"[ERROR] Fallo en fetch_video: {e}")
#        raise VideoError()
#    finally:
#        await page.close()
#
#    return Video(url=final_url)

#import re
#from playwright.async_api import BrowserContext
#from ..constants import VIDEO_BASE_URL, VIDEO_M3U8_URL
#from ..errors import VideoError
#from ..models import Video
#from ..utils import is_video
#
#async def fetch_video(context: BrowserContext, url: str) -> Video:
#    VIDEO_ID_SELECTOR = "input[name='video_id']"
#    COURSE_ID_SELECTOR = "input[name='course_id']"
#    
#    if not is_video(url):
#        raise VideoError()
#
#    page = await context.new_page()
#    bunny_url = None
#
#    # Escuchador de peticiones para cazar el token de BunnyCDN
#    async def intercept_request(request):
#        nonlocal bunny_url
#        if ".m3u8" in request.url:
#            bunny_url = request.url
#            print(f"\n[DEBUG] ¡URL Cazada!: {bunny_url[:65]}...")
#
#    page.on("request", intercept_request)
#
#    try:
#        # 1. Cambiamos a 'domcontentloaded' para evitar el Timeout de red infinita
#        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
#        
#        # 2. Intentamos activar el video directamente por JS (más efectivo que el click)
#        try:
#            await page.wait_for_selector("video", timeout=5000)
#            await page.evaluate("document.querySelector('video').play()")
#        except:
#            # Si falla el JS, hacemos click físico como plan B
#            await page.mouse.click(640, 360)
#
#        # 3. Tiempo de gracia para que el token se firme y la petición vuele
#        await page.wait_for_timeout(5000)
#
#        # 4. Lógica de selección de URL
#        if bunny_url:
#            final_url = bunny_url
#        else:
#            # Fallback para cursos antiguos
#            try:
#                course_id = await page.locator(COURSE_ID_SELECTOR).first.get_attribute("value")
#                video_id = await page.locator(VIDEO_ID_SELECTOR).first.get_attribute("value")
#                if course_id and video_id:
#                    final_url = VIDEO_M3U8_URL.format(course_id=course_id, video_id=video_id)
#                else:
#                    final_url = url
#            except:
#                final_url = url
#
#    except Exception as e:
#        print(f"[ERROR] Fallo en fetch_video: {e}")
#        raise VideoError()
#    finally:
#        # Cerramos la página para liberar memoria de Chrome
#        await page.close()
#
#    return Video(url=final_url)



import re
from playwright.async_api import BrowserContext
from ..constants import VIDEO_BASE_URL, VIDEO_M3U8_URL
from ..errors import VideoError
from ..models import Video
from ..utils import is_video

async def fetch_video(context: BrowserContext, url: str) -> Video:
    VIDEO_ID_SELECTOR = "input[name='video_id']"
    COURSE_ID_SELECTOR = "input[name='course_id']"
    
    if not is_video(url):
        raise VideoError()

    page = await context.new_page()
    bunny_url = None

    # Escuchador de peticiones para cazar el token de BunnyCDN
    async def intercept_request(request):
        nonlocal bunny_url
        if ".m3u8" in request.url:
            bunny_url = request.url
            print(f"\n[DEBUG] ¡URL Cazada!: {bunny_url[:65]}...")

    page.on("request", intercept_request)

    try:
        # 1. Navegamos esperando solo la carga inicial del DOM
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # 2. Forzamos la reproducción del elemento de video para gatillar la petición HLS
        try:
            await page.wait_for_selector("video", timeout=5000)
            await page.evaluate("document.querySelector('video').play()")
        except:
            await page.mouse.click(640, 360)

        # 3. Margen de tiempo para asegurar la captura del evento de red
        await page.wait_for_timeout(5000)

        # 4. Procesamiento de la URL final
        if bunny_url:
#            # Engañamos al validador estricto de VSD forzando que termine con extensión .m3u8
#            final_url = bunny_url + "&ext=.m3u8"
#
#Importante: Limpiar el truco anterior en video.py de collectors
#
#Como ya no necesitamos "engañar" a la URL porque el comando vsd download procesará la URL directamente sin importar sus parámetros, asegúrate de que en src/facilito/collectors/video.py quitamos el + "&ext=.m3u8".
#
#Debería quedar limpio, asignando directamente la URL cazada:

            final_url = bunny_url
        else:
            # Fallback tradicional para los cursos con la infraestructura anterior
            try:
                course_id = await page.locator(COURSE_ID_SELECTOR).first.get_attribute("value")
                video_id = await page.locator(VIDEO_ID_SELECTOR).first.get_attribute("value")
                if course_id and video_id:
                    final_url = VIDEO_M3U8_URL.format(course_id=course_id, video_id=video_id)
                else:
                    final_url = url
            except:
                final_url = url

    except Exception as e:
        print(f"[ERROR] Fallo en fetch_video: {e}")
        raise VideoError()
    finally:
        await page.close()

    return Video(url=final_url)
