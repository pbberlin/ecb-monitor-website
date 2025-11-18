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
