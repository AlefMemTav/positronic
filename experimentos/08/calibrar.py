"""Executa somente calibração e congela a configuração antes do teste."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from modelos import (MAX_EXPOSICOES_RETORNO, SIGMAS, avaliar, configuracoes_traco,
                     gerar_episodio)
from protocolo import (CONFIGURACAO, REGISTROS, codigo_fingerprint,
                       exigir_arvore_limpa)
from registro import criar_registro, salvar_registro


SEMENTES = tuple(range(12000, 12030))
MARGEM_R = 0.30
MEIA_LARGURA_ALVO = 0.10


def _avaliar_apagar(sigma: float) -> list[dict]:
    resultados = []
    for seed in SEMENTES:
        episodio = gerar_episodio(seed, sigma=sigma)
        resultados.append(avaliar(episodio, metodo="apagar", sigma=sigma,
                                  seed=seed))
    return resultados


def _passa_gate(resultados: list[dict]) -> bool:
    recall_medio = float(np.mean([r["recall_alvo_antes"] for r in resultados]))
    e90 = [r["e90"] for r in resultados]
    return bool(
        0.70 <= recall_medio <= 0.98
        and all(r["alvo_expulso"] for r in resultados)
        and all(1 <= valor <= MAX_EXPOSICOES_RETORNO for valor in e90)
        and float(np.mean(e90)) >= 2.0
    )


def executar() -> dict:
    if CONFIGURACAO.exists():
        raise FileExistsError(f"não sobrescrevo {CONFIGURACAO}")
    if list(REGISTROS.glob("08-calibracao-*.json")):
        raise FileExistsError("já existe registro de calibração do experimento 8")
    commit_inicio = exigir_arvore_limpa()

    por_sigma: dict[str, list[dict]] = {}
    sigma_escolhido = None
    apagamento_escolhido = None
    for sigma in SIGMAS:
        resultados = _avaliar_apagar(sigma)
        por_sigma[str(sigma)] = resultados
        if _passa_gate(resultados):
            sigma_escolhido = sigma
            apagamento_escolhido = resultados
            break

    metricas: dict[str, list[float]] = {}
    resumo_configuracoes = []
    config_escolhida = None
    cache_resultados = []
    dimensionamento = None

    for indice_sigma, sigma in enumerate(SIGMAS):
        if str(sigma) not in por_sigma:
            continue
        metricas[f"sigma_{indice_sigma}_{sigma}/apagar/e90"] = [
            float(r["e90"]) for r in por_sigma[str(sigma)]
        ]
        metricas[f"sigma_{indice_sigma}_{sigma}/apagar/recall_alvo_antes"] = [
            float(r["recall_alvo_antes"]) for r in por_sigma[str(sigma)]
        ]

    if sigma_escolhido is not None and apagamento_escolhido is not None:
        episodos = {seed: gerar_episodio(seed, sigma=sigma_escolhido)
                    for seed in SEMENTES}
        apagamento = np.asarray([r["e90"] for r in apagamento_escolhido], dtype=float)
        melhor_media = -np.inf
        for indice, config_traco in enumerate(configuracoes_traco()):
            resultados = [
                avaliar(episodos[seed], metodo="traco", sigma=sigma_escolhido,
                        config=config_traco, seed=seed)
                for seed in SEMENTES
            ]
            e90_traco = np.asarray([r["e90"] for r in resultados], dtype=float)
            economia = 1.0 - e90_traco / apagamento
            chave = f"traco/{indice:02d}"
            metricas[chave] = economia.tolist()
            resumo_configuracoes.append({
                "config": config_traco,
                "media_economia_relativa": float(np.mean(economia)),
                "e90_por_semente": e90_traco.tolist(),
                "economia_por_semente": economia.tolist(),
            })
            if float(np.mean(economia)) > melhor_media:
                melhor_media = float(np.mean(economia))
                config_escolhida = config_traco

        cache_resultados = [
            avaliar(episodos[seed], metodo="cache", sigma=sigma_escolhido,
                    seed=seed)
            for seed in SEMENTES
        ]
        e90_cache = np.asarray([r["e90"] for r in cache_resultados], dtype=float)
        metricas["cache/economia_relativa_vs_apagar"] = (
            1.0 - e90_cache / apagamento
        ).tolist()
        metricas["cache/e90"] = e90_cache.tolist()
        s_r = float(np.std(
            resumo_configuracoes[
                configuracoes_traco().index(config_escolhida)
            ]["economia_por_semente"], ddof=1
        ))
        n_teste = min(100, max(30, math.ceil((1.96 * s_r / MEIA_LARGURA_ALVO) ** 2)))
        dimensionamento = {
            "s_R_calibracao": s_r,
            "meia_largura_alvo": MEIA_LARGURA_ALVO,
            "n": n_teste,
            "sementes_teste": list(range(13000, 13000 + n_teste)),
        }

    executavel = sigma_escolhido is not None
    config_final = {
        "experimento": "08-retorno-rapido",
        "criado_em_utc": datetime.now(timezone.utc).isoformat(),
        "executavel_confirmatorio": executavel,
        "sigma_primario": sigma_escolhido,
        "config_traco": config_escolhida,
        "ementa_gate": {
            "recall_alvo_antes_minimo": 0.70,
            "recall_alvo_antes_maximo": 0.98,
            "e90_apagar_minima_media": 2.0,
            "max_exposicoes": MAX_EXPOSICOES_RETORNO,
            "ordem_sigma": list(SIGMAS),
        },
        "dimensionamento_teste": dimensionamento,
        "sementes_calibracao": list(SEMENTES),
        "resumo_configuracoes_traco": resumo_configuracoes,
        "cache_secundario_e90": [r.get("e90") for r in cache_resultados],
        "fingerprint_codigo": codigo_fingerprint(),
        "git": {"commit": commit_inicio, "alteracoes_locais": False},
    }

    registro = criar_registro(
        experimento="08-calibracao",
        parametros={"sigma_candidatos": list(SIGMAS),
                    "grade_traco": configuracoes_traco(),
                    "efeito_minimo_economia": MARGEM_R},
        metricas=metricas,
        sementes_calibracao=list(SEMENTES),
        sementes_teste=[],
        sementes_metricas=list(SEMENTES),
        configuracao={
            "executavel_confirmatorio": executavel,
            "sigma_primario": sigma_escolhido,
            "config_traco": config_escolhida,
            "commit_no_inicio": commit_inicio,
            "gates_por_sigma": {
                sigma: _passa_gate(resultados)
                for sigma, resultados in por_sigma.items()
            },
        },
    )
    caminho_registro = salvar_registro(registro)
    with CONFIGURACAO.open("x", encoding="utf-8") as stream:
        json.dump(config_final, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")

    if executavel:
        print(f"Calibração concluída: sigma={sigma_escolhido}; "
              f"configuração={config_escolhida}; n_teste={dimensionamento['n']}")
    else:
        print("Calibração não executável; nenhuma semente de teste deve ser aberta.")
    print(f"Registro: {caminho_registro}")
    return config_final


if __name__ == "__main__":
    executar()
