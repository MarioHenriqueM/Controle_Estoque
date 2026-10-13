"""Sistema de Controle de Estoque e Vendas (paradigma imperativo).

Execute com:  python main.py

Fluxo do programa:
1. carrega o estado (produtos, vendas e movimentações) do arquivo de dados;
2. repete o menu até o usuário escolher 0 (sair);
3. executa a opção escolhida (estrutura de decisão if/elif/else);
4. salva o estado depois de cada operação que alterou os dados.
"""

import os

from loja import leitura
from loja import persistencia
from loja import telas

PASTA_DO_PROGRAMA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DADOS = os.path.join(PASTA_DO_PROGRAMA, "dados", "loja.json")
CAMINHO_EXEMPLO = os.path.join(PASTA_DO_PROGRAMA, "dados", "exemplo.json")
AVISO_NAO_SALVOU = "ATENÇÃO: os dados NÃO foram salvos (o arquivo está aberto em outro programa?)."


def executar_menu(produtos, vendas, movimentacoes):
    """Laço principal: mostra o menu, executa a opção e salva após cada alteração."""
    executando = True
    while executando:
        telas.mostrar_menu()
        opcao = leitura.ler_inteiro("Escolha uma opção: ", 0)
        alterou = False
        if opcao == 1:
            alterou = telas.cadastrar_produto(produtos, movimentacoes)
        elif opcao == 2:
            alterou = telas.registrar_entrada(produtos, movimentacoes)
        elif opcao == 3:
            alterou = telas.registrar_saida(produtos, movimentacoes)
        elif opcao == 4:
            alterou = telas.registrar_venda(produtos, vendas, movimentacoes)
        elif opcao == 7:
            telas.opcao_em_construcao()
        elif opcao == 5:
            telas.consultar_saldo(produtos, movimentacoes)
        elif opcao == 6:
            telas.listar_estoque(produtos)
        elif opcao == 0:
            executando = False
        else:
            print("Opção inválida.")
        if alterou:
            salvou = persistencia.salvar_dados(CAMINHO_DADOS, produtos, vendas, movimentacoes)
            if not salvou:
                print(AVISO_NAO_SALVOU)

    salvou = persistencia.salvar_dados(CAMINHO_DADOS, produtos, vendas, movimentacoes)
    if salvou:
        print("Dados salvos. Até logo!")
    else:
        print(AVISO_NAO_SALVOU)


def main():
    produtos, vendas, movimentacoes, aviso = persistencia.carregar_dados(CAMINHO_DADOS, CAMINHO_EXEMPLO)
    if aviso != "":
        print(aviso)
    try:
        executar_menu(produtos, vendas, movimentacoes)
    except (EOFError, KeyboardInterrupt):
        # Ctrl+C ou fim da entrada: encerra sem mensagem de erro e SEM salvar,
        # porque cada operação concluída já foi salva.
        print()
        print("Programa encerrado. As operações concluídas já estavam salvas.")


if __name__ == "__main__":
    main()
