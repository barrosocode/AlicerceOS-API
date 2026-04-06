# API Documentation Specification

## 1. Visão Geral

A API do **Alicerce OS** deve ser auto-documentada e possuir uma referência estática em Markdown para consultas rápidas e arquiteturais.

## 2. Documentação Automática (Swagger/OpenAPI)

- **Ferramenta:** `drf-spectacular`.
- **Requisito:** Todos os ViewSets devem utilizar `@extend_schema` para detalhar inputs, outputs e descrições de filtros.
- **Endpoints:**
    - `/api/schema/`: Download do arquivo YAML/JSON.
    - `/api/docs/`: Interface Swagger UI.
    - `/api/redoc/`: Interface ReDoc.

## 3. Documentação Estática (docs/API_REFERENCE.md)

Este arquivo deve ser mantido manualmente ou via script e conter:

### 3.1 Padrão de Respostas

- **Sucesso:** `200 OK` ou `201 Created`.
- **Erro de Validação:** `400 Bad Request` com detalhamento por campo.
- **Erro de Permissão:** `403 Forbidden` com a mensagem da regra RBAC violada.

### 3.2 Detalhamento de Endpoints (Exemplo de Estrutura)

Para cada módulo (Financeiro, Projetos, Licenciamento), o documento deve listar:

- **Endpoint:** `GET /api/financeiro/resumo/`
- **Descrição:** Retorna agregação financeira para o Dashboard.
- **Query Params:** `start_date`, `end_date`, `project_id`.
- **Payload de Exemplo:**

```json
{
    "total_entradas": 15000.0,
    "total_saidas": 5000.0,
    "saldo": 10000.0,
    "por_categoria": {"Material": 3000.0, "Mao de Obra": 2000.0}
}
```
