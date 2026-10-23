# AfricaWeather deployment

55 requested country/territory editions plus africaweather.africandroid.world.
The source is olamidebello/weathernigeria; the supplied africandriod.com hostname is not used.

Run on the Olamidepanel Debian server as root:

```bash
apt-get update
apt-get install -y git ansible-core
ansible-pull -U https://github.com/olamidebello/weathernigeria.git -C main -d /opt/africaweather-bootstrap -i localhost, -c local deploy/africaweather.yml
```

The gateway uses loopback port 18766. Nigeria is replaced by the country edition;
its old deployment timer is disabled to prevent competing Nginx configurations.
Other Olamidepanel sites are retained. Re-deployment runs every 30 minutes.
This creates Nginx hosting on the panel server; it does not register entries in the
panel database because no stable panel API is provided in this repository.

DNS: point each requested host to 154.16.170.86, or configure a wildcard record
only where it will not interfere with other subdomains. Remove stale AAAA records.
DNS credentials and existing mail records are not modified.

HTTPS: obtain a wildcard certificate using the DNS provider, then run:

```bash
ansible-playbook -i localhost, -c local /opt/africaweather-source/deploy/africaweather.yml -e africa_enable_tls=true -e africa_tls_cert=/etc/letsencrypt/live/africandroid.world/fullchain.pem -e africa_tls_key=/etc/letsencrypt/live/africandroid.world/privkey.pem
```

All 56 hostnames are checked against the certificate before HTTPS configuration.
HTTP is the default staging mode; directory links target the final HTTPS URLs.

Mobile: run the GitHub Actions workflow **Build all African weather Android downloads**.
It builds 56 debug APKs with separate application IDs, labels and domain URLs, uploads
a release, then commits africa/downloads.json. The next automatic deployment shows
the real APK links. Until then, pages show download availability honestly. Production
signing/Play Store publication is not configured. Native WebView geolocation is not
implemented; users can search a city. No APK was built merely by generating web assets.

Languages: one configurable editorial default per edition, with 12 selectable
languages. Core forecast headings and search controls are localized; slogans,
legal documents, explanatory text and some status messages currently remain English.
These are not claims that any country has only one language. Edit countries.json
for a different default. Local-language copy needs native-speaker review.

Forecast locations are restricted to each edition's approximate regional bounds;
simplified bounding boxes can include neighbouring areas near borders. Search
results are filtered by country code. Natural Earth 110m boundaries and Mapsicon
island silhouettes are illustrative. Western Sahara is a requested separate edition;
no sovereignty determination is implied. Country card weather is for the named
reference city, not a national average. Maps and provider attribution appear on pages.

The privacy/terms pages describe this version of the app. Review host logging and
retention configuration before making privacy promises beyond the published text.

Check:
```bash
curl -H 'Host: africaweather.africandroid.world' http://127.0.0.1:18766/api/health
systemctl status africaweather africaweather-deploy.timer
journalctl -u africaweather -n 50 --no-pager
```
