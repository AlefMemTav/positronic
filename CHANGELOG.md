# Changelog

Mudanças relevantes por versão. As tags apontam para os commits de integração
indicados em cada seção.

## Não lançado

- Adicionados testes unitários mecânicos para brotar, erosão, murchar e
  deslocamento, além de comandos `make install`, `make test` e `make run`.
- Definidos os requisitos mínimos da Fase 0 para iniciar novos experimentos;
  reexecuções e gráficos legados 3b/3c foram adiados sem alterar os resultados
  históricos.

## v0.4-exp6 — 2026-10-21

- Integrados a avaliação do prior adaptativo (Fase 1) e o experimento 6 de
  contexto não aditivo.
- Registrados o resultado inconclusivo da Fase 1 e o resultado não informativo
  do experimento 6, reclassificado por efeito de teto.
- Documentado o comportamento exploratório com zero exposições, a limitação dos
  hashes antigos e as regras de margem de manobra e rastreabilidade.
- Tag no commit de integração `f1aa186`.

## v0.3-json — 2026-10-21

- Adicionado o registro JSON por execução, com métricas por semente, metadados
  do ambiente e do Git, bootstrap pareado e uma função de correção de Holm.
- Adicionados testes para o módulo de registro. Os experimentos 1 a 5 não foram
  migrados para produzir esses JSONs e permanecem exploratórios.
- Tag no commit de integração `10f82ac`.

## v0.2-estrutura — 2026-10-21

- Reorganizados o núcleo e os experimentos 1 a 5 em módulos e pastas separados.
- Comparadas as saídas normalizadas antes e depois do refactor; as tabelas
  numéricas foram preservadas.
- Tag no commit de integração `0c49bce`.

## v0.1-prototipo — 2026-10-21

- Registrado o protótipo original no commit `22fa015`.
