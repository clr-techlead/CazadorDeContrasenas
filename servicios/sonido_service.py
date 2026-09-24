"""
sonido_service.py — Efectos de sonido opcionales usando winsound / beep.

Usa winsound en Windows (nativo, sin dependencias extra).
En otros sistemas, los efectos de sonido se deshabilitan silenciosamente
para no romper la ejecución.

El patrón de diseño aquí es «graceful degradation»: si el sonido no está
disponible, el juego continúa sin él, sin lanzar excepciones al usuario.
"""

import sys
import threading
from typing import Optional


class SonidoService:
    """Reproduce efectos de sonido en un hilo separado para no bloquear la UI.

    Usar threading.Thread para el sonido es crucial: winsound.Beep() es
    bloqueante, y si lo llamo desde el hilo de UI, congela la ventana
    durante la duración del beep.
    """

    def __init__(self, habilitado: bool = True) -> None:
        self._habilitado = habilitado and sys.platform == "win32"
        self._winsound: Optional[object] = None
        if self._habilitado:
            try:
                import winsound
                self._winsound = winsound
            except ImportError:
                self._habilitado = False

    def toggle(self) -> bool:
        """Activa/desactiva el sonido. Retorna el nuevo estado."""
        self._habilitado = not self._habilitado
        return self._habilitado

    @property
    def activo(self) -> bool:
        return self._habilitado

    def _reproducir(self, frecuencia: int, duracion: int) -> None:
        """Ejecutar en hilo separado para no bloquear la UI."""
        if not self._habilitado or self._winsound is None:
            return
        try:
            self._winsound.Beep(frecuencia, duracion)   # type: ignore
        except Exception:
            pass

    def _en_hilo(self, frecuencia: int, duracion: int) -> None:
        t = threading.Thread(
            target=self._reproducir,
            args=(frecuencia, duracion),
            daemon=True,
        )
        t.start()

    # ── Efectos específicos ──────────────────────────────────────────────────

    def sonido_exito(self) -> None:
        """Acorde ascendente para éxito."""
        self._en_hilo(880, 80)

    def sonido_error(self) -> None:
        """Tono grave para error o cofre maldito."""
        self._en_hilo(220, 200)

    def sonido_legendario(self) -> None:
        """Secuencia épica para cofre legendario."""
        def _secuencia() -> None:
            for freq in [523, 659, 784, 1047]:
                self._reproducir(freq, 100)
        if self._habilitado:
            t = threading.Thread(target=_secuencia, daemon=True)
            t.start()

    def sonido_click(self) -> None:
        """Click suave para interacciones de UI."""
        self._en_hilo(440, 30)

    def sonido_raro(self) -> None:
        """Efecto para cofre raro."""
        self._en_hilo(660, 120)
