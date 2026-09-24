"""
Pruebas unitarias para el modelo Jugador (estado de sesión, rachas, logros).
"""
from modelos.jugador import Jugador, EstadisticasSesion


class TestJugadorEstadoBasico:

    def test_jugador_inicia_en_cero(self):
        j = Jugador("Ana")
        assert j.puntaje == 0
        assert j.estadisticas.rondas_jugadas == 0

    def test_nombre_vacio_usa_valor_por_defecto(self):
        j = Jugador("   ")
        assert j.nombre == "Cazador"

    def test_registrar_ronda_acumula_puntaje(self):
        j = Jugador("Ana")
        j.registrar_ronda("Abc12345!", "Fuerte", "Cofre Común", "común", 10)
        j.registrar_ronda("Xyz98765!", "Fuerte", "Cofre Raro", "raro", 25)
        assert j.puntaje == 35
        assert j.estadisticas.rondas_jugadas == 2

    def test_puntos_negativos_no_cuentan_como_ronda_ganada(self):
        j = Jugador("Ana")
        j.registrar_ronda("Abc12345!", "Débil", "Cofre Maldito", "maldito", -20)
        assert j.estadisticas.rondas_ganadas == 0
        assert j.estadisticas.rondas_jugadas == 1

    def test_historial_registra_cada_ronda(self):
        j = Jugador("Ana")
        j.registrar_ronda("Abc12345!", "Fuerte", "Cofre Común", "común", 10)
        assert len(j.historial) == 1
        assert j.historial[0]["puntos"] == 10


class TestRachas:

    def test_racha_aumenta_sin_cofre_maldito(self):
        j = Jugador("Ana")
        for _ in range(3):
            j.registrar_ronda("Abc12345!", "Fuerte", "Cofre Común", "común", 10)
        assert j.estadisticas.racha_sin_maldito == 3

    def test_cofre_maldito_reinicia_la_racha(self):
        j = Jugador("Ana")
        j.registrar_ronda("Abc12345!", "Fuerte", "Cofre Común", "común", 10)
        j.registrar_ronda("Xyz98765!", "Fuerte", "Cofre Maldito", "maldito", -20)
        assert j.estadisticas.racha_sin_maldito == 0

    def test_racha_maxima_se_conserva_tras_reiniciarse(self):
        j = Jugador("Ana")
        for _ in range(5):
            j.registrar_ronda("Abc12345!", "Fuerte", "Cofre Común", "común", 10)
        j.registrar_ronda("Xyz98765!", "Fuerte", "Cofre Maldito", "maldito", -20)
        assert j.estadisticas.racha_maxima == 5
        assert j.estadisticas.racha_sin_maldito == 0


class TestLogros:

    def test_primera_ronda_desbloquea_primera_sangre(self):
        j = Jugador("Ana")
        nuevos = j.registrar_ronda("Abc12345!", "Fuerte", "Cofre Común", "común", 10)
        assert "primera_sangre" in nuevos

    def test_logro_no_se_repite_en_rondas_siguientes(self):
        j = Jugador("Ana")
        j.registrar_ronda("Abc12345!", "Fuerte", "Cofre Común", "común", 10)
        nuevos = j.registrar_ronda("Xyz98765!", "Fuerte", "Cofre Común", "común", 10)
        assert "primera_sangre" not in nuevos

    def test_logro_coleccionista_al_llegar_a_100_puntos(self):
        j = Jugador("Ana")
        j.registrar_ronda("Abc12345!", "Fuerte", "Cofre Legendario", "legendario", 50)
        nuevos = j.registrar_ronda("Xyz98765!", "Fuerte", "Cofre Legendario", "legendario", 50)
        assert "coleccionista" in nuevos

    def test_logro_invicto_tras_cinco_rondas_sin_maldito(self):
        j = Jugador("Ana")
        nuevos_totales = []
        for _ in range(5):
            nuevos_totales += j.registrar_ronda("Abc12345!", "Fuerte", "Cofre Común", "común", 10)
        assert "invicto" in nuevos_totales


class TestEstadisticasSesion:

    def test_porcentaje_exito_sin_rondas_es_cero(self):
        stats = EstadisticasSesion()
        assert stats.porcentaje_exito() == 0.0

    def test_porcentaje_exito_se_calcula_correctamente(self):
        stats = EstadisticasSesion(rondas_jugadas=4, rondas_ganadas=3)
        assert stats.porcentaje_exito() == 75.0
