# -*- coding: utf-8 -*-
"""
==============================================================================
PLANTILLA: ESCENAS CON VIDEOS DE STOCK PEXELS (VERSIÓN SHORTS)
==============================================================================
Conserva tu lógica de bucle ping-pong para que no se note el corte del
presentador. Ajusta los videos de Pexels para llenar el marco 9:16.
"""

import os
import logging
import subprocess
import textwrap
import uuid
from config import *

logger = logging.getLogger(__name__)

def formatear_texto(texto, max_chars):
    if not texto:
        return ""
    texto = texto.replace("\\n", " ").replace("\n", " ") 
    texto = " ".join(texto.split()) 
    texto = texto.replace("'", "\u2019").replace(":", "\:") 
    wrapper = textwrap.TextWrapper(width=max_chars)
    word_list = wrapper.wrap(text=texto)
    if len(word_list) > 4:
        return "\n".join(word_list[:4]) + "..." 
    return "\n".join(word_list)

def renderizar_escena_pexels(termino, overlay_path, audio_tts_path, bgm_path, sfx_path, texto, output_path, unique_id):
    import background_fetcher
    
    logger.info(f"  [Pexels Short] Buscando video para: '{termino}'...")
    
    fondo_path = os.path.join(TEMP_VIDEO_DIR, f"pexels_bg_{unique_id}.mp4")
    fondo_path = background_fetcher.obtener_video_stock(termino, fondo_path)
    
    if not fondo_path:
        fondo_path = os.path.join(ASSETS_DIR, "images", "default_news_bg.jpg")
        logger.warning(f"  [Pexels Short] Falló la descarga. Usando fondo por defecto.")
    
    if not os.path.exists(fondo_path) or not os.path.exists(overlay_path) or not os.path.exists(audio_tts_path):
        logger.error("  [Pexels Short] Faltan archivos clave para ensamblar la escena.")
        return False

    filename = os.path.basename(overlay_path)
    config = get_layout_config(filename)
    
    clean_text = formatear_texto(texto, config["max_letras_por_linea"])
    x, y = config["texto_x"], config["texto_y"]
    color, size = config["color"], config["font_size"]
    shadow = "bordercolor=black:borderw=2" 

    texto_path = os.path.join(TEMP_VIDEO_DIR, f"txt_pex_{uuid.uuid4().hex[:6]}.txt").replace('\\', '/')
    if clean_text:
        with open(texto_path, "wb") as f:
            f.write(clean_text.encode("utf-8"))

    es_video_fondo = fondo_path.lower().endswith(('.mp4', '.mov', '.avi'))
    cmd = ["ffmpeg", "-y"]

    if es_video_fondo:
        cmd.extend(["-stream_loop", "-1", "-i", fondo_path])
        # Cortamos el video Pexels para llenar el 9:16 perfectamente
        fondo_filtro_complex = (
            f"[0:v]format=yuv420p,fps=12,"
            f"scale={RESOLUTION_W}:{RESOLUTION_H}:force_original_aspect_ratio=increase,"
            f"crop={RESOLUTION_W}:{RESOLUTION_H}:(iw-ow)/2:(ih-oh)/2[bg];"
        )
    else:
        cmd.extend(["-loop", "1", "-framerate", "12", "-i", fondo_path])
        # Magia vertical para el default: blur + nitidez + zoom suave
        fondo_filtro_complex = (
            f"[0:v]scale={RESOLUTION_W}:{RESOLUTION_H}:force_original_aspect_ratio=increase,crop={RESOLUTION_W}:{RESOLUTION_H}:(iw-ow)/2:(ih-oh)/2,boxblur=20:5[bg_blur];"
            f"[0:v]scale={RESOLUTION_W}:-1[img_sharp];"
            f"[bg_blur][img_sharp]overlay=0:(H-h)/2[combined];"
            f"[combined]zoompan=z='min(zoom+0.0005,1.2)':d=450:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={RESOLUTION_W}x{RESOLUTION_H}:fps=12[bg];"
        )

    cmd.extend(["-stream_loop", "-1", "-i", overlay_path])
    cmd.extend(["-i", audio_tts_path])

    # El filtro ping-pong inverso maravillosamente preservado e integrado a la vertical
    filter_complex = fondo_filtro_complex + (
        f"[1:v]format=yuv420p,split=2[ov1][ov2];"
        f"[ov2]reverse[ov2r];"
        f"[ov1][ov2r]concat=n=2:v=1:a=0[pingpong_ov];"
        f"[pingpong_ov]scale={RESOLUTION_W}:{RESOLUTION_H}[v_scaled];"
        f"[v_scaled]chromakey={CHROMA_COLOR}:{CHROMA_SIMILARITY}:{CHROMA_BLEND}[v_keyed];"
        f"[bg][v_keyed]overlay=0:0:shortest=1[comp];"
    )

    if clean_text:
        font_safe = str(FONT_PATH).replace('\\', '/').replace(':', '\\:')
        txt_safe = str(texto_path).replace('\\', '/').replace(':', '\\:')
        filter_complex += f"[comp]drawtext=fontfile='{font_safe}':textfile='{txt_safe}':fontcolor={color}:fontsize={size}:{shadow}:x={x}:y={y}[vout];"
    else:
        filter_complex += f"[comp]copy[vout];"

    audio_inputs = "[2:a]"
    input_count = 1

    if bgm_path and os.path.exists(bgm_path):
        cmd.extend(["-i", bgm_path])
        audio_inputs += "[3:a]"
        input_count += 1
        
    if sfx_path and os.path.exists(sfx_path):
        cmd.extend(["-i", sfx_path])
        audio_inputs += "[4:a]"
        input_count += 1

    if input_count > 1:
        filter_complex += f"{audio_inputs}amix=inputs={input_count}:duration=first:dropout_transition=2:weights=1 0.1 0.2[aout]"
        audio_map = "-map [aout]"
    else:
        filter_complex = filter_complex.rstrip(';')
        audio_map = "-map 2:a"

    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[vout]", 
        *audio_map.split(),
        "-c:v", "libx264", 
        "-preset", VIDEO_PRESET, 
        "-r", str(FPS),
        "-c:a", "aac", 
        "-b:a", "128k", 
        "-shortest", 
        output_path
    ])

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1024:
            return True
        return False
            
    except Exception as e:
        logger.error(f"  [FFmpeg Pexels Short] Error: {e}")
        return False 
    finally:
        if 'texto_path' in locals() and os.path.exists(texto_path):
            try: os.remove(texto_path)
            except: pass
        if 'fondo_path' in locals() and os.path.exists(fondo_path):
            if "default_news_bg" not in fondo_path:
                try: os.remove(fondo_path)
                except: pass