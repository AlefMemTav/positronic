import json
from pathlib import Path
import tempfile
import unittest

from registro import criar_registro, diferenca_pareada, holm, salvar_registro


class RegistroTests(unittest.TestCase):
    def test_diferenca_pareada_preserva_empate(self):
        resultado = diferenca_pareada(
            [0.8, 0.7, 0.9], [0.7, 0.6, 0.8],
            reamostragens=500, margem=0.05,
        )
        self.assertAlmostEqual(resultado["media"], 0.1)
        self.assertEqual(resultado["decisao"], "confirmado")

    def test_diferenca_pareada_exige_pares(self):
        with self.assertRaises(ValueError):
            diferenca_pareada([0.8, 0.7], [0.7])

    def test_holm_retorna_ordem_original(self):
        self.assertEqual(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])

    def test_registro_guarda_versoes_e_metricas_por_semente(self):
        registro = criar_registro(
            experimento="exp-teste", parametros={"alpha": 0.1},
            metricas={"acuracia": [0.7, 0.8]},
            sementes_calibracao=[1, 2], sementes_teste=[3, 4],
        )
        self.assertEqual(registro["metricas_por_semente"]["acuracia"], [0.7, 0.8])
        with tempfile.TemporaryDirectory() as tmp:
            caminho = salvar_registro(registro, tmp)
            self.assertEqual(json.loads(caminho.read_text())["run_id"], registro["run_id"])
            self.assertTrue(Path(caminho).is_file())


if __name__ == "__main__":
    unittest.main()
