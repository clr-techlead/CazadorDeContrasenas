"""
Pruebas unitarias para la jerarquía de cofres (herencia, polimorfismo,
abstracción) y la fábrica de cofres.
"""
import pytest

from modelos.cofres import (
    CofreBase,
    CofreComun,
    CofreRaro,
    CofreLegendario,
    CofreMaldito,
    FabricaCofre,
)


class TestCofreBaseEsAbstracta:

    def test_no_se_puede_instanciar_directamente(self):
        with pytest.raises(TypeError):
            CofreBase()  # ABC con métodos abstractos: no instanciable


class TestCofresConcretos:

    @pytest.mark.parametrize(
        "clase,rareza,es_positivo",
        [
            (CofreComun, "común", True),
            (CofreRaro, "raro", True),
            (CofreLegendario, "legendario", True),
            (CofreMaldito, "maldito", False),
        ],
    )
    def test_abrir_devuelve_resultado_coherente_con_su_rareza(self, clase, rareza, es_positivo):
        cofre = clase()
        resultado = cofre.abrir()
        assert resultado.rareza == rareza
        assert resultado.es_positivo == es_positivo
        assert resultado.nombre_cofre == cofre.nombre

    def test_cofre_comun_otorga_puntos_positivos(self):
        cofre = CofreComun()
        resultado = cofre.abrir()
        assert resultado.puntos == 10  # PUNTOS_COMUN

    def test_cofre_maldito_resta_puntos(self):
        cofre = CofreMaldito()
        resultado = cofre.abrir()
        assert resultado.puntos == -20  # PUNTOS_MALDITO

    def test_multiplicador_escala_los_puntos(self):
        cofre = CofreComun(multiplicador=2.0)
        assert cofre.puntos_finales() == 20

    def test_animacion_ascii_no_esta_vacia(self):
        for clase in (CofreComun, CofreRaro, CofreLegendario, CofreMaldito):
            assert len(clase().animacion_ascii()) > 0


class TestPolimorfismoCofres:

    def test_misma_llamada_abrir_distinto_resultado_por_subclase(self):
        """El controlador solo conoce cofre.abrir() — el comportamiento
        real depende de qué subclase se instanció."""
        cofres = [CofreComun(), CofreRaro(), CofreLegendario(), CofreMaldito()]
        rarezas = {c.abrir().rareza for c in cofres}
        assert rarezas == {"común", "raro", "legendario", "maldito"}


class TestFabricaCofre:

    def test_crear_por_rareza_devuelve_tipo_correcto(self):
        assert isinstance(FabricaCofre.crear_por_rareza("común"), CofreComun)
        assert isinstance(FabricaCofre.crear_por_rareza("raro"), CofreRaro)
        assert isinstance(FabricaCofre.crear_por_rareza("legendario"), CofreLegendario)
        assert isinstance(FabricaCofre.crear_por_rareza("maldito"), CofreMaldito)

    def test_crear_por_rareza_desconocida_usa_comun_por_defecto(self):
        assert isinstance(FabricaCofre.crear_por_rareza("inexistente"), CofreComun)

    def test_crear_con_probabilidad_100_por_ciento_es_determinista(self):
        # Con peso 1.0 en "raro" y 0 en el resto, siempre debe salir CofreRaro
        cofre = FabricaCofre.crear(probabilidades=[0, 1.0, 0, 0])
        assert isinstance(cofre, CofreRaro)

    def test_crear_aplica_multiplicador(self):
        cofre = FabricaCofre.crear(probabilidades=[1.0, 0, 0, 0], multiplicador=3.0)
        assert cofre.puntos_finales() == 30  # 10 * 3
