#  Python Flask application

* Debian 11

* apache2 and wsgi / mod_wsgi

* Python flask web app




```bash
sudo apt update
sudo apt install -y python3-venv python3-pip apache2
sudo apt install -y libapache2-mod-proxy-uwsgi
sudo apt install -y libapache2-mod-wsgi-py3
sudo a2enmod proxy proxy_http headers



sudo mkdir -p /var/www/ecb-app
sudo chown -R $USER:$USER /var/www/ecb-app
python3 -m venv /var/www/ecb-app/.venv
source /var/www/ecb-app/.venv/bin/activate
pip install --upgrade pip
pip install flask mod_wsgi


python3.11 -m venv /var/www/ecb-app/.venv
source /var/www/ecb-app/.venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install --no-cache-dir mod_wsgi

pip install pip install gingado
pip install pip install pandas
pip install pip install matplotlib

sudo vim  /etc/apache2/sites-available/ecb.conf
sudo vim  /etc/apache2/sites-available/ecb-le-ssl.conf


sudo vim  /etc/apache2/sites-available/ecb.conf
# paste file ecb.conf
sudo /var/www/ecb-app/.venv/bin/mod_wsgi-express module-config  | sudo tee /etc/apache2/mods-available/wsgi_express.load
sudo a2enmod wsgi_express
sudo systemctl reload apache2

sudo apache2ctl -S
sudo apache2ctl configtest

python /var/www/ecb-app/app.py
# then http://127.0.0.1:5000 testen; mit Ctrl+C stoppen


sudo less /var/log/apache2/error.log
sudo less /var/log/apache2/ecb_access_ssl.log
sudo less /var/log/apache2/ecb_error_ssl.log

sudo less /var/log/apache2/other_vhosts_access.log


sudo less /var/log/apache2/ecb_error.log
sudo less /var/log/apache2/ecb_access.log

# refresh

sudo touch /var/www/ecb-app/ecb.wsgi


sudo systemctl reload apache2


```
## lets encrypt - let's encrypt - certbot

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-apache

sudo a2ensite ecb.conf
sudo systemctl reload apache2


sudo certbot --apache \
-d ecb-monitor.zew.de  \
-d ezb-monitor.zew.de  \
-d ezb-transparenz-monitor.zew.de  \
-d ecb-transparency-monitor.zew.de  \
-d ecb-watch.zew.de  \
-d ezb-watch.zew.de  \
-d ecbwatch.zew.de  \
-d ezbwatch.zew.de  \
-d stats2.zew.de


sudo a2enmod rewrite
sudo a2enmod http2


```


## Rights

* We need user `pbu` and `var-www`
* App scheduler is also running as `var-www` and needs to git push
* We have to go beyond class Linux chmod/chown - and us ACL

```bash

sudo git config --system --add safe.directory /var/www/ecb-app
# verify
git config --system --get-all safe.directory
sudo -u www-data git -C /var/www/ecb-app status



sudo mkdir -p /var/www/ecb-app

# following dirs are shared between pbu and www-data
# group ownership to www-data
sudo chown -R pbu:www-data /var/www/ecb-app


sudo find /var/www/ecb-app -type d -exec chmod 2775 {} \;
sudo find /var/www/ecb-app -type f -exec chmod 0664 {} \;


# multiple writers with different identities must coexist
#     frist  line _existing_ files and dirs
#     second line _future_   files and dirs - option -d is 'default'
sudo setfacl -R    -m u:pbu:rwX -m g:www-data:rwX /var/www/ecb-app
sudo setfacl -R -d -m u:pbu:rwX -m g:www-data:rwX /var/www/ecb-app

# redundant
sudo setfacl -R    -m u:pbu:rwX -m u:www-data:rwX -m g:www-data:rwX /var/www/ecb-app/.git
sudo setfacl -R -d -m u:pbu:rwX -m u:www-data:rwX -m g:www-data:rwX /var/www/ecb-app/.git

# sudo find /var/www/ecb-app -type f -name '*.py' -exec setfacl -b {} \;


# check getfacl [file]
getfacl ./app.py
getfacl ./*.py
getfacl ./static/dl/ameco_debt_to_gdp.*
getfacl ./static/dl/jsToCSV.py






# minimal home dir for www-data
#  no shell
#  but place for storing git config
sudo mkdir -p /home/www-data
sudo chown www-data:www-data /home/www-data
sudo chmod 0700 /home/www-data

sudo -u www-data env HOME=/home/www-data git -C /var/www/ecb-app config --global user.name "pbu"
sudo -u www-data env HOME=/home/www-data git -C /var/www/ecb-app config --global user.email "pbu@ecb-watch"
sudo -u www-data env HOME=/home/www-data git -C /var/www/ecb-app status

sudo -u www-data bash -lc 'cat > /home/www-data/.netrc <<EOF
machine git.zew.de
login pbu
password Soz!spa26
EOF
chmod 600 /home/www-data/.netrc
'

# now assign this home dir

sudo systemctl stop apache2
sudo systemctl stop app-scheduler.service
sudo usermod -d /home/www-data www-data
# check
getent passwd www-data
# should yield www-data:x:s33:33:www-data:/home/www-data:/usr/sbin/nologin

sudo systemctl start apache2
sudo systemctl start app-scheduler.service




```


## Old right config - obsolete






# some libraries write stuff - we need to give them temp dirs
sudo vim /etc/apache2/envvars
export TMPDIR=/var/www/ecb-app/tmp
export MPLCONFIGDIR=/var/www/ecb-app/tmp


# upload

```bash
# *    copy contents of tmp/, not the tmp/ directory itself
sudo cp -r -f /var/www/ecb-app/tmp/* /var/www/ecb-app/
sudo chown -R pbu:www-data /var/www/ecb-app
sudo chmod 2775            /var/www/ecb-app
sudo touch /var/www/ecb-app/ecb.wsgi
```



## git auto deploy I


```bash
ssh pbu@192.168.2.142 'echo ok'
# sudo -u git ssh pbu@192.168.2.142 'echo ok'

# -p to preserve date
# scp  -p /home/git/workdir/README.md   pbu@192.168.2.142:/var/www/ecb-app/
ssh pbu@192.168.2.142 'touch /var/www/ecb-app/ecb.wsgi'

```


## git auto deploy II



```bash
# on the destination host
git config --global credential.helper store
echo  'https://pbu:L!btardQ2@git.zew.de' > ~/.git-credentials
chmod 600 ~/.git-credentials
cat       ~/.git-credentials
```



```bash
#!/usr/bin/env bash
set -euo pipefail

# Read the 3 fields from stdin (oldrev newrev ref)
# Not strictly needed if you always deploy on any push, but harmless:
if ! read -r oldrev newrev refname; then
  refname=""
fi

# Deploy only on main branch updates; change if you need a different branch.
TARGET_REF="refs/heads/main"
if [[ -n "$refname" && "$refname" != "$TARGET_REF" ]]; then
  exit 0
fi

# ---- EDIT THESE ----
REMOTE_HOST="pbu@192.168.2.142"
REMOTE_DIR="/var/www/ecb-app"
BRANCH="main"
# --------------------

SSH_OPTS=" -o BatchMode=yes -o StrictHostKeyChecking=accept-new"

ssh pbu@192.168.2.142 'touch /var/www/ecb-app/ecb.wsgi'

# Option A (recommended): the remote repo uses SSH auth and has access via a deploy key.
ssh ${SSH_OPTS} "${REMOTE_HOST}" bash -lc "
  set -euo pipefail
  cd \"${REMOTE_DIR}\"

  # Set identity for commits/merges created on this machine (unrelated to auth):
  git config user.name 'pbu'
  git config user.email 'peter.buchmann@zew.de'
  git pull --ff-only origin main
  sudo systemctl restart apache2
  echo 'git pull on remote machine - stop'
"
```


### compression


```bash

sudo a2enmod deflate
sudo systemctl restart apache2

vim /etc/apache2/mods-available/deflate.conf

# add last line
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml
    AddOutputFilterByType DEFLATE text/css text/javascript application/javascript
    AddOutputFilterByType DEFLATE application/json
    AddOutputFilterByType DEFLATE application/geo+json
</IfModule>


sudo systemctl restart apache2

# test 
# response should contain 
#     "Content-Encoding: gzip"
curl -H "Accept-Encoding: gzip" -I https://ecb-monitor.zew.de/
curl -H "Accept-Encoding: gzip" -I https://ecb-monitor.zew.de/static/echart/europe-reduced.geojson


```

### Caching compressed

```bash
sudo a2enmod headers
sudo a2enmod deflate

sudo a2enmod cache
sudo a2enmod cache_disk
sudo systemctl restart apache2

```
