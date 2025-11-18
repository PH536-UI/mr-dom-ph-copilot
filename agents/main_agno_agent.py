from agno import Agent, Tool
from agno.types import Message
from typing import Dict, Any
import json
import logging

# Importar o orquestrador LangGraph
from .orchestrator_graph import run_orchestrator

# Importar Memori
from ..integrations.memori_integration import get_memori_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- 1. Definir a Tool para o LangGraph com Memori ---
# O Agno Agent usará esta Tool para delegar a orquestração ao LangGraph.
@Tool(
    name="langgraph_orchestrator",
    description="Use esta ferramenta para processar qualquer mensagem que precise de roteamento complexo, como saudações, consultas de CRM (Vtiger) ou marketing (Mautic). Ela encapsula a lógica de múltiplos agentes com suporte a memória persistente."
)
def langgraph_orchestrator_tool(message: str) -> str:
    """
    Delega a mensagem de entrada para o orquestrador LangGraph.
    Mantém contexto através do Memori.
    """
    logger.info(f"🔄 AGNO DELEGANDO PARA LANGGRAPH: {message}")
    try:
        # Chama a função de execução do LangGraph
        result = run_orchestrator(message)
        return result
    except Exception as e:
        logger.error(f"❌ Erro ao executar o LangGraph: {e}")
        return f"Erro ao executar o LangGraph: {e}"


@Tool(
    name="memory_context_retriever",
    description="Recupera contexto da memória persistente para entender conversas anteriores e fornecer respostas mais contextualizadas."
)
def memory_context_retriever_tool() -> str:
    """
    Recupera o contexto da memória persistente.
    """
    try:
        memori_manager = get_memori_manager()
        summary = memori_manager.get_conversation_summary()
        
        context_info = f"""
        Contexto da Conversa:
        - Total de mensagens: {summary['total_messages']}
        - Mensagens do usuário: {summary['user_messages']}
        - Respostas do assistente: {summary['assistant_messages']}
        - Memória ativa: {summary['memory_enabled']}
        """
        
        logger.info(f"📚 Contexto recuperado da memória: {summary['total_messages']} mensagens")
        return context_info
    except Exception as e:
        logger.error(f"❌ Erro ao recuperar contexto: {e}")
        return "Contexto não disponível"


# --- 2. Criar o Agno Agent Principal com Memori ---
class MainAgnoAgent(Agent):
    """
    Agente principal do Mr. DOM PH Copilot com suporte a Memori.
    Ele atua como um roteador de alto nível e orquestrador com memória persistente.
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="Mr. DOM PH Copilot Main Agent",
            description="O agente principal responsável por orquestrar a comunicação e as operações de CRM/Marketing com memória persistente. Ele delega tarefas complexas ao orquestrador LangGraph.",
            tools=[langgraph_orchestrator_tool, memory_context_retriever_tool],
            **kwargs
        )
        self.memori_manager = get_memori_manager()
        logger.info("✅ Agno Agent inicializado com suporte a Memori")

    def run(self, message: Message) -> Message:
        """
        Lógica principal de execução do Agno Agent com Memori.
        """
        try:
            # Adicionar mensagem do usuário à memória
            if self.memori_manager.memory_enabled:
                self.memori_manager.add_to_memory("user", message.content)
                logger.info(f"📝 Mensagem adicionada à memória: {message.content[:50]}...")
            
            # Recuperar contexto da memória
            context = self.memory_context_retriever_tool()
            
            # Processar através do LangGraph com contexto
            response_text = self.langgraph_orchestrator_tool(message.content)
            
            # Adicionar resposta do agente à memória
            if self.memori_manager.memory_enabled:
                self.memori_manager.add_to_memory("assistant", response_text)
                logger.info(f"💾 Resposta salva na memória")
            
            return Message(content=response_text)
        
        except Exception as e:
            logger.error(f"❌ Erro ao executar Agno Agent: {e}")
            return Message(content=f"Erro ao processar mensagem: {str(e)}")

    def get_memory_status(self) -> Dict[str, Any]:
        """
        Retorna o status da memória do agente.
        """
        return self.memori_manager.get_memory_status()

    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Retorna um resumo da conversa.
        """
        return self.memori_manager.get_conversation_summary()

    def clear_memory(self) -> None:
        """
        Limpa a memória da conversa.
        """
        self.memori_manager.clear_memory()
        logger.info("🗑️ Memória do agente limpa")


# --- 3. Função de Execução para a API ---
# Instância global do Agno Agent
main_agent = MainAgnoAgent()


def run_main_agno_agent(input_message: str) -> str:
    """
    Executa o Agno Agent principal com suporte a Memori.
    
    Args:
        input_message (str): A mensagem de entrada do usuário
    
    Returns:
        str: A resposta do agente
    """
    try:
        # Cria uma mensagem Agno a partir da string de entrada
        input_message_obj = Message(content=input_message)
        
        # Executa o agente
        output_message = main_agent.run(input_message_obj)
        
        # Retorna o conteúdo da mensagem de saída
        return output_message.content
    
    except Exception as e:
        logger.error(f"❌ Erro ao executar Agno Agent: {e}")
        return f"Erro ao processar mensagem: {str(e)}"


def get_agent_memory_status() -> Dict[str, Any]:
    """
    Retorna o status da memória do agente.
    """
    return main_agent.get_memory_status()


def get_agent_conversation_summary() -> Dict[str, Any]:
    """
    Retorna um resumo da conversa do agente.
    """
    return main_agent.get_conversation_summary()


def clear_agent_memory() -> None:
    """
    Limpa a memória do agente.
    """
    main_agent.clear_memory()


if __name__ == "__main__":
    # Exemplo de uso com Memori
    print("=" * 60)
    print("TESTE AGNO COM MEMORI")
    print("=" * 60)
    
    print("\n--- Teste 1: Saudação ---")
    response1 = run_main_agno_agent("Olá, quem é você?")
    print(f"Resposta: {response1}\n")
    
    print("--- Teste 2: Contexto da Memória ---")
    summary = get_agent_conversation_summary()
    print(f"Resumo da Conversa: {summary}\n")
    
    print("--- Teste 3: CRM ---")
    response2 = run_main_agno_agent("Qual o score do contato joao@exemplo.com no Vtiger?")
    print(f"Resposta: {response2}\n")
    
    print("--- Teste 4: Contexto Atualizado ---")
    summary = get_agent_conversation_summary()
    print(f"Resumo Atualizado: {summary}\n")
    
    print("--- Status da Memória ---")
    status = get_agent_memory_status()
    print(f"Status: {json.dumps(status, indent=2)}")
