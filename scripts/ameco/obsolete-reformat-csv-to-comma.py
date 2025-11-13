from pathlib import Path
import csv
import shutil

def convertNumericStringToCommaDecimal(numericString):
    numericString = numericString.strip()
    if numericString == "":
        return numericString
    try:
        # parse using "." as decimal separator
        parsedFloat = float(numericString)
    except Exception as e:
        print(f"[PARSE ERROR] value='{numericString}': {e}")
        return numericString
    # write using "," as decimal separator
    return str(parsedFloat).replace(".", ",")

def processCsvFile(csvPath):
    # read all rows first
    with csvPath.open("r", encoding="utf-8", newline="") as inFile:
        reader = csv.DictReader(inFile, delimiter=";")
        fieldNames = reader.fieldnames if reader.fieldnames is not None else []
        rows = []
        for idx1, row in enumerate(reader):
            rows.append(row)

    # identify year columns 1960..9999
    yearFields = []
    for idx1, name in enumerate(fieldNames):
        if isinstance(name, str) and name.isdigit():
            yearInt = int(name)
            if 1960 <= yearInt <= 9999:
                yearFields.append(name)

    # transform rows
    for idx1, row in enumerate(rows):
        for idx2, yearCol in enumerate(yearFields):
            if yearCol in row and row[yearCol] is not None:
                row[yearCol] = convertNumericStringToCommaDecimal(row[yearCol])

    # write to temp, then replace original
    tmpPath = csvPath.with_suffix(".tmp.csv")
    with tmpPath.open("w", encoding="utf-8", newline="") as outFile:
        writer = csv.DictWriter(outFile, fieldnames=fieldNames, delimiter=";")
        writer.writeheader()
        for idx1, row in enumerate(rows):
            writer.writerow(row)

    try:
        shutil.move(str(tmpPath), str(csvPath))
    except Exception as e:
        print(f"[REPLACE ERROR] '{tmpPath.name}' -> '{csvPath.name}': {e}")
        # if replace fails, keep the temp file for inspection


def main():
    targetDir = Path.cwd() / ".." / ".." / "static" / "dl"

    if not targetDir.exists():
        print(f"[ERROR] Directory not found: {targetDir}")
        return

    csvFiles = sorted(targetDir.glob("*.csv"))
    if len(csvFiles) == 0:
        print(f"[INFO] No CSV files in: {targetDir}")
        return

    for idx1, csvPath in enumerate(csvFiles):
        print(f"[PROCESS] {csvPath}")
        try:
            processCsvFile(csvPath)
        except Exception as e:
            print(f"[FILE ERROR] {csvPath}: {e}")

if __name__ == "__main__":
    main()
