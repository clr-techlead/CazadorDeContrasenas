"""
ranking_service.py — Gestiona la persistencia del ranking y el historial.

Separé la persistencia del modelo para cumplir SRP: los modelos no
saben cómo guardarse; este servicio sabe cómo serializar y deserializar,
pero no sabe nada de la UI.
"""

import json
from pathlib import Path
from typing import Optional

from excepciones import ErrorPersistencia
from utils.constantes import ARCHIVO_RANKING, ARCHIVO_HISTORIAL, MAX_ENTRADAS_RANKING
from utils.helpers import timestamp_legible


class RankingService:
    """Lee y escribe el ranking local y el historial de partidas en JSON."""

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        # Calculamos la ruta relativa al archivo de este módulo
        raiz = base_dir or Path(__file__).parent.parent
        self._ruta_ranking:   Path = raiz / ARCHIVO_RANKING
        self._ruta_historial: Path = raiz / ARCHIVO_HISTORIAL
        self._asegurar_archivos()

    # ── Ranking ──────────────────────────────────────────────────────────────

    def cargar_ranking(self) -> list[dict]:
        """Lee el ranking del archivo JSON. Retorna lista vacía si falla."""
        try:
            datos = self._leer_json(self._ruta_ranking)
            return datos if isinstance(datos, list) else []
        except ErrorPersistencia:
            return []

    def guardar_entrada(self, nombre: str, puntaje: int, dificultad: str) -> int:
        """Agrega o actualiza una entrada en el ranking.

        Si el jugador ya existe, actualiza sólo si mejoró su puntaje.

        Returns:
            Posición en el ranking (1-based).
        """
        ranking = self.cargar_ranking()

        # Actualizar o insertar
        encontrado = False
        for entrada in ranking:
            if entrada.get("nombre", "").lower() == nombre.lower():
                if puntaje > entrada.get("puntaje", 0):
                    entrada["puntaje"]    = puntaje
                    entrada["dificultad"] = dificultad
                    entrada["timestamp"]  = timestamp_legible()
                encontrado = True
                break

        if not encontrado:
            ranking.append({
                "nombre":     nombre,
                "puntaje":    puntaje,
                "dificultad": dificultad,
                "timestamp":  timestamp_legible(),
            })

        # Ordenar y recortar
        ranking.sort(key=lambda x: x.get("puntaje", 0), reverse=True)
        ranking = ranking[:MAX_ENTRADAS_RANKING]

        self._escribir_json(self._ruta_ranking, ranking)

        # Encontrar posición
        for pos, entrada in enumerate(ranking, start=1):
            if entrada.get("nombre", "").lower() == nombre.lower():
                return pos
        return MAX_ENTRADAS_RANKING

    # ── Historial ────────────────────────────────────────────────────────────

    def cargar_historial(self) -> list[dict]:
        try:
            datos = self._leer_json(self._ruta_historial)
            return datos if isinstance(datos, list) else []
        except ErrorPersistencia:
            return []

    def guardar_sesion(self, datos_jugador: dict) -> None:
        """Agrega la sesión al historial."""
        historial = self.cargar_historial()
        historial.append(datos_jugador)
        # Mantener sólo las últimas 50 sesiones
        if len(historial) > 50:
            historial = historial[-50:]
        self._escribir_json(self._ruta_historial, historial)

    # ── I/O JSON ─────────────────────────────────────────────────────────────

    def _leer_json(self, ruta: Path) -> list | dict:
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ErrorPersistencia(str(ruta), str(e)) from e

    def _escribir_json(self, ruta: Path, datos: list | dict) -> None:
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
        except OSError as e:
            raise ErrorPersistencia(str(ruta), str(e)) from e

    def _asegurar_archivos(self) -> None:
        """Crea los archivos JSON vacíos si no existen."""
        for ruta, estructura in [
            (self._ruta_ranking, []),
            (self._ruta_historial, []),
        ]:
            if not ruta.exists():
                try:
                    self._escribir_json(ruta, estructura)
                except ErrorPersistencia:
                    pass   # Si falla la creación inicial, fallará en el primer uso
