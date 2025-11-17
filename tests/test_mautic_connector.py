import unittest
from unittest.mock import patch, Mock
import json
from ..integrations.mautic_connector import MauticConnector
import requests

# Dados mock para simular respostas da API
MOCK_CONTACT = {
    "id": 100,
    "points": 50,
    "tags": ["High_Value"],
    "fields": {
        "core": {
            "email": {"value": "maria@exemplo.com"},
            "firstname": {"value": "Maria"}
        }
    }
}

class TestMauticConnector(unittest.TestCase):
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.base_url = "https://test.mautic.com/api"
        self.access_token = "test_token"
        self.connector = MauticConnector(self.base_url, access_token=self.access_token)

    @patch('requests.Session.get')
    def test_get_contact_by_email_found(self, mock_get):
        """Testa a busca por email quando o contato é encontrado."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 1,
            "contacts": {
                "100": MOCK_CONTACT
            }
        }
        mock_get.return_value = mock_response
        
        result = self.connector.get_contact_by_email("maria@exemplo.com")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["id"], 100)

    @patch('requests.Session.get')
    def test_get_contact_by_email_not_found(self, mock_get):
        """Testa a busca por email quando o contato não é encontrado."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 0,
            "contacts": {}
        }
        mock_get.return_value = mock_response
        
        result = self.connector.get_contact_by_email("naoexiste@exemplo.com")
        
        self.assertFalse(result["success"])
        self.assertIn("Nenhum contato encontrado", result["error"])

    @patch('requests.Session.post')
    def test_add_tag_to_contact_success(self, mock_post):
        """Testa a adição de tag bem-sucedida."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "contact": MOCK_CONTACT
        }
        mock_post.return_value = mock_response
        
        result = self.connector.add_tag_to_contact(100, "New_Tag")
        
        self.assertTrue(result["success"])
        self.assertIn("contact", result)

    @patch('requests.Session.get')
    def test_list_contacts_pagination(self, mock_get):
        """Testa a lógica de paginação do list_all_contacts."""
        
        # Primeira página (100 resultados)
        mock_response_page1 = Mock()
        mock_response_page1.status_code = 200
        mock_response_page1.json.return_value = {
            "total": 150,
            "contacts": {str(i): MOCK_CONTACT for i in range(100)}
        }
        
        # Segunda página (50 resultados - última página)
        mock_response_page2 = Mock()
        mock_response_page2.status_code = 200
        mock_response_page2.json.return_value = {
            "total": 150,
            "contacts": {str(i): MOCK_CONTACT for i in range(100, 150)}
        }
        
        # Configura o mock para retornar as respostas em ordem
        mock_get.side_effect = [mock_response_page1, mock_response_page2]
        
        result = self.connector.list_all_contacts()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["total_retrieved"], 150)
        self.assertEqual(len(result["result"]), 150)
        
        # Verifica se o mock foi chamado duas vezes com os offsets corretos
        expected_calls = [
            unittest.mock.call(
                'https://test.mautic.com/api/contacts', 
                params={'limit': 100, 'start': 0}, 
                headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer test_token'}
            ),
            unittest.mock.call(
                'https://test.mautic.com/api/contacts', 
                params={'limit': 100, 'start': 100}, 
                headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer test_token'}
            )
        ]
        mock_get.assert_has_calls(expected_calls)

    @patch('requests.Session.get')
    def test_api_validation_error(self, mock_get):
        """Testa um erro de validação retornado pela API Mautic."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "errors": [
                {"message": "O campo 'email' é obrigatório.", "code": 400}
            ]
        }
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Client Error: Bad Request")
        mock_get.return_value = mock_response
        
        # Chamamos um método que faria uma requisição
        result = self.connector.list_contacts(limit=1, start=0)
        
        self.assertFalse(result["success"])
        self.assertIn("Erro de Validação Mautic", result["error"])
        self.assertIn("O campo 'email' é obrigatório", result["error"])

if __name__ == '__main__':
    unittest.main()
