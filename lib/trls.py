from   flask import g


# to have       {{i18n.hello}}  instead of       {{i18n["hello"]}}
class AttrDict(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except Exception as ex:
            print(ex)
            raise




trlsRaw = [
    {
        "app_title":    { 
            "en": "ECB-Transparency-Monitor", 
            "de": "EZB-Transparenz-Monitor",
        },
    },
    {
        "hello":    { "en": "hello", "de": "Hallo" }
    },
    {
        "good_day": { "en": "Good day", "de": "Guten tag" }
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

    curI18n = {}
    if curLg in trlsByLg:
        curI18n = trlsByLg[curLg]

    return curLg, AttrDict(curI18n)
