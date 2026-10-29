# Financeiro em Dia

Painel de análise de **contas a pagar** e previsão de desembolsos, construído com Python, Streamlit e Plotly. O projeto usa uma base inteiramente sintética, gerada localmente, para demonstrar um fluxo de análise financeira sem expor dados reais.

## O que o projeto responde

- Quanto há em aberto e quanto está vencido?
- Quais pagamentos vencem nas próximas semanas?
- Como os compromissos se distribuem por fornecedor e centro de custo?
- Que títulos precisam de atenção primeiro?

## Funcionalidades

- Indicadores de saldo em aberto, vencidos, pagos e vencimento médio.
- Filtros por fornecedor, centro de custo, categoria e criticidade.
- Previsão semanal de pagamentos em aberto para as próximas 8 semanas.
- Visões de compromissos por categoria e principais fornecedores.
- Tabela detalhada com dias até o vencimento e prioridade sugerida.
- Geração reproduzível de dados fictícios com semente fixa.

## Pré-requisitos

- Python 3.10 ou superior

## Como executar

No terminal, dentro desta pasta:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Instale as dependências e inicie o painel:

```bash
pip install -r requirements.txt
streamlit run app.py
```

O navegador abrirá o painel local. O arquivo `data/contas_pagar.csv` já acompanha o projeto.

## Gerar uma nova base sintética

```bash
python scripts/gerar_dados.py
```

O comando recria `data/contas_pagar.csv` com 500 títulos. A geração é determinística para a data de execução e para a semente definida no script.

## Estrutura do projeto

```text
financeiro-em-dia/
├── app.py
├── data/
│   └── contas_pagar.csv
├── scripts/
│   └── gerar_dados.py
├── src/
│   └── financeiro.py
├── requirements.txt
└── README.md
```

## Regras de análise

- Um título é considerado vencido quando está em aberto e sua data de vencimento é anterior à data de referência.
- A prioridade sugerida combina situação de atraso, criticidade e proximidade do vencimento. Ela é uma regra demonstrativa e deve ser adaptada às políticas de cada empresa.
- A previsão semanal considera apenas títulos em aberto, agrupados pela semana de vencimento.
- Não há conexão com bancos, ERPs ou sistemas de pagamento.

## Campos da base

| Campo | Descrição |
|---|---|
| `id_titulo` | Identificador fictício do título |
| `fornecedor` | Nome fictício do fornecedor |
| `categoria` | Natureza da despesa |
| `centro_custo` | Área responsável pela despesa |
| `data_emissao` | Data fictícia de emissão |
| `data_vencimento` | Data prevista para pagamento |
| `valor` | Valor fictício em reais |
| `status` | `Pago` ou `Em aberto` |
| `data_pagamento` | Data de pagamento, quando aplicável |
| `criticidade` | Classificação operacional fictícia |
| `descricao` | Descrição curta do título |

## Acesso ao projeto

Repositório: https://github.com/danielestrela-dev/financeiro-em-dia

O painel roda localmente com Streamlit. Veja os passos em [Como executar](#como-executar). O repositório contém apenas dados sintéticos e pode ser usado como demonstração de portfólio.

## Limitações

Os dados e as regras são fictícios e servem para demonstração. A previsão mostra compromissos registrados, sem modelagem estatística de fluxo de caixa, impostos, descontos, renegociação ou saldo bancário.
