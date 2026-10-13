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

As listas são **passadas como parâmetro** para as funções que precisam delas, e o programa não usa variáveis globais. Assim, a assinatura da função mostra o que ela pode modificar.

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

- **Interação** (`leitura`, `telas`, `formatacao`): são os únicos módulos que conversam com o usuário.
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

**`main.py`, função `main`:** a sequência do programa inteiro (carregar → avisar → executar o menu).

```python
produtos, vendas, movimentacoes, aviso = persistencia.carregar_dados(CAMINHO_DADOS, CAMINHO_EXEMPLO)
if aviso != "":
    print(aviso)
try:
    executar_menu(produtos, vendas, movimentacoes)
```

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

- **`while` com variável de controle:**
  - o menu principal (`while executando:` em `main.executar_menu`);
  - o carrinho da venda (`while montando:` em `telas.registrar_venda`);
  - as leituras validadas (`while not valido:` em `leitura.ler_inteiro`), que repetem a pergunta até o valor ser válido.
- **`for` percorrendo uma lista:**
  - busca linear do produto (`cadastro.buscar_produto`):

    ```python
    for produto in produtos:
        if produto["codigo"] == codigo:
            return produto
    return None
    ```
  - acumuladores (`caixa.calcular_total`, `relatorios.faturamento_total`).
- **Laços aninhados**, em `loja/relatorios.py`, função `vendas_por_produto`: para cada produto, percorre todas as vendas e todos os itens de cada venda, somando unidades e valores.

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

### 2.5 Funções e procedimentos

O programa é dividido em funções pequenas, cada uma com uma tarefa:

- **Funções que calculam e devolvem um valor** (`return`): `calcular_subtotal`, `calcular_total`, `formatar_moeda`, `texto_para_centavos`, `buscar_produto`, `tem_saldo_suficiente`, `faturamento_total`.
- **Procedimentos que alteram o estado recebido:** `registrar_entrada`, `registrar_saida`, `cadastrar_produto`, `adicionar_ao_carrinho`, `remover_do_carrinho` e `efetivar_venda`. A docstring de cada um diz o que ele altera (`Altera: ...`).

Em Python, listas e dicionários passados como parâmetro **não são copiados**: a função recebe uma referência ao mesmo objeto. Por isso `buscar_produto` devolve o próprio dicionário que está na lista `produtos`, e a atribuição `produto["saldo"] = ...` em `estoque` altera de fato o estoque. O teste "busca devolve o próprio registro da lista", em `testes.py`, comprova isso.

## 3. Mapa de mutações: onde cada parte do estado muda

| Mudança | Único lugar no código | Elementos usados |
|---------|----------------------|------------------|
| Produto novo | `cadastro.cadastrar_produto` → `produtos.append(novo)` | decisão (código já existe?) + alteração da lista |
| Saldo aumenta | `estoque.registrar_entrada` → `produto["saldo"] = produto["saldo"] + quantidade` | atribuição |
| Saldo diminui | `estoque.registrar_saida` → `produto["saldo"] = produto["saldo"] - quantidade` | decisão (saldo basta?) + atribuição |
| Histórico cresce | `estoque.registrar_entrada` / `registrar_saida` → `movimentacoes.append(registro)` | alteração da lista |
| Carrinho (temporário) | `caixa.adicionar_ao_carrinho` / `caixa.remover_do_carrinho` | repetição + decisão + atribuição |
| Venda registrada | `caixa.efetivar_venda` → `vendas.append(venda)` | 2 laços + decisões + chamada de procedimento |
| Fim do programa | `main.executar_menu` → `executando = False` | variável de controle do laço |

A venda **reaproveita** `estoque.registrar_saida` para baixar o estoque. Assim, a regra "o saldo só diminui em um lugar" vale tanto para a saída avulsa quanto para a venda.

## 4. Como funciona uma venda (teste de mesa)

`loja/caixa.py`, função `efetivar_venda`, executa em **duas passadas**. A primeira só confere o saldo de todos os itens. A segunda baixa o estoque. Se algum item não tiver saldo, a função devolve `None` antes de alterar qualquer coisa (venda **tudo-ou-nada**).

```python
# 1ª passada: só confere; nenhuma alteração no estado
for item in carrinho:
    produto = cadastro.buscar_produto(produtos, item["codigo"])
    if produto is None or not estoque.tem_saldo_suficiente(produto, item["quantidade"]):
        return None
# 2ª passada: agora sim baixa o estoque de cada item
numero = len(vendas) + 1
for item in carrinho:
    produto = cadastro.buscar_produto(produtos, item["codigo"])
    estoque.registrar_saida(produto, item["quantidade"], movimentacoes, data,
                            estoque.TIPO_VENDA, "venda " + str(numero))
venda = {"numero": numero, "data": data, "itens": carrinho, "total_centavos": calcular_total(carrinho)}
vendas.append(venda)
```

**Teste de mesa da venda 1 dos dados de exemplo.** Estado inicial: Caderno com saldo 50 (preço 1999), Caneta com saldo 97 (preço 250), nenhuma venda.

| Passo | Instrução | `item` | Variáveis / estado depois do passo |
|-------|-----------|--------|------------------------------------|
| 1 | `adicionar_ao_carrinho(carrinho, caderno, 3)` | — | carrinho = [Caderno ×3, subtotal 5997] |
| 2 | `adicionar_ao_carrinho(carrinho, caneta, 5)` | — | carrinho = [Caderno ×3 (5997), Caneta ×5 (1250)] |
| 3 | 1ª passada, volta 1 | Caderno ×3 | saldo 50 ≥ 3 → continua (nada muda) |
| 4 | 1ª passada, volta 2 | Caneta ×5 | saldo 97 ≥ 5 → continua (nada muda) |
| 5 | `numero = len(vendas) + 1` | — | numero = 1 |
| 6 | 2ª passada, volta 1 | Caderno ×3 | **saldo Caderno 50 → 47**; movimentações +1 (VENDA) |
| 7 | 2ª passada, volta 2 | Caneta ×5 | **saldo Caneta 97 → 92**; movimentações +1 (VENDA) |
| 8 | `calcular_total(carrinho)` | — | total_centavos: 0 → 5997 → 7247 |
| 9 | `vendas.append(venda)` | — | vendas = [venda 1, total 7247 = **R$ 72,47**] |

**Teste de mesa da leitura do preço "19,99"** (`leitura.texto_para_centavos`):

| Instrução | Valor |
|-----------|-------|
| `texto = texto.strip().replace(",", ".")` | `"19.99"` |
| `partes = texto.split(".")` | `["19", "99"]` |
| `parte_reais = partes[0]` / `parte_centavos = partes[1]` | `"19"` / `"99"` |
| validações (`isdecimal`, 2 casas, até 6 dígitos) | passam |
| `int(parte_reais) * 100 + int(parte_centavos)` | `1999` |

## 5. Decisões que o professor pode perguntar

- **Por que centavos inteiros?** Números com casas decimais (`float`) têm erro de representação: `int(0.29 * 100)` dá `28`. Em centavos inteiros, as contas são exatas.
- **Por que a venda tem duas passadas?** Para que uma venda nunca fique pela metade. Se o segundo item não tiver saldo, o primeiro já teria baixado o estoque. Conferindo tudo antes, ou baixa tudo ou não baixa nada.
- **Por que passar as listas como parâmetro, e não usar `global`?** Fica visível o que cada função altera, e as regras podem ser testadas com listas criadas no próprio teste.
- **O que `buscar_produto` devolve?** O próprio dicionário que está na lista (não uma cópia). Alterar `produto["saldo"]` altera o estoque.
- **Por que o preço é copiado para o item da venda?** Para "congelar" o preço do momento da venda. Se o preço do produto mudar depois, os comprovantes e relatórios antigos continuam corretos.
- **Como os dados são salvos?** Em `persistencia.salvar_dados`: o texto JSON é montado na memória, gravado num arquivo `.tmp` e trocado de uma vez com `os.replace`, para nunca deixar o arquivo de dados pela metade.
