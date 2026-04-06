# 📋 Requisitos do Sistema: Alicerce OS (JELL)

Este documento detalha os Requisitos Funcionais (RF) do **Alicerce OS**, divididos por módulos lógicos e prioridade de implementação.

---

## 🏗️ Módulo 0: Autenticação e Base (Fundação)

_Foco: Segurança e cadastros primários._

| ID       | Título                     | Descrição Breve                                                                                         | Est. Tempo |
| :------- | :------------------------- | :------------------------------------------------------------------------------------------------------ | :--------- |
| **RF01** | Gestão de Acesso (RBAC)    | Implementação de Login via JWT, recuperação de senha e controle de níveis (Admin, Gestor, Colaborador). | 3 dias     |
| **RF02** | Cadastro de Entidades Base | CRUD completo de Clientes, Parceiros/Terceirizados e Colaboradores.                                     | 4 dias     |

---

## 💰 Módulo 1: Financeiro (Prioridade 1)

_Foco: Visibilidade imediata de caixa e saúde financeira._

| ID       | Título               | Descrição Breve                                                                               | Est. Tempo |
| :------- | :------------------- | :-------------------------------------------------------------------------------------------- | :--------- |
| **RF03** | Fluxo de Caixa       | Registro de Entradas (projetos, investimentos) e Saídas (fixas, variáveis, insumos, pessoal). | 6 dias     |
| **RF04** | Dashboard Financeiro | Visualização de KPIs e gráficos com filtros por período, projeto e categoria.                 | 5 dias     |

---

## 🔨 Módulo 2: Gestão de Projetos e Orçamentos

_Foco: Operação e execução das obras._

| ID       | Título                      | Descrição Breve                                                                                                      | Est. Tempo |
| :------- | :-------------------------- | :------------------------------------------------------------------------------------------------------------------- | :--------- |
| **RF05** | Construtor de Orçamentos    | Interface para levantamento de custos de materiais e mão de obra vinculada a parceiros antes da ativação do projeto. | 7 dias     |
| **RF06** | Diário de Obra / Relatórios | Registro de atividades (diário/semanal) com suporte a upload de fotos e logs de progresso.                           | 5 dias     |

---

## 📄 Módulo 3: Licenciamento e Documentos (Parte Crítica)

_Foco: Redução de riscos de prazos e automação._

| ID       | Título                  | Descrição Breve                                                                             | Est. Tempo |
| :------- | :---------------------- | :------------------------------------------------------------------------------------------ | :--------- |
| **RF07** | Gestão de Licenciamento | Cadastro de protocolos (Prefeitura, IDEMA, Bombeiros) com gestão de status manual e anexos. | 5 dias     |
| **RF08** | Sistema de Alertas      | Notificações automáticas via Dashboard/E-mail sobre vencimentos iminentes e pendências.     | 4 dias     |
| **RF09** | Automação (Webscraping) | Integração para consulta automática de status em portais governamentais (Fase Final).       | 15 dias    |

---

## 📅 Resumo do Cronograma (MVP)

O **MVP (Minimum Viable Product)** do Alicerce OS compreende a entrega dos **Módulos 0 e 1**.

- **Prazo Estimado:** 3 a 4 semanas.
- **Objetivo do MVP:** Garantir que o banco de dados no Django esteja normalizado e que o controle financeiro básico esteja funcional e testado via TDD.
