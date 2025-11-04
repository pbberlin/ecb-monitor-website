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


##  tmp rights for libraries

[wsgi:error]  File "/var/www/ecb-app/.venv/lib/python3.11/site-packages/gingado/internals.py", line 153, in download_csv
[wsgi:error]   Path(timestamped_file_path).parent.mkdir(exist_ok=True)
                PermissionError: [Errno 13] Permission denied: 'gingado'


```bash

# following dirs are shared between

sudo mkdir -p /var/www/ecb-app/tmp
# group ownership to www-data
sudo chown -R pbu:www-data /var/www/ecb-app/tmp
# both users read/write/execute
#    The 2 in 2775 sets the setgid bit, meaning any files created inside inherit the www-data group automatically.
#    That ensures new files made by the app (www-data) or by you (pbu) remain group-accessible.
sudo chmod 2775 /var/www/ecb-app/tmp


# application files - unreachable via URL
sudo chown -R pbu:www-data /var/www/ecb-app/data/dl
sudo chmod 2775            /var/www/ecb-app/data/dl

# application files - with URL - images, charts ...
sudo mkdir -p /var/www/ecb-app/static/tmp
sudo chown -R pbu:www-data /var/www/ecb-app/static/tmp
sudo chmod 2775            /var/www/ecb-app/static/tmp






# some libraries write stuff - we need to give them temp dirs
sudo vim /etc/apache2/envvars
export TMPDIR=/var/www/ecb-app/tmp
export MPLCONFIGDIR=/var/www/ecb-app/tmp


# upload
# *    copy contents of tmp/, not the tmp/ directory itself
sudo cp -r -f /var/www/ecb-app/tmp/* /var/www/ecb-app/
sudo chown -R pbu:www-data /var/www/ecb-app
sudo chmod 2775            /var/www/ecb-app
sudo touch /var/www/ecb-app/ecb.wsgi


```


## git auto deploy

```bash
# on the destination host
git config --global credential.helper store
echo  'https://pbu:L!btardQ2@git.zew.de' > ~/.git-credentials
chmod 600 ~/.git-credentials
cat       ~/.git-credentials
```

```bash
ssh pbu@192.168.2.142 'echo ok'
# sudo -u git ssh pbu@192.168.2.142 'echo ok'


# -p to preserve date
scp  -p /home/git/workdir/README.md   pbu@192.168.2.142:/var/www/ecb-app/
ssh pbu@192.168.2.142 'touch /var/www/ecb-app/ecb.wsgi'


#!/bin/bash
# Gitea post-receive: after push to git.zew.de/ecb-flask -> pull on ecb-monitor.zew.de

# read stdin so hook is "post-receive" correct
while read oldRev newRev refName; do
    :
done

remoteUser="pbu"
# remoteHost="ecb-monitor.zew.de"
remoteHost="192.168.2.142"
remoteRepoPath="/var/www/ecb-app"

# run the pull on the remote host
ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new "${remoteUser}@${remoteHost}" \
    "cd ${remoteRepoPath} && git pull --ff-only" || {
    echo "post-receive: remote pull failed" >&2
    exit 1
}


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

# Option A (recommended): the remote repo uses SSH auth and has access via a deploy key.
ssh ${SSH_OPTS} "${REMOTE_HOST}" bash -lc "
  set -euo pipefail
  cd \"${REMOTE_DIR}\"

  # Set identity for commits/merges created on this machine (unrelated to auth):
  git config user.name 'pbu'
  git config user.email 'peter.buchmann@zew.de'
  git pull --ff-only origin main
"
```