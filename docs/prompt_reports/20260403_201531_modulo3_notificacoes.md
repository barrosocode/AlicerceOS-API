# Relatório — Módulo 3 RF08 Notificações automáticas (Licenciamento)

**Arquivo:** `20260403_201531_modulo3_notificacoes.md`  
**Referência:** `docs/project/REQUIREMENTS.md` (RF08), Seção 5 de `docs/project/ENGINEERING_GUIDE.md`.

---

## 1. Resumo técnico

### Modelo `Notificacao` (`apps/licenciamento`)

- **`licenca`** (FK, CASCADE), **`destinatario`** (FK `accounts.User`), **`data_envio`** (`DateTimeField`, default `timezone.now`), **`lida`** (`BooleanField`, default `False`).
- Índice composto em `(licenca, destinatario, lida, data_envio)` para consultas de duplicidade.

### Engine RF08 (`apps/licenciamento/services.py`)

- **`executar_verificacao_vencimentos()`** → `int` (quantidade de notificações criadas nesta execução):
  - Usa **`Licenca.objects.criticas()`** (manager existente).
  - Processa apenas licenças com **`status_efetivo`** em **`alerta`** ou **`expirada`**.
  - Destinatários: usuários **`admin`**, **`gestor`** ou **`is_superuser`** (com e-mail).
  - **Anti-spam:** não cria nova linha se já existir notificação **não lida** para o mesmo par **(licença, destinatário)** com **`data_envio` no mesmo dia** (filtro `data_envio__date=hoje`).
  - **E-mail:** `django.core.mail.send_mail` com `fail_silently=True` + **`logger.info`** por alerta registrado.

### Comando Django

- **`python manage.py verificar_vencimentos`** → chama o serviço e imprime `Notificações criadas: N`.

### Configuração

- **`EMAIL_BACKEND`** (default: **console**) e **`DEFAULT_FROM_EMAIL`** em `config/settings.py`, sobrescrevíveis por variável de ambiente.

### API

- **`GET /api/licenciamento/notificacoes/`** — alertas do usuário autenticado; por padrão só **`lida=False`**; **`?todas=1`** inclui lidas.
- **`PATCH /api/licenciamento/notificacoes/{id}/ler/`** — marca **`lida=True`** (apenas notificação do próprio usuário).

### Infraestrutura

- **`docker-compose.yml`:** comentário com exemplo `docker compose run --rm web python manage.py verificar_vencimentos`.
- **`Dockerfile`:** nota de que `manage.py` permanece disponível na imagem/volume para comandos.

### Migration

- **`licenciamento.0002_notificacao_rf08`**

---

## 2. Testes (TDD)

Arquivo: **`apps/licenciamento/tests/test_notifications.py`**

1. Licença **fora** da janela crítica **não** gera notificação; licença **crítica** gera **2** (admin + gestor).
2. Segunda execução no **mesmo dia** **não duplica** (0 novas).
3. **`call_command('verificar_vencimentos')`** imprime contagem esperada.
4. Destinatários **apenas** admin/gestor (colaborador **não** recebe).
5. **API:** lista pendentes + **`PATCH .../ler/`** + lista vazia; **`todas=1`** ainda retorna a notificação lida.

**Comando da suíte completa:**

```bash
docker compose run --rm web sh -c "python manage.py migrate --noinput && python manage.py test apps.core.tests apps.financeiro.tests apps.licenciamento.tests"
```

**Resultado esperado:** **36 testes OK** (31 anteriores + 5 RF08 em `test_notifications`).

---

## 3. Próximos passos sugeridos

- Agendar **`verificar_vencimentos`** (cron no host, Celery Beat ou serviço dedicado no Compose).
- Templates HTML de e-mail e canal adicional (push/WebSocket).
- Permitir novo envio no dia seguinte se ainda não lido (política configurável).

---

*Relatório gerado para rastreabilidade (Prompt Reports).*
