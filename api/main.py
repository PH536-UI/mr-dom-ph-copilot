from fastapi import FastAPI
from pydantic import BaseModel
import os
from ..agents.greeting_agent import run_greeting_agent
from ..agents.crm_marketing_agent import run_crm_marketing_agent

app = FastAPI(
    title="Mr. DOM PH Copilot API",
    description="API para orquestração de agentes LangChain/LangGraph e integração com N8N.",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Mr. DOM PH Copilot API está online!"}

# Exemplo de endpoint para LangChain/N8N
class MessageRequest(BaseModel):
    message: str
    user_id: str = "default_user"

@app.post("/process_message")
def process_message(request: MessageRequest):
    """
    Endpoint principal para processar mensagens de entrada via N8N/Mensageria.
    Orquestra o agente LangChain apropriado.
    """
    # Exemplo de orquestração simples: usar o agente de saudação
    try:
        # Lógica de orquestração: decide qual agente usar com base na mensagem
        # Esta é uma lógica simplificada. Em LangGraph/Agno, seria um roteador.
        
        message_lower = request.message.lower()
        
        if "olá" in message_lower or "saudação" in message_lower or "oi" in message_lower:
            agent_response = run_greeting_agent(request.message)
            agent_used = "Greeting Agent"
        elif "vtiger" in message_lower or "mautic" in message_lower or "score" in message_lower or "tag" in message_lower or "contato" in message_lower:
            agent_response = run_crm_marketing_agent(request.message)
            agent_used = "CRM/Marketing Agent"
        else:
            # Fallback para o agente de saudação ou um agente geral
            agent_response = run_greeting_agent(request.message)
            agent_used = "Greeting Agent (Fallback)"
        
        return {
            "status": "success",
            "user_id": request.user_id,
            "input_message": request.message,
            "agent_used": agent_used,
            "agent_response": agent_response
        }
        
        return {
            "status": "success",
            "user_id": request.user_id,
            "input_message": request.message,
            "agent_response": agent_response
        }
    except Exception as e:
        return {
            "status": "error",
            "user_id": request.user_id,
            "input_message": request.message,
            "error_detail": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
