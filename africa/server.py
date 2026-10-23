"""Host-selected African editions; no arbitrary upstream host or coordinate proxy."""
import importlib.util,json,os
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from http.server import ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gateway',ROOT/'server.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
COUNTRIES=json.loads((ROOT/'africa/countries.json').read_text());BY_SLUG={c['slug']:c for c in COUNTRIES};BY_HOST={c['domain']:c for c in COUNTRIES}
ASSETS=Path(os.getenv('WEATHER_ASSETS','/opt/africaweather/assets'))
def inside(lat,lon,c):
 # Regional bounding boxes accommodate simplified coastlines and island groups.
 g=c['geometry'];polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
 return any(min(p[0] for p in poly[0])-.3<=lon<=max(p[0] for p in poly[0])+.3 and min(p[1] for p in poly[0])-.3<=lat<=max(p[1] for p in poly[0])+.3 for poly in polys)
def forecast(lat,lon):
 return base.upstream('api.open-meteo.com','/v1/forecast',dict(latitude=lat,longitude=lon,timezone='auto',forecast_days=7,current='temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m',daily='temperature_2m_max,temperature_2m_min,precipitation_probability_max'))
class Handler(base.Handler):
 def __init__(self,*args,**kwargs):
  # Host is parsed by the HTTP handler before serving files.
  super().__init__(*args,**kwargs)
 def do_GET(self):
  host=self.headers.get('Host','').split(':')[0].lower();c=BY_HOST.get(host);hub=host=='africaweather.africandroid.world'
  if not c and not hub:return self.reply(404,{'error':'Unknown weather host'})
  self.directory=str(ASSETS/(c['slug'] if c else 'africa'))
  p=urlparse(self.path);q=parse_qs(p.query)
  try:
   if p.path=='/api/health':return self.reply(200,{'status':'ok'})
   if p.path=='/api/download':
    manifest=ROOT/'africa/downloads.json';downloads=json.loads(manifest.read_text()) if manifest.exists() else {};url=downloads.get(c['slug'] if c else 'africa');return self.reply(200,{'url':url if isinstance(url,str) and url.startswith('https://') else None})
   if p.path=='/api/overview' and hub:
    selected=BY_SLUG[q.get('country',[''])[0]];return self.reply(200,forecast(selected['lat'],selected['lon']))
   if p.path=='/api/search' and c:
    name=q.get('q',[''])[0].strip()
    if not 2<=len(name)<=80:raise ValueError()
    lang=c['language'] if c['language'] in ['en','fr','pt','ar','es','sw'] else 'en'
    d=base.upstream('geocoding-api.open-meteo.com','/v1/search',{'name':name,'count':20,'language':lang,'countryCode':c['code']});return self.reply(200,{'results':[v for v in d.get('results',[]) if v.get('country_code')==c['code']]})
   if p.path=='/api/weather' and c:
    lat=float(q['lat'][0]);lon=float(q['lon'][0])
    if not inside(lat,lon,c):raise ValueError()
    return self.reply(200,forecast(lat,lon))
   if p.path.startswith('/api/'):return self.reply(404,{'error':'Unknown endpoint'})
   return super(base.Handler,self).do_GET()
  except (ValueError,KeyError,TypeError):return self.reply(400,{'error':'Select a location within this edition’s region.'})
  except Exception:return self.reply(502,{'error':'Weather provider unavailable'})
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',int(os.getenv('PORT','18766'))),Handler).serve_forever()
