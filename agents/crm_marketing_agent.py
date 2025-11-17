from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage

# Importar as Tools
from .tools.vtiger_tools import query_vtiger_contact, update_vtiger_lead_score
from .tools.mautic_tools import query_mautic_segment, add_mautic_tag

# Configuração do LLM
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

# 1. Definir todas as Tools disponíveis para o Agente de CRM/Marketing
crm_marketing_tools = [
    query_vtiger_contact,
    update_vtiger_lead_score,
    query_mautic_segment,
    add_mautic_tag
]

# 2. Definir o Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é o Agente de CRM e Marketing do Mr. DOM PH Copilot. Sua função é analisar a solicitação do usuário e usar as ferramentas disponíveis (Vtiger e Mautic) para consultar dados de contato, atualizar o Lead Score ou adicionar tags de marketing. Responda de forma concisa e profissional, sempre citando os resultados das ferramentas."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# 3. Criar o Agente
crm_marketing_agent = create_tool_calling_agent(llm, crm_marketing_tools, prompt)

# 4. Criar o Executor do Agente
agent_executor = AgentExecutor(agent=crm_marketing_agent, tools=crm_marketing_tools, verbose=True)

def run_crm_marketing_agent(input_message: str) -> str:
    """
    Executa o Agente de CRM/Marketing com a mensagem de entrada.
    """
    # Para simplificar a integração com a API, usamos o AgentExecutor diretamente.
    # Em uma implementação LangGraph, este seria um "node" do grafo.
    
    # Simulação de histórico de chat vazio
    chat_history = [] 
    
    result = agent_executor.invoke({
        "input": input_message,
        "chat_history": chat_history
    })
    
    return result["output"]

if __name__ == "__main__":
    # Exemplo de uso: Consulta
    print("--- Exemplo 1: Consulta de Contato ---")
    response1 = run_crm_marketing_agent("Qual o status e score do contato com email joao@exemplo.com?")
    print(f"Resposta do Agente: {response1}\n")
    
    # Exemplo de uso: Atualização
    print("--- Exemplo 2: Atualização de Score e Tag ---")
    response2 = run_crm_marketing_agent("Atualize o score de maria@exemplo.com para 90 e adicione a tag 'High_Value'.")
    print(f"Resposta do Agente: {response2}")
