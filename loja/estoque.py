"""Movimentações de estoque: entrada, saída (avulsa e de venda) e histórico.

É o ÚNICO lugar do programa onde o saldo de um produto muda:
- registrar_entrada  -> o saldo AUMENTA;
- registrar_saida    -> o saldo DIMINUI (usado pela saída avulsa e pela venda).
Cada mudança gera um registro na lista de movimentações (histórico).
Regras sem tela: não usam input()/print() e recebem a data pronta.
"""

TIPO_ENTRADA = "ENTRADA"
TIPO_SAIDA = "SAIDA"
TIPO_VENDA = "VENDA"
MOTIVO_COMPRA = "compra"
MOTIVO_SALDO_INICIAL = "saldo inicial"
MOTIVOS_SAIDA = ("perda", "avaria", "uso interno")    # tupla: constante que não muda


def criar_movimentacao(data, tipo, produto, quantidade, motivo):
    """Monta e devolve o registro de uma movimentação, com o saldo já atualizado."""
    movimentacao = {
        "data": data,
        "tipo": tipo,
        "codigo": produto["codigo"],
        "quantidade": quantidade,
        "motivo": motivo,
        "saldo_apos": produto["saldo"],
    }
    return movimentacao


def tem_saldo_suficiente(produto, quantidade):
    """Devolve True se o produto tem pelo menos 'quantidade' unidades em estoque."""
    return produto["saldo"] >= quantidade


def registrar_entrada(produto, quantidade, movimentacoes, data, motivo):
    """Único ponto onde o saldo AUMENTA.
    Altera: produto["saldo"] e movimentacoes (acrescenta 1 registro)."""
    produto["saldo"] = produto["saldo"] + quantidade
    registro = criar_movimentacao(data, TIPO_ENTRADA, produto, quantidade, motivo)
    movimentacoes.append(registro)


def registrar_saida(produto, quantidade, movimentacoes, data, tipo, motivo):
    """Único ponto onde o saldo DIMINUI (saída avulsa e venda).
    Altera: produto["saldo"] e movimentacoes (acrescenta 1 registro).
    Retorna: True se baixou; False (sem alterar nada) se o saldo não basta."""
    if not tem_saldo_suficiente(produto, quantidade):
        return False
    produto["saldo"] = produto["saldo"] - quantidade
    registro = criar_movimentacao(data, tipo, produto, quantidade, motivo)
    movimentacoes.append(registro)
    return True


def extrato_do_produto(movimentacoes, codigo):
    """Devolve uma lista nova só com as movimentações do produto, em ordem cronológica."""
    extrato = []
    for movimentacao in movimentacoes:
        if movimentacao["codigo"] == codigo:
            extrato.append(movimentacao)
    return extrato
