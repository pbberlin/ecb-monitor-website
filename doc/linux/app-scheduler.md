# cron jobs

## Debian

```bash
sudo vim /etc/systemd/system/app-scheduler.service
```

```conf
[Unit]
Description=Python job scheduler for my Flask app
After=network.target

[Service]
WorkingDirectory=/var/www/ecb-app/
ExecStart=/var/www/ecb-app/.venv/bin/python scripts/scheduler/scheduler_main.py
Restart=always
User=www-data
Group=www-data
Environment=HOME=/home/www-data
UMask=0002
Environment=GIT_TERMINAL_PROMPT=0


[Install]
WantedBy=multi-user.target
```


```bash
sudo systemctl daemon-reload
sudo systemctl enable app-scheduler
sudo systemctl start  app-scheduler

# alternatively
# @reboot /path/to/venv/bin/python /path/to/project/scheduler_main.py >> /var/log/app-scheduler.log 2>&1

sudo journalctl -u app-scheduler.service
sudo journalctl -u app-scheduler.service -f

sudo journalctl -u app-scheduler.service -o cat --no-pager | less


sudo -u www-data test -r /var/www/ecb-app/scripts && echo "read ok"    || echo "read denied"
sudo -u www-data test -x /var/www/ecb-app/scripts && echo "execute ok" || echo "execute denied"


```

## Send results to zabbix

```bash

# requires zabbix_sender

powershell
Test-NetConnection -ComputerName monitor2.zew.de -Port 10050
# port is 10050 or 10051


sudo apt install zabbix-sender
# or sudo apt install zabbix-agent


# for data sent with zabbix_sender 
#   =>  we need to create an item of type "zabbix trapper" 
http://monitor2.zew.de/zabbix/zabbix.php?action=item.list&filter_set=1&filter_hostids%5B%5D=10672&context=host


```


## run manual

```bash

# windows
# cd into development git repo - scripts/scheduler
cd C:\users\pbu\Documents\zew_work\git\python\ecb-monitor\scripts\scheduler\
python -u .\scheduler_main.py


# linux
# run
..\..\venv\Scripts\python.exe scheduler_main.py


# or run the job script directly

# linux debian
cd /var/www/ecb-app
source /var/www/ecb-app/.venv/bin/activate
python ./scripts/fetch-ameco-eurostat.py



```
