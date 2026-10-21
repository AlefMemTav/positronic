# Modelo de organização dos experimentos

Os números das pastas identificam experimentos; os nomes "Fase 1", "Fase 2" e
assim por diante identificam etapas do roteiro em `docs/04-proximos-passos.md`.
O mapa da organização existente está em `experimentos/README.md`.

Cada experimento novo recebe o próximo ID numérico livre e uma pasta própria,
com:

- `LEIA.md`: pergunta, instruções, resultado e conclusão, inclusive quando
  negativa ou inconclusiva;
- `PREREGISTRO.md` ou seção equivalente versionada antes das sementes de teste;
- um ou mais scripts de execução. Um experimento em duas etapas pode usar, por
  exemplo, `calibrar.py` e `run_teste.py`; não é obrigatório ter um único
  `run.py`;
- configuração explícita de sementes, hiperparâmetros e versão do gerador.

Código compartilhado fica em `experimentos/comum/`. Cada execução que usar o
registrador grava um JSON em `resultados/execucoes/`; esse arquivo registra uma
execução, não necessariamente um experimento inteiro. O índice dos registros e
as limitações dos dados históricos estão em `resultados/README.md`. Os
experimentos 1 a 5 são históricos e exploratórios; não são migrados
retroativamente. Ver `docs/protocolo.md`.
