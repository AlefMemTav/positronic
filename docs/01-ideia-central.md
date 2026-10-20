# 01 - Ideia central e o "neurônio artificial"

## A ideia em um parágrafo

O modelo atual de IA é ótimo para aprender sobre o **mundo** (conhecimento
cristalizado, média estatística) e ruim para aprender sobre **uma pessoa
específica**, de forma contínua, com poucos exemplos e sem apagar o que já sabe.
A proposta é um **módulo pequeno, elástico e autobiográfico** que conviva com o
modelo grande:

- aprende **online**, um episódio de cada vez;
- aprende uma pessoa com **um único encontro** (a ranhura brota);
- aprender algo novo **não sobrescreve** o antigo (brota em outro lugar);
- guarda **contexto**, não só fato ("confiável calmo, diferente com medo");
- **esquece de forma elástica**: o que não é usado murcha, mas não some de uma vez
  e volta rápido quando reencontrado.

Hipótese de substrato (não implementada): isso poderia rodar em computação por
**ressonância/eco** (som, eletromagnetismo), onde uma ranhura é uma cavidade com
frequências próprias e "entender" é o eco formar um padrão coerente.

> O que está implementado é a **lógica** das ranhuras em CPU. O substrato físico
> ficou de fora de propósito (decisão de 20/10/2026).

## O neurônio artificial: a ranhura

Uma **Ranhura** representa uma entidade (uma pessoa, um conceito) e contém:

| Campo | Papel |
|---|---|
| `camaras: {contexto → Camara}` | uma cavidade por contexto em que a entidade já foi vista |
| `forca` | vigor da ranhura; sobe a cada eco e decai com o tempo (murchar) |
| `t_ultimo`, `n_ecos` | quando e quantas vezes ecoou |
| `rotulo` | nome, quando há supervisão (opcional) |

Uma **Câmara** (sub-ranhura) é a cavidade propriamente dita:

| Campo | Papel |
|---|---|
| `centro` (vetor de D valores) | o "formato" da cavidade: o espectro típico daquela entidade naquele contexto |
| `w` | **largura**: tolerância do eco. Ranhura rasa e larga aceita quase tudo; funda e estreita é seletiva |
| `n` | quantos ecos já a desgastaram |
| `ctx` | contexto em que se formou |

A entrada `x` é um vetor (um "espectro" de D bins).

## As quatro operações

**1. Eco** (reconhecer). Para cada câmara:

```
d2(x, c) = (1/D) * soma_i (x_i - c_i)^2        distância quadrática média
z        = d2 / w                              dissonância, em "larguras"
score    = z + log(w / w0)                     comparador entre larguras diferentes
```

A câmara de menor `score` vence. Se `z <= z_max`, ela **ressoa**.
(`z + log w` é a verossimilhança de uma gaussiana isotrópica; sem o `log`, ranhuras
estreitas seriam punidas demais.)

**2. Brotar** (aprender algo novo). Sem rótulo: se nenhuma câmara ressoa
(`z > z_max`), nasce uma ranhura com **uma** observação como centro e largura
inicial `w0`. Com rótulo: se o rótulo é inédito, nasce; se já existe, ecoa nele.
Não há reaprendizagem global: nada do que já existia é tocado.

**3. Erosão** (refinar). Cada eco que ressoa desgasta a câmara vencedora:

```
taxa = max(1/(n+1), eta_min)
c   <- c + taxa * (x - c)                      centro caminha até a observação
w   <- max(w + taxa * (d2 - w), w_min)         largura segue o espalhamento real
n   <- n + 1
```

No início (`n` pequeno) é uma média móvel; depois a taxa estaciona em `eta_min`,
então a ranhura **continua elástica** e acompanha mudanças lentas. É isso que
transforma "uma observação" em "uma ranhura funda".

**4. Murchar** (esquecer com elasticidade). A cada eco:

```
forca <- forca * exp(-(t - t_ultimo)/tau) + 1
```

A força é um contador com vazamento (recência e frequência juntas). Com memória
limitada (`max_ranhuras`), sai primeiro a ranhura de menor força decaída. Sem
limite, nada é apagado: só perde prioridade.

## Contexto: câmaras e "deslocamento de tom"

Uma ranhura guarda **uma câmara por contexto**. Ao ver a entidade num contexto
novo, nasce uma câmara nova na mesma ranhura (herdando a largura).

Opcionalmente (`aprende_deslocamento=True`), o sistema aprende o efeito médio de
cada contexto com quem já foi visto em dois contextos:

```
delta[ctx] = média sobre ranhuras de ( centro_câmara[ctx] - centro_câmara[ref] )
```

e **transpõe** a entrada (`x - delta[ctx]`) antes de comparar. Assim, quem só foi
visto em `ref` ("calmo") pode ser reconhecido em "medo". É a mesma ideia de
transpor uma melodia de tom. **Limite:** só vale se o contexto desloca todo mundo
da mesma forma (aditivo e global).

## Tradução metáfora → matemática → código

| Metáfora | Matemática | Onde está |
|---|---|---|
| ranhura | par (centro, largura) por contexto | `Ranhura`, `Camara` |
| eco | `z = d2/w` | `_dissonancia` |
| ressoar | `z <= z_max` | `aprender` (modo sem rótulo) |
| dissonância = novidade | `z > z_max` → brotar | `_brotar` |
| erosão | média móvel do centro e da largura, taxa ≥ `eta_min` | `_erodir` |
| ranhura funda | `w` pequeno, `n` grande | `Camara` |
| murchar | força com decaimento exponencial | `aprender`, `_esquecer` |
| "tom" do contexto | `delta[ctx]` | `_recalcular_delta` |
| frequências da cavidade, espectro de modos | **não implementado** | - |
| o eco que dispara outra ranhura (corrente) | **não implementado** | - |
| entendimento = acorde coerente | **não implementado** | - |

## Glossário PT ↔ EN (para buscar literatura)

ranhura / câmara ≈ prototype / mixture component · eco ≈ similarity / kernel
response · brotar ≈ novelty-triggered unit creation (nonparametric) · erosão ≈
online prototype update · murchar ≈ decayed usage counter / cache eviction ·
deslocamento de tom ≈ context-conditioned offset / domain shift correction.
