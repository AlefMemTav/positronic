# Registro de decisões

## 2026-10-21 — preservar o protótipo inicial

- O commit `22fa015` é a referência imutável `v0.1-prototipo`.
- Experimentos 1 a 5 permanecem exploratórios; seus números não sustentam
  alegações confirmatórias.
- O README e os documentos existentes não serão alterados sem autorização.
- A estrutura e a coleta de resultados serão adicionadas em arquivos novos.
- A versão do Python fica em `.python-version`; dependências diretas ficam
  fixadas em `requirements.txt`.

## 2026-10-21 — ordem experimental

- A Fase 0 de `docs/04-proximos-passos.md` precede mudanças no algoritmo.
- A Fase 1 (calibração de `w0` e `z_max`) precede a Fase 2 (experimento 6),
  conforme o próprio roteiro, que declara as duas fases como pré-requisitos.
- O refactor estrutural deve preservar as tabelas dos experimentos 1 a 5;
  campos variáveis, como tempo de execução, não fazem parte da comparação.

## 2026-10-21 — inferência do experimento confirmatório

- Comparações usam diferenças pareadas por semente e IC de bootstrap dessa
  diferença.
- O melhor baseline e seus hiperparâmetros são escolhidos apenas nas sementes
  de calibração e ficam congelados antes da avaliação de teste.
- O número de sementes de teste é fixado antes de abrir os resultados. Não se
  acrescentam sementes após inspeções intermediárias usando IC convencional.
- Se houver mais de uma hipótese primária, a família confirmatória inteira
  recebe correção de multiplicidade. Células secundárias são exploratórias.

## 2026-10-21 — organização e registros após v0.4

- Os números das pastas identificam experimentos; as fases são etapas do
  roteiro. Mantêm-se os caminhos históricos: `experimentos/fase1` para o prior
  adaptativo e `experimentos/06` para o contexto não aditivo, correspondente à
  Fase 2.
- Cada JSON em `resultados/execucoes/` representa uma execução. Os experimentos
  1 a 5 permanecem exploratórios e não serão migrados retroativamente para o
  registrador.
- Os JSONs existentes não serão editados para substituir hashes ausentes. A
  correspondência inferida e a execução exploratória com árvore suja permanecem
  identificadas como limitações.
- Na revisão inicial, a Fase 0 foi classificada como parcialmente concluída.
  A decisão posterior abaixo define o escopo mínimo de entrada e os itens
  legados adiados.

## 2026-10-21 — escopo mínimo da Fase 0

- Para iniciar um novo experimento, a Fase 0 exige testes mecânicos do núcleo e
  comandos reproduzíveis de instalação, teste e execução. O `Makefile` oferece
  esses comandos.
- Reexecuções das varreduras 3b/3c, seus gráficos e a instrumentação dos
  experimentos 1 a 5 ficam adiados; não são requisitos para o experimento 7.
- “Não migrar retroativamente” significa que não se criam JSONs para resultados
  históricos resumidos. Uma reexecução futura pode produzir um registro novo,
  rotulado como exploratório e com sua própria proveniência; ela não substitui
  nem altera o resultado histórico.
- A comparação da Fase 1 com parâmetros históricos e sementes novas é evidência
  exploratória adicional. Não corrige a seleção de parâmetros feita nas
  varreduras originais 3b/3c.
