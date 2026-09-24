"""
cofres.py — Jerarquía de cofres usando herencia y polimorfismo.
Autor: Camilo Andrés León Rubriche — UNAD

HERENCIA: CofreBase es la clase abstracta con la interfaz común.
Cada cofre concreto hereda de ella y redefine los métodos que cambian.

POLIMORFISMO: el método abrir() tiene la misma firma en todos los cofres
pero devuelve resultados distintos según el tipo. El controlador puede
llamar cofre.abrir() sin saber si es común, raro, legendario o maldito.

ABSTRACCIÓN: CofreBase oculta los detalles de cada tipo. Los clientes
del sistema sólo necesitan conocer la interfaz, no la implementación.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import NamedTuple

from utils.constantes import (
    PUNTOS_COMUN,
    PUNTOS_RARO,
    PUNTOS_LEGENDARIO,
    PUNTOS_MALDITO,
    MENSAJES_COFRE_MALDITO,
)


# ── Resultado de apertura (tipo valor) ──────────────────────────────────────

class ResultadoApertura(NamedTuple):
    """Contiene todo lo que necesita la UI al abrir un cofre.

    NamedTuple provee _replace() para crear copias modificadas,
    útil cuando el controlador necesita enriquecer el mensaje de error.
    """
    nombre_cofre: str
    puntos: int
    emoji: str
    color_hex: str
    mensaje: str
    es_positivo: bool
    rareza: str             # "común", "raro", "legendario", "maldito"
    descripcion_visual: str


# ── Clase base abstracta ─────────────────────────────────────────────────────

class CofreBase(ABC):
    """Define el contrato que todos los cofres deben cumplir.

    Abstracción: los atributos de clase (nombre, puntos, emoji, color)
    son declarados aquí pero definidos en cada subclase.
    """

    nombre: str
    puntos_base: int
    emoji: str
    color_hex: str
    rareza: str
    descripcion_visual: str

    def __init__(self, multiplicador: float = 1.0) -> None:
        """
        Args:
            multiplicador: Factor que modifica los puntos según dificultad.
        """
        self._multiplicador = multiplicador

    @abstractmethod
    def abrir(self) -> ResultadoApertura:
        """Abre el cofre y devuelve el resultado de la interacción.

        Método abstracto: fuerza a cada subclase a implementar su propia
        lógica de apertura, garantizando que ningún cofre sea «genérico».
        """
        ...

    @abstractmethod
    def animacion_ascii(self) -> str:
        """Representación ASCII del cofre para mostrar en la UI de texto."""
        ...

    def puntos_finales(self) -> int:
        """Aplica el multiplicador y retorna los puntos enteros.

        Método concreto heredado: la lógica de multiplicación es igual
        para todos, pero cada subclase define puntos_base distinto.
        """
        return int(self.puntos_base * self._multiplicador)

    def __str__(self) -> str:
        return f"{self.emoji} {self.nombre} ({self.rareza})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(multiplicador={self._multiplicador})"


# ── Cofres concretos ─────────────────────────────────────────────────────────

class CofreComun(CofreBase):
    """Cofre básico. Recompensa modesta, aparece con frecuencia.

    Herencia: hereda toda la estructura de CofreBase y sólo redefine
    los atributos de clase y los métodos abstractos.
    """

    nombre             = "Cofre Común"
    puntos_base        = PUNTOS_COMUN
    emoji              = "📦"
    color_hex          = "#6e7681"
    rareza             = "común"
    descripcion_visual = "Un cofre de madera desgastado. No parece gran cosa..."

    def abrir(self) -> ResultadoApertura:
        mensajes = [
            "Algo de valor, al menos.",
            "Modesto, pero es tuyo.",
            "No es un tesoro, pero suma.",
            "La humildad también recompensa.",
        ]
        return ResultadoApertura(
            nombre_cofre      = self.nombre,
            puntos            = self.puntos_finales(),
            emoji             = self.emoji,
            color_hex         = self.color_hex,
            mensaje           = random.choice(mensajes),
            es_positivo       = True,
            rareza            = self.rareza,
            descripcion_visual = self.descripcion_visual,
        )

    def animacion_ascii(self) -> str:
        return (
            "  ┌───────────┐\n"
            "  │  📦  C O F R E  │\n"
            "  │   C O M Ú N   │\n"
            "  └───────────┘"
        )


class CofreRaro(CofreBase):
    """Cofre de material metálico con engastes de gema. Recompensa notable.

    Polimorfismo: abrir() tiene la misma firma que en CofreComun pero
    devuelve mensajes distintos, color distinto y más puntos.
    """

    nombre             = "Cofre Raro"
    puntos_base        = PUNTOS_RARO
    emoji              = "💎"
    color_hex          = "#388bfd"
    rareza             = "raro"
    descripcion_visual = "Acero azulado con incrustaciones de zafiro. Llamativo."

    def abrir(self) -> ResultadoApertura:
        mensajes = [
            "¡Una gema oculta entre los bits!",
            "La rareza tiene su precio, y vale la pena.",
            "El algoritmo te favoreció hoy.",
            "Azul como el mar, valioso como el oro.",
        ]
        return ResultadoApertura(
            nombre_cofre      = self.nombre,
            puntos            = self.puntos_finales(),
            emoji             = self.emoji,
            color_hex         = self.color_hex,
            mensaje           = random.choice(mensajes),
            es_positivo       = True,
            rareza            = self.rareza,
            descripcion_visual = self.descripcion_visual,
        )

    def animacion_ascii(self) -> str:
        return (
            "  ╔═══════════╗\n"
            "  ║  💎  C O F R E  ║\n"
            "  ║    R A R O    ║\n"
            "  ╚═══════════╝"
        )


class CofreLegendario(CofreBase):
    """Cofre de oro macizo. Difícil de conseguir, recompensa extraordinaria.

    Herencia + polimorfismo: misma interfaz, comportamiento premium distinto.
    Agrega lógica de «bonus aleatorio» que los otros cofres no tienen.
    """

    nombre             = "Cofre Legendario"
    puntos_base        = PUNTOS_LEGENDARIO
    emoji              = "👑"
    color_hex          = "#d4a017"
    rareza             = "legendario"
    descripcion_visual = "Oro puro con grabados ancestrales. La leyenda hecha cofre."

    def abrir(self) -> ResultadoApertura:
        # Los cofres legendarios tienen 20% de chance de dar el doble
        puntos = self.puntos_finales()
        bonus_activo = random.random() < 0.20
        if bonus_activo:
            puntos *= 2
            mensaje = "¡DOBLE RECOMPENSA! El cofre legendario fue generoso hoy. ¡Épico!"
        else:
            mensajes = [
                "¡El legendario es tuyo! Mereces la corona.",
                "Pocos llegan aquí. Tú lo lograste.",
                "El código te reconoce como maestro.",
                "La leyenda confirma tu talento. ¡Formidable!",
            ]
            mensaje = random.choice(mensajes)

        return ResultadoApertura(
            nombre_cofre      = self.nombre,
            puntos            = puntos,
            emoji             = self.emoji,
            color_hex         = self.color_hex,
            mensaje           = mensaje,
            es_positivo       = True,
            rareza            = self.rareza,
            descripcion_visual = self.descripcion_visual,
        )

    def animacion_ascii(self) -> str:
        return (
            "  ★═══════════★\n"
            "  ║  👑 LEGENDARIO ║\n"
            "  ║   ¡ÉPICO!   ║\n"
            "  ★═══════════★"
        )


class CofreMaldito(CofreBase):
    """Cofre trampa. Drena puntos al abrirlo. Riesgo real del juego.

    Polimorfismo: es_positivo=False señala al controlador que debe
    restar puntos en lugar de sumarlos. Misma interfaz, semántica opuesta.
    """

    nombre             = "Cofre Maldito"
    puntos_base        = PUNTOS_MALDITO    # negativo
    emoji              = "💀"
    color_hex          = "#8957e5"
    rareza             = "maldito"
    descripcion_visual = "Algo oscuro emana de él. Deberías haber sospechado."

    def abrir(self) -> ResultadoApertura:
        return ResultadoApertura(
            nombre_cofre      = self.nombre,
            puntos            = self.puntos_finales(),    # será negativo
            emoji             = self.emoji,
            color_hex         = self.color_hex,
            mensaje           = random.choice(MENSAJES_COFRE_MALDITO),
            es_positivo       = False,
            rareza            = self.rareza,
            descripcion_visual = self.descripcion_visual,
        )

    def animacion_ascii(self) -> str:
        return (
            "  ╬═══════════╬\n"
            "  ║  💀  M A L D I T O  ║\n"
            "  ║  ¡TRAMPA!  ║\n"
            "  ╬═══════════╬"
        )


# ── Fábrica de cofres ────────────────────────────────────────────────────────

class FabricaCofre:
    """Selecciona y construye el tipo de cofre basándose en probabilidades.

    Patrón Factory Method: el controlador no necesita conocer las subclases
    ni las probabilidades; sólo llama a FabricaCofre.crear().

    Composición: JuegoCazador usa FabricaCofre sin heredar de ella.
    """

    _TIPOS: list[type[CofreBase]] = [
        CofreComun,
        CofreRaro,
        CofreLegendario,
        CofreMaldito,
    ]

    @classmethod
    def crear(
        cls,
        probabilidades: list[float],
        multiplicador: float = 1.0,
    ) -> CofreBase:
        """Elige aleatoriamente un tipo de cofre según los pesos dados.

        Args:
            probabilidades: Lista de 4 floats [comun, raro, legendario, maldito]
                           que deben sumar 1.0.
            multiplicador: Modificador de puntos por dificultad.

        Returns:
            Instancia del cofre elegido.
        """
        # random.choices con weights es la forma idiomática de selección ponderada
        tipo_elegido = random.choices(cls._TIPOS, weights=probabilidades, k=1)[0]
        return tipo_elegido(multiplicador=multiplicador)

    @classmethod
    def crear_por_rareza(cls, rareza: str, multiplicador: float = 1.0) -> CofreBase:
        """Crea un cofre específico por nombre de rareza (útil para pruebas)."""
        mapa: dict[str, type[CofreBase]] = {
            "común":      CofreComun,
            "raro":       CofreRaro,
            "legendario": CofreLegendario,
            "maldito":    CofreMaldito,
        }
        tipo = mapa.get(rareza.lower(), CofreComun)
        return tipo(multiplicador=multiplicador)
