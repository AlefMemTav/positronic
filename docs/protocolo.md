# Protocolo experimental

Este protocolo aplica-se aos experimentos novos. Os experimentos 1 a 5 são
exploratórios e seus resultados históricos não serão reclassificados como
confirmatórios.

## Pré-registro e histórico

Antes de executar um experimento confirmatório, registrar em arquivo versionado
e em commit próprio: pergunta, hipótese, gerador/dados, divisões, baselines,
busca de hiperparâmetros, métrica primária, células primárias, efeito mínimo,
regra de exclusão, sementes e análise estatística. Esse commit precisa anteceder
a execução das sementes de teste. Explorações de desenvolvimento devem usar
somente calibração.

## Calibração e teste

- Usar fluxos independentes de sementes para calibração e teste.
- Ajustar hiperparâmetros, escolher o melhor baseline e definir o orçamento de
  memória apenas com calibração.
- Congelar a configuração antes de avaliar teste. O teste não pode orientar
  seleção de modelo, parâmetros ou células a reportar.
- Reservar também configurações do gerador fora das usadas no desenvolvimento.
- Registrar o número de sementes antes do teste. Não aumentar a amostra após
  consultar resultados intermediários usando intervalos convencionais. Se uma
  análise sequencial for necessária, seu método de controle de erro e regra de
  parada devem ser pré-registrados.

## Comparações e estatística

- Usar os mesmos dados de teste por semente para os métodos comparados.
- Definir a diferença pareada por semente: `Δ = métrica do modelo − métrica do
  baseline selecionado na calibração`.
- Reportar média de Δ e IC95% por bootstrap das sementes, com pelo menos 10.000
  reamostragens. Sementes, e não observações individuais, são a unidade de
  reamostragem.
- Para um efeito mínimo relevante de 5 pontos percentuais: confirmado se o
  limite inferior do IC de Δ for ≥ +0,05; refutado se o limite superior for
  < +0,05; caso contrário, inconclusivo.
- Fixar uma única célula primária sempre que possível. Se houver várias,
  corrigir a família de testes confirmatórios pelo método de Holm. Resultados
  secundários são descritos como exploratórios.
- Planejar o tamanho da amostra usando poder/precisão na calibração ou literatura
  relevante; 30 sementes é um ponto de partida, não uma garantia de poder.

## Baselines e orçamento

Dar a cada método o mesmo número pré-registrado de configurações de busca e os
mesmos dados de calibração. Justificar a faixa de busca por método. Comparar
somente métodos compatíveis com a tarefa: protótipos (NCM, NCM com o mesmo
ajuste de contexto), instâncias (kNN), agrupamento incremental (online k-means,
DP-means ou ART) e MLP ajustado. GNG, replay e EWC entram quando a pergunta e o
desenho realmente os tornam comparáveis; não são baselines obrigatórios por
mera disponibilidade.

## Ablações, resultados e rastreabilidade

- Desligar cada componente relevante, mantendo o restante fixo.
- Arquivar resultados positivos, negativos e inconclusivos.
- Registrar por execução parâmetros, métricas por semente, commit, estado
  versionado ou sujo, versões de Python e bibliotecas e identificador das
  sementes.
- O critério de parada do projeto é o descrito em `docs/04-proximos-passos.md`.

## Margem de manobra (aplicável a partir do experimento 7)

- Definir `H = 1 − métrica do melhor baseline` na calibração, na célula
  primária (para acurácia; para outras métricas, definir o equivalente no
  pré-registro).
- Exigir `H ≥ 2 × efeito mínimo relevante` (0,10 para um efeito de 5 pontos),
  verificado e registrado **antes** de congelar a configuração.
- Se a condição não for satisfeita, o experimento é declarado "não executável
  como confirmatório": nenhuma semente de teste é aberta, e o gerador ou a tarefa
  é redesenhado e pré-registrado de novo.
- O rótulo "refutado" só vale se a condição também for satisfeita no teste; caso
  contrário, a decisão é "não informativo". Isso não afeta "confirmado", pois um
  ganho confirmado demonstra que havia margem.
- O experimento 6, anterior a esta regra, foi reclassificado como "não
  informativo" na errata de `experimentos/06/LEIA.md`.

## Rastreabilidade e histórico

- Depois que um commit é citado por um registro JSON, não reescrever o histórico
  (rebase, amend, force-push) de branches que o contenham. Se for inevitável,
  incluir no `LEIA.md` do experimento, antes do merge, a tabela de hashes
  antigos e atuais, sem editar os JSONs.
- Enviar ao remoto os commits de pré-registro e de congelamento antes de abrir
  as sementes de teste.
- A partir do experimento 7, o script de teste deve abortar se houver alterações
  locais não commitadas; o JSON de cada execução é commitado antes da execução
  seguinte.
- A função `holm` de `registro.py` opera sobre p-valores, e as decisões atuais
  usam intervalos de bootstrap. Ela só se aplica a análises que produzam p-valores
  pré-registrados; até lá, a multiplicidade se controla fixando uma única célula
  primária.
