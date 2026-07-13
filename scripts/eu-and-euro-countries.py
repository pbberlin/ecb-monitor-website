import sys
import json
import re
from pathlib import Path

# resolving parent directory to import lib.util
parentDir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parentDir))
from lib.util import stackTrace

# mapping of EU and Euro member states to their accession and leave dates
# serving as single source of truth for frontend and CSV generation
countryDates = {
    "Euro area (20 countries)":
                      {"euJoin": "1999-01-01", "euLeave": None, "euroJoin": "1999-01-01", "euroLeave": None},
    "Austria":        {"euJoin": "1995-01-01", "euLeave": None, "euroJoin": "1999-01-01", "euroLeave": None},
    "Belgium":        {"euJoin": "1958-01-01", "euLeave": None, "euroJoin": "1999-01-01", "euroLeave": None},
    "Bulgaria":       {"euJoin": "2007-01-01", "euLeave": None, "euroJoin": "2025-01-01", "euroLeave": None},
    "Croatia":        {"euJoin": "2013-07-01", "euLeave": None, "euroJoin": "2023-01-01", "euroLeave": None},
    "Cyprus":         {"euJoin": "2004-05-01", "euLeave": None, "euroJoin": "2008-01-01", "euroLeave": None},
    "Czech Republic": {"euJoin": "2004-05-01", "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Denmark":        {"euJoin": "1973-01-01", "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Estonia":        {"euJoin": "2004-05-01", "euLeave": None, "euroJoin": "2011-01-01", "euroLeave": None},
    "Finland":        {"euJoin": "1995-01-01", "euLeave": None, "euroJoin": "1999-01-01", "euroLeave": None},
    "France":         {"euJoin": "1958-01-01", "euLeave": None, "euroJoin": "1999-01-01", "euroLeave": None},
    "Germany":        {"euJoin": "1958-01-01", "euLeave": None, "euroJoin": "1999-01-01", "euroLeave": None},
    "Greece":         {"euJoin": "1981-01-01", "euLeave": None, "euroJoin": "2001-01-01", "euroLeave": None},
    "Hungary":        {"euJoin": "2004-05-01", "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Ireland":        {"euJoin": "1973-01-01", "euLeave": None, "euroJoin": "1999-01-01", "euroLeave": None},
    "Italy":          {"euJoin": "1958-01-01", "euLeave": None, "euroJoin": "1999-01-01", "euroLeave": None},
    "Latvia":         {"euJoin": "2004-05-01", "euLeave": None, "euroJoin": "2014-01-01", "euroLeave": None},
    "Lithuania":      {"euJoin": "2004-05-01", "euLeave": None, "euroJoin": "2015-01-01", "euroLeave": None},
    "Luxembourg":     {"euJoin": "1958-01-01", "euLeave": None, "euroJoin": "1999-01-01", "euroLeave": None},
    "Malta":          {"euJoin": "2004-05-01", "euLeave": None, "euroJoin": "2008-01-01", "euroLeave": None},
    "Netherlands":    {"euJoin": "1958-01-01", "euLeave": None, "euroJoin": "1999-01-01", "euroLeave": None},
    "Poland":         {"euJoin": "2004-05-01", "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Portugal":       {"euJoin": "1986-01-01", "euLeave": None, "euroJoin": "1999-01-01", "euroLeave": None},
    "Romania":        {"euJoin": "2007-01-01", "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Slovakia":       {"euJoin": "2004-05-01", "euLeave": None, "euroJoin": "2009-01-01", "euroLeave": None},
    "Slovenia":       {"euJoin": "2004-05-01", "euLeave": None, "euroJoin": "2007-01-01", "euroLeave": None},
    "Spain":          {"euJoin": "1986-01-01", "euLeave": None, "euroJoin": "1999-01-01", "euroLeave": None},
    "Sweden":         {"euJoin": "1995-01-01", "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "United Kingdom": {"euJoin": "1973-01-01", "euLeave": "2020-01-31", "euroJoin": None, "euroLeave": None},
    "Norway":         {"euJoin": None,         "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Switzerland":    {"euJoin": None,         "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Andorra":        {"euJoin": None,         "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Ukraine":        {"euJoin": None,         "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Moldova":        {"euJoin": None,         "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Belarus":        {"euJoin": None,         "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Bosnia and Herzegovina":
                      {"euJoin": None, "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Albania":        {"euJoin": None,         "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Montenegro":     {"euJoin": None,         "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Macedonia":      {"euJoin": None,         "euLeave": None, "euroJoin": None,         "euroLeave": None},
    "Serbia":         {"euJoin": None,         "euLeave": None, "euroJoin": None,         "euroLeave": None},
}

def isPreAccession(countryName, timeKey):
    # checking if the data point predates the country's accession date
    if countryName not in countryDates:
        return False

    dates = countryDates[countryName]
    if not dates["euJoin"]:
        return True

    accDate = dates["euJoin"]
    accYear = accDate[0:4]
    accMonth = accDate[0:7]

    if len(timeKey) == 4:
        if timeKey < accYear:
            return True
    elif len(timeKey) == 7:
        if timeKey < accMonth:
            return True

    return False

def extractJsonStringFromJs(jsText):
    # isolating the JSON payload from the JS variable declaration
    equalsIndex = jsText.find("=")
    if equalsIndex == -1:
        raise ValueError("Could not find '=' in JS file")

    braceIndex = jsText.find("{", equalsIndex)
    if braceIndex == -1:
        raise ValueError("Could not find '{' after '=' in JS file")

    lastBraceIndex = jsText.rfind("}")
    if lastBraceIndex == -1:
        raise ValueError("Could not find closing '}' in JS file")

    jsonText = jsText[braceIndex:lastBraceIndex + 1]
    varDeclaration = jsText[:braceIndex]
    return varDeclaration, jsonText

def detectOrientation(dataDict):
    keysList = list(dataDict.keys())
    if len(keysList) == 0:
        return "unknown"

    sampleKey = keysList[0]
    yearPattern = re.compile(r"^\d{4}(-\d{2})?$")
    if isinstance(sampleKey, str) and yearPattern.match(sampleKey):
        return "year_first"
    else:
        return "country_first"

def processJsFile(pth):
    try:
        jsText = pth.read_text(encoding="utf-8")
        varDeclaration, jsonText = extractJsonStringFromJs(jsText)
        dataDict = json.loads(jsonText)

        if not isinstance(dataDict, dict):
            return

        orientation = detectOrientation(dataDict)
        if orientation == "unknown":
            return

        maskCount = 0

        if orientation == "year_first":
            for idx1, yearKey in enumerate(dataDict):
                countryData = dataDict[yearKey]
                if not isinstance(countryData, dict):
                    continue
                for idx2, countryName in enumerate(countryData):
                    if isPreAccession(countryName, yearKey):
                        dataDict[yearKey][countryName] = None
                        maskCount += 1
        else:
            for idx1, countryName in enumerate(dataDict):
                yearData = dataDict[countryName]
                if not isinstance(yearData, dict):
                    continue
                for idx2, yearKey in enumerate(yearData):
                    if isPreAccession(countryName, yearKey):
                        dataDict[countryName][yearKey] = None
                        maskCount += 1

        if maskCount > 0:
            newJsonText = json.dumps(dataDict, indent=2)
            newJsText = f"{varDeclaration}{newJsonText};\n"
            pth.write_text(newJsText, encoding="utf-8")
            print(f"\tMasked {maskCount:4} values in {pth.name}")

    except Exception as exc:
        stackTrace(exc)
        print(f"Error processing {pth}")



def generateCountryJs(pth):
    # generating JS file to serve as single source of truth for frontend
    try:
        jsLines = []
        jsLines.append("// dynamically generated by eu-and-euro-countries.py")
        jsLines.append(f"const countryDates = {json.dumps(countryDates, indent=4)};")
        jsLines.append("")
        pth.write_text("\n".join(jsLines), encoding="utf-8")
        print(f"\tGenerated {pth.name}")
    except Exception as exc:
        stackTrace(exc)
        print(f"Error generating {pth}")


def main():
    dlDir = parentDir / "static" / "dl"

    generateCountryJs(dlDir / "eu-and-euro-countries.js")

    jsFilesList = []
    for idx1, pth in enumerate(sorted(dlDir.glob("*.js"))):
        # skipping council files as they do not contain economic time series
        if "council" in pth.name:
            continue
        jsFilesList.append(pth)

    for idx1, pth in enumerate(jsFilesList):
        if idx1 % 10 == 0:
            print(f"\t{idx1:3} of {pth.name} of jsFilesList")
        processJsFile(pth)

if __name__ == "__main__":
    main()