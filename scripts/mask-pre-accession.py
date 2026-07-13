import sys
import json
import re
from pathlib import Path

# resolving parent directory to import lib.util
parentDir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parentDir))
from lib.util import stackTrace

# mapping of EU member states to their accession dates
accessionDates = {
    "Austria": "1995-01-01",
    "Belgium": "1958-01-01",
    "Bulgaria": "2007-01-01",
    "Croatia": "2013-07-01",
    "Cyprus": "2004-05-01",
    "Czech Republic": "2004-05-01",
    "Denmark": "1973-01-01",
    "Estonia": "2004-05-01",
    "Finland": "1995-01-01",
    "France": "1958-01-01",
    "Germany": "1958-01-01",
    "Greece": "1981-01-01",
    "Hungary": "2004-05-01",
    "Ireland": "1973-01-01",
    "Italy": "1958-01-01",
    "Latvia": "2004-05-01",
    "Lithuania": "2004-05-01",
    "Luxembourg": "1958-01-01",
    "Malta": "2004-05-01",
    "Netherlands": "1958-01-01",
    "Poland": "2004-05-01",
    "Portugal": "1986-01-01",
    "Romania": "2007-01-01",
    "Slovakia": "2004-05-01",
    "Slovenia": "2004-05-01",
    "Spain": "1986-01-01",
    "Sweden": "1995-01-01",
    "United Kingdom": "1973-01-01"
}

def isPreAccession(countryName, timeKey):
    # checking if the data point predates the country's accession date
    # timeKey can be 'YYYY' (AMECO) or 'YYYY-MM' (Eurostat)
    if countryName not in accessionDates:
        return False
    
    accDate = accessionDates[countryName]
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


def main():
    dlDir = parentDir / "static" / "dl"
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