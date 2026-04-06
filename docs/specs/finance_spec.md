# Finance Module Specification (SDD + TDD)

## Regras de Negócio (Back-end)

### RF03 - Fluxo de Caixa

- **Cálculo de Saldo**: O sistema deve prover um endpoint que retorne o saldo atual (Soma das Entradas - Soma das Saídas).
- **Validação de Data**: Não permitir registros de transações com data futura superior a 365 dias.
- **Categorização**: Gastos com licenciamento devem ser automaticamente vinculados à categoria "Licenca".

### RF04 - Dashboard Data

- **Agregação**: O endpoint de dashboard deve retornar os dados agrupados por `categoria` e por `projeto`.
- **Filtros Obrigatórios**: Os endpoints devem aceitar query params `start_date`, `end_date` e `project_id`.

## Plano de Testes (TDD)

### Testes de Unidade (Models)

- `test_total_projeto_calculo`: Garantir que a soma de gastos vinculados a um projeto X não inclua gastos do projeto Y.
- `test_obrigatoriedade_parceiro_em_mao_de_obra`: Tentar salvar um gasto de mão de obra sem parceiro deve retornar erro de validação.

### Testes de Integração (API)

- `test_get_financeiro_summary_filter`: Validar se o filtro de data realmente reduz o escopo dos resultados.
- `test_unauthorized_access`: Garantir que um "Colaborador" não possa ver o resumo financeiro total da empresa, apenas de seus projetos (se configurado).

## Endpoints Esperados

- `GET /api/financeiro/resumo/`
- `POST /api/financeiro/transacoes/`
- `GET /api/financeiro/transacoes/?projeto=ID`
