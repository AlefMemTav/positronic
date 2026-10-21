# Pré-registro — Experimento 7: contexto heteroscedástico

**Estado deste documento:** pré-registro integrado ao `master` no merge commit
`191685b963e396887cc74c8ca0a124d43126827f`. Nenhuma semente de calibração ou
teste do experimento 7 foi executada. Os esclarecimentos ao final deste documento
foram registrados antes de qualquer calibração; o commit original do pré-registro
permanece preservado no histórico.

## Pergunta e hipótese

Na tarefa sintética abaixo, a versão v0.4 das câmaras por contexto supera o
melhor baseline selecionado apenas na calibração por pelo menos 5 pontos
percentuais de acurácia?

A hipótese confirmatória aplica-se exclusivamente à condição primária escolhida
pela regra de margem de manobra desta nota. Não é uma afirmação sobre todos os
níveis possíveis de ruído, heterogeneidade, força contextual ou exposições.

## Gerador e tarefa

O gerador parte da estrutura do experimento 6, preservando dimensão, classes,
contextos, efeitos e protocolo de consulta. Parâmetros da condição primária:

- dimensão `D = 64`;
- 30 identidades de suporte e 20 identidades-alvo;
- 4 contextos; contexto 0 é referência e contexto 3 é o contexto final;
- cada identidade de suporte tem 5 observações em cada contexto;
- cada identidade-alvo tem 3 observações no contexto de referência e 3 no
  contexto final;
- 50 consultas por identidade-alvo no contexto final; a acurácia considera
  todas as 50 identidades como classes candidatas, inclusive identidades de
  suporte;
- força do efeito contextual individual `f = 0,8`;
- heterogeneidade de ruído `h = 1,0`.

Para a identidade `i` no contexto `c`, uma observação é

`x_ic = μ_i + g_c + u_ic + ε_ic`,

onde `μ_i` é o protótipo da identidade, `g_0 = 0`, `g_c ~ N(0, 0,25² I_D)` para
`c > 0`, `u_i0 = 0` e `u_ic ~ N(0, f² I_D)` para `c > 0`. Os efeitos são
amostrados uma vez por episódio e mantidos entre observações da mesma identidade
e contexto.

O desvio padrão de ruído da identidade é

`σ_i = σ̄ · exp(Z_i)`, com `Z_i ~ N(−h²/2, h²)`,

e `ε_ic ~ N(0, σ_i² I_D)`. Assim, `E[σ_i] = σ̄`, enquanto
`E[σ_i²] = σ̄² exp(h²)`. “Ruído médio” designa a média do desvio padrão, não a
média da variância.

Protótipos e demais detalhes não alterados seguem `experimentos/06/modelos.py`
e `experimentos/comum/legado.py`, com versões fixadas no repositório. O código
novo deve tornar explícitos os parâmetros `σ̄` e `h`, manter a geração
determinística por semente e não consultar rótulos ou amostras de consulta para
ajuste.

## Condição primária e margem de manobra

A condição primária fixa contexto, exposições, força e heterogeneidade conforme
a seção anterior. A calibração avaliará `σ̄` nesta ordem fixa:

1. `1,6`;
2. `2,0`;
3. `2,4`.

Para cada candidato, ajustar os baselines com as sementes de calibração e
selecionar o baseline de maior acurácia média. Calcular
`H_cal = 1 − acurácia_calibração_do_melhor_baseline`. A condição primária será o
primeiro valor de `σ̄` com `H_cal ≥ 0,10`. Essa seleção depende apenas da
calibração; o valor escolhido e todos os resultados de calibração serão
registrados antes do teste.

Se nenhum dos três valores satisfizer a margem, o experimento será declarado
**não executável como confirmatório**. Nenhuma semente de teste será aberta. Uma
mudança de gerador ou hipótese exigirá novo pré-registro e novas sementes de
teste; resultados de teste nunca serão usados para escolher outro `σ̄`.

## Métodos e orçamento de ajuste

O método em teste é a implementação da `MemoriaDeRanhuras` congelada na tag
`v0.4-exp6` (commit `f1aa186`), com câmaras, deslocamento global e busca dos 20
pares `(w0, eta_min)` já usados no experimento 6. O algoritmo da memória não
será alterado neste experimento.

Comparadores:

- NCM sem ajuste e NCM com deslocamento global, como referências fixas;
- kNN com `k ∈ {1,3,5,7,9,11,13,15,17,19}` e pesos uniforme ou por distância;
- centro por identidade-contexto, com retração `λ` em 20 valores igualmente
  espaçados entre 0 e 1;
- MLP com `hidden ∈ {32,64,128,256,512}` e
  `alpha ∈ {1e-5,1e-4,1e-3,1e-2}`;
- Gaussian Naive Bayes, com priors uniformes entre as 50 classes e 20 valores de
  `var_smoothing` igualmente espaçados em escala logarítmica de `1e-12` a `1e-1`;
- centro-contexto com variância isotrópica por identidade, retração do centro
  (`λ`) e retração da variância (`κ`), com 20 pares de configuração.

Definição do baseline de variância por identidade:

1. Estimar o deslocamento global de cada contexto usando apenas amostras de
   treino com rótulos conhecidos e observações na referência e no contexto.
2. Para cada identidade, calcular o centro do contexto final como
   `μ_ic = (1−λ)(μ_i0 + ĝ_c) + λ x̄_ic` quando há observações locais; sem
   observações locais, usar `μ_i0 + ĝ_c`.
3. Estimar a variância residual escalar `v_i` pela soma dos quadrados dos
   resíduos em torno das médias identidade-contexto, dividida por `D` vezes os
   graus de liberdade residuais. Estimar `v_global` da mesma forma, agrupando
   identidades. Usar somente amostras de treino.
4. Aplicar retração `v_iκ = (1−κ)v_i + κ v_global`. Se uma identidade não tiver
   graus de liberdade residuais, usar `v_global`; aplicar piso numérico fixo
   `1e-12`.
5. Classificar pela menor pontuação gaussiana isotrópica
   `D log(v_iκ) + ||x − μ_ic||² / v_iκ`, omitindo constantes comuns.

Usar `λ ∈ {0, 0,25, 0,5, 0,75, 1}` e
`κ ∈ {0, 1/3, 2/3, 1}`, totalizando 20 configurações. Para cada família ajustável,
usar o mesmo conjunto de 30 sementes de calibração e o mesmo orçamento de 20
configurações. Os comparadores fixos não têm busca. Toda decisão de parâmetros,
inclusive o baseline vencedor, usa apenas calibração.

GaussianNB é incluído como referência conhecida que estima variâncias por
característica e classe. O baseline isotrópico com retração é específico deste
estudo; não será descrito como método padrão.

O melhor baseline é a família/configuração com maior acurácia média na condição
primária, entre todos os comparadores acima. Em caso de empate exato, usar a
ordem fixa listada nesta seção. O baseline e a configuração das câmaras serão
salvos em `configuracao-congelada.json` antes do teste.

## Sementes e tamanho do teste

- Desenvolvimento: `7000–7015`, queimadas e excluídas de qualquer análise
  confirmatória.
- Calibração e seleção do nível `σ̄`: `8000–8029`.
- Teste confirmatório: sementes consecutivas a partir de `9000`, com `n` fixado
  antes da primeira execução.
- Grade exploratória: `10000–10009`, independente das sementes anteriores.

Após selecionar a configuração e o baseline na calibração, calcular `s_Δ`, o
desvio padrão entre sementes das diferenças pareadas de calibração. Planejar
`n = min(100, max(30, ceil((1,96 · s_Δ / 0,015)²)))`, usando acurácias como
proporções. O alvo é uma meia-largura aproximada de 1,5 ponto percentual para
um IC95% da média de `Δ`; a fórmula é de planejamento, não garantia da largura
do bootstrap. `n` e `s_Δ` serão registrados antes do teste. Se `n` atingir 100 e
a precisão observada for pior que o alvo, relatar essa limitação sem acrescentar
sementes após consultar o teste.

## Métrica e análise confirmatória

A métrica primária é a acurácia média por identidade-alvo na condição primária.
Para cada semente de teste, calcular
`Δ = acurácia_câmaras − acurácia_melhor_baseline_calibração`, usando exatamente
os mesmos dados gerados para ambos os métodos.

Calcular média de `Δ` e IC95% percentil por bootstrap pareado de sementes, com
10.000 reamostragens e semente do bootstrap fixa em `81`.

- **Confirmado:** limite inferior do IC95% de `Δ ≥ +0,05`.
- **Refutado quanto ao ganho mínimo:** limite superior do IC95% de `Δ < +0,05`.
- **Inconclusivo:** o IC inclui `+0,05`.
- **Não executável como confirmatório:** nenhum nível de `σ̄` passa o gate de
  margem na calibração.

Há uma única hipótese primária; portanto, não haverá correção de multiplicidade
para a decisão primária. Não haverá parada antecipada, extensão de sementes,
exclusão posterior ou troca de condição após abrir o teste.

## Grade exploratória e ablações

Com as configurações primárias congeladas, usar as sementes `10000–10009` para
avaliar a grade completa:

- `σ̄ ∈ {1,6; 2,0; 2,4}`;
- `h ∈ {0,35; 1,0}`;
- contextos `{2,4,8}`;
- força contextual `{0,4; 0,8; 1,2}`;
- exposições `{0,1,3,10}`.

Isso produz 216 células exploratórias. Avaliar também ablações sem largura
adaptativa, sem deslocamento e sem câmaras, mantendo os demais parâmetros
congelados. Reportar todas as células; zero exposições é uma análise separada.
Nenhum resultado da grade ou ablação será usado para confirmar ou resgatar a
hipótese primária. Qualquer alegação confirmatória secundária exigirá outro
pré-registro e sementes novas.

## Execução, rastreabilidade e relato

- Commit próprio deste pré-registro antes de calibração; enviar e integrar esse
  commit ao `master` antes de abrir sementes de calibração.
- Commit do código e da configuração congelada antes de abrir teste. O script
  aborta se a árvore Git estiver suja.
- Registrar resultados por semente, parâmetros, configuração, hash, estado Git,
  versões de Python e bibliotecas e sementes. Commitar cada JSON antes de uma
  nova execução.
- Não reescrever commits que forem referenciados pelos JSONs.
- Documentar em `LEIA.md` todos os desfechos, inclusive falha do gate,
  resultados negativos e resultados inconclusivos.

Este é um experimento sintético. Não testa dados reais, embeddings congelados,
memória autobiográfica ou hardware.

## Esclarecimentos pré-calibração

Este adendo foi registrado depois da integração do pré-registro original e antes
de qualquer execução de calibração. Ele torna operacionais escolhas que estavam
implícitas; não usa resultados de calibração ou teste.

### Gaussian Naive Bayes

Para cada episódio, calcular os deslocamentos globais por contexto com a mesma
função e os mesmos dados de treino usados pelos comparadores em
`experimentos/06/modelos.py::deslocamentos_globais`. Subtrair o deslocamento do
contexto de cada observação de treino e o deslocamento do contexto final de cada
consulta. Ajustar `GaussianNB` apenas nesses vetores corrigidos e rótulos de
treino, com prior uniforme explícito entre as classes presentes no treino. A
busca usa `np.geomspace(1e-12, 1e-1, 20)` para `var_smoothing`; nenhuma outra
configuração ou transformação será ajustada.

### Desvio padrão para dimensionar o teste

`s_Δ` é o desvio padrão amostral (`ddof=1`) dos 30 deltas pareados de calibração,
calculados com a configuração das câmaras e o melhor baseline já selecionados
pelas médias de calibração. Esse valor entra na fórmula de `n` já registrada;
não se reestima `n` com sementes de teste.

### Grade das câmaras e ablações

A grade das câmaras é o produto cartesiano
`w0 ∈ {0,08; 0,16; 0,32; 0,64; 1,28}` e
`eta_min ∈ {0,01; 0,02; 0,05; 0,10}`, como no pré-registro do Exp. 6.
Nas ablações exploratórias, usar a configuração da câmara congelada na célula
primária e avaliá-las apenas na célula primária, com as sementes exploratórias
`10000–10009`:

- **sem largura adaptativa:** `largura_adaptativa=False`, mantendo contextos e
  deslocamento aprendidos pela memória;
- **sem deslocamento:** `aprende_deslocamento=False`, mantendo as câmaras por
  contexto;
- **sem câmaras por contexto:** corrigir treino e consultas pelos deslocamentos
  globais calculados apenas com treino; alimentar todas as observações à memória
  com `ctx=0` e consultar com `ctx=0`, sem deslocamento interno. Assim a memória
  conserva uma câmara por identidade, sem armazenar câmaras separadas por
  contexto.
