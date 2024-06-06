import unittest
import pandas as pd
from datetime import datetime
from app import app
import os

script_dir = os.path.dirname(__file__)
csv_path = os.path.join(script_dir, 'person_finance.csv')

class TestFinanceDash(unittest.TestCase):

    def setUp(self):
        self.app = app.server
        self.client = self.app.test_client()

    def test_date_format(self):
        date_str = '2023-01-03'
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        self.assertEqual(date_obj.strftime('%Y-%m-%d'), date_str)

    def test_add_entry(self):
        with self.client:
            self.client.post('/_dash-update-component', json={
                'output' :'income-expense-graph.figure',
                'inputs' :[
                    {'id': 'submit-button', 'property': 'n_clicks', 'value':1},
                    {'id': 'date-input', 'property': 'date', 'value': '2023-09-09'},
                    {'id': 'income-input', 'property': 'value', 'value': 5000},
                    {'id': 'expenses-input', 'property': 'value', 'value': 3000}
                    ]   
            })
            df = pd.read_csv(csv_path)
            last_entry = df.iloc[-1]
            self.assertEqual(last_entry['Date'], '2023-09-09')
            self.assertEqual(last_entry['Income'], 5000)
            self.assertEqual(last_entry['Expenses'], 3000)

    def test_remove_entry(self):
        with self.client:
            self.client.post('/_dash-update-component', json={
                'output': 'income-expense-graph.figure',
                'inputs': [
                        {'id':'remove-button', 'property': 'n_clicks', 'value':1},
                        {'id': 'date-input', 'property': 'date', 'value': '2023-09-09'}
                        ]
            })

            df = pd.read_csv(csv_path)
            self.assertNotIn('2023-09-09', df['Date'].values)
if __name__=='__main__':
    unittest.main()