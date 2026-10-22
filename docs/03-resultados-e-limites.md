# 03 - O que foi feito, resultados e limites

Nos experimentos 1 a 5, os números vêm de `resultados.txt` (gerado pelo módulo
legado `experimentos/comum/legado.py`, 10 sementes; "±" é o desvio entre
sementes, não um intervalo de confiança formal). Os resultados da Fase 1 e do
experimento 6 têm relatos próprios em `experimentos/fase1/LEIA.md` e
`experimentos/06/LEIA.md`; os dois estudos também são resumidos abaixo. Os
resultados dos experimentos 6 a 8 estão registrados por execução em
`resultados/execucoes/`. Dados 100% sintéticos.

## O que foi construído

1. **Núcleo** (`ranhuras/__init__.py`): `MemoriaDeRanhuras` com eco, brotar,
   erosão, câmaras por contexto, deslocamento de tom aprendido e murchar com
   orçamento de memória. Ver `docs/01-ideia-central.md`.
2. **Mundo sintético legado** (`experimentos/comum/legado.py`, classe `Mundo`):
   cada pessoa é um espectro-protótipo de 64 bins (6 a 11 picos gaussianos
   estreitos, média zero, rms 1). Observação = protótipo × ganho + deslocamento
   do contexto + ruído.
3. **Baselines**: kNN-1, centro da classe (NCM), MLP retreinado com tudo, MLP
   incremental (só o lote novo), k-means com K dado, leader clustering, e
   versões com o mesmo deslocamento de tom (kNN e NCM), LRU, LFU, FIFO e
   aleatório.
4. **Cinco experimentos exploratórios originais** (abaixo); estudos posteriores
   têm registros próprios em suas pastas.

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

### Exp. 6 - contexto não aditivo (não informativo por efeito de teto)

O experimento avaliou se as câmaras por contexto ajudam quando cada identidade
tem um efeito contextual próprio. Na calibração, porém, o melhor baseline já
atingia 0,9968 e as câmaras 0,9994: a margem disponível era de cerca de 0,3 ponto
percentual, muito menor que o ganho mínimo de 5 pp. O gerador, portanto, não
permitia um teste informativo desse ganho.

| Método na condição primária | Acurácia média de teste |
|---|---:|
| Câmaras por contexto | 0,9994 |
| Centro por identidade-contexto com retração (`λ=0,684`) | 0,9979 |

Nas 30 sementes, `Δ = +0,15` pp, IC95% bootstrap `[+0,02; +0,30]` pp. A regra
mecânica pré-registrada classificaria o resultado como refutado quanto ao ganho
mínimo, mas a errata o reclassifica corretamente como **não informativo por
efeito de teto**. Ele não confirma nem refuta a hipótese de memória contextual.

A grade secundária, com 10 sementes, foi exploratória. As perdas concentraram-se
nas células com zero exposições no contexto final: o Δ médio foi −29,9 pp nessas
células. Com 1, 3 e 10 exposições, as médias exploratórias foram +0,9, +0,3 e
+0,1 pp, respectivamente. Sem as células de zero exposições, a média geral da
grade foi +0,4 pp; esses resultados não substituem o teste primário nem têm
interpretação confirmatória. A tabela das nove células de zero exposições e os
limites completos estão em `experimentos/06/LEIA.md`.

### Exp. 7 - contexto heteroscedástico (câmaras isoladas)

O experimento comparou a versão v0.4 das câmaras com baselines ajustados na
calibração. A condição primária tinha quatro contextos, três exposições no
contexto final, força contextual 0,8 e heterogeneidade de ruído 1,0. A calibração
selecionou `σ̄ = 2,0` como primeiro nível que passou a margem de manobra
(`H_cal = 0,1094`); `σ̄ = 1,6` não passou (`H_cal = 0,0712`).

| Método na condição primária | Acurácia média |
|---|---:|
| Câmaras v0.4 (`w0=0,08`, `eta_min=0,01`) | 0,7928 |
| Baseline `variancia_identidade` (`λ=0,75`, `κ=0`) | 0,8664 |

Em 30 sementes de teste (`9000–9029`), a diferença pareada foi `Δ = −7,36`
pontos percentuais, com IC95% bootstrap `[−8,50; −6,22]` pp. Como o limite
superior ficou abaixo do ganho mínimo pré-registrado de `+5` pp, o resultado foi
**refutado quanto ao ganho mínimo na condição primária**. Isso é evidência contra
uma vantagem das câmaras isoladas nessa condição sintética; não testa a rede de
ranhuras com ligações, que não está implementada.

A grade exploratória usou 10 sementes (`10000–10009`) em 216 células. A tabela
mostra a média de Δ por número de exposições e quantas das 54 células tiveram
Δ positivo:

| Exposições | Δ médio | Células com Δ > 0 |
|---:|---:|---:|
| 0 | +0,8 pp | 34/54 |
| 1 | +3,3 pp | 36/54 |
| 3 | −9,5 pp | 0/54 |
| 10 | −5,0 pp | 3/54 |

Essas médias não têm papel confirmatório. A grade reutilizou o baseline
congelado na calibração da condição primária (`λ=0,75`, escolhido para três
exposições); ele não foi reajustado em cada célula. Portanto, os ganhos
exploratórios em algumas células de uma exposição não demonstram vantagem das
câmaras nesse regime. A grade responde como a configuração congelada se comporta
fora da condição primária, não qual método seria melhor após ajuste específico
por célula.

Na ablação exploratória da célula primária, também com as mesmas 10 sementes,
a acurácia foi 0,8137 na versão completa, 0,6855 sem largura adaptativa, 0,8146
sem deslocamento e 0,8735 sem câmaras por contexto; o baseline obteve 0,8823.
Isso sugere que a largura adaptativa contribuiu nessa execução, enquanto as
câmaras por contexto não ajudaram. A ablação tem somente 10 sementes e não é um
novo teste confirmatório.

O resultado confirmatório agregado, os registros por semente, a calibração e a
grade estão em `resultados/execucoes/`; o protocolo e a interpretação completa
estão em `experimentos/07/PREREGISTRO.md` e `experimentos/07/LEIA.md`.

### Exp. 8 - retorno rápido após esquecimento

A calibração executou as 30 sementes pré-registradas (`12000–12029`) no commit
`da4b2a6`, com Python 3.12.15, NumPy 2.5.3 e scikit-learn 1.9.1. Nenhum dos
quatro valores candidatos de `σ` passou os gates de executabilidade. Em cada
caso, o recall médio do alvo antes da expulsão ficou acima do limite superior
pré-registrado de `0,98`:

| `σ` | Recall médio antes da expulsão | `E90` médio de Apagar |
|---:|---:|---:|
| 0,6 | 1,0000 | 1,000 |
| 0,8 | 1,0000 | 1,100 |
| 1,0 | 0,9973 | 2,000 |
| 1,2 | 0,9840 | 3,467 |

Pela regra definida antes da calibração, o experimento é **não executável como
confirmatório**. A configuração registra `executavel_confirmatorio: false`,
`sigma_primario: null` e nenhum tamanho de amostra de teste. Nenhuma semente de
teste foi aberta. Portanto, este resultado de calibração não é evidência a favor
nem contra a hipótese de que o traço acelere o reaprendizado. Uma nova tentativa
que altere o gerador ou os gates precisa de pré-registro próprio e novas
sementes. Os artefatos estão em `experimentos/08/LEIA.md`,
`experimentos/08/configuracao-congelada.json` e `resultados/execucoes/`.

## Por que a ranhura empata com o NCM aqui (e por que isso é esperado)

No gerador, todas as pessoas têm ruído gaussiano **isotrópico, de mesma variância**,
e protótipo fixo no tempo. Nesse mundo, classificar pelo centro mais próximo (NCM) é
essencialmente o classificador **ótimo** (Bayes). Nenhum método consegue vencê-lo de
verdade; as ranhuras só podem empatar. Logo, o empate nos exps. 1 e 2 **não é
evidência contra nem a favor** da ideia: é uma propriedade do gerador.

Para um teste capaz de mostrar vantagem, o mundo precisa quebrar a otimalidade do
NCM: pessoas com mais de um modo (contextos), variância de ruído diferente por
pessoa, deriva lenta do protótipo no tempo (aí a taxa mínima `eta_min` passa a
importar), ruído não gaussiano ou estrutura temporal. Os experimentos 6 e 7
testaram algumas dessas condições; seus resultados e limites estão resumidos
acima e em `experimentos/06/LEIA.md` e `experimentos/07/LEIA.md`.

## O que **não** foi mostrado

- Nada com dados reais (voz, rosto, texto).
- **Ressonância entre ranhuras** (A8) e **leitura por coerência** (A7): não existem no código. O experimento 7 não as testou.
- O contexto não aditivo específico por pessoa foi testado no Exp. 6, mas o
  resultado foi não informativo por efeito de teto; não se concluiu sobre essa
  hipótese.
- **Retorno rápido** após longo esquecimento ("saudade"): não teve teste
  confirmatório; a calibração do experimento 8 não passou os gates de
  executabilidade pré-registrados.
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
- O resultado negativo do experimento 7 vale para a hipótese e a condição
  primária registradas; não deve ser generalizado para uma rede com ligações.
  Inversamente, células exploratórias positivas da grade não revertem o
  resultado primário.
- Ajustar hiperparâmetros olhando o conjunto de teste infla os resultados. Nos
  próximos passos, separar calibração de teste.
- Versões diferentes de scikit-learn ou NumPy podem alterar os números do MLP
  na terceira casa decimal.
