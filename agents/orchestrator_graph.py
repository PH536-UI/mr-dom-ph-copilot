from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
import operator

# Importar os agentes
from .greeting_agent import run_greeting_agent
from .crm_marketing_agent import run_crm_marketing_agent

# --- 1. Definição do Estado do Grafo ---
class AgentState(TypedDict):
    """
    Representa o estado do grafo.
    """
    # A mensagem de entrada do usuário
    input: str
    # Histórico de mensagens
    chat_history: Annotated[List[BaseMessage], operator.add]
    # O nome do agente que deve ser executado em seguida
    next_agent: str
    # Resultado da execução do agente
    agent_output: str

# --- 2. Definição dos Nodes (Agentes) ---

def call_greeting_agent(state: AgentState) -> AgentState:
    """
    Node para chamar o Agente de Saudação.
    """
    print("--- Executando Agente de Saudação ---")
    output = run_greeting_agent(state["input"])
    return {"agent_output": output}

def call_crm_marketing_agent(state: AgentState) -> AgentState:
    """
    Node para chamar o Agente de CRM/Marketing.
    """
    print("--- Executando Agente de CRM/Marketing ---")
    output = run_crm_marketing_agent(state["input"])
    return {"agent_output": output}

# --- 3. Definição do Roteador (Router) ---

def router(state: AgentState) -> str:
    """
    Função de roteamento para decidir qual agente executar.
    Em uma implementação real, usaria um LLM para roteamento.
    Aqui, usamos a lógica de palavras-chave da API para demonstração.
    """
    message_lower = state["input"].lower()
    
    if "vtiger" in message_lower or "mautic" in message_lower or "score" in message_lower or "tag" in message_lower or "contato" in message_lower:
        return "crm_marketing_agent"
    else:
        return "greeting_agent"

# --- 4. Construção do Grafo ---

# 4.1. Inicializa o grafo com o estado
workflow = StateGraph(AgentState)

# 4.2. Adiciona os nodes
workflow.add_node("greeting_agent", call_greeting_agent)
workflow.add_node("crm_marketing_agent", call_crm_marketing_agent)

# 4.3. Define o ponto de entrada
workflow.set_entry_point("router")

# 4.4. Adiciona o node de roteamento
workflow.add_node("router", router)

# 4.5. Adiciona as edges condicionais
workflow.add_conditional_edges(
    "router",
    router,
    {
        "greeting_agent": "greeting_agent",
        "crm_marketing_agent": "crm_marketing_agent",
    },
)

# 4.6. Define as edges finais
workflow.add_edge("greeting_agent", END)
workflow.add_edge("crm_marketing_agent", END)

# 4.7. Compila o grafo
app = workflow.compile()

# --- 5. Função de Execução para a API ---

def run_orchestrator(input_message: str) -> str:
    """
    Executa o orquestrador LangGraph.
    """
    initial_state = {
        "input": input_message,
        "chat_history": [],
        "next_agent": "",
        "agent_output": ""
    }
    
    # Executa o grafo
    final_state = app.invoke(initial_state)
    
    # Retorna a saída do agente
    return final_state["agent_output"]

if __name__ == "__main__":
    # Exemplo de uso
    print("--- Teste 1: Saudação ---")
    response1 = run_orchestrator("Olá, quem é você?")
    print(f"Resposta Final: {response1}\n")
    
    print("--- Teste 2: CRM ---")
    response2 = run_orchestrator("Qual o score do contato joao@exemplo.com no Vtiger?")
    print(f"Resposta Final: {response2}")
