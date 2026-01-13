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
            "de": "switch language  (ALT+L)",     # reverse translation
            "en": "Sprache wechseln (ALT+L)",
        },
    },
    {
        "switch_language_label": {
            "de": "To English version",  # reverse translation
            "en": "Zur deutschen Fassung",
        },
    },
    # {
    #     "app_title":    {
    #         "de": "EZB-Transparenz-Monitor",
    #         "en": "ECB-Transparency-Monitor",
    #     },
    # },
    {
        "app_title":    {
            "de": "EZB-Monitor",
            "en": "ECB-Monitor",
        },
    },

    {
        "headline_ecb_council": {
            "de": "EZB-Rat",
            "en": "ECB Council",
        },
    },

    {
        "headline_ecb_monetary_policy": {
            "de": "EZB-Geldpolitik",
            "en": "ECB Monetary Policy",
        },
    },
    {
        "headline_fiscal_data":    {
            "de": "Fiskaldaten",
            "en": "Fiscal Landscape",
        },
    },
    {
        "headline_economic_data":    {
            "de": "Ökonomisches Umfeld",
            "en": "Economic Landscape",
        },
    },
    {
        "headline_science":    {
            "de": "Wissenschaft",
            "en": "Science",
        },
    },


    {
        "our_topics":    {
            "de": "Unsere <br> <b>Themen</b>",
            "en": "Our    <br> <b>Topics</b>",
        },
    },



    {
        "entire_euro_area":    {
            "de": "Durchschnitt\\nEurozone",
            "en": "Euro area\\naverage",
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
            "de": "Staatsausgaben in % BIP",
            "en": "Government expenditure in % GDP",
        },
    },
    {
        "ameco_total_expenditure_desc":    {
            "de": """
                <li>
                Gesamtstaatliche Ausgaben in % BIP
                </li>
                <li>
                Quelle:
                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                    Europäische Kommission, AMECO Database, Variablen-Code: UUTG
                    </a>
                </li>
            """,
            "en": """
                <li>
                General government expenditure in % GDP
                </li>
                <li>
                    Source:
                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                    European Commission, AMECO Database, variable code: UUTG
                    </a>
                </li>
            """,
        },
    },
    {
        "ameco_interest_expenditure_label":    {
            "de": "Zinszahlungen in % Staatsausgaben",
            "en": "Interest payments in % government expenditure",
        },
    },
    {
        "ameco_interest_expenditure_desc":    {
            "de": """
                <li>
                Gesamtstaatliche  Zinszahlungen in % Staatsausgaben
                </li>
                <li>
                Quelle:
                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                    Europäische Kommission, AMECO Database, Variablen-Code: UYIG/D.41
                    </a>
                </li>
            """,
            "en": """
                <li>
                General government interest payments in % government expenditure
                </li>
                <li>
                    Source:
                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                    European Commission, AMECO Database, variable code: UYIG/D.41
                    </a>
                </li>
            """,
        },
    },
    {
        "eurostat_yields_10y_label":    {
            "de": "Rendite Staatsanleihe 10 Jahre",
            "en": "Government bond yield 10 years",
        },
    },
    {
        "eurostat_yields_10y_desc":    {
            "de": """
                <li>
                Rendite Staatsanleihen des Zentralstaats auf dem Sekundärmarkt mit ungefährer Restlaufzeit von 10 Jahren
                </li>
                <li>
                Quelle:
                    <a href="https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/teimf050/?format=TSV&compressed=false">
                    Eurostat, online data code: teimf050
                    </a>
                </li>
            """,
            "en": """
                <li>
                Central government bond yield secondary market with residual maturity of around 10 years.
                </li>
                <li>
                    Source:
                    <a href="https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/teimf050/?format=TSV&compressed=false">
                    Source: Eurostat, online data code: teimf050
                    </a>
                </li>
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
        "career_education":    {
            "de": "Ausbildung, Berufserfahrung",
            "en": "Education, professional expertise",
        },
    },
    {
        "since":    {
            "de": "seit",
            "en": "since",
        },
    },
    {
        "president":    {
            "de": "Präsident",
            "en": "President",
        },
    },
    {
        "vice_president":    {
            "de": "Vizepräs.",
            "en": "Vice-Pres.",
        },
    },




]


trlsByLg = {}
for idx1, trlEntry in enumerate(trlsRaw):
    for key in trlEntry:
        if "-" in key:
            raise(f"key {key} contains '-' - we want underscore")
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
