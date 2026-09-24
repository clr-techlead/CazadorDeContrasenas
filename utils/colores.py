"""
colores.py — Paleta cromática del juego.

Separar los colores en un módulo propio permite cambiar el tema visual
sin tocar ningún widget. También facilita agregar temas en el futuro
(modo claro, alto contraste, etc.) simplemente swapeando este módulo.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Paleta:
    """Encapsula un conjunto coherente de colores para la UI."""

    # Fondos
    fondo_principal: str
    fondo_panel: str
    fondo_card: str
    fondo_input: str

    # Texto
    texto_principal: str
    texto_secundario: str
    texto_acento: str

    # Botones
    boton_primario: str
    boton_primario_hover: str
    boton_peligro: str
    boton_peligro_hover: str
    boton_neutro: str

    # Estado / feedback
    exito: str
    advertencia: str
    error: str
    info: str

    # Cofres
    comun: str
    raro: str
    legendario: str
    maldito: str

    # Barras y bordes
    borde: str
    barra_progreso: str
    separador: str


# ── Tema principal (oscuro, estilo cyberpunk suavizado) ──────────────────────

OSCURO = Paleta(
    fondo_principal  = "#0d1117",
    fondo_panel      = "#161b22",
    fondo_card       = "#1c2333",
    fondo_input      = "#21262d",

    texto_principal  = "#e6edf3",
    texto_secundario = "#8b949e",
    texto_acento     = "#58a6ff",

    boton_primario       = "#238636",
    boton_primario_hover = "#2ea043",
    boton_peligro        = "#da3633",
    boton_peligro_hover  = "#f85149",
    boton_neutro         = "#30363d",

    exito       = "#3fb950",
    advertencia = "#d29922",
    error       = "#f85149",
    info        = "#58a6ff",

    comun       = "#6e7681",
    raro        = "#388bfd",
    legendario  = "#d4a017",
    maldito     = "#8957e5",

    borde          = "#30363d",
    barra_progreso = "#238636",
    separador      = "#21262d",
)

# Alias por defecto
TEMA = OSCURO


# ── Colores por tipo de cofre (para animaciones y texto) ────────────────────

COLOR_COFRE: dict[str, str] = {
    "común":      OSCURO.comun,
    "raro":       OSCURO.raro,
    "legendario": OSCURO.legendario,
    "maldito":    OSCURO.maldito,
}

# ── Colores por nivel de seguridad ──────────────────────────────────────────

COLOR_NIVEL: dict[str, str] = {
    "Débil":    "#f85149",
    "Moderado": "#d29922",
    "Fuerte":   "#3fb950",
    "Extremo":  "#58a6ff",
}

# ── Gradientes simulados (inicio → fin para canvas) ─────────────────────────

GRADIENTE_LEGENDARIO = ("#d4a017", "#f5d478")
GRADIENTE_RARO       = ("#388bfd", "#79c0ff")
GRADIENTE_MALDITO    = ("#8957e5", "#d2a8ff")
