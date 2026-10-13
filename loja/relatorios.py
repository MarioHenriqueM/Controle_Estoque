"""Relatórios de valores: faturamento, vendas por produto e valor do estoque.

Cálculos com acumuladores dentro de laços. Não imprimem nada: devolvem
números e listas para a tela mostrar. Dinheiro em centavos (int).
Só a lista de VENDAS entra no faturamento (saída avulsa não é receita).
"""


def faturamento_total(vendas):
    """Soma o total de todas as vendas registradas."""
    total_centavos = 0
    for venda in vendas:
        total_centavos = total_centavos + venda["total_centavos"]
    return total_centavos


def ticket_medio_centavos(faturamento_centavos, quantidade_vendas):
    """Valor médio por venda, arredondado para o centavo mais próximo (sem float).
    Devolve 0 quando não há vendas (evita divisão por zero)."""
    if quantidade_vendas == 0:
        return 0
    return (faturamento_centavos + quantidade_vendas // 2) // quantidade_vendas


def vendas_por_produto(produtos, vendas):
    """Para cada produto cadastrado (inclusive os que não venderam), soma as unidades
    vendidas e o valor vendido, usando os itens gravados (com o preço do momento da venda).
    Devolve uma lista de dicionários {codigo, nome, unidades, valor_centavos}."""
    resumo = []
    for produto in produtos:
        unidades = 0
        valor_centavos = 0
        for venda in vendas:
            for item in venda["itens"]:
                if item["codigo"] == produto["codigo"]:
                    unidades = unidades + item["quantidade"]
                    valor_centavos = valor_centavos + item["subtotal_centavos"]
        linha = {"codigo": produto["codigo"], "nome": produto["nome"],
                 "unidades": unidades, "valor_centavos": valor_centavos}
        resumo.append(linha)
    return resumo


def valor_do_estoque(produtos):
    """Calcula saldo x preço de cada produto (a preço de venda) e o total geral.
    Devolve (lista de {codigo, nome, saldo, valor_centavos}, total_centavos)."""
    linhas = []
    total_centavos = 0
    for produto in produtos:
        valor_centavos = produto["saldo"] * produto["preco_centavos"]
        linha = {"codigo": produto["codigo"], "nome": produto["nome"],
                 "saldo": produto["saldo"], "valor_centavos": valor_centavos}
        linhas.append(linha)
        total_centavos = total_centavos + valor_centavos
    return linhas, total_centavos
