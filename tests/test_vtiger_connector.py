import unittest
from unittest.mock import patch, Mock
import json
from ..integrations.vtiger_connector import VtigerConnector

# Dados mock para simular respostas da API
MOCK_CONTACT = {
    "id": "20x12345",
    "firstname": "Joao",
    "lastname": "Silva",
    "email": "joao@exemplo.com",
    "phone": "5511987654321",
    "cf_lead_score": 85,
    "leadstatus": "Active Client",
    "modifiedtime": "2025-11-10"
}

class TestVtigerConnector(unittest.TestCase):
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.base_url = "https://test.vtiger.com/restapi/v1/vtiger/default"
        self.username = "test_user"
        self.access_key = "test_key"
        self.connector = VtigerConnector(self.base_url, self.username, self.access_key)

    @patch('requests.Session.get')
    def test_query_success(self, mock_get):
        """Testa uma consulta VQL bem-sucedida."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": [MOCK_CONTACT]
        }
        mock_get.return_value = mock_response
        
        result = self.connector.query("SELECT * FROM Contacts LIMIT 1;")
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["result"]), 1)
        self.assertEqual(result["result"][0]["id"], "20x12345")

    @patch('requests.Session.get')
    def test_query_vtiger_api_error(self, mock_get):
        """Testa um erro retornado pela API Vtiger (success: false)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "error": {
                "code": "INVALID_QUERY",
                "message": "Sintaxe VQL inválida."
            }
        }
        mock_get.return_value = mock_response
        
        result = self.connector.query("SELECT * FROM InvalidModule;")
        
        self.assertFalse(result["success"])
        self.assertIn("INVALID_QUERY", result["error"])
        self.assertIn("Sintaxe VQL inválida", result["error"])

    @patch('requests.Session.get')
    def test_query_http_error(self, mock_get):
        """Testa um erro HTTP (ex: 401 Unauthorized)."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Client Error: Unauthorized")
        mock_response.text = "Unauthorized Access"
        
        mock_get.return_value = mock_response
        
        result = self.connector.query("SELECT * FROM Contacts;")
        
        self.assertFalse(result["success"])
        self.assertIn("Erro HTTP: 401 Client Error: Unauthorized", result["error"])
        self.assertIn("Unauthorized Access", result["error"])

    @patch('requests.Session.get')
    def test_retrieve_by_email_found(self, mock_get):
        """Testa a busca por email quando o contato é encontrado."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": [MOCK_CONTACT]
        }
        mock_get.return_value = mock_response
        
        result = self.connector.retrieve_by_email("joao@exemplo.com")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["email"], "joao@exemplo.com")

    @patch('requests.Session.get')
    def test_retrieve_by_email_not_found(self, mock_get):
        """Testa a busca por email quando o contato não é encontrado."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": []
        }
        mock_get.return_value = mock_response
        
        result = self.connector.retrieve_by_email("naoexiste@exemplo.com")
        
        self.assertFalse(result["success"])
        self.assertIn("Nenhum registro de Contacts encontrado", result["error"])

    @patch('requests.Session.get')
    def test_query_all_pagination(self, mock_get):
        """Testa a lógica de paginação do query_all."""
        
        # Primeira página (100 resultados)
        mock_response_page1 = Mock()
        mock_response_page1.status_code = 200
        mock_response_page1.json.return_value = {
            "success": True,
            "result": [MOCK_CONTACT] * 100
        }
        
        # Segunda página (50 resultados - última página)
        mock_response_page2 = Mock()
        mock_response_page2.status_code = 200
        mock_response_page2.json.return_value = {
            "success": True,
            "result": [MOCK_CONTACT] * 50
        }
        
        # Configura o mock para retornar as respostas em ordem
        mock_get.side_effect = [mock_response_page1, mock_response_page2]
        
        result = self.connector.query_all("SELECT * FROM Contacts;")
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["result"]), 150)
        
        # Verifica se o mock foi chamado duas vezes com os offsets corretos
        expected_calls = [
            unittest.mock.call(
                'https://test.vtiger.com/restapi/v1/vtiger/default/query', 
                params={'query': 'SELECT * FROM Contacts LIMIT 0, 100;'}, 
                headers={'Content-Type': 'application/json'}
            ),
            unittest.mock.call(
                'https://test.vtiger.com/restapi/v1/vtiger/default/query', 
                params={'query': 'SELECT * FROM Contacts LIMIT 100, 100;'}, 
                headers={'Content-Type': 'application/json'}
            )
        ]
        mock_get.assert_has_calls(expected_calls)

if __name__ == '__main__':
    unittest.main()
