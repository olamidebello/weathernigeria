"""Build isolated country assets and the AfricaWeather directory."""
import json, html, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COUNTRIES=json.loads((ROOT/'africa/countries.json').read_text())
def rings(g):
 return [r for p in (g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]) for r in p]
def svg(geometries):
 rs=[r for g in geometries for r in rings(g)]; pts=[p for r in rs for p in r];xs=[p[0] for p in pts];ys=[p[1] for p in pts];x,y=min(xs),max(ys);scale=96/max(max(xs)-x,y-min(ys)); paths=['M'+' L'.join(f'{(p[0]-x)*scale+2:.2f},{(y-p[1])*scale+2:.2f}' for p in r)+' Z' for r in rs]
 return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path fill="#168466" fill-rule="evenodd" d="'+' '.join(paths)+'"/></svg>'
def build(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 for c in COUNTRIES+[dict(slug='africa',name='Africa',language='en',slogan='One continent. Every sky. Weather for the way we live.',city='Africa',lat=0,lon=20)]:
  target=out/c['slug'];target.mkdir(exist_ok=True); shutil.copytree(ROOT/'africa/web',target,dirs_exist_ok=True)
  (target/'config.json').write_text(json.dumps({k:v for k,v in c.items() if k!='geometry'},ensure_ascii=False))
  icon=ROOT/'africa/maps'/f"{c.get('code','').lower()}.svg"
  (target/'logo.svg').write_text(icon.read_text() if icon.exists() else svg([c['geometry']] if c['slug']!='africa' else [v['geometry'] for v in COUNTRIES if v['code'] not in ['KM','CV','MU','SC','ST']]))
  for page,title,text in [
   ('terms','Terms and Conditions','This service provides model based forecasts for general planning. Forecasts can change and are not official emergency warnings. Follow your national meteorological service and local authorities. Do not misuse the service, attempt unauthorized access, or overload its infrastructure. Third party services have separate terms. No accuracy or uninterrupted availability is guaranteed. Mandatory consumer rights remain applicable.'),
   ('privacy','Privacy Policy','The operator is Olamide Olatayo Bello. This site sends searched place names and forecast coordinates to Open-Meteo and its geocoding service. Location access requires your permission. Your selected language is stored in your browser. Server access logs may include IP addresses, request paths, and timestamps for operations and security; retention follows the hosting configuration. Map tiles and map libraries are loaded from OpenStreetMap and unpkg, which receive connection information. No account or payment is required by this weather edition. You can clear browser storage and revoke location permission in browser settings.'),
   ('copyright','Copyright and Credits','© 2026 Olamide Olatayo Bello. Original application content reserved. Weather: Open-Meteo, CC BY 4.0; place data: GeoNames. Maps: OpenStreetMap contributors, ODbL. Country silhouettes: Natural Earth, public domain; island icons: Mapsicon by Djaiss, used with attribution, not for separate resale. Simplified boundaries are illustrative, do not establish sovereignty, and may omit small islands. Western Sahara is shown as a separate requested edition without a position on its disputed status.')]:
   (target/(page+'.html')).write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><link rel="stylesheet" href="/style.css"><main><a href="/">← '+html.escape(c['name'])+'</a><h1>'+title+'</h1><p>'+text+'</p><p>Updated 23 October 2026.</p></main></html>')
 maps=out/'africa/maps';maps.mkdir(exist_ok=True)
 for c in COUNTRIES:shutil.copyfile(out/c['slug']/'logo.svg',maps/(c['code'].lower()+'.svg'))
 (out/'africa/countries.json').write_text(json.dumps([{k:v for k,v in c.items() if k!='geometry'} for c in COUNTRIES],ensure_ascii=False))
if __name__=='__main__':build(sys.argv[1])
