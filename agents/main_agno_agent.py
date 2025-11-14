from agno import Agent, Tool
from agno.types import Message
from typing import Dict, Any
import json

# Importar o orquestrador LangGraph
from .orchestrator_graph import run_orchestrator

# --- 1. Definir a Tool para o LangGraph ---
# O Agno Agent usará esta Tool para delegar a orquestração ao LangGraph.
@Tool(
    name="langgraph_orchestrator",
    description="Use esta ferramenta para processar qualquer mensagem que precise de roteamento complexo, como saudações, consultas de CRM (Vtiger) ou marketing (Mautic). Ela encapsula a lógica de múltiplos agentes."
)
def langgraph_orchestrator_tool(message: str) -> str:
    """
    Delega a mensagem de entrada para o orquestrador LangGraph.
    """
    print(f"AGNO DELEGANDO PARA LANGGRAPH: {message}")
    try:
        # Chama a função de execução do LangGraph
        result = run_orchestrator(message)
        return result
    except Exception as e:
        return f"Erro ao executar o LangGraph: {e}"

# --- 2. Criar o Agno Agent Principal ---
class MainAgnoAgent(Agent):
    """
    Agente principal do Mr. DOM PH Copilot.
    Ele atua como um roteador de alto nível e orquestrador.
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="Mr. DOM PH Copilot Main Agent",
            description="O agente principal responsável por orquestrar a comunicação e as operações de CRM/Marketing. Ele delega tarefas complexas ao orquestrador LangGraph.",
            tools=[langgraph_orchestrator_tool],
            **kwargs
        )

    def run(self, message: Message) -> Message:
        """
        Lógica principal de execução do Agno Agent.
        """
        # O Agno Agent pode ter sua própria lógica de raciocínio (LLM) aqui,
        # mas para este exemplo, ele simplesmente delega ao LangGraph.
        
        # Para demonstrar o uso da Tool, vamos forçar o uso dela.
        # Em um cenário real, o LLM do Agno decidiria se usa a Tool ou responde diretamente.
        
        # Simula a decisão de usar a Tool
        response_text = self.langgraph_orchestrator_tool(message.content)
        
        return Message(content=response_text)

# --- 3. Função de Execução para a API ---
# Instância global do Agno Agent
main_agent = MainAgnoAgent()

def run_main_agno_agent(input_message: str) -> str:
    """
    Executa o Agno Agent principal.
    """
    # Cria uma mensagem Agno a partir da string de entrada
    input_message_obj = Message(content=input_message)
    
    # Executa o agente
    output_message = main_agent.run(input_message_obj)
    
    # Retorna o conteúdo da mensagem de saída
    return output_message.content

if __name__ == "__main__":
    # Exemplo de uso
    print("--- Teste Agno: Saudação ---")
    response1 = run_main_agno_agent("Olá, quem é você?")
    print(f"Resposta Final: {response1}\n")
    
    print("--- Teste Agno: CRM ---")
    response2 = run_main_agno_agent("Qual o score do contato joao@exemplo.com no Vtiger?")
    print(f"Resposta Final: {response2}")
