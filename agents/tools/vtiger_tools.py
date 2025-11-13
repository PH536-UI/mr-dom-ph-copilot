from langchain_core.tools import tool
from typing import Dict, Any

@tool
def query_vtiger_contact(email: str) -> Dict[str, Any]:
    """
    Consulta o Vtiger CRM para obter informações detalhadas de um contato pelo email.
    Retorna um dicionário com os dados do contato (nome, telefone, score, status).
    """
    # --- IMPLEMENTAÇÃO MOCK ---
    # Na implementação real, esta função faria uma chamada à API do Vtiger.
    print(f"MOCK: Consultando Vtiger para o email: {email}")
    
    if "joao" in email.lower():
        return {
            "status": "success",
            "contact_name": "João Silva",
            "phone": "5511987654321",
            "lead_score": 85,
            "status": "Cliente Ativo",
            "last_activity": "2025-11-10"
        }
    elif "maria" in email.lower():
        return {
            "status": "success",
            "contact_name": "Maria Souza",
            "phone": "5521912345678",
            "lead_score": 30,
            "status": "Lead Frio",
            "last_activity": "2025-08-01"
        }
    else:
        return {
            "status": "not_found",
            "message": f"Contato com email {email} não encontrado no Vtiger."
        }
    # --- FIM IMPLEMENTAÇÃO MOCK ---

@tool
def update_vtiger_lead_score(email: str, new_score: int) -> Dict[str, Any]:
    """
    Atualiza o Lead Score de um contato no Vtiger CRM.
    O score deve ser um número inteiro entre 0 e 100.
    """
    # --- IMPLEMENTAÇÃO MOCK ---
    # Na implementação real, esta função faria uma chamada à API do Vtiger para atualizar o score.
    print(f"MOCK: Atualizando Lead Score de {email} para {new_score} no Vtiger.")
    
    if new_score < 0 or new_score > 100:
        return {"status": "error", "message": "Score inválido. Deve ser entre 0 e 100."}
    
    return {
        "status": "success",
        "email": email,
        "old_score": "Simulado",
        "new_score": new_score,
        "message": f"Lead Score de {email} atualizado com sucesso para {new_score}."
    }
    # --- FIM IMPLEMENTAÇÃO MOCK ---
