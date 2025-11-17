import os
from langchain_core.tools import tool
from typing import Dict, Any
from ...integrations.vtiger_connector import VtigerConnector

# Configuração do Conector (lê variáveis de ambiente)
VTIGER_URL = os.getenv("VTIGER_URL", "https://seu_vtiger.com/restapi/v1/vtiger/default")
VTIGER_USERNAME = os.getenv("VTIGER_USERNAME", "seu_usuario@email.com")
VTIGER_ACCESS_KEY = os.getenv("VTIGER_ACCESS_KEY", "sua_access_key")

# Instância do Conector (será criada apenas uma vez)
try:
    vtiger_connector = VtigerConnector(VTIGER_URL, VTIGER_USERNAME, VTIGER_ACCESS_KEY)
except Exception as e:
    print(f"Aviso: Não foi possível inicializar o VtigerConnector. As Tools podem falhar se as variáveis de ambiente não estiverem configuradas. Erro: {e}")
    vtiger_connector = None # Permite que o código continue, mas as chamadas falharão

@tool
def query_vtiger_contact(email: str) -> Dict[str, Any]:
    """
    Consulta o Vtiger CRM para obter informações detalhadas de um contato pelo email.
    Retorna um dicionário com os dados do contato (nome, telefone, score, status).
    """
        if not vtiger_connector:
            return {"status": "error", "message": "Vtiger Connector não inicializado. Verifique as variáveis de ambiente."}
            
        result = vtiger_connector.retrieve_by_email(email, module="Contacts")
        
        if result.get("success"):
        contact = result["result"]
        # Mapeamento simplificado dos campos do Vtiger para o formato esperado pelo Agente
        return {
            "status": "success",
            "contact_id": contact.get("id"),
            "contact_name": f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip(),
            "phone": contact.get("phone"),
            "lead_score": contact.get("cf_lead_score"), # Assumindo um campo customizado para score
            "status": contact.get("leadstatus"),
            "last_activity": contact.get("modifiedtime")
        }
    else:
        return {
            "status": "not_found",
            "message": f"Contato com email {email} não encontrado no Vtiger. Detalhe: {result.get('error')}"
        }

@tool
def update_vtiger_lead_score(email: str, new_score: int) -> Dict[str, Any]:
    """
    Atualiza o Lead Score de um contato no Vtiger CRM.
    O score deve ser um número inteiro entre 0 e 100.
    """
    if not vtiger_connector:
        return {"status": "error", "message": "Vtiger Connector não inicializado. Verifique as variáveis de ambiente."}
        
    if new_score < 0 or new_score > 100:
        return {"status": "error", "message": "Score inválido. Deve ser entre 0 e 100."}
        
    # 1. Buscar o ID do contato
    contact_data = vtiger_connector.retrieve_by_email(email, module="Contacts")
    
    if not contact_data.get("success"):
        return {"status": "not_found", "message": f"Contato com email {email} não encontrado para atualização."}
        
    contact_id = contact_data["result"]["id"]
    
    # 2. Atualizar o score
    update_values = {"cf_lead_score": new_score} # Assumindo um campo customizado para score
    update_result = vtiger_connector.update(contact_id, update_values)
    
    if update_result.get("success"):
        return {
            "status": "success",
            "email": email,
            "new_score": new_score,
            "message": f"Lead Score de {email} (ID: {contact_id}) atualizado com sucesso para {new_score}."
        }
    else:
        return {
            "status": "error",
            "message": f"Falha ao atualizar o score de {email}. Detalhe: {update_result.get('error')}"
        }
