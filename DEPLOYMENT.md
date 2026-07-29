# Coderr Deployment Runbook

Betriebsdokumentation für das Deployment des Coderr-Backends auf einem
eigenen VPS. Stand: 29.07.2026

---

## 1. Überblick

### Architektur

```
                              Internet
                                 |
                          Port 443 (HTTPS)
                                 |
                         ┌───────────────┐
                         │     Nginx     │  TLS-Terminierung
                         └───────┬───────┘
                                 │
              ┌──────────────────┴──────────────────┐
              │                                     │
      benjaminblarr.de                   coderr.benjaminblarr.de
   (sites-available/benjaminblarr)        (sites-available/coderr)
              │                                     │
     ┌────────┼────────┐              ┌─────────────┼─────────────┐
     │        │        │              │             │             │
     /    /join/ u.a.  /api/contact   /          /api/       /static/
     │        │        │              │        /admin/       /media/
 Portfolio  statische  │          Coderr-       │             │
 (Angular)  Projekte   │          Frontend   Unix-Socket   Dateien
                       │          (statisch) /run/gunicorn/ direkt von
                       └──────────┬──────────┘ coderr.sock   der Platte
                                  │              │
                                  └──────┬───────┘
                                         │
                                  ┌──────────────┐
                                  │   Gunicorn   │  3 Worker
                                  │   (Django)   │
                                  └──────┬───────┘
                                         │
                                  ┌──────────────┐
                                  │  PostgreSQL  │  nur localhost
                                  └──────────────┘
```

Beide Server-Blöcke sprechen denselben Gunicorn-Socket an. Die
Hauptdomain nutzt davon nur `/api/contact/` für das Kontaktformular des
Portfolios, die Subdomain die komplette Coderr-Anwendung.

### Komponenten

| Baustein     | Version / Details                      |
|--------------|----------------------------------------|
| Server       | Hostinger VPS KVM 2, 2 vCPU, 8 GB RAM  |
| Betriebssystem | Ubuntu 24.04 LTS (noble)             |
| Webserver    | Nginx 1.24 (Ubuntu-Paket)              |
| App-Server   | Gunicorn 26.0.0, 3 Worker, Unix-Socket |
| Framework    | Django 6.0.6, DRF 3.17.1               |
| Datenbank    | PostgreSQL 16                          |
| Python       | 3.12.3                                 |
| TLS          | Let's Encrypt via certbot, Auto-Renewal|

### URLs

| Adresse                                                     | Inhalt                       |
|-------------------------------------------------------------|------------------------------|
| `https://benjaminblarr.de/`                                 | Portfolio (Angular)          |
| `https://benjaminblarr.de/api/contact/`                     | Kontaktformular des Portfolios |
| `https://benjaminblarr.de/join/`                            | Join (Angular, Hash-Routing) |
| `https://benjaminblarr.de/pokedex/`                         | Pokédex (statisch)           |
| `https://benjaminblarr.de/el-pollo-loco/`                   | El Pollo Loco (statisch)     |
| `https://coderr.benjaminblarr.de/`                          | Coderr-Frontend              |
| `https://coderr.benjaminblarr.de/api/`                      | REST-API                     |
| `https://coderr.benjaminblarr.de/api/schema/swagger-ui/`    | API-Dokumentation            |
| `https://coderr.benjaminblarr.de/admin/`                    | Django-Admin                 |

Coderr lief bis zum 29.07.2026 unter dem Unterpfad
`benjaminblarr.de/coderr/`. Diese Adressen bleiben gültig und leiten mit
`301` auf die Subdomain um, der Pfad dahinter bleibt dabei erhalten.
Warum umgestellt wurde, steht in Abschnitt 7.

### Verzeichnisse auf dem Server

```
/var/www/
├── portfolio/                       Angular-Build (statisch)
└── coderr/
    ├── backend/                     Django-Repo
    │   ├── .venv/                   virtuelle Python-Umgebung
    │   ├── .env                     Secrets, Rechte 600, NICHT im Repo
    │   ├── staticfiles/             Ergebnis von collectstatic
    │   └── media/                   Uploads der Nutzer
    └── frontend/                    Klon des Akademie-Repos

/etc/nginx/sites-available/benjaminblarr        Portfolio und Projekte
/etc/nginx/sites-available/coderr               Subdomain coderr.*
/etc/nginx/sites-available/benjaminblarr-dev    Weiterleitung alte Domain
/etc/nginx/snippets/projekte.conf               Projekt-Blöcke, eingebunden
/etc/systemd/system/gunicorn-coderr.service     Dienstdefinition
/etc/ssh/sshd_config.d/00-hardening.conf        SSH-Absicherung
/usr/local/bin/backup-coderr.sh                 tägliche Sicherung
/swapfile                                        2 GB Swap
```

---

## 2. Zugang

```bash
ssh vps
```

Voraussetzung ist der Eintrag in `~/.ssh/config` auf dem Arbeitsrechner:

```
Host vps
    HostName <SERVER-IP>
    User benni
    ServerAliveInterval 60
    ServerAliveCountMax 10
```

Anmeldung ausschließlich per SSH-Schlüssel. Passwort-Anmeldung und
Root-Anmeldung sind abgeschaltet.

**Notzugang**, falls SSH nicht mehr erreichbar ist: Browser-Terminal im
Hostinger hPanel unter dem VPS-Eintrag.

---

## 3. Erstinstallation

Die Schritte in dieser Reihenfolge reproduzieren den aktuellen Zustand
auf einem frischen Ubuntu-24.04-Server.

### 3.1 System aktualisieren

```bash
apt update && apt upgrade -y
```

Bei Rückfragen zu geänderten Konfigurationsdateien immer
**"keep the local version currently installed"** wählen. Die
Maintainer-Version der `sshd_config` kann den Root-Zugang sperren,
bevor ein eigener Schlüssel hinterlegt ist.

Danach neu starten, wenn `*** System restart required ***` erscheint.

### 3.2 Arbeitsnutzer anlegen

```bash
adduser benni
usermod -aG sudo benni
```

Das `-a` bei `usermod -G` ist zwingend, sonst werden alle bestehenden
Nebengruppen des Nutzers ersetzt.

### 3.3 SSH-Schlüssel hinterlegen

```bash
mkdir -p /home/benni/.ssh
nano /home/benni/.ssh/authorized_keys      # öffentlichen Schlüssel einfügen
chown -R benni:benni /home/benni/.ssh
chmod 700 /home/benni/.ssh
chmod 600 /home/benni/.ssh/authorized_keys
```

Die Rechte sind nicht optional. Bei zu weiten Rechten ignoriert der
SSH-Server die Datei ohne Fehlermeldung und fragt nach einem Passwort.

**Vor dem nächsten Schritt in einem zweiten Terminal prüfen, dass die
Anmeldung als `benni` per Schlüssel funktioniert.**

### 3.4 SSH absichern

```bash
sudo tee /etc/ssh/sshd_config.d/00-hardening.conf > /dev/null <<'EOF'
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
EOF

sudo chmod 644 /etc/ssh/sshd_config.d/00-hardening.conf
sudo sshd -t                      # keine Ausgabe = Syntax in Ordnung
sudo sshd -T | grep -Ei "permitrootlogin|passwordauthentication"
sudo systemctl reload ssh
```

**Wichtig:** Bei OpenSSH gewinnt der **erste** gefundene Wert, nicht der
letzte. Ubuntu lädt `/etc/ssh/sshd_config.d/*.conf` am Anfang der
Hauptkonfiguration und alphabetisch. Die von `cloud-init` erzeugte
`50-cloud-init.conf` setzt `PasswordAuthentication yes`. Nur eine Datei
mit kleinerer Nummer, hier `00-hardening.conf`, überschreibt das.
Die 50er Datei selbst nicht bearbeiten, `cloud-init` kann sie beim
Serverstart neu schreiben.

`sudo sshd -T` zeigt die tatsächlich wirksamen Werte nach Auswertung
aller Includes. Das ist die einzige verlässliche Quelle.

### 3.5 Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

**Immer erst die Regeln setzen, dann aktivieren.** `ufw enable` ohne
freigegebenen Port 22 trennt die laufende Verbindung.

PostgreSQL wird absichtlich nicht freigegeben. Django spricht über
`localhost` mit der Datenbank, dieser Verkehr verlässt den Server nie.

### 3.6 Swap

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-swappiness.conf
sudo sysctl --system > /dev/null
```

Das `-a` bei `tee` ist entscheidend. Ohne `-a` wird `/etc/fstab`
überschrieben und der Server startet nicht mehr korrekt.

Swap dient hier nicht als Speichererweiterung, sondern verhindert, dass
der Kernel bei einer Speicherspitze den größten Prozess beendet, also
üblicherweise die Datenbank oder Gunicorn.

### 3.7 Pakete

```bash
sudo apt install -y nginx postgresql postgresql-contrib python3-venv \
  python3-dev libpq-dev git certbot python3-certbot-nginx fail2ban
```

### 3.8 Datenbank

```bash
sudo -u postgres psql
```

```sql
CREATE USER coderr WITH PASSWORD '<DB-PASSWORT>';
CREATE DATABASE coderr OWNER coderr;
ALTER ROLE coderr SET client_encoding TO 'utf8';
ALTER ROLE coderr SET default_transaction_isolation TO 'read committed';
ALTER ROLE coderr SET timezone TO 'UTC';
ALTER USER coderr CREATEDB;
\c coderr
GRANT ALL ON SCHEMA public TO coderr;
\q
```

`GRANT ALL ON SCHEMA public` ist ab PostgreSQL 15 nötig. Ohne diese
Zeile scheitert `manage.py migrate` an
`permission denied for schema public`. Der Fehler klingt so, als wäre
der Nutzer falsch angelegt, es fehlt aber nur dieses Recht.

`CREATEDB` braucht Django, um für Tests eine temporäre Datenbank
anzulegen.

Passwörter erzeugen:

```bash
openssl rand -hex 24                                       # DB-Passwort
python3 -c 'import secrets; print(secrets.token_urlsafe(64))'   # SECRET_KEY
```

Hex statt Sonderzeichen, weil Sonderzeichen in Konfigurationsdateien und
beim Escapen in SQL wiederholt Probleme machen. Die Länge gleicht das aus.

### 3.9 Anwendung einrichten

```bash
sudo mkdir -p /var/www/coderr
sudo chown -R benni:benni /var/www/coderr

cd /var/www/coderr
git clone https://github.com/B-Blarr/Coderr-Backend.git backend
cd backend

python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

Dann `.env` anlegen (siehe Abschnitt 4.1) und:

```bash
chmod 600 .env
.venv/bin/python manage.py check
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py seed_demo
```

`collectstatic` ist nicht optional. Bei `DEBUG=False` liefert Django
keine statischen Dateien mehr aus. Ohne diesen Schritt fehlt dem
Admin-Bereich jedes Stylesheet und die Swagger-Oberfläche funktioniert
nicht.

### 3.10 Frontend einrichten

```bash
cd /var/www/coderr
git clone https://github.com/Developer-Akademie-Backendkurs/project.Coderr.git frontend
cd frontend

sed -i "s|const API_BASE_URL = .*|const API_BASE_URL = 'https://coderr.benjaminblarr.de/api/';|" shared/scripts/config.js
sed -i "s|const STATIC_BASE_URL = .*|const STATIC_BASE_URL = 'https://coderr.benjaminblarr.de/';|" shared/scripts/config.js
```

Danach die eigenen Rechtstexte vom Arbeitsrechner hochladen:

```powershell
scp imprint.html privacy_policy.html vps:/var/www/coderr/frontend/
```

> **Achtung:** Diese drei Anpassungen (`config.js`, `imprint.html`,
> `privacy_policy.html`) sind nicht im Akademie-Repo. Ein `git pull` im
> Frontend-Ordner überschreibt sie. Nach einem Update des Frontends
> müssen sie erneut eingespielt werden.

### 3.10a Portfolio und die übrigen Projekte

Statische Projekte direkt von GitHub holen, das ist schneller als ein
Upload und spart den Umweg über den Arbeitsrechner:

```bash
sudo mkdir -p /var/www/el-pollo-loco /var/www/pokedex /var/www/join
sudo chown benni:benni /var/www/el-pollo-loco /var/www/pokedex /var/www/join

git clone https://github.com/B-Blarr/El-Pollo-Loco.git /var/www/el-pollo-loco
git clone https://github.com/B-Blarr/Pokedex.git /var/www/pokedex
```

Angular-Projekte lokal bauen und hochladen. Beim Portfolio liegt das
Ergebnis in `dist/portfolio/browser/`, bei Join in
`dist/join-project/browser/`. Seit Angular 17 gibt es diese
Zwischenebene `browser`, wer den Ordner darüber hochlädt, bekommt eine
leere Seite.

```powershell
# Portfolio
cd <projekt>\portfolio
npm run build
cd dist\portfolio\browser
scp -r * vps:/var/www/portfolio/

# Join, laeuft unter einem Unterpfad und braucht deshalb base-href
cd <projekt>\Join
npx ng build --base-href /join/
cd dist\join-project\browser
scp -r * vps:/var/www/join/
```

**Nach jedem `scp` die Rechte richten**, siehe Abschnitt 7:

```bash
chmod -R a+rX /var/www/portfolio /var/www/join
```

Vor einem erneuten Deployment den Zielordner leeren, sonst sammeln sich
alte Bundles an, weil Angular an jeden Dateinamen einen Hash hängt:

```bash
rm -rf /var/www/portfolio/*
```

### 3.11 Gunicorn als Dienst

Datei anlegen (Inhalt siehe Abschnitt 4.2), dann:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn-coderr
sudo systemctl status gunicorn-coderr --no-pager
```

Test ohne Nginx:

```bash
curl --unix-socket /run/gunicorn/coderr.sock \
     -H "Host: coderr.benjaminblarr.de" http://localhost/api/base-info/
```

Der `Host`-Header ist nötig, weil `ALLOWED_HOSTS` gesetzt ist. Ohne ihn
antwortet Django korrekt mit `400 Bad Request`.

### 3.12 Nginx

Beide Dateien anlegen (Inhalte siehe Abschnitt 4.3 und 4.4), dann:

```bash
sudo ln -s /etc/nginx/sites-available/benjaminblarr /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/coderr /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

> **Konfigurationsdateien nicht per Copy-Paste ins Terminal einfügen.**
> Bei längeren `tee`-Blöcken verschluckt die Terminalsitzung
> gelegentlich Zeilen oder schiebt zwei Befehle ineinander, ohne dass es
> auffällt. Das ist hier zweimal passiert. Zuverlässiger ist, die Datei
> lokal zu schreiben und hochzuladen:
>
> ```powershell
> scp nginx-coderr.conf vps:/tmp/
> ```
> ```bash
> sudo install -m 644 -o root -g root /tmp/nginx-coderr.conf \
>   /etc/nginx/sites-available/coderr
> ```

### 3.13 DNS für die Subdomain

Beim Domain-Anbieter ein zusätzlicher Eintrag:

| Typ | Name     | Wert         |
|-----|----------|--------------|
| A   | `coderr` | `<SERVER-IP>`|

`A` zeigt direkt auf eine IP-Adresse, `CNAME` auf einen anderen Namen.
Für `@`, also die Domain selbst, ist `CNAME` nicht erlaubt. Weil hier
ohnehin alles auf demselben Server liegt, ist `A` überall die einfachere
Wahl: eine Auflösung weniger und keine Sonderregeln.

Vor dem certbot-Aufruf prüfen, ob der Eintrag verteilt ist:

```bash
dig +short coderr.benjaminblarr.de
```

### 3.14 TLS-Zertifikat

```bash
sudo certbot --nginx -d benjaminblarr.de -d www.benjaminblarr.de
sudo certbot --nginx -d coderr.benjaminblarr.de
sudo certbot renew --dry-run
sudo systemctl list-timers | grep certbot
```

Getrennte Aufrufe, damit die Subdomain ein eigenes Zertifikat bekommt.
Ein gemeinsames Zertifikat über alle Namen ginge auch, dann hängt aber
die Erneuerung aller Namen an einer Datei. Certbot muss den passenden
`server`-Block finden, die Nginx-Datei aus 4.4 muss also vorher stehen
und geladen sein.

certbot ergänzt die Nginx-Konfiguration selbstständig um die
Zertifikatspfade, den `listen 443 ssl` Block und die Weiterleitung von
HTTP auf HTTPS. Die Datei sieht danach anders aus als die selbst
geschriebene Version.

Zertifikate laufen nach 90 Tagen ab. Der Timer erneuert automatisch ab
30 Tagen Restlaufzeit. Der Trockenlauf spielt das durch, ohne ein echtes
Zertifikat zu verbrauchen.

### 3.15 HSTS aktivieren

**Erst nachdem HTTPS nachweislich funktioniert.** In der `.env`:

```ini
HSTS_SECONDS=31536000
```

```bash
sudo systemctl restart gunicorn-coderr
```

HSTS wird im Browser gespeichert. Wird es aktiviert, bevor die
Zertifikate stimmen, sperrt man sich und alle Besucher für die
eingestellte Dauer aus. Zurücknehmen wirkt erst nach Ablauf der Zeit.

---

## 4. Konfigurationsdateien

### 4.1 `/var/www/coderr/backend/.env`

Rechte 600, nicht im Repository.

```ini
SECRET_KEY=<64 Zeichen, für diese Umgebung neu erzeugt>
DEBUG=False
ALLOWED_HOSTS=coderr.benjaminblarr.de,benjaminblarr.de,www.benjaminblarr.de
CSRF_TRUSTED_ORIGINS=https://coderr.benjaminblarr.de,https://benjaminblarr.de,https://www.benjaminblarr.de
CORS_ALLOWED_ORIGINS=https://coderr.benjaminblarr.de,https://benjaminblarr.de
DB_NAME=coderr
DB_USER=coderr
DB_PASSWORD=<48 Hex-Zeichen>
DB_HOST=localhost
DB_PORT=5432
HSTS_SECONDS=31536000

EMAIL_HOST=mail.gmx.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<eigene Adresse>
EMAIL_HOST_PASSWORD=<anwendungsspezifisches Passwort, nicht das Kontopasswort>
DEFAULT_FROM_EMAIL=<dieselbe Adresse wie EMAIL_HOST_USER>
CONTACT_RECIPIENT=<Zieladresse der Formularnachrichten>
```

Ohne gesetzte Variablen verhält sich das Projekt wie in der Entwicklung:
`DEBUG=True`, SQLite, CORS auf `localhost:5500`. Der Produktionsmodus
entsteht ausschließlich durch diese Datei.

`benjaminblarr.de` muss in `ALLOWED_HOSTS` und den
`CSRF_TRUSTED_ORIGINS` stehen bleiben, obwohl Coderr dort nicht mehr
liegt. Das Kontaktformular des Portfolios spricht dieselbe Django-Instanz
unter der Hauptdomain an. Wird der Eintrag entfernt, antwortet der
Endpunkt mit `400 Bad Request`.

`FORCE_SCRIPT_NAME` ist seit dem 29.07.2026 **nicht mehr gesetzt**.
Solange Coderr unter `/coderr/` lief, teilte diese Variable Django mit,
dass es unter einem Unterpfad wohnt, und Django setzte den Wert vor die
relativen `STATIC_URL` und `MEDIA_URL` sowie vor alles, was `reverse()`
erzeugt. Auf einer eigenen Subdomain beginnt die Anwendung an der Wurzel,
die Variable würde jetzt ein falsches `/coderr` in jede Bild- und
Paginierungsadresse schreiben. Kontrolle nach einer Umstellung: eine
Bildadresse aus der Angebotsliste ansehen, sie muss
`https://coderr.benjaminblarr.de/media/...` lauten.

### 4.2 `/etc/systemd/system/gunicorn-coderr.service`

```ini
[Unit]
Description=Gunicorn daemon for Coderr backend
After=network.target postgresql.service
Requires=postgresql.service

[Service]
User=benni
Group=www-data
WorkingDirectory=/var/www/coderr/backend
RuntimeDirectory=gunicorn
ExecStart=/var/www/coderr/backend/.venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/gunicorn/coderr.sock \
    --umask 007 \
    --access-logfile - \
    --error-logfile - \
    core.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

| Zeile | Zweck |
|---|---|
| `Group=www-data` | damit Nginx den Socket benutzen darf |
| `--umask 007` | Socket mit Rechten 770 statt für alle offen |
| `RuntimeDirectory=gunicorn` | systemd legt `/run/gunicorn` an und räumt auf |
| `Restart=always` | Neustart nach Absturz |
| `Requires=postgresql.service` | Datenbank startet vor der Anwendung |
| `--access-logfile -` | Logs nach stdout, landen im systemd-Journal |

### 4.3 `/etc/nginx/sites-available/benjaminblarr`

Portfolio und die statischen Projekte. Coderr taucht hier seit dem
29.07.2026 nicht mehr auf, die Weiterleitung der alten Adressen steckt
im Snippet aus Abschnitt 4.5.

Basisversion vor der Bearbeitung durch certbot. Nach `certbot --nginx`
kommen `listen 443 ssl`, die Zertifikatspfade und ein
Weiterleitungsblock für Port 80 hinzu.

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name benjaminblarr.de www.benjaminblarr.de;

    root /var/www/portfolio;
    index index.html;

    # Uploads: Django-Profilbilder brauchen mehr als die 1 MB Standard
    client_max_body_size 10M;

    include /etc/nginx/snippets/projekte.conf;

    access_log /var/log/nginx/benjaminblarr.access.log;
    error_log  /var/log/nginx/benjaminblarr.error.log;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Wichtige Punkte:

- `client_max_body_size 10M` überschreibt Nginx' Standard von 1 MB.
  Ohne diese Zeile lehnt Nginx Uploads mit
  `413 Request Entity Too Large` ab, bevor Django sie überhaupt sieht.
  Der Fehler taucht deshalb in keinem Django-Log auf. Der Wert gilt pro
  `server`-Block und muss in der Coderr-Datei erneut stehen.
- Nginx wählt nicht den ersten passenden `location`-Block, sondern den
  mit dem längsten übereinstimmenden Prefix. Die Reihenfolge im File ist
  daher unkritisch. Das ist genau umgekehrt zu OpenSSH.

certbot hängt seine Zeilen (`listen 443 ssl`, Zertifikatspfade) **ans
Ende** des `server`-Blocks und ergänzt einen zweiten Block für Port 80,
der auf HTTPS umleitet. Der erste Block in der Datei ist danach also der
HTTPS-Block, auch wenn das erst unten sichtbar wird.

### 4.4 `/etc/nginx/sites-available/coderr`

Eigener `server`-Block für die Subdomain. Basisversion vor certbot.

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name coderr.benjaminblarr.de;

    root /var/www/coderr/frontend;
    index index.html;

    client_max_body_size 10M;

    access_log /var/log/nginx/coderr.access.log;
    error_log  /var/log/nginx/coderr.error.log;

    location /api/ {
        proxy_pass http://unix:/run/gunicorn/coderr.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /admin/ {
        proxy_pass http://unix:/run/gunicorn/coderr.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /var/www/coderr/backend/staticfiles/;
        expires 30d;
        access_log off;
    }

    location /media/ {
        alias /var/www/coderr/backend/media/;
        expires 7d;
        access_log off;
    }

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Wichtige Punkte:

- Hinter dem Socket steht **kein** Pfad mehr. Solange Coderr unter
  `/coderr/` lag, hieß es `...coderr.sock:/api/`, weil Nginx den Prefix
  abschneiden musste. Auf der Subdomain stimmt der Pfad bereits, die
  Adresse wird unverändert durchgereicht.
- Das Frontend liegt jetzt in `root` statt in einem `alias`-Block. Das
  ist der eigentliche Gewinn der Subdomain: keine Pfadumschreibung mehr,
  weder im Webserver noch in Django.
- `try_files ... =404` ist richtig, weil das Akademie-Frontend ein
  klassisches Mehrseiten-Projekt ist. Ein SPA-Rückfall auf `index.html`
  würde fehlende Dateien mit Status 200 beantworten.
- `X-Forwarded-Proto $scheme` wird von `SECURE_PROXY_SSL_HEADER` in den
  Django-Einstellungen gelesen. Ohne diesen Header hält Django jede
  Anfrage für unverschlüsselt und erzeugt `http://`-Links.

### 4.5 `/etc/nginx/snippets/projekte.conf`

Ausgelagert, damit die von certbot bearbeitete Hauptdatei übersichtlich
bleibt und neue Projekte ohne Eingriff dort ergänzt werden können.
Eingebunden im HTTPS-`server`-Block mit:

```nginx
include /etc/nginx/snippets/projekte.conf;
```

```nginx
# Coderr liegt seit dem 29.07.2026 auf einer eigenen Subdomain.
# Die alten Adressen bleiben dauerhaft gueltig.
location = /coderr {
    return 301 https://coderr.benjaminblarr.de/;
}

location /coderr/ {
    rewrite ^/coderr/(.*)$ https://coderr.benjaminblarr.de/$1 permanent;
}

# Adressen ohne abschliessenden Schraegstrich auf die Variante mit umleiten
location = /join          { return 301 /join/; }
location = /pokedex       { return 301 /pokedex/; }
location = /el-pollo-loco { return 301 /el-pollo-loco/; }

location /el-pollo-loco/ {
    alias /var/www/el-pollo-loco/;
    index index.html;
    try_files $uri $uri/ =404;
}

location /pokedex/ {
    alias /var/www/pokedex/;
    index index.html;
    try_files $uri $uri/ =404;
}

location /join/ {
    alias /var/www/join/;
    index index.html;
    try_files $uri $uri/ /join/index.html;
}

# Kontaktformular des Portfolios, beantwortet von Django
location /api/contact {
    proxy_pass http://unix:/run/gunicorn/coderr.sock;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Die `location =` Blöcke sind exakte Übereinstimmungen und werden von
Nginx vor allen Prefix-Blöcken geprüft. Warum sie nötig sind, steht in
Abschnitt 7.

Die Weiterleitung von Coderr ist bewusst zweigeteilt. `rewrite` mit der
Gruppe `(.*)` hängt den Rest des Pfades an die neue Adresse an, damit
`/coderr/login.html` auf `coderr.benjaminblarr.de/login.html` landet und
nicht auf der Startseite. Der Sonderfall `/coderr` ohne Schrägstrich
passt nicht auf `location /coderr/` und braucht deshalb den eigenen
exakten Block. `permanent` entspricht `301`, Browser und Suchmaschinen
merken sich das dauerhaft.

Beim Kontakt-Block steht hinter dem Socket **kein** Pfad. Dadurch reicht
Nginx die Adresse unverändert weiter und Django sieht `/api/contact/`.
Der Header `X-Real-IP` ist hier keine Kosmetik: die
Ratenbegrenzung des Endpunkts liest ihn aus, um Absender zu
unterscheiden. Ohne ihn käme jede Anfrage scheinbar von `127.0.0.1` und
das Limit würde für alle Besucher gemeinsam gelten.

Der Unterschied beim Rückfall: Join ist eine Angular-Anwendung und
braucht `/join/index.html` als Rückfall, Pokédex und El Pollo Loco sind
klassische Mehrseiten-Projekte, dort ist `=404` richtig.

### 4.6 `/etc/nginx/sites-available/benjaminblarr-dev`

Weiterleitung der alten Domain. `$request_uri` erhält den Pfad, damit
alte Links wie `benjaminblarr.dev/pokedex` auf der passenden Unterseite
landen und nicht auf der Startseite.

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name benjaminblarr.dev www.benjaminblarr.dev;

    return 301 https://benjaminblarr.de$request_uri;
}
```

---

## 5. Regelmäßiger Betrieb

### 5.1 Code-Änderung ausrollen

```bash
cd /var/www/coderr/backend
git pull
.venv/bin/pip install -r requirements.txt      # nur bei neuen Paketen
.venv/bin/python manage.py migrate             # nur bei neuen Migrationen
.venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart gunicorn-coderr
sudo systemctl status gunicorn-coderr --no-pager
```

### 5.2 Logs ansehen

```bash
# Anwendung, live mitlesen
sudo journalctl -u gunicorn-coderr -f

# Anwendung, letzte 100 Zeilen
sudo journalctl -u gunicorn-coderr -n 100 --no-pager

# Nginx, Portfolio und Projekte
sudo tail -f /var/log/nginx/benjaminblarr.error.log
sudo tail -f /var/log/nginx/benjaminblarr.access.log

# Nginx, Coderr-Subdomain
sudo tail -f /var/log/nginx/coderr.error.log
sudo tail -f /var/log/nginx/coderr.access.log

# Datenbank
sudo journalctl -u postgresql -n 50 --no-pager
```

Bei einem `502 Bad Gateway` liegt die Ursache fast immer in
`journalctl -u gunicorn-coderr`, nicht im Nginx-Log.

### 5.3 Dienste

```bash
sudo systemctl restart gunicorn-coderr    # Anwendung neu starten
sudo systemctl reload nginx               # Nginx-Konfiguration neu laden
sudo nginx -t                             # Konfiguration prüfen
systemctl is-active nginx postgresql gunicorn-coderr
```

`reload` vor `restart` bevorzugen, wo möglich. `reload` unterbricht
bestehende Verbindungen nicht.

### 5.4 Demo-Daten erneuern

```bash
cd /var/www/coderr/backend
.venv/bin/python manage.py seed_demo
```

Der Befehl ist wiederholbar. Vorhandene Datensätze werden aktualisiert,
nicht doppelt angelegt. Er läuft in einer Transaktion, bei einem Fehler
bleibt der vorherige Zustand erhalten.

### 5.5 Datenbank sichern

Läuft automatisch täglich um 03:30 Uhr Serverzeit (UTC) über
`/usr/local/bin/backup-coderr.sh`, ausgelöst von
`coderr-backup.timer`. Gesichert werden die Datenbank und der
`media`-Ordner, Ablage unter `/var/backups/coderr/`, Aufbewahrung
14 Tage.

```bash
# Status und naechster Lauf
systemctl list-timers coderr-backup --no-pager

# Letzte Laeufe nachlesen
sudo journalctl -u coderr-backup -n 30 --no-pager

# Sofort ausfuehren
sudo /usr/local/bin/backup-coderr.sh

# Sicherung einspielen
gunzip -c /var/backups/coderr/db-2026-07-27_0330.sql.gz \
  | sudo -u postgres psql coderr
```

Der Timer nutzt `Persistent=true`, ein wegen Neustart verpasster Lauf
wird also nachgeholt. `RandomizedDelaySec=300` streut den Start über
fünf Minuten.

Hostinger erstellt zusätzlich wöchentlich automatische Backups des
gesamten Servers. Ein manueller Snapshot vor riskanten Änderungen ist im
hPanel kostenlos möglich, allerdings nur einer gleichzeitig und mit
einem Tag Haltbarkeit.

### 5.6 Kontaktformular

Das Formular des Portfolios postet an `/api/contact/`. Zuständig ist
die App `contact_app` im Coderr-Backend.

Ablauf einer Nachricht:

1. Angular sendet Name, E-Mail, Nachricht und das Honeypot-Feld
   `website` als JSON.
2. Ist `website` befüllt, verwirft der Server die Einsendung und
   antwortet trotzdem mit 201. Ein Bot soll nicht erkennen, dass es
   eine Falle gibt.
3. Andernfalls wird die Nachricht **zuerst in der Datenbank
   gespeichert** und erst danach versendet. Ein ausgefallener
   Mailserver kostet damit keine Anfrage.
4. Versendet wird über SMTP bei einem echten Mailanbieter, nicht vom
   Server selbst. Absender ist die eigene Adresse, die Adresse des
   Besuchers steht im `Reply-To`. Umgekehrt wäre es ein
   Fälschungsversuch und würde von Spamfiltern abgestraft.

Eingegangene Nachrichten stehen unter
`https://coderr.benjaminblarr.de/admin/` bei "Kontaktnachrichten",
inklusive der Angabe, ob der Versand geklappt hat.

```bash
# Hat der Versand funktioniert?
sudo journalctl -u gunicorn-coderr -n 50 --no-pager | grep Kontaktformular

# Endpunkt direkt testen
curl -i -X POST https://benjaminblarr.de/api/contact/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","message":"Testnachricht."}'
```

Die Ratenbegrenzung liegt bei 5 Nachrichten pro Stunde und Absender,
eingestellt über `DEFAULT_THROTTLE_RATES` in den Django-Einstellungen.
Sie zählt über den Datenbank-Cache, damit alle Gunicorn-Prozesse
gemeinsam zählen. Nach einer Neuinstallation muss die Cache-Tabelle
einmalig angelegt werden:

```bash
.venv/bin/python manage.py createcachetable
```

---

## 6. Fehlersuche

| Symptom | Wahrscheinliche Ursache | Prüfen mit |
|---|---|---|
| `502 Bad Gateway` | Gunicorn läuft nicht oder ist abgestürzt | `sudo systemctl status gunicorn-coderr`, `journalctl -u gunicorn-coderr -n 50` |
| `400 Bad Request` | Angefragter Hostname nicht in `ALLOWED_HOSTS` | `grep ALLOWED_HOSTS .env` |
| `413 Request Entity Too Large` | `client_max_body_size` zu klein | Nginx-Konfiguration, Standard ist 1 MB |
| Admin ohne Stylesheets | `collectstatic` nicht gelaufen | `ls staticfiles/admin/css/` |
| Bilder werden nicht angezeigt | Pfad falsch zusammengesetzt | Bildadresse im Browser prüfen, muss `coderr.benjaminblarr.de/media/...` lauten, ohne `/coderr` |
| Upload schlägt fehl | Schreibrechte im `media`-Ordner | `ls -ld /var/www/coderr/backend/media` |
| `permission denied for schema public` | `GRANT ALL ON SCHEMA public` fehlt | Abschnitt 3.8 |
| CSRF-Fehler im Admin | `CSRF_TRUSTED_ORIGINS` fehlt oder falsch | `.env` prüfen, muss mit `https://` beginnen |
| SSH-Schlüssel wird ignoriert | Rechte auf `.ssh` oder `authorized_keys` zu weit | `ls -la ~/.ssh`, muss 700 und 600 sein |
| SSH-Einstellung wirkt nicht | Datei in `sshd_config.d` mit kleinerer Nummer gewinnt | `sudo sshd -T \| grep <option>` |
| Zertifikat läuft ab | certbot-Timer inaktiv | `sudo systemctl list-timers \| grep certbot` |
| Subdomain zeigt das Portfolio | `server_name` greift nicht, Anfrage landet im Standard-Block | `sudo nginx -T \| grep server_name`, Symlink in `sites-enabled` prüfen |
| Kontaktformular antwortet mit 400 | `benjaminblarr.de` aus `ALLOWED_HOSTS` entfernt | `grep ALLOWED_HOSTS .env`, Hauptdomain muss drinbleiben |
| Bildadressen enthalten `/coderr` | `FORCE_SCRIPT_NAME` noch gesetzt | `grep FORCE_SCRIPT_NAME .env`, Zeile muss weg |
| Seite lädt sehr langsam | Speicher voll, System swappt | `free -h`, `top` |

### Wichtigste Diagnosebefehle

```bash
sudo journalctl -u gunicorn-coderr -n 50 --no-pager   # Anwendungsfehler
sudo nginx -t                                          # Nginx-Syntax
sudo sshd -T                                           # wirksame SSH-Werte
.venv/bin/python manage.py check --deploy              # Produktionsreife
free -h && df -h /                                     # Speicher und Platte
```

---

## 7. Erlebte Stolpersteine

Dokumentiert, weil sie beim nächsten Projekt wieder auftreten.

**`requirements.txt` in UTF-16.** Entsteht durch
`pip freeze > requirements.txt` in der PowerShell. `pip install -r` kann
die Datei unter Linux nicht lesen. Prüfen mit `file requirements.txt`,
erwartet wird `ASCII text` oder `UTF-8`. Lösung: die Datei als UTF-8
neu schreiben. Besser gleich
`pip freeze | Out-File -Encoding utf8 requirements.txt` verwenden.

**Reihenfolge in `sshd_config.d`.** Siehe Abschnitt 3.4. Der erste Wert
gewinnt, nicht der letzte.

**Schema-Rechte ab PostgreSQL 15.** Siehe Abschnitt 3.8.

**GitHub-Passwort funktioniert nicht.** Passwort-Anmeldung für
Git-Operationen ist seit 2021 abgeschaltet. Für private Repos wird ein
Deploy Key oder ein Personal Access Token benötigt. Bei öffentlichen
Repos ist gar keine Anmeldung nötig.

**Gastzugänge fehlten in der Datenbank.** Das Akademie-Frontend
erwartet in `config.js` die Nutzer `andrey` und `kevin` mit festgelegten
Passwörtern. Ohne diese Konten scheitert der Gast-Login-Knopf, also der
erste Klick jedes Besuchers. Die Konten werden von
`manage.py seed_demo` angelegt.

**Zeilenenden zwischen Windows und Linux.** Auf dem Arbeitsrechner ist
`core.autocrlf` aktiv, in einer Linux-Umgebung nicht. Dadurch kann
`git status` alle Dateien als geändert melden, obwohl inhaltlich nichts
geändert wurde. Konsequenz: alle Git-Operationen für dieses Repo auf
demselben System ausführen und beim Committen einzelne Dateien statt
`git add .` angeben.

**Verzeichnisrechte nach `scp`.** Nach dem Hochladen des
Angular-Builds von Windows kamen die Unterordner mit `700` auf dem
Server an. Nginx läuft als `www-data` und konnte sie nicht betreten.
Die Folge war heimtückisch: statt eines Fehlers lieferte Nginx für
jede Datei aus einem Unterordner die `index.html` aus, weil
`try_files` die Datei als nicht vorhanden ansah und auf den
SPA-Rückfall ging. Der Browser bekam also Status 200 und
`Content-Type: text/html`, wo er ein JPEG oder JSON erwartete. Bilder
blieben leer, Übersetzungen fehlten, ohne eine einzige Fehlermeldung.

Erkennungsmerkmal: `curl -sI <url> | grep content-type` liefert
`text/html` für eine Datei, die kein HTML ist.

```bash
chmod -R a+rX /var/www/portfolio
```

Das grosse `X` setzt das Ausführungsrecht nur bei Verzeichnissen. Mit
kleinem `x` würde jedes Bild als ausführbar markiert.

**Prefix-Blöcke matchen den Pfad ohne Schrägstrich nicht.** Ein
`location /join/` greift bei der Anfrage `/join` nicht, weil diese
nicht mit `/join/` beginnt. Die Anfrage fällt dann auf `location /`
durch und landet im SPA-Rückfall, liefert also das Portfolio statt des
Projekts, mit Status 200. Bei einem `root`-Verzeichnis würde Nginx
selbst auf die Variante mit Schrägstrich umleiten, bei `alias` mit
Prefix-Block nicht, weil der Block gar nicht erst zum Zug kommt.

Lösung sind die `location = /join { return 301 /join/; }` Blöcke aus
Abschnitt 4.5. Die Korrektur gehört in den Server und nicht in die
Links der eigenen Seite, denn getippte oder kopierte Adressen lassen
sich nicht kontrollieren.

**Terminal verschluckt eingefügte Zeilen.** Beim Einfügen langer
`tee`-Blöcke in die SSH-Sitzung kamen zweimal nicht alle Zeilen an. Beim
zweiten Mal rutschten sogar zwei Befehle ineinander, die Ausgabe sah
dadurch aus, als sei ein `systemctl reload` mit einem Pfad verschmolzen.
Weil die Datei danach syntaktisch trotzdem plausibel wirkte, fällt so
etwas erst beim Testen auf. Konsequenz: Konfigurationsdateien lokal
schreiben, per `scp` hochladen und mit `install` an ihren Platz legen.
Der Nebeneffekt ist erwünscht, die Dateien liegen dann versioniert auf
dem Arbeitsrechner statt nur auf dem Server.

Gegenprobe nach dem Übertragen:

```bash
wc -l /etc/nginx/sites-available/coderr
sudo nginx -t
```

**Unterpfad gegen Subdomain.** Coderr lief zuerst unter
`benjaminblarr.de/coderr/`. Das funktioniert, kostet aber an drei
Stellen Sonderbehandlung: `FORCE_SCRIPT_NAME` in Django, ein `alias`
statt `root` in Nginx und ein `proxy_pass` mit angehängtem Pfad, der den
Prefix wieder abschneidet. Jede dieser Stellen kann einzeln kaputtgehen,
und der typische Fehler ist ein doppeltes oder fehlendes `/coderr` in
Bild- und Paginierungsadressen.

Auf einer eigenen Subdomain entfallen alle drei. Die Anwendung beginnt
an der Wurzel, so wie sie es lokal auch tut. Dazu kommt die saubere
Trennung: eigenes Zertifikat, eigene Logdateien, eigene Cookie-Domain.
Der Preis ist ein zusätzlicher DNS-Eintrag.

Umgestellt wurde am 29.07.2026 auf Empfehlung des Mentors. Die alten
Adressen wurden bewusst nicht abgeschaltet, sondern leiten weiter, weil
der Link zum Zeitpunkt der Abgabe schon verschickt war.

Reihenfolge bei so einer Umstellung, damit nie eine Lücke entsteht:

1. DNS-Eintrag anlegen und Verteilung mit `dig` prüfen
2. Neuen `server`-Block anlegen und aktivieren, alter Weg bleibt bestehen
3. Zertifikat für die Subdomain holen
4. Frontend-`config.js` auf die neuen Adressen setzen
5. `FORCE_SCRIPT_NAME` aus der `.env` nehmen, Gunicorn neu starten
6. Erst jetzt die alten Blöcke durch die Weiterleitung ersetzen
7. Links im Portfolio anpassen, neu bauen, hochladen

**Secret Key in der Git-Historie.** Der von `startproject` erzeugte
Schlüssel steckte im ersten Commit. Beim Öffentlichmachen eines Repos
wird die gesamte Historie lesbar, nicht nur der aktuelle Stand. Prüfen
mit `git log --all -S "django-insecure"`. In diesem Fall unkritisch, weil
es ein Entwicklungsschlüssel war und in Produktion ein anderer läuft.
Für die Zukunft: Secret Key ab dem ersten Commit in die `.env`.

---

## 8. Offene Punkte

- [ ] Wiederherstellung einer Sicherung einmal proben, mit einer
      Kopie der Datenbank und nicht mit der echten
- [ ] Entscheiden, ob `benjaminblarr.dev` über den 06.02.2027 hinaus
      verlängert wird. Die automatische Verlängerung steht derzeit auf
      aus. Solange die Domain lebt, funktionieren alte Links aus
      Bewerbungen und von LinkedIn über die Weiterleitung weiter.
      Läuft sie aus, laufen diese Links ins Leere und der Name wird
      für jeden frei
- [ ] Alte DNS-Einträge in der `.dev`-Zone aufräumen, sobald über den
      Punkt darüber entschieden ist: `A ftp` auf den alten
      Webhosting-Server, die drei `hostingermail-*._domainkey`, die
      beiden `MX`, `autodiscover`, `autoconfig` und der SPF-Eintrag.
      **Nicht anfassen:** `A @`, `AAAA @` und `CNAME www`, die zeigen
      auf den VPS und tragen die Weiterleitung

### Erledigt am 29.07.2026

- [x] Coderr auf die eigene Subdomain `coderr.benjaminblarr.de` gelegt
- [x] Eigener Nginx-Block, eigenes Zertifikat, eigene Logdateien
- [x] `FORCE_SCRIPT_NAME` entfernt, Frontend-`config.js` angepasst
- [x] Alte Adressen unter `/coderr/` leiten dauerhaft weiter, mit
      erhaltenem Pfad
- [x] Portfolio-Link auf die neue Adresse gesetzt und neu ausgerollt
- [x] `sendMail.php` und `.htaccess` aus dem Portfolio entfernt,
      inklusive des Asset-Eintrags in `angular.json`
- [x] DNS-TTL nach der Umstellung wieder hochgesetzt
- [x] Webhosting-Tarif und ein Mail-Testabo auf auslaufend gestellt.
      Das Hosting bleibt bis 06.05.2027 erreichbar, danach ist alles
      dort Liegende weg
- [x] Darstellung des Portfolios auf allen Breiten nachgearbeitet

### Erledigt am 27.07.2026

- [x] VPS eingerichtet, abgesichert, Swap, Firewall
- [x] PostgreSQL, Django, Gunicorn, Nginx, Let's Encrypt, HSTS
- [x] Coderr live inklusive Demo-Daten und Gastzugängen
- [x] Portfolio, Join, Pokédex und El Pollo Loco umgezogen
- [x] `benjaminblarr.dev` leitet dauerhaft auf `benjaminblarr.de` um
- [x] Tägliche Sicherung von Datenbank und Medien
- [x] Kontaktformular auf eigenen Django-Endpunkt umgestellt
- [x] Coderr als viertes Projekt ins Portfolio aufgenommen
