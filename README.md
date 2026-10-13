# Sistema de Controle de Estoque e Vendas

- **Trabalho em dupla:** Mario Henrique Martins dos Santos e Paulo Renan Santana de Almeida
- **Disciplina:** Paradigmas de Programação, UNAMA. Prof. Rodrigo Medeiros Costa
- **Atividade:** Avaliativa AV1, resolução de problema com **paradigma imperativo** (Python)
- **Vídeo de demonstração:** _(link do vídeo aqui)_

Programa de terminal que controla o estoque e as vendas de um pequeno comércio. Ele permite cadastrar produtos, registrar entradas e saídas de itens, consultar saldos, registrar vendas com vários itens e calcular os valores vendidos. Foi escrito no paradigma **imperativo/procedural**: o programa é uma sequência de instruções que alteram o estado dos dados (variáveis, listas e dicionários) usando atribuições, decisões (`if/elif/else`), repetições (`while`/`for`) e funções. Não usa classes nem recursos de outros paradigmas.

## Sumário

1. [Descrição do problema](#1-descrição-do-problema)
2. [Como executar](#2-como-executar)
3. [Funcionalidades (menu)](#3-funcionalidades-menu)
4. [Estrutura do projeto](#4-estrutura-do-projeto)
5. [Explicação da solução](#5-explicação-da-solução)
6. [Reflexão sobre o desenvolvimento](#6-reflexão-sobre-o-desenvolvimento)
7. [Integrantes](#7-integrantes)

---

## 1. Descrição do problema

Um pequeno comércio (por exemplo, uma papelaria) precisa saber **quanto tem de cada produto** e **quanto vendeu**. Sem um sistema, é fácil vender o que não existe em estoque, perder o controle das perdas e avarias e errar o cálculo do faturamento. O programa resolve isso mantendo o cadastro de produtos e o saldo de cada um. Cada movimento de estoque (entrada, saída avulsa ou venda) altera esse saldo e fica registrado num histórico.

### Entradas

| Operação | O usuário informa |
|----------|-------------------|
| Cadastro de produto | código (inteiro de 1 a 999.999, único), nome (não vazio, até 30 caracteres), preço de venda (de R$ 0,01 a R$ 999.999,99, com vírgula ou ponto e sem separador de milhar, ex.: `19,99`) e saldo inicial (inteiro de 0 a 999.999) |
| Entrada de itens | código do produto e quantidade (inteiro de 1 a 999.999) |
| Saída avulsa | código, quantidade (inteiro de 1 a 999.999, até o saldo) e motivo (1 perda, 2 avaria, 3 uso interno) |
| Venda | um ou mais itens (código + quantidade, até o disponível), com opção de remover itens, e a confirmação (`s`/`n`) |
| Menus | número da opção (0 a 7 no menu principal; 0 a 4 no de relatórios) |

### Regras do negócio

1. **Código único:** não é possível cadastrar dois produtos com o mesmo código.
2. **Entradas validadas:** valores fora dos limites acima (texto em campo numérico, negativos, zero onde não cabe, números grandes demais) são recusados com uma mensagem, e a pergunta se repete. O programa não "quebra".
3. **Sem saldo, sem saída:** uma saída avulsa ou venda só acontece se houver saldo suficiente. Caso contrário, **nada é alterado**.
4. **Saída avulsa não é venda:** perda, avaria ou uso interno diminuem o estoque, mas **não** entram no faturamento.
5. **Venda com vários itens:** o carrinho pode ter vários produtos. Adicionar de novo o mesmo produto soma no mesmo item, e o disponível é o saldo menos o que já está no carrinho. A venda é **tudo-ou-nada**: ou todos os itens baixam do estoque, ou nenhum.
6. **Preço congelado:** cada item vendido guarda o nome e o preço do momento da venda, então os comprovantes e relatórios antigos não mudam.
7. **Histórico:** toda entrada, saída avulsa e venda gera um registro de movimentação com data, tipo, quantidade, motivo e saldo após a operação.
8. **Relatórios:** o faturamento soma só as vendas. O ticket médio é o faturamento dividido pelo número de vendas, arredondado ao centavo. Sem vendas, o programa avisa em vez de dividir por zero.

### Decisões técnicas

- **Dinheiro em centavos:** os preços são guardados como inteiros de centavos (`19,99` vira `1999`), o que evita os erros de arredondamento dos números com casas decimais. Na tela, aparecem como `R$ 1.234,56`.
- **Persistência:** os dados ficam em `dados/loja.json` e são salvos após cada operação, com gravação segura (arquivo temporário + troca). Se o arquivo estiver corrompido ou com formato inválido, o programa guarda uma cópia `.corrompido`, avisa e começa vazio. Se o arquivo não puder ser aberto (por exemplo, bloqueado por outro programa), o programa avisa e encerra sem alterá-lo.

### Resultados esperados

- Toda operação que altera o estado mostra a mudança no formato **"antes -> depois"** (ex.: `Saldo de Caneta azul: 100 -> 97`).
- **Comprovante de venda** com quantidade × preço unitário, subtotais e total.
- **Extrato** de movimentações de cada produto na consulta de saldo.
- **Relatórios:** faturamento total (com número de vendas e ticket médio), vendas por produto, valor do estoque (saldo × preço) e lista de todas as vendas.
- Os dados continuam lá ao fechar e abrir o programa de novo.
- Operações inválidas são recusadas **sem alterar nada**, com mensagens como:
  - saída de 100 cadernos com saldo 47 → `Saldo insuficiente (há 47 unidade(s)). Nada foi alterado.`
  - cadastro com código já usado → `Já existe um produto com o código 1. Cadastro cancelado.`
  - preço `abc` → `Preço inválido. Use o formato 12,50 (de R$ 0,01 a R$ 999.999,99, sem separador de milhar).`

### Exemplo verificável (dados de exemplo)

Na primeira execução, o programa carrega `dados/exemplo.json` (papelaria com 5 produtos). Nele:

- **Venda 1:** 3 × Caderno 96 folhas (R$ 19,99) = R$ 59,97 + 5 × Caneta azul (R$ 2,50) = R$ 12,50 → **total R$ 72,47**. O saldo do caderno foi de 50 para 47.
- **Faturamento total:** R$ 72,47 + R$ 92,90 + R$ 37,00 = **R$ 202,37** em 3 vendas, com ticket médio de **R$ 67,46**.
- **Valor do estoque:** 47 × R$ 19,99 + 82 × R$ 2,50 + 68 × R$ 1,20 + 48 × R$ 1,50 + 7 × R$ 89,90 = **R$ 1.927,43**.
- As saídas avulsas (3 canetas com avaria e 2 lápis perdidos) diminuíram o estoque, mas não aparecem no faturamento.

## 2. Como executar

**Requisitos:** Python **3.10 ou superior** (desenvolvido e testado no 3.12). Não há bibliotecas para instalar: só a biblioteca padrão.

```bash
git clone https://github.com/MarioHenriqueM/Controle_Estoque.git
cd Controle_Estoque
python main.py
```

- No Windows também funciona `py main.py`. No Linux/macOS, use `python3 main.py`.
- O programa pode ser executado a partir de qualquer pasta (`python caminho/para/main.py`).

**Testes automáticos** (regras e cálculos: leitura de valores, moeda, cadastro, estoque, carrinho, venda, relatórios e persistência):

```bash
python testes.py
```

O resultado esperado é `Todos os testes passaram.`, com código de saída 0.

**Onde ficam os dados:** em `dados/loja.json`, criado na primeira gravação. Se ele não existir, o programa carrega os dados de exemplo (`dados/exemplo.json`, que nunca é alterado). Para **recomeçar com os dados de exemplo**, apague o arquivo `dados/loja.json`.

## 3. Funcionalidades (menu)

```
========= CONTROLE DE ESTOQUE E VENDAS =========
1 - Cadastrar produto
2 - Registrar entrada de itens
3 - Registrar saída avulsa (perda, avaria, uso interno)
4 - Registrar venda
5 - Consultar saldo de um produto
6 - Listar estoque
7 - Relatórios
0 - Sair
```

| Opção | O que faz |
|-------|-----------|
| 1 | Cadastra produto. O saldo inicial entra no histórico como ENTRADA "saldo inicial" |
| 2 | Soma uma quantidade ao saldo (motivo "compra") |
| 3 | Baixa o saldo por perda, avaria ou uso interno, se houver saldo, sem gerar receita |
| 4 | Abre o carrinho (adicionar, remover, finalizar ou cancelar), mostra o resumo, pede confirmação e emite o comprovante |
| 5 | Mostra o produto e o extrato de movimentações dele |
| 6 | Lista todos os produtos com preço e saldo |
| 7 | Submenu: faturamento total, vendas por produto, valor do estoque, todas as vendas |
| 0 | Salva e encerra (Ctrl+C também encerra sem mensagem de erro) |

## 4. Estrutura do projeto

```
├── main.py              # programa principal: carrega os dados, repete o menu e salva
├── testes.py            # testes automáticos (python testes.py)
├── loja/                # pacote com os módulos do sistema (só funções)
│   ├── leitura.py       # lê do teclado com validação (único módulo com input())
│   ├── telas.py         # uma função para cada opção do menu (perguntas e resultados)
│   ├── formatacao.py    # transforma valores em texto (R$ 1.234,56, linhas de tabela)
│   ├── cadastro.py      # cria, busca e cadastra produtos
│   ├── estoque.py       # entrada, saída e histórico (único lugar onde o saldo muda)
│   ├── caixa.py         # carrinho e registro da venda (tudo-ou-nada)
│   ├── relatorios.py    # faturamento, vendas por produto, valor do estoque
│   └── persistencia.py  # salva e carrega os dados em JSON (único módulo que abre arquivos)
├── dados/
│   └── exemplo.json     # dados de demonstração carregados na primeira execução
└── docs/
    └── EXPLICACAO.md    # explicação detalhada da solução, com trechos do código
```

O estado do programa são **três listas** criadas no `main.py` e passadas como parâmetro para as funções: `produtos`, `vendas` e `movimentacoes`. Cada registro é um dicionário. Por exemplo, a Caneta azul dos dados de exemplo é `{"codigo": 2, "nome": "Caneta azul", "preco_centavos": 250, "saldo": 82}`.

## 5. Explicação da solução

**Explicação completa, com trechos do código e teste de mesa: [docs/EXPLICACAO.md](docs/EXPLICACAO.md)**

Resumo da lógica: o `main.py` carrega o estado (três listas: `produtos`, `vendas`, `movimentacoes`) e repete o menu até o usuário sair. Cada opção chama uma tela, que lê os dados, chama a regra correspondente e mostra o resultado. Depois de cada operação que altera o estado, os dados são salvos.

Onde estão os elementos do paradigma imperativo:

| Elemento | Exemplo no código |
|----------|-------------------|
| Sequência de instruções | `formatar_moeda` em [loja/formatacao.py](loja/formatacao.py): calcula reais e centavos passo a passo. `main` em [main.py](main.py): carregar → avisar → executar o menu |
| Alteração de estado (variáveis e atribuições) | `registrar_entrada` em [loja/estoque.py](loja/estoque.py): `produto["saldo"] = produto["saldo"] + quantidade`. Acumulador `total_centavos` em `calcular_total` ([loja/caixa.py](loja/caixa.py)). `executando = False` no menu |
| Decisões | `if/elif/else` do menu em `executar_menu` ([main.py](main.py)). `if not tem_saldo_suficiente(...)` em `registrar_saida` ([loja/estoque.py](loja/estoque.py)). Validações em `ler_inteiro` ([loja/leitura.py](loja/leitura.py)) |
| Repetições | `while executando:` (menu), `while not valido:` (leituras), `for` com acumuladores e laços aninhados em `vendas_por_produto` ([loja/relatorios.py](loja/relatorios.py)) |
| Funções e procedimentos | Funções sem efeito colateral (`calcular_total`, `buscar_produto`, `formatar_moeda`) e procedimentos que alteram as listas recebidas (`registrar_entrada`, `efetivar_venda`) |

A venda é feita em **duas passadas** (`efetivar_venda`, em [loja/caixa.py](loja/caixa.py)): primeiro confere o saldo de cada produto do carrinho, depois baixa o estoque. Assim, ou a venda acontece inteira, ou nada muda.

A explicação completa também cobre:

- passagem de parâmetros (mutação × reatribuição);
- escopo e constantes;
- aliasing e cópias;
- a ordem das instruções;
- a comparação com os paradigmas orientado a objetos e funcional, e com C.

## 6. Reflexão sobre o desenvolvimento

### Principais decisões

Cada decisão aparece no formato **o que escolhemos** (em vez do quê) e o motivo.

- **Python em estilo procedural** (em vez de C): o Python já estava instalado e deixa o código mais legível. Mantivemos só construções imperativas, sem classes, `lambda`, *comprehensions* ou `map`/`filter`.
- **Centavos inteiros** (em vez de `float`): `int(0.29 * 100)` dá `28`, e não `29`. Com inteiros, somas e multiplicações são exatas.
- **Estado em três listas passadas por parâmetro** (em vez de variáveis globais): a assinatura mostra o que cada função altera, e os testes usam listas próprias.
- **Regras separadas das telas** (em vez de `input`/`print` dentro das regras): `cadastro`, `estoque`, `caixa` e `relatorios` podem ser testados automaticamente.
- **Venda em duas passadas** (em vez de baixar item a item): conferir tudo antes garante o tudo-ou-nada.
- **Saída avulsa separada da venda** (em vez de uma operação só): as duas baixam o estoque, mas só a venda gera receita.
- **JSON com gravação segura** (em vez de banco de dados): é simples de explicar, e o `.tmp` + `os.replace` evita deixar o arquivo pela metade.

### Dificuldades encontradas

- **Ler preços com vírgula sem usar `float`.** A solução foi separar reais e centavos pelo texto e validar cada parte (`texto_para_centavos`). Os testes "0,29 sem erro de float" e "três casas é inválido" provam o resultado.
- **Produto repetido no carrinho.** Adicionar o mesmo produto duas vezes podia ultrapassar o saldo. Passamos a somar no mesmo item e a calcular o *disponível* como saldo menos o que já está no carrinho. Na revisão final, a confirmação da venda também passou a conferir o **total** de cada produto, garantindo o tudo-ou-nada (teste "produto repetido acima do saldo é recusado").
- **Nomes de módulos × nomes de variáveis.** Um módulo `vendas.py` entraria em conflito com a lista `vendas` recebida como parâmetro. Por isso os módulos se chamam `caixa`, `cadastro` e `estoque`.
- **Acentuação no Windows.** Todo `open()` informa a codificação de forma explícita: `"utf-8"` na gravação e `"utf-8-sig"` na leitura, que também aceita arquivos salvos com BOM (como os do Bloco de Notas). Na revisão final, descobrimos que no Git Bash o menu saía com caracteres trocados e um nome digitado como "Lápis" era gravado como "LÃ¡pis". O `main` passou a configurar UTF-8 na entrada e na saída (`configurar_acentos`).
- **Ordem das perguntas.** No primeiro teste da saída avulsa, o motivo era pedido antes de conferir o saldo: o usuário escolhia o motivo e só depois era recusado. Ajustamos para conferir o saldo logo depois da quantidade. A correção entrou no mesmo commit da tela.
- **Manter o estilo imperativo.** Foi preciso disciplina para não usar atalhos como *comprehensions* e para cuidar do aliasing das listas passadas por parâmetro. Na revisão, percebemos que a venda guardava a mesma lista do carrinho, e ela passou a guardar cópias dos itens.
- **Arquivo de dados editado à mão.** Um JSON válido, mas sem as chaves ou com os tipos errados (um produto sem `"nome"`, ou um preço como texto), derrubava o programa. Agora a estrutura é validada ao carregar (`persistencia.estrutura_valida`), e o arquivo inválido é guardado como cópia `.corrompido` (testes "estrutura errada começa vazio" e "preço como texto é inválido").

### Possíveis melhorias

**Prioritárias**, porque seriam as mais úteis para o comerciante:

1. Cancelar ou estornar uma venda, devolvendo os itens ao estoque.
2. Estoque mínimo com alerta de reposição.
3. Alterar o preço e o nome de um produto. As vendas antigas não mudariam, porque o preço fica congelado no item.

**Outras:**

- Buscar produtos por parte do nome.
- Destacar o produto mais vendido e gerar relatórios por período (data inicial e final).
- Quando o arquivo de dados estiver bloqueado por outro programa, oferecer uma nova tentativa em vez de encerrar.
- Interface gráfica ou banco de dados, para um uso real com mais dados.

Elas ficaram de fora para manter o programa pequeno, correto e fácil de explicar no porte desta atividade.

### Etapas do desenvolvimento (histórico de commits)

As mensagens de commit indicam a etapa entre parênteses, por exemplo `feat(fase-2): ...`:

| Etapa | O que foi construído |
|-------|----------------------|
| `fase-1` | Leitura validada, formatação de moeda, persistência em JSON, cadastro, consulta, listagem e menu principal |
| `fase-2` | Entrada de itens, saída avulsa, histórico de movimentações e extrato |
| `fase-3` | Carrinho e venda com vários itens, comprovante, relatórios e dados de exemplo |
| `fase-4` | Documentação: README e explicação da solução |
| `fix` / `refactor` | Correções e ajustes encontrados ao testar e revisar o programa (validação do arquivo, venda com produto repetido, acentuação no Git Bash, legibilidade) |

### Uso de ferramentas

Usamos um assistente de IA (Claude) como apoio no planejamento, na pesquisa de boas práticas e na escrita do código e da documentação. Revisamos, executamos e testamos o programa, e estudamos cada parte para conseguir explicá-la.

## 7. Integrantes

| Integrante | Participação |
|------------|--------------|
| Mario Henrique Martins dos Santos | Implementação do programa (`main.py` e pacote `loja/`) e testes automatizados (`testes.py`) |
| Paulo Renan Santana de Almeida | Documentação: descrição do problema, explicação da solução ([docs/EXPLICACAO.md](docs/EXPLICACAO.md)), reflexão, roteiro e gravação do vídeo de demonstração |

**Versionamento:** todos os commits do repositório foram feitos pela conta do GitHub de Mario Henrique, que também integrou ao repositório a documentação produzida por Paulo Renan.
