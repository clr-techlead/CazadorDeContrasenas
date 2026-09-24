"""
validaciones_controlador.py — Validaciones de entrada desacopladas de la UI.

Mantener las validaciones aquí (y no en los widgets) permite que la misma
lógica se use desde la GUI, desde tests automatizados o desde una hipotética
CLI sin duplicar código.
"""

from excepciones import EntradaNoNumericaError, LongitudInvalidaError
from utils.constantes import MINIMO_LONGITUD, MAXIMO_LONGITUD
from utils.helpers import es_entero_valido, limpiar_cadena


class ValidacionesControlador:
    """Valida entradas del usuario antes de pasarlas al dominio."""

    @staticmethod
    def validar_longitud_texto(texto: str) -> int:
        """Parsea y valida la longitud ingresada por el usuario.

        Returns:
            El entero válido.

        Raises:
            EntradaNoNumericaError: Si no es un número.
            LongitudInvalidaError:  Si está fuera de rango.
        """
        texto = limpiar_cadena(texto)
        if not texto:
            raise EntradaNoNumericaError("(vacío)")
        if not es_entero_valido(texto):
            raise EntradaNoNumericaError(texto)
        longitud = int(texto)
        if longitud < MINIMO_LONGITUD or longitud > MAXIMO_LONGITUD:
            raise LongitudInvalidaError(longitud)
        return longitud

    @staticmethod
    def validar_nombre(nombre: str) -> str:
        """Limpia y valida el nombre del jugador."""
        nombre = limpiar_cadena(nombre)
        if not nombre:
            return "Cazador"
        if len(nombre) > 20:
            return nombre[:20]
        return nombre
