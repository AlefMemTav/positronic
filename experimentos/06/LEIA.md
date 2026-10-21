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

## Errata e reclassificação (21/10/2026, revisão posterior à execução)

Esta errata não altera nenhum número nem nenhum JSON; corrige a leitura do
resultado acima. O texto original foi mantido.

### 1. O resultado é "não informativo" por efeito de teto

Na calibração (sementes 4000–4029), as câmaras tiveram 0,9994, o melhor
baseline 0,9968 e o NCM simples 0,9963. A margem de manobra máxima era de cerca
de 0,3 a 0,4 ponto percentual, de modo que um ganho de 5 pontos era impossível
antes de o teste ser aberto. O rótulo "refutado" decorre mecanicamente da regra
de decisão pré-registrada (limite superior do IC < +0,05), mas o teste não tinha
como confirmar a hipótese. Leitura correta: **não há evidência de ganho nesta
tarefa porque a tarefa não deixa espaço para ganho; nada se conclui sobre a
hipótese mais ampla.** Em toda a grade exploratória o menor desempenho médio do
baseline foi 0,909, então nenhuma célula tinha margem de 10 pontos. O protocolo
passa a exigir verificação de margem de manobra (ver `docs/protocolo.md`).

### 2. Comportamento com 0 exposições no contexto final

A grade exploratória (10 sementes, 35 células, exploratória) tem as perdas
concentradas nas 9 células com 0 exposições. Esta análise é posterior e
exploratória:

| Contextos | Força | Δ (câmaras − baseline) | baseline | câmaras |
|---:|---:|---:|---:|---:|
| 2 | 0,4 | +0,029 | 0,957 | 0,986 |
| 2 | 0,8 | −0,257 | 0,949 | 0,693 |
| 2 | 1,2 | −0,664 | 0,927 | 0,262 |
| 4 | 0,4 | +0,007 | 0,969 | 0,976 |
| 4 | 0,8 | −0,274 | 0,961 | 0,687 |
| 4 | 1,2 | −0,699 | 0,938 | 0,240 |
| 8 | 0,4 | +0,025 | 0,930 | 0,955 |
| 8 | 0,8 | −0,232 | 0,926 | 0,694 |
| 8 | 1,2 | −0,626 | 0,909 | 0,283 |

- Média do Δ nas células com 0 exposições: **−0,299**. Com 1, 3 e 10 exposições
  (26 células), o Δ médio é +0,009, +0,003 e +0,001, com mínimo −0,016 e máximo
  +0,055. A média geral de −0,074 citada acima é dominada pelas células de 0
  exposições; sem elas, a média é +0,004.
- Com 0 exposições o Δ piora à medida que o efeito individual cresce, e só é
  positivo na força 0,4.
- O mecanismo não foi diagnosticado. Hipótese não testada: sem dado no contexto
  final, a identidade-alvo só tem câmara no contexto de referência, enquanto as
  identidades de suporte têm câmara exata no contexto final; quando o efeito
  individual é forte, essas câmaras "roubam" as consultas da identidade-alvo. O
  baseline vencedor (centro por identidade-contexto com retração) é imune a isso.
- Isso reforça o que o experimento 4 já mostrava: a câmara de um contexto nunca
  visto não ajuda. Fica como achado a investigar, não como conclusão.

### 3. Rastreabilidade dos hashes após o rebase

O histórico foi reescrito (rebase) em 21/10 por volta de 13:10–13:11, e os hashes
gravados nos JSONs deixaram de existir no repositório. Os JSONs não foram
alterados. A correspondência abaixo é **inferida** pela ordem das datas de autor
e pela ancestralidade; não é verificável, porque os objetos antigos não existem
mais.

| Arquivo | Hash gravado | Commit equivalente hoje (inferido) |
|---|---|---|
| `experimentos/06/configuracao-congelada.json` | `fbe57bf` | `abe12d4` (gerador e baselines) |
| execução primária do exp. 6 | `45b1ca2` | `cf977a9` (congelamento) |
| grade exploratória do exp. 6 | `45b1ca2`, `alteracoes_locais: true` | `cf977a9` mais o JSON primário ainda não versionado |
| Fase 1 (`fase1-prior-adaptativo`) | `e932a10` | `472d727` (replicação congelada) |

A grade foi executada com árvore suja porque o JSON primário, recém-criado, ainda
não estava commitado. Isso é benigno aqui, mas fica registrado.

### 4. Tag

A tag `v0.1-prototipo` (commit `22fa015`) ainda não existe no repositório; ver
`CHANGELOG.md`.
