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
2. Edit `deploy/inventory.ini` for your server and SSH user, and set `ansible_host=YOUR_SERVER_IP` if DNS is not ready.
3. Run from the repository root:

```sh
python3 -m pip install ansible-core
ansible-playbook -i deploy/inventory.ini deploy/site.yml -e tls_email=YOUR_EMAIL
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

## Automatic DNS provisioning (Cloudflare)

Use this only if **africandroid.world is authoritatively hosted on Cloudflare**. Hosting a website on the server does not itself grant control of public DNS. The default deployment remains `dns_provider=manual` for other DNS providers.

Create a Cloudflare API token scoped to `africandroid.world` with **Zone / DNS / Edit**. Obtain that zone's ID from Cloudflare. Supply credentials in the control machine's environment, never command-line arguments or Git. Run these commands in your server terminal:

```bash
cd /opt/weathernigeria-source
git pull --ff-only origin main
read -rp 'Cloudflare Zone ID: ' CLOUDFLARE_ZONE_ID
read -rsp 'Cloudflare API token: ' CLOUDFLARE_API_TOKEN; echo
export CLOUDFLARE_ZONE_ID CLOUDFLARE_API_TOKEN
ansible-playbook -i deploy/local.ini deploy/site.yml \
  -e dns_provider=cloudflare -e tls_email=dobcalldemo@gmail.com
unset CLOUDFLARE_API_TOKEN CLOUDFLARE_ZONE_ID
```

DNS-only invocation: `ansible-playbook -i deploy/local.ini deploy/dns.yml` with the same exported credentials. The integrated deployment creates/updates only the exact hostname A record, disables Cloudflare proxying for direct certificate validation, waits for Google and Cloudflare public resolvers, then requests HTTPS. Credentials are hidden from task output. Existing CNAME, NS, AAAA or multiple A records cause an explicit failure rather than deleting records. Change `dns_ipv4` if the server IP changes. Negative DNS caches may require waiting longer and rerunning. This cannot change registrar nameserver delegation or configure other DNS providers.

## Android app and automatic builds

The native Android WebView app loads the live HTTPS site. It needs internet; city search is supported, native geolocation is not yet implemented. This is a debug-signed development APK, not a store release.

Pushes to mobile source on main and manual runs of **Build Android app** provision Java 17, Gradle 8.9 and Android SDK 35, then invoke `ansible-playbook deploy/mobile.yml`. A verified APK and SHA-256 checksum are published to GitHub Releases. The website's Android app page discovers the latest successful release and only displays a download button when an APK exists. Redeploy the website with the existing site playbook to install that page.

To build locally, install Java 17, Gradle 8.9 and Android SDK platform 35/build-tools 35.0.0, set ANDROID_HOME, install ansible-core and run:

```sh
ansible-playbook deploy/mobile.yml
```

Outputs: dist/WeatherNigeria.apk and dist/WeatherNigeria.apk.sha256. GitHub-hosted builds do not preserve the debug signing key across runs; reinstall may be required. Use a securely managed persistent release signing key before public production distribution. No iOS binary is built.
