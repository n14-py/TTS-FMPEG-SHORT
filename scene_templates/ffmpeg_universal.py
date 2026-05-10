# -*- coding: utf-8 -*-
"""
==============================================================================
SÚPER MÓDULO FFMPEG UNIVERSAL (VERSIÓN SHORTS)
==============================================================================
Integra tu motor Ken Burns y corrección de color, pero adaptado a la 
pipeline vertical 9:16 (Fondo borroso expandido + Imagen nítida centrada).
"""

import os
import random
import logging
import subprocess
import textwrap
from config import *

logger = logging.getLogger(__name__)

def obtener_duracion_audio(audio_path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
    try:
        resultado = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
        return float(resultado.stdout.strip()) + 0.4
    except Exception:
        return 25.0

def formatear_texto(texto, max_chars):
    if not texto:
        return ""
    texto = texto.replace("\\n", " ").replace("\n", " ") 
    texto = " ".join(texto.split()) 
    texto = texto.replace("'", "\u2019").replace(":", "\:") 
    wrapper = textwrap.TextWrapper(width=max_chars)
    word_list = wrapper.wrap(text=texto)
    # 4 líneas máximo para el formato estrecho de Short
    if len(word_list) > 4:
        return "\n".join(word_list[:4]) + "..."
    return "\n".join(word_list)

# ==============================================================================
# MOTORES DE ALEATORIEDAD VISUAL ADAPTADOS A SHORTS
# ==============================================================================
def generar_movimiento_camara_imagen():
    """
    Primero crea la composición Short (fondo blur + centro nítido)
    y LUEGO aplica el Ken Burns a todo el cuadro vertical 1080x1920.
    """
    velocidad = "0.001" 
    
    # 1. Pipeline de preparación visual Shorts
    base_prep = (
        f"[0:v]scale={RESOLUTION_W}:{RESOLUTION_H}:force_original_aspect_ratio=increase,"
        f"crop={RESOLUTION_W}:{RESOLUTION_H}:(iw-ow)/2:(ih-oh)/2,boxblur=20:5[bg_blur];"
        f"[0:v]scale={RESOLUTION_W}:-1[img_sharp];"
        f"[bg_blur][img_sharp]overlay=0:(H-h)/2[combined];"
    )
    
    # 2. Aplicamos el Ken Burns al [combined]
    efectos = [
        # ZOOM IN SUAVE
        f"{base_prep}[combined]zoompan=z='min(zoom+{velocidad},1.2)':d=200:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={RESOLUTION_W}x{RESOLUTION_H}:fps={FPS}[bg];",
        # PANEO DERECHA
        f"{base_prep}[combined]zoompan=z=1.05:d=200:x='x+1':y='ih/2-(ih/zoom/2)':s={RESOLUTION_W}x{RESOLUTION_H}:fps={FPS}[bg];",
        # PANEO IZQUIERDA
        f"{base_prep}[combined]zoompan=z=1.05:d=200:x='if(eq(on,1),iw-iw/zoom,x-1)':y='ih/2-(ih/zoom/2)':s={RESOLUTION_W}x{RESOLUTION_H}:fps={FPS}[bg];"
    ]
    
    efecto_elegido = random.choice(efectos)
    logger.info(f"    [FX Motor] Aplicando Ken Burns Vertical ({FPS}fps)")
    return efecto_elegido

def generar_color_grading_video():
    """Aplica Color Grading y recorta el video de B-Roll a 9:16."""
    filtros_color = [
        "eq=contrast=1.05:saturation=1.1",     
        "eq=contrast=1.1:brightness=-0.02",    
        "eq=saturation=0.9:gamma=1.05",        
        "colorbalance=rs=.05:gs=.02:bs=-.02",  
        "colorbalance=rs=-.05:gs=.02:bs=.05",  
        "eq=contrast=1.0"                      
    ]
    
    filtro_elegido = random.choice(filtros_color)
    logger.info(f"    [FX Motor] Color Grading: {filtro_elegido}")
    
    filtro_completo = (
        f"[0:v]format=yuv420p,"
        f"{filtro_elegido},"
        f"scale={RESOLUTION_W}:{RESOLUTION_H}:force_original_aspect_ratio=increase,"
        f"crop={RESOLUTION_W}:{RESOLUTION_H}:(iw-ow)/2:(ih-oh)/2[bg];"
    )
    return filtro_completo

# ==============================================================================
# EL ENSAMBLADOR MAESTRO
# ==============================================================================
def ensamblar_escena(fondo_path, overlay_path, audio_tts_path, bgm_path, sfx_path, texto, output_path):
    duracion_exacta = obtener_duracion_audio(audio_tts_path)
    logger.info(f"  [FFmpeg Universal Short] Ensamblando escena de alta complejidad (Duración: {duracion_exacta}s)...")

    if not os.path.exists(fondo_path) or not os.path.exists(overlay_path) or not os.path.exists(audio_tts_path):
        logger.error("  [FFmpeg Universal] Faltan archivos clave.")
        return False

    filename = os.path.basename(overlay_path)
    config = get_layout_config(filename)
    
    clean_text = formatear_texto(texto, config["max_letras_por_linea"])
    x, y = config["texto_x"], config["texto_y"]
    color, size = config["color"], config["font_size"]
    shadow = "bordercolor=black:borderw=2" 

    import uuid
    texto_path = os.path.join(TEMP_VIDEO_DIR, f"txt_{uuid.uuid4().hex[:6]}.txt").replace('\\', '/')
    if clean_text:
        with open(texto_path, "wb") as f:
            f.write(clean_text.encode("utf-8"))

    es_video_fondo = fondo_path.lower().endswith(('.mp4', '.mov', '.avi'))
    cmd = ["ffmpeg", "-y"]

    if es_video_fondo:
        cmd.extend(["-stream_loop", "-1", "-i", fondo_path])
        fondo_filtro_complex = generar_color_grading_video()
    else:
        cmd.extend(["-loop", "1", "-framerate", str(FPS), "-i", fondo_path])
        fondo_filtro_complex = generar_movimiento_camara_imagen()

    cmd.extend(["-stream_loop", "-1", "-i", overlay_path])
    cmd.extend(["-i", audio_tts_path])

    filter_complex = fondo_filtro_complex + (
        f"[1:v]format=yuv420p,scale={RESOLUTION_W}:{RESOLUTION_H}[v_scaled];"
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
        "-filter_threads", "2",  
        "-filter_complex", filter_complex,
        "-map", "[vout]", 
        *audio_map.split(),
        "-c:v", "libx264", 
        "-preset", "superfast", 
        "-threads", "2",         
        "-r", str(FPS),
        "-c:a", "aac", 
        "-b:a", "128k", 
        "-t", str(duracion_exacta), 
        output_path
    ])

    try:
        proceso = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        proceso.communicate(timeout=600) 
        
        if proceso.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1024:
            logger.info(f"  [FFmpeg Universal Short] ¡ÉXITO! Escena lista: {os.path.basename(output_path)}")
            return True
        else:
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("  [FFmpeg Universal] TIMEOUT Zombi...")
        proceso.kill() 
        proceso.communicate() 
        return False
    except Exception as e:
        if 'proceso' in locals():
            proceso.kill()
            proceso.communicate()
        return False 
    finally:
        if 'texto_path' in locals() and os.path.exists(texto_path):
            try:
                os.remove(texto_path)
            except:
                pass