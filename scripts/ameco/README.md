AMECO

[main page](https://economy-finance.ec.europa.eu/economic-research-and-databases/economic-databases/ameco-database_en)


[download-csv](https://economy-finance.ec.europa.eu/economic-research-and-databases/economic-databases/ameco-database/download-annual-data-set-macro-economic-database-ameco_en)

    * AMECO - All [zipped CSV files](https://economy-finance.ec.europa.eu/document/download/fd885a67-e390-46fb-a6d0-bbc67d946ebf_en)
    * Redirects [here](https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip)

```bash

curl  https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip  -o tmp-ameco-all.zip
tar -xf .\tmp-ameco-all.zip AMECO18.CSV AMECO16.CSV



python  process-a-csv-to-subset.py

# CSV to JavaScript
python  process-b-csv-to-js.py

# CSV reformatting the decimal separator "."  to  "," - so that European Excel does at least show 
cd ..\..\\static\dl\
python jsToCSV.py



# files written to  .\static\dl\

```
