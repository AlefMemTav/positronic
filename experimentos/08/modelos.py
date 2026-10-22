"""Gerador e métodos do experimento 8, conforme o pré-registro."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np

from experimentos.comum.legado import Mundo
from ranhuras import Camara, MemoriaDeRanhuras, Ranhura


N_CLASSES = 16
N_EXPOSICOES_INICIAIS = 8
CICLOS_ANTES = 20
CICLOS_DEPOIS = 5
MAX_EXPOSICOES_RETORNO = 30
N_CONSULTAS_POR_CLASSE = 50
ORCAMENTO_ATIVO = 16
ORCAMENTO_TRACOS = 1
TAU_ATIVO = 300.0
LIMIAR_TRACO = 0.05
SIGMAS = (0.6, 0.8, 1.0, 1.2)


def configuracoes_traco() -> list[dict]:
    """Grade pré-registrada de 18 configurações, em ordem de desempate."""
    return [
        {"tau_traco": tau, "peso_prior": peso,
         "fator_largura": fator}
        for tau, peso, fator in product((150.0, 300.0, 600.0), (4, 8, 16), (1.0, 2.0))
    ]


@dataclass
class Episodio:
    inicio: list[tuple[int, np.ndarray]]
    interferencia_antes: list[tuple[int, np.ndarray]]
    amostra_nova: np.ndarray
    interferencia_depois: list[tuple[int, np.ndarray]]
    retorno: list[tuple[np.ndarray, list[tuple[int, np.ndarray]]]]
    x_consulta: np.ndarray
    y_consulta: np.ndarray


def gerar_episodio(semente: int, *, sigma: float) -> Episodio:
    """Gera o mesmo episódio para todos os métodos naquela semente."""
    if sigma <= 0:
        raise ValueError("sigma deve ser positivo")

    mundo = Mundo(semente + 700_000, sigma=sigma)
    prototipos = [mundo.pessoa() for _ in range(N_CLASSES + 1)]

    def observar(rotulo: int) -> np.ndarray:
        return mundo.amostras(prototipos[rotulo], 1, sigma=sigma)[0]

    inicio = [
        (rotulo, observar(rotulo))
        for rotulo in range(N_CLASSES)
        for _ in range(N_EXPOSICOES_INICIAIS)
    ]
    ancoras = range(1, N_CLASSES)
    interferencia_antes = [
        (rotulo, observar(rotulo))
        for _ in range(CICLOS_ANTES)
        for rotulo in ancoras
    ]
    amostra_nova = observar(N_CLASSES)
    interferencia_depois = [
        (rotulo, observar(rotulo))
        for _ in range(CICLOS_DEPOIS)
        for rotulo in ancoras
    ]
    retorno = []
    for _ in range(MAX_EXPOSICOES_RETORNO):
        amostra_alvo = observar(0)
        amostras_ancoras = [(rotulo, observar(rotulo)) for rotulo in ancoras]
        retorno.append((amostra_alvo, amostras_ancoras))

    x_consulta, y_consulta = [], []
    for rotulo in range(N_CLASSES):
        x_consulta.append(
            mundo.amostras(prototipos[rotulo], N_CONSULTAS_POR_CLASSE,
                           sigma=sigma)
        )
        y_consulta.extend([rotulo] * N_CONSULTAS_POR_CLASSE)

    return Episodio(
        inicio=inicio,
        interferencia_antes=interferencia_antes,
        amostra_nova=amostra_nova,
        interferencia_depois=interferencia_depois,
        retorno=retorno,
        x_consulta=np.vstack(x_consulta),
        y_consulta=np.asarray(y_consulta, dtype=int),
    )


@dataclass
class ResumoCompacto:
    id: int
    rotulo: int
    centro_f16: np.ndarray
    largura_f16: np.float16
    n: int
    forca: float
    t_ultimo: int
    guardado_em: int


class MemoriaComResumo(MemoriaDeRanhuras):
    """Memória v0.5 com arquivo comprimido usado somente neste experimento."""

    def __init__(self, *, modo: str, sigma: float, config: dict | None = None,
                 seed: int = 0):
        if modo not in {"traco", "cache"}:
            raise ValueError("modo deve ser 'traco' ou 'cache'")
        self.modo_resumo = modo
        self.config_traco = config or {}
        self.resumos: dict[int, ResumoCompacto] = {}
        super().__init__(
            w0=2 * sigma**2, w_min=0.02, z_max=2.5, eta_min=0.02,
            erosao=True, largura_adaptativa=True,
            aprende_deslocamento=False, max_ranhuras=ORCAMENTO_ATIVO,
            politica="murchar", tau=TAU_ATIVO, seed=seed,
        )

    def _vitima_atual(self, protegida: Ranhura) -> Ranhura:
        candidatas = [g for g in self.ranhuras if g is not protegida]
        return min(
            candidatas,
            key=lambda g: g.forca * np.exp(-(self.t - g.t_ultimo) / self.tau),
        )

    def _esquecer(self, protegida: Ranhura) -> None:
        vitima = self._vitima_atual(protegida)
        if vitima.rotulo is not None:
            camara = vitima.camaras[None]
            self.resumos[int(vitima.rotulo)] = ResumoCompacto(
                id=vitima.id,
                rotulo=int(vitima.rotulo),
                centro_f16=np.asarray(camara.centro, dtype=np.float16),
                largura_f16=np.float16(camara.w),
                n=int(camara.n),
                forca=float(vitima.forca),
                t_ultimo=int(vitima.t_ultimo),
                guardado_em=int(self.t),
            )
            while len(self.resumos) > ORCAMENTO_TRACOS:
                mais_antigo = min(
                    self.resumos.values(), key=lambda resumo: resumo.guardado_em
                )
                self.resumos.pop(mais_antigo.rotulo)
        super()._esquecer(protegida)

    def _restaurar(self, rotulo: int) -> bool:
        resumo = self.resumos.pop(rotulo, None)
        if resumo is None:
            return False

        if self.modo_resumo == "traco":
            idade = max(0, self.t - resumo.guardado_em)
            vigor = float(np.exp(-idade / float(self.config_traco["tau_traco"])))
            if vigor < LIMIAR_TRACO:
                return False
            fator_largura = float(self.config_traco["fator_largura"])
            n_camara = max(0, int(self.config_traco["peso_prior"]) - 1)
            forca = vigor
            t_ultimo = self.t
        else:
            fator_largura = 1.0
            n_camara = resumo.n
            forca = resumo.forca
            t_ultimo = self.t

        largura = max(float(resumo.largura_f16) * fator_largura, self.w_min)
        restaurada = Ranhura(
            id=resumo.id,
            rotulo=rotulo,
            camaras={None: Camara(
                centro=np.asarray(resumo.centro_f16, dtype=np.float64),
                w=largura,
                n=n_camara,
                ctx=None,
            )},
            forca=forca,
            t_ultimo=t_ultimo,
            n_ecos=resumo.n,
        )
        self.ranhuras.append(restaurada)
        self._por_rotulo[rotulo] = restaurada
        self._prox_id = max(self._prox_id, restaurada.id + 1)
        self._sujo = True
        return True

    def aprender(self, x, ctx=None, rotulo=None):
        if (rotulo is not None and rotulo not in self._por_rotulo
                and rotulo in self.resumos):
            self._restaurar(int(rotulo))
        return super().aprender(x, ctx=ctx, rotulo=rotulo)


def criar_modelo(metodo: str, *, sigma: float, config: dict | None = None,
                 seed: int = 0):
    if metodo == "apagar":
        return MemoriaDeRanhuras(
            w0=2 * sigma**2, w_min=0.02, z_max=2.5, eta_min=0.02,
            erosao=True, largura_adaptativa=True,
            aprende_deslocamento=False, max_ranhuras=ORCAMENTO_ATIVO,
            politica="murchar", tau=TAU_ATIVO, seed=seed,
        )
    if metodo == "traco":
        return MemoriaComResumo(modo="traco", sigma=sigma, config=config,
                                seed=seed)
    if metodo == "cache":
        return MemoriaComResumo(modo="cache", sigma=sigma, config=config,
                                seed=seed)
    if metodo == "manter_tudo":
        return MemoriaDeRanhuras(
            w0=2 * sigma**2, w_min=0.02, z_max=2.5, eta_min=0.02,
            erosao=True, largura_adaptativa=True,
            aprende_deslocamento=False, max_ranhuras=None,
            politica="murchar", tau=TAU_ATIVO, seed=seed,
        )
    raise ValueError(f"método desconhecido: {metodo}")


def acuracia(memoria: MemoriaDeRanhuras, episodio: Episodio) -> float:
    predicoes, _, _ = memoria.prever(episodio.x_consulta)
    return float(np.mean(np.asarray(predicoes, dtype=int) == episodio.y_consulta))


def recall_alvo(memoria: MemoriaDeRanhuras, episodio: Episodio) -> float:
    mascara = episodio.y_consulta == 0
    predicoes, _, _ = memoria.prever(episodio.x_consulta[mascara])
    return float(np.mean(np.asarray(predicoes, dtype=int) == 0))


def avaliar(episodio: Episodio, *, metodo: str, sigma: float,
            config: dict | None = None, seed: int = 0) -> dict:
    memoria = criar_modelo(metodo, sigma=sigma, config=config, seed=seed)
    for rotulo, x in episodio.inicio:
        memoria.aprender(x, rotulo=rotulo)
    for rotulo, x in episodio.interferencia_antes:
        memoria.aprender(x, rotulo=rotulo)

    acuracia_antes = recall_alvo(memoria, episodio)
    acuracia_balanceada_antes = acuracia(memoria, episodio)
    memoria.aprender(episodio.amostra_nova, rotulo=N_CLASSES)
    alvo_expulso = 0 not in memoria._por_rotulo
    for rotulo, x in episodio.interferencia_depois:
        memoria.aprender(x, rotulo=rotulo)

    limiar = 0.90 * acuracia_antes
    curva = [recall_alvo(memoria, episodio)]
    curva_balanceada = [acuracia(memoria, episodio)]
    e90 = 0 if curva[0] >= limiar else MAX_EXPOSICOES_RETORNO + 1
    if e90 != 0:
        for indice, (x_alvo, amostras_ancoras) in enumerate(episodio.retorno, start=1):
            memoria.aprender(x_alvo, rotulo=0)
            for rotulo, x in amostras_ancoras:
                memoria.aprender(x, rotulo=rotulo)
            valor = recall_alvo(memoria, episodio)
            curva.append(valor)
            curva_balanceada.append(acuracia(memoria, episodio))
            if valor >= limiar:
                e90 = indice
                break

    return {
        "e90": int(e90),
        "recall_alvo_antes": acuracia_antes,
        "acuracia_balanceada_antes": acuracia_balanceada_antes,
        "limiar_90_por_cento_recall": limiar,
        "curva_recall_alvo": curva,
        "curva_acuracia_balanceada": curva_balanceada,
        "alvo_expulso": bool(alvo_expulso),
        "n_ranhuras_final": memoria.n_ranhuras(),
        "n_resumos_final": len(getattr(memoria, "resumos", {})),
    }
