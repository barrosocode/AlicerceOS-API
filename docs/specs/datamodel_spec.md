# Data Model Specification (ERD Implementation)

## Objetivo

Definir a estrutura de dados central do sistema Alicerce OS para o Django ORM.

## Entidades Base

### 1. Usuarios (Custom User)

- Extend `AbstractUser`
- **Fields**: `email` (unique), `role` (Admin, Gestor, Colaborador).
- **TDD Rule**: O login deve ser realizado via e-mail, não username.

### 2. Clientes & Parceiros

- **Cliente**: `nome`, `cpf_cnpj`, `contato`, `data_criacao`.
- **Parceiro**: `nome`, `especialidade` (Choice: Eletrica, Civil, etc), `telefone`.

### 3. Projetos

- **Fields**:
    - `nome` (char)
    - `cliente` (FK)
    - `status` (Choice: Orcamento, Ativo, Pausado, Finalizado)
    - `data_inicio`, `data_entrega_prevista`
    - `orcamento_estimado` (decimal)

### 4. Financeiro (Gasto/Entrada)

- **Fields**:
    - `projeto` (FK, opcional para gastos fixos)
    - `tipo` (Choice: Entrada, Saida)
    - `categoria` (Choice: Material, Mao_de_Obra, Licenca, Fixo, Outros)
    - `valor` (decimal, max_digits=12, decimal_places=2)
    - `parceiro` (FK, null=True)
    - `data_pagamento` (date)

### 5. Licenciamento

- **OrgaoEmissor**: `nome` (IDEMA, Bombeiros, etc), `url_portal`.
- **Licenca**:
    - `projeto` (FK)
    - `orgao` (FK)
    - `numero_processo` (char)
    - `data_vencimento` (date)
    - `status` (Choice: Pendente, Aprovado, Alerta)

## Regras de Integridade

- Deletar um `Projeto` não deve deletar os `Gastos` associados (Set Null ou Protect).
- Todo `Gasto` do tipo "Mao_de_Obra" deve obrigatoriamente ter um `Parceiro` vinculado.
