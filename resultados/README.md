# Registros de execução

`execucoes/` contém um JSON por execução registrada. Os registros não
substituem o `LEIA.md` do estudo, que interpreta os resultados e documenta suas
limitações.

## Inventário atual

| Arquivo | Estudo | Papel | Observação |
|---|---|---|---|
| `execucoes/fase1-prior-adaptativo-af3c2cae-0b0b-440b-bc6d-2aaa8f04fc12.json` | Fase 1: prior adaptativo | Execução principal | Resultado inconclusivo; árvore limpa no registro |
| `execucoes/06-contexto-nao-aditivo-primario-3c1abd3d-999e-455f-9581-73767b31f251.json` | Experimento 6 | Célula primária | Análise confirmatória reclassificada como não informativa por efeito de teto |
| `execucoes/06-contexto-nao-aditivo-grade-exploratoria-ec31c2c8-e3bb-4543-ab5c-c0fb04b35a5e.json` | Experimento 6 | Grade exploratória | 10 sementes; registro indica alterações locais (`alteracoes_locais: true`) |

Não há JSONs dos experimentos 1 a 5: eles são estudos legados exploratórios e
não foram migrados para usar o registrador. Portanto, não existem dois JSONs do
experimento 3; os dois registros com `06` no nome são do experimento 6.

## Limitações de rastreabilidade

Os três JSONs preservam os hashes que foram registrados na execução. Os hashes
da Fase 1 e do experimento 6 não estão mais presentes no histórico atual. O
`experimentos/06/LEIA.md` contém uma correspondência inferida para alguns deles;
ela não recupera nem comprova os objetos originais. Os JSONs são mantidos sem
alteração, e essa limitação deve acompanhar qualquer interpretação dos dados.

O JSON da grade exploratória foi gerado com alterações locais. Esse estado está
explicitado no próprio registro e no LEIA do experimento 6; não deve ser tratado
como uma execução confirmatória limpa.
