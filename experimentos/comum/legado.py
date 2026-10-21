"""
experimentos.py - testa o modelo de ranhuras contra baselines simples.

Uso:  python3 experimentos.py            (roda tudo, ~alguns minutos)
      python3 experimentos.py 1 3        (só os experimentos 1 e 3)

"Pessoas" sintéticas: cada uma é um espectro-protótipo de D bins (picos
gaussianos aleatórios, média zero, rms 1). Cada observação = protótipo
* ganho + deslocamento do contexto + ruído gaussiano.
"""
import sys
import warnings

import numpy as np
from sklearn.cluster import KMeans
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import adjusted_rand_score
from sklearn.neural_network import MLPClassifier

from ranhuras import MemoriaDeRanhuras

warnings.filterwarnings("ignore", category=ConvergenceWarning)

D = 64
SIGMA = 1.2          # ruído real nos exps 1,2,4,5 (difícil o bastante p/ 1 exemplo errar)
W0 = 2 * SIGMA ** 2  # prior de largura da ranhura = d2 esperado entre 2 ecos da mesma pessoa
SEEDS = 10


# ======================================================================
# Mundo sintético
# ======================================================================
class Mundo:
    def __init__(self, seed, sigma=SIGMA, forca_medo=0.8):
        self.rng = np.random.default_rng(seed)
        self.sigma = sigma
        f = np.arange(D)
        pad = np.zeros(D)                       # padrão do contexto "medo"
        for _ in range(4):
            pad += self.rng.uniform(-1, 1) * np.exp(
                -0.5 * ((f - self.rng.uniform(0, D)) / self.rng.uniform(3, 8)) ** 2)
        pad -= pad.mean()
        pad /= np.sqrt((pad ** 2).mean())
        self.desloc = {"calmo": np.zeros(D), "medo": forca_medo * pad}
        self.f = f

    def pessoa(self):
        p = np.zeros(D)
        for _ in range(self.rng.integers(6, 12)):
            p += self.rng.uniform(0.5, 1.5) * np.exp(
                -0.5 * ((self.f - self.rng.uniform(0, D))
                        / self.rng.uniform(0.8, 2.0)) ** 2)
        p -= p.mean()
        return p / np.sqrt((p ** 2).mean())

    def amostras(self, proto, n, ctx="calmo", sigma=None):
        s = self.sigma if sigma is None else sigma
        ganho = np.exp(self.rng.normal(0, 0.1, (n, 1)))
        return (proto[None] * ganho + self.desloc[ctx][None]
                + self.rng.normal(0, s, (n, D)))


def d2_mat(X, C):
    return np.maximum((X ** 2).sum(1)[:, None] + (C ** 2).sum(1)[None]
                      - 2 * X @ C.T, 0) / X.shape[1]


# ======================================================================
# Modelos (interface: aprender(X, y, ctx) / prever(X, ctx) / n_vetores())
# ======================================================================
class Ranhuras:
    def __init__(self, nome="ranhuras", usar_ctx=False, **kw):
        self.nome = nome
        self.usar_ctx = usar_ctx
        self.m = MemoriaDeRanhuras(**kw)

    def aprender(self, X, y, ctx=None):
        c = ctx if self.usar_ctx else None
        for xi, yi in zip(X, y):
            self.m.aprender(xi, ctx=c, rotulo=int(yi))

    def prever(self, X, ctx=None):
        c = ctx if self.usar_ctx else None
        return np.array(self.m.prever(X, ctx=c)[0])

    def n_vetores(self):
        return self.m.n_vetores()


class KNN1:
    nome = "kNN-1 (guarda tudo)"

    def __init__(self):
        self.X, self.y = [], []

    def aprender(self, X, y, ctx=None):
        self.X.append(np.asarray(X))
        self.y += list(y)

    def prever(self, X, ctx=None):
        return np.array(self.y)[d2_mat(X, np.vstack(self.X)).argmin(1)]

    def n_vetores(self):
        return len(self.y)


class NCM:
    nome = "centro da classe (NCM)"

    def __init__(self):
        self.soma, self.cont = {}, {}

    def aprender(self, X, y, ctx=None):
        for xi, yi in zip(X, y):
            self.soma[yi] = self.soma.get(yi, 0) + xi
            self.cont[yi] = self.cont.get(yi, 0) + 1

    def prever(self, X, ctx=None):
        ks = list(self.soma)
        C = np.array([self.soma[k] / self.cont[k] for k in ks])
        return np.array(ks)[d2_mat(X, C).argmin(1)]

    def n_vetores(self):
        return len(self.soma)


class MLPConjunto:
    """Retreina do zero com TUDO que já viu (precisa guardar os dados)."""
    nome = "MLP retreinado com tudo"

    def __init__(self, seed=0):
        self.X, self.y, self.seed, self.sujo, self.clf = [], [], seed, True, None

    def aprender(self, X, y, ctx=None):
        self.X.append(np.asarray(X))
        self.y += list(y)
        self.sujo = True

    def prever(self, X, ctx=None):
        if self.sujo:
            self.clf = MLPClassifier((64,), max_iter=400, random_state=self.seed)
            self.clf.fit(np.vstack(self.X), self.y)
            self.sujo = False
        return self.clf.predict(X)

    def n_vetores(self):
        return len(self.y)


class MLPIncremental:
    """Só vê o lote novo (sem guardar o passado): sofre esquecimento."""
    nome = "MLP incremental (só lote novo)"

    def __init__(self, classes, seed=0, epocas=40):
        self.clf = MLPClassifier((64,), random_state=seed)
        self.classes, self.epocas = np.array(classes), epocas

    def aprender(self, X, y, ctx=None):
        X, y = np.asarray(X), np.asarray(y)
        for _ in range(self.epocas):
            self.clf.partial_fit(X, y, classes=self.classes)

    def prever(self, X, ctx=None):
        return self.clf.predict(X)

    def n_vetores(self):
        return 0


def fmt(v):
    v = np.asarray(v, float)
    return f"{v.mean():.3f}±{v.std():.3f}"


def tabela(cab, linhas, larg0=34, larg=15):
    print(f"{cab[0]:<{larg0}}" + "".join(f"{c:>{larg}}" for c in cab[1:]))
    for l in linhas:
        print(f"{l[0]:<{larg0}}" + "".join(f"{c:>{larg}}" for c in l[1:]))


# ======================================================================
# Experimento 1 - aprender com poucos exemplos
# ======================================================================
def exp1():
    print("\n" + "=" * 78)
    print("EXPERIMENTO 1 - reconhecer pessoa após n exposições (40 pessoas, "
          f"ruído={SIGMA}, {SEEDS} sementes)")
    print("=" * 78)
    ns, N, T = [1, 2, 3, 5, 10], 40, 30
    nomes = ["ranhuras", "kNN-1 (guarda tudo)", "centro da classe (NCM)",
             "MLP retreinado com tudo"]
    res = {m: {n: [] for n in ns} for m in nomes}
    for seed in range(SEEDS):
        mundo = Mundo(seed)
        protos = [mundo.pessoa() for _ in range(N)]
        Xte = np.vstack([mundo.amostras(p, T) for p in protos])
        yte = np.repeat(np.arange(N), T)
        for n in ns:
            Xtr = np.vstack([mundo.amostras(p, n) for p in protos])
            ytr = np.repeat(np.arange(N), n)
            mods = {"ranhuras": Ranhuras(w0=W0), "kNN-1 (guarda tudo)": KNN1(),
                    "centro da classe (NCM)": NCM(),
                    "MLP retreinado com tudo": MLPConjunto(seed)}
            for nome, mod in mods.items():
                mod.aprender(Xtr, ytr)
                res[nome][n].append((mod.prever(Xte) == yte).mean())
    tabela(["acurácia por nº de exposições"] + [f"n={n}" for n in ns],
           [[m] + [fmt(res[m][n]) for n in ns] for m in nomes])
    return res


# ======================================================================
# Experimento 2 - aprender em etapas (esquecimento)
# ======================================================================
def exp2():
    S, P, n, T = 6, 8, 8, 20
    print("\n" + "=" * 78)
    print(f"EXPERIMENTO 2 - {S} etapas x {P} pessoas novas ({n} exposições cada); "
          f"{SEEDS} sementes")
    print("=" * 78)
    nomes = ["ranhuras", "kNN-1 (guarda tudo)", "centro da classe (NCM)",
             "MLP retreinado com tudo", "MLP incremental (só lote novo)"]
    geral = {m: [[] for _ in range(S)] for m in nomes}
    etapa1 = {m: [] for m in nomes}
    for seed in range(SEEDS):
        mundo = Mundo(100 + seed)
        protos = [mundo.pessoa() for _ in range(S * P)]
        mods = {"ranhuras": Ranhuras(w0=W0), "kNN-1 (guarda tudo)": KNN1(),
                "centro da classe (NCM)": NCM(),
                "MLP retreinado com tudo": MLPConjunto(seed),
                "MLP incremental (só lote novo)":
                    MLPIncremental(range(S * P), seed)}
        Xte_all = [mundo.amostras(p, T) for p in protos]
        for s in range(S):
            ids = list(range(s * P, (s + 1) * P))
            Xs = np.vstack([mundo.amostras(protos[i], n) for i in ids])
            ys = np.repeat(ids, n)
            vistos = list(range((s + 1) * P))
            Xte = np.vstack([Xte_all[i] for i in vistos])
            yte = np.repeat(vistos, T)
            for nome, mod in mods.items():
                mod.aprender(Xs, ys)
                geral[nome][s].append((mod.prever(Xte) == yte).mean())
        X0 = np.vstack(Xte_all[:P])
        y0 = np.repeat(np.arange(P), T)
        for nome, mod in mods.items():
            etapa1[nome].append((mod.prever(X0) == y0).mean())
    tabela(["acurácia em TODAS as pessoas já vistas"]
           + [f"após etapa {s + 1}" for s in range(S)],
           [[m] + [fmt(geral[m][s]) for s in range(S)] for m in nomes], larg=14)
    print()
    tabela(["retenção: pessoas da etapa 1, no fim", "acurácia"],
           [[m, fmt(etapa1[m])] for m in nomes])
    return geral, etapa1


# ======================================================================
# Experimento 3 - descobrir pessoas sem rótulo (brotar) + ablação
# ======================================================================
def fluxo_sem_rotulo(seed, sigma, N=20, m=15):
    mundo = Mundo(200 + seed, sigma=sigma)
    protos = [mundo.pessoa() for _ in range(N)]
    X = np.vstack([mundo.amostras(p, m) for p in protos])
    y = np.repeat(np.arange(N), m)
    ordem = mundo.rng.permutation(len(y))
    return X[ordem], y[ordem], N


def roda_descoberta(X, y, **kw):
    mem = MemoriaDeRanhuras(**kw)
    ids = [mem.aprender(x) for x in X]
    return adjusted_rand_score(y, ids), mem.n_ranhuras()


def exp3():
    print("\n" + "=" * 78)
    print("EXPERIMENTO 3 - descobrir pessoas SEM rótulos (20 pessoas reais, 15 "
          "observações\n   embaralhadas cada). Ideal: 20 ranhuras e ARI=1. "
          f"Prior de largura fixo w0=0.32; {SEEDS} sementes")
    print("=" * 78)
    variantes = {
        "completo (erosão + largura)": dict(erosao=True, largura_adaptativa=True),
        "só o centro erode": dict(erosao=True, largura_adaptativa=False),
        "sem erosão (leader clustering)": dict(erosao=False, largura_adaptativa=False),
    }
    sigmas = [0.3, 0.4, 0.5]
    print("\n(a) variantes x ruído real   [ARI / nº de ranhuras]   z_max=2.0")
    linhas = []
    for nome, kw in variantes.items():
        lin = [nome]
        for sg in sigmas:
            ari, nr = [], []
            for seed in range(SEEDS):
                X, y, N = fluxo_sem_rotulo(seed, sg)
                a, k = roda_descoberta(X, y, w0=0.32, z_max=2.0, **kw)
                ari.append(a); nr.append(k)
            lin.append(f"{np.mean(ari):.2f} / {np.mean(nr):.0f}")
        linhas.append(lin)
    ref = ["k-means (K=20 dado de graça)"]
    for sg in sigmas:
        ari = []
        for seed in range(SEEDS):
            X, y, N = fluxo_sem_rotulo(seed, sg)
            ari.append(adjusted_rand_score(
                y, KMeans(N, n_init=5, random_state=seed).fit_predict(X)))
        ref.append(f"{np.mean(ari):.2f} / 20")
    linhas.append(ref)
    tabela(["variante"] + [f"σ={s}" for s in sigmas], linhas, larg=16)

    print("\n(b) sensibilidade ao limiar z_max (modelo completo, σ=0.4)")
    linhas = []
    for zm in [1.0, 1.5, 2.0, 3.0, 5.0, 8.0]:
        ari, nr = [], []
        for seed in range(SEEDS):
            X, y, N = fluxo_sem_rotulo(seed, 0.4)
            a, k = roda_descoberta(X, y, w0=0.32, z_max=zm)
            ari.append(a); nr.append(k)
        linhas.append([f"z_max={zm}", f"{np.mean(ari):.2f}", f"{np.mean(nr):.1f}"])
    tabela(["limiar", "ARI", "nº ranhuras"], linhas, larg0=14, larg=14)

    print("\n(c) sensibilidade ao prior de largura w0 (σ=0.4, z_max=2.0): a largura"
          "\n    adaptativa conserta um prior errado?   [ARI / nº de ranhuras]")
    linhas = []
    for w0 in [0.08, 0.16, 0.32, 0.64, 1.28]:
        lin = [f"w0={w0}"]
        for kw in (dict(largura_adaptativa=True), dict(largura_adaptativa=False)):
            ari, nr = [], []
            for seed in range(SEEDS):
                X, y, N = fluxo_sem_rotulo(seed, 0.4)
                a, k = roda_descoberta(X, y, w0=w0, z_max=2.0, **kw)
                ari.append(a); nr.append(k)
            lin.append(f"{np.mean(ari):.2f} / {np.mean(nr):.0f}")
        linhas.append(lin)
    tabela(["prior", "com largura adapt.", "largura fixa"], linhas, larg0=14, larg=20)


# ======================================================================
# Experimento 4 - contexto: câmaras e deslocamento de tom
# ======================================================================
class KNN1Desloc:
    """kNN com o mesmo truque: aprende o deslocamento do contexto."""
    nome = "kNN-1 + deslocamento (mesmo truque)"

    def __init__(self):
        self.X, self.y, self.c = [], [], []

    def aprender(self, X, y, ctx=None):
        self.X.append(np.asarray(X)); self.y += list(y); self.c += [ctx] * len(y)

    def _delta(self):
        X, y, c = np.vstack(self.X), np.array(self.y), np.array(self.c)
        difs = []
        for p in set(y):
            a = X[(y == p) & (c == "calmo")]
            b = X[(y == p) & (c == "medo")]
            if len(a) and len(b):
                difs.append(b.mean(0) - a.mean(0))
        return np.mean(difs, axis=0) if difs else np.zeros(D)

    def prever(self, X, ctx=None):
        d = self._delta()
        desloc = np.array([d if c == "medo" else np.zeros(D) for c in self.c])
        A = np.vstack(self.X) - desloc
        Xq = X - (d if ctx == "medo" else 0)
        return np.array(self.y)[d2_mat(Xq, A).argmin(1)]

    def n_vetores(self):
        return len(self.y)


class NCMDesloc(KNN1Desloc):
    """Centro da classe + o mesmo deslocamento (o análogo justo das ranhuras)."""
    nome = "NCM + deslocamento (mesmo truque)"

    def prever(self, X, ctx=None):
        d = self._delta()
        desloc = np.array([d if c == "medo" else np.zeros(D) for c in self.c])
        A, y = np.vstack(self.X) - desloc, np.array(self.y)
        ks = sorted(set(y))
        C = np.array([A[y == k].mean(0) for k in ks])
        Xq = X - (d if ctx == "medo" else 0)
        return np.array(ks)[d2_mat(Xq, C).argmin(1)]

    def n_vetores(self):
        return len(set(self.y))


def exp4():
    K, M, nk, nn, T = 30, 20, 5, 3, 30
    print("\n" + "=" * 78)
    print(f"EXPERIMENTO 4 - contexto. {K} pessoas conhecidas vistas {nk}x em "
          f"'calmo' e {nk}x em 'medo';\n   {M} pessoas novas vistas {nn}x só em "
          f"'calmo'. Teste: as novas em 'medo'. {SEEDS} sementes")
    print("=" * 78)
    nomes = ["ranhura plana (ignora contexto)", "ranhura + câmaras",
             "ranhura + câmaras + deslocamento", "kNN-1 (guarda tudo)",
             "kNN-1 + deslocamento (mesmo truque)", "centro da classe (NCM)",
             "NCM + deslocamento (mesmo truque)"]
    r_novas, r_conh, mem = ({m: [] for m in nomes} for _ in range(3))
    for seed in range(SEEDS):
        mundo = Mundo(300 + seed)
        protos = [mundo.pessoa() for _ in range(K + M)]
        mods = {
            nomes[0]: Ranhuras(w0=W0, usar_ctx=False),
            nomes[1]: Ranhuras(w0=W0, usar_ctx=True),
            nomes[2]: Ranhuras(w0=W0, usar_ctx=True, aprende_deslocamento=True),
            nomes[3]: KNN1(), nomes[4]: KNN1Desloc(), nomes[5]: NCM(),
            nomes[6]: NCMDesloc()}
        for ctx in ["calmo", "medo"]:                    # conhecidas: ambos
            for i in range(K):
                X = mundo.amostras(protos[i], nk, ctx)
                for mod in mods.values():
                    mod.aprender(X, [i] * nk, ctx=ctx)
        for i in range(K, K + M):                        # novas: só calmo
            X = mundo.amostras(protos[i], nn, "calmo")
            for mod in mods.values():
                mod.aprender(X, [i] * nn, ctx="calmo")
        Xn = np.vstack([mundo.amostras(protos[i], T, "medo") for i in range(K, K + M)])
        yn = np.repeat(np.arange(K, K + M), T)
        Xc = np.vstack([mundo.amostras(protos[i], T, c) for c in ["calmo", "medo"]
                        for i in range(K)])
        yc = np.tile(np.repeat(np.arange(K), T), 2)
        cc = ["calmo"] * (K * T) + ["medo"] * (K * T)
        for nome, mod in mods.items():
            r_novas[nome].append((mod.prever(Xn, ctx="medo") == yn).mean())
            ac = [(mod.prever(Xc[j * K * T:(j + 1) * K * T], ctx=c)
                   == yc[j * K * T:(j + 1) * K * T]).mean()
                  for j, c in enumerate(["calmo", "medo"])]
            r_conh[nome].append(np.mean(ac))
            mem[nome].append(mod.n_vetores())
    tabela(["modelo", "novas em 'medo'", "conhecidas", "vetores guardados"],
           [[m, fmt(r_novas[m]), fmt(r_conh[m]), f"{np.mean(mem[m]):.0f}"]
            for m in nomes], larg0=38, larg=18)
    print("\nObs.: o deslocamento de contexto é aditivo e global NESTE gerador;"
          " isso favorece\nqualquer método que modele esse deslocamento "
          "(inclusive o kNN com o mesmo truque).")


# ======================================================================
# Experimento 5 - esquecimento elástico com orçamento de memória
# ======================================================================
def exp5():
    N, L = 60, 3000
    print("\n" + "=" * 78)
    print(f"EXPERIMENTO 5 - memória com orçamento: {N} pessoas, fluxo de {L} "
          "observações com\n   popularidade Zipf; na metade a popularidade "
          f"muda. Acurácia em quem JÁ foi visto. {SEEDS} sementes")
    print("=" * 78)
    budgets = [10, 20, 30]
    pols = ["murchar", "lru", "lfu", "fifo", "aleatorio"]
    res = {(p, b): [] for p in pols for b in budgets}
    teto = []
    for seed in range(SEEDS):
        mundo = Mundo(400 + seed)
        protos = [mundo.pessoa() for _ in range(N)]
        rng = np.random.default_rng(500 + seed)
        zipf = 1.0 / (np.arange(N) + 1) ** 1.1
        zipf /= zipf.sum()
        pa, pb = np.empty(N), np.empty(N)
        pa[rng.permutation(N)] = zipf
        pb[rng.permutation(N)] = zipf
        ys = np.concatenate([rng.choice(N, L // 2, p=pa),
                             rng.choice(N, L - L // 2, p=pb)])
        Xs = np.vstack([mundo.amostras(protos[y], 1) for y in ys])

        def roda(**kw):
            mem = MemoriaDeRanhuras(w0=W0, **kw)
            vistos, ac = set(), []
            for x, y in zip(Xs, ys):
                if y in vistos:
                    ac.append(mem.prever(x)[0][0] == y)
                mem.aprender(x, rotulo=int(y))
                vistos.add(y)
            return np.mean(ac)
        teto.append(roda())
        for b in budgets:
            for p in pols:
                res[(p, b)].append(roda(max_ranhuras=b, politica=p, tau=300.0,
                                        seed=seed))
    tabela(["política de esquecimento"] + [f"orçamento={b}" for b in budgets],
           [[{"murchar": "murchar (força decai c/ o tempo)",
              "lru": "LRU (menos recente)", "lfu": "LFU (menos frequente)",
              "fifo": "FIFO", "aleatorio": "aleatório"}[p]]
            + [fmt(res[(p, b)]) for b in budgets] for p in pols], larg0=36)
    print(f"\nteto (memória ilimitada, 60 ranhuras): {fmt(teto)}")


# ======================================================================
if __name__ == "__main__":
    todos = {"1": exp1, "2": exp2, "3": exp3, "4": exp4, "5": exp5}
    escolha = sys.argv[1:] or list(todos)
    for k in escolha:
        todos[k]()
