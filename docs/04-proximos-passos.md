# 04 - Próximos passos

## Regra do jogo

Até aqui, o protótipo implementa brotar, erodir, murchar e câmaras, mas os
resultados não demonstram uma vantagem geral sobre métodos de protótipos. Cada passo abaixo
precisa de: **hipótese · tarefa · baseline · métrica · critério de falsificação
definido antes de rodar**. Se a hipótese falhar, isso entra em
`docs/03-resultados-e-limites.md` como resultado, não some.

Modelo para registrar cada experimento novo:

```
Experimento N - <nome>
Hipótese:        <o que deve ser verdade se a ideia vale>
Tarefa/dados:    <gerador ou dataset; split de calibração separado do teste>
Baselines:       <os mais fortes e justos, incluindo o "truque" equivalente>
Métrica:         <uma principal>
Falsificada se:  <ex.: não vence o melhor baseline por >= 5 pontos em 10 sementes>
Sementes/config: <fixas, salvas em arquivo>
```

---

## Baselines obrigatórios a partir de agora

Todo experimento novo deve incluir, quando fizer sentido para a tarefa:

- **Protótipos:** NCM e NCM + o mesmo truque que as ranhuras usarem.
- **Instâncias:** kNN com k > 1 e ponderado por distância.
- **Agrupamento incremental:** online k-means, **DP-means**, **Fuzzy ART**,
  **Growing Neural Gas** (o parente mais próximo que roda em laptop).
- **Aprendizado contínuo:** replay com buffer pequeno e EWC.
- **Parametrizado:** MLP com hiperparâmetros ajustados em conjunto de calibração.

---

## Visão geral (ordem sugerida)

| Fase/estudo | Foco | Por quê agora | Esforço (estimativa) | Estado em 2026-10-22 |
|---|---|---|---|---|
| 0 | Higiene do repositório | base para tudo o resto | 1 a 2 dias | Requisitos mínimos concluídos; itens legados adiados |
| 1 | Núcleo sem prior mágico | o exp. 3 mostrou fragilidade | 2 a 4 dias | Executada; resultado inconclusivo |
| 2 | **Exp. 6: contexto não aditivo** | teste exploratório da generalização por contexto | 3 a 5 dias | Executada; não informativa por efeito de teto |
| Exp. 7 | Câmaras isoladas sob ruído heteroscedástico | comparar v0.4 com baselines ajustados | concluído | Refutado quanto ao ganho mínimo na célula primária |
| 3 | Retorno rápido ("saudade") | testa uma promessa específica da memória elástica | 2 a 4 dias | Experimento 8 pré-registrado; pipeline pendente neste commit |
| 4 | Ressonância entre ranhuras | testa a hipótese de rede e associação | 1 a 2 semanas | Não iniciada; requer especificação e revisão de literatura |
| 5 | Ranhura espectral (modos) | testa processamento de sinais temporais | 2 a 3 semanas | Não iniciada |
| 6 | Dados reais e concorrentes | sair do sintético | 2 a 3 semanas | Não iniciada |
| 7 | Revisão de literatura e escrita | delimitar o que já existe antes de alegar novidade | contínuo | Não concluída; necessária antes de prototipar a hipótese de rede |
| 8 | Hardware (adiado) | só se a fase 5 justificar | - | Adiada |

O requisito operacional mínimo da Fase 0 está concluído; as tarefas de
reprodução e visualização dos experimentos legados foram adiadas. O experimento 7
também foi concluído, mas não testa as ligações entre unidades da hipótese de
rede. A Fase 1 continua inconclusiva, portanto não conta como confirmação do
núcleo sem prior mágico. O pré-registro de cada novo estudo deve declarar se sua
hipótese depende da Fase 1 ou se pode ser avaliada independentemente dela. A
Fase 2 foi executada primeiro por poder testar a tese central diretamente.

### Leitura do estado atual

O experimento 6 foi executado como a Fase 2, mas não respondeu à hipótese de
vantagem das câmaras: a acurácia do melhor baseline na calibração deixou margem
insuficiente para detectar o efeito mínimo. A conclusão registrada é
"não informativo", não "confirmado" nem "refutado". Uma eventual repetição será
um novo experimento, com pré-registro próprio; os resultados do experimento 6
permanecem históricos.

A Fase 1 também foi executada, mas seu resultado foi inconclusivo. A execução
anterior à Fase 2 está documentada; ela não demonstra que a hipótese do núcleo
sem prior mágico foi satisfeita.

O experimento 7 avaliou a versão isolada das câmaras, não uma rede de ranhuras.
Na condição primária, a acurácia foi 0,7928 contra 0,8664 do baseline
`variancia_identidade`; `Δ = −7,36` pp, IC95% `[−8,50; −6,22]` pp. O resultado
refuta o ganho mínimo de 5 pp naquela condição sintética. A grade exploratória
reutilizou os parâmetros selecionados para a célula primária, portanto seus
ganhos em algumas células não são evidência confirmatória nem comparação entre
métodos ajustados especificamente para cada célula. Ver `experimentos/07/LEIA.md`.

**Encerramento da linha isolada:** a versão v0.4 das câmaras e sua hipótese de
ganho na condição primária ficam encerradas com o experimento 7. Não ajustar essa
mesma versão para tentar reverter o resultado. Uma variante futura é uma hipótese
nova e exige justificativa, pré-registro e avaliação próprios.

---

## Fase 0 - Higiene

**Estado: requisitos mínimos concluídos para iniciar novos experimentos.** O
Git, as dependências fixadas, o CHANGELOG, os testes unitários do núcleo e do
registrador e os comandos básicos do `Makefile` estão disponíveis. Itens de
reprodução e visualização dos experimentos legados ficam adiados; a conclusão
do experimento 7 não os cobriu.

| Item | Estado |
|---|---|
| Controle de versão (Git) e CHANGELOG | Concluído; o histórico de versões está em `CHANGELOG.md`. |
| Testes unitários do núcleo (brotar, erosão, murchar e deslocamento) | Concluído; propriedades mecânicas cobertas em `tests/test_ranhuras.py`. |
| Separar calibração e teste nos experimentos antigos, em especial nas varreduras do experimento 3 | Adiado para os experimentos 1 a 5. A avaliação comparativa da Fase 1 usou sementes novas, mas não substitui uma nova análise das varreduras 3b/3c. |
| Parâmetros de linha de comando e saída JSON para os experimentos antigos | Adiado. Os resultados antigos permanecem históricos; não serão convertidos em registros retroativos. |
| Reexecuções exploratórias das varreduras 3b/3c e gráficos dos experimentos 1, 2 e 3 | Adiados; não foram cobertos pelo experimento 7. |
| `Makefile` com comandos de instalação, teste e execução | Concluído: `make install`, `make test` e `make run`. |

Os experimentos 1 a 5 permanecem exploratórios; seus arquivos e números não
serão reescritos para preencher retroativamente esses itens. Reexecuções futuras
serão registros novos, com rótulo exploratório e proveniência própria. A Fase 1
usou sementes novas para avaliar o comparador histórico, mas isso não corrige a
seleção original nas varreduras 3b/3c nem substitui sua reexecução. Esses itens
foram explicitamente adiados. A pasta `experimentos/README.md` explica a relação
entre fases do roteiro e IDs das pastas.

## Fase 1 - Núcleo sem prior mágico

**Problema:** `w0` e `z_max` exigem conhecer a escala do ruído (exp. 3b/3c).

**Hipótese:** dá para derivar o limiar de uma regra estatística em vez de ajustá-lo
à mão.
- Sob ruído gaussiano isotrópico, `D · d2 / σ²` segue qui-quadrado com `D` graus de
  liberdade. Se `w` acompanha o erro esperado, vale `z_max = quantil(1-α) de χ²_D / D`
  (por ex. α = 1%). Verificar empiricamente: o ruído real pode não ser isotrópico.
- Estimar `w0` online com uma **variância compartilhada** entre ranhuras
  (hierárquico): ranhuras novas herdam a média de `w` das existentes em vez de
  um `w0` fixo.

**Tarefa:** repetir o exp. 3 e a varredura 3c sem retunar.
**Baselines:** versão atual; k-means com K dado.
**Falsificada se:** o ARI não for ≥ 0,95 em σ ∈ {0.3, 0.4, 0.5} com um único
conjunto de parâmetros e `w0` variando por um fator 4.

## Fase 2 - Experimento 6: contexto não aditivo (executada; não informativa)

**Pergunta:** as câmaras por contexto ganham do NCM com deslocamento quando o
contexto afeta **cada pessoa de um jeito próprio**?

**Requisito do gerador:** o mundo precisa ser um em que o NCM seja
*comprovadamente subótimo* (ver `docs/03`); caso contrário o empate está garantido.
Opções: pessoas com mais de um modo por contexto, variância de ruído diferente por
pessoa, deriva lenta do protótipo (aí `eta_min` importa), ruído não gaussiano.

**Gerador sugerido:** cada pessoa tem um perfil por contexto,
`x = proto_p + A_p · u_ctx + ruído`, com `A_p` específico da pessoa (ou
interpolação entre dois protótipos conforme o contexto). Variar: nº de contextos
(2, 4, 8), nº de exposições no contexto novo (0, 1, 3, 10), força do efeito
específico da pessoa.

**Baselines:** NCM, NCM + deslocamento global, kNN, Prototypical Network com
contexto como entrada, centro por (pessoa, contexto) sem hierarquia.
**Métrica:** acurácia nas pessoas em contexto novo, em função do nº de exposições.
O experimento 6 foi classificado como não informativo por efeito de teto. Esse
resultado histórico não é substituído pelo experimento 7, que testou outra
condição e uma hipótese confirmatória própria.

## Experimento 7 - Câmaras isoladas sob ruído heteroscedástico (concluído)

**Pergunta:** a versão v0.4 das câmaras supera o melhor baseline ajustado por
pelo menos 5 pp na condição primária pré-registrada?

**Resultado:** refutado quanto ao ganho mínimo na condição primária: `Δ = −7,36`
pp, IC95% `[−8,50; −6,22]` pp, em 30 sementes. Isso limita a conclusão à
condição sintética especificada no pré-registro; não testa a hipótese da rede
com ligações, ativação propagada ou ressonância coletiva.

A grade de 216 células é exploratória e usa o baseline congelado na calibração
da condição primária (três exposições). Ganhos em células de uma exposição não
demonstram vantagem após ajuste por célula. Detalhes e ablações estão em
`experimentos/07/LEIA.md`.

**Extensão:** aprender `A_p` compartilhando estrutura entre pessoas (por ex.
`u_ctx` aprendido com quem foi visto em vários contextos), para generalizar a
quem só foi visto uma vez.

## Fase 3 - Retorno rápido ("saudade")

**Hipótese:** uma ranhura que murchou volta com **menos exposições** do que
aprender do zero (economia no reaprendizado, Ebbinghaus).

**Estado:** pré-registro do Experimento 8 preparado; nenhuma semente de
calibração ou teste foi executada. O pipeline será adicionado em commit
subsequente. Ver `experimentos/08/PREREGISTRO.md`.

**Operacionalização:** ao ser removida do orçamento ativo, a ranhura pode deixar
um resumo comprimido com centro e largura. No reencontro, o resumo pode ser
restaurado como prior. O código v0.5 não tem esse arquivo de traços; é uma
condição nova implementada isoladamente no Experimento 8.

**Tarefa:** 16 classes em vetores sintéticos. Uma classe-alvo é expulsa por uma
classe nova após um período sem observações; depois de um intervalo, o alvo
retorna com exposições rotuladas. A cada exposição, medir o recall do alvo em
consultas independentes e calcular quantas exposições são necessárias para
recuperar 90% do recall anterior à expulsão; acurácia balanceada fica como
métrica secundária.

**Baselines:** apagar completamente (comparação confirmatória); cache
comprimido sem decaimento (controle secundário); manter tudo (teto descritivo).
As condições com orçamento ativo limitado usam 16 ranhuras e um resumo
comprimido, quando aplicável.

**Critério:** confirmado se o limite inferior do IC95% da economia relativa de
exposições (`1 − E90_traço / E90_apagar`) for pelo menos 30%; refutado quanto ao
efeito mínimo se o limite superior ficar abaixo de 30%; inconclusivo nos demais
casos. A métrica, os gates e a regra estão definidos em
`experimentos/08/PREREGISTRO.md`.

## Fase 4 - Ressonância entre ranhuras (A7 e A8)

Hoje cada ranhura age sozinha. A proposta pede que ranhuras **ressoem juntas** e
que um acorde coerente "ligue entendimentos".

Versão em software, em duas etapas:
1. **Associação por recuperação**: arestas hebbianas entre ranhuras que ecoam
   perto no tempo; ativação que se espalha. Comparar com **Modern Hopfield /
   atenção softmax** sobre os centros e com uma tabela de relações explícita.
   Tarefa: dado um sinal parcial, recuperar a ranhura relacionada (pessoa → lugar,
   pessoa → contexto frequente).
2. **Dinâmica coletiva**: definir uma medida de coerência (por ex. energia do
   estado conjunto ou coerência de fase de osciladores acoplados) como variável
   diagnóstica. O sucesso principal deve ser medido numa tarefa de recuperação
   ou associação; coerência por si só não define que o sistema "entendeu".
**Falsificada se:** a recuperação por ressonância não superar a atenção softmax
simples nem a tabela explícita em acurácia ou em robustez a ruído.

## Fase 5 - Ranhura espectral (a "ressonância" de verdade)

**Hipótese:** representar a ranhura como um **banco de ressonadores amortecidos**
(frequência, fator Q, amplitude por modo) e ler o eco como energia de resposta
é mais robusto que um protótipo vetorial para **sinais no tempo** (variação de
fase e de velocidade).

**Implementação:** NumPy/SciPy, sem hardware. Erosão = deslocar a frequência e o
Q do modo em direção ao sinal que ecoou.
**Tarefa:** reconhecer locutores ou sons a partir de séries temporais (sintéticas
primeiro, depois áudio real pequeno), com 1 a 3 exemplos.
**Baselines:** MFCC + NCM, MFCC + kNN, Prototypical Network, reservoir computing
(ESN).
**Falsificada se:** não igualar MFCC + NCM com menos parâmetros ou mais robustez
a deformação temporal. Se falhar, a "ressonância" fica como metáfora e a
contribuição vira só A1 a A6.

## Fase 6 - Dados reais e concorrentes

- **Dados** (`[verificar]` disponibilidade e licenças): embeddings de rosto ou voz
  (LFW, VoxCeleb), Omniglot (poucos exemplos), CORe50 (aprendizado contínuo com
  sessões e contextos diferentes).
- **Concorrentes:** Prototypical Networks, **Fuzzy ART** (implementar ou usar uma
  biblioteca), Growing Neural Gas, kNN-LM, uma memória estilo Titans em pequena
  escala, LoRA por usuário.
- **Teste cedo e barato (pode rodar em paralelo à Fase 2):** fluxo de classes que
  surgem ao longo do tempo (class-incremental) sobre **embeddings congelados** de um
  encoder pré-treinado. Expectativa realista: com features pré-treinadas, um
  classificador por protótipos já é um baseline muito forte em aprendizado
  incremental de classes (`[verificar]`, linha de trabalho de "pre-trained models
  for class-incremental learning"), então empatar com ele já seria o esperado; o
  teste serve para descobrir se há algo além disso. Não chamar de "aprender pessoas"
  até haver dados e avaliação que sustentem essa leitura.
- **Cenário-alvo da ideia original:** módulo pessoal em cima de um encoder
  congelado, rodando no dispositivo. Medir: acurácia com 1 a 5 exemplos, memória
  usada, tempo por atualização, esquecimento após N etapas.

## Fase 7 - Literatura e escrita

- [ ] Revisão sistemática curta de ART, CLS, fast weights, Titans, physical
      reservoir computing, Hamiltonian Echo Backpropagation (ver `docs/02-teoria.md`).
- [ ] Preencher a tabela "o que sobra de novo" com evidência, não palpite.
- [ ] Nota técnica (pode ser pré-print) incluindo os resultados negativos.
- [ ] Buscar 1 ou 2 pessoas da área (reservoir computing, aprendizado contínuo,
      ART) para revisar a proposta antes de investir em hardware.

## Fase 8 - Hardware (adiado)

Só reabrir se a fase 5 mostrar vantagem em sinais **e** houver um argumento
quantitativo de energia ou latência. Antes de construir: simular a acústica
(guia de onda ou cavidades ressonantes em diferenças finitas), ler Tanaka et al.
(2019) e conversar com grupos de physical reservoir computing.

---

## Perguntas abertas

1. O que a ranhura faria que um protótipo com média móvel não faz? (fases 2, 3, 5)
2. Como a erosão sabe *qual* mudança melhora o desempenho em tarefas além de
   "lembrar quem é quem"? (atribuição de crédito)
3. Qual é a representação certa para "pessoa + contexto + tempo" (função, não escalar)?
4. Como definir e medir "acorde coerente" sem cair em circularidade?
5. O módulo rápido deve **substituir** o modelo grande, ou ser uma memória acoplada
   a ele? (a literatura aponta para acoplar)
6. Em que ponto a vantagem de um substrato físico (paralelismo, energia)
   compensa a perda de precisão e estabilidade?

## Decisões a tomar

- **Alvo principal:** memória pessoal para IA no dispositivo, **ou** computação de
  sinais por ressonância? As fases 2, 3 e 6 servem ao primeiro; a 5 e a 8 ao segundo.
- **Ambição:** exploração de ideia, nota técnica, ou produto. Isso define o rigor
  e o tempo investido.
- **Orçamento de tempo semanal** para o projeto: ele define quantas fases cabem
  por mês e qual ordem vale a pena.

## Critério de parada honesto

Os critérios dos experimentos 4, 6 e 7 se aplicam às respectivas versões e
condições, não à hipótese de rede ainda não implementada. Antes de adotar um
critério de parada para o projeto inteiro, é preciso especificar a tarefa e as
regras da rede com ligações e compará-la com baselines adequados. A linha v0.4
das câmaras isoladas está encerrada; uma variante só deve ser reaberta como nova
hipótese, com justificativa e pré-registro próprios. O resultado do experimento 7
permanece histórico.
