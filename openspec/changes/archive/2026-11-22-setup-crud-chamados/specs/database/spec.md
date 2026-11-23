# Specification: Database Schema

## ADDED Requirements

### Requirement: Tabela de Usuários
O banco de dados MUST manter uma tabela `usuarios` para clientes e técnicos com as colunas `id` (PK), `nome` (VARCHAR, NOT NULL), `email` (VARCHAR, UNIQUE, NOT NULL), `perfil` (`'CLIENTE'` ou `'TECNICO'`, NOT NULL) e `criado_em` (TIMESTAMP).

#### Scenario: Persistência de usuário com e-mail único
- **WHEN** um registro é inserido na tabela `usuarios` com um e-mail já existente
- **THEN** o banco de dados rejeita a operação por violação de constraint `UNIQUE`

### Requirement: Tabela de Chamados
O banco de dados MUST manter uma tabela `chamados` com as colunas `id` (PK), `titulo` (VARCHAR, NOT NULL), `descricao` (TEXT, NOT NULL), `status` (`'ABERTO'`, `'EM_ANDAMENTO'`, `'RESOLVIDO'`, `'FECHADO'`), `prioridade` (`'BAIXA'`, `'MEDIA'`, `'ALTA'`), `cliente_id` (FK NOT NULL), `tecnico_id` (FK NULLABLE) e `criado_em` (TIMESTAMP).

#### Scenario: Criação de chamado com colunas obrigatórias
- **WHEN** um chamado é inserido com título, descrição, status, prioridade e `cliente_id` válidos
- **THEN** o banco persiste o registro com `tecnico_id` opcional

### Requirement: Integridade Referencial entre Chamados e Usuários
As chaves estrangeiras `cliente_id` e `tecnico_id` MUST referenciar `usuarios(id)` com regra `ON DELETE RESTRICT`, impedindo a exclusão de usuários vinculados a chamados.

#### Scenario: Bloqueio de exclusão de usuário com chamados vinculados
- **WHEN** uma exclusão (`DELETE`) é executada na tabela `usuarios` para um `id` referenciado em `chamados`
- **THEN** o banco de dados impede a exclusão para preservar a integridade referencial