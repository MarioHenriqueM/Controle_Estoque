"""Caixa: monta o carrinho e registra a venda com vários itens.

O carrinho é uma lista LOCAL da tela de venda: montar o carrinho não muda
o estoque. Só efetivar_venda altera o estado, no modo TUDO-OU-NADA.
Regras sem tela: não usam input()/print(). Dinheiro em centavos (int).
"""

from loja import cadastro
from loja import estoque


def calcular_subtotal(quantidade, preco_unitario_centavos):
    """Devolve quantidade x preço unitário (em centavos)."""
    return quantidade * preco_unitario_centavos


def calcular_total(itens):
    """Soma os subtotais de todos os itens (acumulador)."""
    total_centavos = 0
    for item in itens:
        total_centavos = total_centavos + item["subtotal_centavos"]
    return total_centavos


def quantidade_no_carrinho(carrinho, codigo):
    """Soma quantas unidades do produto já estão no carrinho (0 se nenhuma)."""
    quantidade = 0
    for item in carrinho:
        if item["codigo"] == codigo:
            quantidade = quantidade + item["quantidade"]
    return quantidade


def adicionar_ao_carrinho(carrinho, produto, quantidade):
    """Altera: carrinho. Se o produto já está no carrinho, soma no mesmo item.
    O nome e o preço são COPIADOS do produto: ficam congelados no item."""
    for item in carrinho:
        if item["codigo"] == produto["codigo"]:
            item["quantidade"] = item["quantidade"] + quantidade
            item["subtotal_centavos"] = calcular_subtotal(item["quantidade"], item["preco_unitario_centavos"])
            return
    novo_item = {
        "codigo": produto["codigo"],
        "nome": produto["nome"],
        "quantidade": quantidade,
        "preco_unitario_centavos": produto["preco_centavos"],
        "subtotal_centavos": calcular_subtotal(quantidade, produto["preco_centavos"]),
    }
    carrinho.append(novo_item)


def remover_do_carrinho(carrinho, codigo):
    """Altera: carrinho (tira o item do produto informado).
    Retorna: True se removeu; False se o produto não estava no carrinho."""
    posicao = 0
    while posicao < len(carrinho):
        if carrinho[posicao]["codigo"] == codigo:
            carrinho.pop(posicao)
            return True
        posicao = posicao + 1
    return False


def efetivar_venda(produtos, vendas, movimentacoes, carrinho, data):
    """Registra a venda no modo TUDO-OU-NADA.
    Altera: saldo dos produtos, movimentacoes e vendas.
    Retorna: o registro da venda, ou None (sem alterar nada) se algum item não tiver saldo."""
    if len(carrinho) == 0:
        return None
    # 1ª passada: só confere; nenhuma alteração no estado.
    # Compara o saldo com o TOTAL do produto no carrinho (soma de todos os itens dele).
    for item in carrinho:
        produto = cadastro.buscar_produto(produtos, item["codigo"])
        quantidade_total = quantidade_no_carrinho(carrinho, item["codigo"])
        if produto is None or not estoque.tem_saldo_suficiente(produto, quantidade_total):
            return None
    # 2ª passada: agora sim baixa o estoque de cada item.
    # Não falha: a 1ª passada já conferiu o total de cada produto e nada mudou desde então.
    numero = len(vendas) + 1
    for item in carrinho:
        produto = cadastro.buscar_produto(produtos, item["codigo"])
        estoque.registrar_saida(produto, item["quantidade"], movimentacoes, data,
                                estoque.TIPO_VENDA, "venda " + str(numero))
    # A venda guarda CÓPIAS dos itens: depois de registrada, ela não muda
    # mesmo que a lista carrinho (ou um item dela) seja alterada.
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
    return venda
