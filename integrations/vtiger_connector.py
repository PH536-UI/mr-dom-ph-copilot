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

            # O Vtiger sempre retorna 200 OK, mesmo em caso de erro de API,
            # mas o JSON de resposta terá "success": false.
            # Se o status HTTP não for 200, tratamos como erro de conexão/servidor.
            response.raise_for_status() 
            
            response_json = response.json()
            
            if not response_json.get("success"):
                # Erro de API Vtiger (ex: sintaxe VQL incorreta, módulo inexistente)
                error_info = response_json.get("error", {})
                error_message = error_info.get("message", "Erro desconhecido da API Vtiger.")
                error_code = error_info.get("code", "VTIGER_UNKNOWN_ERROR")
                return {"success": False, "error": f"Erro da API Vtiger ({error_code}): {error_message}", "status_code": response.status_code}
            
            return response_json

        except requests.exceptions.HTTPError as errh:
            # Erro de HTTP (ex: 401 Unauthorized, 500 Internal Server Error)
            try:
                # Tenta ler o erro detalhado do corpo, se disponível
                error_detail = response.json().get("error", {}).get("message", response.text)
            except:
                error_detail = response.text
            return {"success": False, "error": f"Erro HTTP: {errh}. Detalhe: {error_detail}", "status_code": response.status_code}
        except requests.exceptions.ConnectionError as errc:
            return {"success": False, "error": f"Erro de Conexão: {errc}"}
        except requests.exceptions.Timeout as errt:
            return {"success": False, "error": f"Timeout: {errt}"}
        except requests.exceptions.RequestException as err:
            return {"success": False, "error": f"Erro na Requisição: {err}"}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def query(self, query_string: str, page_size: int = 100) -> Dict[str, Any]:
        """
        Executa uma consulta VQL (Vtiger Query Language).
        A API Vtiger limita o resultado a 100 registros por padrão.
        Este método retorna apenas a primeira página. Para todas as páginas, use query_all.
        """
        # A API Vtiger usa LIMIT e OFFSET dentro da string VQL.
        # Não há parâmetros de paginação separados na requisição GET.
        # A string VQL deve incluir LIMIT e OFFSET para paginação manual.
        
        # Para simplificar o uso pelo Agente, vamos assumir que a string VQL
        # já contém o LIMIT e OFFSET, ou que o Agente só precisa da primeira página.
        # Se o Agente precisar de mais, ele deve usar o método query_all.
        
        return self._request("GET", "query", {"query": query_string})

    def query_all(self, base_query: str) -> Dict[str, Any]:
        """
        Executa uma consulta VQL e itera automaticamente para buscar todos os resultados.
        A base_query deve ser a consulta VQL SEM as cláusulas LIMIT e OFFSET.
        """
        all_results = []
        offset = 0
        page_size = 100 # Limite máximo por página na API Vtiger
        
        while True:
            # Adiciona LIMIT e OFFSET à consulta base
            paginated_query = f"{base_query.rstrip(';')} LIMIT {offset}, {page_size};"
            
            print(f"Executando VQL paginada: {paginated_query}")
            
            result = self._request("GET", "query", {"query": paginated_query})
            
            if not result.get("success"):
                # Retorna o erro se a consulta falhar
                return result
            
            current_page_results = result.get("result", [])
            all_results.extend(current_page_results)
            
            # Se o número de resultados for menor que o tamanho da página, é a última página
            if len(current_page_results) < page_size:
                break
            
            offset += page_size
            
            # Limite de segurança para evitar loops infinitos em caso de erro de lógica
            if offset > 10000: # Limite de 10000 registros para evitar sobrecarga
                print("Aviso: Limite de 10000 registros atingido na paginação do Vtiger.")
                break
                
        return {"success": True, "result": all_results}

    def retrieve_by_email(self, email: str, module: str = "Contacts") -> Dict[str, Any]:
        """
        Busca um registro pelo email.
        """
        # Usamos query_all para garantir que, se houver mais de um, todos sejam retornados,
        # mas a VQL já deve ser otimizada para buscar apenas 1.
        # A VQL com LIMIT 1 é a forma mais eficiente.
        query_string = f"SELECT * FROM {module} WHERE email = '{email}' LIMIT 1;"
        result = self.query(query_string)
        
        if not result.get("success"):
            # Propaga o erro detalhado da API
            return {"success": False, "error": result.get("error", "Erro desconhecido na consulta.")}
            
        if result.get("result"):
            # Encontrou o contato
            return {"success": True, "result": result["result"][0]}
        
        # Não encontrou o contato
        return {"success": False, "error": f"Nenhum registro de {module} encontrado com o email: {email}."}

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
