"""Testes automáticos das regras e cálculos do sistema.

Execute com:  python testes.py
Cada teste compara o valor obtido com o esperado usando verificar().
O programa termina com código 0 se tudo passou e 1 se algo falhou.
"""

import os
import shutil
import sys
import tempfile

from loja import cadastro
from loja import caixa
from loja import estoque
from loja import formatacao
from loja import leitura
from loja import persistencia


def verificar(descricao, obtido, esperado):
    """Mostra o resultado e devolve 1 se falhou, 0 se passou."""
    if obtido == esperado:
        print("[OK]    " + descricao)
        return 0
    print("[FALHA] " + descricao + " | esperado: " + repr(esperado) + " | obtido: " + repr(obtido))
    return 1


def testar_texto_para_inteiro():
    falhas = 0
    falhas = falhas + verificar("inteiro com espaços", leitura.texto_para_inteiro(" 42 "), 42)
    falhas = falhas + verificar("inteiro com zeros à esquerda", leitura.texto_para_inteiro("007"), 7)
    falhas = falhas + verificar("texto não numérico é inválido", leitura.texto_para_inteiro("abc"), -1)
    falhas = falhas + verificar("número negativo é inválido", leitura.texto_para_inteiro("-5"), -1)
    falhas = falhas + verificar("vazio é inválido", leitura.texto_para_inteiro(""), -1)
    falhas = falhas + verificar("mais de 6 dígitos é inválido", leitura.texto_para_inteiro("1234567"), -1)
    return falhas


def testar_texto_para_centavos():
    falhas = 0
    falhas = falhas + verificar("preço com vírgula", leitura.texto_para_centavos("19,99"), 1999)
    falhas = falhas + verificar("preço com ponto", leitura.texto_para_centavos("12.50"), 1250)
    falhas = falhas + verificar("preço com uma casa", leitura.texto_para_centavos("12,5"), 1250)
    falhas = falhas + verificar("preço inteiro", leitura.texto_para_centavos("12"), 1200)
    falhas = falhas + verificar("0,29 sem erro de float", leitura.texto_para_centavos("0,29"), 29)
    falhas = falhas + verificar("três casas é inválido", leitura.texto_para_centavos("12,345"), -1)
    falhas = falhas + verificar("separador de milhar é inválido", leitura.texto_para_centavos("1.234,56"), -1)
    falhas = falhas + verificar("notação científica é inválida", leitura.texto_para_centavos("1e3"), -1)
    falhas = falhas + verificar("preço negativo é inválido", leitura.texto_para_centavos("-5,00"), -1)
    falhas = falhas + verificar("reais com 7 dígitos é inválido", leitura.texto_para_centavos("1000000"), -1)
    return falhas


def testar_formatar_moeda():
    falhas = 0
    falhas = falhas + verificar("milhar com ponto", formatacao.formatar_moeda(123456), "R$ 1.234,56")
    falhas = falhas + verificar("só centavos", formatacao.formatar_moeda(5), "R$ 0,05")
    falhas = falhas + verificar("zero", formatacao.formatar_moeda(0), "R$ 0,00")
    falhas = falhas + verificar("3 x 19,99", formatacao.formatar_moeda(3 * 1999), "R$ 59,97")
    return falhas


def testar_cadastro():
    falhas = 0
    produtos = []
    novo = cadastro.cadastrar_produto(produtos, 1, "Caneta", 250, 10)
    falhas = falhas + verificar("cadastro acrescenta o produto", len(produtos), 1)
    falhas = falhas + verificar("preço guardado em centavos", novo["preco_centavos"], 250)
    repetido = cadastro.cadastrar_produto(produtos, 1, "Lápis", 150, 5)
    falhas = falhas + verificar("código duplicado é recusado", repetido, None)
    falhas = falhas + verificar("duplicado não altera a lista", len(produtos), 1)
    achado = cadastro.buscar_produto(produtos, 1)
    falhas = falhas + verificar("busca devolve o produto certo", achado["nome"], "Caneta")
    falhas = falhas + verificar("busca de código inexistente", cadastro.buscar_produto(produtos, 99), None)
    achado["saldo"] = 7
    falhas = falhas + verificar("busca devolve o próprio registro da lista", produtos[0]["saldo"], 7)
    return falhas


def testar_estoque():
    falhas = 0
    data = "13/10/2026 10:00"
    produto = cadastro.criar_produto(1, "Caneta", 250, 10)
    movimentacoes = []

    estoque.registrar_entrada(produto, 5, movimentacoes, data, estoque.MOTIVO_COMPRA)
    falhas = falhas + verificar("entrada aumenta o saldo (10 -> 15)", produto["saldo"], 15)
    falhas = falhas + verificar("entrada gera 1 movimentação", len(movimentacoes), 1)
    falhas = falhas + verificar("movimentação guarda o saldo após", movimentacoes[0]["saldo_apos"], 15)

    baixou = estoque.registrar_saida(produto, 3, movimentacoes, data, estoque.TIPO_SAIDA, "perda")
    falhas = falhas + verificar("saída com saldo suficiente é aceita", baixou, True)
    falhas = falhas + verificar("saída diminui o saldo (15 -> 12)", produto["saldo"], 12)
    falhas = falhas + verificar("saída registra o tipo SAIDA", movimentacoes[1]["tipo"], "SAIDA")

    baixou = estoque.registrar_saida(produto, 50, movimentacoes, data, estoque.TIPO_SAIDA, "avaria")
    falhas = falhas + verificar("saída maior que o saldo é recusada", baixou, False)
    falhas = falhas + verificar("saída recusada não altera o saldo", produto["saldo"], 12)
    falhas = falhas + verificar("saída recusada não gera movimentação", len(movimentacoes), 2)

    outro = cadastro.criar_produto(2, "Lápis", 150, 0)
    estoque.registrar_entrada(outro, 4, movimentacoes, data, estoque.MOTIVO_COMPRA)
    extrato = estoque.extrato_do_produto(movimentacoes, 1)
    falhas = falhas + verificar("extrato só traz o produto pedido", len(extrato), 2)
    return falhas


def testar_carrinho():
    falhas = 0
    caderno = cadastro.criar_produto(1, "Caderno", 1999, 10)
    caneta = cadastro.criar_produto(2, "Caneta", 500, 10)
    carrinho = []
    caixa.adicionar_ao_carrinho(carrinho, caderno, 2)
    caixa.adicionar_ao_carrinho(carrinho, caderno, 1)
    falhas = falhas + verificar("mesmo produto soma no mesmo item", len(carrinho), 1)
    falhas = falhas + verificar("quantidade somada (2 + 1)", caixa.quantidade_no_carrinho(carrinho, 1), 3)
    caixa.adicionar_ao_carrinho(carrinho, caneta, 2)
    falhas = falhas + verificar("subtotal 3 x R$ 19,99", carrinho[0]["subtotal_centavos"], 5997)
    falhas = falhas + verificar("total 3 x 19,99 + 2 x 5,00", caixa.calcular_total(carrinho), 6997)
    falhas = falhas + verificar("produto fora do carrinho tem 0", caixa.quantidade_no_carrinho(carrinho, 99), 0)
    caderno["preco_centavos"] = 2500
    falhas = falhas + verificar("preço fica congelado no item", carrinho[0]["preco_unitario_centavos"], 1999)
    removeu = caixa.remover_do_carrinho(carrinho, 2)
    falhas = falhas + verificar("remover item do carrinho", removeu, True)
    falhas = falhas + verificar("carrinho fica com 1 item", len(carrinho), 1)
    falhas = falhas + verificar("remover item ausente devolve False", caixa.remover_do_carrinho(carrinho, 2), False)
    return falhas


def testar_venda():
    falhas = 0
    data = "13/10/2026 10:00"
    produtos = [cadastro.criar_produto(1, "Caderno", 1999, 10), cadastro.criar_produto(2, "Caneta", 500, 4)]
    vendas = []
    movimentacoes = []
    carrinho = []
    caixa.adicionar_ao_carrinho(carrinho, produtos[0], 3)
    caixa.adicionar_ao_carrinho(carrinho, produtos[1], 2)
    venda = caixa.efetivar_venda(produtos, vendas, movimentacoes, carrinho, data)
    falhas = falhas + verificar("venda registrada", len(vendas), 1)
    falhas = falhas + verificar("número da venda", venda["numero"], 1)
    falhas = falhas + verificar("total da venda R$ 69,97", venda["total_centavos"], 6997)
    falhas = falhas + verificar("saldo do caderno baixou (10 -> 7)", produtos[0]["saldo"], 7)
    falhas = falhas + verificar("saldo da caneta baixou (4 -> 2)", produtos[1]["saldo"], 2)
    falhas = falhas + verificar("uma movimentação VENDA por item", len(movimentacoes), 2)
    falhas = falhas + verificar("movimentação do tipo VENDA", movimentacoes[0]["tipo"], "VENDA")

    # Venda impossível: o segundo item não tem saldo -> nada pode mudar
    carrinho = []
    caixa.adicionar_ao_carrinho(carrinho, produtos[0], 1)
    caixa.adicionar_ao_carrinho(carrinho, produtos[1], 5)
    venda = caixa.efetivar_venda(produtos, vendas, movimentacoes, carrinho, data)
    falhas = falhas + verificar("venda sem saldo devolve None", venda, None)
    falhas = falhas + verificar("primeiro item não baixou (tudo-ou-nada)", produtos[0]["saldo"], 7)
    falhas = falhas + verificar("nenhuma venda nova", len(vendas), 1)
    falhas = falhas + verificar("nenhuma movimentação nova", len(movimentacoes), 2)
    falhas = falhas + verificar("carrinho vazio não vira venda", caixa.efetivar_venda(produtos, vendas, movimentacoes, [], data), None)
    return falhas


def testar_persistencia():
    falhas = 0
    pasta = tempfile.mkdtemp()
    caminho = os.path.join(pasta, "dados", "loja.json")
    caminho_exemplo = os.path.join(pasta, "dados", "exemplo.json")

    # 1. Sem arquivo e sem exemplo: começa vazio
    produtos, vendas, movimentacoes, aviso = persistencia.carregar_dados(caminho, caminho_exemplo)
    falhas = falhas + verificar("arquivo ausente começa sem produtos", len(produtos), 0)
    falhas = falhas + verificar("arquivo ausente não gera aviso", aviso, "")

    # 2. Salvar e carregar de novo devolve o mesmo estado
    produtos = [{"codigo": 1, "nome": "Caneta", "preco_centavos": 250, "saldo": 10}]
    salvou = persistencia.salvar_dados(caminho, produtos, [], [])
    falhas = falhas + verificar("salvar devolve True", salvou, True)
    lidos, vendas, movimentacoes, aviso = persistencia.carregar_dados(caminho, caminho_exemplo)
    falhas = falhas + verificar("ida e volta preserva os produtos", lidos, produtos)
    falhas = falhas + verificar("não sobra arquivo .tmp", os.path.exists(caminho + ".tmp"), False)

    # 3. Arquivo corrompido: vira .corrompido e o programa começa vazio
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("{isto não é json")
    lidos, vendas, movimentacoes, aviso = persistencia.carregar_dados(caminho, caminho_exemplo)
    falhas = falhas + verificar("arquivo corrompido começa vazio", len(lidos), 0)
    falhas = falhas + verificar("cópia .corrompido foi criada", os.path.exists(caminho + ".corrompido"), True)
    falhas = falhas + verificar("aviso menciona a cópia", ".corrompido" in aviso, True)

    # 4. Sem loja.json, mas com exemplo: carrega o exemplo
    persistencia.salvar_dados(caminho_exemplo, produtos, [], [])
    lidos, vendas, movimentacoes, aviso = persistencia.carregar_dados(caminho, caminho_exemplo)
    falhas = falhas + verificar("primeira execução carrega o exemplo", lidos, produtos)
    falhas = falhas + verificar("aviso de exemplo carregado", aviso, "Primeira execução: dados de exemplo carregados.")

    shutil.rmtree(pasta)
    return falhas


def main():
    total_falhas = 0
    total_falhas = total_falhas + testar_texto_para_inteiro()
    total_falhas = total_falhas + testar_texto_para_centavos()
    total_falhas = total_falhas + testar_formatar_moeda()
    total_falhas = total_falhas + testar_cadastro()
    total_falhas = total_falhas + testar_estoque()
    total_falhas = total_falhas + testar_carrinho()
    total_falhas = total_falhas + testar_venda()
    total_falhas = total_falhas + testar_persistencia()
    print()
    if total_falhas > 0:
        print(f"{total_falhas} teste(s) falharam.")
        return 1
    print("Todos os testes passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
