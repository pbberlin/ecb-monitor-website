from   flask import g
from   flask import request 


# to have       {{i18n.hello}}  instead of       {{i18n["hello"]}}
class AttrDict(dict):
    def __getattr__(self, key):
        try:
            if key in self:
                return self[key]
            else:
                return f"? trl '{key}'"
        except Exception as ex:
            print(ex)
            raise




trlsRaw = [
    {
        "good_day": { 
            "en": "Good day", 
            "de": "Guten Tag",
        },
    },
    {
        "app_title":    { 
            "de": "EZB-Transparenz-Monitor",
            "en": "ECB-Transparency-Monitor", 
        },
    },
    {
        "public_debt_in_percent_gdp":    { 
            "de": "Öffentliche Schulden in % BIP",
            "en": "Public debt in pct GDP", 
        },
    },
    {
        "public_debt_in_percent_gdp_desc":    { 
            "de": """
                <li>
                Allgemeine konsolidierte Bruttoschulden des Staates
                </li>

                <li>
                Prozentsatz des BIP zu aktuellen Preisen
                </li>

                <li>
                Verfahren bei übermäßigem Defizit, basierend auf ESA 2010
                </li>

                <li>
                Originalquelle:   
                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                        Ameco, Code UDGG
                    </a>
                </li>
            """, 
            "en": """
                <li>
                General government consolidated gross debt
                </li>

                <li>
                Percentage of GDP at current prices
                </li>

                <li>
                Excessive deficit procedure, based on ESA 2010
                </li>

                <li>
                    Original source: 

                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                        Ameco, Code UDGG
                    </a>
                
                </li>
            """, 
        },
    },
    {
        "net_lending_in_percent_gdp":    { 
            "de": "Nettokreditaufnahme % BIP",
            "en": "Net lending in pct GDP", 
        },
    },
    {
        "total_expenditure_in_percent_gdp":    { 
            "de": "Staatsquote in % BIP",
            "en": "Total expenditure in pct GDP", 
        },
    },
    {
        "interest_expenditure":    { 
            "de": "Zinszahlungen in % Staatsausgaben",
            "en": "Interest expenditure in pct GDP", 
        },
    },
    {
        "yields_10y":    { 
            "de": "Umlaufrendite 10-j. Staatsanleihen",
            "en": "Yields 10-year government bond", 
        },
    },
    {
        "download_data":    { 
            "de": "Daten herunterladen",
            "en": "Download data", 
        },
    },
    {
        "download_data_help":    { 
            "de": "Europäische CSV Datei, Semikolon delimited, Dezimal-Trennzeichen: Komma, UTF-8",
            "en": "European CSV, semikolon delimited, decimal separator: comma, UTF-8", 
        },
    },
    {
        "color_saturation":    { 
            "de": "Farbsättigung",
            "en": "Color saturation", 
        },
    },
    {
        "headline_fiscal_data":    { 
            "de": "Fiskaldaten",
            "en": "Fiscal Data", 
        },
    },
]


trlsByLg = {}
for idx1, trlEntry in enumerate(trlsRaw):
    for key in trlEntry:
        translations = trlEntry[key]
        for lg in translations:
            val = translations[lg]
            if lg not in trlsByLg:
                trlsByLg[lg] = {}
            trlsByLg[lg][key] = val



def getCurrentLanguageAndI18n():
    # curLg = getattr(g, "currentLanguage", "en")
    curLg = getattr(g, "currentLanguage", "de")

    #  arg.get does *not* contain POST values
    lg = request.args.get('lang')
    if (lg is None) or (lg == "") :
        pass
    else:
        curLg = lg

    curI18n = {}
    if curLg in trlsByLg:
        curI18n = trlsByLg[curLg]

    return curLg, AttrDict(curI18n)
