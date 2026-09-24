"""
constantes.py — Valores fijos del dominio del juego.

Centralizar constantes evita «números mágicos» dispersos y facilita
ajustar el balance del juego sin tocar lógica de negocio.
"""

# ── Generación de contraseñas ────────────────────────────────────────────────

CARACTERES_ESPECIALES: str = "¿¡?=)(/¨*+-%&$#!"
MINIMO_LONGITUD: int = 8
MAXIMO_LONGITUD: int = 64

# ── Puntuación de cofres ─────────────────────────────────────────────────────

PUNTOS_COMUN: int       = 10
PUNTOS_RARO: int        = 25
PUNTOS_LEGENDARIO: int  = 50
PUNTOS_MALDITO: int     = -20

# ── Probabilidades de aparición de cofre (deben sumar 1.0) ──────────────────
# Ajustadas por dificultad en el controlador; estas son las del modo normal.
PROB_COMUN: float       = 0.50
PROB_RARO: float        = 0.30
PROB_LEGENDARIO: float  = 0.12
PROB_MALDITO: float     = 0.08

# ── Niveles de seguridad de contraseña ──────────────────────────────────────

NIVEL_DEBIL: int      = 0
NIVEL_MODERADO: int   = 1
NIVEL_FUERTE: int     = 2
NIVEL_EXTREMO: int    = 3

UMBRALES_NIVEL: dict[int, int] = {
    NIVEL_DEBIL:    0,
    NIVEL_MODERADO: 40,
    NIVEL_FUERTE:   65,
    NIVEL_EXTREMO:  85,
}

# ── Multiplicadores de puntos por dificultad ────────────────────────────────

MULTIPLICADORES: dict[str, float] = {
    "fácil":   0.8,
    "normal":  1.0,
    "difícil": 1.5,
    "extremo": 2.0,
}

# ── Persistencia ─────────────────────────────────────────────────────────────

ARCHIVO_RANKING: str   = "data/ranking.json"
ARCHIVO_HISTORIAL: str = "data/historial.json"

MAX_ENTRADAS_RANKING: int = 10

# ── Mensajes motivacionales ──────────────────────────────────────────────────

MENSAJES_EXITO: list[str] = [
    "¡Eso es! El cofre cedió ante tu astucia.",
    "Contraseña perfecta. Eres un cazador de élite.",
    "El sistema no pudo contigo. ¡Sigue así!",
    "Cada byte fue elegido con precisión. Impresionante.",
    "El cofre era tuyo desde el principio.",
    "Seguridad máxima, recompensa merecida.",
    "Tu lógica es imbatible hoy.",
]

MENSAJES_COFRE_MALDITO: list[str] = [
    "El cofre estaba maldito... pero la experiencia vale.",
    "A veces el azar juega en tu contra. Sigue intentando.",
    "Mala suerte, buen jugador. Vuelve con más fuerza.",
    "El cofre te robó puntos, pero no tu destreza.",
]

MENSAJES_INICIO: list[str] = [
    "Bienvenido, cazador. Los cofres te esperan.",
    "¿Listo para demostrar tu dominio sobre las claves?",
    "Cada contraseña es una llave. Encuéntrala.",
    "El algoritmo no miente. Tú tampoco deberías fallar.",
]

# ── Logros ───────────────────────────────────────────────────────────────────

LOGROS: dict[str, dict] = {
    "primera_sangre": {
        "nombre":      "Primera Sangre",
        "descripcion": "Abre tu primer cofre.",
        "icono":       "🗡️",
        "condicion":   "rondas_jugadas >= 1",
    },
    "coleccionista": {
        "nombre":      "Coleccionista",
        "descripcion": "Acumula 100 puntos.",
        "icono":       "💰",
        "condicion":   "puntaje_total >= 100",
    },
    "legendario": {
        "nombre":      "Legendario",
        "descripcion": "Obtén un cofre legendario.",
        "icono":       "👑",
        "condicion":   "cofres_legendarios >= 1",
    },
    "invicto": {
        "nombre":      "Invicto",
        "descripcion": "5 rondas seguidas sin cofre maldito.",
        "icono":       "🛡️",
        "condicion":   "racha_sin_maldito >= 5",
    },
    "maestro_clave": {
        "nombre":      "Maestro de Claves",
        "descripcion": "Genera 10 contraseñas de nivel Extremo.",
        "icono":       "🔐",
        "condicion":   "contrasenas_extremas >= 10",
    },
}
