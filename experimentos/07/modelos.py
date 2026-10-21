"""Gerador, métodos e buscas definidos no pré-registro do experimento 7."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.naive_bayes import GaussianNB
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
    n_contextos: int


def gerar_dados(semente: int, *, sigma_medio: float, heterogeneidade: float,
                n_contextos: int = 4, exposicoes: int = 3,
                forca: float = 0.8, consultas_por_identidade: int = 50) -> Dados:
    """Gera um episódio; cada identidade mantém seu próprio desvio de ruído."""
    if sigma_medio <= 0 or heterogeneidade < 0:
        raise ValueError("sigma_medio deve ser positivo e heterogeneidade não negativa")
    if n_contextos < 2 or exposicoes < 0 or forca < 0:
        raise ValueError("contextos, exposições ou força fora do domínio")
    if consultas_por_identidade < 1:
        raise ValueError("é necessária ao menos uma consulta por identidade")

    rng = np.random.default_rng(semente)
    mundo = Mundo(semente + 800_000)
    n_suporte, n_alvo, por_contexto = 30, 20, 5
    n_pessoas = n_suporte + n_alvo
    prototipos = [mundo.pessoa() for _ in range(n_pessoas)]
    deslocamento = np.zeros((n_contextos, D))
    efeito_pessoa = np.zeros((n_pessoas, n_contextos, D))
    for contexto in range(1, n_contextos):
        deslocamento[contexto] = rng.normal(0, 0.25, D)
        efeito_pessoa[:, contexto] = rng.normal(0, forca, (n_pessoas, D))
    sigma = sigma_medio * np.exp(
        rng.normal(-heterogeneidade**2 / 2, heterogeneidade, n_pessoas)
    )

    xs: list[np.ndarray] = []
    ys: list[int] = []
    cs: list[int] = []

    def observar(identidade: int, contexto: int, n: int) -> np.ndarray:
        centro = (prototipos[identidade] + deslocamento[contexto]
                 + efeito_pessoa[identidade, contexto])
        return centro[None, :] + rng.normal(0, sigma[identidade], (n, D))

    for identidade in range(n_suporte):
        for contexto in range(n_contextos):
            amostras = observar(identidade, contexto, por_contexto)
            xs.append(amostras)
            ys.extend([identidade] * len(amostras))
            cs.extend([contexto] * len(amostras))

    contexto_final = n_contextos - 1
    for identidade in range(n_suporte, n_pessoas):
        referencia = observar(identidade, 0, 3)
        xs.append(referencia)
        ys.extend([identidade] * len(referencia))
        cs.extend([0] * len(referencia))
        if exposicoes:
            locais = observar(identidade, contexto_final, exposicoes)
            xs.append(locais)
            ys.extend([identidade] * len(locais))
            cs.extend([contexto_final] * len(locais))

    xq, yq = [], []
    for identidade in range(n_suporte, n_pessoas):
        consultas = observar(identidade, contexto_final, consultas_por_identidade)
        xq.append(consultas)
        yq.extend([identidade] * len(consultas))

    return Dados(
        x_treino=np.vstack(xs), y_treino=np.asarray(ys, dtype=int),
        c_treino=np.asarray(cs, dtype=int), x_teste=np.vstack(xq),
        y_teste=np.asarray(yq, dtype=int), n_contextos=n_contextos,
    )


def deslocamentos_globais(dados: Dados) -> np.ndarray:
    """Deslocamentos médios estimados apenas com identidades e amostras de treino."""
    deslocamentos = np.zeros((dados.n_contextos, D))
    for contexto in range(1, dados.n_contextos):
        diferencas = []
        for identidade in np.unique(dados.y_treino):
            referencia = dados.x_treino[(dados.y_treino == identidade)
                                        & (dados.c_treino == 0)]
            local = dados.x_treino[(dados.y_treino == identidade)
                                   & (dados.c_treino == contexto)]
            if len(referencia) and len(local):
                diferencas.append(local.mean(axis=0) - referencia.mean(axis=0))
        if diferencas:
            deslocamentos[contexto] = np.mean(diferencas, axis=0)
    return deslocamentos


def distancias_quadradas(x: np.ndarray, centros: np.ndarray) -> np.ndarray:
    return np.maximum(
        (x * x).sum(axis=1)[:, None] + (centros * centros).sum(axis=1)[None, :]
        - 2 * x @ centros.T,
        0.0,
    )


def _corrigir_contexto(dados: Dados) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    delta = deslocamentos_globais(dados)
    x = dados.x_treino - delta[dados.c_treino]
    xq = dados.x_teste - delta[dados.n_contextos - 1]
    return x, xq, delta


def prever_camaras(dados: Dados, config: dict, *, largura_adaptativa: bool = True,
                   deslocamento_interno: bool = True) -> np.ndarray:
    memoria = MemoriaDeRanhuras(
        w0=float(config["w0"]), eta_min=float(config["eta_min"]),
        aprende_deslocamento=deslocamento_interno,
        largura_adaptativa=largura_adaptativa,
    )
    for x, identidade, contexto in zip(
            dados.x_treino, dados.y_treino, dados.c_treino):
        memoria.aprender(x, ctx=int(contexto), rotulo=int(identidade))
    return np.asarray(
        memoria.prever(dados.x_teste, ctx=dados.n_contextos - 1)[0], dtype=int
    )


def prever_camaras_sem_contextos(dados: Dados, config: dict) -> np.ndarray:
    """Uma câmara por identidade após correção global estimada só no treino."""
    x, xq, _ = _corrigir_contexto(dados)
    memoria = MemoriaDeRanhuras(
        w0=float(config["w0"]), eta_min=float(config["eta_min"]),
        aprende_deslocamento=False,
    )
    for observacao, identidade in zip(x, dados.y_treino):
        memoria.aprender(observacao, ctx=0, rotulo=int(identidade))
    return np.asarray(memoria.prever(xq, ctx=0)[0], dtype=int)


def prever_ncm(dados: Dados, *, deslocamento_global: bool) -> np.ndarray:
    x, xq = dados.x_treino, dados.x_teste
    if deslocamento_global:
        x, xq, _ = _corrigir_contexto(dados)
    classes = np.unique(dados.y_treino)
    centros = np.vstack([x[dados.y_treino == classe].mean(axis=0)
                         for classe in classes])
    return classes[distancias_quadradas(xq, centros).argmin(axis=1)]


def prever_knn(dados: Dados, config: dict) -> np.ndarray:
    x, xq, _ = _corrigir_contexto(dados)
    modelo = KNeighborsClassifier(
        n_neighbors=int(config["k"]), weights=str(config["pesos"])
    ).fit(x, dados.y_treino)
    return modelo.predict(xq)


def prever_centro_contexto(dados: Dados, config: dict) -> np.ndarray:
    delta = deslocamentos_globais(dados)
    classes = np.unique(dados.y_treino)
    contexto_final = dados.n_contextos - 1
    lam = float(config["lambda"])
    centros = []
    for classe in classes:
        ref = dados.x_treino[(dados.y_treino == classe)
                             & (dados.c_treino == 0)]
        local = dados.x_treino[(dados.y_treino == classe)
                               & (dados.c_treino == contexto_final)]
        base = ref.mean(axis=0) + delta[contexto_final]
        centro = (1 - lam) * base + lam * local.mean(axis=0) if len(local) else base
        centros.append(centro)
    return classes[distancias_quadradas(dados.x_teste, np.vstack(centros)).argmin(1)]


def prever_mlp(dados: Dados, config: dict, *, semente: int) -> np.ndarray:
    codigos = np.eye(dados.n_contextos)[dados.c_treino]
    x = np.column_stack([dados.x_treino, codigos])
    contexto_consulta = np.zeros((len(dados.x_teste), dados.n_contextos))
    contexto_consulta[:, -1] = 1
    xq = np.column_stack([dados.x_teste, contexto_consulta])
    modelo = MLPClassifier(
        hidden_layer_sizes=(int(config["hidden"]),),
        alpha=float(config["alpha"]), learning_rate_init=0.001,
        max_iter=200, early_stopping=True, n_iter_no_change=10,
        random_state=int(semente),
    ).fit(x, dados.y_treino)
    return modelo.predict(xq)


def prever_gaussian_nb(dados: Dados, config: dict) -> np.ndarray:
    x, xq, _ = _corrigir_contexto(dados)
    classes = np.unique(dados.y_treino)
    priors = np.full(len(classes), 1.0 / len(classes))
    modelo = GaussianNB(
        priors=priors, var_smoothing=float(config["var_smoothing"])
    ).fit(x, dados.y_treino)
    return modelo.predict(xq)


def _estatisticas_residuais(dados: Dados) -> tuple[dict[int, tuple[float, int]], float]:
    por_identidade: dict[int, tuple[float, int]] = {}
    ss_global, gl_global = 0.0, 0
    for identidade in np.unique(dados.y_treino):
        ss_i, gl_i = 0.0, 0
        for contexto in np.unique(dados.c_treino[dados.y_treino == identidade]):
            grupo = dados.x_treino[(dados.y_treino == identidade)
                                   & (dados.c_treino == contexto)]
            if len(grupo) > 1:
                residuos = grupo - grupo.mean(axis=0)
                ss_i += float(np.square(residuos).sum())
                gl_i += (len(grupo) - 1) * D
        por_identidade[int(identidade)] = (ss_i, gl_i)
        ss_global += ss_i
        gl_global += gl_i
    if gl_global == 0:
        raise ValueError("não há graus de liberdade para estimar variância residual")
    return por_identidade, ss_global / gl_global


def prever_variancia_identidade(dados: Dados, config: dict) -> np.ndarray:
    """Centro com retração e escore Gaussiano isotrópico por identidade."""
    delta = deslocamentos_globais(dados)
    classes = np.unique(dados.y_treino)
    contexto_final = dados.n_contextos - 1
    lam, kappa = float(config["lambda"]), float(config["kappa"])
    estatisticas, v_global = _estatisticas_residuais(dados)
    centros, variancias = [], []
    for classe in classes:
        ref = dados.x_treino[(dados.y_treino == classe)
                             & (dados.c_treino == 0)]
        local = dados.x_treino[(dados.y_treino == classe)
                               & (dados.c_treino == contexto_final)]
        base = ref.mean(axis=0) + delta[contexto_final]
        centro = (1 - lam) * base + lam * local.mean(axis=0) if len(local) else base
        ss_i, gl_i = estatisticas[int(classe)]
        v_i = ss_i / gl_i if gl_i else v_global
        v_retraida = max((1 - kappa) * v_i + kappa * v_global, 1e-12)
        centros.append(centro)
        variancias.append(v_retraida)
    centros = np.vstack(centros)
    variancias = np.asarray(variancias)
    scores = (D * np.log(variancias)[None, :]
              + distancias_quadradas(dados.x_teste, centros) / variancias[None, :])
    return classes[scores.argmin(axis=1)]


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
            {"lambda": float(lam)} for lam in np.linspace(0, 1, 20)
        ],
        "mlp": [
            {"hidden": hidden, "alpha": alpha}
            for hidden in (32, 64, 128, 256, 512)
            for alpha in (1e-5, 1e-4, 1e-3, 1e-2)
        ],
        "gaussian_nb": [
            {"var_smoothing": float(valor)}
            for valor in np.geomspace(1e-12, 1e-1, 20)
        ],
        "variancia_identidade": [
            {"lambda": float(lam), "kappa": float(kappa)}
            for lam in (0.0, 0.25, 0.5, 0.75, 1.0)
            for kappa in (0.0, 1 / 3, 2 / 3, 1.0)
        ],
    }


def prever(dados: Dados, familia: str, config: dict, *, semente: int) -> np.ndarray:
    if familia == "camaras":
        return prever_camaras(dados, config)
    if familia == "ncm":
        return prever_ncm(dados, deslocamento_global=False)
    if familia == "ncm_global":
        return prever_ncm(dados, deslocamento_global=True)
    if familia == "knn":
        return prever_knn(dados, config)
    if familia == "centro_contexto":
        return prever_centro_contexto(dados, config)
    if familia == "mlp":
        return prever_mlp(dados, config, semente=semente)
    if familia == "gaussian_nb":
        return prever_gaussian_nb(dados, config)
    if familia == "variancia_identidade":
        return prever_variancia_identidade(dados, config)
    raise ValueError(f"família desconhecida: {familia}")


def acuracia(dados: Dados, familia: str, config: dict, *, semente: int) -> float:
    predicoes = prever(dados, familia, config, semente=semente)
    return float(np.mean(predicoes == dados.y_teste))
