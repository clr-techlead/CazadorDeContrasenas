"""
excepciones.py — Jerarquía de excepciones del juego.
Autor: Camilo Andrés León Rubriche — UNAD

Diseñé esta jerarquía para que los errores del dominio sean distinguibles
de los errores estándar de Python. Esto permite capturar sólo lo que
realmente nos interesa en cada capa sin mezclar lógica de negocio con
errores del sistema operativo o de la biblioteca estándar.
"""

# ── Raíz de la jerarquía ────────────────────────────────────────────────────

class ErrorJuego(Exception):
    """Base de todas las excepciones del juego.

    Heredar de Exception (en lugar de BaseException) garantiza que un
    'except Exception' genérico la capture, pero podemos filtrarla con
    'except ErrorJuego' cuando necesitemos ser precisos.
    """

    def __init__(self, mensaje: str, codigo: int = 0) -> None:
        super().__init__(mensaje)
        self.codigo = codigo          # útil para logging o telemetría futura
        self.mensaje = mensaje

    def __str__(self) -> str:        # polimorfismo: cada subclase puede sobreescribir
        return f"[Error {self.codigo}] {self.mensaje}"


# ── Errores de validación ────────────────────────────────────────────────────

class ErrorValidacion(ErrorJuego):
    """Agrupa todos los errores que surgen de validar entradas o reglas."""

    def __init__(self, mensaje: str, campo: str = "") -> None:
        super().__init__(mensaje, codigo=100)
        self.campo = campo           # qué campo falló (útil para resaltar en la GUI)


class LongitudInvalidaError(ErrorValidacion):
    """La longitud pedida no cumple el mínimo o máximo permitido.

    Se lanza antes de intentar cualquier generación, para no desperdiciar
    ciclos de CPU en un parámetro inviable.
    """

    MINIMO = 8
    MAXIMO = 64

    def __init__(self, longitud: int) -> None:
        super().__init__(
            mensaje=f"Longitud {longitud} fuera de rango [{self.MINIMO}–{self.MAXIMO}].",
            campo="longitud",
        )
        self.longitud = longitud

    def __str__(self) -> str:
        return (
            f"La longitud '{self.longitud}' no es válida. "
            f"Debe estar entre {self.MINIMO} y {self.MAXIMO} caracteres."
        )


class EntradaNoNumericaError(ErrorValidacion):
    """El usuario escribió algo que no es un número donde se esperaba uno."""

    def __init__(self, valor: str) -> None:
        super().__init__(
            mensaje=f"Se esperaba un número pero se recibió: '{valor}'",
            campo="entrada",
        )
        self.valor = valor

    def __str__(self) -> str:
        return f"Entrada inválida: '{self.valor}' no es un número entero."


class ContrasenaInvalidaError(ErrorValidacion):
    """La contraseña generada o proporcionada no cumple las reglas de seguridad.

    Incluye el detalle de cuáles reglas fallaron para mostrarlo en la UI.
    """

    def __init__(self, mensaje: str, reglas_fallidas: list[str] | None = None) -> None:
        super().__init__(mensaje, campo="contrasena")
        self.reglas_fallidas: list[str] = reglas_fallidas or []

    def __str__(self) -> str:
        detalle = ", ".join(self.reglas_fallidas) if self.reglas_fallidas else "sin detalle"
        return f"Contraseña inválida. Reglas fallidas: {detalle}."


class CaracterRepetidoError(ErrorValidacion):
    """La contraseña contiene al menos un carácter duplicado.

    Separé esto de ContrasenaInvalidaError porque es una regla de negocio
    distinta y queremos mostrar exactamente qué carácter se repitió.
    """

    def __init__(self, caracter: str) -> None:
        super().__init__(
            mensaje=f"El carácter '{caracter}' aparece más de una vez.",
            campo="contrasena",
        )
        self.caracter = caracter

    def __str__(self) -> str:
        return f"Carácter repetido detectado: '{self.caracter}'. Cada símbolo debe ser único."


# ── Errores de persistencia / sistema ───────────────────────────────────────

class ErrorPersistencia(ErrorJuego):
    """Problemas al leer o escribir archivos JSON de datos."""

    def __init__(self, ruta: str, detalle: str = "") -> None:
        super().__init__(
            mensaje=f"Error de persistencia en '{ruta}': {detalle}",
            codigo=200,
        )
        self.ruta = ruta
