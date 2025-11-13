# Preparação de Ambiente de Trabalho Remoto e Integração de Equipe

**Projeto:** Mr. DOM PH Copilot
**Data:** 12 de Novembro de 2025
**Autor:** Manus AI

## 1. Visão Geral

Este documento detalha as etapas necessárias para configurar o ambiente de desenvolvimento e produção, bem como as diretrizes para a integração da equipe e o uso das ferramentas de comunicação e gestão.

## 2. Configuração do Ambiente de Desenvolvimento (Local/Remoto)

O ambiente de desenvolvimento é baseado em Python e FastAPI, com orquestração de agentes LangChain.

### 2.1. Pré-requisitos

*   **Python 3.11+**
*   **Git**
*   **Docker** (Recomendado para produção e testes de integração)
*   **Acesso ao n8n** (Instância local ou em nuvem)
*   **Chave de API OpenAI-compatível** (Para o LLM, armazenada em variáveis de ambiente)

### 2.2. Configuração Inicial

1.  **Clonar o Repositório:**
    ```bash
    git clone https://github.com/PH536-UI/mr-dom-ph-copilot.git
    cd mr-dom-ph-copilot
    ```
2.  **Configurar o Ambiente Virtual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Instalar Dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Variáveis de Ambiente:**
    Crie um arquivo `.env` na raiz do projeto (adicionado ao `.gitignore`) e adicione as chaves de API necessárias:
    ```ini
    # Chave de API para o LLM (OpenAI, Gemini, etc.)
    OPENAI_API_KEY="sua_chave_aqui"
    OPENAI_API_BASE="https://api.openai.com/v1" # Ajuste se usar outro provedor
    
    # Configurações de acesso ao Vtiger, Mautic, etc.
    VTIGER_URL="https://crm.exemplo.com"
    VTIGER_USERNAME="user"
    VTIGER_PASSWORD="password"
    ```

### 2.3. Execução da API (Desenvolvimento)

```bash
# Certifique-se de estar no ambiente virtual ativado
uvicorn api.main:app --reload
```

## 3. Integração com Ferramentas

### 3.1. Repositório de Código (GitHub)

*   **URL:** `https://github.com/PH536-UI/mr-dom-ph-copilot`
*   **Branch Principal:** `master` (Sugestão de renomear para `main` para seguir o padrão moderno)
*   **Fluxo de Trabalho:** Utilizar o fluxo **GitFlow** simplificado: `feature` branches para desenvolvimento, `master` para produção.

### 3.2. Orquestração e Automação (N8N)

*   **Fluxo de Exemplo:** O arquivo `n8n-flows/example_message_flow.json` contém um fluxo básico para integração de mensageria.
*   **Importação:** O fluxo deve ser importado para a instância do n8n.
*   **Configuração:** O nó **"Chamar API FastAPI (Agente)"** deve ter a URL da API em execução (`http://<SEU_IP_OU_DOMINIO_FASTAPI>:8000/process_message`) ajustada.

### 3.3. Agentes de IA (LangChain/LangGraph)

*   **Localização:** O código dos agentes deve residir na pasta `/agents`.
*   **Padrão:** Cada agente deve ter sua própria Tool (em `/agents/tools`) e sua lógica de orquestração.

## 4. Comunicação e Gestão de Equipe

| Ferramenta | Finalidade | Diretrizes |
|---|---|---|
| **GitHub Issues** | Gestão de Tarefas (Backlog, Bugs, Features) | Usar *labels* para prioridade e tipo. Atribuir tarefas a membros específicos. |
| **Slack/Teams** | Comunicação Síncrona e Rápida | Canais dedicados para `geral`, `dev-backend`, `dev-ia`, `suporte`. |
| **Reuniões Diárias (Daily)** | Alinhamento Rápido | Máximo de 15 minutos. Foco em: O que fiz ontem? O que farei hoje? Quais impedimentos? |

## 5. Próximos Passos Imediatos

1.  **Push Final:** O código atualizado (com o agente e a API) precisa ser enviado para o GitHub.
2.  **Teste de Integração:** Realizar um teste de ponta a ponta: N8N (Webhook) -> FastAPI -> Agente LangChain.
3.  **Desenvolvimento de Agentes:** Iniciar a implementação dos agentes de consulta ao Vtiger e Mautic.
