# Relatório — Módulo 1 Financeiro (Alicerce OS)

**Arquivo:** `20260403_154615_modulo1_financeiro.md`  
**Referências:** `docs/project/REQUIREMENTS.md` (RF03, RF04), `docs/specs/finance_spec.md`, Seção 5 de `docs/project/ENGINEERING_GUIDE.md`.

---

## 1. Resumo técnico

### Refatoração e app `financeiro`

- Novo app Django **`apps.financeiro`** registrado em `INSTALLED_APPS`.
- **`Gasto`** removido de `apps.core` (migration **`core.0002_delete_gasto`**) e recriado em **`apps/financeiro/models.py`** com FKs para **`core.Projeto`** (`SET_NULL`, `related_name='gastos'`) e **`core.Parceiro`** (`PROTECT`, `related_name='gastos'`).
- Novo model **`Entrada`** (entradas de caixa) com FK opcional para **`Projeto`** (`related_name='entradas'`), `categoria`, `valor`, `data_transacao`.
- **`Gasto`** deixou de ter campo `tipo` (apenas saídas); usa `data_transacao`, `categoria`, `vinculo_licenciamento` (RF03: força categoria **Licença** em `clean()`).

### Regras de negócio (models)

- **`calcular_saldo(queryset_entradas, queryset_gastos)`:** soma entradas − soma saídas.
- **Data:** `validar_data_transacao_nao_alem_de_um_ano` — bloqueia data de transação **além de 365 dias** no futuro (`Entrada` e `Gasto`).
- **Mão de obra:** `Gasto` com `categoria=mao_de_obra` exige **`parceiro`** (alinhado ao datamodel / Módulo 0).
- **`save()`** chama **`full_clean()`** para garantir validação também em `objects.create()`.

### API (DRF)

- **`GET /api/financeiro/resumo/`** — query params obrigatórios **`start_date`**, **`end_date`**; opcional **`project_id`**. Resposta: `saldo`, `entradas_por_categoria`, `gastos_por_categoria`, `por_projeto`, `filtros`.
- **`GET|POST /api/financeiro/transacoes/`** — listagem unificada (entradas + saídas com campo `tipo`) e criação com corpo contendo **`tipo`**: `entrada` | `saida` e campos do serializer correspondente.
- **Filtros na listagem:** `projeto`, `categoria`, `start_date`, `end_date` (implementados em `apps/financeiro/services.py`).
- **Permissão:** `PodeVerResumoFinanceiroGlobal` — perfil **`colaborador`** recebe **403** no resumo; **`admin`** e **`gestor`** autorizados.

### Arquivos principais

- Models: `apps/financeiro/models.py`
- Serviços/agregação: `apps/financeiro/services.py`
- Serializers: `apps/financeiro/serializers.py`
- Views: `apps/financeiro/views.py`
- URLs: `apps/financeiro/urls.py` (inclusão em `config/urls.py`)
- Testes: `apps/financeiro/tests/test_models.py`, `apps/financeiro/tests/test_api.py`
- Testes do núcleo atualizados: `apps/core/tests/test_models.py` importa `Gasto` de `apps.financeiro`.

---

## 2. Estado dos testes

Execução (PostgreSQL via Docker Compose):

```bash
docker compose run --rm web sh -c "python manage.py migrate --noinput && python manage.py test apps.core.tests apps.financeiro.tests -v 2"
```

**Resultado:** **17 testes OK** (7 do Módulo 0 em `apps.core.tests` + 10 do Módulo 1 em `apps.financeiro.tests`).

| Área | Quantidade | Observação |
|------|------------|------------|
| `apps.core.tests` | 7 | Integridade projeto/gasto, mão de obra, user por e-mail |
| `apps.financeiro.tests.test_models` | 6 | Saldo, data futura, parceiro mão de obra, total por projeto, licenciamento |
| `apps.financeiro.tests.test_api` | 4 | Filtro de datas no resumo, 403 colaborador no resumo, filtros de listagem |

---

## 3. Migrations aplicadas

- `core.0002_delete_gasto`
- `financeiro.0001_initial` (tabelas `Entrada` e `Gasto`)

---

## 4. Comandos úteis

```bash
docker compose build
docker compose up
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py test apps.core.tests apps.financeiro.tests
```

**JWT:** obter token em `POST /api/auth/token/` com `email` e `password`; usar header `Authorization: Bearer <access>`.

**Exemplos:**

- `GET /api/financeiro/resumo/?start_date=2026-04-01&end_date=2026-04-30&project_id=1`
- `GET /api/financeiro/transacoes/?projeto=1&categoria=material&start_date=2026-04-01&end_date=2026-04-30`
- `POST /api/financeiro/transacoes/` com `{"tipo":"entrada","categoria":"projeto","valor":"100.00","data_transacao":"2026-04-03","projeto":1}` ou `tipo":"saida"` e campos de `Gasto`.

---

## 5. Próximos passos sugeridos

- Paginação e ordenação estável na listagem de transações.
- Regra fina de **colaborador** com escopo por projeto (quando existir vínculo usuário–projeto).
- OpenAPI/Swagger e políticas RBAC por endpoint.
- Testes adicionais para `POST /api/financeiro/transacoes/` e resumo sem `project_id` (visão consolidada).

---

*Relatório gerado para rastreabilidade (Prompt Reports).*
