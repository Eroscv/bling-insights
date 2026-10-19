# Bling Insights

Monitor de vendas e estoque para pequenos negócios que usam o [Bling ERP](https://www.bling.com.br/).
Puxa pedidos e produtos, calcula faturamento, ticket médio, top produtos e alerta quando algum item
está com estoque no mínimo ou abaixo dele — no terminal, em planilha Excel ou por e-mail.

## Por que este projeto

Automatizar esse tipo de checagem evita duas dores comuns de quem vende online: descobrir
tarde demais que um produto parou no estoque, e perder tempo toda semana montando o mesmo
relatório de vendas manualmente.

## Arquitetura

```
bling_insights/
├── datasource.py   # Interface DataSource + BlingAPISource (real) e MockDataSource (demo)
├── models.py       # Product, Order, OrderItem (dataclasses)
├── analyzer.py      # Regras de negócio: resumo de vendas, estoque baixo, vendas por dia
├── report.py        # Saída: tabela no terminal (rich) e exportação para .xlsx
├── alerts.py         # Envio de e-mail de alerta via SMTP
└── cli.py             # Entrypoint (argparse)
```

A fonte de dados é abstraída por `DataSource` (inversão de dependência): o restante do
sistema não sabe se os dados vêm da API real do Bling ou de arquivos JSON de exemplo.
Isso permite rodar e testar o projeto inteiro sem credenciais.

## Rodando em modo demo (sem credenciais)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m bling_insights --demo
```

Saída esperada: um resumo de vendas dos últimos 30 dias (dados de `data/sample/`) e os
produtos que estão com estoque baixo, formatados em tabelas no terminal.

### Exportar para Excel

```bash
python -m bling_insights --demo --export-excel relatorio.xlsx
```

## Rodando com dados reais do Bling

1. Crie um app em [developer.bling.com.br](https://developer.bling.com.br/) e complete o
   fluxo OAuth2 para obter um `access_token`.
2. Copie `.env.example` para `.env` e preencha `BLING_ACCESS_TOKEN`.
3. Rode:

```bash
export $(cat .env | xargs)   # ou use python-dotenv / direnv
python -m bling_insights --days 7
```

### Alertas por e-mail

Preencha as variáveis `SMTP_*` e `ALERT_RECIPIENT` no `.env` e adicione `--send-alert`:

```bash
python -m bling_insights --send-alert
```

Só envia e-mail se houver ao menos um produto com estoque baixo.

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

Os testes cobrem as regras de negócio (`analyzer.py`) e a fonte de dados mock, sem precisar
de rede ou credenciais.

## Possíveis próximos passos

- Agendar a execução diária (`cron` ou GitHub Actions) e mandar o resumo para um canal
  de WhatsApp/Slack.
- Histórico de vendas em banco de dados (SQLite) para gráficos de tendência ano a ano.
- Dashboard web simples (Streamlit) sobre os mesmos módulos `analyzer`/`datasource`.

## Stack

Python 3.10+, `requests`, `rich`, `openpyxl`, `pytest`. Sem frameworks pesados — o foco é
design limpo (interface de dados, separação de camadas) e automação prática de um
problema real de e-commerce.
