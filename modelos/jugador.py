"""
jugador.py — Modelo del jugador y su estado en la sesión actual.
Autor: Camilo Andrés León Rubriche — UNAD

Encapsulamiento: el estado del jugador (puntuación, logros, estadísticas
de la sesión) se mantiene privado y se expone mediante métodos con
semántica clara. Nadie puede modificar el puntaje directamente; sólo
a través de registrar_ronda(), que valida y actualiza atomicamente.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from utils.helpers import generar_id_sesion, timestamp_legible
from utils.constantes import LOGROS


@dataclass
class EstadisticasSesion:
    """Estado acumulado de la sesión actual (no persiste entre sesiones)."""

    rondas_jugadas:       int   = 0
    rondas_ganadas:       int   = 0
    cofres_comunes:       int   = 0
    cofres_raros:         int   = 0
    cofres_legendarios:   int   = 0
    cofres_malditos:      int   = 0
    contrasenas_extremas: int   = 0
    racha_sin_maldito:    int   = 0
    racha_maxima:         int   = 0
    puntaje_total:        int   = 0
    puntaje_maximo_ronda: int   = 0

    def actualizar_racha(self, fue_maldito: bool) -> None:
        if fue_maldito:
            self.racha_sin_maldito = 0
        else:
            self.racha_sin_maldito += 1
            if self.racha_sin_maldito > self.racha_maxima:
                self.racha_maxima = self.racha_sin_maldito

    def porcentaje_exito(self) -> float:
        if self.rondas_jugadas == 0:
            return 0.0
        return round(self.rondas_ganadas / self.rondas_jugadas * 100, 1)


class Jugador:
    """Representa al jugador durante una sesión de juego.

    Mantiene el estado de la sesión, el historial de rondas y verifica
    qué logros se han desbloqueado. La clase no sabe nada de la UI ni
    del almacenamiento persistente (eso lo hace RankingService).

    Composición: Jugador *tiene* EstadisticasSesion en lugar de heredar,
    porque la relación es «posee» y no «es-un».
    """

    def __init__(self, nombre: str, dificultad: str = "normal") -> None:
        self._nombre: str = nombre.strip() or "Cazador"
        self._dificultad: str = dificultad
        self._puntaje: int = 0
        self._historial_rondas: list[dict] = []
        self._logros_desbloqueados: set[str] = set()
        self._stats: EstadisticasSesion = EstadisticasSesion()
        self._id_sesion: str = generar_id_sesion()
        self._inicio_sesion: float = time.time()

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def puntaje(self) -> int:
        return self._puntaje

    @property
    def dificultad(self) -> str:
        return self._dificultad

    @property
    def estadisticas(self) -> EstadisticasSesion:
        return self._stats

    @property
    def historial(self) -> list[dict]:
        return list(self._historial_rondas)   # copia defensiva

    @property
    def logros(self) -> set[str]:
        return set(self._logros_desbloqueados)

    @property
    def tiempo_sesion(self) -> float:
        return time.time() - self._inicio_sesion

    # ── Lógica de negocio ────────────────────────────────────────────────────

    def registrar_ronda(
        self,
        contrasena: str,
        nivel_seguridad: str,
        tipo_cofre: str,
        rareza_cofre: str,
        puntos_obtenidos: int,
    ) -> list[str]:
        """Actualiza el estado del jugador tras completar una ronda.

        Returns:
            Lista de IDs de logros recién desbloqueados en esta ronda.
        """
        self._puntaje += puntos_obtenidos
        self._stats.rondas_jugadas += 1

        if puntos_obtenidos > 0:
            self._stats.rondas_ganadas += 1

        # Actualizar contadores de cofres
        mapa_cofres = {
            "común":      "cofres_comunes",
            "raro":       "cofres_raros",
            "legendario": "cofres_legendarios",
            "maldito":    "cofres_malditos",
        }
        attr = mapa_cofres.get(rareza_cofre)
        if attr:
            setattr(self._stats, attr, getattr(self._stats, attr) + 1)

        fue_maldito = rareza_cofre == "maldito"
        self._stats.actualizar_racha(fue_maldito)
        self._stats.puntaje_total = self._puntaje

        if puntos_obtenidos > self._stats.puntaje_maximo_ronda:
            self._stats.puntaje_maximo_ronda = puntos_obtenidos

        if nivel_seguridad == "Extremo":
            self._stats.contrasenas_extremas += 1

        # Registrar en historial
        entrada = {
            "ronda":           self._stats.rondas_jugadas,
            "contrasena":      contrasena,
            "nivel_seguridad": nivel_seguridad,
            "tipo_cofre":      tipo_cofre,
            "rareza":          rareza_cofre,
            "puntos":          puntos_obtenidos,
            "puntaje_total":   self._puntaje,
            "timestamp":       timestamp_legible(),
        }
        self._historial_rondas.append(entrada)

        # Verificar logros nuevos
        nuevos_logros = self._verificar_logros()
        return nuevos_logros

    def _verificar_logros(self) -> list[str]:
        """Evalúa condiciones de logros y retorna los nuevamente desbloqueados."""
        nuevos: list[str] = []
        stats = self._stats

        condiciones: dict[str, bool] = {
            "primera_sangre": stats.rondas_jugadas >= 1,
            "coleccionista":  stats.puntaje_total >= 100,
            "legendario":     stats.cofres_legendarios >= 1,
            "invicto":        stats.racha_sin_maldito >= 5,
            "maestro_clave":  stats.contrasenas_extremas >= 10,
        }

        for logro_id, cumple in condiciones.items():
            if cumple and logro_id not in self._logros_desbloqueados:
                self._logros_desbloqueados.add(logro_id)
                nuevos.append(logro_id)

        return nuevos

    def to_dict(self) -> dict:
        """Serializa el jugador para persistencia en JSON."""
        return {
            "nombre":          self._nombre,
            "puntaje":         self._puntaje,
            "dificultad":      self._dificultad,
            "id_sesion":       self._id_sesion,
            "timestamp":       timestamp_legible(),
            "estadisticas":    self._stats.__dict__,
            "logros":          list(self._logros_desbloqueados),
            "total_rondas":    self._stats.rondas_jugadas,
        }

    def __str__(self) -> str:
        return f"Jugador({self._nombre}, puntos={self._puntaje}, rondas={self._stats.rondas_jugadas})"
