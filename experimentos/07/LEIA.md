# Experimento 7 — estado e execução

**Estado:** calibração e teste confirmatório concluídos; grade exploratória ainda
pendente. O PR do pipeline e o PR da calibração foram integrados antes do teste.

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
Nenhuma semente exploratória foi executada. A grade e as ablações continuam
pendentes e não alteram o desfecho primário.
