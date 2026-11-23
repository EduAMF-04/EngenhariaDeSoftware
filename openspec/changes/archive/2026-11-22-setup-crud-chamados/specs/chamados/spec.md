# Specification: Gerenciamento de Usuários e Chamados (CRUD)

## ADDED Requirements

### Requirement: Cadastro e Gestão de Usuários
O sistema MUST disponibilizar operações CRUD completas para `usuarios` (`POST /usuarios`, `GET /usuarios`, `GET /usuarios/:id`, `PUT /usuarios/:id`, `DELETE /usuarios/:id`).

#### Scenario: Criação de usuário com sucesso
- **WHEN** uma requisição `POST /usuarios` é enviada com `nome`, `email` inédito e `perfil` igual a `"CLIENTE"` ou `"TECNICO"`
- **THEN** o sistema cria o registro e retorna status HTTP `201 Created` com os dados do usuário

#### Scenario: Tentativa de criar usuário com perfil inválido
- **WHEN** uma requisição `POST /usuarios` é enviada com um `perfil` diferente de `"CLIENTE"` ou `"TECNICO"`
- **THEN** o sistema rejeita a requisição e retorna status HTTP `400 Bad Request`

#### Scenario: Exclusão de usuário com chamados ativos ou históricos
- **WHEN** uma requisição `DELETE /usuarios/:id` é enviada para um usuário vinculado a pelo menos um chamado
- **THEN** o sistema bloqueia a exclusão e retorna status HTTP `409 Conflict`

### Requirement: Abertura de Chamados
O sistema MUST permitir a criação de novos chamados via `POST /chamados`, exigindo um cliente válido e definindo o status inicial automaticamente.

#### Scenario: Abertura de chamado válida
- **WHEN** uma requisição `POST /chamados` é enviada com `titulo`, `descricao`, `prioridade` e um `cliente_id` existente com perfil `"CLIENTE"`
- **THEN** o sistema cria o chamado com `status` igual a `"ABERTO"`, `tecnico_id` nulo e retorna status HTTP `201 Created`

#### Scenario: Abertura de chamado com cliente inexistente
- **WHEN** uma requisição `POST /chamados` é enviada com um `cliente_id` que não existe no banco
- **THEN** o sistema retorna status HTTP `404 Not Found`

### Requirement: Consulta e Listagem de Chamados
O sistema MUST permitir listar todos os chamados (`GET /chamados`) e buscar detalhes de um chamado específico (`GET /chamados/:id`), retornando os dados básicos do cliente e do técnico atribuído.

#### Scenario: Listagem de chamados com filtro por status
- **WHEN** uma requisição `GET /chamados?status=ABERTO` é realizada
- **THEN** o sistema retorna status HTTP `200 OK` contendo apenas os chamados cujo status seja `"ABERTO"`

#### Scenario: Busca de chamado inexistente
- **WHEN** uma requisição `GET /chamados/:id` é feita com um identificador inexistente
- **THEN** o sistema retorna status HTTP `404 Not Found`

### Requirement: Atualização e Encerramento de Chamados
O sistema MUST permitir atualizar dados, atribuir técnico e alterar o status de um chamado via `PATCH /chamados/:id`.

#### Scenario: Atribuição de técnico válido
- **WHEN** uma requisição `PATCH /chamados/:id` informa um `tecnico_id` pertencente a um usuário com perfil `"TECNICO"`
- **THEN** o sistema vincula o técnico ao chamado e retorna status HTTP `200 OK`

#### Scenario: Bloqueio de fechamento sem técnico atribuído
- **WHEN** uma requisição `PATCH /chamados/:id` tenta alterar o `status` para `"FECHADO"` em um chamado onde `tecnico_id` é nulo
- **THEN** o sistema recusa a alteração e retorna status HTTP `422 Unprocessable Entity` (ou `400 Bad Request`) informando que um técnico deve ser atribuído antes do fechamento

### Requirement: Exclusão de Chamados
O sistema MUST permitir remover um chamado existente via `DELETE /chamados/:id`.

#### Scenario: Remoção de chamado com sucesso
- **WHEN** uma requisição `DELETE /chamados/:id` é enviada para um ID válido
- **THEN** o registro é removido do banco de dados e o sistema retorna status HTTP `204 No Content`