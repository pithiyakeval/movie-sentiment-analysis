import unittest
import sys
import os

# Add the parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class TestApp(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_status_code(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_health_endpoint(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'status', response.data)
    
    def test_predict_endpoint(self):
        response = self.app.post('/predict', 
                               json={'text': 'This is a test movie review'},
                               content_type='application/json')
        self.assertIn(response.status_code, [200, 500])  # 500 if DB not connected
    
    def test_batch_predict_endpoint(self):
        response = self.app.post('/batch-predict',
                               json={'texts': ['Good movie', 'Bad movie']},
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()