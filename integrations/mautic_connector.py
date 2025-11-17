import requests
import json
import os
from typing import Dict, Any, List

class MauticConnector:
    """
    Conector para a API REST do Mautic.
    Implementação base para OAuth 2.0 (recomendado).
    A autenticação Basic Auth é mantida como fallback/exemplo, mas o foco é OAuth.
    """
    
    def __init__(self, base_url: str, client_id: str = None, client_secret: str = None, access_token: str = None, username: str = None, password: str = None):
        """
        Inicializa o conector com as credenciais.
        
        :param base_url: URL base da sua instância Mautic (ex: https://seu_mautic.com/api)
        :param client_id: ID do cliente OAuth 2.0.
        :param client_secret: Segredo do cliente OAuth 2.0.
        :param access_token: Token de acesso OAuth 2.0 (se já obtido).
        :param username: Nome de usuário (para Basic Auth - fallback).
        :param password: Senha (para Basic Auth - fallback).
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        
        # Lógica de autenticação
        if access_token:
            self.headers["Authorization"] = f"Bearer {access_token}"
        elif username and password:
            # Fallback para Basic Auth
            self.session.auth = (username, password)
        elif client_id and client_secret:
            # Lógica para obter o token (Placeholder - requer mais detalhes da API Mautic)
            # Para o escopo atual, vamos focar em usar o access_token diretamente.
            print("Aviso: Autenticação OAuth 2.0 requer mais lógica para obter e renovar o token.")
        else:
            raise ValueError("Credenciais Mautic insuficientes. Forneça access_token ou username/password.")

    def _get_new_access_token(self):
        """
        Placeholder para a lógica de obtenção/renovação de token OAuth 2.0.
        """
        # Implementação real envolveria uma requisição POST para o endpoint /oauth/v2/token
        # com client_id, client_secret e grant_type.
        return "MOCK_NEW_ACCESS_TOKEN" # Retorno mock para manter a estrutura

    # ... (o restante da classe permanece o mesmo, usando self.session e self.headers)

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
            response_json = response.json()
            
            # O Mautic retorna o status HTTP correto, mas podemos ter erros de validação no corpo
            if response_json.get("errors"):
                error_message = response_json["errors"][0].get("message", "Erro de validação Mautic.")
                return {"success": False, "error": f"Erro de Validação Mautic: {error_message}", "status_code": response.status_code}
                
            return response_json

        except requests.exceptions.HTTPError as errh:
            # Erro de HTTP (ex: 401 Unauthorized, 500 Internal Server Error)
            try:
                # Tenta ler o erro detalhado do corpo, se disponível
                error_detail = response.json().get("errors", [{}])[0].get("message", response.text)
            except:
                error_detail = response.text
            return {"success": False, "error": f"Erro HTTP: {errh}. Detalhe: {error_detail}", "status_code": response.status_code}
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
        
        if not result.get("success", True): # Verifica se houve erro na requisição
            return result
            
        if result.get("contacts"):
            # O Mautic retorna um dicionário de contatos, onde a chave é o ID.
            contact_id = list(result["contacts"].keys())[0]
            return {"success": True, "result": result["contacts"][contact_id]}
        
        return {"success": False, "error": f"Nenhum contato encontrado com o email: {email}."}

    def list_contacts(self, limit: int = 100, start: int = 0) -> Dict[str, Any]:
        """
        Lista contatos com suporte a paginação.
        """
        endpoint = "contacts"
        params = {
            "limit": limit,
            "start": start
        }
        
        result = self._request("GET", endpoint, params=params)
        
        if not result.get("success", True):
            return result
            
        contacts = list(result.get("contacts", {}).values())
        
        return {
            "success": True,
            "result": contacts,
            "total": result.get("total"),
            "count": len(contacts)
        }

    def list_all_contacts(self) -> Dict[str, Any]:
        """
        Lista todos os contatos iterando sobre as páginas.
        """
        all_contacts = []
        start = 0
        limit = 100 # Limite padrão do Mautic
        
        while True:
            result = self.list_contacts(limit=limit, start=start)
            
            if not result.get("success"):
                return result
                
            current_page_contacts = result.get("result", [])
            all_contacts.extend(current_page_contacts)
            
            # Se o número de resultados for menor que o limite, é a última página
            if len(current_page_contacts) < limit:
                break
            
            start += limit
            
            # Limite de segurança para evitar loops infinitos
            if start > 10000:
                print("Aviso: Limite de 10000 registros atingido na paginação do Mautic.")
                break
                
        return {"success": True, "result": all_contacts, "total_retrieved": len(all_contacts)}

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
