# Changelog

Mudanças relevantes por versão. As tags apontam para os commits de integração
indicados em cada seção.

## Não lançado

- Documentados os resultados confirmatórios e exploratórios do experimento 7,
  seus limites de interpretação e o estado atualizado do roteiro.
- Registrado em `docs/02-teoria.md` um levantamento focal preliminar de trabalhos
  relacionados; a revisão sistemática e qualquer afirmação de novidade seguem
  pendentes.
- Atualizado o índice de experimentos e corrigidas referências antigas de
  estrutura e escopo nos documentos de resultados e próximos passos.
- Adicionados testes unitários mecânicos para brotar, erosão, murchar e
  deslocamento, além de comandos `make install`, `make test` e `make run`.
- Definidos os requisitos mínimos da Fase 0 para iniciar novos experimentos;
  reexecuções e gráficos legados 3b/3c foram adiados sem alterar os resultados
  históricos.

## v0.5-exp7 — 2026-10-21

- Concluído o experimento 7: na condição primária, as câmaras tiveram acurácia
  0,7928 contra 0,8664 do baseline ajustado; `Δ = −7,36` pp, IC95%
  `[−8,50; −6,22]` pp. O ganho mínimo de 5 pp foi refutado nessa condição.
- Registrada uma grade exploratória de 216 células e as ablações, sem usá-las
  para alterar a conclusão confirmatória.
- A tag aponta para o commit de integração `d46475a`.

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
