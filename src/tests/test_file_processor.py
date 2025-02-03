import unittest
from src.api.app import app
from src.models.order import Order
from src.utils.database import get_db_connection

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.session = get_db_connection()
        self.session.query(Order).delete()
        self.session.commit()

    def tearDown(self):
        self.session.query(Order).delete()
        self.session.commit()
        self.session.close()

    def test_upload_file(self):
        with open('tests/data_1.txt', 'rb') as file:
            response = self.app.post('/upload', data={'file': file})
            self.assertEqual(response.status_code, 200)
            self.assertIn("Arquivo processado com sucesso", response.json['message'])

    def test_upload_invalid_file(self):
        with open('tests/invalid_file.jpg', 'rb') as file:
            response = self.app.post('/upload', data={'file': file})
            self.assertEqual(response.status_code, 400)
            self.assertIn("O arquivo deve ser do tipo .txt", response.json['error'])

    def test_get_orders(self):
        response = self.app.get('/orders')
        self.assertEqual(response.status_code, 200)

    def test_get_orders_with_filter(self):
       
        with open('tests/data_1.txt', 'rb') as file:
            self.app.post('/upload', data={'file': file})
        
        response = self.app.get('/orders?order_id=273')  
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json), 0)  
    def test_get_orders_with_date_filter(self):
       
        with open('tests/data_1.txt', 'rb') as file:
            self.app.post('/upload', data={'file': file})

        response = self.app.get('/orders?start_date=2021-01-01&end_date=2021-12-31')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json), 0)  

if __name__ == '__main__':
    unittest.main()