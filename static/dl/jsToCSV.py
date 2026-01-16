#!/usr/bin/env python3

# replaces obsolete-reformat-csv-to-comma.py

import sys
import json
import csv
import re
from pathlib import Path



# importing from ../../lib/trls.py
parentDir = Path(__file__).resolve().parent.parent.parent
libPath = parentDir / "lib"
sys.path.insert(0, str(libPath))
from trls import trlsByLg


def debugPrintNestedDict(myDict, maxLevel=3, maxItemsPerLevel=3, indentLevel=1):

    indentText = "\t" + "  " * indentLevel

    if not isinstance(myDict, dict):
        print(f"{indentText}{myDict}")
        return

    sizeMsg = f"{indentText}dict of size {len(myDict)}"
    print(f"{indentText}dict of size {len(myDict)}")

    for idx1, key1 in enumerate(myDict):
        if idx1 >= maxItemsPerLevel:
            break

        if idx1 == 0:
            print(f"{indentText}\tkey: {key1} - {sizeMsg}")
        else:
            print(f"{indentText}\tkey: {key1}")

        value1 = myDict[key1]

        if isinstance(value1, dict):
            debugPrintNestedDict(
                value1,
                maxLevel=maxLevel - 1,
                maxItemsPerLevel=maxItemsPerLevel,
                indentLevel=indentLevel + 2
            )
        else:
            try:
                formattedValue = f"{float(value1):8.4f}"
            except Exception as ex:
                print(f"{indentText}\t\tException while formatting value: {ex}")
                formattedValue = str(value1)

            print(f"{indentText}\t\t{formattedValue}")


def formatValueForCsv(value):
    if value is None:
        return ""
    valueText = str(value)
    valueText = valueText.replace(".", ",")
    return valueText


def extractJsonStringFromJs(jsText):
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
    return jsonText


def detectOrientation(dataDict):
    keysList = list(dataDict.keys())
    if len(keysList) == 0:
        raise ValueError("Top-level dictionary has no keys")

    sampleKey = keysList[0]

    yearPattern = re.compile(r"^\d{4}(-\d{2})?$")
    if isinstance(sampleKey, str) and yearPattern.match(sampleKey):
        return "year_first"
    else:
        return "country_first"


def buildCountryYearStructure(dataDict):

    orientation = detectOrientation(dataDict)

    countryToYearToValue = {}
    yearKeysSet = set()

    if orientation == "year_first":
        for yearKey, countryDict in dataDict.items():

            if isinstance(yearKey, str) and yearKey.startswith("mapping"):
                continue

            yearKeysSet.add(yearKey)

            if not isinstance(countryDict, dict):
                continue

            for countryName, value in countryDict.items():
                if isinstance(countryName, str) and countryName.startswith("mapping"):
                    continue

                if countryName not in countryToYearToValue:
                    countryToYearToValue[countryName] = {}

                countryToYearToValue[countryName][yearKey] = value

    else:
        for countryName, yearDict in dataDict.items():
            if isinstance(countryName, str) and countryName.startswith("mapping"):
                continue

            if not isinstance(yearDict, dict):
                continue

            if countryName not in countryToYearToValue:
                countryToYearToValue[countryName] = {}

            for yearKey, value in yearDict.items():
                yearKeysSet.add(yearKey)
                countryToYearToValue[countryName][yearKey] = value

    return countryToYearToValue, yearKeysSet


def cleanseForCsv(txt):

    lines    = txt.splitlines()
    cleansed = []

    tagRe = re.compile(r"^\s*<[^>]+>\s*$")

    for idx1, line in enumerate(lines):

        line = line.strip()
        if line == "":
            continue
        if tagRe.match(line) is not None:
            continue
        cleansed.append(line)

    resultText = "\n".join(cleansed)
    return resultText



def appendAfterLastCol(csvFilePath, row):
    """ append the bibliography source after the last column """
    key = f"{csvFilePath.stem}_desc"
    print(f"\tsearching for key -{key}-  in  ../lib/trls.py.trlsByLg")
    val = ""
    if key in trlsByLg["en"]:
        val = trlsByLg["en"][key]
        print(f"\tfound key -{key}-  {val}")
        val = cleanseForCsv(val)

    # csvWriter.writerow([f"todo - {csvFilePath.stem}_desc from ../lib/trls.py.trlsRaw"])
    # csvWriter.writerow([val])
    row.append(val)
    return row



def writeCsvForJsFile(jsFilePath, dbg=False):

    try:
        jsText = jsFilePath.read_text(encoding="utf-8")
    except Exception as ex:
        print(f"Error reading file '{jsFilePath}': {ex}")
        return

    try:
        jsonText = extractJsonStringFromJs(jsText)
    except Exception as ex:
        print(f"Error extracting JSON from '{jsFilePath}': {ex}")
        return

    try:
        dataDict = json.loads(jsonText)
        if type(dataDict) is not dict:
            # ecb-council-by-function.js
            print(f"skipping type {type(dataDict)} - '{jsFilePath}'")
            return
        if dbg:
            debugPrintNestedDict(dataDict)

    except Exception as ex:
        print(f"Error parsing JSON in '{jsFilePath}': {ex}")
        return

    try:
        countryToYearToValue, yearKeysSet = buildCountryYearStructure(dataDict)
        if dbg:
            debugPrintNestedDict(countryToYearToValue)
    except Exception as ex:
        print(f"Error building country/year structure for '{jsFilePath}': {ex}")
        return

    sortedYearKeysList = sorted(list(yearKeysSet))

    csvHeader = []
    csvHeader.append("Country")

    for idx1, yearKey in enumerate(sortedYearKeysList):
        csvHeader.append(yearKey)

    csvFilePath = jsFilePath.with_suffix(".csv")

    try:
        with csvFilePath.open("w", encoding="utf-8", newline="") as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=";")

            csvWriter.writerow(csvHeader)

            sortedCountriesList = sorted(list(countryToYearToValue.keys()))

            for idx1, countryName in enumerate(sortedCountriesList):
                row = []
                row.append(countryName)

                yearToValueDict = countryToYearToValue[countryName]

                for idx2, yearKey in enumerate(sortedYearKeysList):
                    if yearKey in yearToValueDict:
                        value = yearToValueDict[yearKey]
                        formattedValue = formatValueForCsv(value)
                        row.append(formattedValue)
                    else:
                        row.append("")

                if idx1 == 0:
                    row = appendAfterLastCol(csvFilePath, row)

                csvWriter.writerow(row)


        print(f"\tWrote CSV: {csvFilePath}")

    except Exception as ex:
        print(f"Error writing CSV for '{jsFilePath}': {ex}")


def processDirectory(inputDirPath):

    inputDirPath = Path(inputDirPath)

    if not inputDirPath.is_dir():
        print(f"Not a directory: {inputDirPath}")
        return

    jsFilesList = []
    for idx1, jsPath in enumerate(sorted(inputDirPath.glob("*.js"))):
        print(f"\t{idx1:2} adding: {jsPath}")
        jsFilesList.append(jsPath)

    if len(jsFilesList) == 0:
        print(f"No .js files found in directory: {inputDirPath}")
        return

    for idx1, jsFilePath in enumerate(jsFilesList):
        print(f"\tprocessing JS file: {jsFilePath}")
        writeCsvForJsFile(jsFilePath, idx1<2)


def main():
    if len(sys.argv) > 1:
        inputDirArg = sys.argv[1]
    else:
        inputDirArg = "."

    processDirectory(inputDirArg)


if __name__ == "__main__":
    main()
