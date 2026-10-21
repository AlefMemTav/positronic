"""
ranhuras.py - protótipo em CPU da lógica de "ranhuras elásticas".

Tradução da metáfora para algoritmo (tudo em NumPy, sem hardware especial):

  eco           -> a entrada x (um espectro de D bins) é comparada com cada
                   câmara de cada ranhura; a "dissonância" z = d2 / w diz quão
                   longe x está do que aquela câmara sabe, medido em larguras.
  brotar        -> se nenhuma câmara ressoa (z > z_max), nasce uma ranhura nova
                   com UMA observação (aprendizado de um exemplo só).
  erosão        -> cada eco que ressoa desgasta a câmara: o centro caminha para
                   a observação e a largura w encolhe até o espalhamento real
                   daquela pessoa (a ranhura fica mais funda/seletiva).
                   A taxa nunca cai abaixo de eta_min: a ranhura continua
                   elástica e acompanha mudanças lentas.
  câmaras       -> uma ranhura guarda uma câmara por contexto (calmo, medo...).
  deslocamento  -> opcional: o sistema aprende o "deslocamento de tom" de cada
                   contexto com as pessoas vistas em mais de um contexto, e o
                   aplica a quem só foi visto em um (transposição de tom).
  murchar       -> cada ranhura tem uma força que decai com o tempo sem eco e
                   sobe a cada eco; com orçamento de memória limitado, a mais
                   murcha é a primeira a ser esquecida.

Aviso honesto: matematicamente isso é parente próximo de clustering online com
núcleos gaussianos (Adaptive Resonance Theory, redes RBF, leader clustering).
O ponto de construí-lo é medir QUAIS partes da metáfora fazem diferença.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Camara:
    """Sub-ranhura: uma cavidade ajustada a um contexto."""
    centro: np.ndarray
    w: float          # largura: variância média por bin (tolerância do eco)
    n: int            # quantos ecos já desgastaram esta câmara
    ctx: object = None


@dataclass
class Ranhura:
    id: int
    rotulo: object
    camaras: dict = field(default_factory=dict)   # ctx -> Camara
    forca: float = 1.0
    t_ultimo: int = 0
    n_ecos: int = 0


class MemoriaDeRanhuras:
    def __init__(self, w0=0.5, w_min=0.02, z_max=2.5, eta_min=0.02,
                 erosao=True, largura_adaptativa=True,
                 aprende_deslocamento=False,
                 max_ranhuras=None, politica="murchar", tau=300.0, seed=0):
        self.w0 = w0                      # largura inicial (prior de tolerância)
        self.w_min = w_min
        self.z_max = z_max                # acima disso: dissonância => brotar
        self.eta_min = eta_min            # elasticidade mínima da erosão
        self.erosao = erosao
        self.largura_adaptativa = largura_adaptativa
        self.aprende_deslocamento = aprende_deslocamento
        self.max_ranhuras = max_ranhuras
        self.politica = politica          # "murchar" | "lru" | "lfu" | "fifo" | "aleatorio"
        self.tau = tau
        self.rng = np.random.default_rng(seed)

        self.ranhuras: list[Ranhura] = []
        self._por_rotulo: dict = {}
        self._prox_id = 0
        self.t = 0
        self.ref_ctx = None
        self._delta: dict = {}
        self._sujo = False

    # ------------------------------------------------------------ utilidades
    def n_ranhuras(self):
        return len(self.ranhuras)

    def n_vetores(self):
        return sum(len(g.camaras) for g in self.ranhuras)

    def _recalcular_delta(self):
        self._delta = {}
        self._sujo = False
        if not self.aprende_deslocamento or self.ref_ctx is None:
            return
        acum: dict = {}
        for g in self.ranhuras:
            ref = g.camaras.get(self.ref_ctx)
            if ref is None:
                continue
            for ctx, cam in g.camaras.items():
                if ctx != self.ref_ctx:
                    acum.setdefault(ctx, []).append(cam.centro - ref.centro)
        for ctx, v in acum.items():
            self._delta[ctx] = np.mean(v, axis=0)

    def _delta_de(self, ctx):
        if self._sujo:
            self._recalcular_delta()
        return self._delta.get(ctx, 0.0)

    # ------------------------------------------------------------------ eco
    def _dissonancia(self, X, ctx):
        """z[i,k]: dissonância da amostra i com a câmara k (em larguras)."""
        Xc = X - self._delta_de(ctx)
        centros, ws, dono = [], [], []
        for gi, g in enumerate(self.ranhuras):
            for c, cam in g.camaras.items():
                centros.append(cam.centro - self._delta_de(c))
                ws.append(cam.w)
                dono.append(gi)
        C, W, dono = np.array(centros), np.array(ws), np.array(dono)
        d2 = ((Xc ** 2).sum(1)[:, None] + (C ** 2).sum(1)[None, :]
              - 2 * Xc @ C.T) / X.shape[1]
        z = np.maximum(d2, 0) / W[None, :]
        # comparador entre câmaras de larguras diferentes (verossimilhança
        # gaussiana isotrópica: z + log w)
        score = z + np.log(W / self.w0)[None, :]
        return z, score, dono

    def prever(self, X, ctx=None):
        """Retorna (rótulos, ids das ranhuras, dissonância mínima)."""
        X = np.atleast_2d(np.asarray(X, float))
        z, score, dono = self._dissonancia(X, ctx)
        k = score.argmin(1)
        zmin = z[np.arange(len(X)), k]
        rot = [self.ranhuras[dono[j]].rotulo for j in k]
        ids = np.array([self.ranhuras[dono[j]].id for j in k])
        return rot, ids, zmin

    # ------------------------------------------------------------ aprendizado
    def _brotar(self, x, ctx, rotulo):
        g = Ranhura(id=self._prox_id, rotulo=rotulo, t_ultimo=self.t)
        g.camaras[ctx] = Camara(x.copy(), self.w0, 1, ctx)
        self._prox_id += 1
        self.ranhuras.append(g)
        if rotulo is not None:
            self._por_rotulo[rotulo] = g
        return g

    def _erodir(self, cam, x):
        if not self.erosao:
            return
        d2 = float(np.mean((x - cam.centro) ** 2))
        taxa = max(1.0 / (cam.n + 1), self.eta_min)
        cam.centro = cam.centro + taxa * (x - cam.centro)
        if self.largura_adaptativa:
            cam.w = max(cam.w + taxa * (d2 - cam.w), self.w_min)
        cam.n += 1

    def _eco(self, g, x, ctx):
        cam = g.camaras.get(ctx)
        if cam is not None:
            self._erodir(cam, x)
        else:  # primeira vez nesse contexto: nasce uma câmara nova
            w = (np.mean([c.w for c in g.camaras.values()])
                 if self.largura_adaptativa else self.w0)
            g.camaras[ctx] = Camara(x.copy(), w, 1, ctx)

    def aprender(self, x, ctx=None, rotulo=None):
        """Uma observação. Com rótulo: supervisionado. Sem: descobre sozinho."""
        self.t += 1
        x = np.asarray(x, float)
        if self.ref_ctx is None and ctx is not None:
            self.ref_ctx = ctx
        if rotulo is not None:
            g = self._por_rotulo.get(rotulo)
            if g is None:
                g = self._brotar(x, ctx, rotulo)
            else:
                self._eco(g, x, ctx)
        elif not self.ranhuras:
            g = self._brotar(x, ctx, None)
        else:
            z, score, dono = self._dissonancia(x[None], ctx)
            k = int(score.argmin())
            if z[0, k] <= self.z_max:
                g = self.ranhuras[dono[k]]
                self._eco(g, x, ctx)
            else:
                g = self._brotar(x, ctx, None)

        g.forca = g.forca * np.exp(-(self.t - g.t_ultimo) / self.tau) + 1.0
        g.t_ultimo = self.t
        g.n_ecos += 1
        self._sujo = True
        if self.max_ranhuras and len(self.ranhuras) > self.max_ranhuras:
            self._esquecer(protegida=g)
        return g.id

    # -------------------------------------------------------------- esquecer
    def _esquecer(self, protegida):
        cand = [g for g in self.ranhuras if g is not protegida]
        if self.politica == "murchar":
            alvo = min(cand, key=lambda g: g.forca
                       * np.exp(-(self.t - g.t_ultimo) / self.tau))
        elif self.politica == "lru":      # menos recentemente usada
            alvo = min(cand, key=lambda g: g.t_ultimo)
        elif self.politica == "lfu":      # menos frequentemente usada
            alvo = min(cand, key=lambda g: g.n_ecos)
        elif self.politica == "fifo":
            alvo = min(cand, key=lambda g: g.id)
        else:
            alvo = cand[int(self.rng.integers(len(cand)))]
        self.ranhuras.remove(alvo)
        if alvo.rotulo is not None:
            self._por_rotulo.pop(alvo.rotulo, None)
