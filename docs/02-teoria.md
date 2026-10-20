# 02 - Teoria: o que é meu, o que já existe, onde se encaixa

**Aviso de proveniência.** As referências abaixo vêm da memória do assistente
(sem busca na web). Os autores e anos são os que ele conhece com confiança, mas
**confira cada um antes de citar formalmente**. Itens marcados `[verificar]`
têm menos certeza ou não foram checados. Nenhuma busca sistemática de
literatura foi feita, então **não está estabelecido que algo aqui seja inédito**.

Legenda de status: `[MINHA]` hipótese/intuição proposta por mim ·
`[EXISTE]` campo estabelecido · `[IMPL]` implementado neste repositório ·
`[NÃO TESTADO]` ainda sem teste.

---

## A. O que é meu (hipóteses e intuições)

| # | Ideia | Status | Comentário honesto |
|---|---|---|---|
| A1 | **Neurônio como ranhura**: a memória é a *forma* de uma cavidade, não um peso escalar | `[MINHA]` `[IMPL]` (como centro + largura) | Na CPU virou protótipo gaussiano. A parte "forma/geometria como código" só existiria no substrato físico |
| A2 | **Aprendizado como erosão** (cada eco desgasta e muda a ranhura) | `[MINHA]` `[IMPL]` (média móvel com taxa mínima) | Implementada como atualização local, sem backprop. Falta explicar *por que* a erosão melhoraria o desempenho em geral (problema de atribuição de crédito) |
| A3 | **Aprender = brotar ranhura nova em outro lugar**, sem sobrescrever | `[MINHA]` `[IMPL]` | Funciona, mas é o mesmo mecanismo de ART/DP-means (ver B2) |
| A4 | **Ranhura codifica contexto**: a pessoa é uma função do contexto, não um número | `[MINHA]` `[IMPL]` parcial | Só o caso aditivo e global foi testado. O caso interessante (efeito do contexto específico de cada pessoa, não linear) `[NÃO TESTADO]` |
| A5 | **Esquecimento elástico**: murcha, não some; volta rápido ao reencontrar | `[MINHA]` `[IMPL]` parcial | Murchar com orçamento de memória foi testado (exp. 5). O **retorno rápido** (a "saudade") `[NÃO TESTADO]` |
| A6 | **Dois sistemas**: modelo grande de mundo + modelo elástico pequeno e pessoal no dispositivo | `[MINHA]` (convergente com a literatura) | Ver B1 e B7. Não implementado: o módulo roda sozinho |
| A7 | **Entendimento = eco coerente (consonância)**; dissonância = não entendeu | `[MINHA]` `[NÃO TESTADO]` | Hoje "consonância" é só `z <= z_max`. Não há critério de coerência entre várias ranhuras |
| A8 | **Roteamento por ressonância**: ranhuras com forma parecida ressoam juntas e uma corrente liga os entendimentos | `[MINHA]` `[NÃO TESTADO]` | É a parte mais distinta da proposta e a menos explorada aqui |
| A9 | **Substrato físico** (som/eletromagnético) em que o cálculo é o próprio eco | `[MINHA]` fora do escopo | Existe como área (ver B5). Adiado de propósito |

**Resumo do que pode ser mais distintivo:** A7, A8 e A9 (readout e roteamento por
coerência de ressonância, em substrato oscilatório) e a combinação de A3 + A4 + A5
numa única unidade. Os demais itens individualmente têm equivalentes conhecidos.

---

## B. Frentes que já existem

### B1. Dois sistemas de aprendizado (rápido e lento) `[EXISTE]`
- **Complementary Learning Systems**: McClelland, McNaughton & O'Reilly (1995),
  *Psychological Review*. Hipocampo aprende rápido episódios; neocórtex integra devagar.
  É a base teórica de A6.
- Aprendizado episódico em IA: *Neural Episodic Control* (Pritzel et al., 2017) `[verificar]`.

### B2. Estabilidade vs plasticidade e categorias que brotam `[EXISTE]`
- **Adaptive Resonance Theory (ART)**: Grossberg (1976); Carpenter & Grossberg
  (1987). Foi desenhada exatamente para o "dilema estabilidade-plasticidade".
  Compara a entrada com uma categoria; se **ressoa** (acima do parâmetro de
  *vigilância*), a categoria aprende; se não, **cria categoria nova**. Seu
  `z_max` equivale à vigilância e "brotar" equivale a "resetar e criar". A
  semelhança é grande: **leia ART antes de afirmar novidade em A3.**
- **DP-means** (Kulis & Jordan, 2012): k-means não paramétrico, abre cluster novo
  quando a distância passa de um limiar (o mesmo que o exp. 3).
- **Growing Neural Gas** (Fritzke, 1995), **SOM** (Kohonen, 1982): unidades que
  nascem e se movem para os dados.
- **Redes RBF**, **mistura de gaussianas online**: centro + largura por unidade.

### B3. Memória associativa e ressonância `[EXISTE]`
- **Redes de Hopfield** (1982); **Dense Associative Memory** (Krotov & Hopfield,
  2016); **Modern Hopfield Networks** (Ramsauer et al., 2020, *Hopfield Networks
  is All You Need*): recuperação associativa que se liga à atenção de transformers.
  Candidata natural para A8 em software.
- **Hyperdimensional computing** (Kanerva, 2009) e **Holographic Reduced
  Representations** (Plate, 1995): codificar e combinar entidades em vetores de
  alta dimensão. Relevante para guardar "pessoa + contexto".
- **Fast weights** (Hinton & Plaut, 1987; Ba et al., 2016): pesos que mudam rápido
  e decaem. Parente direto de A2 + A5.

### B4. Aprendizado com poucos exemplos e protótipos `[EXISTE]`
- **Prototypical Networks** (Snell, Swersky & Zemel, 2017) e **Matching Networks**
  (Vinyals et al., 2016): classificar por distância a protótipos. O que o exp. 1
  mostra (ranhura ≈ NCM) é exatamente esse princípio.
- **Teorias de exemplares vs protótipos** em psicologia: Medin & Schaffer (1978),
  Nosofsky (1986, *Generalized Context Model*), Kruschke (1992, *ALCOVE*).
  Relevantes para decidir se guardar protótipo, exemplares ou ambos.
- **Neurônios de conceito**: Quian Quiroga et al. (2005, *Nature*). Evidência de
  codificação esparsa de conceitos individuais, mas a leitura "um neurônio criado
  só para ela" é simplificação.

### B5. Computação por ondas, ressonância e substratos físicos `[EXISTE]`
- **Reservoir computing**: Echo State Networks (Jaeger, 2001); Liquid State
  Machines (Maass, Natschläger & Markram, 2002). Um sistema dinâmico fixo "ecoa"
  a entrada e só a leitura é treinada.
- **"Pattern recognition in a bucket"** (Fernando & Sojakka, 2003): o balde de
  água que classifica. Revisão: **Tanaka et al. (2019)**, *Recent advances in
  physical reservoir computing*, *Neural Networks*.
- **Redes neurais físicas treinadas**: Wright et al. (2022), *Nature* `[verificar]`;
  **Hamiltonian Echo Backpropagation** (López-Pastor & Marquardt, 2023)
  `[verificar]`: aprendizado por "eco" em sistemas físicos. Muito próximo do
  espírito de A2 + A9.
- **Neurônios ressonadores e osciladores acoplados**: *Resonate-and-fire*
  (Izhikevich, 2001); redes oscilatórias (Hoppensteadt & Izhikevich, 1999)
  `[verificar]`. Candidatos para uma versão "espectral" da ranhura.
- **Fonônica / fotônica**: computação com ondas acústicas e luz existe como área;
  a menção específica a Cornell na conversa original **não foi verificada**.
- **Sincronia como ligação de informação**: Singer & Gray (1995); Fries (2005).
  Suporta a ideia de "a corrente liga entendimentos que ressoam juntos" (A8)
  como hipótese neurocientífica, ainda debatida.

### B6. Aprendizado sem backprop `[EXISTE]`
- Hebb, BCM, **STDP** (Bi & Poo, 1998); **Equilibrium Propagation** (Scellier &
  Bengio, 2017); **Forward-Forward** (Hinton, 2022). A pergunta "como a erosão sabe
  que mudança melhora o resultado?" é o problema de atribuição de crédito, e essas
  são as tentativas locais. Nenhuma iguala backprop em tarefas gerais.

### B7. Aprendizado contínuo e personalização `[EXISTE]`
- **Esquecimento catastrófico**: McCloskey & Cohen (1989); French (1999).
  Mitigações: **EWC** (Kirkpatrick et al., 2017), replay, redes progressivas
  (Rusu et al., 2016), adapters/**LoRA** (Hu et al., 2021).
- **Memória externa**: Neural Turing Machine (Graves et al., 2014), kNN-LM
  (Khandelwal et al., 2019/2020), RAG (Lewis et al., 2020), **Titans**
  (Behrouz et al., 2024/2025: memória que aprende em tempo de teste). É a
  vizinhança mais direta de A6 hoje.

### B8. Esquecimento e contexto `[EXISTE]`
- **Curva do esquecimento e "economia no reaprendizado"** (Ebbinghaus, 1885): o
  que foi esquecido é reaprendido mais rápido. É a base empírica do A5 ("volta
  rápido").
- **Princípio da especificidade de codificação** (Tulving & Thomson, 1973): a
  lembrança depende do contexto da aprendizagem. Base de A4.
- **Políticas de cache**: LRU, LFU, **LRFU** (Lee et al., 2001), ARC (Megiddo &
  Modha, 2003). O "murchar" é um contador com vazamento do tipo LRFU.
- Consolidação sináptica e *synaptic tagging and capture* (Frey & Morris, 1997).

### B9. Contexto como transformação `[EXISTE]`
- Adaptação de domínio e modulação por contexto (por ex. **FiLM**, Perez et al.,
  2018). O "deslocamento de tom" aditivo é o caso mais simples.

### B10. Fora do consenso (cuidado) `[EXISTE, controverso]`
- Microtúbulos como substrato de computação ressonante (linha Orch OR, Hameroff
  e Penrose; medições atribuídas a Bandyopadhyay). Não é consenso, e há críticas
  de decoerência (Tegmark, 2000). **Não use como fundamento da proposta.**

### B11. Crescimento de estrutura e aprendizado local (sugerido na conversa original) `[EXISTE]`
- **NEAT** (Stanley & Miikkulainen, 2002): redes que crescem por evolução.
  **Neural Developmental Programs** (Najarro et al., 2023) `[verificar]`: um
  programa que constrói a rede.
- **Hypernetworks** (Ha et al., 2016): uma rede que gera os pesos de outra. Não é o
  mesmo que "ranhura elástica", apesar de a conversa original equiparar os dois.
- **KAN, Kolmogorov-Arnold Networks** (Liu et al., 2024) `[verificar]`: arestas como
  funções aprendíveis (splines). Vantagens relatadas em tarefas pequenas; sem
  consenso de que valham em geral. (A conversa original datou em 2023 e falou em
  "10x melhor com 10x menos parâmetros".)
- **Redes de spikes + STDP** e hardware **neuromórfico** (Loihi 2, TrueNorth,
  NorthPole, SpiNNaker) e **memristores**: áreas reais, com objetivos e limites
  próprios. A proposta da conversa (STDP + neurogênese) é uma direção **diferente**
  da implementada aqui e enfrenta o mesmo problema de atribuição de crédito (B6).
- **Growing Neural Gas** (já em B2): o parente mais próximo que roda em laptop;
  deve virar baseline.

---

## C. Mapa: ingrediente → quem já fez → o que sobra

| Ingrediente | Já existe em | O que sobraria de possivelmente novo |
|---|---|---|
| Brotar categoria quando nada ressoa | ART, DP-means, GNG | nada, só a combinação com os demais |
| Média móvel de protótipo com taxa mínima | quase tudo (online k-means, fast weights) | nada |
| Rápido + lento | CLS, Titans, kNN-LM | a forma específica do módulo rápido |
| Câmara por contexto | exemplares, codificação específica | contexto **não aditivo e por pessoa**, aprendido |
| Murchar sem sumir, voltar rápido | LRFU, economia no reaprendizado | o **retorno rápido** como mecanismo explícito |
| Eco como cálculo | reservoir computing, redes físicas | ranhura como **cavidade com modos próprios** e leitura por coerência |
| Roteamento por ressonância | Hopfield moderno, osciladores acoplados, sincronia | a regra de "corrente" que liga clusters ressoantes |

---

## D. Leituras sugeridas, em ordem

1. Carpenter & Grossberg, **ART** (a mais próxima da lógica atual).
2. McClelland et al. 1995, **CLS** (a justificativa biológica de A6).
3. Ramsauer et al. 2020, **Modern Hopfield Networks** (para A8 em software).
4. Tanaka et al. 2019, **Physical reservoir computing** (para A9).
5. Behrouz et al., **Titans** e Khandelwal et al., **kNN-LM** (concorrentes diretos).
6. Snell et al. 2017, **Prototypical Networks** (o baseline que mais importa).
7. Izhikevich 2001, **Resonate-and-fire** (para a ranhura "espectral").