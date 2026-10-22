# Índice dos experimentos

O projeto usa dois tipos de identificador: números para experimentos e nomes de
fase para etapas do roteiro de pesquisa. Eles não formam uma única sequência.

| Pasta | Conteúdo | Relação com o roteiro | Situação |
|---|---|---|---|
| `01` a `05` | Experimentos exploratórios originais | Estudos anteriores às fases atuais | Históricos; resultados não confirmatórios |
| `fase1` | Avaliação do prior adaptativo | Fase 1 — núcleo sem prior mágico | Executada; resultado inconclusivo |
| `06` | Contexto não aditivo | Fase 2 — experimento 6 | Executado; resultado não informativo por efeito de teto |
| `07` | Contexto heteroscedástico e câmaras isoladas | Estudo confirmatório independente; não testa a rede com ligações | Executado; ganho mínimo refutado na célula primária |
| `08` | Retorno rápido após esquecimento | Fase 3 — retorno rápido ("saudade") | Pré-registro e pipeline preparados; calibração pendente |
| `comum` | Código compartilhado, incluindo a implementação legada | Infraestrutura, não uma fase | Usado pelos wrappers dos experimentos 1 a 5 |

Por isso não existe uma pasta `fase2`: essa etapa do roteiro foi registrada como
experimento `06`. Os nomes atuais são mantidos para preservar referências a
resultados e commits. Experimentos novos recebem o próximo ID numérico livre;
cada `LEIA.md` deve indicar a fase do roteiro a que responde.

## Registros de execução

Os JSONs ficam em `resultados/execucoes/`. Um arquivo representa uma execução
ou análise, não necessariamente um experimento completo. O inventário e as
limitações de rastreabilidade estão em `resultados/README.md`.
