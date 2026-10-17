import sys, unittest, threading, json
from pathlib import Path
from unittest.mock import patch
from urllib.request import urlopen
from urllib.error import HTTPError
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server

class GatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.base = 'http://127.0.0.1:' + str(cls.http.server_port)
        threading.Thread(target=cls.http.serve_forever, daemon=True).start()
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
    def get(self, path):
        with urlopen(self.base + path) as r:
            return json.load(r)
    def test_health(self):
        self.assertEqual(self.get('/api/health'), {'status': 'ok'})
    def test_outside_region_and_nan_rejected(self):
        for lat,lon in [('50','3'),('nan','3'),('6','180')]:
            with self.assertRaises(HTTPError) as e:
                self.get('/api/weather?lat='+lat+'&lon='+lon)
            self.assertEqual(e.exception.code,400)
    @patch('server.upstream')
    def test_search_filters_other_countries(self, upstream):
        upstream.return_value={'results':[{'name':'Lagos','country_code':'NG'},{'name':'Lagos','country_code':'PT'}]}
        self.assertEqual(len(self.get('/api/search?q=Lagos')['results']),1)
    @patch('server.upstream',side_effect=TimeoutError)
    def test_provider_failure_is_json(self, upstream):
        with self.assertRaises(HTTPError) as e:
            self.get('/api/weather?lat=6.5&lon=3.4')
        self.assertEqual(e.exception.code,502)
        self.assertIn('error',json.load(e.exception))
    @patch('server.upstream')
    def test_forecast_contract(self, upstream):
        upstream.return_value={'current':{},'hourly':{},'daily':{}}
        self.get('/api/weather?lat=6.5&lon=3.4')
        args=upstream.call_args.args
        self.assertEqual(args[2]['forecast_days'],7)
        self.assertEqual(args[2]['timezone'],'Africa/Lagos')
if __name__=='__main__': unittest.main()
