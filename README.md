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
