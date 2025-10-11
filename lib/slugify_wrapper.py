from unidecode import unidecode
from slugify   import slugify as libSlugify # alias in order prevent accidental importing 

import re



def transliterateUmlaute(text):
    replacements = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
        'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue',
        'ß': 'ss',
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text



def normalizeAcronymDots(text: str) -> str:
    # Replace patterns like S.C. or S.A. with Sc or SA
    # or or S.L.R. with "abc" or "SLR"
    def replaceAcronym(match):
        acronym = match.group(0)
        return acronym.replace('.', '')

    return re.sub(r'\b(?:[A-Za-z]\.){1,}[A-Za-z]?\b', replaceAcronym, text)



# short for "transliterate" - "slugify"
def tlsl(s: str):
    s = transliterateUmlaute(s)
    s = unidecode(s)              # remove accents
    s = normalizeAcronymDots(s)
    s = libSlugify(s)
    return s



if __name__ == "__main__":

    text = "Crème brûlée, déjà vu, façade, München. Schröder, Straße, Łódź"

    text = transliterateUmlaute(text)
    text = unidecode(text)  # Remove accents

    print(text)

    slug = libSlugify(text)

    print(slug)
