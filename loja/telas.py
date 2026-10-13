"""Telas do programa: uma função para cada opção do menu.

Cada tela pergunta os dados (usando o módulo leitura), chama a regra
correspondente e mostra o resultado. As telas que alteram o estado
devolvem True, para que o main.py saiba que precisa salvar os dados.
"""

import datetime

from loja import cadastro
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


def cadastrar_produto(produtos):
    """Opção 1: cadastra um produto novo.
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
    cadastro.cadastrar_produto(produtos, codigo, nome, preco_centavos, saldo_inicial)
    quantidade_depois = len(produtos)
    preco = formatacao.formatar_moeda(preco_centavos)
    print(f"Produto cadastrado: {nome} ({preco}), saldo inicial {saldo_inicial}.")
    print(f"Produtos cadastrados: {quantidade_antes} -> {quantidade_depois}")
    return True


def consultar_saldo(produtos):
    """Opção 5: mostra o saldo atual de um produto."""
    print()
    print("--- Consulta de saldo ---")
    if len(produtos) == 0:
        print("Nenhum produto cadastrado.")
        return
    codigo = leitura.ler_inteiro("Código do produto: ", 1)
    produto = cadastro.buscar_produto(produtos, codigo)
    if produto is None:
        print("Produto não encontrado.")
        return
    print(formatacao.cabecalho_produtos())
    print(formatacao.linha_produto(produto))


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
