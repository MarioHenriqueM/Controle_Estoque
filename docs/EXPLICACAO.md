# Explicação da solução

Este documento explica a lógica do **Sistema de Controle de Estoque e Vendas** e aponta, no código, os elementos do **paradigma imperativo**:

- sequência de instruções;
- alteração de estado por variáveis e atribuições;
- estruturas de decisão;
- estruturas de repetição;
- funções e procedimentos.

Os trechos são citados por **arquivo e função**.

## 1. Visão geral da lógica

### O estado do programa

No paradigma imperativo, o programa é uma sequência de comandos que **altera o estado** guardado na memória. Aqui o estado completo são **três listas**, criadas na função `main` do `main.py`:

| Lista | Cada elemento (dicionário) | Exemplo |
|-------|----------------------------|---------|
| `produtos` | código, nome, preço em centavos, saldo | `{"codigo": 1, "nome": "Caderno 96 folhas", "preco_centavos": 1999, "saldo": 47}` |
| `vendas` | número, data, itens, total | `{"numero": 1, "data": "13/10/2026 12:09", "itens": [...], "total_centavos": 7247}` |
| `movimentacoes` | data, tipo, código, quantidade, motivo, saldo após | `{"data": "...", "tipo": "VENDA", "codigo": 1, "quantidade": 3, "motivo": "venda 1", "saldo_apos": 47}` |

As listas são **passadas como parâmetro** para as funções que precisam delas. O programa não tem estado global mutável (veja a seção 2.6), e a assinatura de cada função mostra o que ela pode modificar.

### O fluxo

```
python main.py
   │
   ▼
main()                      carrega as 3 listas do arquivo dados/loja.json
   │
   ▼
executar_menu()  ◄──────┐   while executando:
   │                    │     mostra o menu e lê a opção
   ▼                    │     if/elif/else chama a tela da opção
telas.<opção>()         │       a tela pergunta os dados (leitura)
   │                    │       chama a regra (cadastro/estoque/caixa/relatorios)
   ▼                    │       mostra o resultado ("antes -> depois")
persistencia.salvar ────┘     se o estado mudou, salva no arquivo
```

O código é dividido em três camadas:

- **Interação** (`leitura`, `telas`, `formatacao` e o próprio `main.py`): `leitura` é o único módulo com `input()`; `telas` e `main.py` mostram mensagens com `print()`; `formatacao` só monta os textos (devolve strings) que as telas imprimem.
- **Regras** (`cadastro`, `estoque`, `caixa`, `relatorios`): recebem dados prontos, calculam e alteram as listas, sem `input()` nem `print()`. Por isso podem ser testadas automaticamente em `testes.py`.
- **Dados** (`persistencia`): é o único módulo que abre arquivos.

## 2. Elementos do paradigma imperativo no código

Os trechos abaixo foram copiados do código. Em alguns, comentários com o valor das variáveis foram acrescentados **só nesta explicação**, para acompanhar a execução.

### 2.1 Sequência de instruções

As instruções são executadas uma depois da outra, e cada uma usa o resultado das anteriores.

**`loja/formatacao.py`, função `formatar_moeda`:** transforma centavos em texto, passo a passo.

```python
sinal = ""
if centavos < 0:
    sinal = "-"
    centavos = -centavos
reais = centavos // 100                       # 123456 // 100 -> 1234
resto = centavos % 100                        # 123456 % 100  -> 56
reais_texto = f"{reais:,}".replace(",", ".")  # 1234 -> "1,234" -> "1.234"
return f"{sinal}R$ {reais_texto},{resto:02d}"   # "R$ 1.234,56"
```

**`main.py`, função `main`:** a sequência do programa inteiro. Ela:

1. configura o terminal;
2. carrega os dados (se o arquivo não puder ser aberto, avisa e encerra);
3. mostra o aviso, se houver;
4. chama `executar_menu(produtos, vendas, movimentacoes)` dentro de um `try`.

```python
configurar_acentos()
try:
    produtos, vendas, movimentacoes, aviso = persistencia.carregar_dados(CAMINHO_DADOS,
                                                                         CAMINHO_EXEMPLO)
except OSError:
    print("Não foi possível abrir o arquivo de dados (ele está aberto em outro programa?).")
    print("Feche o arquivo e execute o programa de novo.")
    return
if aviso != "":
    print(aviso)
```

A **ordem importa**: as listas só existem depois de `carregar_dados`, e o menu só pode começar depois disso. A seção 5.2 traz mais exemplos de por que a ordem das instruções muda o resultado.

### 2.2 Alteração de estado por variáveis e atribuições

O saldo de um produto **só muda em `loja/estoque.py`**, em duas atribuições.

**Função `registrar_entrada`:** o saldo aumenta, e a movimentação é acrescentada ao histórico.

```python
produto["saldo"] = produto["saldo"] + quantidade
registro = criar_movimentacao(data, TIPO_ENTRADA, produto, quantidade, motivo)
movimentacoes.append(registro)
```

**Função `registrar_saida`:** o saldo diminui, mas só se houver saldo.

```python
if not tem_saldo_suficiente(produto, quantidade):
    return False
produto["saldo"] = produto["saldo"] - quantidade
```

**Acumulador**, em `loja/caixa.py`, função `calcular_total`: a variável `total_centavos` muda a cada volta do laço.

```python
total_centavos = 0
for item in itens:
    total_centavos = total_centavos + item["subtotal_centavos"]
return total_centavos
```

**Variável de controle**, em `main.py`, função `executar_menu`: a atribuição `executando = False` (opção 0) é o que faz o laço do menu terminar.

**Listas que crescem:**
- `produtos.append(novo)` em `cadastro.cadastrar_produto`;
- `vendas.append(venda)` em `caixa.efetivar_venda`;
- `movimentacoes.append(registro)` em `estoque`.

Na tela, cada alteração é mostrada como **"antes -> depois"**, por exemplo em `telas.registrar_entrada`:

```python
saldo_antes = produto["saldo"]
quantidade = leitura.ler_inteiro("Quantidade que entrou: ", 1)
estoque.registrar_entrada(produto, quantidade, movimentacoes,
                          data_hora_atual(), estoque.MOTIVO_COMPRA)
nome = produto["nome"]
saldo_depois = produto["saldo"]
print(f"Entrada registrada. Saldo de {nome}: {saldo_antes} -> {saldo_depois}")
```

### 2.3 Estruturas de decisão

**`main.py`, função `executar_menu`:** o `if/elif/else` escolhe o que fazer com a opção digitada.

```python
if opcao == 1:
    alterou = telas.cadastrar_produto(produtos, movimentacoes)
elif opcao == 2:
    alterou = telas.registrar_entrada(produtos, movimentacoes)
...
elif opcao == 0:
    executando = False
else:
    print("Opção inválida.")
```

**`loja/leitura.py`, função `ler_inteiro`:** três caminhos para o valor digitado.

```python
if numero == -1:
    print("Valor inválido: digite só números inteiros, sem sinal, com até 6 dígitos.")
elif numero < minimo:
    print(f"Digite um número maior ou igual a {minimo}.")
else:
    valido = True
```

**`loja/relatorios.py`, função `ticket_medio_centavos`:** a decisão evita a divisão por zero.

```python
if quantidade_vendas == 0:
    return 0
# Somar metade do divisor antes da divisão inteira arredonda para o centavo
# mais próximo. Ex.: 7497 / 2 = 3748,5 -> (7497 + 1) // 2 = 3749.
return (faturamento_centavos + quantidade_vendas // 2) // quantidade_vendas
```

### 2.4 Estruturas de repetição

**Quando usar `while` e quando usar `for`:**

- **`while`** quando o número de repetições **não é conhecido** de antemão e depende do usuário ou de uma condição. A repetição é controlada por uma variável:
  - `while executando:` em `main.executar_menu` (menu principal);
  - `while montando:` em `telas.registrar_venda` (carrinho);
  - `while no_menu:` em `telas.menu_relatorios` (submenu de relatórios);
  - `while not valido:` em `leitura.ler_inteiro` e `leitura.ler_texto`, que repetem a pergunta até o valor ser válido.
- **`for`** quando é preciso **percorrer uma lista inteira**: busca linear, acumuladores e laços aninhados.

**O Python não tem `do-while`.** Para garantir que a pergunta seja feita pelo menos uma vez, a variável de controle começa com um valor que **força a primeira volta**. Em `leitura.ler_preco_centavos`:

```python
centavos = 0
while centavos <= 0:
    texto = input(mensagem)
    centavos = texto_para_centavos(texto)
```

O mesmo acontece com `resposta = ""` em `leitura.ler_confirmacao` e com `opcao = 0` em `telas.escolher_motivo_saida`.

**`for` percorrendo uma lista.** Busca linear do produto, em `cadastro.buscar_produto`:

```python
for produto in produtos:
    if produto["codigo"] == codigo:
        return produto
return None
```

Também são `for` os acumuladores de `caixa.calcular_total` e `relatorios.faturamento_total`.

**`while` com índice explícito**, em `caixa.remover_do_carrinho`. A variável `posicao` começa em 0 e aumenta 1 a cada volta. Quando o item é encontrado, ele é removido pela posição e a função termina:

```python
posicao = 0
while posicao < len(carrinho):
    if carrinho[posicao]["codigo"] == codigo:
        carrinho.pop(posicao)
        return True
    posicao = posicao + 1
return False
```

**Laços aninhados**, em `loja/relatorios.py`, função `vendas_por_produto`. Para cada produto, o código percorre todas as vendas e todos os itens de cada venda, somando unidades e valores:

```python
for produto in produtos:
    unidades = 0
    valor_centavos = 0
    for venda in vendas:
        for item in venda["itens"]:
            if item["codigo"] == produto["codigo"]:
                unidades = unidades + item["quantidade"]
                valor_centavos = valor_centavos + item["subtotal_centavos"]
```

### 2.5 Funções, procedimentos e efeito colateral

**Efeito colateral** é qualquer mudança que uma função causa fora dela, além do valor que devolve. Exemplos: alterar uma lista ou um dicionário recebido, gravar um arquivo, escrever na tela (`print`) ou ler do teclado (`input`). O código tem três tipos de subprograma:

| Tipo | Exemplos | O que fazem |
|------|----------|-------------|
| **Funções sem efeito colateral** | `calcular_subtotal`, `calcular_total`, `formatar_moeda`, `texto_para_centavos`, `tem_saldo_suficiente`, `buscar_produto`, `faturamento_total`, `vendas_por_produto` | Só calculam e devolvem um valor. Com os mesmos dados, o resultado é sempre o mesmo |
| **Procedimentos** | `estoque.registrar_entrada`, `caixa.adicionar_ao_carrinho` | Não devolvem valor. Existem para **alterar** o estado recebido (efeito colateral) |
| **Procedimentos que também devolvem um resultado** | `estoque.registrar_saida` (`True`/`False`), `cadastro.cadastrar_produto` (o produto ou `None`), `caixa.remover_do_carrinho` (`True`/`False`), `caixa.efetivar_venda` (a venda ou `None`) | Alteram o estado e devolvem se deu certo, ou o registro criado, para a tela decidir a mensagem |

A docstring de cada procedimento diz o que ele altera (`Altera: ...`).

**Passagem de parâmetros.** O Python não copia listas nem dicionários ao passá-los para uma função: o parâmetro é um **novo nome para o mesmo objeto** de quem chamou. Isso se chama passagem "por referência de objeto", ou "por compartilhamento", e gera dois comportamentos diferentes:

1. **Alterar o objeto recebido muda o objeto de quem chamou.** É o que faz `estoque.registrar_entrada` funcionar:

   ```python
   produto["saldo"] = produto["saldo"] + quantidade   # altera o dicionário que está na lista produtos
   movimentacoes.append(registro)                     # altera a lista criada no main
   ```

2. **Reatribuir o parâmetro muda só a variável local.** Em `formatacao.formatar_moeda`, a linha `centavos = -centavos` troca apenas o valor da variável local `centavos`, e o número de quem chamou continua igual. O mesmo vale para `texto = texto.strip()` em `leitura.texto_para_inteiro`. Números e textos, aliás, nem podem ser alterados, porque são imutáveis.

Por isso `cadastro.buscar_produto` devolve o **próprio dicionário** que está na lista, e não uma cópia: alterar `produto["saldo"]` depois altera o estoque. O teste "busca devolve o próprio registro da lista", em `testes.py`, comprova isso.

### 2.6 Escopo: variáveis locais e constantes

- **Variáveis locais:**
  - `produtos`, `vendas` e `movimentacoes` são locais da função `main` e chegam às outras funções **por parâmetro**.
  - `opcao` e `alterou` são locais de `executar_menu` e recebem um valor novo a cada volta do laço. Em cada volta, depois de mostrar o menu e ler a opção, `alterou = False` zera a variável antes do `if/elif`.
  - Quando a função termina, as variáveis locais dela deixam de existir. Por exemplo, o `carrinho` de `telas.registrar_venda` nasce vazio (`carrinho = []`) a cada venda.
- **Constantes de módulo:**
  - São os nomes em MAIÚSCULAS, como `CAMINHO_DADOS` (`main.py`), `MAXIMO_DIGITOS` (`leitura.py`), `TIPO_VENDA` e `MOTIVOS_SAIDA` (`estoque.py`).
  - Ficam no nível do módulo, mas **só são lidas, nunca alteradas**. `MOTIVOS_SAIDA` é uma tupla, que nem pode ser modificada.
  - Por isso o programa não tem **estado global mutável**: o comando `global` não aparece no código, e todo o estado que muda passa por parâmetro.

## 3. Mapa de mutações: onde cada parte do estado muda

| Mudança | Único lugar no código | Elementos usados |
|---------|----------------------|------------------|
| Produto novo | `cadastro.cadastrar_produto` → `produtos.append(novo)` | decisão (código já existe?) + alteração da lista |
| Saldo aumenta | `estoque.registrar_entrada` → `produto["saldo"] = produto["saldo"] + quantidade` | atribuição |
| Saldo diminui | `estoque.registrar_saida` → `produto["saldo"] = produto["saldo"] - quantidade` | decisão (saldo basta?) + atribuição |
| Histórico cresce | `estoque.registrar_entrada` / `registrar_saida` → `movimentacoes.append(registro)` | alteração da lista |
| Carrinho (temporário) | `caixa.adicionar_ao_carrinho` / `caixa.remover_do_carrinho` | repetição + decisão + atribuição |
| Venda registrada | `caixa.efetivar_venda` → `vendas.append(venda)`, com cópias dos itens | 3 laços + decisões + chamada de procedimento |
| Fim do programa | `main.executar_menu` → `executando = False` | variável de controle do laço |

A venda **reaproveita** `estoque.registrar_saida` para baixar o estoque. Assim, a regra "o saldo só diminui em um lugar" vale tanto para a saída avulsa quanto para a venda.

## 4. Como funciona uma venda (teste de mesa)

A função `efetivar_venda`, em `loja/caixa.py`, executa em **duas passadas**:

- A **primeira passada** só confere. Para cada produto, compara o saldo com a quantidade **total** daquele produto no carrinho.
- A **segunda passada** baixa o estoque.

Se algum produto não tiver saldo, a função devolve `None` antes de alterar qualquer coisa: a venda é **tudo-ou-nada**.

```python
if len(carrinho) == 0:
    return None
# 1ª passada: só confere; nenhuma alteração no estado.
for item in carrinho:
    produto = cadastro.buscar_produto(produtos, item["codigo"])
    quantidade_total = quantidade_no_carrinho(carrinho, item["codigo"])
    if produto is None or not estoque.tem_saldo_suficiente(produto, quantidade_total):
        return None
# 2ª passada: agora sim baixa o estoque de cada item.
numero = len(vendas) + 1
for item in carrinho:
    produto = cadastro.buscar_produto(produtos, item["codigo"])
    estoque.registrar_saida(produto, item["quantidade"], movimentacoes, data,
                            estoque.TIPO_VENDA, "venda " + str(numero))
itens = []
for item in carrinho:
    itens.append(item.copy())
venda = {
    "numero": numero,
    "data": data,
    "itens": itens,
    "total_centavos": calcular_total(itens),
}
vendas.append(venda)
```

**Teste de mesa da venda 1 dos dados de exemplo.** Estado inicial: Caderno com saldo 50 (preço 1999), Caneta com saldo 97 (preço 250), nenhuma venda.

| Passo | Instrução | `item` | Variáveis / estado depois do passo |
|-------|-----------|--------|------------------------------------|
| 1 | `adicionar_ao_carrinho(carrinho, caderno, 3)` | — | carrinho = [Caderno ×3, subtotal 5997] |
| 2 | `adicionar_ao_carrinho(carrinho, caneta, 5)` | — | carrinho = [Caderno ×3 (5997), Caneta ×5 (1250)] |
| 3 | 1ª passada, volta 1 | Caderno | quantidade_total = 3; saldo 50 ≥ 3 → continua (nada muda) |
| 4 | 1ª passada, volta 2 | Caneta | quantidade_total = 5; saldo 97 ≥ 5 → continua (nada muda) |
| 5 | `numero = len(vendas) + 1` | — | numero = 1 |
| 6 | 2ª passada, volta 1 | Caderno ×3 | **saldo Caderno 50 → 47**; movimentações +1 (VENDA) |
| 7 | 2ª passada, volta 2 | Caneta ×5 | **saldo Caneta 97 → 92**; movimentações +1 (VENDA) |
| 8 | `itens.append(item.copy())` (2 voltas) | — | itens = cópias dos 2 itens do carrinho |
| 9 | `calcular_total(itens)` | — | total_centavos: 0 → 5997 → 7247 |
| 10 | `vendas.append(venda)` | — | vendas = [venda 1, total 7247 = **R$ 72,47**] |

**E se faltar saldo?** Com o carrinho [Caderno ×3, Caneta ×100], a volta 2 da 1ª passada testa `97 ≥ 100`, que é falso. A função devolve `None` ali mesmo, nenhuma linha da 2ª passada é executada, e os saldos continuam 50 e 97. O teste "primeiro item não baixou (tudo-ou-nada)", em `testes.py`, comprova esse comportamento.

**Teste de mesa da leitura do preço "19,99"** (`leitura.texto_para_centavos`):

| Instrução | Valor |
|-----------|-------|
| `texto = texto.strip().replace(",", ".")` | `"19.99"` |
| `partes = texto.split(".")` | `["19", "99"]` |
| `parte_reais = partes[0]` / `parte_centavos = partes[1]` | `"19"` / `"99"` |
| validações (`isdecimal`, 2 casas, até 6 dígitos) | passam |
| `int(parte_reais) * 100 + int(parte_centavos)` | `1999` |

## 5. Conceitos do paradigma aplicados a este código

### 5.1 Por que é imperativo, e não orientado a objetos nem funcional

- **Imperativo/procedural:** **dados e procedimentos ficam separados**. O produto é um registro passivo (um dicionário), e funções externas o recebem e o alteram passo a passo (`estoque.registrar_saida(produto, ...)`).
- **Orientação a objetos:** haveria uma classe `Produto`, com o estado encapsulado, e um método `produto.baixar(quantidade)`. O comportamento ficaria junto do dado. O dicionário não tem métodos próprios nem encapsulamento.
- **Estilo funcional:** não haveria mutação. `registrar_entrada` devolveria um produto **novo** em vez de fazer `produto["saldo"] = ...`, e as repetições seriam feitas com recursão, `map`/`filter` ou *comprehensions*. Aqui, as repetições são laços `while`/`for` explícitos, e o estado muda por atribuição.
- **Equivalente em C:**
  - cada dicionário faria o papel de uma `struct` (por exemplo, `struct Produto { int codigo; char nome[31]; int preco_centavos; int saldo; }`);
  - a lista seria um vetor de `struct` com um contador de posições em uso;
  - passar a lista para uma função seria como passar um ponteiro para o vetor e um ponteiro para o contador (ou um ponteiro para uma `struct` que guarde os dois), para que a função também possa acrescentar elementos;
  - passar um produto seria como passar `struct Produto *p`, e não a `struct` por valor, que em C seria copiada (e aí a alteração do saldo não valeria fora da função).

### 5.2 A ordem das instruções importa

- **Em `estoque.registrar_entrada`,** a movimentação é criada **depois** da atribuição do saldo. `criar_movimentacao` grava `"saldo_apos": produto["saldo"]`, ou seja, lê o saldo **naquele momento**. Com a ordem invertida, o histórico guardaria o saldo antigo. O teste "movimentação guarda o saldo após" (10 + 5 → 15) pega esse erro.
- **Em `caixa.efetivar_venda`,** `numero = len(vendas) + 1` é calculado **antes** de `vendas.append(venda)`.
- **Em `telas.cadastrar_produto`,** o produto é criado com saldo 0. Se o saldo inicial for maior que 0, logo em seguida é registrada uma ENTRADA "saldo inicial". Assim, o saldo só aumenta num lugar (`registrar_entrada`), e o saldo de cada produto é sempre igual à soma das suas movimentações (entradas menos saídas e vendas).

### 5.3 Cópias e aliasing

**Aliasing** é quando dois nomes apontam para o mesmo objeto. Às vezes ele é desejado: `buscar_produto` devolve o próprio dicionário da lista justamente para que a alteração do saldo valha no estoque. Em outros casos, seria perigoso, e o código **copia de propósito**:

- **Ao entrar no carrinho**, o item copia o **nome e o preço** do produto (`caixa.adicionar_ao_carrinho`). Se o preço do produto mudar depois, a venda continua com o preço daquele momento ("preço congelado"). O teste "preço fica congelado no item" comprova isso.
- **Ao registrar a venda**, `efetivar_venda` monta uma lista nova, `itens`, com cópias de cada item (`itens.append(item.copy())`). Por isso, limpar o carrinho ou alterar um item dele depois não muda a venda registrada. Os testes comprovam as duas partes:
  - "venda guarda cópia dos itens (limpar o carrinho não a altera)": a venda não usa a mesma lista;
  - "alterar um item do carrinho não altera a venda": cada item foi copiado.

  O `.copy()` faz uma cópia **rasa**: copia o dicionário, mas não o que está dentro dele. Isso basta aqui, porque os valores do item são números e textos, que são imutáveis.

### 5.4 Valor sentinela -1 na leitura de números

`leitura.texto_para_inteiro` e `leitura.texto_para_centavos` devolvem `-1` quando o texto é inválido:

- **Por que o `-1` funciona:** todo valor válido é maior ou igual a 0. O `isdecimal()` já recusa sinal, espaços internos e notação científica.
- **O ganho:** a conversão fica sendo uma função sem efeito colateral (não lê o teclado nem imprime), e por isso pode ser testada automaticamente.
- **Quem decide o que fazer com o `-1`** é a função de leitura. Em `ler_inteiro`, uma decisão de três caminhos (`if/elif/else`) separa valor inválido, valor abaixo do mínimo e valor válido.

## 6. Perguntas frequentes sobre as decisões

- **Por que centavos inteiros?** Números com casas decimais (`float`) têm erro de representação: `int(0.29 * 100)` dá `28`. Com centavos inteiros, as contas são exatas.
- **Por que a venda tem duas passadas?** Para que uma venda nunca fique pela metade. Se a baixa fosse feita item a item, o primeiro item poderia baixar o estoque e o segundo falhar. A 1ª passada confere o total de cada produto. A 2ª só é executada se tudo passou e, como o programa é sequencial e nada muda entre as passadas, ela nunca encontra falta de saldo.
- **Por que passar as listas como parâmetro, e não usar `global`?** Fica visível o que cada função pode alterar (por exemplo, `efetivar_venda(produtos, vendas, movimentacoes, carrinho, data)`), e as regras podem ser testadas com listas criadas no próprio teste.
- **Por que o preço é copiado para o item da venda?** Para "congelar" o preço do momento da venda. Se o preço do produto mudar depois, os comprovantes e relatórios antigos continuam corretos.
- **Por que `formatar_moeda` trata número negativo, se não há valores negativos?** Em Python, `-150 // 100` dá `-2`, porque a divisão inteira arredonda para baixo, e sairia `R$ -2,50`. Tratar o sinal antes custa duas linhas e deixa a função correta para qualquer inteiro.
- **Por que o programa salva de novo ao sair, se já salva depois de cada operação?** É uma redundância barata. Ela atende ao requisito "salvar ao sair" e tenta gravar mais uma vez caso um salvamento anterior tenha falhado (por exemplo, com o arquivo aberto em outro programa).
- **Como os dados são salvos?** Em `persistencia.salvar_dados`, o texto JSON é montado na memória, gravado num arquivo `.tmp` e trocado de uma vez com `os.replace`. Assim, o arquivo de dados nunca fica pela metade.
