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
