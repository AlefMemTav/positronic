# Pré-registro — Experimento 6: contexto não aditivo

**Estado:** protocolo congelado antes do código do experimento e antes de
qualquer execução de suas sementes. A Fase 1 foi executada e documentada como
inconclusiva em `experimentos/fase1/LEIA.md`.

## Pergunta e hipótese

As câmaras por contexto melhoram o reconhecimento de identidades em um contexto
já conhecido globalmente, quando cada identidade tem um efeito de contexto
próprio, em comparação com o melhor baseline escolhido apenas na calibração?

Hipótese confirmatória: na célula primária, as câmaras têm ganho de pelo menos
5 pontos percentuais de acurácia sobre o melhor baseline de calibração.

## Gerador e tarefa

- Dimensão 64; 30 identidades de suporte vistas em todos os contextos e 20
  identidades-alvo vistas em contexto de referência e, em número variável, no
  contexto de teste. Cada identidade tem protótipo próprio, efeito de contexto
  global e efeito residual específico por identidade e contexto.
- Ruído por identidade é heteroscedástico, amostrado de lognormal com média
  marginal 0,8. A força do efeito residual controla quanto a transformação
  difere entre identidades.
- Em cada semente, protótipos vêm de `Mundo.pessoa()` do gerador histórico. Para
  cada contexto `c>0`, o deslocamento global é `N(0, 0.25² I)` e o efeito
  individual é `N(0, força² I)`. Contexto 0 tem ambos os deslocamentos iguais a
  zero. O ruído de cada
  identidade é `sigma_p = 0.8 * exp(N(-0.5*0.35², 0.35²))`.
- Usar `numpy.random.default_rng(semente)` para os efeitos e manter a geração
  determinística. Para cada identidade, observações são protótipo + deslocamento
  global + efeito individual + ruído isotrópico `N(0, sigma_p² I)`.
- Treino de suporte: 5 exemplos por identidade e contexto. Alvos: 3 exemplos no
  contexto de referência e `0, 1, 3 ou 10` exemplos no contexto final.
- Consulta: 50 amostras por identidade-alvo no contexto final. A acurácia inclui
  erro para uma identidade de suporte, pois todos os 50 rótulos são candidatos.
- Grade secundária: contextos `{2,4,8}` × exposições no contexto final
  `{0,1,3,10}` × força residual `{0.4,0.8,1.2}`. Célula primária única:
  4 contextos, 3 exposições e força 0,8.

## Métodos e ajuste

- Modelo: `MemoriaDeRanhuras` supervisionada com câmaras e deslocamento global.
- Baselines: NCM sem ajuste; NCM com deslocamento global; kNN (k e pesos
  variados); centro por identidade-contexto com retração ao deslocamento global;
  MLP com contexto codificado como entrada.
- Para cada família, selecionar até 20 configurações em sementes de calibração.
  Configurações congeladas: modelo usa o produto cartesiano `w0 ∈
  {0.08,0.16,0.32,0.64,1.28}` × `eta_min ∈ {0.01,0.02,0.05,0.10}`; kNN usa
  `k ∈ {1,3,5,7,9,11,13,15,17,19}` × pesos `{uniforme, distância}`; centro
  identidade-contexto usa 20 valores igualmente espaçados de retração de 0 a 1;
  MLP usa `hidden ∈ {32,64,128,256,512}` × `alpha ∈
  {1e-5,1e-4,1e-3,1e-2}`. Taxa de aprendizado do MLP é fixa em 0.001; os demais
  parâmetros não listados ficam nos padrões registrados no código. NCM sem
  ajuste e NCM com deslocamento global são dois comparadores fixos adicionais.
  O número de configurações tentadas e a escolha ficam registrados antes do
  teste.
- O baseline vencedor é a configuração com maior acurácia média na célula
  primária de calibração. O baseline escolhido e o modelo ficam congelados num
  `configuracao-congelada.json` versionado antes do teste.
- DP-means, ART e GNG não entram: a tarefa fornece identidade e mede
  classificação supervisionada, não descoberta de clusters. Replay e EWC não
  entram porque não há sequência de tarefas de treinamento de pesos.

## Sementes e análise

- Calibração: `4000–4029`. Teste confirmatório: `5000–5029`, uma única avaliação
  após congelar código e configuração. A grade secundária usa sementes
  independentes `6000–6009` e é exploratória.
- Métrica primária: acurácia média das consultas das identidades-alvo na célula
  primária. Calcular `Δ = acurácia das câmaras − acurácia do baseline congelado`
  por semente e IC95% bootstrap pareado com 10.000 reamostragens de sementes.
- Confirmado se o limite inferior do IC de Δ ≥ +0,05; refutado como ganho
  relevante se o limite superior < +0,05; caso contrário, inconclusivo.
- As demais células são exploratórias; não serão usadas para resgatar a hipótese
  principal. Correção de Holm só será aplicada a qualquer conjunto de alegações
  secundárias que venha a ser tratado como confirmatório.
- Nenhuma extensão de sementes é permitida após ver o teste. Bugs que invalidem
  a execução exigem registrar o incidente e pré-registrar sementes novas.

## Registro e conclusão

Salvar métricas por semente, parâmetros, versões, commit, estado Git, seeds e
configuração em JSON. Documentar a conclusão em `LEIA.md`, qualquer que seja o
resultado. A execução não testa dados reais, lembrança autobiográfica ou
ressonância física.
