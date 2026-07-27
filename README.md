# 🔄 Sync Clockify → Redmine

Automação em Python para sincronização diária de lançamentos de horas do **Clockify** para o **Redmine** via GitHub Actions.

## 📌 Funcionalidades

- **Agrupamento Automático:** Consolida múltiplos registros da mesma issue no mesmo dia em um único lançamento de tempo.
- **Extração de Issue ID:** Reconhece automaticamente o ID da issue do Redmine informado no formato `#1234` na descrição da tarefa do Clockify.
- **Consolidação de Comentários:** Junta os comentários de diferentes sessões de trabalho separando-os por ` | `.
- **Execução Automática ($D-1$):** Processa os dados do dia anterior para garantir que a jornada de trabalho esteja encerrada.
- **Execução Segura:** Sem arquivos com credenciais trafegando no Git; utiliza **GitHub Repository Secrets**.

---

## 🛠️ Pré-requisitos e Estrutura de Arquivos

Para rodar este projeto, a estrutura de pastas deve ser a seguinte:

```text
.
├── .github/
│   └── workflows/
│       └── sync.yml      # Workflow do GitHub Actions
├── .gitignore            # Arquivos ignorados pelo Git
├── README.md             # Documentação do projeto
└── main.py               # Script principal de sincronização
```

---

## 🚀 Configuração Passo a Passo

### 1. Criar Repositório Privado
Crie um repositório **Privado** no seu GitHub para hospedar o código.

### 2. Configurar os Secrets no GitHub
No seu repositório no GitHub, acesse:
`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Cadastre as seguintes chaves:

| Nome do Secret | Descrição / Exemplo |
| :--- | :--- |
| `REDMINE_URL` | URL base do Redmine (ex: `https://redmine.suaempresa.com`) |
| `REDMINE_API_KEY` | Sua Chave de API do Redmine (*Minha Conta -> Chave de Acesso API*) |
| `CLOCKIFY_API_KEY` | Sua Chave de API do Clockify (*Configurações de Perfil -> API Key*) |
| `CLOCKIFY_WORKSPACE_ID` | ID do seu Workspace no Clockify (presente na URL do browser) |
| `DEFAULT_REDMINE_ACTIVITY_ID` | ID da atividade padrão no Redmine (ex: `9` para Desenv/Atividade) |

---

## 🏷️ Padrão de Apontamento no Clockify

Para que o script encontre a issue correspondente no Redmine, inclua o símbolo `#` seguido do número da issue na descrição da tarefa no Clockify.

**Exemplos válidos:**
- `#1234 Corrigindo bug na tela de login`
- `Refatorando módulo de relatórios #4321`

Se uma tarefa não contiver um ID no formato `#1234`, ela será ignorada na sincronização.

---

## ⏰ Agendamento e Execução

- **Automático:** O GitHub Actions executará o script diariamente via `cron` processando os dados do dia anterior.
- **Manual:** Para forçar a execução a qualquer momento:
  1. Vá até a aba **Actions** no seu repositório no GitHub.
  2. Selecione a action **Sync Clockify to Redmine**.
  3. Clique em **Run workflow**.

---

## 🔒 Segurança

O arquivo `.gitignore` já vem configurado para evitar o envio acidental de arquivos de configuração locais ou variáveis de ambiente para o repositório.
