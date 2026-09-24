"""
contrasena.py — Modelo de dominio para la contraseña.
Autor: Camilo Andrés León Rubriche — UNAD

Esta clase aplica el principio de Responsabilidad Única (SRP): sólo sabe
generar y validar contraseñas. No sabe nada de la UI ni del almacenamiento.

Encapsulamiento: los atributos internos están prefijados con _ y se exponen
sólo mediante propiedades de sólo lectura, lo que protege el estado interno.
"""

import random
import string
from dataclasses import dataclass, field
from typing import NamedTuple

from excepciones import (
    LongitudInvalidaError,
    ContrasenaInvalidaError,
    CaracterRepetidoError,
)
from utils.constantes import (
    CARACTERES_ESPECIALES,
    MINIMO_LONGITUD,
    MAXIMO_LONGITUD,
    NIVEL_DEBIL,
    NIVEL_MODERADO,
    NIVEL_FUERTE,
    NIVEL_EXTREMO,
    UMBRALES_NIVEL,
)


# ── Resultado de validación (inmutable, tipo valor) ──────────────────────────

class ResultadoValidacion(NamedTuple):
    """Agrupa todos los resultados de una validación en una sola estructura.

    NamedTuple en lugar de dataclass porque es un tipo valor: inmutable
    y comparable por contenido, no por identidad.
    """
    es_valida: bool
    tiene_mayuscula: bool
    tiene_minuscula: bool
    tiene_numero: bool
    tiene_especial: bool
    sin_repetidos: bool
    longitud_ok: bool
    puntaje_seguridad: int          # 0–100
    nivel: str                      # "Débil", "Moderado", "Fuerte", "Extremo"
    reglas_fallidas: list[str]


# ── Clase principal ──────────────────────────────────────────────────────────

class Contrasena:
    """Representa una contraseña generada o evaluada por el sistema.

    Encapsula la lógica de generación y validación. El atributo _valor
    sólo se puede leer desde fuera; modificarlo requeriría generar una nueva
    instancia, lo que garantiza consistencia del estado interno.

    Herencia: esta clase podría extenderse con ContrasenaPersonalizada
    sin modificar esta lógica base (Open/Closed Principle).
    """

    # Pools de caracteres separados para asegurar cobertura de categorías
    _LETRAS_MAYUS: str = string.ascii_uppercase
    _LETRAS_MINUS: str = string.ascii_lowercase
    _NUMEROS: str      = string.digits
    _ESPECIALES: str   = CARACTERES_ESPECIALES

    def __init__(self, longitud: int) -> None:
        """Inicializa y genera automáticamente la contraseña.

        Args:
            longitud: Número de caracteres deseado.

        Raises:
            LongitudInvalidaError: Si la longitud está fuera del rango permitido.
        """
        # Validación defensiva en el constructor: mejor fallar aquí que
        # producir un objeto en estado incoherente.
        if longitud < MINIMO_LONGITUD or longitud > MAXIMO_LONGITUD:
            raise LongitudInvalidaError(longitud)

        self._longitud: int = longitud
        self._valor: str = self._generar()
        self._resultado: ResultadoValidacion = self._validar_interna()

    # ── Propiedades (encapsulamiento) ────────────────────────────────────────

    @property
    def valor(self) -> str:
        """La cadena de la contraseña generada (sólo lectura)."""
        return self._valor

    @property
    def longitud(self) -> int:
        return self._longitud

    @property
    def es_valida(self) -> bool:
        return self._resultado.es_valida

    @property
    def nivel_seguridad(self) -> str:
        return self._resultado.nivel

    @property
    def puntaje_seguridad(self) -> int:
        return self._resultado.puntaje_seguridad

    @property
    def resultado(self) -> ResultadoValidacion:
        """Expone el resultado completo de validación (inmutable)."""
        return self._resultado

    # ── Generación ───────────────────────────────────────────────────────────

    def _generar(self) -> str:
        """Construye la contraseña garantizando diversidad de categorías.

        Estrategia: primero aseguro exactamente un carácter de cada categoría
        obligatoria, luego relleno con caracteres únicos al azar del pool
        combinado y mezclo todo con shuffle para eliminar cualquier patrón.

        random.sample garantiza sin reemplazo (caracteres únicos).
        random.shuffle elimina el patrón posicional.
        """
        pool_completo = (
            self._LETRAS_MAYUS
            + self._LETRAS_MINUS
            + self._NUMEROS
            + self._ESPECIALES
        )

        # Primero los «mandatorios» (uno de cada categoría)
        obligatorios: list[str] = [
            random.choice(self._LETRAS_MAYUS),
            random.choice(self._LETRAS_MINUS),
            random.choice(self._NUMEROS),
            random.choice(self._ESPECIALES),
        ]

        # Pool disponible: eliminamos los ya seleccionados para evitar repetidos
        disponibles = [c for c in pool_completo if c not in obligatorios]
        faltantes = self._longitud - len(obligatorios)

        # random.sample garantiza selección sin reemplazo
        if faltantes > len(disponibles):
            # Caso límite: pool insuficiente para la longitud pedida → usamos
            # todos los disponibles y completamos con muestra ampliada
            relleno = disponibles
        else:
            relleno = random.sample(disponibles, faltantes)

        caracteres = obligatorios + relleno

        # random.shuffle garantiza que los obligatorios no queden siempre al inicio
        random.shuffle(caracteres)
        return "".join(caracteres)

    # ── Validación ───────────────────────────────────────────────────────────

    def _validar_interna(self) -> ResultadoValidacion:
        """Aplica todas las reglas y devuelve un resultado estructurado."""
        texto = self._valor
        reglas_fallidas: list[str] = []

        tiene_mayus = any(c in self._LETRAS_MAYUS for c in texto)
        tiene_minus = any(c in self._LETRAS_MINUS for c in texto)
        tiene_num   = any(c in self._NUMEROS for c in texto)
        tiene_esp   = any(c in self._ESPECIALES for c in texto)
        longitud_ok = MINIMO_LONGITUD <= len(texto) <= MAXIMO_LONGITUD
        sin_rep     = len(set(texto)) == len(texto)

        if not tiene_mayus:   reglas_fallidas.append("mayúscula")
        if not tiene_minus:   reglas_fallidas.append("minúscula")
        if not tiene_num:     reglas_fallidas.append("número")
        if not tiene_esp:     reglas_fallidas.append("carácter especial")
        if not longitud_ok:   reglas_fallidas.append("longitud")
        if not sin_rep:       reglas_fallidas.append("caracteres únicos")

        es_valida = len(reglas_fallidas) == 0

        puntaje = self._calcular_puntaje(
            tiene_mayus, tiene_minus, tiene_num, tiene_esp, sin_rep
        )
        nivel = self._puntaje_a_nivel(puntaje)

        return ResultadoValidacion(
            es_valida        = es_valida,
            tiene_mayuscula  = tiene_mayus,
            tiene_minuscula  = tiene_minus,
            tiene_numero     = tiene_num,
            tiene_especial   = tiene_esp,
            sin_repetidos    = sin_rep,
            longitud_ok      = longitud_ok,
            puntaje_seguridad = puntaje,
            nivel             = nivel,
            reglas_fallidas   = reglas_fallidas,
        )

    def _calcular_puntaje(
        self,
        mayus: bool,
        minus: bool,
        num: bool,
        esp: bool,
        sin_rep: bool,
    ) -> int:
        """Asigna un puntaje de seguridad de 0 a 100.

        Pesa cada criterio y añade bonificación por longitud extra.
        """
        score = 0
        if mayus:   score += 20
        if minus:   score += 15
        if num:     score += 20
        if esp:     score += 25
        if sin_rep: score += 10

        # Bonificación por longitud: +1 por cada carácter extra sobre el mínimo, máx 10
        bonus_longitud = min(10, self._longitud - MINIMO_LONGITUD)
        score += bonus_longitud

        return min(score, 100)

    @staticmethod
    def _puntaje_a_nivel(puntaje: int) -> str:
        if puntaje >= UMBRALES_NIVEL[NIVEL_EXTREMO]:
            return "Extremo"
        if puntaje >= UMBRALES_NIVEL[NIVEL_FUERTE]:
            return "Fuerte"
        if puntaje >= UMBRALES_NIVEL[NIVEL_MODERADO]:
            return "Moderado"
        return "Débil"

    # ── Excepciones explícitas (para uso externo) ────────────────────────────

    def lanzar_si_invalida(self) -> None:
        """Lanza excepción si la contraseña generada no cumple las reglas.

        Uso del bloque try/except/else/finally en el llamador:
            try:
                pwd.lanzar_si_invalida()
            except ContrasenaInvalidaError as e:
                ...   # mostrar error en UI
            except CaracterRepetidoError as e:
                ...   # mostrar carácter repetido
            else:
                ...   # continuar con lógica de cofre
            finally:
                ...   # limpiar estado temporal
        """
        r = self._resultado
        if not r.sin_repetidos:
            # Encontrar el primer carácter repetido para el mensaje
            visto: set[str] = set()
            for c in self._valor:
                if c in visto:
                    raise CaracterRepetidoError(c)
                visto.add(c)
        if not r.es_valida:
            raise ContrasenaInvalidaError(
                mensaje="La contraseña no cumple los requisitos de seguridad.",
                reglas_fallidas=r.reglas_fallidas,
            )

    # ── Representación ───────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Contrasena(longitud={self._longitud}, "
            f"nivel='{self.nivel_seguridad}', "
            f"valida={self.es_valida})"
        )

    def __str__(self) -> str:
        return self._valor
