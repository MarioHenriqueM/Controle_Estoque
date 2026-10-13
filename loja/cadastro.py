"""Cadastro de produtos: criar o registro, buscar por código e cadastrar sem duplicar.

Regras sem tela: recebem a lista de produtos por parâmetro e não usam input()/print().
"""


def criar_produto(codigo, nome, preco_centavos, saldo):
    """Monta e devolve o registro (dicionário) de um produto. Preço em centavos (int)."""
    produto = {"codigo": codigo, "nome": nome, "preco_centavos": preco_centavos, "saldo": saldo}
    return produto


def buscar_produto(produtos, codigo):
    """Procura o produto pelo código, percorrendo a lista (busca linear).
    Devolve o PRÓPRIO dicionário que está na lista (não uma cópia), ou None se não achar."""
    for produto in produtos:
        if produto["codigo"] == codigo:
            return produto
    return None


def cadastrar_produto(produtos, codigo, nome, preco_centavos, saldo_inicial):
    """Altera: produtos (acrescenta 1 registro no fim da lista).
    Retorna: o produto criado, ou None (sem alterar nada) se o código já existe."""
    if buscar_produto(produtos, codigo) is not None:
        return None
    novo = criar_produto(codigo, nome, preco_centavos, saldo_inicial)
    produtos.append(novo)
    return novo
