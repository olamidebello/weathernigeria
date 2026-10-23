import importlib.util,json,threading,unittest,tempfile,sys
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('africa_server',ROOT/'africa/server.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sys.path.insert(0,str(ROOT/'scripts'));from build_africa import build
class AfricaTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();build(cls.tmp.name);m.ASSETS=Path(cls.tmp.name);cls.server=ThreadingHTTPServer(('127.0.0.1',0),m.Handler);threading.Thread(target=cls.server.serve_forever,daemon=True).start()
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.tmp.cleanup()
 def get(self,path,host):
  return urlopen(Request('http://127.0.0.1:'+str(self.server.server_port)+path,headers={'Host':host}))
 def test_all_editions(self):
  self.assertEqual(len(m.COUNTRIES),55)
  for c in m.COUNTRIES:
   for path in ['/','/logo.svg','/terms.html','/privacy.html','/copyright.html','/api/health']:
    with self.get(path,c['domain']) as r:self.assertEqual(r.status,200)
 def test_country_search_filters(self):
  with patch.object(m.base,'upstream',return_value={'results':[{'name':'Nairobi','country_code':'KE'},{'name':'Lagos','country_code':'NG'}]}) as upstream:
   with self.get('/api/search?q=Nairobi','weatherkenya.africandroid.world') as r:self.assertEqual(json.load(r)['results'][0]['name'],'Nairobi')
   self.assertEqual(upstream.call_args.args[2]['countryCode'],'KE')
 def test_invalid_host_and_region(self):
  for path,host,status in [('/','evil.example',404),('/api/weather?lat=50&lon=0','weathernigeria.africandroid.world',400),('/api/weather?lat=nan&lon=0','weatherkenya.africandroid.world',400)]:
   with self.assertRaises(HTTPError) as e:self.get(path,host)
   self.assertEqual(e.exception.code,status)
 def test_hub(self):
  with self.get('/countries.json','africaweather.africandroid.world') as r:self.assertEqual(len(json.load(r)),55)
  for c in m.COUNTRIES:self.assertTrue((m.ASSETS/'africa/maps'/(c['code'].lower()+'.svg')).exists())
if __name__=='__main__':unittest.main()
