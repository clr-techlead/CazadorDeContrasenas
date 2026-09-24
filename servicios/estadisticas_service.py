"""
estadisticas_service.py — Agrega y expone estadísticas globales del juego.
"""

import json
from pathlib import Path
from typing import Optional

from modelos.estadisticas import EstadisticasGlobales
from excepciones import ErrorPersistencia

_RUTA_STATS = "data/estadisticas_globales.json"


class EstadisticasService:

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        raiz = base_dir or Path(__file__).parent.parent
        self._ruta = raiz / _RUTA_STATS
        self._stats: EstadisticasGlobales = self._cargar()

    @property
    def stats(self) -> EstadisticasGlobales:
        return self._stats

    def registrar_sesion(self, datos_jugador: dict) -> None:
        self._stats.actualizar_con_sesion(datos_jugador)
        self._guardar()

    def _cargar(self) -> EstadisticasGlobales:
        try:
            with open(self._ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
            return EstadisticasGlobales.from_dict(datos)
        except (FileNotFoundError, json.JSONDecodeError):
            return EstadisticasGlobales()

    def _guardar(self) -> None:
        try:
            self._ruta.parent.mkdir(parents=True, exist_ok=True)
            with open(self._ruta, "w", encoding="utf-8") as f:
                json.dump(self._stats.to_dict(), f, ensure_ascii=False, indent=2)
        except OSError as e:
            raise ErrorPersistencia(str(self._ruta), str(e)) from e
