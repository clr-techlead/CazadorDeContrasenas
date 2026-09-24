"""
Pruebas unitarias para el modelo Contrasena (generación y validación).
"""
import pytest

from modelos.contrasena import Contrasena
from excepciones.excepciones import (
    LongitudInvalidaError,
    ContrasenaInvalidaError,
    CaracterRepetidoError,
)


class TestGeneracion:

    def test_longitud_generada_coincide_con_la_solicitada(self):
        pwd = Contrasena(16)
        assert len(pwd.valor) == 16

    def test_longitud_fuera_de_rango_lanza_excepcion(self):
        with pytest.raises(LongitudInvalidaError):
            Contrasena(4)  # menor al mínimo (8)

    def test_longitud_excede_el_maximo_lanza_excepcion(self):
        with pytest.raises(LongitudInvalidaError):
            Contrasena(100)  # mayor al máximo (64)

    def test_longitud_minima_permitida_es_valida(self):
        pwd = Contrasena(8)
        assert len(pwd.valor) == 8

    def test_sin_caracteres_repetidos(self):
        pwd = Contrasena(20)
        assert len(set(pwd.valor)) == len(pwd.valor)

    def test_generacion_es_aleatoria_entre_instancias(self):
        contrasenas = {Contrasena(12).valor for _ in range(10)}
        assert len(contrasenas) > 1  # extremadamente improbable que coincidan


class TestValidacion:

    def test_contrasena_generada_es_valida_por_construccion(self):
        """El generador siempre garantiza al menos un carácter de cada
        categoría obligatoria, así que toda contraseña generada debe
        pasar sus propias reglas de validación."""
        pwd = Contrasena(12)
        assert pwd.es_valida
        assert pwd.resultado.reglas_fallidas == []

    def test_incluye_mayuscula_minuscula_numero_y_especial(self):
        pwd = Contrasena(16)
        r = pwd.resultado
        assert r.tiene_mayuscula
        assert r.tiene_minuscula
        assert r.tiene_numero
        assert r.tiene_especial

    def test_lanzar_si_invalida_no_lanza_para_contrasena_valida(self):
        pwd = Contrasena(12)
        pwd.lanzar_si_invalida()  # no debe lanzar nada

    @pytest.mark.parametrize("longitud", [8, 12, 20, 32, 64])
    def test_puntaje_seguridad_entre_0_y_100(self, longitud):
        pwd = Contrasena(longitud)
        assert 0 <= pwd.puntaje_seguridad <= 100

    def test_nivel_seguridad_es_uno_de_los_esperados(self):
        pwd = Contrasena(16)
        assert pwd.nivel_seguridad in ("Débil", "Moderado", "Fuerte", "Extremo")

    def test_contrasena_larga_tiende_a_mejor_puntaje_que_una_corta(self):
        corta = Contrasena(8)
        larga = Contrasena(40)
        assert larga.puntaje_seguridad >= corta.puntaje_seguridad
