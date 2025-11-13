import requests
import json
import os
from typing import Dict, Any

class VtigerConnector:
    """
    Conector para a API REST do Vtiger CRM.
    Autenticação via HTTP Basic Auth (username e accessKey).
    """
    
    def __init__(self, base_url: str, username: str, access_key: str):
        """
        Inicializa o conector com as credenciais.
        
        :param base_url: URL base da sua instância Vtiger (ex: https://sua_instancia.odx.vtiger.com/restapi/v1/vtiger/default)
        :param username: Email de login do CRM.
        :param access_key: Chave de acesso (API Key) gerada no Vtiger.
        """
        self.base_url = base_url.rstrip('/')
        self.auth = (username, access_key)
        self.session = requests.Session()
        self.session.auth = self.auth

    def _request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Método genérico para fazer requisições à API.
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method == "GET":
                response = self.session.get(url, params=data, headers=headers)
            elif method == "POST":
                response = self.session.post(url, data=json.dumps(data), headers=headers)
            # Adicionar outros métodos (PUT, DELETE) conforme necessário
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")

            response.raise_for_status() # Levanta exceção para códigos de status HTTP 4xx/5xx
            
            return response.json()

        except requests.exceptions.HTTPError as errh:
            return {"success": False, "error": f"Erro HTTP: {errh}", "status_code": response.status_code}
        except requests.exceptions.ConnectionError as errc:
            return {"success": False, "error": f"Erro de Conexão: {errc}"}
        except requests.exceptions.Timeout as errt:
            return {"success": False, "error": f"Timeout: {errt}"}
        except requests.exceptions.RequestException as err:
            return {"success": False, "error": f"Erro na Requisição: {err}"}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def query(self, query_string: str) -> Dict[str, Any]:
        """
        Executa uma consulta VQL (Vtiger Query Language).
        """
        return self._request("GET", "query", {"query": query_string})

    def retrieve_by_email(self, email: str, module: str = "Contacts") -> Dict[str, Any]:
        """
        Busca um registro pelo email.
        """
        query_string = f"SELECT * FROM {module} WHERE email = '{email}' LIMIT 1;"
        result = self.query(query_string)
        
        if result.get("success") and result.get("result"):
            return {"success": True, "result": result["result"][0]}
        
        return {"success": False, "error": "Contato não encontrado ou erro na consulta."}

    def update(self, record_id: str, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza um registro existente.
        """
        # O Vtiger API espera o campo 'id' e o campo 'element' com os valores a serem atualizados.
        # O campo 'element' deve ser um JSON string.
        values["id"] = record_id
        data = {
            "operation": "update",
            "element": json.dumps(values)
        }
        # O endpoint para 'update' é o mesmo para 'create', mas com a operação 'update'
        return self._request("POST", "update", data)

# Exemplo de uso (para referência, não será executado)
if __name__ == '__main__':
    # As variáveis de ambiente devem ser configuradas
    VTIGER_URL = os.getenv("VTIGER_URL", "https://seu_vtiger.com/restapi/v1/vtiger/default")
    VTIGER_USERNAME = os.getenv("VTIGER_USERNAME", "seu_usuario@email.com")
    VTIGER_ACCESS_KEY = os.getenv("VTIGER_ACCESS_KEY", "sua_access_key")
    
    connector = VtigerConnector(VTIGER_URL, VTIGER_USERNAME, VTIGER_ACCESS_KEY)
    
    # Exemplo de consulta
    # contact_data = connector.retrieve_by_email("joao@exemplo.com")
    # print(contact_data)
    
    # Exemplo de atualização (requer um ID de registro real)
    # update_result = connector.update("20x12345", {"leadsource": "Web", "cf_lead_score": 90})
    # print(update_result)
