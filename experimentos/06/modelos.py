"""Gerador e baselines congelados para o experimento 6."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

from experimentos.comum.legado import D, Mundo
from ranhuras import MemoriaDeRanhuras


@dataclass
class Dados:
    x_treino: np.ndarray
    y_treino: np.ndarray
    c_treino: np.ndarray
    x_teste: np.ndarray
    y_teste: np.ndarray
    rotulo_alvo: np.ndarray
    n_contextos: int


def gerar_dados(semente: int, n_contextos: int, exposicoes: int,
                forca: float, consultas_por_pessoa: int = 50) -> Dados:
    """Gera um episódio com contexto global e efeito pessoal não aditivo."""
    if n_contextos < 2 or exposicoes < 0:
        raise ValueError("são necessários ≥2 contextos e exposições não negativas")
    rng = np.random.default_rng(semente)
    mundo = Mundo(semente + 800_000)
    n_suporte, n_alvo, por_contexto = 30, 20, 5
    n_pessoas = n_suporte + n_alvo
    protos = [mundo.pessoa() for _ in range(n_pessoas)]
    global_ctx = np.zeros((n_contextos, D))
    efeito_pessoa = np.zeros((n_pessoas, n_contextos, D))
    for ctx in range(1, n_contextos):
        global_ctx[ctx] = rng.normal(0, 0.25, D)
        efeito_pessoa[:, ctx] = rng.normal(0, forca, (n_pessoas, D))
    sigma_p = 0.8 * np.exp(rng.normal(-0.5 * 0.35**2, 0.35, n_pessoas))

    xs, ys, cs = [], [], []

    def observa(pessoa: int, contexto: int, n: int) -> np.ndarray:
        centro = protos[pessoa] + global_ctx[contexto] + efeito_pessoa[pessoa, contexto]
        return centro[None, :] + rng.normal(0, sigma_p[pessoa], (n, D))

    for pessoa in range(n_suporte):
        for contexto in range(n_contextos):
            x = observa(pessoa, contexto, por_contexto)
            xs.append(x)
            ys.extend([pessoa] * len(x))
            cs.extend([contexto] * len(x))

    contexto_teste = n_contextos - 1
    for pessoa in range(n_suporte, n_pessoas):
        x_ref = observa(pessoa, 0, 3)
        xs.append(x_ref)
        ys.extend([pessoa] * len(x_ref))
        cs.extend([0] * len(x_ref))
        if exposicoes:
            x_ctx = observa(pessoa, contexto_teste, exposicoes)
            xs.append(x_ctx)
            ys.extend([pessoa] * len(x_ctx))
            cs.extend([contexto_teste] * len(x_ctx))

    xq, yq = [], []
    for pessoa in range(n_suporte, n_pessoas):
        q = observa(pessoa, contexto_teste, consultas_por_pessoa)
        xq.append(q)
        yq.extend([pessoa] * len(q))
    return Dados(
        np.vstack(xs), np.asarray(ys, int), np.asarray(cs, int),
        np.vstack(xq), np.asarray(yq, int),
        np.arange(n_suporte, n_pessoas), n_contextos,
    )


def deslocamentos_globais(dados: Dados) -> np.ndarray:
    """Média do deslocamento de cada contexto entre identidades observadas."""
    delta = np.zeros((dados.n_contextos, D))
    for ctx in range(1, dados.n_contextos):
        diferencas = []
        for identidade in np.unique(dados.y_treino):
            ref = dados.x_treino[(dados.y_treino == identidade)
                                 & (dados.c_treino == 0)]
            observado = dados.x_treino[(dados.y_treino == identidade)
                                       & (dados.c_treino == ctx)]
            if len(ref) and len(observado):
                diferencas.append(observado.mean(axis=0) - ref.mean(axis=0))
        if diferencas:
            delta[ctx] = np.mean(diferencas, axis=0)
    return delta


def _distancias(x: np.ndarray, centros: np.ndarray) -> np.ndarray:
    return np.maximum(
        (x * x).sum(axis=1)[:, None] + (centros * centros).sum(axis=1)[None, :]
        - 2 * x @ centros.T, 0.0,
    )


def prever_ranhuras(dados: Dados, config: dict) -> np.ndarray:
    memoria = MemoriaDeRanhuras(
        w0=float(config["w0"]), eta_min=float(config["eta_min"]),
        aprende_deslocamento=True,
    )
    for x, identidade, contexto in zip(dados.x_treino, dados.y_treino,
                                       dados.c_treino):
        memoria.aprender(x, ctx=int(contexto), rotulo=int(identidade))
    return np.asarray(memoria.prever(dados.x_teste,
                                     ctx=dados.n_contextos - 1)[0], int)


def prever_ncm(dados: Dados, *, global_ctx: bool) -> np.ndarray:
    x = dados.x_treino.copy()
    xq = dados.x_teste.copy()
    if global_ctx:
        delta = deslocamentos_globais(dados)
        x -= delta[dados.c_treino]
        xq -= delta[dados.n_contextos - 1]
    classes = np.unique(dados.y_treino)
    centros = np.vstack([x[dados.y_treino == classe].mean(axis=0)
                         for classe in classes])
    return classes[_distancias(xq, centros).argmin(axis=1)]


def prever_knn(dados: Dados, config: dict) -> np.ndarray:
    delta = deslocamentos_globais(dados)
    x = dados.x_treino - delta[dados.c_treino]
    xq = dados.x_teste - delta[dados.n_contextos - 1]
    modelo = KNeighborsClassifier(
        n_neighbors=int(config["k"]), weights=config["pesos"],
    ).fit(x, dados.y_treino)
    return modelo.predict(xq)


def prever_centro_contexto(dados: Dados, config: dict) -> np.ndarray:
    delta = deslocamentos_globais(dados)
    classes = np.unique(dados.y_treino)
    contexto = dados.n_contextos - 1
    lam = float(config["retracao"])
    centros = []
    for classe in classes:
        ref = dados.x_treino[(dados.y_treino == classe)
                             & (dados.c_treino == 0)]
        local = dados.x_treino[(dados.y_treino == classe)
                               & (dados.c_treino == contexto)]
        base = ref.mean(axis=0) + delta[contexto]
        centro = (1 - lam) * base + lam * local.mean(axis=0) if len(local) else base
        centros.append(centro)
    return classes[_distancias(dados.x_teste, np.vstack(centros)).argmin(axis=1)]


def prever_mlp(dados: Dados, config: dict, *, semente: int) -> np.ndarray:
    codigos = np.eye(dados.n_contextos)[dados.c_treino]
    x = np.column_stack([dados.x_treino, codigos])
    contexto_teste = np.zeros((len(dados.x_teste), dados.n_contextos))
    contexto_teste[:, -1] = 1
    xq = np.column_stack([dados.x_teste, contexto_teste])
    modelo = MLPClassifier(
        hidden_layer_sizes=(int(config["hidden"]),),
        alpha=float(config["alpha"]), learning_rate_init=0.001,
        max_iter=200, early_stopping=True, n_iter_no_change=10,
        random_state=semente,
    ).fit(x, dados.y_treino)
    return modelo.predict(xq)


def configuracoes() -> dict[str, list[dict]]:
    return {
        "camaras": [
            {"w0": w0, "eta_min": eta}
            for w0 in (0.08, 0.16, 0.32, 0.64, 1.28)
            for eta in (0.01, 0.02, 0.05, 0.10)
        ],
        "knn": [
            {"k": k, "pesos": peso}
            for k in (1, 3, 5, 7, 9, 11, 13, 15, 17, 19)
            for peso in ("uniform", "distance")
        ],
        "centro_contexto": [
            {"retracao": float(lam)} for lam in np.linspace(0, 1, 20)
        ],
        "mlp": [
            {"hidden": hidden, "alpha": alpha}
            for hidden in (32, 64, 128, 256, 512)
            for alpha in (1e-5, 1e-4, 1e-3, 1e-2)
        ],
    }


def prever_familia(dados: Dados, familia: str, config: dict,
                   *, semente: int) -> np.ndarray:
    if familia == "camaras":
        return prever_ranhuras(dados, config)
    if familia == "ncm":
        return prever_ncm(dados, global_ctx=False)
    if familia == "ncm_global":
        return prever_ncm(dados, global_ctx=True)
    if familia == "knn":
        return prever_knn(dados, config)
    if familia == "centro_contexto":
        return prever_centro_contexto(dados, config)
    if familia == "mlp":
        return prever_mlp(dados, config, semente=semente)
    raise ValueError(f"família desconhecida: {familia}")


def acuracia(dados: Dados, familia: str, config: dict,
             *, semente: int) -> float:
    pred = prever_familia(dados, familia, config, semente=semente)
    return float(np.mean(pred == dados.y_teste))
