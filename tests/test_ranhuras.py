import unittest

import numpy as np

from ranhuras import MemoriaDeRanhuras


class MemoriaDeRanhurasTests(unittest.TestCase):
    def test_entrada_distante_faz_brotar_uma_ranhura(self):
        memoria = MemoriaDeRanhuras(w0=0.5, z_max=2.5)

        memoria.aprender([0.0])
        memoria.aprender([10.0])

        self.assertEqual(memoria.n_ranhuras(), 2)

    def test_erosao_move_centro_para_media_das_observacoes(self):
        memoria = MemoriaDeRanhuras(w0=1.0, largura_adaptativa=False)
        observacoes = ([0.0, 0.0], [2.0, 4.0], [4.0, 8.0])

        for observacao in observacoes:
            memoria.aprender(observacao, rotulo="A")

        centro = memoria.ranhuras[0].camaras[None].centro
        np.testing.assert_allclose(centro, [2.0, 4.0])

    def test_murchar_respeita_orcamento_e_remove_mais_fraca(self):
        memoria = MemoriaDeRanhuras(
            max_ranhuras=2, politica="murchar", tau=1.0,
        )

        memoria.aprender([0.0], rotulo="antiga")
        memoria.aprender([10.0], rotulo="recente")
        memoria.aprender([20.0], rotulo="nova")

        self.assertEqual(memoria.n_ranhuras(), 2)
        self.assertEqual(
            [ranhura.rotulo for ranhura in memoria.ranhuras],
            ["recente", "nova"],
        )

    def test_deslocamento_aprendido_recupera_rotulo_em_contexto_novo(self):
        memoria = MemoriaDeRanhuras(aprende_deslocamento=True)
        deslocamento = np.array([0.0, 20.0])
        exemplos = {
            "A": np.array([0.0, 0.0]),
            "B": np.array([10.0, 0.0]),
            "C": np.array([0.0, 10.0]),
        }

        for rotulo in ("A", "B"):
            base = exemplos[rotulo]
            memoria.aprender(base, ctx="referencia", rotulo=rotulo)
            memoria.aprender(base + deslocamento, ctx="deslocado", rotulo=rotulo)
        memoria.aprender(exemplos["C"], ctx="referencia", rotulo="C")

        rotulos, _, _ = memoria.prever(
            exemplos["C"] + deslocamento, ctx="deslocado",
        )

        self.assertEqual(rotulos, ["C"])


if __name__ == "__main__":
    unittest.main()
