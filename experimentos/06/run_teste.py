"""Avaliação congelada do experimento 6: teste primário e grade exploratória."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from modelos import acuracia, gerar_dados
from registro import criar_registro, diferenca_pareada, salvar_registro


CALIBRACAO = tuple(range(4000, 4030))
TESTE_PRIMARIO = tuple(range(5000, 5030))
TESTE_GRADE = tuple(range(6000, 6010))
CONFIG_PATH = Path(__file__).with_name("configuracao-congelada.json")


def _par(dados, camera, baseline, semente):
    a = acuracia(dados, "camaras", camera, semente=semente)
    b = acuracia(dados, baseline["familia"], baseline["config"],
                 semente=semente)
    return a, b


def executar() -> dict:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    camera = config["config_camera"]["config"]
    baseline = config["baseline_selecionado"]
    celula = config["celula_primaria"]

    cameras, baselines = [], []
    for semente in TESTE_PRIMARIO:
        dados = gerar_dados(semente, **celula)
        a, b = _par(dados, camera, baseline, semente)
        cameras.append(a)
        baselines.append(b)

    delta = diferenca_pareada(cameras, baselines, margem=0.05, semente=81)
    primario = criar_registro(
        experimento="06-contexto-nao-aditivo-primario",
        parametros={"camera": camera, "baseline": baseline,
                    "celula": celula, "margem": 0.05},
        metricas={"acuracia_camaras": cameras,
                  "acuracia_baseline": baselines,
                  "delta_pareado": [a - b for a, b in zip(cameras, baselines)]},
        sementes_calibracao=list(CALIBRACAO),
        sementes_teste=list(TESTE_PRIMARIO),
        configuracao={"baseline_selecionado_na_calibracao": baseline,
                      "analise_delta": delta},
    )
    caminho_primario = salvar_registro(primario)
    print(f"Primário: Δ={delta['media']:.3f}; "
          f"IC95% [{delta['inferior']:.3f}, {delta['superior']:.3f}]; "
          f"decisão={delta['decisao']}")
    print(f"Registro primário: {caminho_primario}")

    metricas_grade = {}
    resumo_grade = {}
    for n_contextos in (2, 4, 8):
        for exposicoes in (0, 1, 3, 10):
            for forca in (0.4, 0.8, 1.2):
                if (n_contextos == celula["n_contextos"]
                        and exposicoes == celula["exposicoes"]
                        and forca == celula["forca"]):
                    continue
                chave = f"c{n_contextos}_e{exposicoes}_f{forca:.1f}"
                ac, ab = [], []
                for semente in TESTE_GRADE:
                    dados = gerar_dados(semente, n_contextos, exposicoes, forca)
                    a, b = _par(dados, camera, baseline, semente)
                    ac.append(a)
                    ab.append(b)
                ds = [a - b for a, b in zip(ac, ab)]
                metricas_grade[f"{chave}_camaras"] = ac
                metricas_grade[f"{chave}_baseline"] = ab
                metricas_grade[f"{chave}_delta"] = ds
                resumo_grade[chave] = {
                    "media_camaras": float(np.mean(ac)),
                    "media_baseline": float(np.mean(ab)),
                    "media_delta": float(np.mean(ds)),
                }
    exploratorio = criar_registro(
        experimento="06-contexto-nao-aditivo-grade-exploratoria",
        parametros={"camera": camera, "baseline": baseline},
        metricas=metricas_grade,
        sementes_calibracao=list(CALIBRACAO),
        sementes_teste=list(TESTE_GRADE),
        configuracao={"grade": resumo_grade,
                      "interpretacao": "exploratoria, sem decisão confirmatória"},
    )
    caminho_grade = salvar_registro(exploratorio)
    print(f"Registro da grade exploratória: {caminho_grade}")
    return {"primario": delta, "grade": resumo_grade}


if __name__ == "__main__":
    executar()
