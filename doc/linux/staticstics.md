## GoAccess

```bash

sudo apt install goaccess

sudo mkdir -p /var/lib/goaccess


sudo goaccess /var/log/apache2/ecb_access_ssl.log \
  --log-format=COMBINED \
  --persist \
  --db-path=/var/lib/goaccess \
  --real-time-html \
  --ws-url=127.0.0.1 \
  -o /var/www/ecb-app/static/goaccess.html


# edit 
sudo vim /etc/cron.d/goaccess
*/5 * * * * root goaccess /var/log/apache2/ecb_access_ssl.log --log-format=COMBINED --persist --db-path=/var/lib/goaccess -o /var/www/ecb-app/static/goaccess.html


https://ecb-watch.zew.de/static/goaccess.html#requestsl


```

##  Shynet (no cookies, can work without JS)

What you get: simple, privacy-friendly metrics; no users/funnels fluff.
Storage: Postgres (not file-only).
Why pick it: cookie-less + straightforward dashboards. 


### GoatCounter

* Instructions by chatGPT 

* Same domain, sub-path, SQLite 

```bash
# install binary release

cd ~
curl -L --fail -o goatcounter.gz https://github.com/arp242/goatcounter/releases/download/v2.6.0/goatcounter-v2.6.0-linux-amd64.gz

gunzip -f goatcounter.gz
chmod +x goatcounter
./goatcounter -version


sudo su

# create system user (no shell), create dirs, set ownership
useradd -r -s /usr/sbin/nologin goat

mkdir -p /opt/goatcounter/goatcounter-data
chown -R goat:goat /opt/goatcounter
chmod 750 /opt/goatcounter

cp /home/pbu/goatcounter   /usr/local/bin/goatcounter 
chmod 0755 /usr/local/bin/goatcounter


#########
# /etc/systemd/system/goatcounter.service
[Unit]
Description=GoatCounter analytics daemon
After=network.target

[Service]
Type=simple
User=goat
Group=goat
WorkingDirectory=/opt/goatcounter
Environment=GOATCOUNTER_DB=sqlite3+/opt/goatcounter/ecb-monitor.zew.de.sqlite
ExecStart=/usr/local/bin/goatcounter serve -listen 0.0.0.0:8811 -automigrate
Restart=on-failure
RestartSec=5
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target


systemctl daemon-reload
systemctl enable --now goatcounter.service

systemctl status goatcounter.service
journalctl -u goatcounter.service -f


# create a db
# password is for goatkeeper user 'admin' HTML frontent
sudo -u goat /usr/local/bin/goatcounter db create site \
  -vhost=ecb-monitor.zew.de \
  -user.email=peter.buchmann@zew.de \
  -password 'Pb165025.' \
  -createdb \
  -db 'sqlite3+/opt/goatcounter/ecb-monitor.zew.de.sqlite'

# confirm the DB file is there and owned by goat
sudo -u goat ls -l /opt/goatcounter/ecb-monitor.zew.de.sqlite


```



### Apache

no way ro run goatcounter as a subdirectory.

we need to request a sub-sub domain  stats.ecb-monitor.zew.de

http://192.168.2.142:8811
http://192.168.2.142:8811







Add the pixel (no JS) to your pages (loads fast, cookie-less):

<img src="/stats/count?p=/current-page" alt="" referrerpolicy="no-referrer-when-downgrade" />


Or use the 3.5 KB script:

<script data-goatcounter="/stats/count" async src="/stats/count.js"></script>

