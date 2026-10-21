"""Seleciona configuração apenas com sementes de calibração do pré-registro."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from modelos import acuracia, configuracoes, gerar_dados
from registro import ambiente_git


SEMENTES = tuple(range(4000, 4030))
PRIMARY = {"n_contextos": 4, "exposicoes": 3, "forca": 0.8}
SAIDA = Path(__file__).with_name("configuracao-congelada.json")
warnings.filterwarnings("ignore", category=ConvergenceWarning)


def executar() -> dict:
    configs = configuracoes()
    familias = {
        familia: [(config, []) for config in lista]
        for familia, lista in configs.items()
    }
    fixos = {"ncm": [], "ncm_global": []}
    for semente in SEMENTES:
        dados = gerar_dados(semente, **PRIMARY)
        for familia, tentativas in familias.items():
            for config, scores in tentativas:
                scores.append(acuracia(dados, familia, config, semente=semente))
        for familia in fixos:
            fixos[familia].append(acuracia(dados, familia, {}, semente=semente))

    escolhidos = {}
    tabela = {}
    for familia, tentativas in familias.items():
        melhor_config, melhor_scores = max(tentativas, key=lambda item: np.mean(item[1]))
        escolhidos[familia] = {
            "config": melhor_config,
            "media_calibracao": float(np.mean(melhor_scores)),
        }
        tabela[familia] = [
            {"config": config, "media": float(np.mean(scores)),
             "por_semente": [float(v) for v in scores]}
            for config, scores in tentativas
        ]

    melhores_baselines = {
        "ncm": {"familia": "ncm", "config": {},
                "media_calibracao": float(np.mean(fixos["ncm"]))},
        "ncm_global": {"familia": "ncm_global", "config": {},
                       "media_calibracao": float(np.mean(fixos["ncm_global"]))},
    }
    for familia in ("knn", "centro_contexto", "mlp"):
        melhores_baselines[familia] = {
            "familia": familia,
            "config": escolhidos[familia]["config"],
            "media_calibracao": escolhidos[familia]["media_calibracao"],
        }
    baseline = max(melhores_baselines.values(), key=lambda item: item["media_calibracao"])
    congelada = {
        "schema_version": 1,
        "experimento": "06-contexto-nao-aditivo",
        "criado_em_utc": datetime.now(timezone.utc).isoformat(),
        "git": ambiente_git(),
        "semente_calibracao": list(SEMENTES),
        "celula_primaria": PRIMARY,
        "config_camera": escolhidos["camaras"],
        "baseline_selecionado": baseline,
        "media_calibracao_camaras": escolhidos["camaras"]["media_calibracao"],
        "media_calibracao_baseline": baseline["media_calibracao"],
        "placar_calibracao": tabela,
        "baselines_fixos": {
            nome: {"media": float(np.mean(valores)),
                   "por_semente": [float(v) for v in valores]}
            for nome, valores in fixos.items()
        },
    }
    with SAIDA.open("x", encoding="utf-8") as stream:
        json.dump(congelada, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(f"Câmaras: {escolhidos['camaras']['config']} — "
          f"{escolhidos['camaras']['media_calibracao']:.3f}")
    print(f"Baseline selecionado: {baseline['familia']} {baseline['config']} — "
          f"{baseline['media_calibracao']:.3f}")
    print(f"Configuração congelada: {SAIDA}")
    return congelada


if __name__ == "__main__":
    executar()
