"""
estadisticas.py — Modelo de estadísticas globales acumuladas entre sesiones.

Separo las estadísticas de sesión (en Jugador) de las estadísticas
globales para respetar SRP: Jugador gestiona la sesión actual,
este módulo gestiona la visión histórica de todas las sesiones.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EstadisticasGlobales:
    """Estadísticas acumuladas de todas las partidas (persiste en JSON)."""

    total_partidas:        int   = 0
    total_rondas:          int   = 0
    total_puntos:          int   = 0
    mejor_puntaje:         int   = 0
    mejor_jugador:         str   = ""
    cofres_totales:        dict  = field(default_factory=lambda: {
        "común": 0, "raro": 0, "legendario": 0, "maldito": 0
    })
    contrasenas_generadas: int   = 0
    niveles_seguridad:     dict  = field(default_factory=lambda: {
        "Débil": 0, "Moderado": 0, "Fuerte": 0, "Extremo": 0
    })
    logros_desbloqueados:  dict  = field(default_factory=dict)

    def actualizar_con_sesion(self, datos_sesion: dict) -> None:
        """Integra los datos de una sesión terminada en las estadísticas globales."""
        self.total_partidas   += 1
        stats = datos_sesion.get("estadisticas", {})
        self.total_rondas     += stats.get("rondas_jugadas", 0)
        self.total_puntos     += datos_sesion.get("puntaje", 0)

        puntaje = datos_sesion.get("puntaje", 0)
        nombre  = datos_sesion.get("nombre", "")
        if puntaje > self.mejor_puntaje:
            self.mejor_puntaje  = puntaje
            self.mejor_jugador  = nombre

    def to_dict(self) -> dict:
        return self.__dict__

    @classmethod
    def from_dict(cls, datos: dict) -> "EstadisticasGlobales":
        obj = cls()
        for k, v in datos.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        return obj

    def resumen_texto(self) -> str:
        lineas = [
            f"Partidas jugadas:   {self.total_partidas}",
            f"Rondas totales:     {self.total_rondas}",
            f"Puntos acumulados:  {self.total_puntos}",
            f"Mejor puntaje:      {self.mejor_puntaje} ({self.mejor_jugador})",
        ]
        return "\n".join(lineas)
