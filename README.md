# 🔄 Sincronizador Clockify ➔ Redmine

Automação em Python desenvolvida para buscar os lançamentos de horas do **Clockify**, consolidá-los por tarefa e registrá-los automaticamente no **Redmine**, gerando também o resumo formatado para a reunião Daily no **Discord**.

---

## 📌 Funcionalidades Principais

- **Lançamento Automático:** Consolida horas trabalhadas no Clockify agrupando por `#ID` da Issue do Redmine.
- **Limpeza de Lançamentos:** Deleta lançamentos anteriores do próprio usuário na data de execução para evitar duplicações ao reprocessar.
- **Busca de Títulos de Issues:** Consulta a API do Redmine para enriquecer o relatório com o título/assunto de cada tarefa.
- **Relatório para a Daily:** Formata o resumo do dia anterior no padrão:
  `#ID [Título da Issue], Descrição`
- **Validação de Carga Horária (8h):** Calcula o total acumulado do dia e emite alerta caso a soma seja inferior a 8 horas.
- **Notificação de Inconsistências:** Alerta sobre lançamentos no Clockify que não continham o `#ID` da issue do Redmine.
- **Notificações no Discord:** Envia relatórios diários de sucesso e alertas de falha/erro diretamente para um canal do Discord via Webhook.
- **Suíte de Testes Unitários:** Testes cobrindo módulos de serviço, parsing, formatação de relatórios e configurações com `pytest` e `unittest.mock`.
- **Execução Automática (CI/CD):** Workflow no GitHub Actions agendado para rodar diariamente em máquina local (Self-Hosted Runner).

---

## 🏗️ Arquitetura do Projeto

O projeto adota uma estrutura modularizada e limpa:

```text
.
├── .github/
│   └── workflows/
│       └── sync.yml              # Configuração do pipeline no GitHub Actions
├── tests/                        # Camada de testes unitários automatizados
│   ├── test_clockify_service.py  # Testes do serviço Clockify
│   ├── test_config.py            # Testes do carregamento de configurações
│   ├── test_redmine_service.py   # Testes do serviço Redmine
│   └── test_reporter_service.py  # Testes do gerador de relatórios e Discord
├── config.py                     # Carregamento e validação de variáveis de ambiente
├── clockify_service.py           # Integração e tratamento de dados da API do Clockify
├── redmine_service.py            # Integração e limpeza de dados da API do Redmine
├── reporter_service.py           # Formatação de relatórios, validações e envio ao Discord
├── main.py                       # Orquestrador principal da aplicação
├── requirements.txt              # Dependências Python do projeto
├── .env.example                  # Modelo para variáveis de ambiente locais
└── README.md                     # Documentação do projeto

```

---

## 🚀 Como Funciona a Sintaxe no Clockify

Para que o script identifique a qual tarefa do Redmine o tempo pertence, a **descrição** do lançamento no Clockify deve conter o padrão `#ID_DA_ISSUE`:

### Exemplos:

* `#102023 Validando erro com UX` ➔ Registra na Issue `#102023` com o comentário `Validando erro com UX`.
* `#102233 Identificando erro no módulo financeiro` ➔ Registra na Issue `#102233`.
* `Ajustando configurações gerais` ➔ Sem `#ID`: O tempo **não** é enviado ao Redmine e é listado no alerta de *Registros Não Vinculados*.

---

## ⚙️ Configuração do Ambiente

### 1. Requisitos

* Python 3.10+
* Dependências listadas em `requirements.txt`:
```bash
pip install -r requirements.txt

```

### 2. Variáveis de Ambiente (`.env`)

Crie um arquivo `.env` na raiz do projeto baseado no exemplo abaixo:

```env
REDMINE_URL=https://redmine.suaempresa.com.br
REDMINE_API_KEY=seu_token_api_redmine
CLOCKIFY_API_KEY=seu_token_api_clockify
CLOCKIFY_WORKSPACE_ID=seu_workspace_id_clockify
DEFAULT_REDMINE_ACTIVITY_ID=9 # Ex: Desenvolvimento/Atividade Padrão
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/sua_url_webhook # (Opcional)

```

---

## 🖥️ Como Executar

### Modo Automático (Processa D-1 / Dia Anterior)

```bash
python main.py

```

### Modo Manual / Teste (Para uma data específica)

```bash
python main.py YYYY-MM-DD

```

*Exemplo:* `python main.py 2026-07-29`

---

## 🧪 Executando os Testes

Para executar a suíte de testes unitários automatizados:

```bash
pytest
```

Ou via módulo do Python:

```bash
python -m pytest
```


---

## 🤖 Execução via GitHub Actions

A automação está configurada no repositório para ser executada via **Self-Hosted Runner** (máquina local/rede privada da empresa) para contornar restrições de firewall do Redmine.

* **Agendamento:** Configurado no `sync.yml` para rodar diariamente às **05:58 (Horário de Brasília)** (`58 8 * * *` UTC).
* **Gatilho Manual:** Habilitado via `workflow_dispatch` na aba **Actions** do GitHub.
* **Secrets Requeridas no GitHub:**
* `REDMINE_URL`
* `REDMINE_API_KEY`
* `CLOCKIFY_API_KEY`
* `CLOCKIFY_WORKSPACE_ID`
* `DEFAULT_REDMINE_ACTIVITY_ID`
* `DISCORD_WEBHOOK_URL`



---

## 📊 Exemplo de Saída no Discord / Logs

```text
============================================================
📋 RESUMO PARA A DAILY (ONTEM - 2026-07-29)
============================================================
• #102023 [Ajuste de Usabilidade no Painel], Validando erro com UX
• #102233 [Erro ao processar lote no financeiro], Identificando erro.
• #102235 [Refatoração da Controller], Revisando impactos
• #102228 [Deploy de Hotfix], Testes e merge | Ajustes de configuração

⏱️ Total de horas sincronizadas: 8.00h / 8.00h
============================================================

