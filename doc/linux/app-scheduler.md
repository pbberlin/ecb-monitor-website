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
WorkingDirectory=/var/www/ecb-app/scripts/scheduler/
ExecStart=/var/www/ecb-app/.venv/bin/python scheduler_main.py
Restart=always
User=www-data
Group=www-data

[Install]
WantedBy=multi-user.target
```


```bash
sudo systemctl daemon-reload
sudo systemctl enable app-scheduler
sudo systemctl start  app-scheduler

# alternatively
# @reboot /path/to/venv/bin/python /path/to/project/scheduler_main.py >> /var/log/app-scheduler.log 2>&1

```


## windows

<!-- cd into development git repo - scripts/scheduler -->
cd C:\users\pbu\Documents\zew_work\git\python\guw-flask\scripts\scheduler\
<!-- run  -->
..\..\venv\Scripts\python.exe scheduler_main.py
