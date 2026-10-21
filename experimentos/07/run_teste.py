"""Executa uma única vez o teste confirmatório do Exp. 7."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from modelos import acuracia, gerar_dados
from protocolo import REGISTROS, carregar_configuracao, exigir_arvore_limpa
from registro import criar_registro, diferenca_pareada, salvar_registro


def executar() -> dict:
    commit_inicio = exigir_arvore_limpa()
    config = carregar_configuracao()
    n = int(config["dimensionamento_teste"]["n"])
    sementes = tuple(range(9000, 9000 + n))
    if sementes != tuple(config["dimensionamento_teste"]["sementes_teste"]):
        raise RuntimeError("sementes de teste não correspondem ao tamanho congelado")
    if list(REGISTROS.glob("07-primario-*.json")):
        raise FileExistsError("teste primário já iniciado; não repetir sementes")

    celula = config["celula_primaria"]
    camera = config["config_camera"]
    baseline = config["baseline_selecionado"]
    acuracias_camera, acuracias_baseline = [], []
    for semente in sementes:
        dados = gerar_dados(
            semente, sigma_medio=float(celula["sigma_medio"]),
            heterogeneidade=float(celula["heterogeneidade"]),
            n_contextos=int(celula["n_contextos"]),
            exposicoes=int(celula["exposicoes"]), forca=float(celula["forca"]),
        )
        score_camera = acuracia(dados, "camaras", camera, semente=semente)
        score_baseline = acuracia(
            dados, baseline["familia"], baseline["config"], semente=semente
        )
        acuracias_camera.append(score_camera)
        acuracias_baseline.append(score_baseline)
        por_semente = criar_registro(
            experimento="07-primario-semente",
            parametros={"semente": semente, "celula_primaria": celula,
                        "camera": camera, "baseline": baseline},
            metricas={"acuracia_camaras": [score_camera],
                      "acuracia_baseline": [score_baseline],
                      "delta_pareado": [score_camera - score_baseline]},
            sementes_calibracao=config["sementes_calibracao"],
            sementes_teste=[semente], sementes_metricas=[semente],
            configuracao={"commit_no_inicio": commit_inicio},
        )
        salvar_registro(por_semente)

    deltas = np.asarray(acuracias_camera) - np.asarray(acuracias_baseline)
    analise = diferenca_pareada(
        acuracias_camera, acuracias_baseline, margem=0.05,
        confianca=0.95, reamostragens=10_000, semente=81,
    )
    registro = criar_registro(
        experimento="07-primario",
        parametros={"celula_primaria": celula, "camera": camera,
                    "baseline": baseline, "efeito_minimo": 0.05},
        metricas={"acuracia_camaras": acuracias_camera,
                  "acuracia_baseline": acuracias_baseline,
                  "delta_pareado": deltas.tolist()},
        sementes_calibracao=config["sementes_calibracao"],
        sementes_teste=list(sementes),
        configuracao={"configuracao_congelada": "experimentos/07/configuracao-congelada.json",
                      "analise_delta": analise,
                      "commit_no_inicio": commit_inicio},
    )
    caminho = salvar_registro(registro)
    print(f"Δ médio={analise['media']:.4f}; IC95% "
          f"[{analise['inferior']:.4f}, {analise['superior']:.4f}]; "
          f"desfecho={analise['decisao']}")
    print(f"Registro por semente: {caminho}")
    return registro


if __name__ == "__main__":
    executar()
