import unittest

import backtest


class TestSerie(unittest.TestCase):
    def test_convierte_porcentaje_a_fraccion_y_filtra_desde(self):
        datos = [{"fecha": "2016-12-31", "valor": 1.2}, {"fecha": "2017-01-31", "valor": 1.6}]
        self.assertEqual(backtest.serie_mensual(datos), {"2017-01": 0.016})

    def test_detecta_huecos(self):
        datos = [{"fecha": "2017-01-31", "valor": 1.6}, {"fecha": "2017-03-31", "valor": 2.4}]
        with self.assertRaises(ValueError):
            backtest.serie_mensual(datos)

    def test_siguiente_mes_cruza_el_año(self):
        self.assertEqual(backtest.siguiente_mes("2017-12"), "2018-01")
        self.assertEqual(backtest.siguiente_mes("2017-09"), "2017-10")


class TestValorReal(unittest.TestCase):
    def test_sin_inflacion_las_cuotas_valen_lo_mismo(self):
        self.assertAlmostEqual(backtest.valor_real_cuotas([0, 0, 0], 3), 1.0)

    def test_una_cuota_se_deflacta_un_mes(self):
        self.assertAlmostEqual(backtest.valor_real_cuotas([0.10], 1), 1 / 1.10)

    def test_inflacion_variable_se_acumula(self):
        esperado = (1 / 2) / 1.10 + (1 / 2) / (1.10 * 1.20)
        self.assertAlmostEqual(backtest.valor_real_cuotas([0.10, 0.20], 2), esperado)

    def test_descuento_equivalente_crece_con_mas_cuotas(self):
        inf = [0.02] * 12
        self.assertLess(backtest.descuento_equivalente(inf, 3), backtest.descuento_equivalente(inf, 12))

    def test_faltan_meses(self):
        with self.assertRaises(ValueError):
            backtest.valor_real_cuotas([0.02], 3)


class TestBacktest(unittest.TestCase):
    def test_ultimos_meses_quedan_vacios_si_no_hay_inflacion_futura(self):
        serie = {f"2017-{m:02d}": 0.02 for m in range(1, 6)}
        filas = backtest.backtest(serie, planes=(3,))
        self.assertNotEqual(filas[0]["cuotas_3"], "")
        self.assertNotEqual(filas[1]["cuotas_3"], "")
        self.assertEqual(filas[2]["cuotas_3"], "")


if __name__ == "__main__":
    unittest.main()
