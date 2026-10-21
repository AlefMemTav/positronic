"""Fase 1 pré-registrada: estimativa compartilhada de w0 e z_max."""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
from scipy.stats import chi2
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experimentos.comum.legado import D, fluxo_sem_rotulo, roda_descoberta
from registro import intervalo_bootstrap, criar_registro, salvar_registro


SIGMAS = (0.3, 0.4, 0.5)
SEMENTES_CALIBRACAO = tuple(range(1000, 1030))
SEMENTES_TESTE = tuple(range(3000, 3030))
ALFA = 0.01
K_VIZINHO = 3
Q_ORDEM = 0.75
PREFIXO = 1 / 3


def estimar_w0_sem_rotulo(X: np.ndarray) -> float:
    """Estima escala de ruído pela distância ao 3º vizinho no prefixo."""
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or len(X) <= K_VIZINHO:
        raise ValueError("X precisa conter mais que três vetores")
    norma = np.sum(X * X, axis=1)
    d2 = np.maximum(
        norma[:, None] + norma[None, :] - 2 * X @ X.T, 0.0
    ) / X.shape[1]
    np.fill_diagonal(d2, np.inf)
    k_vizinho = np.partition(d2, K_VIZINHO - 1, axis=1)[:, K_VIZINHO - 1]
    fator = chi2.ppf(Q_ORDEM, D) / D
    return max(float(np.median(k_vizinho) / fator), 0.02)


def _uma_condicao(semente: int, sigma: float) -> dict:
    X, y, K = fluxo_sem_rotulo(semente, sigma)
    n_prefixo = int(len(X) * PREFIXO)
    prefixo, sufixo, y_sufixo = X[:n_prefixo], X[n_prefixo:], y[n_prefixo:]
    w0 = estimar_w0_sem_rotulo(prefixo)
    z_max = float(chi2.ppf(1 - ALFA, D) / D)

    ari_auto, n_auto = roda_descoberta(
        sufixo, y_sufixo, w0=w0, z_max=z_max,
    )
    ari_fixo, n_fixo = roda_descoberta(
        sufixo, y_sufixo, w0=0.32, z_max=2.0,
    )
    labels_kmeans = KMeans(K, n_init=5, random_state=semente).fit_predict(sufixo)
    ari_kmeans = adjusted_rand_score(y_sufixo, labels_kmeans)
    return {
        "w0_estimado": w0,
        "z_max": z_max,
        "auto_ari": float(ari_auto),
        "auto_n_grupos": int(n_auto),
        "fixo_ari": float(ari_fixo),
        "fixo_n_grupos": int(n_fixo),
        "kmeans_ari": float(ari_kmeans),
    }


def executar() -> dict:
    sementes = SEMENTES_CALIBRACAO + SEMENTES_TESTE
    linhas = {sigma: [_uma_condicao(seed, sigma) for seed in sementes]
              for sigma in SIGMAS}

    def valores(chave, sigma, recorte):
        return np.array([linha[chave] for linha in linhas[sigma][recorte]])

    inicio_teste = len(SEMENTES_CALIBRACAO)
    resultados = {}
    print("Fase 1 — estimativa adaptativa, replicação nas sementes 3000–3029")
    print("σ       w0 estimado     ARI adaptativo      grupos adaptativos")
    for sigma in SIGMAS:
        teste = slice(inicio_teste, None)
        w = valores("w0_estimado", sigma, teste)
        ari = valores("auto_ari", sigma, teste)
        grupos = valores("auto_n_grupos", sigma, teste)
        fixo = valores("fixo_ari", sigma, teste)
        km = valores("kmeans_ari", sigma, teste)
        resultados[f"auto_ari_sigma_{sigma:.1f}"] = ari.tolist()
        resultados[f"auto_grupos_sigma_{sigma:.1f}"] = grupos.tolist()
        resultados[f"auto_w0_sigma_{sigma:.1f}"] = w.tolist()
        resultados[f"fixo_ari_sigma_{sigma:.1f}"] = fixo.tolist()
        resultados[f"kmeans_ari_sigma_{sigma:.1f}"] = km.tolist()
        print(f"{sigma:.1f}     {w.mean():.3f}±{w.std(ddof=1):.3f}"
              f"       {ari.mean():.3f}±{ari.std(ddof=1):.3f}"
              f"          {grupos.mean():.1f}±{grupos.std(ddof=1):.1f}")

    menor_ari_por_semente = np.min(
        np.column_stack([
            valores("auto_ari", sigma, slice(inicio_teste, None))
            for sigma in SIGMAS
        ]), axis=1,
    )
    ic_pior = intervalo_bootstrap(menor_ari_por_semente, semente=71)
    grupos_ok = all(
        18 <= valores("auto_n_grupos", sigma, slice(inicio_teste, None)).mean() <= 22
        for sigma in SIGMAS
    )
    if ic_pior["inferior"] >= 0.95 and grupos_ok:
        decisao = "sucesso"
    elif ic_pior["superior"] < 0.95:
        decisao = "refutado"
    else:
        decisao = "inconclusivo"
    print(f"Pior ARI médio por semente: {ic_pior['media']:.3f}; "
          f"IC95% [{ic_pior['inferior']:.3f}, {ic_pior['superior']:.3f}]"
          f"; grupos adequados={grupos_ok}; decisão={decisao}")

    registro = criar_registro(
        experimento="fase1-prior-adaptativo",
        parametros={"alpha": ALFA, "k_vizinho": K_VIZINHO,
                    "quantil_correcao": Q_ORDEM, "fracao_prefixo": PREFIXO,
                    "w0_fixo_baseline": 0.32, "z_max_fixo_baseline": 2.0},
        metricas=resultados,
        sementes_calibracao=list(SEMENTES_CALIBRACAO),
        sementes_teste=list(SEMENTES_TESTE),
        configuracao={"sigmas": list(SIGMAS), "pior_ari_teste": ic_pior,
                      "grupos_ok": grupos_ok, "decisao": decisao},
    )
    caminho = salvar_registro(registro)
    print(f"Registro: {caminho}")
    return {"linhas": linhas, "ic_pior": ic_pior, "decisao": decisao}


if __name__ == "__main__":
    executar()
