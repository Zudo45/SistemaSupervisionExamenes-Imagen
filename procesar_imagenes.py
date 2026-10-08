# ============================================================
# PROCESAMIENTO POR LOTES DEL MODULO IMAGEN
# Uso:
#   python procesar_imagenes.py                 (imagenes de prueba)
#   python procesar_imagenes.py ruta/carpeta
#   python procesar_imagenes.py ruta/video.mp4
# ============================================================

import os
import sys
import time

import cv2

from modulo_imagen.config_imagen import (
    CARPETA_IMAGENES_PRUEBA,
    CARPETA_RESULTADOS
)
from modulo_imagen.recepcion import (
    frames_desde_carpeta,
    frames_desde_video
)
from modulo_imagen.pipeline import procesar_frame
from modulo_imagen.exportacion import guardar_resultados
from modulo_imagen.visualizacion import dibujar_verificadas


def ejecutar(fuente):

    if os.path.isdir(fuente):
        paquetes = frames_desde_carpeta(fuente)
    else:
        paquetes = frames_desde_video(fuente)

    carpeta_frames = os.path.join(CARPETA_RESULTADOS, "frames")
    os.makedirs(carpeta_frames, exist_ok=True)

    resultados = []

    for paquete in paquetes:

        inicio = time.time()

        resultado = procesar_frame(paquete)

        # No se guardan las imagenes intermedias en memoria
        resumen = resultado["resumen"]

        print(
            f"[{paquete['frame_id']:03d}] {paquete['origen']}: "
            f"VIDEO={resumen['detecciones_video']} "
            f"confirmadas={resumen['confirmadas']} "
            f"no_confirmadas={resumen['no_confirmadas']} "
            f"conf. media {resumen['comparacion_video']['confianza_media_antes']:.2f}"
            f"->{resumen['comparacion_video']['confianza_media_despues']:.2f} "
            f"({time.time() - inicio:.1f}s)"
        )

        anotada = dibujar_verificadas(
            resultado["imagenes"]["mejorado"],
            [o["deteccion"] for o in resultado["objetos"]]
        )

        nombre = os.path.splitext(paquete["origen"])[0]
        cv2.imwrite(
            os.path.join(carpeta_frames, f"{paquete['frame_id']:03d}_{nombre}.jpg"),
            anotada
        )

        resultado["imagenes"] = {}
        for objeto in resultado["objetos"]:
            objeto["segmento"] = None

        resultados.append(resultado)

    ruta_json, ruta_csv = guardar_resultados(resultados, CARPETA_RESULTADOS)

    print(f"\nJSON: {ruta_json}")
    print(f"CSV:  {ruta_csv}")


if __name__ == "__main__":

    ejecutar(sys.argv[1] if len(sys.argv) > 1 else CARPETA_IMAGENES_PRUEBA)
