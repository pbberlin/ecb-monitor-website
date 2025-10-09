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
# paste file ecb.conf

sudo /var/www/ecb-app/.venv/bin/mod_wsgi-express module-config  | sudo tee /etc/apache2/mods-available/wsgi_express.load
sudo a2enmod wsgi_express
sudo systemctl reload apache2

python /var/www/ecb-app/app.py
# then http://127.0.0.1:5000 testen; mit Ctrl+C stoppen


sudo less /var/log/apache2/ecb_error.log
sudo less /var/log/apache2/ecb_access.log

# refresh

sudo touch /var/www/ecb-app/ecb.wsgi


sudo systemctl reload apache2


```

#  tmp rights for libraries

[wsgi:error]  File "/var/www/ecb-app/.venv/lib/python3.11/site-packages/gingado/internals.py", line 153, in download_csv
[wsgi:error]   Path(timestamped_file_path).parent.mkdir(exist_ok=True)  
                PermissionError: [Errno 13] Permission denied: 'gingado'


```bash
# following dirs are shared between 

sudo mkdir -p /var/www/ecb-app/tmp
# Set group ownership to www-data
sudo chown -R pbu:www-data /var/www/ecb-app/tmp
# both users read/write/execute
#    The 2 in 2775 sets the setgid bit, meaning any files created inside inherit the www-data group automatically.
#    That ensures new files made by the app (www-data) or by you (pbu) remain group-accessible.
sudo chmod 2775 /var/www/ecb-app/tmp

sudo chown -R pbu:www-data /var/www/ecb-app/data/dl
sudo chmod 2775            /var/www/ecb-app/data/dl


# some libraries write stuff - we need to give them temp dirs
sudo vim /etc/apache2/envvars
export TMPDIR=/var/www/ecb-app/tmp
export MPLCONFIGDIR=/var/www/ecb-app/tmp


# upload
# *    copy contents of tmp/, not the tmp/ directory itself
sudo cp -r -f /var/www/ecb-app/tmp/* /var/www/ecb-app/
sudo chown -R pbu:www-data /var/www/ecb-app
sudo chmod 2775            /var/www/ecb-app


```


