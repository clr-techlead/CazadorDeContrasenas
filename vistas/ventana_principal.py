"""
ventana_principal.py — Ventana raíz de la aplicación.
Autor: Camilo Andrés León Rubriche — UNAD

Gestiona el ciclo de vida de la ventana, la pantalla de inicio y la
transición al panel de juego. También coordina el controlador.
"""

from __future__ import annotations

import tkinter as tk
from typing import Optional

import customtkinter as ctk

from utils.colores import TEMA
from utils.constantes import MENSAJES_INICIO, LOGROS
from utils.helpers import elegir_aleatorio
from utils.animaciones import callback_con_delay, parpadeo
from vistas.panel_juego import PanelJuego
from vistas.panel_ranking import VentanaRanking
from controladores import JuegoControlador, ValidacionesControlador
from excepciones import (
    LongitudInvalidaError,
    EntradaNoNumericaError,
    ContrasenaInvalidaError,
    CaracterRepetidoError,
    ErrorJuego,
)


class VentanaPrincipal(ctk.CTk):
    """Ventana raíz: gestiona pantallas y el controlador del juego.

    Herencia de ctk.CTk: extiende la ventana principal de CustomTkinter
    para añadir configuración de tema, icono y gestión de pantallas.
    """

    def __init__(self) -> None:
        super().__init__()

        # Configuración de CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Cazador de Contraseñas")
        self.geometry("1000x680")
        self.minsize(900, 620)
        self.configure(fg_color=TEMA.fondo_principal)

        # Centrar en pantalla
        self._centrar_ventana(1000, 680)

        self._controlador: Optional[JuegoControlador] = None
        self._panel_juego: Optional[PanelJuego] = None
        self._ventana_ranking: Optional[VentanaRanking] = None
        self._validaciones = ValidacionesControlador()

        self._mostrar_pantalla_inicio()

    def _centrar_ventana(self, ancho: int, alto: int) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth()  // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto  // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    # ── Pantalla de inicio ───────────────────────────────────────────────────

    def _mostrar_pantalla_inicio(self) -> None:
        """Pantalla de bienvenida con selector de nombre y dificultad."""
        self._limpiar_ventana()

        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / título
        ctk.CTkLabel(
            marco,
            text="🔑",
            font=ctk.CTkFont(size=72),
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            marco,
            text="CAZADOR DE CONTRASEÑAS",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=TEMA.texto_acento,
        ).pack()

        ctk.CTkLabel(
            marco,
            text="Genera claves seguras · Abre cofres · Conquista el ranking",
            font=ctk.CTkFont(size=14),
            text_color=TEMA.texto_secundario,
        ).pack(pady=(4, 24))

        # Mensaje dinámico
        self._lbl_bienvenida = ctk.CTkLabel(
            marco,
            text=elegir_aleatorio(MENSAJES_INICIO),
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color=TEMA.texto_principal,
        )
        self._lbl_bienvenida.pack(pady=(0, 20))

        # Formulario
        form = ctk.CTkFrame(marco, fg_color=TEMA.fondo_panel, corner_radius=16)
        form.pack(padx=40, pady=0, ipadx=20, ipady=16)

        ctk.CTkLabel(
            form,
            text="Tu nombre de cazador",
            font=ctk.CTkFont(size=13),
            text_color=TEMA.texto_secundario,
        ).pack(padx=30, pady=(16, 4), anchor="w")

        self._entry_nombre = ctk.CTkEntry(
            form,
            placeholder_text="Ej: ShadowHunter42",
            width=320,
            fg_color=TEMA.fondo_input,
            border_color=TEMA.borde,
            text_color=TEMA.texto_principal,
            font=ctk.CTkFont(size=14),
        )
        self._entry_nombre.pack(padx=30, pady=(0, 14))

        ctk.CTkLabel(
            form,
            text="Dificultad",
            font=ctk.CTkFont(size=13),
            text_color=TEMA.texto_secundario,
        ).pack(padx=30, anchor="w")

        self._dificultad_var = ctk.StringVar(value="normal")
        difs = [("😌 Fácil", "fácil"), ("⚔️ Normal", "normal"),
                ("💀 Difícil", "difícil"), ("☠️ Extremo", "extremo")]

        fila_dif = ctk.CTkFrame(form, fg_color="transparent")
        fila_dif.pack(padx=30, pady=(6, 16), fill="x")

        for texto, valor in difs:
            ctk.CTkRadioButton(
                fila_dif,
                text=texto,
                variable=self._dificultad_var,
                value=valor,
                text_color=TEMA.texto_principal,
                fg_color=TEMA.texto_acento,
                hover_color=TEMA.boton_primario_hover,
                font=ctk.CTkFont(size=12),
            ).pack(side="left", padx=8)

        # Error label
        self._lbl_error_inicio = ctk.CTkLabel(
            form, text="", font=ctk.CTkFont(size=12), text_color=TEMA.error
        )
        self._lbl_error_inicio.pack()

        # Botón iniciar
        ctk.CTkButton(
            form,
            text="⚡  COMENZAR A CAZAR",
            command=self._iniciar_juego,
            fg_color=TEMA.boton_primario,
            hover_color=TEMA.boton_primario_hover,
            font=ctk.CTkFont(size=15, weight="bold"),
            height=48,
            corner_radius=10,
            width=320,
        ).pack(padx=30, pady=(0, 16))

        # Bind Enter
        self._entry_nombre.bind("<Return>", lambda e: self._iniciar_juego())

        # Firma del autor — esquina inferior izquierda
        ctk.CTkLabel(
            self,
            text="Camilo Andrés León Rubriche  ·  UNAD",
            font=ctk.CTkFont(size=10),
            text_color=TEMA.texto_secundario,
        ).place(relx=0.0, rely=1.0, anchor="sw", x=12, y=-8)

        # Versión — esquina inferior derecha
        ctk.CTkLabel(
            self,
            text="v1.0  ·  Python 3.12  ·  CustomTkinter",
            font=ctk.CTkFont(size=10),
            text_color=TEMA.texto_secundario,
        ).place(relx=1.0, rely=1.0, anchor="se", x=-12, y=-8)

    def _iniciar_juego(self) -> None:
        nombre = self._entry_nombre.get()
        try:
            nombre = self._validaciones.validar_nombre(nombre)
        except Exception:
            nombre = "Cazador"

        dificultad = self._dificultad_var.get()

        # Crear controlador con el nombre y dificultad elegidos
        self._controlador = JuegoControlador(
            nombre_jugador=nombre,
            dificultad=dificultad,
        )
        self._controlador.set_callback_logro(self._notificar_logro)

        self._mostrar_panel_juego()

    # ── Panel de juego ───────────────────────────────────────────────────────

    def _mostrar_panel_juego(self) -> None:
        self._limpiar_ventana()

        self._panel_juego = PanelJuego(
            self,
            on_generar       = self._on_generar,
            on_abrir_cofre   = self._on_abrir_cofre,
            on_nueva_partida = self._on_nueva_partida,
            on_ver_ranking   = self._abrir_ranking,
            on_salir         = self._on_salir,
        )
        self._panel_juego.pack(fill="both", expand=True)

    # ── Callbacks del panel de juego ─────────────────────────────────────────

    def _on_generar(self, texto_longitud: str) -> None:
        """PASO 1 — Genera la contraseña y actualiza la UI. No abre el cofre."""
        if self._controlador is None:
            return

        try:
            contrasena = self._controlador.generar_contrasena(texto_longitud)

        except EntradaNoNumericaError as e:
            self._panel_juego.mostrar_error(str(e))
            return

        except LongitudInvalidaError as e:
            self._panel_juego.mostrar_error(str(e))
            return

        except ErrorJuego as e:
            self._panel_juego.mostrar_error(str(e))
            return

        except Exception as e:
            self._panel_juego.mostrar_error(f"Error inesperado: {e}")
            return

        else:
            # Mostrar contraseña + activar el botón "ABRIR COFRE"
            self._panel_juego.mostrar_contrasena_generada(
                valor   = contrasena.valor,
                nivel   = contrasena.nivel_seguridad,
                puntaje = contrasena.puntaje_seguridad,
            )

        finally:
            pass

    def _on_abrir_cofre(self) -> None:
        """PASO 2 — Abre el cofre y revela el resultado."""
        if self._controlador is None:
            return

        try:
            resultado = self._controlador.abrir_cofre()

        except ErrorJuego as e:
            self._panel_juego.mostrar_error(str(e))
            return

        except Exception as e:
            self._panel_juego.mostrar_error(f"Error inesperado: {e}")
            return

        else:
            self._panel_juego.mostrar_resultado(resultado)
            self._panel_juego.actualizar_racha(
                self._controlador.jugador.estadisticas.racha_sin_maldito
            )

        finally:
            pass

    def _on_nueva_partida(self) -> None:
        """Termina la partida actual, guarda datos y vuelve a inicio."""
        if self._controlador:
            self._controlador.terminar_partida()
        self._mostrar_pantalla_inicio()

    def _on_salir(self) -> None:
        """Termina la partida, guarda datos y cierra la aplicación limpiamente."""
        if self._controlador:
            try:
                self._controlador.terminar_partida()
            except Exception:
                pass
        # destroy() es suficiente para cerrar la ventana y detener el mainloop.
        # Llamar quit() antes puede generar errores de «ventana destruida» en tkinter.
        self.destroy()

    # ── Ranking ──────────────────────────────────────────────────────────────

    def _abrir_ranking(self) -> None:
        if self._ventana_ranking and self._ventana_ranking.winfo_exists():
            self._ventana_ranking.focus()
            return

        ranking     = self._controlador.obtener_ranking() if self._controlador else []
        stats_texto = self._controlador.obtener_estadisticas_globales() if self._controlador else ""

        self._ventana_ranking = VentanaRanking(
            self,
            ranking      = ranking,
            stats_texto  = stats_texto,
            on_cerrar    = lambda: None,
        )

    # ── Notificación de logros ────────────────────────────────────────────────

    def _notificar_logro(self, logro_id: str) -> None:
        """Muestra un popup de logro desbloqueado."""
        if logro_id not in LOGROS:
            return
        logro = LOGROS[logro_id]
        popup = ctk.CTkToplevel(self)
        popup.title("¡Logro desbloqueado!")
        popup.geometry("340x160")
        popup.resizable(False, False)
        popup.configure(fg_color=TEMA.fondo_panel)

        # Centrar sobre la ventana principal
        x = self.winfo_x() + (self.winfo_width()  // 2) - 170
        y = self.winfo_y() + (self.winfo_height() // 2) - 80
        popup.geometry(f"+{x}+{y}")
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text=f"{logro['icono']}  ¡Logro desbloqueado!",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEMA.advertencia,
        ).pack(pady=(20, 6))

        ctk.CTkLabel(
            popup,
            text=logro["nombre"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEMA.texto_principal,
        ).pack()

        ctk.CTkLabel(
            popup,
            text=logro["descripcion"],
            font=ctk.CTkFont(size=12),
            text_color=TEMA.texto_secundario,
        ).pack(pady=(4, 12))

        ctk.CTkButton(
            popup,
            text="OK",
            command=popup.destroy,
            fg_color=TEMA.boton_primario,
            hover_color=TEMA.boton_primario_hover,
            width=100,
            height=32,
        ).pack()

        # Auto-cerrar después de 4 segundos
        callback_con_delay(popup, 4000, lambda: popup.destroy() if popup.winfo_exists() else None)

    # ── Utilidades ───────────────────────────────────────────────────────────

    def _limpiar_ventana(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self._panel_juego = None
