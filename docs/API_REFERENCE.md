# Alicerce OS — Referência da API (Módulos 0, 1 e 2)

Documento de consulta rápida para integradores e arquitetos. Complementa a **fonte canônica** gerada pelo **OpenAPI** (`drf-spectacular`). Normas de engenharia e versionamento: `docs/project/ENGINEERING_GUIDE.md` (Seção 6 — *Conventional Commits* e IDs de requisito).

---

## 1. Visão geral

| Item | Valor |
|------|--------|
| **Base** | Serviço HTTP da API (ex.: `http://localhost:8000`) |
| **Formato** | JSON (`Content-Type: application/json`) |
| **Autenticação** | **JWT** (`Authorization: Bearer <access>`) na maior parte dos recursos de negócio |
| **OpenAPI** | `GET /api/schema/` (YAML/JSON), UI **Swagger** em `/api/docs/`, **ReDoc** em `/api/redoc/` |

A documentação interativa incorpora descrições por endpoint (*tags*: Autenticação, Financeiro, Projetos, Licenciamento). **Este arquivo abrange explicitamente os Módulos 0, 1 e 2**; rotas adicionais podem existir na mesma instância e aparecem no schema.

---

## 2. Convenção de respostas HTTP

Alinhado a `docs/specs/api_documentation_spec.md`:

| Situação | HTTP | Corpo típico |
|----------|------|----------------|
| Leitura bem-sucedida | **200 OK** | Payload do recurso ou lista |
| Criação bem-sucedida | **201 Created** | Recurso criado |
| Validação ou regra de negócio inválida | **400 Bad Request** | Objeto com erros por campo ou `detail` |
| Autenticado porém sem permissão (RBAC) | **403 Forbidden** | `detail` com a regra violada |
| Não autenticado | **401 Unauthorized** | Tratamento do DRF/JWT |

Valores decimais financeiros são serializados em JSON como **string** ou número conforme o serializer; na integração, validar o contrato no schema gerado.

---

## 3. Módulo 0 — Autenticação e acesso

### 3.1 Obter par de tokens (JWT)

| | |
|---|---|
| **Endpoint** | `POST /api/auth/token/` |
| **Descrição** | Emite `access` e `refresh`. O projeto utiliza **e-mail** como identificador de login (`USERNAME_FIELD`), não `username`. |
| **Autenticação** | Não (público) |

**Corpo (exemplo):**

```json
{
  "email": "gestor@jell.com",
  "password": "********"
}
```

**Resposta (200):**

```json
{
  "access": "<jwt_access>",
  "refresh": "<jwt_refresh>"
}
```

### 3.2 Renovar access token

| | |
|---|---|
| **Endpoint** | `POST /api/auth/token/refresh/` |
| **Descrição** | Troca um `refresh` válido por um novo `access`. |
| **Autenticação** | Não (público) |

**Corpo (exemplo):**

```json
{
  "refresh": "<jwt_refresh>"
}
```

**Resposta (200):**

```json
{
  "access": "<novo_jwt_access>"
}
```

---

## 4. Módulo 1 — Financeiro (RF03 / RF04)

Todos os endpoints abaixo exigem **JWT** salvo o contrário indicado.

### 4.1 Resumo financeiro agregado

| | |
|---|---|
| **Endpoint** | `GET /api/financeiro/resumo/` |
| **Descrição** | Consolida entradas e saídas no intervalo; totais por categoria (entradas e gastos) e lista `por_projeto` com saldo por projeto. Visível apenas a perfis autorizados (**Admin/Gestor** — ver RBAC no código). |
| **Query params** | `start_date` **(obrig.)**, `end_date` **(obrig.)**, `project_id` *(opc.)* — formato `YYYY-MM-DD` nas datas |

**Exemplo de resposta (200):**

```json
{
  "saldo": "500.00",
  "entradas_por_categoria": { "projeto": "1000.00" },
  "gastos_por_categoria": { "material": "300.00", "mao_de_obra": "200.00" },
  "por_projeto": [
    {
      "projeto_id": 1,
      "projeto_nome": "Obra Alfa",
      "total_entradas": "1000.00",
      "total_gastos": "500.00",
      "saldo": "500.00"
    }
  ],
  "filtros": {
    "start_date": "2026-04-01",
    "end_date": "2026-04-30",
    "project_id": "1"
  }
}
```

**Erros:** `400` se faltarem datas; `403` se o perfil não puder ver o resumo global.

### 4.2 Transações (lista unificada)

| | |
|---|---|
| **Endpoint** | `GET /api/financeiro/transacoes/` |
| **Descrição** | Lista mista de **entradas** e **saídas**; cada objeto inclui `tipo`: `entrada` ou `saida`. |
| **Query params** | `projeto`, `categoria`, `start_date`, `end_date` *(todos opcionais)* |

**Exemplo de item na lista (200):**

```json
{
  "id": 10,
  "projeto": 1,
  "categoria": "material",
  "valor": "100.00",
  "parceiro": null,
  "data_transacao": "2026-04-15",
  "vinculo_licenciamento": false,
  "licenca": null,
  "tipo": "saida"
}
```

### 4.3 Criar transação

| | |
|---|---|
| **Endpoint** | `POST /api/financeiro/transacoes/` |
| **Descrição** | Incluir o campo **`tipo`** com valor `entrada` ou `saida`; demais campos conforme o serializer da Entrada ou do Gasto. |
| **Autenticação** | JWT |

**Exemplo — entrada:**

```json
{
  "tipo": "entrada",
  "projeto": 1,
  "categoria": "projeto",
  "valor": "5000.00",
  "data_transacao": "2026-04-03"
}
```

**Exemplo — saída:**

```json
{
  "tipo": "saida",
  "projeto": 1,
  "categoria": "material",
  "valor": "350.00",
  "parceiro": null,
  "data_transacao": "2026-04-03",
  "vinculo_licenciamento": false
}
```

Regras de domínio (projeto em orçamento, mão de obra com parceiro, datas, vínculo com licença, etc.) retornam **400** com detalhes.

---

## 5. Módulo 2 — Projetos, orçamentos e diário de obra (RF05 / RF06)

Prefixo de rota: **`/api/`** (via `apps.core.urls`).

### 5.1 Projetos

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `GET` | `/api/projetos/` | Lista projetos com métricas: `gastos_reais_total`, `orcamento_estimado`, `valor_total_orcamento_itens`, `progresso_barra_percentual`, `percentual_gasto_sobre_orcamento`, etc. |
| `GET` | `/api/projetos/{id}/` | Detalhe |
| `PUT` / `PATCH` | `/api/projetos/{id}/` | Atualização; transição para status **`ativo`** restrita a **Admin/Gestor** (`400` com mensagem de RBAC quando violado). |

### 5.2 Itens de orçamento

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `GET` | `/api/orcamento-itens/` | Lista; filtro opcional `?projeto=<id>` |
| `POST` | `/api/orcamento-itens/` | Cria item (subtotal derivado em leitura) |
| `GET` | `/api/orcamento-itens/{id}/` | Detalhe |
| `PUT` / `PATCH` | `/api/orcamento-itens/{id}/` | Atualização |
| `DELETE` | `/api/orcamento-itens/{id}/` | Exclusão |

### 5.3 Relatórios de atividade (diário / semanal)

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `GET` | `/api/relatorios-atividade/` | Lista; filtro opcional `?projeto=<id>` |
| `POST` | `/api/relatorios-atividade/` | Cria registro (`tipo` diário ou semanal, `descricao`, `fotos_url`, etc.) |
| `GET` | `/api/relatorios-atividade/{id}/` | Detalhe |
| `PUT` / `PATCH` / `DELETE` | `/api/relatorios-atividade/{id}/` | Manutenção |

---

## 6. Sincronização com o OpenAPI

- **Spec:** `GET /api/schema/?format=openapi-json` ou YAML conforme negociação.
- **Contratos com o frontend** devem referenciar o schema versionado no repositório ou artefato de build; este Markdown é **espelho editorial** dos módulos 0–2 e pode ser estendido por *script* ou revisão humana quando o SDD evoluir (`ENGINEERING_GUIDE.md`, passo 4).

---

## 7. Referência operacional (sem commit nesta entrega)

Alterações em dependências (`drf-spectacular`), `settings` e rotas de schema devem, em entregas futuras, seguir **Conventional Commits** com escopo e ID de task, por exemplo:

- `chore(deps): [docs] adiciona drf-spectacular`
- `docs(api): [RF04] referência estática Módulos 0–2`

*Nenhum commit foi realizado nesta solicitação; apenas arquivos preparados para validação.*
