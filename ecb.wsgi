import sys
from pathlib import Path

def ensurePath(p):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

basePath = Path("/var/www/ecb-app")
venvPath = basePath / ".venv"
sitePkgs = list((venvPath / "lib").glob("python*/site-packages"))

ensurePath(basePath)
for sp in sitePkgs:
    ensurePath(sp)

from app import app as application


import os

PROJECT_ROOT = "/var/www/ecb-app"
os.chdir(PROJECT_ROOT)


