"""Piloto de desenvolvimento do experimento 7 (NÃO é o experimento).

Artefato de desenvolvimento, recuperado em 21/10/2026. As funções abaixo são as
do script usado no piloto original; foi acrescentada apenas a função
`executar`, que regrava os resultados por semente em JSON. Sementes
7000-7015: queimadas, nunca usadas em calibração ou teste.
Uso (a partir da raiz do repositório):
    python3 experimentos/07/desenvolvimento/piloto.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from experimentos.comum.legado import D, Mundo
from ranhuras import MemoriaDeRanhuras

SEEDS = range(7000, 7008)  # tabela de seis cenários


def gerar(seed, sigma_medio, het, forca=0.8, n_ctx=4, expo=3, nq=50):
    rng = np.random.default_rng(seed)
    mundo = Mundo(seed + 900_000)
    ns, na = 30, 20
    n = ns + na
    protos = [mundo.pessoa() for _ in range(n)]
    g = np.zeros((n_ctx, D))
    ef = np.zeros((n, n_ctx, D))
    for c in range(1, n_ctx):
        g[c] = rng.normal(0, 0.25, D)
        ef[:, c] = rng.normal(0, forca, (n, D))
    sig = sigma_medio * np.exp(rng.normal(-0.5 * het**2, het, n))

    def obs(p, c, k):
        return (protos[p] + g[c] + ef[p, c])[None] + rng.normal(0, sig[p], (k, D))

    X, y, c_ = [], [], []
    for p in range(ns):
        for c in range(n_ctx):
            x = obs(p, c, 5); X.append(x); y += [p] * 5; c_ += [c] * 5
    cf = n_ctx - 1
    for p in range(ns, n):
        x = obs(p, 0, 3); X.append(x); y += [p] * 3; c_ += [0] * 3
        if expo:
            x = obs(p, cf, expo); X.append(x); y += [p] * expo; c_ += [cf] * expo
    Xq = np.vstack([obs(p, cf, nq) for p in range(ns, n)])
    yq = np.repeat(np.arange(ns, n), nq)
    return np.vstack(X), np.array(y), np.array(c_), Xq, yq, n_ctx


def delta_global(X, y, c, n_ctx):
    d = np.zeros((n_ctx, D))
    for k in range(1, n_ctx):
        dif = []
        for i in np.unique(y):
            r, o = X[(y == i) & (c == 0)], X[(y == i) & (c == k)]
            if len(r) and len(o):
                dif.append(o.mean(0) - r.mean(0))
        d[k] = np.mean(dif, 0)
    return d


def d2(a, B):
    return np.maximum((a * a).sum(1)[:, None] + (B * B).sum(1)[None] - 2 * a @ B.T, 0)


def ncm_global(X, y, c, Xq, n_ctx):
    d = delta_global(X, y, c, n_ctx)
    Z, Zq = X - d[c], Xq - d[n_ctx - 1]
    cl = np.unique(y)
    C = np.vstack([Z[y == k].mean(0) for k in cl])
    return cl[d2(Zq, C).argmin(1)]


def centro_ctx(X, y, c, Xq, n_ctx, lam=0.5):
    d = delta_global(X, y, c, n_ctx)
    cl = np.unique(y); cf = n_ctx - 1; C = []
    for k in cl:
        base = X[(y == k) & (c == 0)].mean(0) + d[cf]
        loc = X[(y == k) & (c == cf)]
        C.append((1 - lam) * base + lam * loc.mean(0) if len(loc) else base)
    return cl[d2(Xq, np.vstack(C)).argmin(1)]


def knn(X, y, c, Xq, n_ctx):
    d = delta_global(X, y, c, n_ctx)
    m = KNeighborsClassifier(5, weights="distance").fit(X - d[c], y)
    return m.predict(Xq - d[n_ctx - 1])


def camaras(X, y, c, Xq, n_ctx, w0, largura=True):
    m = MemoriaDeRanhuras(w0=w0, eta_min=0.02, aprende_deslocamento=True,
                          largura_adaptativa=largura)
    for x, i, k in zip(X, y, c):
        m.aprender(x, ctx=int(k), rotulo=int(i))
    return np.asarray(m.prever(Xq, ctx=n_ctx - 1)[0], int)


def qda_iso(X, y, c, Xq, n_ctx, lam=0.5):
    """Referência de mecanismo: centro como centro_ctx + variância por identidade."""
    d = delta_global(X, y, c, n_ctx)
    cl = np.unique(y); cf = n_ctx - 1; C, V = [], []
    for k in cl:
        base = X[(y == k) & (c == 0)].mean(0) + d[cf]
        loc = X[(y == k) & (c == cf)]
        C.append((1 - lam) * base + lam * loc.mean(0) if len(loc) else base)
        ss, df = 0.0, 0
        for cc in np.unique(c[y == k]):
            z = X[(y == k) & (c == cc)]
            if len(z) > 1:
                ss += ((z - z.mean(0)) ** 2).sum(); df += (len(z) - 1) * D
        V.append(max(ss / df, 1e-3))
    C, V = np.vstack(C), np.array(V)
    score = d2(Xq, C) / (2 * V[None]) + 0.5 * D * np.log(V)[None]
    return cl[score.argmin(1)]



METODOS6 = ("ncm_global", "centro_ctx(.5)", "knn5", "camaras",
            "camaras_sem_largura", "qda_iso(ref)")


def por_semente(sigma_medio, het, sementes, metodos, w0_camaras=None):
    """Acurácia por semente de cada método numa célula do piloto."""
    saida = {m: [] for m in metodos}
    for s in sementes:
        X, y, c, Xq, yq, n_ctx = gerar(s, sigma_medio, het)
        w0 = 2 * sigma_medio ** 2 if w0_camaras is None else w0_camaras
        fns = {
            "ncm_global": lambda: ncm_global(X, y, c, Xq, n_ctx),
            "centro_ctx(.5)": lambda: centro_ctx(X, y, c, Xq, n_ctx),
            "knn5": lambda: knn(X, y, c, Xq, n_ctx),
            "camaras": lambda: camaras(X, y, c, Xq, n_ctx, w0),
            "camaras_sem_largura": lambda: camaras(X, y, c, Xq, n_ctx, w0, largura=False),
            "qda_iso(ref)": lambda: qda_iso(X, y, c, Xq, n_ctx),
        }
        for m in metodos:
            saida[m].append(float((fns[m]() == yq).mean()))
    return saida


def executar():
    from importlib import metadata
    from registro import ambiente_git
    res = {"natureza": "desenvolvimento; não é evidência confirmatória",
           "git": ambiente_git(),
           "ambiente": {"python": sys.version.split()[0],
                        "numpy": metadata.version("numpy"),
                        "scikit_learn": metadata.version("scikit-learn")},
           "parametros_fixos": {"contextos": 4, "exposicoes": 3, "forca": 0.8,
                                "w0_camaras": "2 * sigma_medio**2", "eta_min": 0.02},
           "tabela_seis_cenarios": [], "estatistica_dois_cenarios": [],
           "sensibilidade_w0": []}
    for sm in (0.8, 1.6, 2.4):
        for het in (0.35, 1.0):
            res["tabela_seis_cenarios"].append({
                "sigma_medio": sm, "heterogeneidade": het,
                "sementes": list(range(7000, 7008)),
                "acuracia_por_semente": por_semente(sm, het, range(7000, 7008), METODOS6)})
    for het in (1.0, 0.35):
        res["estatistica_dois_cenarios"].append({
            "sigma_medio": 1.6, "heterogeneidade": het,
            "sementes": list(range(7000, 7016)),
            "acuracia_por_semente": por_semente(
                1.6, het, range(7000, 7016),
                ("camaras", "ncm_global", "centro_ctx(.5)", "qda_iso(ref)"))})
    for het in (1.0, 0.35):
        for w0 in (0.08, 0.16, 0.32, 0.64, 1.28, 2.56, 5.12, 10.24, 20.48):
            res["sensibilidade_w0"].append({
                "sigma_medio": 1.6, "heterogeneidade": het, "w0": w0,
                "sementes": list(range(7000, 7016)),
                "acuracia_camaras_por_semente": por_semente(
                    1.6, het, range(7000, 7016), ("camaras",), w0_camaras=w0)["camaras"]})
    destino = Path(__file__).with_name("piloto-resultados.json")
    with destino.open("x", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    return res


if __name__ == "__main__":
    executar()
    print("gravado piloto-resultados.json")
