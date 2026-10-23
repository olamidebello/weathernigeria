# WeatherNigeria on 154.16.170.86

On the new Debian 12 server, run as root:

```bash
apt-get update
apt-get install -y git ansible-core
ansible-pull -U https://github.com/olamidebello/weathernigeria.git -C main -d /opt/weathernigeria-bootstrap -i localhost, -c local deploy/pull-and-deploy.yml
```

This installs HTTP hosting, a backend on loopback port 18765, and a 15-minute pull/test/deploy timer. The first installation also deploys immediately. Local repository edits cause fast-forward updates to fail rather than being discarded. Deployment settings persist in /etc/weathernigeria/deploy.json. Other hosted sites are retained.

For remote deployment from a checkout, with SSH access already configured:

```bash
ansible-playbook -i deploy/new-server.ini deploy/pull-and-deploy.yml
```

Set the Namecheap A record for weathernigeria.africandroid.world to 154.16.170.86 and remove any stale AAAA record. Allow incoming TCP 80 and 443. DNS is not changed by this playbook.

After DNS resolves to the new server, enable HTTPS and persist it for automatic updates:

```bash
ansible-playbook -i localhost, -c local /opt/weathernigeria-source/deploy/pull-and-deploy.yml -e weather_enable_tls=true
```

Check local HTTP before DNS cutover:

```bash
curl --fail -H 'Host: weathernigeria.africandroid.world' http://127.0.0.1/api/health
systemctl status weathernigeria weathernigeria-deploy.timer
journalctl -u weathernigeria-deploy.service -n 80 --no-pager
```

No existing server data or APK downloads are migrated. This deploys tracked application assets only.
