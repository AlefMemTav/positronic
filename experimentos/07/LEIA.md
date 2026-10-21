# Experimento 7 — estado e execução

**Estado:** pipeline implementado; nenhuma calibração, semente de teste ou grade
exploratória foi executada por este código. O experimento só começa depois que o
PR do pipeline for revisado e integrado.

## Etapas após a integração do código

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

## Resultados

Ainda não há resultado confirmatório. Após as execuções autorizadas pelo
pré-registro, registrar aqui a condição selecionada, o baseline, o tamanho
amostral, `Δ`, IC95%, desfecho, limites de rastreabilidade e resultados
exploratórios, incluindo resultados negativos ou falhas do gate.
