# Experimento 7 — registro de desenvolvimento

**Natureza:** exploração de desenvolvimento; os resultados desta nota não são
evidência confirmatória e não serão combinados com a análise de teste.

## Piloto e sementes consumidas

Antes do pré-registro, foi relatado um piloto com as sementes `7000–7015`.
Essas sementes estão queimadas: não serão usadas para calibração, dimensionar o
teste ou avaliar resultados confirmatórios. O relato informa que seis cenários
foram examinados, mas só fornece os resultados de dois deles. Os outros quatro
cenários e seus valores não são reconstruídos nesta nota.

O piloto usou 4 contextos, 3 exposições no contexto novo, força contextual 0,8
e ruído médio 1,6. O valor de heterogeneidade foi 1,0 ou 0,35 nos dois cenários
relatados. O relato descreve uma escala de ruído lognormal por identidade,
`σ_i = σ̄ · exp(Z_i)` com `Z_i ~ N(−h²/2, h²)`, mas, sem o código do piloto, não
é possível verificar que a implementação usou exatamente essa fórmula.

| Heterogeneidade | NCM global | Câmaras v0.4 | Δ câmaras − NCM | DP de Δ relatado | Referência com variância por identidade |
|---:|---:|---:|---:|---:|---:|
| 1,0 | 0,825 | 0,862 | +3,6 pp | 2,2 pp | 0,883 |
| 0,35 | 0,861 | 0,823 | −4,1 pp | Não informado | 0,942 |

Os valores são os resumos arredondados do relato do piloto. A diferença entre
os valores arredondados de acurácia pode não coincidir exatamente com o Δ,
calculado a partir dos valores não arredondados.

## Interpretação limitada

- Na heterogeneidade alta, a vantagem relatada das câmaras foi de 3,6 pp, abaixo
  do efeito mínimo de 5 pp definido para o experimento confirmatório.
- A referência com variância por identidade teve acurácia maior que as câmaras
  nos dois cenários relatados. Sua fórmula inicial não era ajustada; o baseline
  confirmatório terá uma definição e uma busca próprias no pré-registro.
- Esses resultados motivaram a escolha de um regime de heterogeneidade alta e a
  inclusão do baseline de variância por identidade. Essa escolha baseada no
  piloto limita o alcance da conclusão futura ao regime registrado.

## Limites de rastreabilidade do piloto

O relato recebido não inclui o código, os resultados por semente, os valores
completos dos seis cenários, o hash do commit nem as versões do ambiente usadas
no piloto. Portanto, os números acima não podem ser reproduzidos ou auditados
independentemente a partir deste repositório. Esta lacuna fica registrada; não
será preenchida com números inferidos. O código do experimento 7 será uma nova
implementação pré-registrada, não uma cópia apresentada como reprodução do
piloto.

## Adendo (21/10/2026): recuperação do piloto e correção de um parâmetro

Este adendo é de desenvolvimento, não evidência confirmatória, e **não altera o
pré-registro**. Ele complementa a seção "Limites de rastreabilidade", que
descrevia o piloto como não auditável: o script e os resultados foram
recuperados e regravados.

### Artefatos

- `experimentos/07/desenvolvimento/piloto.py`: as funções são as do script do
  piloto original; só foi acrescentada a função `executar`, que grava os
  resultados por semente. A fórmula de ruído é a do pré-registro:
  `σ_i = σ̄ · exp(N(−h²/2, h²))`.
- `experimentos/07/desenvolvimento/piloto-resultados.json`: valores por semente.
  A regravação reproduziu **todos** os números do piloto original (as seis
  células de 8 sementes e os Δ de 16 sementes), pois o código é determinístico.
  O JSON foi gerado com Python 3.13.16 (o ambiente fixado do repositório é
  Python 3.12), NumPy 2.5.3 e scikit-learn 1.9.1, no commit `f102713`, com
  árvore suja (o próprio script ainda não estava versionado).
- Sementes: a tabela de seis cenários usou `7000–7007`; as estatísticas dos dois
  cenários e a sensibilidade a `w0` usaram `7000–7015`. Todas queimadas.

### Seis cenários (média de 8 sementes; câmaras com `w0 = 2σ̄²`)

Contextos 4, exposições 3, força 0,8. A "referência" é um estimador rápido, sem
ajuste, com variância por identidade; não é o baseline pré-registrado.

| σ̄ | h | NCM global | centro-ctx (λ=0,5) | kNN k=5 | câmaras | câmaras sem largura | referência |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0,8 | 0,35 | 0,995 | 0,995 | 0,932 | 0,999 | 0,986 | 1,000 |
| 0,8 | 1,0 | 0,944 | 0,946 | 0,824 | 0,977 | 0,923 | 0,780 |
| 1,6 | 0,35 | 0,861 | 0,873 | 0,519 | 0,823 | 0,784 | 0,942 |
| 1,6 | 1,0 | 0,825 | 0,827 | 0,610 | 0,862 | 0,778 | 0,883 |
| 2,4 | 0,35 | 0,597 | 0,620 | 0,258 | 0,444 | 0,487 | 0,739 |
| 2,4 | 1,0 | 0,705 | 0,707 | 0,485 | 0,694 | 0,646 | 0,827 |

### Correção: o `w0` do piloto estava fora da faixa de ajuste

O piloto fixou `w0 = 2σ̄²`, que para σ̄ = 1,6 vale 5,12, **fora** da grade
pré-registrada (`0,08 … 1,28`) e numa região em que as câmaras vão pior. Com
`σ̄ = 1,6`, `eta_min = 0,02` e 16 sementes de desenvolvimento, a acurácia média
das câmaras foi:

| `w0` | 0,08 | 0,16 | 0,32 | 0,64 | 1,28 | 2,56 | 5,12 | 10,24 | 20,48 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| h = 1,0 | 0,887 | 0,887 | 0,887 | 0,887 | 0,886 | 0,883 | 0,873 | 0,826 | 0,758 |
| h = 0,35 | 0,879 | 0,879 | 0,879 | 0,878 | 0,875 | 0,864 | 0,830 | 0,759 | 0,681 |

Recalculando o Δ pareado (16 sementes) com `w0` dentro da grade (`w0 = 0,64`,
valor representativo; 0,08 e 1,28 dão praticamente o mesmo):

| Comparador | h = 1,0: Δ (DP) | h = 0,35: Δ (DP) |
|---|---:|---:|
| NCM global | **+5,0 pp** (2,0) | +0,7 pp (2,2) |
| centro-ctx (λ=0,5) | +4,8 pp (2,2) | −0,5 pp (2,0) |
| referência com variância | +0,4 pp (5,9) | −6,3 pp (3,4) |

Com `w0 = 5,12` (o valor do piloto original) os mesmos Δ eram +3,6 pp, −4,1 pp
e −1,0 pp, −11,0 pp. Consequências para a leitura:

- A frase do relato original de que o melhor caso das câmaras ficava em +3,6 pp
  sobre o NCM **subestimava** as câmaras: com `w0` na grade, o Δ sobre o NCM
  fica em torno de +5 pp, no limite do efeito mínimo. A queda de 4 pp com
  heterogeneidade baixa também era, em grande parte, efeito do `w0` mal ajustado.
- O que se mantém: contra a referência com variância por identidade, as câmaras
  empatam com heterogeneidade alta (+0,4 pp) e perdem com heterogeneidade baixa
  (−6 pp). A inclusão desse baseline na comparação é o que decide o desfecho.
- A grade pré-registrada de `w0` não está desajustada para σ̄ = 1,6: a acurácia
  é praticamente constante de 0,08 a 1,28. Não foi verificado para σ̄ = 2,0 e
  2,4.
- A referência é um estimador não ajustado e o NCM pode mudar com os baselines
  ajustados. Todos os números acima têm 8 ou 16 sementes de desenvolvimento e
  servem para orientar o desenho, não para concluir.
