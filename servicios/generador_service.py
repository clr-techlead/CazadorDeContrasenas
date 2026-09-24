"""
generador_service.py — Servicio de generación de contraseñas.

La capa de servicio actúa como intermediario entre los modelos y los
controladores. Aquí vive el manejo de excepciones de alto nivel para
que el controlador reciba resultados limpios o excepciones tipadas.
"""

from modelos.contrasena import Contrasena, ResultadoValidacion
from excepciones import (
    LongitudInvalidaError,
    EntradaNoNumericaError,
    ContrasenaInvalidaError,
    CaracterRepetidoError,
)
from utils.helpers import es_entero_valido, limpiar_cadena


class GeneradorService:
    """Orquesta la generación y validación de contraseñas.

    Esta clase no tiene estado propio; es un servicio sin side-effects,
    por lo que sus métodos podrían ser estáticos. Los hago de instancia
    para facilitar inyección de dependencias y testing.
    """

    def generar_desde_texto(self, texto_longitud: str) -> tuple[Contrasena, list[str]]:
        """Valida la entrada del usuario y genera una contraseña.

        Implementación completa de try/except/else/finally:

        try     → intenta la conversión y generación
        except  → captura errores específicos con mensajes claros
        else    → sólo se ejecuta si no hubo excepciones
        finally → siempre ejecutado, ideal para logging o limpieza

        Returns:
            Tupla (Contrasena generada, lista de advertencias).

        Raises:
            EntradaNoNumericaError: Si el texto no es un número.
            LongitudInvalidaError:  Si la longitud está fuera de rango.
        """
        texto = limpiar_cadena(texto_longitud)
        advertencias: list[str] = []

        try:
            if not es_entero_valido(texto):
                raise EntradaNoNumericaError(texto)

            longitud = int(texto)
            contrasena = Contrasena(longitud)

        except EntradaNoNumericaError:
            # Re-lanzamos con contexto enriquecido
            raise

        except LongitudInvalidaError:
            raise

        except Exception as e:
            # Captura de seguridad: errores inesperados del sistema
            raise ContrasenaInvalidaError(
                mensaje=f"Error inesperado al generar la contraseña: {e}",
            ) from e

        else:
            # Este bloque sólo corre si la generación fue exitosa
            if not contrasena.es_valida:
                advertencias.append(
                    "La contraseña generada fue marcada como inválida; "
                    "esto no debería ocurrir. Por favor reporta este caso."
                )

        finally:
            # Aquí iría logging en producción, limpieza de recursos, etc.
            pass

        return contrasena, advertencias

    def validar_contrasena(self, contrasena: Contrasena) -> ResultadoValidacion:
        """Retorna el resultado de validación ya calculado en el modelo."""
        return contrasena.resultado

    def descripcion_nivel(self, nivel: str) -> str:
        """Texto descriptivo para mostrar junto al indicador de nivel."""
        descripciones = {
            "Débil":    "Contraseña débil. Vulnerabilidad alta.",
            "Moderado": "Seguridad aceptable, pero mejorable.",
            "Fuerte":   "Contraseña robusta. Buen trabajo.",
            "Extremo":  "Nivel máximo. Prácticamente irrompible.",
        }
        return descripciones.get(nivel, "Nivel desconocido.")
