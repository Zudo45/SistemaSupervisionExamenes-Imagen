# ============================================================
# VISUALIZACION
# Dibujo de detecciones, mascaras y histogramas.
# ============================================================

import cv2
import numpy as np


# Colores BGR por estado de verificacion
COLORES_ESTADO = {
    "video": (255, 140, 0),          # azul: deteccion original
    "confirmada": (60, 180, 60),     # verde
    "no_confirmada": (0, 165, 255)   # naranja
}


def _grosor(imagen):

    return max(2, max(imagen.shape[:2]) // 400)


def dibujar_caja(imagen, deteccion, color, texto):

    g = _grosor(imagen)
    escala = max(0.5, max(imagen.shape[:2]) / 1600)

    x1, y1, x2, y2 = deteccion["x1"], deteccion["y1"], deteccion["x2"], deteccion["y2"]

    cv2.rectangle(imagen, (x1, y1), (x2, y2), color, g)

    (tw, th), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, escala, g)

    y_texto = y1 - 6 if y1 - th - 10 > 0 else y1 + th + 6

    cv2.rectangle(imagen, (x1, y_texto - th - 6), (x1 + tw + 6, y_texto + 4), color, cv2.FILLED)

    cv2.putText(imagen, texto, (x1 + 3, y_texto), cv2.FONT_HERSHEY_SIMPLEX,
                escala, (255, 255, 255), max(1, g - 1), cv2.LINE_AA)


def dibujar_video(imagen, detecciones):

    salida = imagen.copy()

    for d in detecciones:
        dibujar_caja(salida, d, COLORES_ESTADO["video"], f"{d['clase']} {d['confianza']:.2f}")

    return salida


def dibujar_verificadas(imagen, verificadas):

    salida = imagen.copy()

    for d in verificadas:

        if d["estado"] == "confirmada":
            texto = f"{d['clase']} {d['confianza_video']:.2f}->{d['confianza_procesada']:.2f}"
        else:
            texto = f"{d['clase']} {d['confianza_video']:.2f} (no confirmada)"

        dibujar_caja(salida, d, COLORES_ESTADO[d["estado"]], texto)

    return salida


def superponer_mascara(recorte, mascara, contorno, color=(0, 255, 0)):

    salida = recorte.copy()

    capa = np.zeros_like(recorte)
    capa[mascara > 0] = color

    salida = cv2.addWeighted(salida, 1.0, capa, 0.35, 0)

    if contorno is not None:
        cv2.drawContours(salida, [contorno], -1, color, 2)

    return salida


def histograma_gris(imagen):

    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    return cv2.calcHist([gris], [0], None, [256], [0, 256]).ravel()


def a_rgb(imagen):

    if imagen.ndim == 2:
        return imagen

    return cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
