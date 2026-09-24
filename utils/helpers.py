"""
helpers.py — Utilidades transversales sin dependencias del dominio.

Estas funciones no saben nada del juego; son herramientas genéricas
reutilizables en cualquier proyecto Python. Eso las mantiene fáciles
de testear y de mover si la arquitectura cambia.
"""

import random
import time
from datetime import datetime
from typing import Any


def timestamp_legible() -> str:
    """Retorna la fecha/hora actual en formato amigable para mostrar en UI."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def truncar_texto(texto: str, maximo: int = 30, sufijo: str = "…") -> str:
    """Acorta un texto largo para que quepa en componentes con espacio limitado."""
    if len(texto) <= maximo:
        return texto
    return texto[: maximo - len(sufijo)] + sufijo


def calcular_porcentaje(valor: int | float, total: int | float) -> float:
    """Devuelve el porcentaje de valor respecto a total, evitando ZeroDivisionError."""
    if total == 0:
        return 0.0
    return round((valor / total) * 100, 2)


def elegir_aleatorio(opciones: list[Any], pesos: list[float] | None = None) -> Any:
    """Selecciona un elemento de la lista.

    Si se pasan pesos, usa random.choices para distribución ponderada.
    Sin pesos, usa random.choice (distribución uniforme).
    """
    if not opciones:
        raise ValueError("La lista de opciones no puede estar vacía.")
    if pesos:
        return random.choices(opciones, weights=pesos, k=1)[0]
    return random.choice(opciones)


def mezclar_lista(lista: list[Any]) -> list[Any]:
    """Devuelve una copia mezclada de la lista sin modificar la original."""
    copia = lista[:]
    random.shuffle(copia)
    return copia


def formatear_puntos(puntos: int) -> str:
    """Formatea puntos con signo explícito para mostrar ganancias/pérdidas."""
    return f"+{puntos}" if puntos >= 0 else str(puntos)


def segundos_a_mmss(segundos: float) -> str:
    """Convierte segundos a formato MM:SS para mostrar tiempo de sesión."""
    segundos = int(segundos)
    minutos, segs = divmod(segundos, 60)
    return f"{minutos:02d}:{segs:02d}"


def es_entero_valido(valor: str) -> bool:
    """Chequeo rápido antes de intentar la conversión, evitando excepciones innecesarias."""
    return valor.strip().lstrip("-").isdigit()


def limpiar_cadena(cadena: str) -> str:
    """Elimina espacios al inicio/fin y retorna vacío si el resultado es vacío."""
    return cadena.strip()


def generar_id_sesion() -> str:
    """Crea un identificador único para cada sesión de juego."""
    return f"SES-{int(time.time())}-{random.randint(1000, 9999)}"
