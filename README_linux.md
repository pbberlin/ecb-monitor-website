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


sudo /var/www/ecb-app/.venv/bin/mod_wsgi-express module-config  | sudo tee /etc/apache2/mods-available/wsgi_express.load
sudo a2enmod wsgi_express
sudo systemctl reload apache2

python /var/www/ecb-app/app.py
# Danach http://127.0.0.1:5000 testen; mit Ctrl+C stoppen


less /var/log/apache2/ecb_error.log