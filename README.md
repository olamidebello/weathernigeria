# WeatherNigeria

A responsive Nigeria weather platform for **weathernigeria.africandroid.world**.

## Features

- Nigerian city and town search, geolocation, remembered location, Celsius/Fahrenheit.
- Current model conditions, feels-like temperature, humidity, wind and precipitation.
- Next 24 hours and seven-day forecast with precipitation probabilities.
- Interactive Leaflet/OpenStreetMap map with temperature, precipitation and wind markers for 11 cities. Markers open forecasts. This is a city conditions map, not radar or a continuous weather surface.
- Python standard-library gateway with fixed upstream hosts, input validation, timeouts and a bounded ten-minute cache. No API keys or database required.
- Accessible controls, responsive layout, explicit loading/failure states, safe DOM text rendering.
- Ansible installation, unprivileged systemd service, Nginx, Let's Encrypt TLS, automatic certificate renewal and CI validation.

## Run locally

Python 3.10+ and a modern browser required.

```sh
python3 server.py
```

Open http://127.0.0.1:8080. External connectivity is needed for Open-Meteo, Leaflet and map tiles. Location access requires HTTPS or localhost.

## Deploy to your server

Requires Debian 12 or Ubuntu 22.04/24.04, SSH key access with root/sudo, and Ansible on your control computer. The playbook installs the platform from this checkout; there is no compilation step.

1. Create an A record for `weathernigeria.africandroid.world` pointing to the server IPv4 address. Only create AAAA if IPv6 is configured. Allow inbound TCP 80/443. Keep backend port 8080 private.
2. Edit `deploy/inventory.ini` for your server and SSH user, or use the explicit inventory below.
3. Run from the repository root:

```sh
python3 -m pip install ansible-core
ansible-playbook -i 'YOUR_SERVER_IP,' -u root deploy/site.yml -e tls_email=YOUR_EMAIL
```

For HTTP-only staging add `-e '{"enable_tls": false}'`. For sudo access add `--become` and use your SSH account. Do not store credentials in the repository. The playbook preserves other Nginx sites and validates configuration before reload. Repeat the same command to deploy updates. Before update, retain the prior checkout for rollback; rerun its playbook to restore the application.

```sh
curl -f https://weathernigeria.africandroid.world/api/health
systemctl status weathernigeria
journalctl -u weathernigeria -n 50
certbot renew --dry-run
```

## Data and operating limits

Weather and geocoding use Open-Meteo, location names use GeoNames and map tiles use OpenStreetMap. Data attribution links are included in the application. Open-Meteo's free hosted endpoint is for noncommercial use under its current service terms; commercial deployments need a suitable subscription/endpoint or a self-hosted provider. Review https://open-meteo.com/en/pricing before commercial launch. Do not expose a commercial API key in browser code.

Conditions are model estimates, not guaranteed local observations or official emergency warnings. Check NiMet for official advisories. Geolocation uses a regional bounding box rather than a national boundary polygon. No user accounts, tracking or persistent server-side personal data are implemented. This is a small-deployment baseline; review provider quotas, caching and front-door rate limiting before high-volume public use.

## Verification

```sh
python3 -m unittest discover -s tests -v
node --check static/app.js
ansible-playbook -i deploy/inventory.ini deploy/site.yml --syntax-check
```

The CI workflow runs these checks on pushes and pull requests. Automated server deployment is invoked through Ansible, not through stored GitHub SSH secrets.
