"""Calibra o Exp. 7; não abre as sementes de teste."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from modelos import acuracia, configuracoes, gerar_dados
from protocolo import CONFIGURACAO, codigo_fingerprint
from registro import ambiente_git, criar_registro, salvar_registro


SEMENTES = tuple(range(8000, 8030))
SIGMAS = (1.6, 2.0, 2.4)
BASELINES = ("ncm", "ncm_global", "knn", "centro_contexto", "mlp",
             "gaussian_nb", "variancia_identidade")
warnings.filterwarnings("ignore", category=ConvergenceWarning)


def _avaliar_sigma(sigma_medio: float) -> dict:
    configs = configuracoes()
    scores = {
        familia: [[] for _ in lista]
        for familia, lista in configs.items()
    }
    fixos = {familia: [] for familia in ("ncm", "ncm_global")}
    for semente in SEMENTES:
        dados = gerar_dados(
            semente, sigma_medio=sigma_medio, heterogeneidade=1.0,
            n_contextos=4, exposicoes=3, forca=0.8,
        )
        for familia, lista in configs.items():
            for indice, config in enumerate(lista):
                valor = acuracia(dados, familia, config, semente=semente)
                scores[familia][indice].append(valor)
        for familia in fixos:
            fixos[familia].append(acuracia(dados, familia, {}, semente=semente))

    ajustes: dict[str, list[dict]] = {}
    melhores: dict[str, dict] = {}
    for familia, lista in configs.items():
        ajustes[familia] = []
        for config, valores in zip(lista, scores[familia]):
            ajustes[familia].append({
                "config": config,
                "media": float(np.mean(valores)),
                "por_semente": [float(v) for v in valores],
            })
        melhores[familia] = max(ajustes[familia], key=lambda item: item["media"])

    fixos_resumo = {
        familia: {"config": {}, "media": float(np.mean(valores)),
                  "por_semente": [float(v) for v in valores]}
        for familia, valores in fixos.items()
    }
    candidatos = [
        {"familia": familia, **fixos_resumo[familia]}
        for familia in ("ncm", "ncm_global")
    ]
    candidatos.extend(
        {"familia": familia, **melhores[familia]}
        for familia in BASELINES[2:]
    )
    # max preserva o primeiro item em empate: a ordem acima é pré-registrada.
    melhor_baseline = max(candidatos, key=lambda item: item["media"])
    melhor_camera = melhores["camaras"]
    return {
        "sigma_medio": float(sigma_medio),
        "H_cal": float(1 - melhor_baseline["media"]),
        "executavel": bool(1 - melhor_baseline["media"] >= 0.10),
        "melhor_camera": melhor_camera,
        "melhor_baseline": melhor_baseline,
        "baselines_fixos": fixos_resumo,
        "melhores_por_familia": melhores,
        "buscas": ajustes,
    }


def _metricas_registro(resultados: list[dict]) -> tuple[dict, dict]:
    metricas: dict[str, list[float]] = {}
    mapa = {}
    for indice_sigma, resultado in enumerate(resultados):
        prefixo = f"sigma_{indice_sigma}_{resultado['sigma_medio']:.1f}"
        for familia, resumo in resultado["baselines_fixos"].items():
            chave = f"{prefixo}/fixo/{familia}"
            metricas[chave] = resumo["por_semente"]
            mapa[chave] = {"familia": familia, "config": {}}
        for familia, tentativas in resultado["buscas"].items():
            for indice, tentativa in enumerate(tentativas):
                chave = f"{prefixo}/{familia}/{indice:02d}"
                metricas[chave] = tentativa["por_semente"]
                mapa[chave] = {"familia": familia, "config": tentativa["config"]}
    return metricas, mapa


def executar() -> dict:
    if CONFIGURACAO.exists():
        raise FileExistsError(
            f"não sobrescrevo configuração existente: {CONFIGURACAO}"
        )
    if list((ROOT / "resultados" / "execucoes").glob("07-calibracao-*.json")):
        raise FileExistsError("já existe registro de calibração do Exp. 7")

    git = ambiente_git()
    if git["alteracoes_locais"]:
        raise RuntimeError("calibração exige árvore limpa antes da primeira semente")

    resultados = []
    selecionado = None
    for sigma_medio in SIGMAS:
        resultado = _avaliar_sigma(sigma_medio)
        resultados.append(resultado)
        if resultado["executavel"]:
            selecionado = resultado
            break

    metricas, mapa_metricas = _metricas_registro(resultados)
    calibracao = criar_registro(
        experimento="07-calibracao",
        parametros={
            "sementes": list(SEMENTES),
            "sigma_barra_em_ordem": list(SIGMAS),
            "regime": {"heterogeneidade": 1.0, "n_contextos": 4,
                       "exposicoes": 3, "forca": 0.8},
        },
        metricas=metricas,
        sementes_calibracao=list(SEMENTES), sementes_teste=[],
        sementes_metricas=list(SEMENTES),
        configuracao={"ordem_baselines": list(BASELINES),
                      "configuracoes_por_metrica": mapa_metricas,
                      "resultados_por_sigma": [
                          {"sigma_medio": item["sigma_medio"],
                           "H_cal": item["H_cal"],
                           "executavel": item["executavel"],
                           "melhor_camera": item["melhor_camera"]["config"],
                           "melhor_baseline": {
                               "familia": item["melhor_baseline"]["familia"],
                               "config": item["melhor_baseline"]["config"],
                               "media": item["melhor_baseline"]["media"],
                           }} for item in resultados
                      ]},
    )
    caminho_registro = salvar_registro(calibracao)

    amostra = None
    if selecionado:
        deltas = np.asarray(selecionado["melhor_camera"]["por_semente"]) - np.asarray(
            selecionado["melhor_baseline"]["por_semente"]
        )
        s_delta = float(np.std(deltas, ddof=1))
        n = min(100, max(30, int(np.ceil((1.96 * s_delta / 0.015) ** 2))))
        amostra = {"s_delta_ddof_1": s_delta, "n": n,
                   "sementes_teste": list(range(9000, 9000 + n))}

    congelada = {
        "schema_version": 1,
        "experimento": "07-heterocedasticidade",
        "criado_em_utc": datetime.now(timezone.utc).isoformat(),
        "executavel_confirmatorio": selecionado is not None,
        "git": git,
        "fingerprint_codigo": codigo_fingerprint(),
        "commit_preregistro": subprocess.run(
            ["git", "log", "-1", "--format=%H", "--",
             "experimentos/07/PREREGISTRO.md"], cwd=ROOT, check=True,
            capture_output=True, text=True,
        ).stdout.strip(),
        "registro_calibracao": caminho_registro.relative_to(ROOT).as_posix(),
        "sementes_calibracao": list(SEMENTES),
        "sigma_avaliados": [item["sigma_medio"] for item in resultados],
        "resultado_por_sigma": [
            {"sigma_medio": item["sigma_medio"], "H_cal": item["H_cal"],
             "passou_gate": item["executavel"]}
            for item in resultados
        ],
        "celula_primaria": (None if selecionado is None else {
            "sigma_medio": selecionado["sigma_medio"],
            "heterogeneidade": 1.0, "n_contextos": 4,
            "exposicoes": 3, "forca": 0.8,
        }),
        "config_camera": (None if selecionado is None else
                          selecionado["melhor_camera"]["config"]),
        "baseline_selecionado": (None if selecionado is None else {
            "familia": selecionado["melhor_baseline"]["familia"],
            "config": selecionado["melhor_baseline"]["config"],
            "media_calibracao": selecionado["melhor_baseline"]["media"],
        }),
        "acuracia_calibracao_camaras": (None if selecionado is None else
                                        selecionado["melhor_camera"]["media"]),
        "H_cal": (None if selecionado is None else selecionado["H_cal"]),
        "dimensionamento_teste": amostra,
        "criterio_s_delta": "desvio padrão amostral ddof=1 dos deltas pareados",
    }
    with CONFIGURACAO.open("x", encoding="utf-8") as stream:
        json.dump(congelada, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")

    if selecionado is None:
        print("Gate H_cal >= 0,10 falhou para todos os níveis de sigma; teste bloqueado.")
    else:
        print(f"Sigma selecionado: {selecionado['sigma_medio']:.1f}")
        print(f"H_cal: {selecionado['H_cal']:.4f}")
        print(f"Baseline: {selecionado['melhor_baseline']['familia']} "
              f"{selecionado['melhor_baseline']['config']}")
        print(f"Câmaras: {selecionado['melhor_camera']['config']}")
        print(f"s_delta (ddof=1): {amostra['s_delta_ddof_1']:.6f}; n={amostra['n']}")
        print("O teste ainda exige commit da configuração e árvore limpa.")
    print(f"Registro de calibração: {caminho_registro}")
    print(f"Configuração: {CONFIGURACAO}")
    return congelada


if __name__ == "__main__":
    executar()
