# Experimento 8 — retorno rápido após esquecimento

**Fase do roteiro:** Fase 3.
**Estado:** calibração concluída; não executável como estudo confirmatório.

O pré-registro está em `PREREGISTRO.md`. A calibração usou as 30 sementes
reservadas (`12000–12029`) em checkout limpo no commit `da4b2a6`. Nenhuma
semente de teste foi aberta. O estado no topo do pré-registro descreve o momento
em que ele foi registrado e foi mantido como parte do registro histórico.

## Fluxo previsto

1. Pré-registrar a tarefa, os gates e as sementes antes da calibração.
2. Em checkout limpo, executar `python3 experimentos/08/calibrar.py`.
3. Versionar a configuração e o registro da calibração.
4. Abrir sementes de teste somente se `executavel_confirmatorio` for `true` e a
   configuração congelada estiver commitada.

## Resultado da calibração

Nenhum dos quatro valores candidatos de `σ` passou todos os gates
pré-registrados. O recall médio do alvo antes da expulsão excedeu o limite
superior elegível de `0,98` em todos eles; o valor mais próximo foi `σ = 1,2`,
com `0,984`. A tabela resume também o `E90` médio do baseline Apagar:

| `σ` | Recall médio antes da expulsão | `E90` médio de Apagar | Gates |
|---:|---:|---:|---|
| 0,6 | 1,0000 | 1,000 | Falhou |
| 0,8 | 1,0000 | 1,100 | Falhou |
| 1,0 | 0,9973 | 2,000 | Falhou |
| 1,2 | 0,9840 | 3,467 | Falhou |

O estudo fica **não executável como confirmatório**, conforme a regra do
pré-registro. `configuracao-congelada.json` registra
`executavel_confirmatorio: false`, sem `σ` primário nem tamanho de teste. Não
foram executadas nem analisadas sementes de teste. Isso não confirma nem refuta
se um traço comprimido acelera o reaprendizado; indica apenas que nenhum regime
calibrado atendeu à condição de elegibilidade fixada antes da calibração.

Os artefatos são `configuracao-congelada.json` e
`resultados/execucoes/08-calibracao-1c198ad8-1cbb-4c30-9d3d-513729e66754.json`.
Uma alteração de gerador ou dos gates exige novo pré-registro e novas sementes;
os resultados desta calibração permanecem registrados.
