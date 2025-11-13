from fastapi import FastAPI
from pydantic import BaseModel
import os
from ..agents.orchestrator_graph import run_orchestrator

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
        # Lógica de orquestração: usa o orquestrador LangGraph para rotear a mensagem
        agent_response = run_orchestrator(request.message)
        
        # O LangGraph já contém a lógica de roteamento e a resposta final
        return {
            "status": "success",
            "user_id": request.user_id,
            "input_message": request.message,
            "agent_used": "LangGraph Orchestrator",
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
