# 🏗️ Projeto Alicerce OS: Sistema de Gestão JELL

## 🎯 Visão Geral e Objetivo

O **Alicerce OS** é uma solução de ERP verticalizada para a **JELL**, uma empresa de gestão de projetos de construção civil. O objetivo central é unificar a operação, hoje fragmentada em ferramentas como Canva e planilhas, focando em dois pilares críticos: **Saúde Financeira** e **Controle de Prazos de Licenciamento**.

- **Público-alvo:** Administradores e gestores operacionais.
- **Problema Central:** Ineficiência no acompanhamento de prazos de órgãos ambientais (IDEMA/Bombeiros) e falta de métricas de rentabilidade por projeto.
- **Solução:** Dashboard administrativo integrado com alertas inteligentes e automatização de consultas externas.

---

## 🛠️ Arquitetura do Back-end (Engine)

O back-end atua como o núcleo de inteligência e automação do sistema.

### Stack Técnica

- **Runtime:** Python 3.12+
- **Framework:** Django REST Framework (DRF)
- **Database:** PostgreSQL
- **Auth:** JWT (SimpleJWT)
- **Infra:** Docker & Docker Compose

### Responsabilidades Críticas para a IA

- **Normalização Financeira:** Cada `Gasto` deve obrigatoriamente estar vinculado a uma `Categoria` e, preferencialmente, a um `Projeto`.
- **Engine de Notificações:** Sistema de checagem diária para licenças com vencimento em < 15 dias.
- **Automação (Fase 2):** Scrapers (Playwright/BeautifulSoup) para monitoramento de portais externos (IDEMA, Bombeiros-RN).
- **Relatórios:** Agregação de dados via ORM para endpoints de performance (KPIs).

---

## 💻 Arquitetura do Front-end (Dashboard)

Interface focada em UX administrativa, velocidade de inserção de dados e clareza visual.

### Stack Técnica

- **Framework:** Next.js 14+ (App Router)
- **Linguagem:** TypeScript (Strict Mode)
- **Styling:** Tailwind CSS + Shadcn/UI
- **State/Fetching:** TanStack Query (React Query)

### Responsabilidades Críticas para a IA

- **KPI Dashboards:** Visualização de Lucro Bruto e prazos críticos.
- **Filtros Globais:** Persistência de filtros por `Projeto` e `Data` via URL States ou Context.
- **Dynamic Forms:** Cálculos em tempo real para orçamentos (Materiais + Mão de Obra).
- **Feedback UI:** Sistema de Toasts para alertas de prazos e erros de validação.

---

## 🔐 Segurança e Infraestrutura

### Controle de Acesso (RBAC)

O sistema deve implementar três níveis distintos de permissão:

1. **Admin:** Acesso total a configurações, usuários e financeiro global.
2. **Gestor:** Gestão total de projetos e orçamentos, mas acesso restrito a configurações de sistema.
3. **Colaborador:** Acesso restrito a leitura de projetos e inserção de Diários de Obra.

### Estratégia de Deploy

- Uso obrigatório de **Docker** para isolamento de ambiente.
- Separação de repositórios para Backend e Frontend, mantendo contratos via **OpenAPI/Swagger**.

---

## 🚀 Metodologia de Desenvolvimento

Este projeto segue rigorosamente:

1. **SDD (Spec Driven Development):** O código deve seguir as definições em `/docs/specs/`.
2. **TDD (Test Driven Development):** Implementação baseada no ciclo Red-Green-Refactor.
