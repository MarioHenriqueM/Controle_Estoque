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
    total_falhas = total_falhas + testar_persistencia()
    print()
    if total_falhas > 0:
        print(f"{total_falhas} teste(s) falharam.")
        return 1
    print("Todos os testes passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
