# way 1

```bash
# windows 
curl -LsSf https://astral.sh/uv/install.sh | sh
pip  install -U uv


# just extract the modules
pipreqs . --savepath requirements.in --mode no-pin --encoding=utf-8 --ignore .venv,venv
# create requirements file - newest module version
uv pip compile requirements.in -o requirements.txt --upgrade

# install/update modules on windows
uv   pip install -r requirements.txt --system

# install/update modules
# on linux - inside venv
source /var/www/ecb-app/.venv/bin/activate
uv pip install -r requirements.txt

playwright install
```


# way 2


```bash
pip install pipreqs
pip install pipreqs -U

# no compatibility, removes httpx[http2]...
pipreqs . --force --encoding=utf-8





flask
pandas
matplotlib

# not possible under windows
wsgiref
```


