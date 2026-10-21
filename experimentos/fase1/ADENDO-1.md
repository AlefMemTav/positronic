# Adendo ao pré-registro da Fase 1 — replicação após falha de registro

**Registrado antes da nova avaliação de teste.** O código do estimador, os
parâmetros e os critérios do pré-registro original permanecem inalterados.

## Execução diagnóstica anterior

A execução com sementes de teste `2000–2029` terminou após imprimir os resumos,
mas antes de gravar JSON: um erro no argumento de sementes do registro associou
30 valores de teste a 60 sementes. Os resumos observados foram:

| σ | `w0` estimado | ARI adaptativo | grupos adaptativos |
|---|---:|---:|---:|
| 0,3 | 0,180 ± 0,005 | 0,983 ± 0,013 | 22,5 ± 1,8 |
| 0,4 | 0,308 ± 0,007 | 0,992 ± 0,007 | 21,3 ± 0,9 |
| 0,5 | 0,472 ± 0,011 | 0,989 ± 0,017 | 21,0 ± 0,7 |

O IC do pior ARI médio entre as três escalas foi [0,972; 0,985]. A regra de ARI
atingiu o limiar, mas o critério conjunto não passou porque o número médio de
grupos em σ=0,3 ficou acima de 22. Essa execução é preservada como diagnóstico,
sem reclassificação e sem ajuste de método.

## Replicação congelada

- Corrigir somente a ligação entre sementes e valores no serializador; nenhuma
  linha do estimador ou dos critérios muda.
- As sementes `2000–2029` deixam de ser usadas para inferência confirmatória,
  pois seus agregados já foram vistos.
- Repetir uma vez com sementes de teste `3000–3029`, mantendo calibração
  `1000–1029`, gerador, dados, métricas, métodos e critérios exatamente iguais.
- Não haverá novas mudanças de algoritmo após a replicação. Qualquer exploração
  posterior exige um pré-registro e sementes distintos.
