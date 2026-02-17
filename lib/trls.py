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
                mit Unterstützung der Stiftung Geld und Währung
            """,
            "en": """
                A research project of ZEW – Leibniz Centre for European Economic Research
                with support from the Foundation for Money and Currency
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
                "ECB Monitor" provides information on the ECB and its monetary policy decisions
                from the independent academic perspective of ZEW.
                It offers key economic and fiscal data on the current monetary policy environment.
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
                <!-- todo  fhe: english translation-->
            """,
        },
    },


    {
        "infobox_header":    {
            "de": "Interpretationshilfe",
            "en": "Interpretation assistance",
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
        "ecb_momentum_report_headline":    {
            # "de": "EZB-ZEW-Momentum-Indikator –  Quartals-Bericht",
            # "en": "ECB-ZEW-Momentum indicator – quartely report",
            "de": "EZB-ZEW-Momentum-Indikator",
            "en": "ECB-ZEW-Momentum indicator",
        },
    },
    {
        "ecb_momentum_report_hint":    {
            "de": "So hat sich das geldpolitische Momentum in den Reden des EZB-Rats über die letzten Monate verändert",
            "en": "This is how the monetary policy momentum in the speeches of the ECB Governing Council has changed over the past months.",
        },
    },
    {
        "ecb_watching_hint":    {
            "de": "Forschende und ECB-Watcher, die nicht für Notenbanken arbeiten, zu aktuellen geldpolitischen Fragestellungen.",
            "en": "Researchers and ECB watchers who do not work for central banks on current monetary policy issues.",
        },
    },


    {
        "blog_policy_headline":    {
            "de": "ECB-Watching – der Kommentar",
            "en": "ECB-Watching – commentary",
        },
    },


    {
        "headline_ecb_monetary_policy": {
            # "de": "EZB-Geldpolitik",
            # "en": "ECB Monetary Policy",
            "de": "EZB Leitzinsen     & Termine",
            "en": "ECB Interest Rates & Calendar",
        },
    },
    {
        "section_interest_rates": {
            "de": "Leitzinsen",
            "en": "Interest Rates",
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
            "de": "Fiskaldaten",
            "en": "Fiscal Landscape",
        },
    },
    {
        "headline_economic_environment":    {
            "de": "Ökonomisches Umfeld",
            "en": "Economic Landscape",
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
                        <li> Starkes Wachstum ↪ geldpolitische Kontraktion gegen „überhitzende“ Inflation</li>
                        <li> Positive Produktionslücke &nbsp; ↪  &nbsp; Kontraktion gegen „Überhitzung“</li>
                        <li> Inflation < 1 %   &nbsp; ↪  &nbsp; deflationäre Spirale ➡ Expansion</li>
                        <li> Inflation > 4 %   &nbsp; ↪  &nbsp; inflationäre Spirale ➡  Kontraktion</li>
                    </ul>
                </ul>
            """,
            "en": """
                <ul>
                    <!--
                        ● ➡ ↪
                    -->
                    <li>The economic environment influences ECB policy</li>
                    <ul>
                        <li> Weak   growth ↪ monetary expansion</li>
                        <li> Strong growth ↪ monetary contraction against 'overheating' inflation</li>
                        <li> Positive output gap &nbsp; ↪  &nbsp; contraction against 'overheating'</li>
                        <li> Inflation < 1 pct   &nbsp; ↪  &nbsp; deflationary spiral ➡ expansion</li>
                        <li> Inflation > 4 pct   &nbsp; ↪  &nbsp; inflationary spiral ➡  contraction</li>
                    </ul>

                    
                </ul>
            """,
        },
    },
    {
        "headline_science":    {
            "de": "Wissenschaft",
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
            """,
        },
    },



    {
        "section_ecb_council": {
            "de": "EZB-Rat",
            "en": "ECB Council",
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
            "de": "Biographisches der Mitglieder",
            "en": "Council members bio",
        },
    },
    {
        "ecb_council_section": {
            "de": "Biographisches der Mitglieder",
            "en": "Council members bio",
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
                    <li>Hawk-dove KI Score
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
                <ul>
                    <li>Hawk-dove AI Score
                        <ul>
                            <li>Collection of all official statements by the council member</li>
                            <li>Evaluation using an LLM regarding expansionary or restrictive fiscal policy</li>
                            <li>Mapped to a numerical range of -1 (dovish) ... +1 (hawkish)</li>
                            <li>See <a href=#>Scientific publication</a></li>
                        </ul>
                    </li>
                   <li>Left: Six <i>supra-national</i>  ECB board members in Frankfurt/Germany</li>
                   <li>Geo map: 20 national central bank presidents
                        <ul>
                           <li>Mouse over for details</li>
                        </ul>
                    </li>
                    <li>Malta and Cyprus are mostly full members</li>
                    <li>Liechtenstein, Malta and Cyprus have been sized up for better mouse navigation</li>


                    <li>Discuss: Tenure ending-starting same year </li>
                    <li>Discuss: Dove-Hawk-Score for all years vs <i>up to selected</i> yr </li>
                    <li>Todo:    Mouse over - also over the numbers - Malta/Cyprus: rect </li>

                </ul>
            """,
        },
    },


    {
        "council_by_6weeks_section": {
            "de": "Hawk-dove Position",
            "en": "Hawk-dove score",
        },
    },
    {
        "headline_council_by_6weeks": {
            "de": "Hawk-dove Position für den gesamten EZB-Rat",
            "en": "Hawk-dove score    for the entire ECB-Council",
        },
    },
    {
        "council_by_6weeks_desc":    {
            "de": "Leitzins Entscheidungen folgen der Hawkish-Dovish Einschätzung der vorangegangenen Kommunikation. Plausibel. Kausalbeziehung nicht beweisbar.",
            "en": "Rate settings follows Hawkish-Dovish score. Plausible, but causal relation cannot be proved.",
        },
    },
    {
        "council_by_6weeks_infobox":    {
            "de": """
                <ul>
                    <!--
                        ● ➡ ↪
                    -->
                    <li>Dovish-hawkish Einschätzung der Ratsmitglieder per sechs Wochen</li>
                    <li>EZB Zinssätze</li>
                </ul>
            """,
            "en": """
                <ul>
                    <!--
                        ● ➡ ↪
                    -->
                    <li>Dovish-hawkish stance every 6-week period</li>
                    <li>ECB interest rates</li>
                </ul>
            """,
        },
    },


    {
        "tempomat_section": {
            # "de": "Mehrheitsverhältnisse EZB-Rat",
            # "en": "Majorities ECB-Council",
            "de": "Mitlieder   Positionen",
            "en": "Council member  positions",
        },
    },
    {
        "headline_council_tempomat": {
            "de": "Falke-Taube-Positionen der EZB Ratsmitglieder und Median Position",
            "en": "Hawk-dove positions of ECB Council members and median position",
        },
    },
    {
        "council_tempomat_desc": {
            "de": "Position der Ratsmitglieder  im jeweiligen Jahr. Die Entscheidungen eines Gremiums konvergieren zur Median-Position.  ",
            "en": "Position of  council members per year. Council decisions converge around the median position.",
        },
    },
    {
        "council_tempomat_chart_label": {
            "de": "Zeiger zeigt die Ratsmitglieder auf Median-Position. <br>Median des Gremiums   ",
            "en": "Needle points to Median council members. <br> Median panel position ",
        },
    },
    {
        "council_tempomat_infobox":    {
            "de": """
                <ul>
                    <!--
                        ● ➡ ↪
                    -->
                    <li>Die Entscheidungen des Gremiums orientieren sich am Median der Ratsmitglieder</li>
                </ul>
            """,
            "en": """
                <ul>
                    <!--
                        ● ➡ ↪
                    -->
                    <li>Panel decisions hinge around the median council member(s)</li>

                    <li>Exchange blue-red direction</li> 
                        <ul>
                            <li>Also switch numbers scale -1 is hawkish, +1 is dovish</li>
                            <li>Change color legend also in council members bio, dovish-hawkish for entire council. </li>
                            <li>Need the countries in the Pickle file</li>
                        </ul>
                    

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
            "en": "Imprint, Team",
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
            "en": "Image Licence Info",
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
