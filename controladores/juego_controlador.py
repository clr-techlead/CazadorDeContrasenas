"""
juego_controlador.py — Orquestador central del juego.
Autor: Camilo Andrés León Rubriche — UNAD

El controlador es el «cerebro» que conecta modelos, servicios y vistas.
No contiene lógica de negocio pura (eso está en los modelos) ni lógica
de presentación (eso está en las vistas). Su rol es coordinar.

Patrón: Model-View-Controller (MVC) adaptado.
"""

from __future__ import annotations

import random
from typing import Callable, Optional

from modelos import (
    Contrasena,
    FabricaCofre,
    CofreBase,
    ResultadoApertura,
    Jugador,
)
from servicios import (
    GeneradorService,
    RankingService,
    EstadisticasService,
    SonidoService,
)
from excepciones import (
    ErrorJuego,
    LongitudInvalidaError,
    EntradaNoNumericaError,
    ContrasenaInvalidaError,
    CaracterRepetidoError,
)
from utils.constantes import (
    MULTIPLICADORES,
    PROB_COMUN,
    PROB_RARO,
    PROB_LEGENDARIO,
    PROB_MALDITO,
    MENSAJES_EXITO,
    LOGROS,
)
from utils.helpers import elegir_aleatorio


# ── Resultado de ronda (tipo valor para la vista) ────────────────────────────

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoRonda:
    """Todo lo que la vista necesita para actualizar la UI después de una ronda."""
    contrasena_str:   str
    nivel_seguridad:  str
    puntaje_seguridad: int
    cofre:            ResultadoApertura
    puntos_obtenidos: int
    puntaje_total:    int
    mensaje_extra:    str
    logros_nuevos:    list[str]
    es_exitosa:       bool


# ── Controlador principal ────────────────────────────────────────────────────

class JuegoControlador:
    """Gestiona el ciclo de vida completo de una partida.

    Composición: usa instancias de los servicios sin heredar de ellos.
    Los servicios se inyectan en el constructor para facilitar testing
    (se pueden pasar mocks sin tocar esta clase).
    """

    def __init__(
        self,
        nombre_jugador: str = "Cazador",
        dificultad: str = "normal",
        generador:    Optional[GeneradorService]    = None,
        ranking:      Optional[RankingService]      = None,
        estadisticas: Optional[EstadisticasService] = None,
        sonido:       Optional[SonidoService]       = None,
    ) -> None:
        self._jugador = Jugador(nombre_jugador, dificultad)
        self._generador    = generador    or GeneradorService()
        self._ranking      = ranking      or RankingService()
        self._estadisticas = estadisticas or EstadisticasService()
        self._sonido       = sonido       or SonidoService()
        self._dificultad   = dificultad
        self._activo       = True

        # Ajustar probabilidades de cofre según dificultad
        self._probs_cofre = self._calcular_probs()
        self._multiplicador = MULTIPLICADORES.get(dificultad, 1.0)

        # Contraseña generada en el paso 1, esperando que el jugador abra el cofre
        self._contrasena_pendiente: Optional["Contrasena"] = None

        # Callback opcional para notificar a la vista sobre eventos externos
        self._callback_logro: Optional[Callable[[str], None]] = None

    # ── Configuración ────────────────────────────────────────────────────────

    def set_callback_logro(self, fn: Callable[[str], None]) -> None:
        """Registra una función que se llamará cuando se desbloquee un logro."""
        self._callback_logro = fn

    def _calcular_probs(self) -> list[float]:
        """Ajusta probabilidades de cofre según dificultad.

        En dificultad alta, hay más cofres malditos y menos comunes.
        """
        base = [PROB_COMUN, PROB_RARO, PROB_LEGENDARIO, PROB_MALDITO]
        ajustes = {
            "fácil":   [0.60, 0.28, 0.10, 0.02],
            "normal":  base,
            "difícil": [0.38, 0.30, 0.15, 0.17],
            "extremo": [0.25, 0.28, 0.18, 0.29],
        }
        return ajustes.get(self._dificultad, base)

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def jugador(self) -> Jugador:
        return self._jugador

    @property
    def puntaje_actual(self) -> int:
        return self._jugador.puntaje

    @property
    def rondas_jugadas(self) -> int:
        return self._jugador.estadisticas.rondas_jugadas

    @property
    def activo(self) -> bool:
        return self._activo

    @property
    def sonido(self) -> SonidoService:
        return self._sonido

    # ── Lógica de ronda en DOS PASOS ────────────────────────────────────────

    def generar_contrasena(self, texto_longitud: str) -> "Contrasena":
        """PASO 1 — Genera y valida la contraseña sin abrir ningún cofre.

        La contraseña generada se guarda en _contrasena_pendiente para que
        abrir_cofre() la use en el paso 2. Separar ambos pasos añade
        suspenso: el jugador ve la contraseña, comprueba que es válida
        y decide cuándo abrir.

        Raises:
            LongitudInvalidaError, EntradaNoNumericaError: el controlador
            deja que suban para que la vista los muestre al usuario.
        """
        contrasena, _ = self._generador.generar_desde_texto(texto_longitud)
        # Guardamos la contraseña validada para usarla en el paso 2.
        # Si el usuario genera otra antes de abrir, la anterior se descarta.
        self._contrasena_pendiente: Optional["Contrasena"] = contrasena
        return contrasena

    def abrir_cofre(self) -> ResultadoRonda:
        """PASO 2 — Abre el cofre usando la contraseña generada en el paso 1.

        Si no hay contraseña pendiente (el jugador no generó antes), lanza
        ErrorJuego para que la vista lo informe correctamente.

        El bloque try/except/else/finally completo vive aquí:
        - try:   validar contraseña + seleccionar cofre
        - except: contraseña inválida → cofre maldito como penalización
        - else:   éxito → reproducir sonido del cofre obtenido
        - finally: siempre → limpiar contraseña pendiente
        """
        if self._contrasena_pendiente is None:
            raise ErrorJuego("Debes generar una contraseña antes de abrir el cofre.")

        contrasena = self._contrasena_pendiente
        es_exitosa: bool = True

        try:
            # Validar que cumple todas las reglas de seguridad
            contrasena.lanzar_si_invalida()

            # Contraseña válida → el azar elige el tipo de cofre
            cofre = FabricaCofre.crear(
                probabilidades=self._probs_cofre,
                multiplicador=self._multiplicador,
            )
            apertura = cofre.abrir()

        except (ContrasenaInvalidaError, CaracterRepetidoError) as e:
            # Contraseña rechazada → penalización automática con cofre maldito.
            # El jugador pierde puntos como consecuencia de una clave débil.
            from modelos.cofres import CofreMaldito
            cofre_castigo = CofreMaldito(multiplicador=self._multiplicador)
            apertura = cofre_castigo.abrir()
            self._sonido.sonido_error()
            apertura = apertura._replace(
                mensaje=f"Clave rechazada: {e.mensaje if hasattr(e, 'mensaje') else str(e)}"
            )
            es_exitosa = False

        else:
            # Sólo si NO hubo excepción: reproducir sonido acorde al cofre obtenido
            es_exitosa = True
            self._reproducir_sonido_cofre(apertura.rareza)

        finally:
            # Siempre: liberar la contraseña pendiente para la siguiente ronda.
            # Si no hacemos esto, el jugador podría abrir el mismo cofre dos veces.
            self._contrasena_pendiente = None

        puntos = apertura.puntos

        logros_nuevos = self._jugador.registrar_ronda(
            contrasena        = contrasena.valor,
            nivel_seguridad   = contrasena.nivel_seguridad,
            tipo_cofre        = apertura.nombre_cofre,
            rareza_cofre      = apertura.rareza,
            puntos_obtenidos  = puntos,
        )

        for logro_id in logros_nuevos:
            if self._callback_logro:
                self._callback_logro(logro_id)

        mensaje_extra = self._generar_mensaje_extra(apertura, logros_nuevos)

        return ResultadoRonda(
            contrasena_str     = contrasena.valor,
            nivel_seguridad    = contrasena.nivel_seguridad,
            puntaje_seguridad  = contrasena.puntaje_seguridad,
            cofre              = apertura,
            puntos_obtenidos   = puntos,
            puntaje_total      = self._jugador.puntaje,
            mensaje_extra      = mensaje_extra,
            logros_nuevos      = logros_nuevos,
            es_exitosa         = es_exitosa,
        )

    # Mantener jugar_ronda como alias de un solo paso (por compatibilidad / tests)
    def jugar_ronda(self, texto_longitud: str) -> ResultadoRonda:
        """Versión de un solo paso: genera y abre en una llamada (para tests)."""
        self.generar_contrasena(texto_longitud)
        return self.abrir_cofre()

    def _reproducir_sonido_cofre(self, rareza: str) -> None:
        mapa = {
            "legendario": self._sonido.sonido_legendario,
            "raro":       self._sonido.sonido_raro,
            "maldito":    self._sonido.sonido_error,
            "común":      self._sonido.sonido_exito,
        }
        fn = mapa.get(rareza, self._sonido.sonido_exito)
        fn()

    def _generar_mensaje_extra(
        self,
        apertura: ResultadoApertura,
        logros: list[str],
    ) -> str:
        partes: list[str] = []
        if apertura.es_positivo:
            partes.append(random.choice(MENSAJES_EXITO))
        if logros:
            nombres = [LOGROS[lid]["nombre"] for lid in logros if lid in LOGROS]
            if nombres:
                partes.append(f"🏆 Logro desbloqueado: {', '.join(nombres)}")
        return " | ".join(partes)

    # ── Fin de partida ───────────────────────────────────────────────────────

    def terminar_partida(self) -> dict:
        """Guarda la sesión y actualiza el ranking. Retorna resumen final."""
        self._activo = False
        datos = self._jugador.to_dict()

        try:
            self._ranking.guardar_sesion(datos)
            posicion = self._ranking.guardar_entrada(
                nombre     = self._jugador.nombre,
                puntaje    = self._jugador.puntaje,
                dificultad = self._dificultad,
            )
            self._estadisticas.registrar_sesion(datos)
        except Exception:
            posicion = -1   # Si falla la persistencia, no rompemos el juego

        datos["posicion_ranking"] = posicion
        return datos

    def reiniciar(self, nombre: str = "", dificultad: str = "") -> None:
        """Reinicia la partida manteniendo configuración o aplicando nueva."""
        nom = nombre or self._jugador.nombre
        dif = dificultad or self._dificultad
        self._jugador               = Jugador(nom, dif)
        self._dificultad            = dif
        self._probs_cofre           = self._calcular_probs()
        self._multiplicador         = MULTIPLICADORES.get(dif, 1.0)
        self._activo                = True
        self._contrasena_pendiente  = None

    # ── Datos para la vista ──────────────────────────────────────────────────

    def obtener_ranking(self) -> list[dict]:
        return self._ranking.cargar_ranking()

    def obtener_historial(self) -> list[dict]:
        return self._jugador.historial

    def obtener_estadisticas_globales(self) -> str:
        return self._estadisticas.stats.resumen_texto()
