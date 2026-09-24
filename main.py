"""
main.py — Punto de entrada de Cazador de Contraseñas.

Autor:       Camilo Andrés León Rubriche
Curso:       Programación — Cuarto semestre
Institución: Universidad Nacional Abierta y a Distancia (UNAD)
Versión:     1.0.0

Mantener main.py lo más delgado posible es una buena práctica:
su único trabajo es arrancar la aplicación y manejar los errores fatales
de inicio para que el usuario vea un mensaje claro en lugar de un traceback.
"""

import sys
import os

# Asegurar que el directorio del proyecto esté en el path de Python
# sin importar desde dónde se ejecute el script.
_raiz = os.path.dirname(os.path.abspath(__file__))
if _raiz not in sys.path:
    sys.path.insert(0, _raiz)


def verificar_dependencias() -> None:
    """Comprueba que las librerías críticas estén instaladas antes de arrancar."""
    faltantes: list[str] = []
    try:
        import customtkinter   # noqa: F401
    except ImportError:
        faltantes.append("customtkinter")

    if faltantes:
        print("=" * 60)
        print("ERROR: Dependencias faltantes.")
        print("Instálalas con:")
        print(f"   pip install {' '.join(faltantes)}")
        print("=" * 60)
        sys.exit(1)


def main() -> None:
    verificar_dependencias()

    # Importar aquí para que el check de dependencias ocurra primero
    from vistas.ventana_principal import VentanaPrincipal

    try:
        app = VentanaPrincipal()
        app.mainloop()
    except KeyboardInterrupt:
        # Ctrl+C en la terminal: salida limpia sin traceback
        print("\nJuego interrumpido por el usuario.")
    except Exception as e:
        # Error fatal no manejado: mostrar información útil
        import traceback
        print("\n" + "=" * 60)
        print("ERROR FATAL — Por favor reporta este mensaje:")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
