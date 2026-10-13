"""Leitura do teclado com validação.

É o ÚNICO módulo do programa que chama input(). Cada função ler_* repete
a pergunta (laço while com variável de controle) até o usuário digitar um
valor válido, e devolve o valor já convertido.
As conversões texto -> número (texto_para_*) não leem o teclado, por isso
podem ser testadas automaticamente em testes.py.
"""

MAXIMO_DIGITOS = 6    # quantidades e códigos até 999.999; preço até R$ 999.999,99


def texto_para_inteiro(texto):
    """Converte ' 42 ' em 42.
    Devolve -1 se o texto não for um inteiro sem sinal com até MAXIMO_DIGITOS dígitos."""
    texto = texto.strip()
    if not texto.isdecimal() or len(texto) > MAXIMO_DIGITOS:
        return -1
    return int(texto)


def texto_para_centavos(texto):
    """Converte '12,50', '12.50', '12,5' ou '12' em centavos (int), sem usar float.
    Devolve -1 se o texto for inválido (letras, sinal, 3 ou mais casas decimais,
    separador de milhar ou mais de MAXIMO_DIGITOS dígitos nos reais)."""
    texto = texto.strip().replace(",", ".")
    if texto == "" or texto.count(".") > 1:
        return -1
    if "." in texto:
        partes = texto.split(".")
        parte_reais = partes[0]
        parte_centavos = partes[1]
    else:
        parte_reais = texto
        parte_centavos = "00"
    if parte_reais == "":
        parte_reais = "0"
    if len(parte_centavos) == 1:
        parte_centavos = parte_centavos + "0"
    if not parte_reais.isdecimal() or not parte_centavos.isdecimal() or len(parte_centavos) != 2:
        return -1
    if len(parte_reais) > MAXIMO_DIGITOS:
        return -1
    return int(parte_reais) * 100 + int(parte_centavos)


def ler_inteiro(mensagem, minimo):
    """Pergunta até o usuário digitar um inteiro >= minimo (até 999.999) e o devolve."""
    numero = -1
    valido = False
    while not valido:
        texto = input(mensagem)
        numero = texto_para_inteiro(texto)
        if numero == -1:
            print("Valor inválido: digite só números inteiros, sem sinal, com até 6 dígitos.")
        elif numero < minimo:
            print(f"Digite um número maior ou igual a {minimo}.")
        else:
            valido = True
    return numero


def ler_preco_centavos(mensagem):
    """Pergunta até o usuário digitar um preço válido e maior que zero.
    Devolve o preço em CENTAVOS (int): '19,99' -> 1999."""
    centavos = 0
    while centavos <= 0:
        texto = input(mensagem)
        centavos = texto_para_centavos(texto)
        if centavos <= 0:
            print("Preço inválido. Use o formato 12,50 (de R$ 0,01 a R$ 999.999,99, sem separador de milhar).")
    return centavos


def ler_texto(mensagem, maximo):
    """Pergunta até o usuário digitar um texto não vazio com até 'maximo' caracteres."""
    texto = ""
    valido = False
    while not valido:
        texto = input(mensagem).strip()
        if texto == "":
            print("O texto não pode ficar vazio.")
        elif len(texto) > maximo:
            print(f"Use no máximo {maximo} caracteres.")
        else:
            valido = True
    return texto


def ler_confirmacao(mensagem):
    """Pergunta até o usuário responder s ou n. Devolve True para 's' e False para 'n'."""
    resposta = ""
    while resposta != "s" and resposta != "n":
        resposta = input(mensagem).strip().lower()
        if resposta != "s" and resposta != "n":
            print("Responda com s (sim) ou n (não).")
    return resposta == "s"
