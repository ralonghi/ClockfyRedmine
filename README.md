# 🔄 Sync Clockify → Redmine

Automação modular em Python para sincronização diária de lançamentos de horas do **Clockify** para o **Redmine** via GitHub Actions ou execução local.

## 📌 Funcionalidades

- **Mapeamento Flexível de Comentários (`--`):** Permite inserir descrições detalhadas no Clockify utilizando o divisor `--` (ex: `#1234 Titulo -- Refatorada controller e corrigido bug`).
- **Agrupamento Automático:** Consolida múltiplos registros da mesma issue no mesmo dia em um único lançamento de tempo.
- **Limpeza Segura (Reprocessamento Idempotente):** Ao rodar para uma data específica, o script remove **exclusivamente os seus lançamentos anteriores no Redmine** antes de reescrever as horas, evitando duplicidades. Os registros de outros usuários permanecem intocados.
- **Alerta de Inconsistências:** Sinais claros e relatórios no log caso existam horas apontadas no Clockify sem o ID do Redmine (`#1234`).
- **Execução Automática ($D-1$):** Por padrão, processa os dados do dia anterior para garantir que a jornada esteja encerrada.
- **Arquitetura Modular:** Separação limpa entre lógica de orquestração (`main.py`), serviços do Clockify (`clockify_service.py`), serviços do Redmine (`redmine_service.py`) e configurações (`config.py`).
- **Segurança de Credenciais:** Suporte a arquivos `.env` locais e **GitHub Repository Secrets** em ambiente de CI/CD.

---

## 🛠️ Estrutura do Projeto

```text
.
├── .github/
│   └── workflows/
│       └── sync.yml            # Workflow do GitHub Actions (Execução diária)
├── .env.example                # Modelo de variáveis de ambiente
├── .gitignore                  # Arquivos ignorados pelo Git (.env, caches, etc)
├── README.md                   # Documentação do projeto
├── requirements.txt            # Dependências Python (requests, python-dotenv)
├── config.py                   # Carregador de configurações (.env / Secrets)
├── clockify_service.py         # Módulo de integração e parsing do Clockify
├── redmine_service.py          # Módulo de integração e operações no Redmine
└── main.py                     # Script principal de orquestração