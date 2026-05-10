# -*- coding: utf-8 -*-
"""
==============================================================================
MÓDULO FFMPEG: ENSAMBLADOR DE INTROS (VERSIÓN SHORTS)
==============================================================================
Se encarga exclusivamente de las intros verticales.
NO HAY CHROMA KEY. Es video directo + texto gigante centrado + audio mezclado.
"""

import os
import logging
import subprocess
import textwrap
from config import *

logger = logging.getLogger(__name__)

def formatear_texto_intro(texto, max_chars):
    """Corta el titular para que encaje perfecto y se vea gigante en el Short."""
    if not texto:
        return ""
    # Escapar comillas simples y dos puntos
    texto = texto.replace("'", "\u2019").replace(":", "\\:")
    wrapper = textwrap.TextWrapper(width=max_chars)
    word_list = wrapper.wrap(text=texto)
    # En Shorts, permitimos hasta 3 líneas para titulares muy impactantes
    if len(word_list) > 3:
        return "\\n".join(word_list[:3]) + "..."
    return "\\n".join(word_list)

def ensamblar_intro(intro_path, audio_tts_path, bgm_path, sfx_path, texto, output_path):
    """
    Toma el video de intro base vertical y le incrusta el título, la voz y la música.
    """
    logger.info(f"  [FFmpeg Intro] Ensamblando escena de Introducción Short...")
    logger.info(f"  --> Intro Base: {os.path.basename(intro_path)}")

    if not os.path.exists(intro_path) or not os.path.exists(audio_tts_path):
        logger.error("  [FFmpeg Intro] Faltan archivos clave (Intro o Audio) para ensamblar.")
        return False

    filename = os.path.basename(intro_path)
    config = get_layout_config(filename)
    
    clean_text = formatear_texto_intro(texto, config["max_letras_por_linea"])
    
    x, y = config["texto_x"], config["texto_y"]
    color, size = config["color"], config["font_size"]
    shadow = "shadowcolor=black@0.8:shadowx=0:shadowy=0" 

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", intro_path, 
        "-i", audio_tts_path                    
    ]

    # Fuerza el formato 1080x1920 por si la intro original es un poco distinta
    filter_complex = (
        f"[0:v]scale={RESOLUTION_W}:{RESOLUTION_H}:force_original_aspect_ratio=increase,"
        f"crop={RESOLUTION_W}:{RESOLUTION_H}:(iw-ow)/2:(ih-oh)/2[bg];"
    )

    if clean_text:
        filter_complex += f"[bg]drawtext=fontfile='{FONT_PATH}':text='{clean_text}':fontcolor={color}:fontsize={size}:{shadow}:x={x}:y={y}[vout];"
    else:
        filter_complex += f"[bg]copy[vout];"

    audio_inputs = "[1:a]"
    input_count = 1

    if bgm_path and os.path.exists(bgm_path):
        cmd.extend(["-i", bgm_path])  
        audio_inputs += "[2:a]"
        input_count += 1
        
    if sfx_path and os.path.exists(sfx_path):
        cmd.extend(["-i", sfx_path])  
        audio_inputs += "[3:a]"
        input_count += 1

    if input_count > 1:
        filter_complex += f"{audio_inputs}amix=inputs={input_count}:duration=first:dropout_transition=2:weights=1 0.15 0.3[aout]"
        audio_map = "-map [aout]"
    else:
        filter_complex = filter_complex.rstrip(';')
        audio_map = "-map 1:a"

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
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=200)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1024:
            logger.info("  [FFmpeg Intro] Intro Short renderizada con éxito.")
            return True
        else:
            logger.error("  [FFmpeg Intro] El archivo resultante está vacío.")
            return False
            
    except Exception as e:
        logger.error(f"  [FFmpeg Intro] Error crítico: {e}")
        return False