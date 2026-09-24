"""
animaciones.py — Efectos de animación para widgets CustomTkinter.

Las animaciones aquí son «animaciones de tick»: cada llamada programa
el siguiente frame con after(), de modo que no bloquean el hilo de UI.
El patrón es: función pública recibe el widget y los parámetros,
función interna _tick hace un paso y se re-programa a sí misma.
"""

import tkinter as tk
from typing import Callable


def parpadeo(
    widget: tk.Widget,
    color_a: str,
    color_b: str,
    veces: int = 4,
    intervalo: int = 120,
    atributo: str = "fg_color",
) -> None:
    """Alterna el color de fondo de un widget veces×2 veces.

    Útil para resaltar feedback sin ser invasivo.
    """
    restantes = [veces * 2]    # lista mutable para que _tick pueda modificarla
    color_original = [color_a]

    def _tick() -> None:
        if restantes[0] <= 0:
            # Restaurar color original al terminar
            try:
                widget.configure(**{atributo: color_original[0]})
            except Exception:
                pass
            return
        color_actual = color_b if restantes[0] % 2 == 0 else color_a
        try:
            widget.configure(**{atributo: color_actual})
        except Exception:
            return
        restantes[0] -= 1
        widget.after(intervalo, _tick)

    _tick()


def fade_texto(
    label: tk.Widget,
    texto_nuevo: str,
    pasos: int = 8,
    intervalo: int = 30,
) -> None:
    """Cambia el texto de un label con un efecto de «deslizamiento» simple.

    Borra carácter a carácter y luego escribe el nuevo texto.
    Funciona con CTkLabel mediante el método configure(text=...).
    """
    texto_viejo = [label.cget("text")]
    fase = ["salida"]     # "salida" → borramos, "entrada" → escribimos
    paso = [0]

    def _tick() -> None:
        if fase[0] == "salida":
            corte = len(texto_viejo[0]) - paso[0]
            if corte < 0:
                corte = 0
            fragmento = texto_viejo[0][:corte]
            try:
                label.configure(text=fragmento)
            except Exception:
                return
            paso[0] += max(1, len(texto_viejo[0]) // pasos)
            if corte == 0:
                fase[0] = "entrada"
                paso[0] = 0
                texto_viejo[0] = texto_nuevo
            label.after(intervalo, _tick)
        else:
            corte = paso[0]
            fragmento = texto_nuevo[:corte]
            try:
                label.configure(text=fragmento)
            except Exception:
                return
            paso[0] += max(1, len(texto_nuevo) // pasos)
            if corte >= len(texto_nuevo):
                try:
                    label.configure(text=texto_nuevo)
                except Exception:
                    pass
                return
            label.after(intervalo, _tick)

    _tick()


def animar_barra(
    progressbar: tk.Widget,
    valor_objetivo: float,
    pasos: int = 20,
    intervalo: int = 20,
) -> None:
    """Mueve suavemente una barra de progreso de su valor actual al objetivo.

    valor_objetivo debe estar en [0.0, 1.0] (CustomTkinter CTkProgressBar).
    """
    try:
        valor_actual = [progressbar.get()]
    except Exception:
        valor_actual = [0.0]

    delta = (valor_objetivo - valor_actual[0]) / max(pasos, 1)

    def _tick() -> None:
        valor_actual[0] += delta
        # Evitar sobrepasar el objetivo por errores de coma flotante
        if (delta > 0 and valor_actual[0] >= valor_objetivo) or \
           (delta < 0 and valor_actual[0] <= valor_objetivo):
            try:
                progressbar.set(valor_objetivo)
            except Exception:
                pass
            return
        try:
            progressbar.set(max(0.0, min(1.0, valor_actual[0])))
        except Exception:
            return
        progressbar.after(intervalo, _tick)

    _tick()


def shake(widget: tk.Widget, distancia: int = 6, repeticiones: int = 3) -> None:
    """Mueve un widget horizontalmente (shake) para indicar error.

    Usa place_configure si el widget usa place(), si no, simplemente
    ignora el efecto sin lanzar excepción.
    """
    try:
        x_orig = widget.winfo_x()
        y_orig = widget.winfo_y()
    except Exception:
        return

    pasos = repeticiones * 4
    contador = [0]
    offsets = [distancia, 0, -distancia, 0] * repeticiones

    def _tick() -> None:
        if contador[0] >= pasos:
            try:
                widget.place_configure(x=x_orig, y=y_orig)
            except Exception:
                pass
            return
        try:
            widget.place_configure(x=x_orig + offsets[contador[0]], y=y_orig)
        except Exception:
            return
        contador[0] += 1
        widget.after(40, _tick)

    _tick()


def pulsar_boton(
    boton: tk.Widget,
    color_flash: str,
    color_original: str,
    duracion: int = 200,
) -> None:
    """Destella el botón brevemente al hacer clic para dar feedback táctil visual."""
    try:
        boton.configure(fg_color=color_flash)
        boton.after(duracion, lambda: boton.configure(fg_color=color_original))
    except Exception:
        pass


def callback_con_delay(
    widget: tk.Widget,
    delay_ms: int,
    fn: Callable,
) -> None:
    """Ejecuta fn después de delay_ms milisegundos usando el scheduler de Tkinter."""
    widget.after(delay_ms, fn)
