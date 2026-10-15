
https://ec.europa.eu/eurostat/databrowser/view/teimf050/default/table?lang=en

https://doi.org/10.2908/TEIMF050

```bash
curl "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/teimf050/?format=TSV&compressed=false" -o estat_teimf050.tsv

```

Monatlich; Aktualität: Letzer Monat
Name der Variable: 
ECB: Harmonised long-term interest rates for convergence assessment purposes

(percentages per annum; period averages; secondary market yields of government bonds with maturities of close to ten years)

teimf050

Eurostat: Long term government bond yields



## old - prc_hicp_manr

https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_manr/default/table?lang=en
downloadUrl = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_manr/?format=TSV&compressed=false"


## prc_hicp_minr

since 2026-01

configure download via https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_minr__custom_23226070/default/table


RCH_A  -  

[M]     - monthly
[RCH_A] - annual rate of change, representing percentage change in a reference month compared to same month of previous year (also called annual inflation)
[TOTAL] - Total ,  [CP01] - Food and non-alcoholic beverages
[Country Code]

M,RCH_A,CP01,CY
M,RCH_A,TOTAL,[country-code]
M,RCH_A,TOTAL,CY



configured subset
https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_minr__custom_23226070/default/table


https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/prc_hicp_minr/1.0/*.*.*.*?c[freq]=M&c[unit]=RCH_A&c[coicop18]=TOTAL&compress=false&format=tsv
