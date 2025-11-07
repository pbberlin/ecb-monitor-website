from pathlib import Path
import csv
import json
import sys

def makeJsFromCsv(inputCsvPath: Path, outputJsPath: Path) -> None:
    years = []
    dataByYear = {}

    try:
        with inputCsvPath.open(mode="r", encoding="utf-8", newline="") as inFile:
            delimiterChar = ","  # fixed delimiter

            csvReader = csv.DictReader(inFile, delimiter=delimiterChar)
            headerFields = csvReader.fieldnames if csvReader.fieldnames is not None else []

            for idx1, colName in enumerate(headerFields):
                try:
                    if colName is None:
                        raise ValueError("Encountered a None column name in header.")
                    stripped = colName.strip()
                    if stripped.isdigit():
                        years.append(int(stripped))
                except Exception as headerExc:
                    print(f"Error processing header index {idx1}: {headerExc}")

            years.sort()

            for idx1, yr in enumerate(years):
                dataByYear[str(yr)] = {}

            for idx1, row in enumerate(csvReader):
                try:
                    country = row.get("COUNTRY", "")
                    if country is None:
                        country = ""
                    country = country.strip()

                    for idx2, yr in enumerate(years):
                        yearStr = str(yr)
                        rawVal = row.get(yearStr, "")
                        if rawVal is None:
                            rawVal = ""
                        rawVal = rawVal.strip()

                        if rawVal == "" or rawVal.lower() == "na":
                            continue  # skip missing

                        try:
                            cleaned = rawVal.replace(",", ".")
                            value = float(cleaned)
                        except Exception as castExc:
                            print(f"Non-numeric value at row {idx1} year {yearStr} ('{rawVal}'): {castExc}")
                            continue

                        dataByYear[yearStr][country] = value
                except Exception as rowExc:
                    print(f"Error processing row index {idx1}: {rowExc}")

    except FileNotFoundError as fnfExc:
        print(f"Input file not found: {fnfExc}")
        return
    except Exception as readExc:
        print(f"Error reading input file: {readExc}")
        return

    try:
        jsonText = json.dumps(
            dataByYear,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

        jsLines = []
        jsLines.append("// Auto-generated from CSV → JS (years → { COUNTRY: value })")
        jsLines.append("const debtPercentOfGDP = " + jsonText + ";")
        jsText = "\n".join(jsLines)

        with outputJsPath.open(mode="w", encoding="utf-8", newline="") as outJs:
            outJs.write(jsText)
    except Exception as writeExc:
        print(f"Error writing JS file: {writeExc}")


if __name__ == "__main__":

    inputPath  = Path.cwd() / ".." / ".." / "static"  / "dl" /  "ameco_debt_to_gdp.csv"
    outputPath = Path.cwd() / ".." / ".." / "static"  / "dl" /  "ameco_debt_to_gdp.js"

    makeJsFromCsv(inputPath, outputPath)
    print(f"Wrote: {outputPath}")
