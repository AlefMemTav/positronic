# Ranhuras elásticas

Protótipo de pesquisa, em Python/NumPy (só CPU), de uma memória de aprendizado
online em que a unidade básica não é um peso e sim uma **ranhura**: uma cavidade
que se molda por erosão a cada eco, brota sozinha quando nada ressoa e murcha
(sem sumir) quando para de ser usada.

> **Status (20/10/2026):** protótipo funcional + 5 experimentos sintéticos.
> Resultado honesto até aqui: o núcleo se comporta como um classificador por
> protótipos com bons truques (sem esquecimento, aprendizado com 1 exemplo,
> esquecimento elástico). **A parte que seria realmente nova (ressonância entre
> ranhuras, contexto não aditivo, substrato oscilatório) ainda não foi
> implementada nem testada.** Veja `docs/03-resultados-e-limites.md`.

## Mapa dos documentos

| Arquivo | Para quê |
|---|---|
| `README.md` (este) | visão geral, como instalar e rodar, uso da API |
| `docs/01-ideia-central.md` | a ideia, o "neurônio artificial" (a ranhura) e a tradução metáfora → matemática |
| `docs/02-teoria.md` | o que é hipótese minha, o que já existe na literatura e onde se encaixa |
| `docs/03-resultados-e-limites.md` | o que foi feito, números, armadilhas, o que **não** foi mostrado |
| `docs/04-proximos-passos.md` | roteiro priorizado com critério de sucesso para cada passo |

## Estrutura do código

```
ranhuras.py        núcleo: classe MemoriaDeRanhuras (Camara, Ranhura)
experimentos.py    gerador sintético, baselines, experimentos 1 a 5
resultados.txt     saída completa da última execução
requirements.txt   dependências
docs/              documentação
```

## Instalar e rodar

Testado com Python 3, NumPy 2.5.3 e scikit-learn 1.9.1.

```bash
pip install -r requirements.txt

python3 experimentos.py          # tudo (~1 min); gera a saída no terminal
python3 experimentos.py 1 3      # só os experimentos 1 e 3
python3 experimentos.py > resultados.txt
```

Tudo é determinístico (sementes fixas). `SIGMA`, `SEEDS` e `D` ficam no topo de
`experimentos.py`.

| Exp. | Pergunta | Compara com |
|---|---|---|
| 1 | Quão bem reconhece uma pessoa após 1, 2, 3, 5, 10 exposições? | kNN-1, centro da classe (NCM), MLP retreinado |
| 2 | Esquece o que sabia ao aprender pessoas novas em etapas? | + MLP incremental (só lote novo) |
| 3 | Descobre quantas pessoas existem, sem rótulos (brotar)? Erosão ajuda? | leader clustering, k-means (K dado) |
| 4 | Generaliza para quem só foi visto em outro contexto? | kNN e NCM com o mesmo "deslocamento de tom" |
| 5 | Com memória limitada, quem esquecer? | LRU, LFU, FIFO, aleatório |

## Usar o núcleo

Descobrindo pessoas sem rótulo (cada observação é um vetor de `D` valores):

```python
from ranhuras import MemoriaDeRanhuras

mem = MemoriaDeRanhuras(w0=0.32, z_max=2.0)   # w0 e z_max: ver tabela abaixo
ids = [mem.aprender(x) for x in X]            # id da ranhura que ecoou (ou brotou)
print(mem.n_ranhuras())
```

Supervisionado, com contexto:

```python
mem = MemoriaDeRanhuras(w0=2.88, aprende_deslocamento=True)
mem.aprender(x, ctx="calmo", rotulo="mae")
mem.aprender(x2, ctx="medo", rotulo="mae")    # nasce uma câmara "medo" na mesma ranhura
rotulos, ids, dissonancia = mem.prever(x_novo, ctx="medo")
```

### Hiperparâmetros

| Parâmetro | Padrão | Significado |
|---|---|---|
| `w0` | 0.5 | largura inicial de uma ranhura nova (prior de tolerância). **Sensível**: ideal ≈ distância² esperada entre dois ecos da mesma pessoa (2σ²) |
| `z_max` | 2.5 | acima desta dissonância nada ressoa e uma ranhura brota (modo sem rótulo). **Sensível** |
| `eta_min` | 0.02 | menor taxa de erosão; mantém a ranhura elástica |
| `w_min` | 0.02 | piso da largura |
| `erosao` | True | desliga para virar *leader clustering* (ablação) |
| `largura_adaptativa` | True | a largura segue o espalhamento real da pessoa |
| `aprende_deslocamento` | False | aprende o "deslocamento de tom" de cada contexto (ver doc 01) |
| `max_ranhuras` | None | orçamento de memória |
| `politica` | "murchar" | quem esquecer: `murchar`, `lru`, `lfu`, `fifo`, `aleatorio` |
| `tau` | 300 | escala de tempo do murchar |

Atenção: os padrões **não** são os valores calibrados dos experimentos. Os
experimentos passam valores explícitos (`w0=0.32, z_max=2.0` no exp. 3;
`w0=2σ²=2.88` nos demais).

## Limitações conhecidas (resumo)

- Dados sintéticos; nenhum teste com dados reais ainda.
- `w0` e `z_max` precisam conhecer a escala do ruído (ver exp. 3b/3c).
- O contexto é modelado como deslocamento aditivo global; contexto não aditivo
  não foi testado.
- Nada aqui simula física de ondas: "ressonância" é uma similaridade gaussiana.
