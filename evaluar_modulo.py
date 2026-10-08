# ============================================================
# EXPERIMENTO COMPARATIVO DEL MODULO IMAGEN
# Uso:
#   python evaluar_modulo.py
# Genera resultados/evaluacion_detalle.csv y
#         resultados/evaluacion_resumen.csv
# ============================================================

import os

import pandas as pd

from modulo_imagen.config_imagen import (
    CARPETA_IMAGENES_PRUEBA,
    CARPETA_RESULTADOS
)
from modulo_imagen.recepcion import frames_desde_carpeta
from modulo_imagen.evaluacion import evaluar, resumen_por_escenario


if __name__ == "__main__":

    tabla = evaluar(
        frames_desde_carpeta(CARPETA_IMAGENES_PRUEBA),
        progreso=lambda i, n, t: print(f"[{i}/{n}] {t}")
    )

    resumen = resumen_por_escenario(tabla)

    os.makedirs(CARPETA_RESULTADOS, exist_ok=True)

    tabla.to_csv(os.path.join(CARPETA_RESULTADOS, "evaluacion_detalle.csv"),
                 index=False, encoding="utf-8-sig")
    resumen.to_csv(os.path.join(CARPETA_RESULTADOS, "evaluacion_resumen.csv"),
                   encoding="utf-8-sig")

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 50)

    print("\nRESUMEN POR ESCENARIO")
    print("antes = VIDEO sobre el frame capturado | despues = VIDEO sobre el frame procesado por IMAGEN")
    print(resumen.T)
