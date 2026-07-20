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
        "section_home":    {
            "de": "Home",
            "en": "Home",
        },
    },
    {
        "back_home_hint": {
            # ⌫ or ⇦
            "de": "Zurück zur Hompage        ALT+ ⬅     oder     ⌫",
            "en": "Back home        ALT+ ⬅     or      ⌫",
        },
    },

    {
        "hp_claim_p1":    {
            "de": """
                Ein Forschungsprojekt des ZEW - Leibniz-Zentrums für Europäische Wirtschaftsforschung
                mit Unterstützung der <a style='display:inline; margin: 0;'   target='_blank' href='https://www.stiftung-geld-und-waehrung.de/stiftung-de'> Stiftung Geld und Währung </a>
            """,
            "en": """
                A research project of ZEW – Leibniz Centre for European Economic Research
                with support from the <a style='display:inline; margin: 0;'  target='_blank' href='https://www.stiftung-geld-und-waehrung.de/stiftung-de'> Monetary Stability Foundation  </a>
            """,
        },
    },
    {
        "hp_claim_p2":    {
            "de": """
                Der "EZB-Monitor" informiert aus der unabhängigen wissenschaftlichen Perspektive
                des ZEW über die EZB und ihre geldpolitischen Entscheidungen. Der Monitor bietet Zugriff auf wichtige ökonomische und fiskalische Daten zum aktuellen Umfeld der Geldpolitik.
            """,
            "en": """
                The ECB-Monitor provides background information on the ECB and its monetary policy decisions
                from the perspective of independent academic research
            """,
        },
    },
    {
        "hp_infobox":    {
            "de": """
                <p>
                    In jedem Quartal erfolgt die Publikation des EZB-Momentum-Indikators.
                    Dieser KI-gestützte Indikator gibt Auskunft über die Botschaft
                    aus den jüngsten Redebeiträgen von Mitgliedern des EZB-Rats.
                    Er dient als Frühindikator, ob die EZB eher in eine
                    expansive oder kontraktive Richtung in ihren geldpolitischen Entscheidungen neigt.
                </p>
                <p>
                    Der EZB-Transparenz-Monitor richtet sich an Akteure in den Medien,
                    der Finanzindustrie, der Politik und der interessierten Fachöffentlichkeit.
                </p>

            """,
            "en": """
                <p>
                    The ECB-Monitor provides the following content
                </p>

                <ul>
                    <li>
                        The quarterly ECB-ZEW-Momentum Indicator; this indicator presents a text-analytical score of the ECB Council's current monetary policy orientation, based on the most recent speeches by Council members
                    </li>

                    <li>
                        Individual scores for the monetary policy positions of all ECB Council members together with bio information.
                    </li>

                    <li>
                        Current analytics from ZEW experts.
                    </li>

                    <li>
                        Current data on the fiscal and economic environment, including data history for eurozone countries, with easy downloads.
                    </li>

                    <li>
                        Current new research insights on monetary policy from academic work.
                    </li>

                    <li>
                        The ECB-Monitor is intended for a broad audience, including the media, the financial industry, the public sector, and the general public, who are interested in independent background information on monetary policy.
                    </li>

                </ul>
            """,
        },
    },


    {
        "infobox_header":    {
            "de": "Kontext und Nutzerhilfe",
            "en": "Context and user help",
        },
    },
    {
        "infobox_header_homepage":    {
            "de": "Mehr Info",
            "en": "More info",
        },
    },


    {
        "headline_news": {
            "de": "Aktuell",
            "en": "News",
        },
    },

    {
        "ecb_quarterly_report_headline":    {
            "de": "EZB Monitor - Quartalsbericht",
            "en": "ECB-Monitor Quarterly Report – most recent issue",
        },
    },
    {
        "ecb_quarterly_report_hint":    {
            "de": "So hat sich das geldpolitische Momentum in den Reden des EZB-Rats über die letzten Monate verändert",
            "en": "This is how the monetary policy momentum in the speeches of the ECB Governing Council has changed over the past months.",
        },
    },

    {
        "ecb_quarterly_report_archive_headline":    {
            "de": "EZB Monitor - Quartalsbericht - frühere Ausgaben",
            "en": "ECB-Monitor Quarterly Report – past issues",
        },
    },
    {
        "ecb_quarterly_report_archive_hint":    {
            "de": "Frühere Quartalsberichte",
            "en": "Past quarterly reports",
        },
    },






    {
        "blog_special_analyses_headline":    {
            "de": "EZB Monitor - Spezialanalysen",
            "en": "ECB-Monitor - special analyses",
        },
    },
    {
        "blog_special_analyses_hint":    {
            "de": "Forschende und ECB-Watcher, die nicht für Notenbanken arbeiten, zu aktuellen geldpolitischen Fragestellungen.",
            "en": "Researchers and ECB watchers who do not work for central banks on current monetary policy issues.",
        },
    },




    #  insider blog template
    {
        "blog_policy_headline":    {
            "de": "EZB-Watching – der Kommentar",
            "en": "Recent expert assessments",
        },
    },




    {
        "headline_ecb_monetary_policy": {
            "de": "EZB Leitzinsen     & Termine",
            "en": "ECB Interest Rates & Calendar",
        },
    },
    {
        "section_ecb_monetary_policy": {
            "de": "Zinsen&shy;+Termine",
            "en": "Rates&shy;+Calendar",
        },
    },

    {
        "section_interest_rates": {
            "de": "Leitzinsen",
            "en": "Interest rates",
        },
    },
    {
        "section_calendar": {
            "de": "Sitzungskalender",
            "en": "Calendar",
        },
    },


    {
        "headline_fiscal_data":    {
            "de": "Fiskal&shy;daten",
            "en": "Fiscal Land&shy;scape",
        },
    },
    {
        "fiscal_data_infobox":    {
            "de": """
                <ul>
                    <li>...</li>
                </ul>
            """,
            "en": """
                <p>
                    The fiscal environment is important for the conduct of monetary policy.
                    The Maastricht Treaty aimed to ensure that public debt levels remained sustainable
                    in order to protect the ECB's effective independence.
                    This page provides essential information on the fiscal positions of eurozone countries over time.
                </p>
                <ul>
                    <li>
                        Using the slider, you can select a time period.
                    </li>
                    <li>
                        Press the play button to see how the respective variable changes over time.
                    </li>
                    <li>
                        Press the download button to get an Excel file containing the respective variable's data history for all eurozone countries.
                    </li>
                </ul>
            """,
        },
    },

    {
        "headline_economic_environment":    {
            "de": "Ökonomisches Umfeld",
            "en": "Economic Landscape",
        },
    },
    {
        "section_economic_environment":    {
            "de": "Ökon. Umfeld",
            "en": "Econ. Land&shy;scape",
        },
    },
    {
        "economic_environment_infobox":    {
            "de": """
                <ul>
                    <!--
                        ● ➡ ↪
                    -->
                    <li>Das wirtschaftliche Umfeld beeinflusst die Politik der EZB</li>
                    <ul>
                        <li> Schwaches   Wachstum ↪ geldpolitische Expansion</li>
                        <li> Starkes Wachstum ↪ geldpolitische Kontraktion gegen „überhitzende" Inflation</li>
                        <li> Positive Produktionslücke &nbsp; ↪  &nbsp; Kontraktion gegen „Überhitzung"</li>
                        <li> Inflation < 1 %   &nbsp; ↪  &nbsp; deflationäre Spirale ➡ Expansion</li>
                        <li> Inflation > 4 %   &nbsp; ↪  &nbsp; inflationäre Spirale ➡  Kontraktion</li>
                    </ul>
                </ul>
            """,
            "en": """
                    <!--
                        ● ➡ ↪
                    -->

                <p>
                    Monetary policy decisions reflect the economic environment.
                    Key variables that central banks consider are both the inflation rate and the growth rate.
                    Typically, central banks will opt for a more expansionary monetary policy
                    if inflation and economic growth are low, and a more restrictive policy if they are high.
                </p>
                <ul>
                    <li>
                        Using the slider, you can select a time period.
                    </li>
                    <li>
                        Press the play button to see how the respective variable changes over time.
                    </li>
                    <li>
                        Press the download button to get an Excel file containing the respective variable's data history for all eurozone countries.
                    </li>
                </ul>
            """,
        },
    },
    {
        "headline_science":    {
            "de": "Wissen&shy;schaft",
            "en": "Science",
        },
    },

    {
        "all_posts":    {
            "de": "Alle Beiträge",
            "en": "All posts",
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
        "debt_to_gdp_label":    {
            "de": "Staatsverschuldung",
            "en": "Government debt",
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
                <li>
                    This variable quantifies the total public debt of all government levels and social security relative to Gross Domestic Product.
                    The data for the current and next year are forecasts provided by the European Commission.
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
        "net_lending_label":    {
            "de": "Haushaltsdefizite",
            "en": "Budget deficits",
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
                <li>
                    This variable indicates whether the general government budget (relative to Gross Domestic Product)
                    is in surplus (a positive number) or in deficit (a negative number). The data for the current and
                    next year are forecasts provided by the European Commission.
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
                <li>
                    This variable indicates the size of the general government in terms of total government expenditure relative
                    to the Gross Domestic Product. The data for the current and next year are forecasts provided by the European Commission.
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
        "interest_expenditure_label":    {
            "de": "Schuldentragfähigkeit",
            "en": "Debt sustainability",
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
                <li>
                    This variable shows the share of interest payments on outstanding public debt in total government expenditure.
                    The data for the current and next year are forecasts provided by the European Commission.
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

                <li>
                    This variable provides information on borrowing costs for new government bonds.
                    It shows central government bond yields on the secondary market with a residual maturity of around 10 years.
                    Unlike the other fiscal variables which are reported on an annual basis, this variable is reported monthly.
                </li>

            """,
        },
    },
    {
        "abs_or_rel":    {
            "de": "Relativ zum Durchschnitt Eurozone",
            "en": "Relative to euro area average",
        },
    },
    {
        "abs_or_rel_help":    {
            "de": "Absolute Zahlen  - oder relativ zur Eurozone",
            "en": "Absolute numbers - or difference to euro area average",
        },
    },
    {
        "threshold_potential_growth":    {
            "de": "durchschn. Potenzialwachstum 1%",
            "en": "avg. growth potential of 1%",
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
    {
        "governor":    {
            "de": "EZB-Ratsmitglied, Präsident der nat. Zentralbank",
            "en": "Central bank governor, member ECB Governing Council",
        },
    },

    {
        "education":    {
            "de": "Ausbildung",
            "en": "Education",
        },
    },
    {
        "experience":    {
            "de": "Berufserfahrung",
            "en": "Experience",
        },
    },


    # economic environment
    # yearly
    # compute growth rate from ameco database (GDP-LEVELS)
    # formula: (GDP(T)/(GDP(T-1)-1)*100
    {
        "ameco_gdp_growth_label":    {
            "de": "BIP Wachstum (real) in %",
            "en": "GDP growth (real) in %",
        },
    },
    {
        "gdp_growth_label":    {
            "de": "Wachstum ",
            "en": "Growth",
        },
    },
    {
        "ameco_gdp_growth_desc":    {
            "de": """
                <li>
                Reales BIP-Wachstum in %
                </li>
                <li>
                    Quelle:
                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                        Europäische Kommission, AMECO Database, Variablen-Code: OVGD
                    </a>
                </li>
            """,
            "en": """
                <li>
                    Real GDP growth in %
                </li>
                <li>
                    Source:
                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                        European Commission, AMECO Database, variable code: OVGD
                    </a>
                </li>
                <li>
                    This variable shows the real (i.e. inflation-adjusted) annual growth rate
                    of the Gross Domestic Product. The data for the current and next year are forecasts
                    provided by the European Commission.
                </li>
            """,
        },
    },
    {
        "ameco_output_gap_label":    {
            "de": "Outputlücke in % Potenzial-BIP",
            "en": "Output gap in % of potential GDP",
        },
    },
    {
        "output_gap_label":    {
            "de": "Konjunktur",
            "en": "Business cycle",
        },
    },
    {
        "ameco_output_gap_desc":    {
            "de": """
                <li>
                Outputlücke: Lücke zwischen tatsächlichem und potenziellem BIP in % des potenziellen BIP
                </li>
                <li>
                    Quelle:
                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                        Europäische Kommission, AMECO Database, Variablen-Code: AVGDGP
                    </a>
                </li>
            """,
            "en": """
                <li>
                Output gap: gap between actual and potential GDP in % of potential GDP
                </li>
                <li>
                    Source:
                    <a href="https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip">
                    European Commission, AMECO Database, variable code: AVGDGP
                    </a>
                </li>
                <li>
                    This variable shows the difference between actual and the potential Gross Domestic Product.
                    A positive number indicates a strong economic situation,
                    as the actual economic activity is above the level that can be sustained in the long term.
                    Conversely, a negative number indicates a weak economic situation,
                    as economic activity is below what is possible given the available production factors.
                    The data for the current and next year are forecasts provided by the European Commission.
                </li>

            """,
        },
    },


    # inflation, monthly
    {
        "eurostat_hicp_label":    {
            "de": "HVPI-Inflation in %",
            "en": "HICP inflation in %",
        },
    },
    {
        "hicp_label":    {
            "de": "Inflation",
            "en": "Inflation",
        },
    },
    {
        "eurostat_hicp_desc":    {
            "de": """
                <li>
                Inflation (Harmonisierter Verbraucherpreisindex) in % zum Vorjahresmonat
                </li>
                <li>
                Quelle:
                    <a https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_manr/default/table?lang=en&category=prc.prc_hicp">
                    Eurostat, Variablen-Code: prc_hicp_manr, CP00 - Gesamt-HVPI
                    </a>
                </li>
            """,
            "en": """
                <li>
                Inflation (Harmonised Index of Consumer Prices) in % relative to same month of previous year
                </li>
                <li>
                    Source:
                   <a https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_manr/default/table?lang=en&category=prc.prc_hicp">
                    Eurostat, Variablen-Code: prc_hicp_manr, CP00 - All-items HICP
                    </a>
                </li>
                <li>
                    This variable shows the inflation rate according to the "Harmonised Index of Consumer Prices" (HICP).
                    The HICP inflation is the most prominent variable considered by the ECB Council since the ECB's primary
                    objective – "inflation of 2% over the medium term" – refers to the HICP.
                    The data for the current and next year are forecasts provided by the European Commission.
                </li>
            """,
        },
    },



    {
        "section_ecb_council": {
            "de": "EZB-Rat Position",
            "en": "ECB Council Stance",
        },
    },
    {
        "headline_ecb_council": {
            "de": "EZB-Rat",
            "en": "ECB Council",
        },
    },
    {
        "ecb_council_label": {
            "de": "EZB-Rat - Geographie",
            "en": "ECB Council dove-hawk positions – individuals' total history since appointment",
        },
    },
    {
        "ecb_council_section": {
            "de": "Nach EZB Ratsmitgliedern",
            "en": "By ECB Council individuals",
        },
    },
    {
        "ecb_council_section_subtitle": {
            "de": "(alle Reden)",
            "en": "(full history of speeches)",
        },
    },
    {
        "ecb_council_desc":    {
            "de": """ EZB-Rat ...""",
            "en": """ ECB Council ...""",
        },
    },
    {
        "ecb_council_infobox":    {
            "de": """
                <ul>
                    <li>Taube-Falke KI Score
                        <ul>
                            <li>Sammlung aller offiziellen Äußerungen des Ratsmitglieds</li>
                            <li>Evaluation mittels LLM hinsichtlich expansiver oder restriktiver Fiskalpolitik</li>
                            <li>Abbildung auf Zahlenbereich -1 (dovish) ... +1 (hawkish)</li>
                            <li>Siehe <a href=#>Wissenschaftliche Veröffentlichung</a>  </li>
                        </ul>
                    </li>
                    <li>Links: Sechs <i>überregionale</i> EZB-Mitglieder in Frankfurt</li>
                    <li>Landkarte: 20 nationale Zentralbankpräsidenten
                        <ul>
                            <li>Maus übers Land ziehen für Details</li>
                        </ul>
                    </li>
                    <li>Malta und Zypern sind annähernd vollwertige Ratsmitglieder</li>

                </ul>
            """,
            "en": """
                <p>
                    The map shows the hawkishness score of each ECB Council member.
                </p>

                <p>
                    It also provides biographical information on each member.
                </p>

                <p>
                    The hawkishness scores on the map are calculated using the full history of the individuals' speeches since their appointment to the ECB Council. The hawkishness scores for each speaker are the average over the hawkishness scores of all speeches held by this person while being a member of the ECB Council.
                </p>

                <p>
                    Due to this method of calculation, differences in scores are influenced by the monetary policy environment during an individual's time on the Council.
                </p>

                <p>
                    Hover over the map to view the names and biographical information of the individual members of the ECB Council.
                </p>



            """,
        },
    },


    {
        "council_by_6weeks_section": {
            "de": "Timeline",
            "en": "Timeline ECB-ZEW-Momentum Indicator",
        },
    },
    {
        "council_by_6weeks_section_subtitle": {
            "de": "(Reden je 6 Wochen)",
            # "en": "(speeches last six weeks)",
            "en": "(speeches per six weeks)",
        },
    },
    {
        "headline_council_by_6weeks": {
            "de": "EZB-Rat insgesamt - Taube-Falke Position über die Zeit ",
            # "en": "Timeline ECB-ZEW-Momentum Indicator (speeches last six weeks)",
            "en": "ECB-ZEW-Momentum Indicator and ECB deposit rate over time",
        },
    },
    {
        "council_by_6weeks_desc":    {
            "de": "Leitzins Entscheidungen folgen der Dovish-Hawkish Einschätzung der vorangegangenen Kommunikation. Plausibel. Kausalbeziehung nicht beweisbar.",
            # "en": "Rate settings follows Dovish-Hawkish score. Plausible, but causal relation cannot be proved.",
            "en": "ECB-ZEW Momentum Indicator and ECB deposit rate over time",
        },
    },
    {
        "council_by_6weeks_chart_series":    {
            "de": "ECB-ZEW Momentum Indikator",
            "en": "ECB-ZEW Momentum Indicator",
        },
    },
    {
        "council_by_6weeks_infobox":    {
            "de": """
                <ul>
                    <!--
                        ● ➡ ↪
                    -->
                    <li>Dovish-Hawkish Einschätzung der Ratsmitglieder per sechs Wochen</li>
                    <li>EZB Zinssätze</li>
                </ul>
            """,
            "en": """
                <p>
                    The graph shows the ECB-ZEW Momentum Indicator alongside the ECB deposit rate.
                </p>

                <p>
                    The deposit rate is the key rate among central bank rates, as determined by the ECB.
                </p>

                <p>
                    The ECB-ZEW Momentum Indicator provides an average hawkishness score based on speeches given by all ECB Council members over the last six weeks.
                </p>

                <p>
                    The indicator thus provides current information on the monetary policy stance revealed in the decision-makers' speeches.
                </p>

                <p>
                    For more information on the methodology behind the ECB-ZEW-Momentum Indicator, please refer to the Method Paper.
                </p>

            """,
        },
    },


    {
        "barometer_section": {
            "de": "Nach Ländern",
            "en": "Majorities ECB Council",
        },
    },
    {
        "barometer_section_subtitle": {
            "de": "(Reden über ein Jahr)",
            # "en": "(speeches over one year)",
            "en": "(speeches per year)",
        },
    },

    {
        "headline_council_barometer": {
            "de": "EZB-Rat Taube-Falke Positionen - Länder und Median",
            "en": "ECB Council dove-hawk positions one year – individuals and median",
        },
    },
    {
        "council_barometer_desc": {
            "de": "Position der Ratsmitglieder  im jeweiligen Jahr. Die Entscheidungen eines Gremiums konvergieren zur Median-Position.  ",
            "en": "Position of  council members per year. Council decisions converge around the median position.",
        },
    },
    {
        # attention: must contain html span element - being updated via JavaScript
        "council_barometer_chart_label": {
        "de": """
                Zeiger:  Median-Position des Gremiums:  &nbsp; <span id="medianVal" ></span>         <br>
                Die Kreise zeigen die Position der Länder.              <br>
                Maus-Over, um den Vertreter des Landes zu sehen
            """,
        "en": """
                Needle shows the median score in the Council:  &nbsp;  <span id="medianVal" ></span> <br>


                The circles show the scores of the individual members of the ECB Council. <br>
                "B" means board member.   <br>
                Hover over circles to see the individual representative of the country.   <br>
                For the current year, scores are calculated based on speeches given over the last 12 months. <br>
                For previous years, they are based on speeches given in the respective calendar year.   <br>
                Values are missing for individuals for whom no speeches exist.   <br>


            """,
        },
    },
    {
        "council_barometer_infobox":    {
            "de": """
                <ul>
                    <!--
                        ● ➡ ↪
                    -->
                    <li>Die Entscheidungen des Gremiums orientieren sich am Median der Ratsmitglieder</li>
                </ul>
            """,
            "en": """

                <p>
                    The graph shows the hawkishness score for each member of the ECB Council, alongside the median score.
                </p>

                <p>

                    The median score divides individuals into two equal groups, one more hawkish and one less.
                </p>

                <p>
                    Thus, the graph conveys an impression of both the majority position and the variance of views in the ECB Council for each year.
                </p>

                <ul>
                    <!--
                        ● ➡ ↪
                    -->

                </ul>

            """,
        },
    },





    {
        "headline_science_news": {
            "de": "Neues aus der Forschung",
            "en": "News from academia",
        },
    },

    {
        "headline_imprint": {
            "de": "Impressum, Team",
            "en": "Imprint, team",
        },
    },
    {
        "headline_data_protection": {
            "de": "Datenschutz",
            "en": "Data protection",
        },
    },
    {
        "headline_image_licenses": {
            "de": "Bildnachweis",
            "en": "Image licence",
        },
    },


]


trlsByLg = {}
for idx1, trlEntry in enumerate(trlsRaw):
    for key in trlEntry:
        if "-" in key:
            raise Exception(f"key {key} contains '-' - we want underscore")
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
