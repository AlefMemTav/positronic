# 03 - O que foi feito, resultados e limites

Todos os números vêm de `resultados.txt` (gerado por `python3 experimentos.py`,
10 sementes; "±" é o desvio entre sementes, não um intervalo de confiança formal).
Dados 100% sintéticos.

## O que foi construído

1. **Núcleo** (`ranhuras.py`): `MemoriaDeRanhuras` com eco, brotar, erosão,
   câmaras por contexto, deslocamento de tom aprendido e murchar com orçamento
   de memória. Ver `docs/01-ideia-central.md`.
2. **Mundo sintético** (`experimentos.py`, classe `Mundo`): cada pessoa é um
   espectro-protótipo de 64 bins (6 a 11 picos gaussianos estreitos, média zero,
   rms 1). Observação = protótipo × ganho + deslocamento do contexto + ruído.
3. **Baselines**: kNN-1, centro da classe (NCM), MLP retreinado com tudo, MLP
   incremental (só o lote novo), k-means com K dado, leader clustering, e
   versões com o mesmo deslocamento de tom (kNN e NCM), LRU, LFU, FIFO e
   aleatório.
4. **Cinco experimentos** (abaixo).

## Resultados

### Exp. 1 - aprender com poucos exemplos (40 pessoas, σ = 1.2)

| Exposições | 1 | 2 | 3 | 5 | 10 |
|---|---|---|---|---|---|
| ranhuras | 0.718 | 0.887 | 0.947 | 0.978 | 0.990 |
| kNN-1 | 0.718 | 0.791 | 0.843 | 0.875 | 0.910 |
| centro da classe (NCM) | 0.718 | 0.890 | 0.949 | 0.979 | 0.990 |
| MLP retreinado com tudo | 0.345 | 0.567 | 0.712 | 0.826 | 0.928 |

**Leitura:** com 1 exemplo, ranhura = kNN = NCM por construção. Com mais, a média
móvel (erosão) vence o kNN-1. **A ranhura ficou praticamente igual ao NCM em todos
os pontos.** O MLP precisa de muito mais exemplos.

### Exp. 2 - aprender em etapas (6 etapas × 8 pessoas)

| Após a etapa 6 | acurácia em todos | retenção das pessoas da etapa 1 |
|---|---|---|
| ranhuras | 0.982 | 0.983 |
| NCM | 0.983 | 0.983 |
| kNN-1 | 0.889 | 0.884 |
| MLP retreinado com tudo | 0.905 | 0.909 |
| MLP incremental (só lote novo) | 0.478 | **0.160** |

**Leitura:** o esquecimento catastrófico do MLP incremental é real e grande. Mas
**kNN e NCM também não esquecem**: não esquecer vem de guardar um protótipo por
entidade, e não é exclusivo das ranhuras.

### Exp. 3 - descobrir pessoas sem rótulo (20 pessoas, 15 observações cada)

(a) ARI / nº de ranhuras (ideal: 1,00 / 20), `z_max = 2.0`, `w0 = 0.32`:

| Variante | σ = 0.3 | σ = 0.4 | σ = 0.5 |
|---|---|---|---|
| completo (erosão + largura) | 0.99 / 20 | 1.00 / 20 | 0.99 / 23 |
| só o centro erode | 0.99 / 20 | 1.00 / 20 | 0.99 / 23 |
| sem erosão (leader clustering) | 1.00 / 20 | 1.00 / 20 | 0.82 / 38 |
| k-means (K=20 dado de graça) | 1.00 / 20 | 1.00 / 20 | 0.99 / 20 |

(b) Sensibilidade ao limiar (σ = 0.4):

| `z_max` | 1.0 | 1.5 | 2.0 | 3.0 | 5.0 | 8.0 |
|---|---|---|---|---|---|---|
| ARI | 0.74 | 0.99 | 1.00 | 0.69 | 0.04 | 0.00 |
| nº ranhuras | 83.5 | 21.1 | 20.1 | 16.4 | 3.9 | 1.3 |

(c) Sensibilidade ao prior de largura (σ = 0.4, `z_max = 2.0`), ARI / nº:

| `w0` | 0.08 | 0.16 | 0.32 | 0.64 | 1.28 |
|---|---|---|---|---|---|
| com largura adaptativa | 0.01 / 298 | 0.92 / 40 | 1.00 / 20 | 0.39 / 11 | 0.01 / 1 |
| largura fixa | 0.00 / 299 | 0.90 / 44 | 1.00 / 20 | 0.68 / 14 | 0.02 / 1 |

**Leitura:** com a calibração certa, brotar descobre as pessoas sozinho. A erosão
só ajuda com ruído mais alto (σ = 0.5). A largura adaptativa **não** corrige um
prior errado (com `w0 = 0.64` ficou pior). O limiar é uma **faca de dois gumes**:
fora de uma faixa estreita o sistema funde todo mundo ou fragmenta tudo.

### Exp. 4 - contexto (30 pessoas conhecidas nos dois contextos; 20 novas só em "calmo"; teste nas novas em "medo")

| Modelo | novas em "medo" | conhecidas | vetores guardados |
|---|---|---|---|
| ranhura plana (ignora contexto) | 0.460 | 0.974 | 50 |
| ranhura + câmaras | 0.429 | 0.975 | 80 |
| ranhura + câmaras + deslocamento | **0.836** | 0.987 | 80 |
| kNN-1 | 0.296 | 0.869 | 360 |
| kNN-1 + deslocamento | 0.682 | 0.915 | 360 |
| NCM | 0.450 | 0.973 | 50 |
| NCM + deslocamento | **0.866** | 0.991 | 50 |

**Leitura:** o ganho vem de **aprender o deslocamento do contexto**, não de ter
câmaras. O NCM com o mesmo truque iguala ou supera as ranhuras com menos memória.
Além disso, no gerador o contexto é aditivo e global, o que favorece qualquer
método que modele esse deslocamento.

### Exp. 5 - memória com orçamento (60 pessoas, 3000 observações, popularidade Zipf que muda na metade)

Acurácia em quem já foi visto (teto sem limite: 0.970):

| Política | orçamento 10 | 20 | 30 |
|---|---|---|---|
| murchar (força com decaimento) | **0.595** | **0.753** | **0.826** |
| LRU | 0.511 | 0.673 | 0.769 |
| FIFO | 0.444 | 0.592 | 0.694 |
| aleatório | 0.443 | 0.592 | 0.700 |
| LFU | 0.419 | 0.573 | 0.687 |

**Leitura:** o murchar vence as outras políticas, e a vantagem sobre LRU é
consistente. É uma política do tipo LRFU (recência + frequência com decaimento),
conhecida. `tau = 300` não foi otimizado.

## Por que a ranhura empata com o NCM aqui (e por que isso é esperado)

No gerador, todas as pessoas têm ruído gaussiano **isotrópico, de mesma variância**,
e protótipo fixo no tempo. Nesse mundo, classificar pelo centro mais próximo (NCM) é
essencialmente o classificador **ótimo** (Bayes). Nenhum método consegue vencê-lo de
verdade; as ranhuras só podem empatar. Logo, o empate nos exps. 1 e 2 **não é
evidência contra nem a favor** da ideia: é uma propriedade do gerador.

Para um teste capaz de mostrar vantagem, o mundo precisa quebrar a otimalidade do
NCM: pessoas com mais de um modo (contextos), variância de ruído diferente por
pessoa, deriva lenta do protótipo no tempo (aí a taxa mínima `eta_min` passa a
importar), ruído não gaussiano ou estrutura temporal. Ver Fase 2 em
`docs/04-proximos-passos.md`.

## O que **não** foi mostrado

- Nada com dados reais (voz, rosto, texto).
- **Ressonância entre ranhuras** (A8) e **leitura por coerência** (A7): não existem no código.
- **Contexto não aditivo** ou específico por pessoa: não testado.
- **Retorno rápido** após longo esquecimento ("saudade"): não testado.
- Comparação com os concorrentes reais (Prototypical Networks, ART, Titans,
  kNN-LM, LoRA por usuário).
- Qualquer vantagem de energia ou paralelismo (isso só faria sentido em hardware).
- Escala (tudo é pequeno: ≤ 60 pessoas, D = 64).

## Decisões e armadilhas (diário de calibração)

1. **Gerador v1 era fácil demais de confundir.** Espectros só com amplitudes
   positivas compartilham um componente médio e as pessoas ficaram parecidas
   (distância² mediana ≈ 1.0, vizinho mais próximo ≈ 0.2). Corrigi com média zero,
   picos mais estreitos e D = 64 (mediana ≈ 2.05, vizinho mais próximo ≈ 0.87).
2. **σ = 0.5 deu 100% em tudo** no exp. 1 e não discriminava nada. Subi para
   σ = 1.2 nos experimentos supervisionados.
3. **O exp. 3 usa σ de 0.3 a 0.5** de propósito: descobrir sem rótulo exige
   que a distância² entre dois ecos da mesma pessoa (2σ²) seja menor que a
   distância² entre pessoas. Com σ alto, a classificação supervisionada ainda
   funciona (a média elimina o ruído), mas a descoberta não.
4. **`w0 = 2σ²`** foi escolhido como prior; `w0 = 0.32` e `z_max = 2.0` no exp. 3
   foram calibrados olhando o próprio exp. 3 (por isso as varreduras b e c).
   Os padrões do código (`w0 = 0.5`, `z_max = 2.5`) não são esses valores.
5. **Os baselines justos mudaram a conclusão.** Antes de incluir "NCM +
   deslocamento", ranhura + deslocamento (0.84) parecia bem à frente do kNN +
   deslocamento (0.68). Com o NCM + deslocamento (0.87), ficou claro que a
   diferença vem de usar protótipos médios e não das ranhuras. Do mesmo modo,
   incluir LRU e LFU mostrou que o murchar vence mas não é uma ideia nova.
6. Um bug no baseline `KNN1Desloc` (formato do array de deslocamentos) foi
   corrigido antes dos resultados finais.
7. **Os baselines não foram otimizados.** O kNN usa k = 1 (k > 1 ou ponderado por
   distância seria mais forte com várias exposições) e o MLP usa hiperparâmetros
   padrão (uma camada de 64, sem busca). Os números do MLP são um piso, não o
   melhor possível. Faltam também baselines de aprendizado contínuo propriamente
   ditos (replay com buffer pequeno, EWC) e de agrupamento incremental (ART,
   DP-means, GNG).

## Como não se enganar com estes números

- Um empate com NCM é o resultado esperado de um protótipo com média móvel. Para
  a proposta valer a pena, ela precisa **ganhar de NCM em algum cenário
  definido de antemão** (ver `docs/04-proximos-passos.md`).
- Ajustar hiperparâmetros olhando o conjunto de teste infla os resultados. Nos
  próximos passos, separar calibração de teste.
- Versões diferentes de scikit-learn ou NumPy podem alterar os números do MLP
  na terceira casa decimal.