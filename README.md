# Sistema de Controle de Estoque e Vendas

**Trabalho individual:** Mario Henrique
**Disciplina:** Paradigmas de Programação, UNAMA. Prof. Rodrigo Medeiros Costa
**Atividade:** Avaliativa AV1, resolução de problema com **paradigma imperativo** (Python)

🎥 **Vídeo de demonstração:** _(link do vídeo aqui)_

Programa de terminal que controla o estoque e as vendas de um pequeno comércio. Ele permite cadastrar produtos, registrar entradas e saídas de itens, consultar saldos, registrar vendas com vários itens e calcular os valores vendidos. Foi escrito no paradigma **imperativo/procedural**: o programa é uma sequência de instruções que alteram o estado dos dados (variáveis, listas e dicionários) usando atribuições, decisões (`if/elif/else`), repetições (`while`/`for`) e funções. Não usa classes nem recursos de outros paradigmas.

## Sumário

1. [Descrição do problema](#1-descrição-do-problema)
2. [Como executar](#2-como-executar)
3. [Funcionalidades (menu)](#3-funcionalidades-menu)
4. [Estrutura do projeto](#4-estrutura-do-projeto)
5. [Explicação da solução](#5-explicação-da-solução)
6. [Reflexão sobre o desenvolvimento](#6-reflexão-sobre-o-desenvolvimento)
7. [Integrante](#7-integrante)

---

## 1. Descrição do problema

Um pequeno comércio (por exemplo, uma papelaria) precisa saber **quanto tem de cada produto** e **quanto vendeu**. Sem um sistema, é fácil vender o que não existe em estoque, perder o controle das perdas e avarias e errar o cálculo do faturamento. O programa resolve isso mantendo o cadastro de produtos e o saldo de cada um. Cada movimento de estoque (entrada, saída avulsa ou venda) altera esse saldo e fica registrado num histórico.

### Entradas

| Operação | O usuário informa |
|----------|-------------------|
| Cadastro de produto | código (inteiro ≥ 1), nome (até 30 caracteres), preço de venda (ex.: `19,99`) e saldo inicial (inteiro ≥ 0) |
| Entrada de itens | código do produto e quantidade (inteiro ≥ 1) |
| Saída avulsa | código, quantidade e motivo (perda, avaria ou uso interno) |
| Venda | um ou mais itens (código + quantidade), com opção de remover itens, e a confirmação (s/n) |
| Consultas e relatórios | código do produto ou número da opção desejada |

### Regras principais

1. **Código único:** não é possível cadastrar dois produtos com o mesmo código.
2. **Entradas validadas:** texto em campo numérico, números negativos, zero onde não cabe e valores grandes demais são recusados com uma mensagem, e a pergunta se repete (o programa não "quebra").
3. **Dinheiro em centavos:** os preços são guardados como números inteiros de centavos (`19,99` vira `1999`), o que evita erros de arredondamento de números com casas decimais. Na tela, aparecem como `R$ 1.234,56`.
4. **Sem saldo, sem saída:** uma saída avulsa ou venda só acontece se houver saldo suficiente. Caso contrário, **nada é alterado**.
5. **Saída avulsa não é venda:** perda, avaria ou uso interno diminuem o estoque, mas **não** entram no faturamento.
6. **Venda com vários itens:** o carrinho pode ter vários produtos. Adicionar de novo o mesmo produto soma no mesmo item, e o disponível é o saldo menos o que já está no carrinho. A venda é **tudo-ou-nada**: ou todos os itens baixam do estoque, ou nenhum.
7. **Preço congelado:** cada item vendido guarda o nome e o preço do momento da venda, então os comprovantes e relatórios antigos não mudam.
8. **Histórico:** toda entrada, saída avulsa e venda gera um registro de movimentação com data, tipo, quantidade, motivo e saldo após a operação.
9. **Relatórios:** o faturamento soma só as vendas. O ticket médio é o faturamento dividido pelo número de vendas, arredondado ao centavo. Sem vendas, o programa avisa em vez de dividir por zero.
10. **Persistência:** os dados ficam em `dados/loja.json` e são salvos após cada operação, com gravação segura (arquivo temporário + troca). Se o arquivo estiver corrompido, o programa guarda uma cópia `.corrompido`, avisa e começa vazio.

### Resultados esperados

- Toda operação que altera o estado mostra a mudança no formato **"antes -> depois"** (ex.: `Saldo de Caneta azul: 100 -> 97`).
- **Comprovante de venda** com quantidade × preço unitário, subtotais e total.
- **Extrato** de movimentações de cada produto na consulta de saldo.
- **Relatórios:** faturamento total (com número de vendas e ticket médio), vendas por produto, valor do estoque (saldo × preço) e lista de todas as vendas.
- Os dados continuam lá ao fechar e abrir o programa de novo.

### Exemplo verificável (dados de exemplo)

Na primeira execução, o programa carrega `dados/exemplo.json` (papelaria com 5 produtos). Nele:

- **Venda 1:** 3 × Caderno 96 folhas (R$ 19,99) = R$ 59,97 + 5 × Caneta azul (R$ 2,50) = R$ 12,50 → **total R$ 72,47**. O saldo do caderno foi de 50 para 47.
- **Faturamento total:** R$ 72,47 + R$ 92,90 + R$ 37,00 = **R$ 202,37** em 3 vendas, com ticket médio de **R$ 67,46**.
- **Valor do estoque:** 47 × R$ 19,99 + 82 × R$ 2,50 + 68 × R$ 1,20 + 48 × R$ 1,50 + 7 × R$ 89,90 = **R$ 1.927,43**.
- As saídas avulsas (3 canetas com avaria e 2 lápis perdidos) diminuíram o estoque, mas não aparecem no faturamento.

## 2. Como executar

**Requisitos:** Python **3.10 ou superior** (desenvolvido e testado no 3.12). Não há bibliotecas para instalar: só a biblioteca padrão.

```bash
git clone <URL deste repositório>
cd <pasta do repositório>
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

O estado do programa são **três listas** criadas no `main.py` e passadas como parâmetro para as funções: `produtos`, `vendas` e `movimentacoes`. Cada registro é um dicionário, por exemplo `{"codigo": 1, "nome": "Caneta azul", "preco_centavos": 250, "saldo": 97}`.

## 5. Explicação da solução

_(em preparação)_

## 6. Reflexão sobre o desenvolvimento

### Principais decisões

- **Python em vez de C.** O Python já estava instalado e deixa o código mais curto e legível para explicar. Ainda assim, mantive o estilo imperativo "puro": nada de classes, `lambda`, *list comprehensions* ou `map`/`filter`. Todas as repetições são laços `while`/`for` explícitos.
- **Estado em três listas passadas por parâmetro**, sem variáveis globais. Assim, a assinatura de cada função mostra o que ela pode alterar (por exemplo, `efetivar_venda(produtos, vendas, movimentacoes, carrinho, data)`).
- **Dinheiro em centavos (inteiros).** Com números de ponto flutuante, `int(0.29 * 100)` dá `28`, e não `29`. Guardando `29` centavos, as somas e multiplicações ficam exatas.
- **Regras separadas das telas.** Os módulos de regra (`cadastro`, `estoque`, `caixa`, `relatorios`) não usam `input()` nem `print()`. Por isso dá para testá-los automaticamente em `testes.py`.
- **Venda tudo-ou-nada em duas passadas:** primeiro confere o saldo de todos os itens, depois baixa o estoque. Assim, uma venda nunca fica "pela metade".
- **Saída avulsa separada da venda.** As duas diminuem o estoque, mas só a venda gera receita.
- **Gravação segura do arquivo:** o JSON é escrito num arquivo temporário e depois trocado com `os.replace`, para não perder os dados se algo falhar no meio da gravação.

### Dificuldades encontradas

- **Ler preços digitados com vírgula** (`19,99`) sem usar `float`. A solução foi separar reais e centavos pelo texto e validar cada parte (`texto_para_centavos`).
- **Produto repetido no carrinho:** adicionar o mesmo produto duas vezes podia ultrapassar o saldo. Passei a calcular o *disponível* como saldo menos o que já está no carrinho e a somar no mesmo item.
- **Nomes de módulos x nomes de variáveis:** um módulo chamado `vendas.py` entraria em conflito com a lista `vendas` recebida como parâmetro. Por isso os módulos se chamam `caixa`, `cadastro` e `estoque`.
- **Acentuação no Windows:** ao testar o programa redirecionando a entrada e a saída, os acentos saíam errados. Todo `open()` passou a usar `encoding="utf-8"`.
- **Ordem das perguntas:** na saída avulsa, o motivo era pedido antes de conferir o saldo. Inverti para recusar logo uma quantidade maior que o saldo.

### Possíveis melhorias

- Alterar preço e nome de um produto (as vendas antigas não mudariam, porque o preço fica congelado no item).
- Buscar produtos por parte do nome.
- Estoque mínimo com alerta de reposição.
- Destacar o produto mais vendido e gerar relatórios por período (data inicial e final).
- Cancelar ou estornar uma venda, devolvendo os itens ao estoque.
- Interface gráfica ou banco de dados, para um uso real com mais dados.

### Uso de ferramentas

Usei um assistente de IA (Claude) como apoio no planejamento, na pesquisa de boas práticas e na escrita do código e da documentação. Revisei, executei e testei o programa, e estudei cada parte para conseguir explicá-la.

## 7. Integrante

| Nome | Participação |
|------|--------------|
| Mario Henrique | Trabalho individual: análise do problema, implementação, testes e documentação |
