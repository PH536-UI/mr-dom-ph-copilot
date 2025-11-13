import requests
import json
import os
from typing import Dict, Any, List

class MauticConnector:
    """
    Conector para a API REST do Mautic.
    Autenticação via OAuth 2.0 (recomendado) ou Basic Auth.
    Usaremos Basic Auth para simplificar o exemplo, mas a implementação real deve usar OAuth.
    """
    
    def __init__(self, base_url: str, username: str, password: str):
        """
        Inicializa o conector com as credenciais.
        
        :param base_url: URL base da sua instância Mautic (ex: https://seu_mautic.com/api)
        :param username: Nome de usuário do Mautic.
        :param password: Senha do Mautic.
        """
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def _request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Método genérico para fazer requisições à API.
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, params=data, headers=self.headers)
            elif method == "POST":
                response = self.session.post(url, data=json.dumps(data), headers=self.headers)
            elif method == "PATCH":
                response = self.session.patch(url, data=json.dumps(data), headers=self.headers)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")

            response.raise_for_status()
            
            return response.json()

        except requests.exceptions.HTTPError as errh:
            return {"success": False, "error": f"Erro HTTP: {errh}", "status_code": response.status_code, "response_text": response.text}
        except requests.exceptions.RequestException as err:
            return {"success": False, "error": f"Erro na Requisição: {err}"}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def get_contact_by_email(self, email: str) -> Dict[str, Any]:
        """
        Busca um contato pelo email.
        A API do Mautic não tem um endpoint direto por email, então usamos a busca.
        """
        endpoint = "contacts"
        # Busca avançada: search=email:seu@email.com
        data = {"search": f"email:{email}", "limit": 1}
        result = self._request("GET", endpoint, data)
        
        if result.get("contacts"):
            # A busca retorna um dicionário de contatos, pegamos o primeiro
            contact_id = list(result["contacts"].keys())[0]
            return {"success": True, "result": result["contacts"][contact_id]}
        
        return {"success": False, "error": "Contato não encontrado ou erro na consulta."}

    def add_tag_to_contact(self, contact_id: int, tag: str) -> Dict[str, Any]:
        """
        Adiciona uma tag a um contato.
        Endpoint: /contacts/{id}/tags/add
        """
        endpoint = f"contacts/{contact_id}/tags/add"
        data = {"tags": [tag]}
        return self._request("POST", endpoint, data)

# Exemplo de uso (para referência, não será executado)
if __name__ == '__main__':
    # As variáveis de ambiente devem ser configuradas
    MAUTIC_URL = os.getenv("MAUTIC_URL", "https://seu_mautic.com/api")
    MAUTIC_USERNAME = os.getenv("MAUTIC_USERNAME", "seu_usuario")
    MAUTIC_PASSWORD = os.getenv("MAUTIC_PASSWORD", "sua_senha")
    
    connector = MauticConnector(MAUTIC_URL, MAUTIC_USERNAME, MAUTIC_PASSWORD)
    
    # Exemplo de consulta
    # contact_data = connector.get_contact_by_email("joao@exemplo.com")
    # print(contact_data)
    
    # Exemplo de adição de tag (requer um ID de contato real)
    # tag_result = connector.add_tag_to_contact(123, "High_Value")
    # print(tag_result)
