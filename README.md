# Sistema de Controle de Estoque e Vendas

**Trabalho individual:** Mario Henrique
**Disciplina:** Paradigmas de Programação, UNAMA. Atividade Avaliativa AV1 (paradigma imperativo)

> 🚧 Em desenvolvimento.

Programa de terminal em Python, escrito no paradigma **imperativo/procedural**, para controlar o estoque e as vendas de um pequeno comércio.

## Como executar

Requisito: **Python 3.10 ou superior**. Não há nada para instalar (só a biblioteca padrão).

```bash
python main.py
```

Para rodar os testes automáticos:

```bash
python testes.py
```

## Funcionalidades

- [x] Cadastro de produtos (código único, nome, preço e saldo inicial)
- [x] Consulta de saldo e listagem do estoque
- [x] Dados salvos em `dados/loja.json` a cada alteração
- [x] Entrada de itens e saída avulsa (perda, avaria, uso interno)
- [x] Histórico de movimentações e extrato por produto
- [x] Venda com vários itens e comprovante
- [x] Relatórios: faturamento, vendas por produto, valor do estoque e todas as vendas
- [x] Dados de exemplo (`dados/exemplo.json`) carregados na primeira execução
