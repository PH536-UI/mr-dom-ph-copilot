from langchain_core.tools import tool
from typing import Dict, Any

@tool
def query_mautic_segment(email: str) -> Dict[str, Any]:
    """
    Consulta o Mautic para verificar a quais segmentos de marketing um contato pertence.
    Retorna uma lista de segmentos.
    """
    # --- IMPLEMENTAÇÃO MOCK ---
    # Na implementação real, esta função faria uma chamada à API do Mautic.
    print(f"MOCK: Consultando Mautic para segmentos do email: {email}")
    
    if "joao" in email.lower():
        return {
            "status": "success",
            "email": email,
            "segments": ["Clientes VIP", "Newsletter Semanal", "Engajamento Alto"]
        }
    elif "maria" in email.lower():
        return {
            "status": "success",
            "email": email,
            "segments": ["Leads Frios", "Campanha de Reengajamento"]
        }
    else:
        return {
            "status": "not_found",
            "message": f"Contato com email {email} não encontrado no Mautic."
        }
    # --- FIM IMPLEMENTAÇÃO MOCK ---

@tool
def add_mautic_tag(email: str, tag: str) -> Dict[str, Any]:
    """
    Adiciona uma tag específica a um contato no Mautic para segmentação.
    """
    # --- IMPLEMENTAÇÃO MOCK ---
    # Na implementação real, esta função faria uma chamada à API do Mautic para adicionar a tag.
    print(f"MOCK: Adicionando tag '{tag}' ao contato {email} no Mautic.")
    
    return {
        "status": "success",
        "email": email,
        "tag_added": tag,
        "message": f"Tag '{tag}' adicionada com sucesso ao contato {email}."
    }
    # --- FIM IMPLEMENTAÇÃO MOCK ---
