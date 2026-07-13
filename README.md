# Flask web application

## Local development web server 

```sh
# at least python 3.11.2
pip install -r requirements.txt

set FLASK_DEBUG=1

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



## Architecture of data files

* We have country groups `nonMembers`, `euCountries`
    * `euCountries`  consisting of `euCountriesEuro` and  `notInEuro`
    * base data in `scripts/eu-and-euro-countries.py`
    * exported to JS file `static/dl/eu-and-euro-countries.js`

Containing time based data for 
    EU   accession   by year
    Euro accession   by year
    EU   leave       by year
    Euro leave       by year


The html javascript gets three lists/dicts
    * non EU   countries - background dark grey       and no   stats number  - on mouse over "[Country] non EU"
    * non Euro countries - background light blue      and with stats number  - on mouse over "[Country] (no €)"
    * in  Euro countries - background dynamic stats   and with stats number  - on mouse over "[Country]"
