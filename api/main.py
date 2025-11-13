from fastapi import FastAPI

app = FastAPI(
    title="Mr. DOM PH Copilot API",
    description="API para orquestração de agentes LangChain/LangGraph e integração com N8N.",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Mr. DOM PH Copilot API está online!"}

# Exemplo de endpoint para LangChain/N8N
@app.post("/process_message")
def process_message(message: str):
    # Lógica de orquestração do LangChain/LangGraph virá aqui
    # Por enquanto, apenas um placeholder
    response = f"Mensagem recebida: '{message}'. Processamento de IA em desenvolvimento."
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
