"""
config.py — Configuración global de la aplicación.

Centralizar la configuración aquí permite cambiar parámetros sin tocar
el código de lógica. En un proyecto real esto podría leer desde un .env
o desde un archivo de configuración del usuario.
"""

from pathlib import Path

# ── Rutas base ────────────────────────────────────────────────────────────────

BASE_DIR: Path = Path(__file__).parent.resolve()
DATA_DIR: Path = BASE_DIR / "data"
ASSETS_DIR: Path = BASE_DIR / "assets"

# ── Aplicación ────────────────────────────────────────────────────────────────

APP_NOMBRE: str    = "Cazador de Contraseñas"
APP_VERSION: str   = "1.0.0"
APP_AUTOR: str     = "Camilo Andrés León Rubriche"
APP_INSTITUCION: str = "Universidad Nacional Abierta y a Distancia — UNAD"
APP_CURSO: str     = "Programación — Cuarto semestre"
APP_DESCRIPCION: str = (
    "Juego educativo que combina generación de contraseñas seguras "
    "con mecánicas de cofres y sistema de puntuación."
)

# ── UI ────────────────────────────────────────────────────────────────────────

VENTANA_ANCHO: int  = 1000
VENTANA_ALTO: int   = 680
VENTANA_MIN_ANCHO: int = 900
VENTANA_MIN_ALTO: int  = 620
TEMA_COLOR: str    = "dark"
TEMA_CTK: str      = "dark-blue"

# ── Juego ─────────────────────────────────────────────────────────────────────

SONIDO_HABILITADO_DEFAULT: bool = True
MAX_HISTORIAL_SESION: int       = 100
