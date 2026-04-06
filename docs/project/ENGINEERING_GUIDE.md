# 🛠️ Guia de Engenharia de Software: Fluxo SDD + TDD

**Projeto:** Alicerce OS (Gestão JELL)
**Responsáveis:** Gabriel Barroso Faustino Gomes e Semaias Rangel
**Versão:** 1.0

---

## 1. Introdução aos Paradigmas

Este projeto adota uma abordagem rigorosa baseada em dois pilares fundamentais para garantir a entrega de um software resiliente, escalável e alinhado às regras de negócio da JELL.

### 1.1 Spec Driven Development (SDD)

O **SDD** estabelece a documentação técnica (Especificação) como a **"Fonte Única da Verdade"**. Antes de qualquer linha de código ser escrita, o comportamento esperado, as interfaces de dados e as regras de negócio são definidos em arquivos de especificação. Isso elimina ambiguidades e fornece o contexto necessário para o uso eficiente de ferramentas de IA (como o Cursor), garantindo que a geração de código seja precisa e fundamentada.

### 1.2 Test Driven Development (TDD)

O **TDD** é um processo iterativo de desenvolvimento que inverte a ordem tradicional de codificação, seguindo o ciclo **Red-Green-Refactor**:

1.  **🔴 Red:** Escrevemos um teste automatizado que falha, baseado estritamente na especificação.
2.  **🟢 Green:** Escrevemos o código mínimo necessário para fazer o teste passar.
3.  **🔵 Refactor:** Melhoramos o código mantendo a integridade funcional garantida pelos testes.

---

## 2. Estrutura de Repositórios e Domínios

O ecossistema é dividido em dois repositórios independentes. Cada um possui seu próprio ciclo de vida de Specs e Testes, comunicando-se através de um contrato de API bem definido.

| Repositório              | Tecnologia   | Foco da Spec                             | Framework de Teste   |
| :----------------------- | :----------- | :--------------------------------------- | :------------------- |
| **Backend (API)**        | Django + DRF | Modelagem, Regras de Negócio e Endpoints | Pytest / Django Test |
| **Frontend (Dashboard)** | Next.js + TS | UX/UI, Fluxos de Navegação e Estados     | Jest / Playwright    |

---

## 3. Fluxo de Implementação Passo a Passo

Para cada nova funcionalidade (feature), o desenvolvedor deve seguir rigorosamente este fluxo:

### Passo 1: Definição da Spec (A Verdade)

Crie ou atualize o arquivo em `docs/specs/[feature_name].md`.

- **No Backend:** Defina o Schema do banco de dados, campos obrigatórios, validações de status e códigos de retorno HTTP.
- **No Frontend:** Defina os componentes Shadcn/UI necessários, os estados da tela (loading, error, success) e as chamadas de API esperadas.

### Passo 2: O Ciclo de Testes (A Garantia)

Utilize a Spec como contexto para a IA gerar os testes.

- **Backend:** Crie testes de integração que validem as constraints do banco e as respostas dos endpoints.
- **Frontend:** Crie testes unitários para componentes lógicos e testes de integração para o fluxo de dados com o React Query.
- **Nota:** _O teste deve obrigatoriamente falhar antes da implementação do código funcional._

### Passo 3: Implementação Orientada (A Execução)

Com a Spec e os Testes falhos abertos no contexto (utilizando `@Files` no Cursor), solicite a implementação do código funcional. A IA utilizará a Spec como guia e o Teste como validador imediato.

### Passo 4: Sincronização de Contratos

Sempre que uma alteração na Spec do Backend afetar o contrato da API, a Spec do Frontend deve ser atualizada imediatamente antes da implementação da UI, garantindo a paridade entre os sistemas.

---

## 4. Padrões de Qualidade

- **Imutabilidade da Spec:** Nenhuma funcionalidade deve existir no código se não estiver descrita na Spec. Se o código mudar, a Spec muda primeiro.
- **Cobertura de Testes:** Priorizamos testes de "Caminho Crítico" (ex: cálculos financeiros e prazos de licença) sobre cobertura superficial de linhas de código.
- **Documentação Viva:** As specs devem ser escritas em Markdown claro, servindo tanto para o desenvolvedor quanto para a auditoria de processos da empresa JELL.

> _"Código é efêmero; a lógica de negócio documentada e testada é o ativo real da empresa."_

---

## 5. Registro de Atividades (Prompt Reports)

Ao final de cada iteração relevante ou entrega de módulo, a IA deve gerar um relatório detalhado de progresso.

1. **Localização**: Os relatórios devem ser salvos na pasta `docs/prompt_reports/`.
2. **Nomenclatura**: O arquivo deve seguir o padrão `YYYYMMDD_HHMMSS_report.md` (Ex: `20260403_153022_module0_setup.md`).
3. **Conteúdo**:
    - Resumo técnico do que foi implementado.
    - Estado atual dos testes (Pass/Fail).
    - Comandos novos introduzidos (Docker, Migrations, etc).
    - Próximos passos sugeridos.

---

## 6. Política de Versionamento e Commits

O projeto adota o padrão **Conventional Commits** integrado ao ID das tasks definidas no `REQUIREMENTS.md`.

### 6.1 Estrutura do Comentário

Todo commit deve seguir o formato:
`<tipo>(<escopo>): [ID_TASK] <descrição curta>`

**Tipos permitidos:**

- `feat`: Nova funcionalidade.
- `fix`: Correção de bug.
- `docs`: Alterações em documentação.
- `test`: Adição ou modificação de testes.
- `refactor`: Alteração de código que não corrige bug nem adiciona feature.
- `chore`: Atualizações de build, pacotes, etc.

**Exemplo:** `feat(financeiro): [RF03] implementa lógica de cálculo de saldo`

### 6.2 Granularidade e Ordem

Os commits devem ser **atômicos** e realizados na ordem de execução da task. Não é permitido commitar feature e teste no mesmo bloco.

1. **Commit de Teste (Red):** `test(core): [RF05] cria testes unitários para orçamentos`
2. **Commit de Feature (Green):** `feat(core): [RF05] implementa models e lógica de itens de orçamento`
3. **Commit de Doc:** `docs(specs): [RF05] atualiza spec de projetos com novos campos`
