"""Rastreabilidade e estatística de execuções experimentais."""
from __future__ import annotations

from datetime import datetime, timezone
from importlib import metadata
import json
from pathlib import Path
import subprocess
import uuid

import numpy as np


ROOT = Path(__file__).resolve().parent


def _versao(distribuicao: str) -> str | None:
    try:
        return metadata.version(distribuicao)
    except metadata.PackageNotFoundError:
        return None


def ambiente_git(root: Path = ROOT) -> dict:
    """Retorna commit e indicador de alterações locais sem falhar fora do Git."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        sujo = bool(subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, check=True,
            capture_output=True, text=True,
        ).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        commit, sujo = None, None
    return {"commit": commit, "alteracoes_locais": sujo}


def _vetor(valores, nome: str = "valores") -> np.ndarray:
    vetor = np.asarray(valores, dtype=float)
    if vetor.ndim != 1 or vetor.size == 0:
        raise ValueError(f"{nome} precisa ser um vetor não vazio")
    if not np.isfinite(vetor).all():
        raise ValueError(f"{nome} contém valor não finito")
    return vetor


def intervalo_bootstrap(valores, *, confianca=0.95, reamostragens=10_000,
                        semente=0) -> dict:
    """IC percentil bootstrap da média; a unidade amostral é a semente."""
    x = _vetor(valores)
    if not 0 < confianca < 1:
        raise ValueError("confianca deve estar entre 0 e 1")
    if reamostragens < 1:
        raise ValueError("reamostragens deve ser positiva")
    rng = np.random.default_rng(semente)
    indices = rng.integers(0, x.size, size=(reamostragens, x.size))
    medias = x[indices].mean(axis=1)
    cauda = (1 - confianca) / 2
    inferior, superior = np.quantile(medias, [cauda, 1 - cauda])
    return {
        "n_sementes": int(x.size),
        "media": float(x.mean()),
        "desvio_padrao": float(x.std(ddof=1)) if x.size > 1 else 0.0,
        "confianca": float(confianca),
        "inferior": float(inferior),
        "superior": float(superior),
        "reamostragens": int(reamostragens),
        "semente_bootstrap": int(semente),
    }


def diferenca_pareada(modelo, baseline, *, margem=0.05, **kwargs) -> dict:
    """IC da diferença modelo−baseline com pareamento por semente."""
    a, b = _vetor(modelo, "modelo"), _vetor(baseline, "baseline")
    if a.shape != b.shape:
        raise ValueError("modelo e baseline precisam ter o mesmo nº de sementes")
    if not 0 <= margem <= 1:
        raise ValueError("margem precisa estar entre 0 e 1")
    resultado = intervalo_bootstrap(a - b, **kwargs)
    lo, hi = resultado["inferior"], resultado["superior"]
    if lo >= margem:
        decisao = "confirmado"
    elif hi < margem:
        decisao = "refutado"
    else:
        decisao = "inconclusivo"
    return {**resultado, "margem_relevante": float(margem), "decisao": decisao}


def holm(p_valores) -> list[float]:
    """Ajuste de Holm–Bonferroni, devolvido na ordem de entrada."""
    p = _vetor(p_valores, "p_valores")
    if ((p < 0) | (p > 1)).any():
        raise ValueError("p-valores devem estar entre 0 e 1")
    ordem = np.argsort(p)
    ajustados = np.empty_like(p)
    maior = 0.0
    n = len(p)
    for posto, indice in enumerate(ordem):
        maior = max(maior, min(1.0, (n - posto) * p[indice]))
        ajustados[indice] = maior
    return ajustados.tolist()


def criar_registro(*, experimento: str, parametros: dict, metricas: dict,
                   sementes_calibracao: list[int],
                   sementes_teste: list[int],
                   sementes_metricas: list[int] | None = None,
                   configuracao: dict | None = None) -> dict:
    """Cria documento JSON com observações por semente e proveniência."""
    metricas_validas = {}
    sementes_metricas = (sementes_teste if sementes_metricas is None
                         else sementes_metricas)
    n_metricas = len(sementes_metricas)
    for nome, valores in metricas.items():
        vetor = _vetor(valores, f"métrica {nome}")
        if vetor.size != n_metricas:
            raise ValueError(f"{nome}: esperado um valor por semente de métrica")
        metricas_validas[nome] = [float(v) for v in vetor]
    return {
        "schema_version": 1,
        "run_id": str(uuid.uuid4()),
        "criado_em_utc": datetime.now(timezone.utc).isoformat(),
        "experimento": experimento,
        "git": ambiente_git(),
        "ambiente": {
            "python": __import__("sys").version.split()[0],
            "numpy": _versao("numpy"),
            "scikit_learn": _versao("scikit-learn"),
        },
        "parametros": parametros,
        "configuracao": configuracao or {},
        "sementes": {
            "calibracao": [int(s) for s in sementes_calibracao],
            "teste": [int(s) for s in sementes_teste],
            "metricas": [int(s) for s in sementes_metricas],
        },
        "metricas_por_semente": metricas_validas,
    }


def salvar_registro(registro: dict, pasta: str | Path = "resultados/execucoes") -> Path:
    """Grava um JSON novo sem sobrescrever resultados anteriores."""
    destino = Path(pasta)
    if not destino.is_absolute():
        destino = ROOT / destino
    destino.mkdir(parents=True, exist_ok=True)
    nome = f"{registro['experimento']}-{registro['run_id']}.json"
    arquivo = destino / nome
    with arquivo.open("x", encoding="utf-8") as stream:
        json.dump(registro, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    return arquivo
