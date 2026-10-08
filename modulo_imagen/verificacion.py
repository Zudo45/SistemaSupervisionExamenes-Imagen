# ============================================================
# VERIFICACION DE DETECCIONES
# IMAGEN no detecta: mide si su procesamiento ayuda a VIDEO.
#   1. Se toman las detecciones de VIDEO sobre el frame capturado.
#   2. Se ejecuta el MISMO modelo de VIDEO (best.pt, sin cambios)
#      sobre el frame procesado por IMAGEN.
#   3. Se emparejan ambas salidas y se compara la confianza:
#      confirmada (se mantiene tras el procesamiento) o
#      no confirmada (desaparece tras el procesamiento).
# ============================================================

from modulo_imagen.config_imagen import (
    GRUPO_CLASE,
    IOU_COINCIDENCIA
)
from modulo_imagen.recepcion import detectar_objetos
from modulo_imagen.caracteristicas import iou


def grupo(clase):

    return GRUPO_CLASE.get(clase, clase)


def emparejar(antes, despues):
    """
    Empareja detecciones del mismo grupo de clase por IoU (greedy,
    de mayor a menor IoU). Devuelve {indice_antes: indice_despues}.
    """

    pares = sorted(
        (
            (iou(a, d), i, j)
            for i, a in enumerate(antes)
            for j, d in enumerate(despues)
            if grupo(a["clase"]) == grupo(d["clase"])
        ),
        reverse=True
    )

    asignados = {}
    usados = set()

    for valor, i, j in pares:

        if valor < IOU_COINCIDENCIA:
            break

        if i in asignados or j in usados:
            continue

        asignados[i] = j
        usados.add(j)

    return asignados


def verificar(frame_procesado, detecciones_video):
    """
    frame_procesado: frame tras preprocesamiento y mejora
    detecciones_video: detecciones de VIDEO sobre el frame capturado

    Devuelve (verificadas, detecciones_despues):
      verificadas: las detecciones de VIDEO con la confianza antes y
                   despues del procesamiento y su estado
      detecciones_despues: salida completa de VIDEO sobre el frame
                           procesado (para las metricas)
    """

    detecciones_despues = [
        {**d, "confianza": round(float(d["confianza"]), 4)}
        for d in detectar_objetos(frame_procesado.copy())
    ]

    pares = emparejar(detecciones_video, detecciones_despues)

    verificadas = []

    for i, original in enumerate(detecciones_video):

        if i in pares:

            despues = detecciones_despues[pares[i]]

            verificadas.append({
                **original,
                "confianza_video": original["confianza"],
                "confianza_procesada": despues["confianza"],
                "variacion_confianza": round(despues["confianza"] - original["confianza"], 4),
                "estado": "confirmada",
                "iou_verificacion": round(iou(original, despues), 3)
            })

        else:

            verificadas.append({
                **original,
                "confianza_video": original["confianza"],
                "confianza_procesada": 0.0,
                "variacion_confianza": round(-original["confianza"], 4),
                "estado": "no_confirmada",
                "iou_verificacion": 0.0
            })

    return verificadas, detecciones_despues


def comparar_salidas(antes, despues):
    """
    Metricas agregadas de la salida de VIDEO antes y despues del
    procesamiento de IMAGEN.
    """

    def media(lista):
        return round(sum(d["confianza"] for d in lista) / len(lista), 4) if lista else 0.0

    pares = emparejar(antes, despues)

    emparejadas_antes = [antes[i] for i in pares]
    emparejadas_despues = [despues[j] for j in pares.values()]

    return {
        "detecciones_antes": len(antes),
        "detecciones_despues": len(despues),
        "confianza_media_antes": media(antes),
        "confianza_media_despues": media(despues),
        "mantenidas": len(pares),
        "perdidas": len(antes) - len(pares),
        "solo_tras_procesamiento": len(despues) - len(pares),
        "variacion_confianza_mantenidas": round(
            media(emparejadas_despues) - media(emparejadas_antes), 4
        )
    }
