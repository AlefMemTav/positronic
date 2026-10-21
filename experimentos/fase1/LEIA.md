# Fase 1 — resultado

**Conclusão pré-registrada: inconclusiva.** A hipótese de ARI passou: o pior
ARI médio por semente nas três escalas foi 0,981, IC95% bootstrap [0,976;
0,985]. Porém, o número médio de grupos excedeu 22 em σ=0,3 (22,8), então a
regra conjunta de sucesso não foi satisfeita. O estimador não foi ajustado após
consultar o teste.

| σ | `w0` estimado | ARI adaptativo | Grupos adaptativos |
|---|---:|---:|---:|
| 0,3 | 0,181 ± 0,008 | 0,981 ± 0,013 | 22,8 ± 1,8 |
| 0,4 | 0,312 ± 0,012 | 0,992 ± 0,006 | 21,3 ± 1,2 |
| 0,5 | 0,477 ± 0,015 | 0,994 ± 0,006 | 21,1 ± 1,1 |

Os desvios são entre 30 sementes de teste, não ICs. Os dados por semente,
comparadores e parâmetros estão no JSON em `resultados/execucoes/`.

## Limites

- O prefixo não rotulado estima a escala, mas os seus exemplos não entram no
  agrupamento avaliado; o escore é medido no sufixo.
- O critério desta execução não testa toda a sensibilidade de `w0` a um erro de
  prior de fator quatro descrita em `docs/04-proximos-passos.md`. Isso requer um
  experimento pré-registrado separado; não foi inferido destes resultados.
- Um único gerador sintético não sustenta generalização para dados reais.
- Uma falha de serialização na primeira execução e o uso de sementes novas estão
  descritos em `ADENDO-1.md`.
