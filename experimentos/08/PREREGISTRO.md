# Pré-registro — Experimento 8: retorno rápido após esquecimento

**Fase do roteiro:** Fase 3 — retorno rápido ("saudade").
**Estado:** pré-registro e pipeline preparados; calibração, teste e resultados
pendentes. Nenhuma semente de calibração ou teste foi executada.
**Versão avaliada:** núcleo da tag `v0.5-exp7`, sem alteração.

## Pergunta e hipótese

Depois que uma ranhura é removida da memória ativa por falta de orçamento, um
traço comprimido da ranhura permite recuperar o desempenho de classificação com
pelo menos 30% menos exposições rotuladas do que reaprender após apagamento
completo?

A hipótese diz respeito a esta tarefa sintética, representação e orçamento. Um
resultado positivo não demonstrará um mecanismo biológico nem novidade em
relação a todo tipo de cache ou memória externa.

## Tarefa e gerador

Cada episódio tem 16 classes ativas, vetores de 64 dimensões e uma classe
adicional usada para provocar uma expulsão. Os protótipos são gerados pelo
`Mundo.pessoa()` do código legado; as observações seguem o gerador
`Mundo.amostras()` com ruído gaussiano isotrópico. Todos os métodos recebem as
mesmas observações, na mesma ordem, para cada semente.

1. Aprender 8 observações rotuladas de cada uma das 16 classes.
2. Deixar a classe-alvo (rótulo 0) sem novas observações enquanto se apresentam
   20 ciclos de uma observação para cada uma das outras 15 classes.
3. Apresentar uma classe nova. O orçamento de 16 ranhuras força uma expulsão;
   a calibração só prossegue se o método `murchar` tiver removido o alvo em
   todas as sementes de calibração.
4. Apresentar mais 5 ciclos das 15 classes restantes para que o traço envelheça.
5. Reintroduzir o alvo em até 30 exposições rotuladas. Após cada exposição do
   alvo, apresentar uma observação de cada classe restante para manter o mesmo
   fluxo de interferência.
6. Depois de cada exposição do alvo, medir o recall do alvo em 50 consultas
   independentes dessa classe. As consultas das outras 15 classes permitem
   calcular acurácia balanceada como métrica secundária. Consultas nunca são
   usadas para atualizar o modelo ou escolher parâmetros.

O desvio padrão do ruído `σ` será escolhido apenas na calibração, na ordem
`{0,6; 0,8; 1,0; 1,2}`. O primeiro valor que satisfizer todos os gates abaixo
será a única condição primária. Nenhuma condição será escolhida com sementes de
teste.

## Métodos e orçamento de memória

- **Apagar (baseline primário):** `MemoriaDeRanhuras` v0.5, `max_ranhuras=16`,
  política `murchar`, `tau=300`; a ranhura removida é descartada.
- **Traço (método em teste):** mesmos parâmetros e orçamento ativo. Ao ocorrer
  uma expulsão, guardar um resumo em precisão reduzida. Cada resumo
  contém o rótulo como chave, centro `float16`, largura `float16`, contador de
  ecos, vigor e instante de armazenamento. O vigor do traço começa em 1 e decai
  por `exp(-idade/tau_traco)`; o traço deixa de ser elegível abaixo de `0,05`.
  Ao retornar um rótulo elegível, restaurar o centro e a largura multiplicada
  por `fator_largura`; usar `peso_prior` como contagem efetiva para a erosão
  inicial. O orçamento de traços é de um resumo.
- **Cache comprimido (controle secundário):** mesmo limite de um resumo e
  mesma representação em precisão reduzida, mas sem decaimento e restauração
  direta do contador de ecos e da largura. É uma referência de cache simples;
  não será usada para a decisão confirmatória principal.
- **Manter tudo (teto descritivo):** sem limite de ranhuras; serve para medir o
  desempenho sem expulsão e não é comparado sob o mesmo orçamento de memória.

Os três parâmetros do traço serão escolhidos em uma grade fixa de 18
configurações:

- `tau_traco ∈ {150, 300, 600}` eventos;
- `peso_prior ∈ {4, 8, 16}` observações efetivas;
- `fator_largura ∈ {1, 2}`.

Escolher a configuração com maior economia relativa média na calibração; em
empate, vence a primeira na ordem acima. O fluxo de dados e os hiperparâmetros
do núcleo v0.5 são idênticos entre condições.

## Gates de executabilidade na calibração

Para cada valor candidato de `σ`, executar o baseline Apagar nas 30 sementes de
calibração. Selecionar o primeiro valor que satisfizer simultaneamente:

- recall médio do alvo antes da expulsão entre `0,70` e `0,98`;
- o alvo foi expulso em todas as sementes;
- o baseline recuperou o limiar em todas as sementes dentro de 30 exposições;
- média de exposições do baseline para recuperação de pelo menos `2`.

Se nenhum valor passar, declarar **não executável como confirmatório** e não
abrir sementes de teste. Não alterar gerador, gates ou hipótese depois de
consultar qualquer semente de teste; uma mudança requer novo pré-registro e
novas sementes.

## Métrica e decisão

Para cada método e semente, `E90` é o número de exposições do alvo necessárias
para o recall do alvo atingir pelo menos 90% do recall medido antes da expulsão.
O recall do alvo é a métrica primária: sem uma ranhura ativa com o rótulo-alvo,
esse recall é zero, mesmo que as outras classes continuem corretas. A acurácia
balanceada nas 16 classes é secundária. Se o limiar não for atingido em 30
exposições, registrar `E90=31`, custo fixo de falha dentro do horizonte
pré-definido. A unidade estatística é a semente.

A métrica primária por semente é a economia relativa do traço contra apagamento:

`R = 1 − E90_traco / E90_apagar`.

Calcular média e IC95% percentil de `R` por bootstrap pareado de sementes, com
10.000 reamostragens e semente do bootstrap `81`.

- **Confirmado:** limite inferior do IC95% de `R ≥ 0,30`.
- **Refutado quanto ao efeito mínimo:** limite superior do IC95% de `R < 0,30`.
- **Inconclusivo:** o IC95% inclui `0,30`.
- **Não executável:** nenhum `σ` passa os gates de calibração.

O cache comprimido e a condição Manter tudo serão reportados como referências
secundárias descritivas; não gerarão hipóteses confirmatórias adicionais.

## Sementes, precisão e rastreabilidade

- Desenvolvimento: `11000–11015`, reservadas; nenhuma foi executada até este
  pré-registro. Se usadas em piloto, todas serão documentadas e queimadas.
- Calibração: `12000–12029`.
- Teste: sementes consecutivas a partir de `13000`, com `n` congelado após a
  calibração.
- Dimensionar `n = min(100, max(30, ceil((1,96 · s_R / 0,10)²)))`, em que
  `s_R` é o desvio padrão entre sementes da economia relativa da configuração
  escolhida na calibração. O alvo de planejamento é meia-largura aproximada de
  0,10 no IC95%; a fórmula não garante a largura do bootstrap.
- Não haverá parada antecipada, extensão de amostra após consultar o teste,
  exclusão posterior de sementes ou troca de célula primária.
- O código abortará se houver alterações locais antes da calibração ou do teste;
  o teste exige configuração congelada e commit de calibração ancestral.
- Registrar métricas por semente, configuração, sementes, commit de início,
  estado da árvore, versões e fingerprint do código.

## Limites de interpretação

O baseline Apagar testa se reter informação ajuda em relação a apagá-la. O
controle Cache verifica se o benefício aparente é apenas o efeito conhecido de
guardar um protótipo comprimido. A decisão confirmatória principal responde à
pergunta pré-registrada contra apagamento; ela não estabelece superioridade
sobre caches em geral. O estudo usa dados sintéticos e rótulos disponíveis nas
exposições de reaprendizado.
