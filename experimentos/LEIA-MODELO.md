# Modelo de organização dos experimentos

Cada experimento novo fica em uma pasta numerada e contém:

- `LEIA.md`: pré-registro, instruções, resultado e conclusão, inclusive quando
  negativa ou inconclusiva;
- `run.py`: execução reproduzível, sem lógica compartilhada duplicada;
- configuração explícita de sementes, hiperparâmetros e versão do gerador.

Código compartilhado fica em `experimentos/comum/`. Resultados de execução são
gravados em `resultados/execucoes/` como JSON e não substituem arquivos
históricos. O commit de pré-registro deve existir antes de executar as sementes
de teste. Ver `docs/protocolo.md`.
