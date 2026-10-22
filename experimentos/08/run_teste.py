"""Executa uma vez o teste confirmatório do experimento 8."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from modelos import avaliar, gerar_episodio
from protocolo import (REGISTROS, carregar_configuracao,
                       exigir_arvore_limpa)
from registro import criar_registro, intervalo_bootstrap, salvar_registro


MARGEM_R = 0.30


def _decisao(limite_inferior: float, limite_superior: float) -> str:
    if limite_inferior >= MARGEM_R:
        return "confirmado"
    if limite_superior < MARGEM_R:
        return "refutado quanto ao efeito mínimo"
    return "inconclusivo"


def executar() -> dict:
    commit_inicio = exigir_arvore_limpa()
    config = carregar_configuracao()
    sementes = tuple(config["dimensionamento_teste"]["sementes_teste"])
    if not 30 <= len(sementes) <= 100:
        raise RuntimeError("tamanho de teste fora dos limites pré-registrados")
    if sementes != tuple(range(13000, 13000 + len(sementes))):
        raise RuntimeError("sementes de teste não correspondem à regra congelada")
    if list(REGISTROS.glob("08-primario-*.json")):
        raise FileExistsError("teste primário já iniciado; não repetir")

    sigma = float(config["sigma_primario"])
    config_traco = config["config_traco"]
    recalls_antes, acuracias_balanceadas_antes = [], []
    e90_apagar, e90_traco, e90_cache, e90_completo = [], [], [], []

    for seed in sementes:
        episodio = gerar_episodio(seed, sigma=sigma)
        apagar = avaliar(episodio, metodo="apagar", sigma=sigma, seed=seed)
        traco = avaliar(episodio, metodo="traco", sigma=sigma,
                        config=config_traco, seed=seed)
        cache = avaliar(episodio, metodo="cache", sigma=sigma, seed=seed)
        completo = avaliar(episodio, metodo="manter_tudo", sigma=sigma, seed=seed)
        if (not apagar["alvo_expulso"] or not traco["alvo_expulso"]
                or not cache["alvo_expulso"] or completo["alvo_expulso"]):
            raise RuntimeError(f"o alvo não foi expulso na semente {seed}")

        recalls_antes.append(apagar["recall_alvo_antes"])
        acuracias_balanceadas_antes.append(apagar["acuracia_balanceada_antes"])
        e90_apagar.append(apagar["e90"])
        e90_traco.append(traco["e90"])
        e90_cache.append(cache["e90"])
        e90_completo.append(completo["e90"])

        economia_traco = 1.0 - traco["e90"] / apagar["e90"]
        economia_cache = 1.0 - cache["e90"] / apagar["e90"]
        registro_semente = criar_registro(
            experimento="08-primario-semente",
            parametros={"semente": seed, "sigma": sigma,
                        "config_traco": config_traco},
            metricas={
                "recall_alvo_antes_expulsao": [apagar["recall_alvo_antes"]],
                "acuracia_balanceada_antes_expulsao": [
                    apagar["acuracia_balanceada_antes"]
                ],
                "e90_apagar": [apagar["e90"]],
                "e90_traco": [traco["e90"]],
                "e90_cache": [cache["e90"]],
                "e90_manter_tudo": [completo["e90"]],
                "economia_relativa_traco": [economia_traco],
                "economia_relativa_cache": [economia_cache],
            },
            sementes_calibracao=config["sementes_calibracao"],
            sementes_teste=[seed], sementes_metricas=[seed],
            configuracao={
                "commit_no_inicio": commit_inicio,
                "curvas_recall_alvo": {
                    "apagar": apagar["curva_recall_alvo"],
                    "traco": traco["curva_recall_alvo"],
                    "cache": cache["curva_recall_alvo"],
                    "manter_tudo": completo["curva_recall_alvo"],
                },
                "curvas_acuracia_balanceada": {
                    "apagar": apagar["curva_acuracia_balanceada"],
                    "traco": traco["curva_acuracia_balanceada"],
                    "cache": cache["curva_acuracia_balanceada"],
                    "manter_tudo": completo["curva_acuracia_balanceada"],
                },
            },
        )
        salvar_registro(registro_semente)

    economia = 1.0 - np.asarray(e90_traco, dtype=float) / np.asarray(
        e90_apagar, dtype=float
    )
    cache_economia = 1.0 - np.asarray(e90_cache, dtype=float) / np.asarray(
        e90_apagar, dtype=float
    )
    ic = intervalo_bootstrap(
        economia, confianca=0.95, reamostragens=10_000, semente=81
    )
    decisao = _decisao(ic["inferior"], ic["superior"])
    resumo = criar_registro(
        experimento="08-primario",
        parametros={"sigma": sigma, "config_traco": config_traco,
                    "economia_minima": MARGEM_R},
        metricas={
            "recall_alvo_antes_expulsao": recalls_antes,
            "acuracia_balanceada_antes_expulsao": acuracias_balanceadas_antes,
            "e90_apagar": e90_apagar,
            "e90_traco": e90_traco,
            "e90_cache": e90_cache,
            "e90_manter_tudo": e90_completo,
            "economia_relativa_traco": economia.tolist(),
            "economia_relativa_cache": cache_economia.tolist(),
        },
        sementes_calibracao=config["sementes_calibracao"],
        sementes_teste=list(sementes), sementes_metricas=list(sementes),
        configuracao={
            "decisao_confirmatoria": decisao,
            "ic95_economia_traco": ic,
            "commit_no_inicio": commit_inicio,
            "configuracao_congelada": "experimentos/08/configuracao-congelada.json",
        },
    )
    salvar_registro(resumo)
    print(f"Economia relativa do traço={ic['media']:.3f}; IC95% "
          f"[{ic['inferior']:.3f}, {ic['superior']:.3f}]; {decisao}")
    return resumo


if __name__ == "__main__":
    executar()
