from pathlib import Path
import csv
import json
import sys

from collections import defaultdict


from datetime import datetime
currentYear = datetime.now().year

euCodesToNames = {
    "EU27_2020": "Euro area (20 countries)",
    "AT": "Austria",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DK": "Denmark",
    "EE": "Estonia",
    "EL": "Greece",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "HR": "Croatia",
    "HU": "Hungary",
    "IE": "Ireland",
    "IT": "Italy",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "MT": "Malta",
    "NL": "Netherlands",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "SE": "Sweden",
    "SI": "Slovenia",
    "SK": "Slovakia",
    # "UK": "United Kingdom",
}


def makeJsFromTsv(
        inputTsvPath: Path, 
        outputJsPath: Path, 
        dataKey:    str,
        jsName: str,
    ) -> None:
    yearMonths       = []
    yearMonthIndices = []
    dataByYearMonth  = {}

    try:
        with inputTsvPath.open(mode="r", encoding="utf-8", newline="") as inFile:
            delimiterChar = "\t"  # fixed delimiter for TSV

            csvReader = csv.reader(inFile, delimiter=delimiterChar)
            headerFields = next(csvReader, None)
            if headerFields is None:
                print("Empty TSV: no header row present.")
                return

            firstHeaderColIdx = 0 if len(headerFields) > 0 else -1

            for idx1, colName in enumerate(headerFields):
                try:
                    if colName is None:
                        raise ValueError("Encountered a None column name in header.")
                    stripped = colName.strip()

                    if idx1 == 0:
                        continue  # skip composite key column e.g. 'freq,int_rt,geo\\TIME_PERIOD'

                    # accept YYYY or YYYY-MM labels
                    isYearOnly = stripped.isdigit()
                    isYearMonth = False
                    if len(stripped) == 7 and stripped[:4].isdigit() and stripped[4] == "-" and stripped[5:].isdigit():
                        isYearMonth = True

                    if isYearOnly or isYearMonth:
                        yearMonths.append(stripped)
                        yearMonthIndices.append(idx1)
                except Exception as headerExc:
                    print(f"Error processing header index {idx1}: {headerExc}")

            # keep chronological order (works for zero-padded YYYY and YYYY-MM)
            # also keep indices aligned with the same sort
            try:
                zipped = list(zip(yearMonths, yearMonthIndices))
                for idx1, pair in enumerate(zipped):
                    pass
                zipped.sort(key=lambda p: p[0])
                yearMonths = [p[0] for p in zipped]
                yearMonthIndices = [p[1] for p in zipped]
            except Exception as sortExc:
                print(f"Error sorting header year-months: {sortExc}")

            print(f"\tsearching for year-months")
            print(f"\t{yearMonths} ")

            for idx1, yM in enumerate(yearMonths):
                dataByYearMonth[str(yM)] = {}

            unwantedKeysCounter = defaultdict(int)


            for idx1, row in enumerate(csvReader):
                try:
                    if row is None:
                        print(f"Row {idx1} is None.")
                        continue

                    # pad short rows to header length
                    if len(row) < len(headerFields):
                        padCount = len(headerFields) - len(row)
                        for padIdx in range(padCount):
                            row.append("")
                    
                    compositeKey = ""
                    if firstHeaderColIdx >= 0 and firstHeaderColIdx < len(row):
                        compositeKey = row[firstHeaderColIdx]
                    if compositeKey is None:
                        compositeKey = ""
                    compositeKey = compositeKey.strip()

                    # first col format  
                    #           'M,MCBY,AT'          -> geo is the 3rd element
                    #           'M,RCH_A,CP09321,UK' -> geo is the 4th element
                    countryCode = ""
                    parts = compositeKey.split(",")
                    numParts = len(parts)
                    if numParts < 3:
                        print(f"\t row{idx1:05}  skipping too short composite key {compositeKey}")
                        continue

                    dataKeyLooped = ",".join(parts[:-1]) 
                    if dataKey != dataKeyLooped:
                        unwantedKeysCounter[dataKeyLooped] += 1
                        if unwantedKeysCounter[dataKeyLooped] == 1 and (len(unwantedKeysCounter) %100) == 0:
                            print(f"\t row{idx1:05}  skipping unwanted data key {dataKeyLooped}")
                        continue

                    countryCode = parts[numParts-1].strip()
                    if not countryCode in euCodesToNames:
                        print(f"\t row{idx1:05}  skipping {countryCode}")
                        continue

                    country = euCodesToNames[countryCode]
                    # if idx1 < 4 or (idx1%10 == 0):
                    if True:
                        print(f"\t row{idx1:05}  - country is {country}")


                    valCounter = 0
                    lenYm = len(yearMonths)
                    for idx2, yMStr in enumerate(yearMonths):

                        try:
                            colIdx = yearMonthIndices[idx2]
                            yMRaw = ""
                            if colIdx < len(row):
                                yMRaw = row[colIdx]
                            if yMRaw is None:
                                yMRaw = ""
                            yMRaw = yMRaw.strip()

                            # print(f"\t     col{idx2:02}  '{yMStr}' -> '{yMRaw}'")

                            if yMRaw == "" or yMRaw.lower() == "na"  or yMRaw.lower() == ":":
                                print(f"\t\t  col{idx2:02}  '{yMStr}' = '{yMRaw}' -> empty or 'na' or ':' ")
                                continue  # skip missing


                            if yMRaw.endswith(" d"):
                                yMRaw = yMRaw[:-2]


                            cleaned = yMRaw.replace(",", ".")
                            if cleaned.endswith(" e"):
                                cleaned = cleaned[:-2]   
                            val = float(cleaned)
                            dataByYearMonth[yMStr][country] = val

                            valCounter += 1

                            if valCounter <= 3 or  valCounter > (lenYm-3)  or (valCounter % 50)==0:
                                print(f"\t     {valCounter:4}   '{yMStr}' -> {val: 6.3f}   {countryCode} ")


                        except Exception as castExc:
                            print(f"\t     Row {idx1} col {yMStr}: cannot parse '{yMRaw}': {castExc}")
                            continue

                except Exception as rowExc:
                    print(f"Error processing row index {idx1}: {rowExc}")

    except FileNotFoundError as fnfExc:
        print(f"Input file not found: {fnfExc}")
        return
    except Exception as readExc:
        print(f"Error reading input file: {readExc}")
        return

    try:

        # build mapping of year-month keys (sorted descending alphabetically)
        sortedKeysDesc = sorted(dataByYearMonth.keys(), reverse=True)
        mapping = {}
        for idx1, yM in enumerate(sortedKeysDesc):
            mapping[yM] = currentYear - idx1


        mappingInverted = {}
        for idx1, key in enumerate(mapping):
            value = mapping[key]
            mappingInverted[ int(value) ] = key


        # padding the mapping2 - 2000, 2001 ... min value, current year + 1 ... max value
        # derive min/max keys (alphanumerically) and their values
        minKey = min(mappingInverted.keys())
        maxKey = max(mappingInverted.keys())
        minValue = mappingInverted[minKey]
        maxValue = mappingInverted[maxKey]
        for idx1, yearInt in enumerate(range(2000, int(minKey))):
            mappingInverted[yearInt] = str(minValue)
            if idx1 == 2000 or (idx1 > (int(minKey)-4)):
                print(f"\t  year {yearInt} - min value {minValue}")
        nextYears = [currentYear + 1, currentYear + 2]
        for idx1, yearInt in enumerate(nextYears):
            mappingInverted[yearInt] = maxValue


        dataByYearMonth["mapping2"] = mappingInverted


        jsonText = json.dumps(
            dataByYearMonth,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

        jsLines = []
        jsLines.append("// Auto-generated from TSV → JS (years → { COUNTRY: value })")
        jsLines.append(f"const {jsName} = " + jsonText + ";")
        jsText = "\n".join(jsLines)


        with outputJsPath.open(mode="w", encoding="utf-8", newline="") as outJs:
            outJs.write(jsText)
    except Exception as writeExc:
        print(f"Error writing JS file: {writeExc}")


if __name__ == "__main__":

    jobDirEurostat     = Path.cwd() / "scripts" / "eurostat"


    # if False:
    if True:
        inputPath  = Path.cwd() / jobDirEurostat / "estat_teimf050.tsv"
        outputPath = Path.cwd() / "static"  / "dl" /  "eurostat_yields_10y.js"
        makeJsFromTsv(inputPath, outputPath, "M,MCBY", "yieldsTenYears")
        print(f"  eurostat wrote: {outputPath}")

    # if False:
    if True:
        inputPath  = Path.cwd() / jobDirEurostat / "estat_prc_hicp_manr.tsv"
        outputPath = Path.cwd() / "static"  / "dl" /  "eurostat_hicp.js"
        makeJsFromTsv(inputPath, outputPath, "M,RCH_A,CP00", "hicp")
        print(f"  eurostat wrote: {outputPath}")
