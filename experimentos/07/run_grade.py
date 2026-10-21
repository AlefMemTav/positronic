"""Executa a grade exploratória somente após o teste primário commitado."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from modelos import (acuracia, gerar_dados, prever_camaras,
                     prever_camaras_sem_contextos)
from protocolo import (REGISTROS, carregar_configuracao,
                       exigir_arvore_limpa, exigir_registro_primario_commitado)
from registro import criar_registro, salvar_registro


SEMENTES = tuple(range(10000, 10010))


def _chave(sigma: float, heterogeneidade: float, contextos: int,
           forca: float, exposicoes: int) -> str:
    return (f"s{sigma:.1f}_h{heterogeneidade:.2f}_c{contextos}"
            f"_f{forca:.1f}_e{exposicoes}")


def executar() -> dict:
    exigir_arvore_limpa()
    exigir_registro_primario_commitado()
    config = carregar_configuracao()
    if list(REGISTROS.glob("07-grade-semente-*.json")):
        raise FileExistsError("a grade exploratória já foi iniciada; não repetir sementes")
    camera = config["config_camera"]
    baseline = config["baseline_selecionado"]
    metricas_por_semente = []

    sigmas = (1.6, 2.0, 2.4)
    heterogeneidades = (0.35, 1.0)
    contextos_grid = (2, 4, 8)
    forca_grid = (0.4, 0.8, 1.2)
    exposicoes_grid = (0, 1, 3, 10)

    for semente in SEMENTES:
        metricas: dict[str, list[float]] = {}
        for sigma in sigmas:
            for heterogeneidade in heterogeneidades:
                for n_contextos in contextos_grid:
                    for forca in forca_grid:
                        for exposicoes in exposicoes_grid:
                            dados = gerar_dados(
                                semente, sigma_medio=sigma,
                                heterogeneidade=heterogeneidade,
                                n_contextos=n_contextos,
                                exposicoes=exposicoes, forca=forca,
                            )
                            nome = _chave(sigma, heterogeneidade, n_contextos,
                                          forca, exposicoes)
                            score_camera = acuracia(
                                dados, "camaras", camera, semente=semente
                            )
                            score_baseline = acuracia(
                                dados, baseline["familia"], baseline["config"],
                                semente=semente,
                            )
                            metricas[f"{nome}/camaras"] = [score_camera]
                            metricas[f"{nome}/baseline"] = [score_baseline]
                            metricas[f"{nome}/delta"] = [score_camera - score_baseline]

        celula = config["celula_primaria"]
        dados_primarios = gerar_dados(
            semente, sigma_medio=float(celula["sigma_medio"]),
            heterogeneidade=float(celula["heterogeneidade"]),
            n_contextos=int(celula["n_contextos"]),
            exposicoes=int(celula["exposicoes"]), forca=float(celula["forca"]),
        )
        sem_largura = prever_camaras(
            dados_primarios, camera, largura_adaptativa=False,
            deslocamento_interno=True,
        )
        sem_deslocamento = prever_camaras(
            dados_primarios, camera, largura_adaptativa=True,
            deslocamento_interno=False,
        )
        sem_contextos = prever_camaras_sem_contextos(dados_primarios, camera)
        metricas["ablacao_primaria/sem_largura"] = [
            float(np.mean(sem_largura == dados_primarios.y_teste))
        ]
        metricas["ablacao_primaria/sem_deslocamento"] = [
            float(np.mean(sem_deslocamento == dados_primarios.y_teste))
        ]
        metricas["ablacao_primaria/sem_camaras_por_contexto"] = [
            float(np.mean(sem_contextos == dados_primarios.y_teste))
        ]

        registro_semente = criar_registro(
            experimento="07-grade-semente",
            parametros={"semente": semente}, metricas=metricas,
            sementes_calibracao=config["sementes_calibracao"],
            sementes_teste=[semente], sementes_metricas=[semente],
            configuracao={"grade": "216 células; ablações na célula primária"},
        )
        salvar_registro(registro_semente)
        metricas_por_semente.append(metricas)

    metricas_completas: dict[str, list[float]] = {}
    for chave in metricas_por_semente[0]:
        metricas_completas[chave] = [
            float(entrada[chave][0]) for entrada in metricas_por_semente
        ]
    resumo = {
        chave: float(np.mean(valores))
        for chave, valores in metricas_completas.items()
    }
    registro_grade = criar_registro(
        experimento="07-grade-exploratoria",
        parametros={"sigma_medio": list(sigmas),
                    "heterogeneidade": list(heterogeneidades),
                    "n_contextos": list(contextos_grid),
                    "forca": list(forca_grid),
                    "exposicoes": list(exposicoes_grid)},
        metricas=metricas_completas,
        sementes_calibracao=config["sementes_calibracao"],
        sementes_teste=list(SEMENTES),
        configuracao={"camera": camera, "baseline": baseline,
                      "medias_exploratorias": resumo,
                      "zero_exposicoes": "interpretar separadamente",
                      "ablacoes": "somente na célula primária"},
    )
    caminho = salvar_registro(registro_grade)
    print(f"Grade exploratória gravada: {caminho}")
    print("Os resultados são exploratórios; não alteram a decisão primária.")
    return registro_grade


if __name__ == "__main__":
    executar()
