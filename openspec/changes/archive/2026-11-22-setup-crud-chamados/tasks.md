## 1. Configuração do Banco de Dados
- [x] 1.1 Configurar conexão com o banco de dados relacional.
- [x] 1.2 Criar migration/schema para a tabela `usuarios` com restrição de unicidade em `email`.
- [x] 1.3 Criar migration/schema para a tabela `chamados` com chaves estrangeiras `cliente_id` e `tecnico_id` referenciando `usuarios(id)`.

## 2. CRUD de Usuários
- [x] 2.1 Implementar endpoint `POST /usuarios` com validação de perfil (`CLIENTE` ou `TECNICO`) e e-mail único.
- [x] 2.2 Implementar endpoints `GET /usuarios` (listagem) e `GET /usuarios/:id` (busca por ID).
- [x] 2.3 Implementar endpoint `PUT /usuarios/:id` para atualização cadastral.
- [x] 2.4 Implementar endpoint `DELETE /usuarios/:id` bloqueando exclusão caso existam chamados vinculados.

## 3. CRUD de Chamados
- [x] 3.1 Implementar endpoint `POST /chamados` vinculando um `cliente_id` válido e definindo status inicial `ABERTO`.
- [x] 3.2 Implementar endpoints `GET /chamados` (com filtros opcionais por status) e `GET /chamados/:id` retornando dados do cliente e do técnico.
- [x] 3.3 Implementar endpoint `PATCH /chamados/:id` validando a regra de atribuição de técnico antes do fechamento.
- [x] 3.4 Implementar endpoint `DELETE /chamados/:id` para remoção de registros.

## 4. Validação e Documentação
- [x] 4.1 Testar todos os cenários descritos nas especificações (`openspec validate setup-crud-chamados`).
- [x] 4.2 Atualizar o `README.md` com exemplos de payload para execução dos testes.