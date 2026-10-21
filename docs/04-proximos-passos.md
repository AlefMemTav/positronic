# 04 - Próximos passos

## Regra do jogo

Até aqui, o protótipo provou que **a lógica funciona** (brotar, erodir, murchar,
câmaras) mas **não provou que ganha de um centro médio** (NCM). Cada passo abaixo
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

| Fase | Foco | Por quê agora | Esforço (estimativa) | Estado em 2026-10-21 |
|---|---|---|---|---|
| 0 | Higiene do repositório | base para tudo o resto | 1 a 2 dias | Parcial |
| 1 | Núcleo sem prior mágico | o exp. 3 mostrou fragilidade | 2 a 4 dias | Executada; resultado inconclusivo |
| 2 | **Exp. 6: contexto não aditivo** | primeiro teste que pode dar vantagem real | 3 a 5 dias | Executada; não informativa por efeito de teto |
| 3 | Retorno rápido ("saudade") | testa uma promessa específica da ideia | 2 a 4 dias | Não iniciada |
| 4 | Ressonância entre ranhuras | a parte mais distinta da proposta | 1 a 2 semanas | Não iniciada |
| 5 | Ranhura espectral (modos) | testa se "ressonância" é mais que metáfora | 2 a 3 semanas | Não iniciada |
| 6 | Dados reais e concorrentes | sair do sintético | 2 a 3 semanas | Não iniciada |
| 7 | Revisão de literatura e escrita | saber o que é novo de fato | contínuo | Não concluída |
| 8 | Hardware (adiado) | só se a fase 5 justificar | - | Adiada |

O roteiro original considera as fases 0 e 1 pré-requisitos. Como a Fase 0 está
parcial e a Fase 1 teve resultado inconclusivo, o estado dessas duas fases deve
ser levado em conta antes de começar outro estudo. As fases 2 a 5 são
independentes entre si depois que esses pré-requisitos forem tratados; a Fase 2
foi executada primeiro por poder testar a tese central diretamente.

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

---

## Fase 0 - Higiene

**Estado: parcialmente concluída.** O Git, as dependências fixadas, o CHANGELOG
e o módulo de registro JSON para as execuções recentes existem. A lista abaixo
separa o que está pronto do que continua pendente:

| Item | Estado |
|---|---|
| Controle de versão (Git) e CHANGELOG | Concluído; o histórico de versões está em `CHANGELOG.md`. |
| Testes unitários do núcleo (brotar, erosão, murchar e deslocamento) | Pendente. Os testes atuais cobrem o módulo de registro, não o núcleo. |
| Separar calibração e teste nos experimentos antigos, em especial nas varreduras do experimento 3 | Pendente para os experimentos 1 a 5. As execuções novas da Fase 1 e do experimento 6 têm sementes separadas. |
| Parâmetros de linha de comando e saída JSON para os experimentos antigos | Parcial. O registro JSON existe, mas os experimentos 1 a 5 não foram migrados para usá-lo. |
| Gráficos dos experimentos 1, 2 e 3 | Pendente. |
| `pyproject.toml` ou `Makefile` com comandos de execução e teste | Pendente. |

Os experimentos 1 a 5 permanecem exploratórios; seus arquivos e números não
serão reescritos para preencher retroativamente esses itens. Antes de iniciar
outro experimento, decidir quais pendências são requisitos de entrada e quais
serão adiadas, registrando essa decisão. A pasta `experimentos/README.md`
explica a relação entre fases do roteiro e IDs das pastas.

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
**Falsificada se:** em nenhuma célula do grid as câmaras vencem o melhor baseline
por ≥ 5 pontos (10 sementes, desvios não sobrepostos). Nesse caso, a tese
"ranhura codifica contexto" não se sustenta além do deslocamento aditivo.

**Extensão:** aprender `A_p` compartilhando estrutura entre pessoas (por ex.
`u_ctx` aprendido com quem foi visto em vários contextos), para generalizar a
quem só foi visto uma vez.

## Fase 3 - Retorno rápido ("saudade")

**Hipótese:** uma ranhura que murchou volta com **menos exposições** do que
aprender do zero (economia no reaprendizado, Ebbinghaus).

**Implementação sugerida:** ao ser esquecida por orçamento, a ranhura deixa um
**traço comprimido** (centro com largura ampla, em memória barata). Ao reencontro,
o traço funciona como prior e a taxa de erosão inicial é maior.
**Tarefa:** aprender N pessoas, intercalar T passos com outras pessoas até o
esquecimento, reencontrar. Medir exposições necessárias para recuperar 90% da
acurácia original.
**Baselines:** apagar e reaprender do zero; manter tudo (teto).
**Falsificada se:** o reaprendizado com traço não exigir pelo menos 30% menos
exposições que do zero.

## Fase 4 - Ressonância entre ranhuras (A7 e A8)

Hoje cada ranhura age sozinha. A proposta pede que ranhuras **ressoem juntas** e
que um acorde coerente "ligue entendimentos".

Versão em software, em duas etapas:
1. **Associação por recuperação**: arestas hebbianas entre ranhuras que ecoam
   perto no tempo; ativação que se espalha. Comparar com **Modern Hopfield /
   atenção softmax** sobre os centros e com uma tabela de relações explícita.
   Tarefa: dado um sinal parcial, recuperar a ranhura relacionada (pessoa → lugar,
   pessoa → contexto frequente).
2. **Critério de coerência**: definir "acorde coerente" numericamente (por ex. energia
   do estado conjunto, ou coerência de fase de um banco de osciladores acoplados,
   modelo de Kuramoto) e usá-lo como medida de "entendeu / não entendeu".
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

Se **os exps. 4 e 6 e a fase 3 falharem** em mostrar vantagem sobre NCM com
deslocamento e sobre o traço comprimido, a descrição mais fiel do projeto passa a
ser: *"uma variante de ART com política de esquecimento por força decaída"*. Isso
ainda é um resultado sólido e reaproveitável, só não é uma nova arquitetura. Decidir isso com dados é um resultado, não um fracasso.
