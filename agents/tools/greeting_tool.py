from langchain_core.tools import tool

@tool
def greet_user(name: str) -> str:
    """
    Saúda o usuário com uma mensagem personalizada.
    Útil para iniciar conversas e confirmar a identidade do usuário.
    """
    return f"Olá, {name}! Bem-vindo ao Mr. DOM PH Copilot. Como posso ajudar você hoje?"
