* Warmup Request nötig

* Erste beide Schritte müssen mit echtem Browser erfolgen (Playwright)

* "Philip R Lane" - kein Punkt

* Lagarde ergänzt

* Eigennamen werden für Dateinamen gemappt auf einfache Buchstaben (ASCII), also Vujčić wird zu vujcic

* Bis zu 25 Reden - auch wenn's weit über die letzten drei Monate hinausgeht

* Einer hat keine Reden?

* Die plain text Versionen haben teilweise keine "Satzende" Trennungen mehr - bspw. Überschrift geht direkt in ersten Satz über. Siehe `example-html-to-text.py` for a fix.



##

```bash

cd /var/www/ecb-app/
source /var/www/ecb-app/.venv/bin/activate

# update playwright
playwright install

# execution right for playwright
chmod +x /var/www/ecb-app/.venv/lib/python3.11/site-packages/playwright/driver/node
chmod +x /var/www/ecb-app/.venv/lib/python3.11/site-packages/playwright/driver/*

python ./scripts/bis-speeches/crawl-01.py --input "./ecb-members-input.csv" --output "./ecb-members-urls.csv"   --headless true
python ./scripts/bis-speeches/crawl-02.py --input "./ecb-members-urls.csv"  --output "./ecb-members-links.csv"  --headless true  
# takes 20 min
python ./scripts/bis-speeches/crawl-03.py --input "./ecb-members-links.csv"
python ./scripts/bis-speeches/crawl-04.py

# sudo apt install tesseract-ocr
python ./scripts/bis-speeches/crawl-05-ocr.py


```
