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
