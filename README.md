# Sistema de Chamados de Suporte (OpenSpec + FastAPI)

Sistema web backend com CRUD completo para gerenciamento de usuários (Clientes e Técnicos) e chamados de suporte técnico, desenvolvido seguindo a metodologia **Spec-Driven Development (OpenSpec)**.

## Tecnologias Utilizadas
- **Python 3.11+** & **FastAPI** (API RESTful e documentação interativa Swagger)
- **SQLite3** (Banco de dados relacional com chaves estrangeiras e restrição `ON DELETE RESTRICT`)
- **OpenSpec** (Especificações de requisitos e cenários em Markdown)

## Especificações (Artefatos OpenSpec)
Toda a arquitetura do banco de dados e regras de negócio foram especificadas antes da implementação:
- [Proposta Inicial](openspec/changes/archive/2026-11-22-setup-crud-chamados/proposal.md)
- [Lista de Tarefas](openspec/changes/archive/2026-11-22-setup-crud-chamados/tasks.md)
- [Especificação do Banco de Dados](openspec/specs/database/spec.md)
- [Especificação do CRUD de Chamados](openspec/specs/chamados/spec.md)

## Como Executar Localmente

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt

2. **Inicie o servidor:**
   ```
   python -m uvicorn src.main:app --reload --app-dir .

4. **Acesse a documentação interativa para testar os endpoints:**
   ```
    Abra no navegador: http://127.0.0.1:8000/docs
