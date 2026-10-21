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
