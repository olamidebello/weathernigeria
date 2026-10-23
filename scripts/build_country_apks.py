"""Run in Android SDK/Gradle CI; publish only after every APK builds."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'dist';out.mkdir(exist_ok=True)
countries=json.loads((root/'africa/countries.json').read_text())+[{'slug':'africa','name':'AfricaWeather','domain':'africaweather.africandroid.world'}]
manifest=root/'mobile/app/src/main/AndroidManifest.xml';original=manifest.read_text();sums=[]
try:
 for c in countries:
  import re,html
  manifest.write_text(re.sub(r'android:label="[^"]*"','android:label="'+html.escape(c['name'],quote=True)+' Weather"',original))
  subprocess.run(['gradle','--no-daemon','clean','assembleDebug'],cwd=root/'mobile',env={**os.environ,'WEATHER_SLUG':c['slug'],'WEATHER_HOST':c['domain']},check=True)
  dest=out/f'weather-{c["slug"]}.apk';shutil.copyfile(root/'mobile/app/build/outputs/apk/debug/app-debug.apk',dest);sums.append(hashlib.sha256(dest.read_bytes()).hexdigest()+'  '+dest.name)
finally:manifest.write_text(original)
(out/'SHA256SUMS').write_text('\n'.join(sums)+'\n')
