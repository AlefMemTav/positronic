# Experimento 6 — contexto não aditivo

O pré-registro está em `PREREGISTRO.md`. O código e a configuração de teste
congelada ficam nesta pasta. Execute nesta ordem:

1. `python experimentos/06/calibrar.py` com as sementes de calibração;
2. revise e versione `configuracao-congelada.json`;
3. execute `python experimentos/06/run_teste.py` uma vez para teste e grade
   exploratória.

Não altere a configuração depois de consultar o teste. Qualquer falha que exija
mudança no algoritmo deve ser registrada e usar sementes de teste novas. A
conclusão e os registros JSON devem ser adicionados aqui e em
`resultados/execucoes/`.

## Resultado

**Conclusão confirmatória:** refutado o ganho prático pré-registrado de pelo
menos 5 pontos percentuais para a célula primária (4 contextos, 3 exposições no
contexto final, força 0,8). Nas 30 sementes de teste, as câmaras tiveram
acurácia média 0,9994; o baseline congelado — centro por identidade-contexto
com retração 0,684 — teve 0,9979. A diferença pareada foi **+0,00147** (0,15
ponto percentual), IC95% bootstrap **[+0,00020; +0,00297]**. O limite superior
fica abaixo do efeito mínimo de +0,05.

Na calibração, a configuração escolhida para as câmaras foi `w0=0.08`,
`eta_min=0.01`; o centro por identidade-contexto venceu os outros baselines
ajustados. O NCM simples e o NCM com deslocamento tiveram médias de calibração
0,9963 e 0,9962. O desempenho próximo do teto deixa pouca margem e significa que
este gerador não criou uma condição em que os baselines fossem claramente
subótimos. Portanto, o resultado é evidência contra um ganho de 5 pontos nesta
tarefa sintética; não decide a hipótese mais ampla sobre memória contextual.

A grade secundária usou 10 sementes e é exploratória: em 35 células, o delta
médio variou de −0,699 a +0,055, com média −0,074 entre células. A maior média
foi +0,055 na célula com 8 contextos, 1 exposição e força 0,4; ela não confirma
uma vantagem, pois foi examinada como resultado exploratório e tem somente 10
sementes. Um teste confirmatório dessa condição exigiria pré-registro e novas
sementes.

## Arquivos de resultado

- `resultados/execucoes/06-contexto-nao-aditivo-primario-3c1abd3d-999e-455f-9581-73767b31f251.json`
- `resultados/execucoes/06-contexto-nao-aditivo-grade-exploratoria-ec31c2c8-e3bb-4543-ab5c-c0fb04b35a5e.json`
- A configuração selecionada só na calibração está em
  `configuracao-congelada.json`; os resumos e métricas por configuração estão
  preservados nesse arquivo.
