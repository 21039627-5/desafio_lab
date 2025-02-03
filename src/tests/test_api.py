import unittest
import os
from src.api.app import app
from src.models.order import Order
from src.utils.database import get_db_connection

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.session = get_db_connection()  # Obtém a sessão do banco de dados
        self.session.query(Order).delete()  # Limpa os dados da tabela Order
        self.session.commit()

    def tearDown(self):
        self.session.query(Order).delete()  # Limpa os dados após cada teste
        self.session.commit()
        self.session.close()  # Fecha a sessão

    def test_health_check(self):
        """Teste do endpoint de health check."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "healthy"})

    def test_upload_file(self):
        """Teste do endpoint de upload com um arquivo válido."""
        print("Diretório atual:", os.getcwd())  # Verifique o diretório atual
        with open('tests/data_1.txt', 'rb') as file:
            response = self.app.post('/upload', data={'file': file})
            self.assertEqual(response.status_code, 200)
            self.assertIn("Arquivo processado com sucesso", response.json['message'])

    def test_upload_invalid_file(self):
        """Teste do endpoint de upload com um arquivo inválido."""
        with open('tests/invalid_file.jpg', 'rb') as file:
            response = self.app.post('/upload', data={'file': file})
            self.assertEqual(response.status_code, 400)
            self.assertIn("O arquivo deve ser do tipo .txt", response.json['error'])

    def test_get_orders(self):
        """Teste do endpoint de consulta de pedidos."""
        # Primeiro, vamos garantir que existem pedidos no banco de dados
        with open('tests/data_1.txt', 'rb') as file:
            self.app.post('/upload', data={'file': file})

        response = self.app.get('/orders')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)  # Verifica se a resposta é uma lista

if __name__ == '__main__':
    unittest.main()