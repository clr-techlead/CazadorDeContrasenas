"""
panel_ranking.py — Ventana emergente con el ranking y estadísticas globales.

Usa CTkToplevel para crear una ventana secundaria modal.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable

import customtkinter as ctk

from utils.colores import TEMA, COLOR_COFRE


class VentanaRanking(ctk.CTkToplevel):
    """Ventana modal con el top 10 de jugadores y estadísticas globales."""

    def __init__(
        self,
        parent: tk.Widget,
        ranking: list[dict],
        stats_texto: str,
        on_cerrar: Callable | None = None,
    ) -> None:
        super().__init__(parent)
        self.title("🏆  Ranking Global — Cazador de Contraseñas")
        self.geometry("560x600")
        self.resizable(False, False)
        self.configure(fg_color=TEMA.fondo_principal)
        self.grab_set()   # modal: bloquea la ventana principal mientras está abierta

        self._on_cerrar = on_cerrar
        self._construir_ui(ranking, stats_texto)
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    def _construir_ui(self, ranking: list[dict], stats_texto: str) -> None:
        # Header
        ctk.CTkLabel(
            self,
            text="🏆  RANKING GLOBAL",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEMA.advertencia,
        ).pack(pady=(20, 4))

        ctk.CTkLabel(
            self,
            text="Los mejores cazadores de contraseñas",
            font=ctk.CTkFont(size=13),
            text_color=TEMA.texto_secundario,
        ).pack(pady=(0, 16))

        # Tabla de ranking
        tabla = ctk.CTkScrollableFrame(
            self,
            fg_color=TEMA.fondo_panel,
            corner_radius=12,
            height=320,
        )
        tabla.pack(padx=20, fill="x")

        if not ranking:
            ctk.CTkLabel(
                tabla,
                text="Aún no hay entradas en el ranking.\n¡Sé el primero!",
                font=ctk.CTkFont(size=14),
                text_color=TEMA.texto_secundario,
            ).pack(pady=40)
        else:
            for pos, entrada in enumerate(ranking, start=1):
                self._fila_ranking(tabla, pos, entrada)

        # Estadísticas globales — panel con fondo propio
        ctk.CTkLabel(
            self,
            text="ESTADÍSTICAS GLOBALES",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEMA.texto_secundario,
        ).pack(padx=20, pady=(16, 4), anchor="w")

        stats_frame = ctk.CTkFrame(
            self, fg_color=TEMA.fondo_panel, corner_radius=10
        )
        stats_frame.pack(padx=20, fill="x")

        ctk.CTkLabel(
            stats_frame,
            text=stats_texto or "Sin datos globales aún.\nJuega una partida completa para ver estadísticas.",
            font=ctk.CTkFont(family="Courier New", size=12),
            text_color=TEMA.texto_principal,
            justify="left",
        ).pack(padx=16, pady=12, anchor="w")

        # Botón cerrar
        ctk.CTkButton(
            self,
            text="Cerrar",
            command=self._cerrar,
            fg_color=TEMA.boton_neutro,
            hover_color=TEMA.borde,
            font=ctk.CTkFont(size=13),
            height=38,
            corner_radius=8,
            width=140,
        ).pack(pady=(12, 4))

        ctk.CTkLabel(
            self,
            text="Camilo Andrés León Rubriche  ·  UNAD",
            font=ctk.CTkFont(size=10),
            text_color=TEMA.texto_secundario,
        ).pack(pady=(0, 10))

    def _fila_ranking(self, parent: tk.Widget, pos: int, datos: dict) -> None:
        emojis_podio = {1: "🥇", 2: "🥈", 3: "🥉"}
        icono = emojis_podio.get(pos, f"#{pos}")
        color = TEMA.advertencia if pos <= 3 else TEMA.texto_secundario

        fila = ctk.CTkFrame(parent, fg_color=TEMA.fondo_card, corner_radius=8)
        fila.pack(padx=8, pady=3, fill="x")

        ctk.CTkLabel(
            fila,
            text=str(icono),
            font=ctk.CTkFont(size=16),
            text_color=color,
            width=40,
        ).pack(side="left", padx=(10, 6), pady=8)

        ctk.CTkLabel(
            fila,
            text=datos.get("nombre", "—"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEMA.texto_principal,
        ).pack(side="left", pady=8)

        ctk.CTkLabel(
            fila,
            text=datos.get("dificultad", "normal"),
            font=ctk.CTkFont(size=11),
            text_color=TEMA.texto_secundario,
        ).pack(side="left", padx=8, pady=8)

        ctk.CTkLabel(
            fila,
            text=f"{datos.get('puntaje', 0)} pts",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEMA.exito,
        ).pack(side="right", padx=14, pady=8)

    def _cerrar(self) -> None:
        if self._on_cerrar:
            self._on_cerrar()
        self.destroy()
