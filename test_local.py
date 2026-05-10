# -*- coding: utf-8 -*-
"""
==============================================================================
TEST LOCAL (Simulador de Node.js) - EDICIÓN SHORTS (9:16)
==============================================================================
Este payload masivo generará un video vertical, adaptando todos los fondos,
presentadores, pexels y mapas a las resoluciones matemáticas de Shorts.
"""

import logging
from main_orchestrator import process_video_payload

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

def ejecutar_prueba_shorts():
    print("\n" + "="*70)
    print("🚀 INICIANDO PRODUCCIÓN: PRUEBA DE MOTOR SHORTS 9:16 🚀")
    print("="*70 + "\n")

    # La imagen original de la noticia
    img_noticia = "https://www.elfinanciero.com.mx/resizer/v2/BVLRGKWUCZAK5KQQI574NNPCWM.jpg?smart=true&auth=da160f5b33d3101bcf32028457ec9e5cc06b41c1ede1220bea5b502cb4ea547b&width=1200&height=630"

    payload = {
  "youtube_title": "¡Ecuador Rompe Récords Turísticos! 🇪🇨 #shorts #ecuador #turismo",
  "youtube_description": "👉 ¡Suscríbete para más noticias!\n🌐 Lee la nota completa: https://www.noticias.lat/articulo/test_123\n\n#shorts #noticias\n\nEl turismo en Ecuador ha roto todos los récords históricos durante este último feriado nacional. Las autoridades confirmaron un aumento masivo de viajeros en todo el país, lo que ha generado una reactivación económica espectacular en los últimos años. Destinos costeros y de montaña alcanzaron una ocupación hotelera del cien por ciento. Restaurantes, comercios locales y empresas de transporte reportaron ingresos muy por encima de las expectativas trazadas por los gremios. El gobierno nacional ha destacado el comportamiento cívico de los ciudadanos y el arduo trabajo de las fuerzas de seguridad para garantizar que no se presenten incidentes graves durante estas festividades. La industria hotelera ya se prepara para la próxima temporada alta con gran optimismo. Las autoridades de tránsito inf",
  "youtube_tags": [
    "Ecuador",
    "Turismo",
    "Economía",
    "Viajes",
    "Shorts"
  ],
  "scenes": [
    {
      "type": "intro",
      "text": "Ahora Ecuador rompe récords históricos de turismo durante el último feriado nacional.",
      "layout_category": "sin_presentador",
      "voice": "hombre_1",
      "bgm_mood": "analisis",
      "sfx_type": "impactos"
    },
    {
      "type": "body",
      "text": "Las autoridades confirmaron un aumento masivo de viajeros en todo el país, generando una reactivación económica espectacular en los últimos años recientes.",
      "image_url": "https://img.eldiario.ec/upload/2026/05/turismo.jpg",
      "layout_category": "sin_presentador",
      "voice": "hombre_1",
      "bgm_mood": "analisis",
      "sfx_type": "transiciones"
    },
    {
      "type": "pexels",
      "text": "Destinos costeros y de montaña alcanzaron una ocupación hotelera del cien por ciento, reflejando una demanda sin precedentes de los turistas nacionales.",
      "termino_busqueda": "beach mountains",
      "layout_category": "sin_presentador",
      "voice": "hombre_1",
      "bgm_mood": "analisis",
      "sfx_type": "transiciones"
    },
    {
      "type": "pexels",
      "text": "Restaurantes, comercios locales y empresas de transporte reportaron ingresos muy por encima de las expectativas trazadas por los gremios industriales del país.",
      "termino_busqueda": "local restaurant",
      "layout_category": "sin_presentador",
      "voice": "hombre_1",
      "bgm_mood": "analisis",
      "sfx_type": "transiciones"
    },
    {
      "type": "mapa",
      "text": "El gobierno nacional destacó el comportamiento cívico de los ciudadanos y el arduo trabajo de seguridad para garantizar la paz social total.",
      "ubicacion": "Ecuador",
      "layout_category": "sin_presentador",
      "voice": "hombre_1",
      "bgm_mood": "analisis",
      "sfx_type": "alertas"
    },
    {
      "type": "pexels",
      "text": "La industria hotelera ya se prepara para la próxima temporada alta con gran optimismo, esperando mantener este ritmo de crecimiento constante y fuerte.",
      "termino_busqueda": "luxury hotel",
      "layout_category": "sin_presentador",
      "voice": "hombre_1",
      "bgm_mood": "analisis",
      "sfx_type": "transiciones"
    },
    {
      "type": "pexels",
      "text": "Autoridades de tránsito informaron que más de un millón de vehículos circularon por las carreteras, demostrando confianza total en la seguridad vial actual.",
      "termino_busqueda": "highway traffic",
      "layout_category": "sin_presentador",
      "voice": "hombre_1",
      "bgm_mood": "analisis",
      "sfx_type": "transiciones"
    },
    {
      "type": "body",
      "text": "Este repunte representa un alivio crucial para la economía de las pequeñas familias emprendedoras que dependen directamente del flujo turístico nacional masivo.",
      "image_url": "https://img.eldiario.ec/upload/2026/05/turismo.jpg",
      "layout_category": "sin_presentador",
      "voice": "hombre_1",
      "bgm_mood": "analisis",
      "sfx_type": "transiciones"
    },
    {
      "type": "pexels",
      "text": "El país se consolida como destino líder, demostrando que su diversidad natural y calidez humana son motores clave del desarrollo económico sostenible.",
      "termino_busqueda": "nature tourism",
      "layout_category": "sin_presentador",
      "voice": "hombre_1",
      "bgm_mood": "analisis",
      "sfx_type": "transiciones"
    },
    {
      "type": "pexels",
      "text": "Estas cifras récord marcan una nueva era para el turismo ecuatoriano, prometiendo un futuro próspero y sostenible para todas las provincias beneficiadas.",
      "termino_busqueda": "happy tourists",
      "layout_category": "sin_presentador",
      "voice": "hombre_1",
      "bgm_mood": "analisis",
      "sfx_type": "impactos"
    }
  ]
}


    resultado = process_video_payload(payload)

    print("\n" + "="*70)
    if resultado:
        print(f"✅ ¡NOTICIERO SHORT CREADO EXITOSAMENTE!\n👉 Archivo guardado en: {resultado}")
    else:
        print("❌ LA PRUEBA HA FALLADO. Revisa los logs arriba para ver el error.")
    print("="*70 + "\n")

if __name__ == "__main__":
    ejecutar_prueba_shorts()