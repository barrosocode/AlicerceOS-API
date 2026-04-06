# Relatório — Módulo 3 (parte 1) Licenciamento e Documentos

**Arquivo:** `20260403_200754_modulo3_licenciamento.md`  
**Referências:** `docs/project/REQUIREMENTS.md` (RF07 contexto), `docs/specs/datamodel_spec.md` (secção 5), Seção 5 de `docs/project/ENGINEERING_GUIDE.md`.

---

## 1. Resumo técnico

### App `apps/licenciamento`

- **`OrgaoEmissor`:** `nome` (único), `url_portal` (URL, opcional).
- **`Licenca`:** FK `projeto` (CASCADE), FK `orgao` (PROTECT), `numero_processo`, `data_protocolo` (opcional), `data_vencimento`, `status` persistido (`pendente`, `aprovado`, `alerta`, `expirada`), `link_portal`, `arquivo_pdf` (`FileField`, opcional, `upload_to=licencas/pdfs/`).

### Motor de alertas

- Constante **`DIAS_JANELA_ALERTA = 15`** (vencimento em **menos de 15 dias**).
- **`LicencaQuerySet.criticas(ref_date=None)`:** `data_vencimento <= ref_date + 14 dias` (inclui vencidas e janela de 0–14 dias à frente).
- **`Licenca.dias_para_vencer`:** `(data_vencimento − hoje).days`.
- **`Licenca.status_efetivo`:** se `data_vencimento < hoje` → **`expirada`**; senão, se `dias_para_vencer < 15` → **`alerta`**; senão → `status` gravado.
- **`services.licencas_criticas(ref_date)`** delega ao manager.

### Integração financeiro

- **`Gasto.licenca`:** FK opcional para `licenciamento.Licenca` (`SET_NULL`).
- Regras em **`Gasto.clean()`:** com `licenca` preenchida é obrigatório **`vinculo_licenciamento=True`**, **`projeto`** definido e **`licenca.projeto == gasto.projeto`**.

### Configuração

- **`INSTALLED_APPS`:** `apps.licenciamento` antes de `apps.financeiro` (dependência de migração).
- **`MEDIA_URL` / `MEDIA_ROOT`** para `arquivo_pdf`.

### API (`/api/licenciamento/`)

- **`GET/POST/PATCH/... /api/licenciamento/licencas/`** — CRUD; filtro `?projeto=`; resposta com **`dias_para_vencer`** e **`status_efetivo`** (Serializer).
- **`GET /api/licenciamento/alertas/`** — apenas licenças **críticas**; permissão **`PodeVerResumoFinanceiroGlobal`** (Admin/Gestor), 403 para Colaborador.
- **`GET /api/licenciamento/orgaos/`** — leitura de órgãos emissores.

### Migrations

- `licenciamento.0001_initial`
- `financeiro.0002_gasto_licenca`

---

## 2. Testes (TDD)

| Arquivo | Cobertura |
|---------|-----------|
| `apps/licenciamento/tests/test_licencas.py` | Status efetivo (vencida → expirada); filtro críticas; gasto + `licenca` com `vinculo_licenciamento`; rejeição de `licenca` sem vínculo. |
| `apps/licenciamento/tests/test_api.py` | Dashboard `alertas/` (gestor vs colaborador); listagem de licenças com dias e status efetivo. |

**Comando:**

```bash
docker compose run --rm web sh -c "python manage.py migrate --noinput && python manage.py test apps.core.tests apps.financeiro.tests apps.licenciamento.tests"
```

**Resultado:** **31 testes OK** (24 anteriores + 7 do módulo licenciamento, incluindo listagem com contagem regressiva).

---

## 3. Próximos passos sugeridos

- Tarefa agendada (cron/Celery) para notificações (RF08).
- Upload seguro de PDF (validação de tipo/tamanho, vírus scan).
- Vínculo explícito de licença com protocolos e anexos (RF07 completo).

---

*Relatório gerado para rastreabilidade (Prompt Reports).*
