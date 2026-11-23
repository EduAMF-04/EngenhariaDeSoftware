# Proposal: Sistema de Chamados de Suporte (CRUD Inicial)

## Why
Atualmente não existe uma estrutura de banco de dados nem endpoints para registrar, acompanhar e gerenciar solicitações de suporte técnico. Precisamos estabelecer a base do sistema com persistência relacional e operações CRUD completas para usuários e chamados.

## What Changes
- Criação do esquema relacional de banco de dados contendo duas tabelas principais: `usuarios` e `chamados`.
- Implementação de API RESTful com CRUD completo (`Create`, `Read`, `Update`, `Delete`) para a entidade `usuarios`.
- Implementação de API RESTful com CRUD completo para a entidade `chamados`, incluindo regras de negócio para atribuição de técnicos e transição de status.

## Impact
- **Affected specs:** `database` (new), `chamados` (new)
- **Affected code:** Estrutura inicial do servidor, camada de acesso a dados (ORM/migrations), controladores e rotas da API.