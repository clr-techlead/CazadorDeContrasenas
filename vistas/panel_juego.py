"""
panel_juego.py — Panel principal donde se desarrolla el juego.
Autor: Camilo Andrés León Rubriche — UNAD

Flujo de dos pasos:
  PASO 1 — "⚡ GENERAR CONTRASEÑA": genera y muestra la clave + nivel de seguridad.
           El cofre permanece cerrado y aparece el botón de apertura.
  PASO 2 — "🔓 ABRIR COFRE": revela el cofre con animación de suspenso.
           Vuelve al estado inicial para una nueva ronda.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

import customtkinter as ctk

from utils.colores import TEMA, COLOR_NIVEL, COLOR_COFRE
from utils.constantes import MINIMO_LONGITUD, MAXIMO_LONGITUD, LOGROS
from utils.animaciones import parpadeo, animar_barra, callback_con_delay
from vistas.componentes import (
    TarjetaStat,
    IndicadorNivel,
    PanelCofre,
    BotonPrincipal,
    FilaHistorial,
    BadgeLogro,
)
from controladores import ResultadoRonda


# Estados internos del panel — máquina de estados simple
_ESTADO_INICIAL    = "inicial"     # sin contraseña generada
_ESTADO_GENERADO   = "generado"    # contraseña visible, cofre cerrado
_ESTADO_ABIERTO    = "abierto"     # cofre revelado, esperando nueva ronda


class PanelJuego(ctk.CTkFrame):
    """Panel central del juego. Implementa la máquina de estados de dos pasos.

    Estado inicial  → [GENERAR] → Estado generado → [ABRIR COFRE] → Estado abierto
                                                                           ↓
                                             ← ← ← ← ← ← ← ← ← ← ← [GENERAR]

    La vista no conoce el dominio: recibe datos crudos y llama callbacks.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_generar:       Callable[[str], None],
        on_abrir_cofre:   Callable[[], None],
        on_nueva_partida: Callable[[], None],
        on_ver_ranking:   Callable[[], None],
        on_salir:         Callable[[], None],
        **kwargs,
    ) -> None:
        super().__init__(parent, fg_color=TEMA.fondo_principal, **kwargs)

        self._on_generar      = on_generar
        self._on_abrir_cofre  = on_abrir_cofre
        self._on_nueva_partida = on_nueva_partida
        self._on_ver_ranking  = on_ver_ranking
        self._on_salir        = on_salir

        self._estado: str = _ESTADO_INICIAL
        self._filas_historial: list[FilaHistorial] = []
        self._logros_mostrados: set[str] = set()

        self._construir_ui()

    # ── Construcción de la UI ────────────────────────────────────────────────

    def _construir_ui(self) -> None:
        # ── Header ──────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=TEMA.fondo_panel, corner_radius=0)
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text="🔑  CAZADOR DE CONTRASEÑAS",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEMA.texto_acento,
        ).pack(side="left", padx=20, pady=14)

        stats_frame = ctk.CTkFrame(header, fg_color="transparent")
        stats_frame.pack(side="right", padx=20, pady=8)

        self._stat_puntos = TarjetaStat(stats_frame, "PUNTOS", "0",
                                         color_acento=TEMA.texto_acento, width=110)
        self._stat_puntos.pack(side="left", padx=4)

        self._stat_rondas = TarjetaStat(stats_frame, "RONDAS", "0",
                                         color_acento=TEMA.exito, width=90)
        self._stat_rondas.pack(side="left", padx=4)

        self._stat_racha = TarjetaStat(stats_frame, "RACHA", "0",
                                        color_acento=TEMA.advertencia, width=90)
        self._stat_racha.pack(side="left", padx=4)

        # ── Cuerpo ──────────────────────────────────────────────────────────
        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=16, pady=12)

        col_izq = ctk.CTkFrame(cuerpo, fg_color="transparent")
        col_izq.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self._construir_panel_control(col_izq)
        self._construir_panel_historial(col_izq)

        col_der = ctk.CTkFrame(cuerpo, fg_color="transparent", width=320)
        col_der.pack(side="right", fill="both", padx=(8, 0))
        col_der.pack_propagate(False)

        self._construir_panel_cofre(col_der)

    def _construir_panel_control(self, parent: tk.Widget) -> None:
        """Controles de longitud y los dos botones del flujo principal."""
        frame = ctk.CTkFrame(parent, fg_color=TEMA.fondo_panel, corner_radius=12)
        frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            frame,
            text="CONFIGURAR CONTRASEÑA",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEMA.texto_secundario,
        ).pack(padx=16, pady=(14, 6), anchor="w")

        # Longitud
        fila_long = ctk.CTkFrame(frame, fg_color="transparent")
        fila_long.pack(padx=16, pady=(0, 4), fill="x")

        ctk.CTkLabel(
            fila_long,
            text=f"Longitud ({MINIMO_LONGITUD}–{MAXIMO_LONGITUD}):",
            font=ctk.CTkFont(size=13),
            text_color=TEMA.texto_principal,
        ).pack(side="left")

        self._entry_longitud = ctk.CTkEntry(
            fila_long,
            width=70,
            fg_color=TEMA.fondo_input,
            border_color=TEMA.borde,
            text_color=TEMA.texto_principal,
            font=ctk.CTkFont(size=14),
            justify="center",
        )
        self._entry_longitud.insert(0, "12")
        self._entry_longitud.pack(side="right")
        self._entry_longitud.bind("<Return>", lambda e: self._disparar_generar())

        # Caracteres especiales disponibles
        ctk.CTkLabel(
            frame,
            text="Especiales: ¿¡?=)(/¨*+-%&$#!",
            font=ctk.CTkFont(family="Courier New", size=11),
            text_color=TEMA.texto_secundario,
        ).pack(padx=16, pady=(0, 10), anchor="w")

        # ── PASO 1: Botón generar ────────────────────────────────────────────
        self._btn_generar = BotonPrincipal(
            frame,
            texto="⚡  GENERAR CONTRASEÑA",
            comando=self._disparar_generar,
        )
        self._btn_generar.pack(padx=16, pady=(0, 6), fill="x")

        # ── PASO 2: Botón abrir cofre (inactivo hasta que se genere) ─────────
        self._btn_abrir = ctk.CTkButton(
            frame,
            text="🔒  ABRIR COFRE",
            command=self._disparar_abrir_cofre,
            fg_color=TEMA.fondo_input,
            hover_color=TEMA.advertencia,
            text_color=TEMA.texto_secundario,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=44,
            corner_radius=10,
            state="disabled",
        )
        self._btn_abrir.pack(padx=16, pady=(0, 6), fill="x")

        # Mensaje de estado / error
        self._lbl_estado = ctk.CTkLabel(
            frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=TEMA.advertencia,
            wraplength=340,
        )
        self._lbl_estado.pack(padx=16, pady=(0, 12))

        # ── Contraseña generada ───────────────────────────────────────────────
        frame_pwd = ctk.CTkFrame(parent, fg_color=TEMA.fondo_panel, corner_radius=12)
        frame_pwd.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            frame_pwd,
            text="CONTRASEÑA GENERADA",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEMA.texto_secundario,
        ).pack(padx=16, pady=(14, 6), anchor="w")

        fila_pwd = ctk.CTkFrame(frame_pwd, fg_color="transparent")
        fila_pwd.pack(padx=16, pady=(0, 6), fill="x")

        self._lbl_password = ctk.CTkLabel(
            fila_pwd,
            text="• • • • • • • • • •",
            font=ctk.CTkFont(family="Courier New", size=18, weight="bold"),
            text_color=TEMA.texto_acento,
        )
        self._lbl_password.pack(side="left", fill="x", expand=True)

        self._btn_copiar = ctk.CTkButton(
            fila_pwd,
            text="📋",
            width=36,
            height=30,
            corner_radius=7,
            fg_color=TEMA.boton_neutro,
            hover_color=TEMA.borde,
            font=ctk.CTkFont(size=14),
            command=self._copiar_contrasena,
            state="disabled",
        )
        self._btn_copiar.pack(side="right", padx=(8, 0))

        self._indicador_nivel = IndicadorNivel(frame_pwd)
        self._indicador_nivel.pack(padx=16, pady=(0, 14), fill="x")

        # ── Botones secundarios ───────────────────────────────────────────────
        fila_btns = ctk.CTkFrame(parent, fg_color="transparent")
        fila_btns.pack(fill="x", pady=(0, 6))

        ctk.CTkButton(
            fila_btns, text="🔄 Nueva partida",
            command=self._on_nueva_partida,
            fg_color=TEMA.boton_neutro, hover_color=TEMA.borde,
            font=ctk.CTkFont(size=12), height=36, corner_radius=8,
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        ctk.CTkButton(
            fila_btns, text="🏆 Ranking",
            command=self._on_ver_ranking,
            fg_color=TEMA.boton_neutro, hover_color=TEMA.borde,
            font=ctk.CTkFont(size=12), height=36, corner_radius=8,
        ).pack(side="left", fill="x", expand=True, padx=(4, 4))

        ctk.CTkButton(
            fila_btns, text="✖ Salir",
            command=self._on_salir,
            fg_color=TEMA.boton_peligro, hover_color=TEMA.boton_peligro_hover,
            font=ctk.CTkFont(size=12), height=36, corner_radius=8,
        ).pack(side="left", fill="x", expand=True, padx=(4, 0))

    def _construir_panel_historial(self, parent: tk.Widget) -> None:
        frame = ctk.CTkFrame(parent, fg_color=TEMA.fondo_panel, corner_radius=12)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            frame,
            text="HISTORIAL DE RONDAS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEMA.texto_secundario,
        ).pack(padx=16, pady=(14, 6), anchor="w")

        self._scroll_historial = ctk.CTkScrollableFrame(
            frame, fg_color="transparent",
            scrollbar_button_color=TEMA.borde,
        )
        self._scroll_historial.pack(padx=8, pady=(0, 12), fill="both", expand=True)

    def _construir_panel_cofre(self, parent: tk.Widget) -> None:
        self._panel_cofre = PanelCofre(parent)
        self._panel_cofre.pack(fill="x", pady=(0, 10))

        # Logros
        frame_logros = ctk.CTkFrame(parent, fg_color=TEMA.fondo_panel, corner_radius=12)
        frame_logros.pack(fill="both", expand=True)

        ctk.CTkLabel(
            frame_logros, text="LOGROS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEMA.texto_secundario,
        ).pack(padx=14, pady=(12, 6), anchor="w")

        self._scroll_logros = ctk.CTkScrollableFrame(
            frame_logros, fg_color="transparent",
            scrollbar_button_color=TEMA.borde, height=200,
        )
        self._scroll_logros.pack(padx=8, pady=(0, 10), fill="both", expand=True)

    # ── Máquina de estados ────────────────────────────────────────────────────

    def _set_estado_inicial(self) -> None:
        """Estado 0: sin contraseña. Sólo GENERAR activo."""
        self._estado = _ESTADO_INICIAL
        self._btn_generar.configure(
            state="normal",
            text="⚡  GENERAR CONTRASEÑA",
            fg_color=TEMA.boton_primario,
            hover_color=TEMA.boton_primario_hover,
            text_color=TEMA.texto_principal,
        )
        self._btn_abrir.configure(
            state="disabled",
            text="🔒  ABRIR COFRE",
            fg_color=TEMA.fondo_input,
            text_color=TEMA.texto_secundario,
        )
        self._entry_longitud.configure(state="normal")

    def _set_estado_generado(self, nivel: str) -> None:
        """Estado 1: contraseña visible, cofre esperando. ABRIR activo."""
        self._estado = _ESTADO_GENERADO
        color_nivel = COLOR_NIVEL.get(nivel, TEMA.texto_acento)

        # Bloquear generar mientras el cofre no se ha abierto
        self._btn_generar.configure(
            state="normal",   # permitir re-generar (descarta la anterior)
            text="🔄  REGENERAR",
            fg_color=TEMA.boton_neutro,
            hover_color=TEMA.borde,
            text_color=TEMA.texto_secundario,
        )
        # Activar el botón de abrir con color dinámico según el nivel
        self._btn_abrir.configure(
            state="normal",
            text="🔓  ABRIR COFRE",
            fg_color=color_nivel,
            hover_color=TEMA.advertencia,
            text_color="#0d1117",
        )
        # El panel del cofre muestra un estado de "suspenso" mientras espera
        self._panel_cofre.mostrar_suspenso()

    def _set_estado_abierto(self) -> None:
        """Estado 2: cofre revelado. Vuelve al estado inicial para nueva ronda."""
        self._estado = _ESTADO_ABIERTO
        self._btn_abrir.configure(
            state="disabled",
            text="✓  COFRE ABIERTO",
            fg_color=TEMA.exito,
            text_color="#0d1117",
        )
        # Restaurar el botón generar para la siguiente ronda
        self.after(1200, self._set_estado_inicial)

    # ── Disparadores ─────────────────────────────────────────────────────────

    def _disparar_generar(self) -> None:
        self._lbl_estado.configure(text="")
        texto = self._entry_longitud.get()
        self._on_generar(texto)

    def _disparar_abrir_cofre(self) -> None:
        if self._estado != _ESTADO_GENERADO:
            return
        self._on_abrir_cofre()

    def _copiar_contrasena(self) -> None:
        texto = self._lbl_password.cget("text")
        if texto and texto != "• • • • • • • • • •":
            try:
                self.clipboard_clear()
                self.clipboard_append(texto)
                self._btn_copiar.configure(text="✓", fg_color=TEMA.exito)
                self.after(1400, lambda: self._btn_copiar.configure(
                    text="📋", fg_color=TEMA.boton_neutro
                ))
            except Exception:
                self._btn_copiar.configure(text="✗", fg_color=TEMA.error)
                self.after(1400, lambda: self._btn_copiar.configure(
                    text="📋", fg_color=TEMA.boton_neutro
                ))

    # ── API pública: llamada desde ventana_principal ──────────────────────────

    def mostrar_contrasena_generada(self, valor: str, nivel: str, puntaje: int) -> None:
        """Actualiza la UI tras el PASO 1 (sólo contraseña, sin cofre)."""
        self._lbl_password.configure(text=valor)
        self._btn_copiar.configure(state="normal")
        self._indicador_nivel.actualizar(nivel, puntaje)
        self._set_estado_generado(nivel)

    def mostrar_resultado(self, resultado: ResultadoRonda) -> None:
        """Actualiza la UI tras el PASO 2 (cofre revelado)."""
        cofre = resultado.cofre
        self._panel_cofre.mostrar_resultado(
            emoji        = cofre.emoji,
            nombre       = cofre.nombre_cofre,
            puntos       = resultado.puntos_obtenidos,
            descripcion  = cofre.descripcion_visual,
            mensaje      = cofre.mensaje,
            color_hex    = cofre.color_hex,
        )

        self._stat_puntos.actualizar(str(resultado.puntaje_total))
        self._stat_rondas.actualizar(str(len(self._filas_historial) + 1))

        datos_fila = {
            "ronda":           len(self._filas_historial) + 1,
            "tipo_cofre":      cofre.nombre_cofre,
            "rareza":          cofre.rareza,
            "puntos":          resultado.puntos_obtenidos,
            "nivel_seguridad": resultado.nivel_seguridad,
        }
        fila = FilaHistorial(self._scroll_historial, datos_fila)
        fila.pack(fill="x", pady=3)
        self._filas_historial.append(fila)

        for logro_id in resultado.logros_nuevos:
            self._agregar_logro(logro_id)

        self._set_estado_abierto()

    def _agregar_logro(self, logro_id: str) -> None:
        if logro_id in self._logros_mostrados or logro_id not in LOGROS:
            return
        self._logros_mostrados.add(logro_id)
        badge = BadgeLogro(self._scroll_logros, LOGROS[logro_id])
        badge.pack(fill="x", pady=3)

    def mostrar_error(self, mensaje: str) -> None:
        self._lbl_estado.configure(text=f"⚠  {mensaje}", text_color=TEMA.error)
        parpadeo(self._lbl_estado, TEMA.error, TEMA.advertencia, veces=3)

    def mostrar_advertencia(self, mensaje: str) -> None:
        self._lbl_estado.configure(text=f"ℹ  {mensaje}", text_color=TEMA.advertencia)

    def actualizar_racha(self, racha: int) -> None:
        self._stat_racha.actualizar(str(racha))

    def resetear_panel(self) -> None:
        self._panel_cofre.resetear()
        self._lbl_password.configure(text="• • • • • • • • • •")
        self._btn_copiar.configure(state="disabled", text="📋", fg_color=TEMA.boton_neutro)
        self._lbl_estado.configure(text="")
        self._stat_puntos.actualizar("0")
        self._stat_rondas.actualizar("0")
        self._stat_racha.actualizar("0")
        for f in self._filas_historial:
            f.destroy()
        self._filas_historial.clear()
        for w in self._scroll_logros.winfo_children():
            w.destroy()
        self._logros_mostrados.clear()
        self._indicador_nivel.actualizar("—", 0)
        self._set_estado_inicial()
