from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI # Usaremos um modelo compatível com OpenAI

# Importar a Tool
from .tools.greeting_tool import greet_user

# Configuração do LLM (usando o modelo compatível com OpenAI)
# O API Key e base URL são injetados automaticamente pelo ambiente
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

# 1. Definir a Tool
tools = [greet_user]

# 2. Definir o Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é o Mr. DOM PH Copilot, um assistente de IA amigável e prestativo. Seu objetivo é saudar o usuário e, se possível, usar a ferramenta 'greet_user' para uma saudação personalizada. Se a ferramenta não for apropriada, responda diretamente."),
    ("human", "{input}")
])

# 3. Criar a Chain (para um agente simples sem LangGraph)
# Esta é uma implementação simplificada. A orquestração completa virá na API.
agent_chain = (
    RunnablePassthrough.assign(
        tools=lambda x: tools,
        tool_names=lambda x: ", ".join([t.name for t in tools])
    )
    | prompt
    | llm
    | StrOutputParser()
)

def run_greeting_agent(input_message: str) -> str:
    """
    Executa o agente de saudação com a mensagem de entrada.
    """
    # Para simplificar, vamos apenas usar o LLM para responder diretamente por enquanto,
    # simulando a lógica de um agente. A integração real com ferramentas e LangGraph
    # é mais complexa e será feita na próxima fase.
    
    # Simulação de resposta direta
    response = llm.invoke(prompt.format(input=input_message))
    return response.content

if __name__ == "__main__":
    print(run_greeting_agent("Olá, meu nome é João"))
    print(run_greeting_agent("Qual é a capital da França?"))
