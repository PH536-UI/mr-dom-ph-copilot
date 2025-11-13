import os
from langchain_core.tools import tool
from typing import Dict, Any
from ...integrations.mautic_connector import MauticConnector

# Configuração do Conector (lê variáveis de ambiente)
MAUTIC_URL = os.getenv("MAUTIC_URL", "https://seu_mautic.com/api")
MAUTIC_USERNAME = os.getenv("MAUTIC_USERNAME", "seu_usuario")
MAUTIC_PASSWORD = os.getenv("MAUTIC_PASSWORD", "sua_senha")

# Instância do Conector (será criada apenas uma vez)
try:
    mautic_connector = MauticConnector(MAUTIC_URL, MAUTIC_USERNAME, MAUTIC_PASSWORD)
except Exception as e:
    print(f"Aviso: Não foi possível inicializar o MauticConnector. As Tools podem falhar se as variáveis de ambiente não estiverem configuradas. Erro: {e}")
    mautic_connector = None

@tool
def query_mautic_segment(email: str) -> Dict[str, Any]:
    """
    Consulta o Mautic para verificar a quais segmentos de marketing um contato pertence.
    Retorna uma lista de segmentos.
    
    NOTA: A API do Mautic não tem um endpoint direto para "segmentos por email".
    Esta Tool simula a lógica: busca o contato e, se encontrado, retorna uma lista
    mock de segmentos (para fins de demonstração da arquitetura).
    """
    if not mautic_connector:
        return {"status": "error", "message": "Mautic Connector não inicializado. Verifique as variáveis de ambiente."}
        
    contact_data = mautic_connector.get_contact_by_email(email)
    
    if contact_data.get("success"):
        # Na API real, seria necessário um endpoint para buscar segmentos do contato.
        # Aqui, retornamos um mock para demonstrar a arquitetura.
        return {
            "status": "success",
            "email": email,
            "segments": ["Clientes VIP (Mock)", "Newsletter Semanal (Mock)"]
        }
    else:
        return {
            "status": "not_found",
            "message": f"Contato com email {email} não encontrado no Mautic. Detalhe: {contact_data.get('error')}"
        }

@tool
def add_mautic_tag(email: str, tag: str) -> Dict[str, Any]:
    """
    Adiciona uma tag específica a um contato no Mautic para segmentação.
    """
    if not mautic_connector:
        return {"status": "error", "message": "Mautic Connector não inicializado. Verifique as variáveis de ambiente."}
        
    # 1. Buscar o ID do contato
    contact_data = mautic_connector.get_contact_by_email(email)
    
    if not contact_data.get("success"):
        return {"status": "not_found", "message": f"Contato com email {email} não encontrado para adicionar a tag."}
        
    contact_id = contact_data["result"]["id"]
    
    # 2. Adicionar a tag
    tag_result = mautic_connector.add_tag_to_contact(contact_id, tag)
    
    if tag_result.get("success"):
        return {
            "status": "success",
            "email": email,
            "tag_added": tag,
            "message": f"Tag '{tag}' adicionada com sucesso ao contato {email} (ID: {contact_id})."
        }
    else:
        return {
            "status": "error",
            "message": f"Falha ao adicionar a tag '{tag}' ao contato {email}. Detalhe: {tag_result.get('error')}"
        }
