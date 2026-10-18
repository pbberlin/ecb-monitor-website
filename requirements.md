# way 1

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


# way2



```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# windows 
pip install -U uv


# extract just the modules
pipreqs . --savepath requirements.in --mode no-pin --encoding=utf-8 --ignore .venv,venv
uv pip compile requirements.in -o requirements.txt --upgrade
uv pip install -r requirements.txt --system

playwright install
```