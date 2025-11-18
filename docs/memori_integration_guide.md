# Guia de Integração Memori - Mr. DOM PH Copilot

**Projeto:** Mr. DOM PH Copilot  
**Data:** 17 de Novembro de 2025  
**Autor:** Manus AI  
**Versão:** 1.0

## 1. Visão Geral do Memori

O **Memori SDK** é uma biblioteca que fornece memória persistente e contexto consciente para sistemas de IA. No contexto do Mr. DOM PH Copilot, o Memori permite que os agentes mantenham histórico de conversas e forneçam respostas mais contextualizadas, compreendendo o contexto completo das interações anteriores.

### 1.1. Benefícios da Integração Memori

| Benefício | Descrição |
| :--- | :--- |
| **Contexto Persistente** | O sistema lembra de conversas anteriores e usa esse contexto para respostas futuras |
| **Conversas Multi-turno** | Suporta conversas longas com múltiplas trocas de mensagens |
| **Redução de Tokens** | Evita repetir contexto em cada chamada ao LLM |
| **Experiência Melhorada** | Usuários recebem respostas mais relevantes e contextualizadas |
| **Auditoria** | Histórico completo de conversas para análise e conformidade |

## 2. Instalação e Configuração

### 2.1. Instalação de Dependências

O Memori SDK foi adicionado ao `requirements.txt`. Para instalar:

```bash
pip install memorisdk openai
```

Ou, se estiver usando o arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2.2. Variáveis de Ambiente

Adicione as seguintes variáveis ao arquivo `.env`:

```ini
# OpenAI API (necessário para Memori + LLM)
OPENAI_API_KEY="sua_chave_openai_aqui"
OPENAI_API_BASE="https://api.openai.com/v1"

# Memori Configuration (opcional - padrões são usados se não definido)
MEMORI_CONSCIOUS_INGEST=true
MEMORI_ENABLE_LOGGING=true
```

## 3. Arquitetura da Integração Memori

### 3.1. Componentes Principais

A integração Memori no Mr. DOM PH Copilot é composta por:

| Componente | Localização | Função |
| :--- | :--- | :--- |
| **MemoriManager** | `integrations/memori_integration.py` | Gerencia a inicialização e operações do Memori |
| **API FastAPI** | `api/main.py` | Endpoints para processar mensagens com Memori |
| **Agno Agent** | `agents/main_agno_agent.py` | Agente principal que usa Memori para contexto |
| **Tools** | `agents/main_agno_agent.py` | Tools para recuperar contexto e orquestrar |

### 3.2. Fluxo de Integração

```
Usuário (N8N/Mensageria)
    ↓
FastAPI (/process_message)
    ↓
MemoriManager (add_to_memory)
    ↓
Agno Main Agent
    ├─ memory_context_retriever_tool (recupera contexto)
    └─ langgraph_orchestrator_tool (processa com contexto)
    ↓
LangGraph Orchestrator
    ├─ Greeting Agent
    └─ CRM/Marketing Agent (Vtiger/Mautic)
    ↓
MemoriManager (add_to_memory - resposta)
    ↓
Resposta com Contexto
```

## 4. Uso da API com Memori

### 4.1. Endpoint Principal: `/process_message`

Processa uma mensagem e mantém contexto através do Memori.

**Requisição:**

```bash
curl -X POST "http://localhost:8000/process_message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá, quem é você?",
    "user_id": "user_123",
    "enable_memory": true,
    "context": {
      "channel": "whatsapp",
      "timestamp": "2025-11-17T10:00:00Z"
    }
  }'
```

**Resposta:**

```json
{
  "status": "success",
  "user_id": "user_123",
  "input_message": "Olá, quem é você?",
  "agent_response": "Olá! Sou o Mr. DOM PH Copilot, um assistente de IA para CRM e marketing.",
  "agent_used": "Agno Main Agent (via LangGraph + Memori)",
  "memory_enabled": true,
  "conversation_id": "user_123_1"
}
```

### 4.2. Endpoint de Status da Memória: `/memory/status`

Obtém o status atual do sistema de memória.

**Requisição:**

```bash
curl -X GET "http://localhost:8000/memory/status"
```

**Resposta:**

```json
{
  "memori_available": true,
  "memory_enabled": true,
  "conscious_ingest": true,
  "conversation_messages": 5,
  "logging_enabled": true
}
```

### 4.3. Endpoint de Resumo da Conversa: `/memory/conversation`

Obtém um resumo da conversa atual.

**Requisição:**

```bash
curl -X GET "http://localhost:8000/memory/conversation"
```

**Resposta:**

```json
{
  "total_messages": 5,
  "memory_enabled": true,
  "user_messages": 3,
  "assistant_messages": 2,
  "conversation_start": "2025-11-17T10:00:00",
  "conversation_end": "2025-11-17T10:15:30"
}
```

### 4.4. Endpoint para Limpar Memória: `/memory/clear`

Limpa o histórico de conversas.

**Requisição:**

```bash
curl -X POST "http://localhost:8000/memory/clear"
```

**Resposta:**

```json
{
  "status": "success",
  "message": "Memory cleared successfully"
}
```

### 4.5. Endpoint para Exportar Conversa: `/memory/export`

Exporta o histórico de conversas para um arquivo.

**Requisição:**

```bash
curl -X POST "http://localhost:8000/memory/export?filepath=conversation_export.json"
```

**Resposta:**

```json
{
  "status": "success",
  "message": "Conversation exported to conversation_export.json"
}
```

## 5. Uso Programático do Memori

### 5.1. Inicializar o Memori Manager

```python
from integrations.memori_integration import initialize_memori

# Inicializar com configurações personalizadas
memori_manager = initialize_memori(conscious_ingest=True, enable_logging=True)
```

### 5.2. Adicionar Mensagens à Memória

```python
# Adicionar mensagem do usuário
memori_manager.add_to_memory(
    role="user",
    content="Qual é o score do contato joao@exemplo.com?",
    metadata={"source": "whatsapp", "timestamp": "2025-11-17T10:00:00"}
)

# Adicionar resposta do assistente
memori_manager.add_to_memory(
    role="assistant",
    content="O score do contato joao@exemplo.com é 85.",
    metadata={"agent": "CRM Agent", "system": "Vtiger"}
)
```

### 5.3. Obter Resposta com Contexto

```python
# Obter resposta com contexto automático do Memori
response = memori_manager.get_contextualized_response(
    user_message="E qual é o email dele?",
    model="gpt-4o-mini",
    system_prompt="Você é um assistente de CRM.",
    temperature=0.7
)

print(response)
# Output: "O email do contato é joao@exemplo.com (conforme mencionado anteriormente)."
```

### 5.4. Obter Resumo da Conversa

```python
summary = memori_manager.get_conversation_summary()
print(summary)
# Output:
# {
#   'total_messages': 4,
#   'memory_enabled': True,
#   'last_message': {...},
#   'conversation_start': '2025-11-17T10:00:00',
#   'conversation_end': '2025-11-17T10:15:30',
#   'user_messages': 2,
#   'assistant_messages': 2
# }
```

### 5.5. Exportar Conversa

```python
# Exportar histórico para arquivo JSON
memori_manager.export_conversation("minha_conversa.json")
```

## 6. Integração com Agentes (Agno)

### 6.1. Usando Memori no Agno Agent

O Agno Agent principal (`agents/main_agno_agent.py`) já está integrado com Memori:

```python
from agents.main_agno_agent import run_main_agno_agent, get_agent_memory_status

# Executar agente (com Memori automático)
response = run_main_agno_agent("Olá, como você pode me ajudar?")

# Obter status da memória
status = get_agent_memory_status()
print(status)

# Obter resumo da conversa
summary = get_agent_conversation_summary()
print(summary)

# Limpar memória se necessário
clear_agent_memory()
```

### 6.2. Tools de Memória no Agno

O Agno Agent possui duas Tools relacionadas a Memória:

| Tool | Descrição |
| :--- | :--- |
| **memory_context_retriever** | Recupera contexto da memória persistente |
| **langgraph_orchestrator** | Processa mensagens com contexto do Memori |

## 7. Boas Práticas

### 7.1. Gerenciamento de Contexto

- **Limite de Histórico:** O sistema mantém os últimos 10 mensagens em contexto para evitar overflow de tokens.
- **Limpeza Periódica:** Limpe a memória periodicamente para conversas muito longas.
- **Exportação:** Exporte conversas importantes para auditoria.

### 7.2. Performance

- **Conscious Ingest:** Mantenha `conscious_ingest=True` para melhor compreensão de contexto.
- **Logging:** Desative logging em produção para melhor performance (`enable_logging=False`).
- **Batch Processing:** Para múltiplos usuários, use instâncias separadas de MemoriManager.

### 7.3. Segurança

- **Dados Sensíveis:** Não armazene dados sensíveis (senhas, tokens) na memória.
- **Exportação:** Proteja arquivos exportados de conversas.
- **Acesso:** Implemente controle de acesso aos endpoints de memória.

## 8. Troubleshooting

### 8.1. Memori SDK Não Disponível

**Erro:** `Memori SDK not installed. Install with: pip install memorisdk`

**Solução:**

```bash
pip install memorisdk openai
```

### 8.2. OpenAI API Key Não Configurada

**Erro:** `OpenAI API key not found`

**Solução:** Adicione a chave ao arquivo `.env`:

```ini
OPENAI_API_KEY="sua_chave_aqui"
```

### 8.3. Memória Não Está Sendo Mantida

**Verificação:**

1. Confirme que `enable_memory=true` no request
2. Verifique o status com `/memory/status`
3. Verifique os logs para erros

### 8.4. Performance Lenta

**Soluções:**

1. Reduza o tamanho do histórico (máximo 10 mensagens)
2. Desative logging em produção
3. Use um modelo mais rápido (ex: `gpt-4o-mini`)

## 9. Exemplos de Uso Completo

### 9.1. Conversa Multi-turno com Memori

```python
from integrations.memori_integration import initialize_memori

# Inicializar
memori = initialize_memori()

# Primeira mensagem
response1 = memori.get_contextualized_response(
    "Meu nome é João e trabalho em vendas"
)
print(f"Bot: {response1}")

# Segunda mensagem (Memori lembra que é João)
response2 = memori.get_contextualized_response(
    "Qual é meu cargo?"
)
print(f"Bot: {response2}")
# Output: "Seu cargo é vendas (conforme você mencionou anteriormente)."

# Resumo
summary = memori.get_conversation_summary()
print(f"Total de mensagens: {summary['total_messages']}")
```

### 9.2. Integração com N8N

No fluxo N8N, configure o nó HTTP para:

```json
{
  "url": "http://localhost:8000/process_message",
  "method": "POST",
  "body": {
    "message": "{{ $json.message }}",
    "user_id": "{{ $json.user_id }}",
    "enable_memory": true,
    "context": {
      "channel": "{{ $json.channel }}",
      "timestamp": "{{ now() }}"
    }
  }
}
```

## 10. Próximos Passos

1. **Testes:** Executar testes de integração com Memori
2. **Otimização:** Ajustar tamanho de histórico e modelo LLM
3. **Expansão:** Adicionar suporte a múltiplos usuários com Memori separado por usuário
4. **Persistência:** Implementar armazenamento em banco de dados para memória de longo prazo

---

**Documentação Preparada por:** Manus AI  
**Data:** 17 de Novembro de 2025  
**Versão:** 1.0
