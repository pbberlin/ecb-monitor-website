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
            "de": "Guten Tag",
            "en": "Good day", 
        },
    },
    {
        "switch_language_hint": { 
            "de": "switch language",   # switched 
            "en": "Sprache wechseln", 
        },
    },
    {
        "switch_language_label": { 
            "de": "To  English version",  # switched
            "en": "Zur Deutschen Fassung", 
        },
    },
    {
        "app_title":    { 
            "de": "EZB-Transparenz-Monitor",
            "en": "ECB-Transparency-Monitor", 
        },
    },
    {
        "ameco_debt_to_gdp_label":    { 
            "de": "Staatsschulden in % BIP",
            "en": "Government debt in % GDP", 
        },
    },
    {
        "ameco_debt_to_gdp_desc":    { 
            "de": """
                <li>
                Gesamtstaatliche Bruttoschulden des Staates in % BIP
                </li>

                <li>
                Quelle: 
                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                        Europäische Kommission, AMECO Database, Variablen-Code: UDGG
                    </a>
                </li>
            """, 
            "en": """
                <li>
                General government gross debt in % GDP
                </li>


                <li>
                    Source: 

                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                        European Commission, AMECO Database, variable code: UDGG
                    </a>
                
                </li>
            """, 
        },
    },
    {
        "ameco_net_lending_label":    { 
            "de": "Haushaltssaldo in % BIP",
            "en": "Government balance in % GDP", 
        },
    },
    {
        "ameco_net_lending_desc":    { 
            "de": """
                <li>
                Gesamtstaatlicher Haushaltssaldo in % BIP
                </li>
                <li>
                Quelle: 
                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                    Europäische Kommission, AMECO Database, Variablen-Code: UBLG
                    </a>
                </li>
            """, 
            "en": """
                <li>
                General government balance in % GDP
                </li>
                <li>
                    Source: 
                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                    European Commission, AMECO Database, variable code: UBLG
                    </a>                
                </li>
            """, 
        },
    },
    {
        "ameco_total_expenditure_label":    { 
            "de": "Staatsquote in % BIP",
            "en": "Total expenditure in pct GDP", 
        },
    },
    {
        "ameco_total_expenditure_desc":    { 
            "de": """
            """, 
            "en": """
            """, 
        },
    },
    {
        "ameco_interest_expenditure_label":    { 
            "de": "Zinszahlungen in % Staatsausgaben",
            "en": "Interest expenditure in pct GDP", 
        },
    },
    {
        "ameco_interest_expenditure_desc":    { 
            "de": """
            """, 
            "en": """
            """, 
        },
    },
    {
        "eurostat_yields_10y_label":    { 
            "de": "Umlaufrendite 10-j. Staatsanleihen",
            "en": "Yields 10-year government bonds", 
        },
    },
    {
        "eurostat_yields_10y_desc":    { 
            "de": """
            """, 
            "en": """
            """, 
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
            "en": "Fiscal Landscape", 
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
            # print(f"{lg} {key:16} {val[:44]}")
            trlsByLg[lg][key] = val



def getCurrentLanguageAndI18n():
    curLg         = getattr(g, "currentLanguage", "de")
    switchLgCode  = getattr(g, "switchLgCode", "de")
    switchLgUrl   = getattr(g, "switchLgUrl", "de")

    #  arg.get does *not* contain POST values
    lg = request.args.get('lang')
    if (lg is None) or (lg == "") :
        pass
    else:
        curLg = lg

    curI18n = {}
    if curLg in trlsByLg:
        curI18n = trlsByLg[curLg]

    return AttrDict(curI18n), curLg, switchLgCode, switchLgUrl
