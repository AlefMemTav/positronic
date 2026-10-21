# Experimento 7 — estado e execução

**Estado:** calibração, teste confirmatório e grade exploratória concluídos. O PR
do pipeline e o PR da calibração foram integrados antes do teste; os resultados
confirmatórios foram integrados antes da grade.

## Fluxo previsto

1. Em checkout limpo, executar `python3 experimentos/07/calibrar.py`.
2. Revisar e versionar `experimentos/07/configuracao-congelada.json` e o registro
   `07-calibracao-*.json`. Se `executavel_confirmatorio` for `false`, parar; o
   script de teste recusará abrir sementes.
3. Com os artefatos de calibração commitados, executar
   `python3 experimentos/07/run_teste.py`. O script exige árvore limpa, verifica
   o fingerprint do protocolo e do código, grava cada semente uma vez e impede
   repetir uma execução que já tenha começado.
4. Revisar e versionar todos os registros `07-primario-*.json`. Só então executar
   `python3 experimentos/07/run_grade.py` em checkout limpo.
5. Revisar e versionar registros por semente `07-grade-semente-*.json` e o resumo
   `07-grade-exploratoria-*.json`.

O teste usa as sementes consecutivas a partir de `9000`, com quantidade definida
pela calibração. A grade usa `10000–10009`, cobre as 216 células e avalia as três
ablações apenas na célula primária. A análise de zero exposições deve ser relatada
separadamente. Nenhum resultado exploratório muda o desfecho primário.

## Resultado confirmatório

Na célula primária pré-registrada (σ̄=2,0; heterogeneidade 1,0; quatro contextos;
três exposições; força 0,8), as câmaras tiveram acurácia média de 0,7928, contra
0,8664 do baseline `variancia_identidade` (λ=0,75; κ=0,0). A diferença pareada
foi `Δ = −0,0736` (−7,36 pontos percentuais), com IC95% bootstrap de
[−0,0850; −0,0622]. Pelo critério pré-registrado — refutado quando o limite
superior do IC fica abaixo de +5 pontos percentuais — o resultado é **refutado**
para esta célula primária. A conclusão não se estende automaticamente a outros
regimes do gerador.

A calibração selecionou σ̄=2,0 como primeiro valor que passou o gate
`H_cal ≥ 0,10` (`H_cal=0,1094`); σ̄=1,6 não passou (`H_cal=0,0712`). O tamanho
amostral foi fixado em 30 sementes. O teste usou as sementes 9000–9029. O
registro agregado e os 30 registros por semente estão em
`resultados/execucoes/07-primario-*.json`; a calibração e a configuração congelada
também estão registradas nessa pasta e em `configuracao-congelada.json`.

O teste começou com árvore limpa no commit `39cd19f`. Os registros por semente
marcam `alteracoes_locais: true` porque o próprio processo grava esses arquivos
durante a execução; `commit_no_inicio` preserva o commit limpo do código usado.

## Grade exploratória

A grade usou dez sementes (`10000–10009`) em 216 células. A média de Δ das câmaras
menos o baseline, agregada descritivamente pelas 54 células de cada número de
exposições e pelas dez sementes, foi:

| Exposições | Δ médio |
| ---: | ---: |
| 0 | +0,8 pp |
| 1 | +3,3 pp |
| 3 | −9,5 pp |
| 10 | −5,0 pp |

Essas médias resumem uma grade heterogênea; não são testes confirmatórios nem
intervalos de confiança. A célula de zero exposições foi mantida separada e ficou
próxima de paridade em média, embora haja variação entre as demais condições.
As maiores médias de Δ ocorreram com uma exposição, heterogeneidade 0,35, dois
contextos e força 0,4 (entre +20,7 e +24,6 pp conforme σ̄). Os valores mais
negativos apareceram sobretudo com três exposições, oito contextos e
heterogeneidade 0,35 (até −20,7 pp). Esses extremos são exploratórios e não
alteram o resultado primário.

Na ablação descritiva da célula primária, a acurácia média foi 0,6855 sem largura
adaptativa, 0,8146 sem deslocamento e 0,8735 sem câmaras por contexto. A versão
completa teve 0,8137 e o baseline 0,8823 nas mesmas dez sementes exploratórias.
Assim, a comparação das ablações é pareada por semente e descreve apenas essa
célula; não constitui um novo teste confirmatório. Os valores do teste
confirmatório de 30 sementes são apresentados separadamente acima.

O resumo agregado e os dez registros por semente estão em
`resultados/execucoes/07-grade-*.json`. Todos os achados da grade são
exploratórios; não mudam o desfecho confirmatório, que permanece refutado para a
célula primária pré-registrada.
