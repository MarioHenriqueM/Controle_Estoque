"""Telas do programa: uma função para cada opção do menu.

Cada tela pergunta os dados (usando o módulo leitura), chama a regra
correspondente e mostra o resultado. As telas que alteram o estado
devolvem True, para que o main.py saiba que precisa salvar os dados.
"""

import datetime

from loja import cadastro
from loja import estoque
from loja import formatacao
from loja import leitura

MAXIMO_CARACTERES_NOME = 30


def data_hora_atual():
    """Devolve a data e a hora atuais no formato dd/mm/aaaa hh:mm."""
    agora = datetime.datetime.now()
    return agora.strftime("%d/%m/%Y %H:%M")


def mostrar_menu():
    print()
    print("========= CONTROLE DE ESTOQUE E VENDAS =========")
    print("1 - Cadastrar produto")
    print("2 - Registrar entrada de itens")
    print("3 - Registrar saída avulsa (perda, avaria, uso interno)")
    print("4 - Registrar venda")
    print("5 - Consultar saldo de um produto")
    print("6 - Listar estoque")
    print("7 - Relatórios")
    print("0 - Sair")


def opcao_em_construcao():
    print("Esta opção ainda está em desenvolvimento.")


def escolher_produto(produtos):
    """Pede o código e devolve o produto encontrado, ou None (com aviso) se não existir."""
    if len(produtos) == 0:
        print("Nenhum produto cadastrado.")
        return None
    codigo = leitura.ler_inteiro("Código do produto: ", 1)
    produto = cadastro.buscar_produto(produtos, codigo)
    if produto is None:
        print("Produto não encontrado.")
        return None
    nome = produto["nome"]
    saldo = produto["saldo"]
    print(f"Produto: {nome} (saldo atual: {saldo})")
    return produto


def escolher_motivo_saida():
    """Mostra os motivos de saída avulsa numerados e devolve o motivo escolhido."""
    print("Motivo da saída:")
    numero = 1
    for motivo in estoque.MOTIVOS_SAIDA:
        print(f"  {numero} - {motivo}")
        numero = numero + 1
    quantidade_motivos = len(estoque.MOTIVOS_SAIDA)
    opcao = 0
    while opcao < 1 or opcao > quantidade_motivos:
        opcao = leitura.ler_inteiro("Escolha o motivo: ", 1)
        if opcao > quantidade_motivos:
            print("Motivo inválido.")
    return estoque.MOTIVOS_SAIDA[opcao - 1]


def cadastrar_produto(produtos, movimentacoes):
    """Opção 1: cadastra um produto novo. O saldo inicial entra no estoque
    como uma movimentação de ENTRADA (motivo 'saldo inicial').
    Retorna: True se cadastrou (o estado foi alterado)."""
    print()
    print("--- Cadastro de produto ---")
    codigo = leitura.ler_inteiro("Código do produto: ", 1)
    if cadastro.buscar_produto(produtos, codigo) is not None:
        print(f"Já existe um produto com o código {codigo}. Cadastro cancelado.")
        return False
    nome = leitura.ler_texto("Nome: ", MAXIMO_CARACTERES_NOME)
    preco_centavos = leitura.ler_preco_centavos("Preço de venda (ex.: 19,99): ")
    saldo_inicial = leitura.ler_inteiro("Saldo inicial em estoque: ", 0)
    quantidade_antes = len(produtos)
    produto = cadastro.cadastrar_produto(produtos, codigo, nome, preco_centavos, 0)
    if saldo_inicial > 0:
        estoque.registrar_entrada(produto, saldo_inicial, movimentacoes,
                                  data_hora_atual(), estoque.MOTIVO_SALDO_INICIAL)
    quantidade_depois = len(produtos)
    preco = formatacao.formatar_moeda(preco_centavos)
    saldo = produto["saldo"]
    print(f"Produto cadastrado: {nome} ({preco}), saldo {saldo}.")
    print(f"Produtos cadastrados: {quantidade_antes} -> {quantidade_depois}")
    return True


def registrar_entrada(produtos, movimentacoes):
    """Opção 2: entrada de itens no estoque (ex.: compra de mercadoria).
    Retorna: True se alterou o estado."""
    print()
    print("--- Entrada de itens ---")
    produto = escolher_produto(produtos)
    if produto is None:
        return False
    saldo_antes = produto["saldo"]
    quantidade = leitura.ler_inteiro("Quantidade que entrou: ", 1)
    estoque.registrar_entrada(produto, quantidade, movimentacoes,
                              data_hora_atual(), estoque.MOTIVO_COMPRA)
    nome = produto["nome"]
    saldo_depois = produto["saldo"]
    print(f"Entrada registrada. Saldo de {nome}: {saldo_antes} -> {saldo_depois}")
    return True


def registrar_saida(produtos, movimentacoes):
    """Opção 3: saída avulsa (perda, avaria ou uso interno). NÃO gera receita.
    Retorna: True se alterou o estado."""
    print()
    print("--- Saída avulsa ---")
    produto = escolher_produto(produtos)
    if produto is None:
        return False
    saldo_antes = produto["saldo"]
    quantidade = leitura.ler_inteiro("Quantidade que vai sair: ", 1)
    if not estoque.tem_saldo_suficiente(produto, quantidade):
        print(f"Saldo insuficiente (há {saldo_antes} unidade(s)). Nada foi alterado.")
        return False
    motivo = escolher_motivo_saida()
    registrou = estoque.registrar_saida(produto, quantidade, movimentacoes,
                                        data_hora_atual(), estoque.TIPO_SAIDA, motivo)
    if not registrou:
        print(f"Saldo insuficiente (há {saldo_antes} unidade(s)). Nada foi alterado.")
        return False
    nome = produto["nome"]
    saldo_depois = produto["saldo"]
    print(f"Saída registrada ({motivo}). Saldo de {nome}: {saldo_antes} -> {saldo_depois}")
    return True


def consultar_saldo(produtos, movimentacoes):
    """Opção 5: mostra o saldo atual de um produto e o extrato de movimentações."""
    print()
    print("--- Consulta de saldo ---")
    produto = escolher_produto(produtos)
    if produto is None:
        return
    print(formatacao.cabecalho_produtos())
    print(formatacao.linha_produto(produto))
    print()
    print("Extrato de movimentações:")
    extrato = estoque.extrato_do_produto(movimentacoes, produto["codigo"])
    if len(extrato) == 0:
        print("Nenhuma movimentação registrada para este produto.")
        return
    print(formatacao.cabecalho_extrato())
    for movimentacao in extrato:
        print(formatacao.linha_extrato(movimentacao))


def listar_estoque(produtos):
    """Opção 6: lista todos os produtos em uma tabela."""
    print()
    print("--- Estoque ---")
    if len(produtos) == 0:
        print("Nenhum produto cadastrado.")
        return
    print(formatacao.cabecalho_produtos())
    total_unidades = 0
    for produto in produtos:
        print(formatacao.linha_produto(produto))
        total_unidades = total_unidades + produto["saldo"]
    quantidade_produtos = len(produtos)
    print(f"{quantidade_produtos} produto(s), {total_unidades} unidade(s) em estoque.")
