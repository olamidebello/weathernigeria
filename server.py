"""WeatherNigeria: bounded, cached weather gateway and static server."""
import json, os, time, threading
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import urlopen, Request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = Path(__file__).parent / 'static'
CACHE = {}
LOCK = threading.Lock()

def upstream(host, path, params):
    url = 'https://' + host + path + '?' + urlencode(params)
    with LOCK:
        item = CACHE.get(url)
        if item and item[0] > time.time():
            return item[1]
    with urlopen(Request(url, headers={'User-Agent': 'WeatherNigeria/1.0'}), timeout=15) as response:
        data = json.loads(response.read(2_000_000))
    with LOCK:
        if len(CACHE) >= 512:
            CACHE.clear()
        CACHE[url] = (time.time() + 600, data)
    return data

def coordinates(q):
    lat, lon = float(q.get('lat', [''])[0]), float(q.get('lon', [''])[0])
    if not (4 <= lat <= 14 and 2.5 <= lon <= 15):
        raise ValueError('Choose a location within Nigeria.')
    return lat, lon

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        super().end_headers()

    def reply(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if not parsed.path.startswith('/api/'):
            return super().do_GET()
        q = parse_qs(parsed.query)
        try:
            if parsed.path == '/api/health':
                return self.reply(200, {'status': 'ok'})
            if parsed.path == '/api/search':
                name = q.get('q', [''])[0].strip()
                if not 2 <= len(name) <= 80:
                    raise ValueError('Enter between 2 and 80 characters.')
                data = upstream('geocoding-api.open-meteo.com', '/v1/search', {'name': name, 'count': 20, 'language': 'en', 'countryCode': 'NG'})
                return self.reply(200, {'results': [r for r in data.get('results', []) if r.get('country_code') == 'NG']})
            if parsed.path == '/api/weather':
                lat, lon = coordinates(q)
                params = {'latitude': lat, 'longitude': lon, 'timezone': 'Africa/Lagos', 'forecast_days': 7,
                    'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m,wind_direction_10m',
                    'hourly': 'temperature_2m,precipitation_probability,weather_code',
                    'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset,uv_index_max'}
                return self.reply(200, upstream('api.open-meteo.com', '/v1/forecast', params))
            return self.reply(404, {'error': 'Unknown endpoint.'})
        except (ValueError, TypeError):
            self.reply(400, {'error': 'Invalid input. Select a Nigerian location.'})
        except Exception:
            self.reply(502, {'error': 'Weather provider unavailable. Please try again shortly.'})

if __name__ == '__main__':
    ThreadingHTTPServer((os.getenv('HOST', '127.0.0.1'), int(os.getenv('PORT', '8080'))), Handler).serve_forever()
