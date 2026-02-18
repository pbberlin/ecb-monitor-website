# Flask web application

## Local development web server 

```sh
pip install -r requirements.txt
cls && python app.py
```

* Use _localhost_ instead of 127.0.0.1

* Open in [browser](http://localhost:5000)


## No Admin

* If you dont have admin right

* pip install <contents of requirements.txt>

* python -m site --user-base yields
    * C:\Users\<YourName>\AppData\Roaming\Python
    * C:\Users\<YourName>\AppData\Roaming\Python\Python311


```powershell
[Environment]::SetEnvironmentVariable(
    "Path",
    $env:Path + ";C:\Users\<YourName>\AppData\Roaming\Python\Python311\Scripts",
    "User"
)
# restart terminal
echo $env:Path
```


## Notes

* This software is part of a research package at ZEW - sponsored by [Geld und Währung](https://www.stiftung-geld-und-waehrung.de/stiftung-de/) 

* The software is _early_ _alpha_




## wsgiref

* Run wsgi under linux

* Fails under windows

* Complete [setup guide](doc/linux/README-linux.md)  for Linux


```sh
# Web Server Gateway Interface (WSGI) 
python app-wsgiref.py
```



## Additonal setup - only for crawling recent speeches

```sh

# only for crawl03.py
pip   install httpx[http2]

# only for crawl05-ocr.py
pip   install ocrmypdf
choco install tesseract
choco install ghostscript
```

