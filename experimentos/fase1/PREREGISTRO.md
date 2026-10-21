# Pré-registro — Fase 1: prior de largura sem escala fixa

**Estado:** registrado antes da implementação e execução. O commit deste arquivo
deve anteceder o primeiro acesso aos resultados das sementes de teste.

## Pergunta e hipótese

Uma regra única, baseada na distribuição qui-quadrado e em distâncias locais
estimadas sem rótulos, consegue substituir os valores fixos `w0=0.32` e
`z_max=2.0` na descoberta das 20 classes sintéticas em ruído
`σ ∈ {0.3, 0.4, 0.5}`?

Hipótese: a regra adaptativa terá ARI médio ≥ 0,95 em cada escala de ruído e
manterá o número médio de grupos entre 18 e 22, sem escolher parâmetros por
escala.

## Método congelado

- Usar o gerador histórico do experimento 3: 20 classes, 15 observações por
  classe, dimensão 64, ordem aleatória e `Mundo` da versão registrada em
  `v0.1-prototipo`.
- Dividir por sementes: calibração `1000–1029`; teste `2000–2029`. Cada semente
  de teste é executada uma vez depois que o código e a regra forem congelados.
- Em cada fluxo, usar o primeiro terço das observações **sem rótulos** para
  estimar `w0`; agrupar o restante. A estimativa é a mediana da distância
  quadrática média até o 3º vizinho dividida por `χ²_64(0.75)/64` (aproximação
  pré-fixada para quatro outros exemplos da mesma classe no prefixo).
- Fixar `z_max = χ²_64(0.99)/64`; não ajustar por `σ`.
- Comparadores: implementação histórica (`w0=0.32`, `z_max=2.0`) e k-means com
  `K=20` conhecido. O k-means é referência de agrupamento, não concorrente sem
  informação equivalente.
- Métricas: ARI no sufixo agrupado e número de grupos produzidos. A métrica
  primária é o pior ARI médio entre as três escalas. Para IC, reamostrar as 30
  sementes em bloco, mantendo juntas as três escalas.

## Decisão e falsificação

- Sucesso: limite inferior do IC95% bootstrap do pior ARI médio ≥ 0,95 **e**
  número médio de grupos entre 18 e 22 em cada escala.
- Refutação prática: limite superior do IC95% do pior ARI médio < 0,95.
- Qualquer outro resultado é inconclusivo. Não haverá aumento adaptativo do
  número de sementes após consulta aos resultados.
- Se a regra falhar, registrar o resultado e não alterar este pré-registro; uma
  nova regra exige um experimento separado, com novas sementes de teste.

## Reprodutibilidade

O registro JSON deve incluir todos os valores por semente, configuração, versões
das bibliotecas, commit e condição limpa/suja do Git. Resultado negativo também
será mantido. Os experimentos 1 a 5 continuam classificados como exploratórios.
