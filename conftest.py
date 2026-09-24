"""
Permite que 'from modelos.x import Y' y 'from excepciones import Z' funcionen
en las pruebas, igual que en main.py, sin depender de instalar el proyecto
como paquete.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
