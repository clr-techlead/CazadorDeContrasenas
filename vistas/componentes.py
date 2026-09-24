"""
componentes.py — Widgets reutilizables personalizados.
Autor: Camilo Andrés León Rubriche — UNAD

Cada componente aquí hereda de un widget de CustomTkinter y añade
comportamiento o estilo adicional. Esto es herencia aplicada a la UI:
reutilizo la base de CTk y especializo para el juego.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

import customtkinter as ctk

from utils.colores import TEMA, COLOR_NIVEL, COLOR_COFRE
from utils.animaciones import parpadeo, animar_barra, pulsar_boton


# ── Tarjeta de estadística ────────────────────────────────────────────────────

class TarjetaStat(ctk.CTkFrame):
    """Muestra una métrica con etiqueta y valor grande.

    Herencia: extiende CTkFrame añadiendo dos labels con jerarquía visual.
    """

    def __init__(
        self,
        parent: tk.Widget,
        titulo: str,
        valor: str = "0",
        color_acento: str = TEMA.texto_acento,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            fg_color=TEMA.fondo_card,
            corner_radius=12,
            **kwargs,
        )

        self._lbl_titulo = ctk.CTkLabel(
            self,
            text=titulo,
            font=ctk.CTkFont(size=11, weight="normal"),
            text_color=TEMA.texto_secundario,
        )
        self._lbl_titulo.pack(padx=14, pady=(10, 2), anchor="w")

        self._lbl_valor = ctk.CTkLabel(
            self,
            text=valor,
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=color_acento,
        )
        self._lbl_valor.pack(padx=14, pady=(0, 10), anchor="w")

    def actualizar(self, nuevo_valor: str) -> None:
        """Actualiza el valor con un parpadeo suave."""
        self._lbl_valor.configure(text=nuevo_valor)
        parpadeo(self._lbl_valor, TEMA.texto_acento, TEMA.texto_principal, veces=2)


# ── Indicador de nivel de seguridad ──────────────────────────────────────────

class IndicadorNivel(ctk.CTkFrame):
    """Barra de progreso coloreada con etiqueta de nivel."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        super().__init__(
            parent,
            fg_color=TEMA.fondo_card,
            corner_radius=10,
            **kwargs,
        )

        ctk.CTkLabel(
            self,
            text="NIVEL DE SEGURIDAD",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEMA.texto_secundario,
        ).pack(padx=12, pady=(8, 4), anchor="w")

        self._barra = ctk.CTkProgressBar(
            self,
            height=12,
            corner_radius=6,
            fg_color=TEMA.fondo_input,
            progress_color=TEMA.barra_progreso,
        )
        self._barra.set(0)
        self._barra.pack(padx=12, pady=(0, 4), fill="x")

        self._lbl_nivel = ctk.CTkLabel(
            self,
            text="—",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEMA.texto_secundario,
        )
        self._lbl_nivel.pack(padx=12, pady=(0, 8), anchor="w")

    def actualizar(self, nivel: str, puntaje: int) -> None:
        # Si el nivel es el placeholder inicial, sólo resetea visualmente
        if nivel == "—" or not nivel:
            self._barra.configure(progress_color=TEMA.borde)
            self._barra.set(0)
            self._lbl_nivel.configure(text="—", text_color=TEMA.texto_secundario)
            return
        color = COLOR_NIVEL.get(nivel, TEMA.texto_acento)
        self._barra.configure(progress_color=color)
        animar_barra(self._barra, max(0.0, min(1.0, puntaje / 100)))
        self._lbl_nivel.configure(text=f"{nivel}  ({puntaje}/100)", text_color=color)


# ── Panel de cofre ────────────────────────────────────────────────────────────

class PanelCofre(ctk.CTkFrame):
    """Muestra el cofre obtenido con su emoji, nombre y descripción."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        super().__init__(
            parent,
            fg_color=TEMA.fondo_panel,
            corner_radius=16,
            border_width=1,
            border_color=TEMA.borde,
            **kwargs,
        )
        self._color_actual = TEMA.fondo_panel

        self._emoji_lbl = ctk.CTkLabel(
            self,
            text="🔒",
            font=ctk.CTkFont(size=52),
        )
        self._emoji_lbl.pack(pady=(20, 4))

        self._nombre_lbl = ctk.CTkLabel(
            self,
            text="Esperando tu clave...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEMA.texto_principal,
        )
        self._nombre_lbl.pack(pady=(0, 4))

        self._puntos_lbl = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=TEMA.texto_acento,
        )
        self._puntos_lbl.pack(pady=(0, 4))

        self._desc_lbl = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=TEMA.texto_secundario,
            wraplength=280,
        )
        self._desc_lbl.pack(pady=(0, 8))

        self._msg_lbl = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color=TEMA.texto_principal,
            wraplength=280,
        )
        self._msg_lbl.pack(pady=(0, 20))

    def mostrar_resultado(
        self,
        emoji: str,
        nombre: str,
        puntos: int,
        descripcion: str,
        mensaje: str,
        color_hex: str,
    ) -> None:
        signo = "+" if puntos >= 0 else ""
        self._emoji_lbl.configure(text=emoji)
        self._nombre_lbl.configure(text=nombre, text_color=color_hex)
        self._puntos_lbl.configure(
            text=f"{signo}{puntos} pts",
            text_color=color_hex if puntos >= 0 else TEMA.error,
        )
        self._desc_lbl.configure(text=descripcion)
        self._msg_lbl.configure(text=mensaje)
        self.configure(border_color=color_hex)
        parpadeo(self, TEMA.fondo_panel, color_hex + "33", veces=3, atributo="fg_color")

    def mostrar_suspenso(self) -> None:
        """Estado intermedio: contraseña generada, cofre esperando ser abierto.

        El cofre parpadea suavemente para generar suspenso visual.
        El jugador debe hacer clic en 'ABRIR COFRE' para revelar el resultado.
        """
        self._emoji_lbl.configure(text="🔒")
        self._nombre_lbl.configure(
            text="¿Qué habrá adentro...?",
            text_color=TEMA.advertencia,
        )
        self._puntos_lbl.configure(text="")
        self._desc_lbl.configure(text="Presiona  🔓 ABRIR COFRE  para descubrirlo.")
        self._msg_lbl.configure(text="")
        self.configure(border_color=TEMA.advertencia)
        # Parpadeo de borde para llamar la atención sin ser invasivo
        parpadeo(self, TEMA.fondo_panel, TEMA.advertencia + "22", veces=4, atributo="fg_color")

    def resetear(self) -> None:
        self._emoji_lbl.configure(text="🔒")
        self._nombre_lbl.configure(text="Esperando tu clave...", text_color=TEMA.texto_principal)
        self._puntos_lbl.configure(text="")
        self._desc_lbl.configure(text="")
        self._msg_lbl.configure(text="")
        self.configure(border_color=TEMA.borde)


# ── Botón principal estilizado ────────────────────────────────────────────────

class BotonPrincipal(ctk.CTkButton):
    """Botón con hover personalizado y efecto de pulso al hacer clic."""

    def __init__(
        self,
        parent: tk.Widget,
        texto: str,
        comando: Callable,
        color: str = TEMA.boton_primario,
        color_hover: str = TEMA.boton_primario_hover,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            text=texto,
            command=self._on_click,
            fg_color=color,
            hover_color=color_hover,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=44,
            corner_radius=10,
            **kwargs,
        )
        self._comando_real = comando
        self._color = color
        self._color_hover = color_hover

    def _on_click(self) -> None:
        pulsar_boton(self, "#ffffff22", self._color, duracion=100)
        self._comando_real()


# ── Lista de historial ────────────────────────────────────────────────────────

class FilaHistorial(ctk.CTkFrame):
    """Una fila del historial de rondas con colores por tipo de cofre."""

    def __init__(
        self,
        parent: tk.Widget,
        datos: dict,
        **kwargs,
    ) -> None:
        rareza = datos.get("rareza", "común")
        color_borde = COLOR_COFRE.get(rareza, TEMA.borde)

        super().__init__(
            parent,
            fg_color=TEMA.fondo_card,
            corner_radius=8,
            border_width=1,
            border_color=color_borde,
            **kwargs,
        )

        # Columna izquierda: ronda y cofre
        izq = ctk.CTkFrame(self, fg_color="transparent")
        izq.pack(side="left", padx=10, pady=6, fill="y")

        ctk.CTkLabel(
            izq,
            text=f"Ronda {datos.get('ronda', '?')}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEMA.texto_principal,
        ).pack(anchor="w")

        ctk.CTkLabel(
            izq,
            text=datos.get("tipo_cofre", ""),
            font=ctk.CTkFont(size=10),
            text_color=color_borde,
        ).pack(anchor="w")

        # Columna derecha: puntos y nivel
        der = ctk.CTkFrame(self, fg_color="transparent")
        der.pack(side="right", padx=10, pady=6, fill="y")

        puntos = datos.get("puntos", 0)
        signo  = "+" if puntos >= 0 else ""
        color_pts = TEMA.exito if puntos >= 0 else TEMA.error

        ctk.CTkLabel(
            der,
            text=f"{signo}{puntos}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=color_pts,
        ).pack(anchor="e")

        ctk.CTkLabel(
            der,
            text=datos.get("nivel_seguridad", ""),
            font=ctk.CTkFont(size=10),
            text_color=COLOR_NIVEL.get(datos.get("nivel_seguridad", ""), TEMA.texto_secundario),
        ).pack(anchor="e")


# ── Badge de logro ────────────────────────────────────────────────────────────

class BadgeLogro(ctk.CTkFrame):
    """Pequeña tarjeta que muestra un logro desbloqueado."""

    def __init__(self, parent: tk.Widget, logro_data: dict, **kwargs) -> None:
        super().__init__(
            parent,
            fg_color=TEMA.fondo_card,
            corner_radius=8,
            border_width=1,
            border_color=TEMA.advertencia,
            **kwargs,
        )
        ctk.CTkLabel(
            self,
            text=f"{logro_data.get('icono', '🏆')}  {logro_data.get('nombre', '')}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEMA.advertencia,
        ).pack(padx=10, pady=(6, 2), anchor="w")

        ctk.CTkLabel(
            self,
            text=logro_data.get("descripcion", ""),
            font=ctk.CTkFont(size=11),
            text_color=TEMA.texto_secundario,
        ).pack(padx=10, pady=(0, 6), anchor="w")
