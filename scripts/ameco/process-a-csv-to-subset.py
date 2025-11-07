from pathlib import Path
import csv
from datetime import datetime

# filter settings
targetUnit = "(Percentage of GDP at current prices (excessive deficit procedure))"

euCountries = [
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Ireland",
    "Italy",
    "Latvia",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Poland",
    "Portugal",
    "Romania",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden"
]

filteredRows = []
headerFields = None


currentYear = datetime.now().year

# input and output paths
inputPath  = Path("AMECO18.CSV")
outputPath = Path.cwd() / ".." /  ".." / "static"  / "dl" /  "ameco_debt_to_gdp.csv"


try:
    with inputPath.open(mode="r", encoding="latin-1", newline="") as inFile:
        csvReader = csv.DictReader(inFile, delimiter=",")
        headerFields = csvReader.fieldnames

        # keep only COUNTRY, UNIT, and years 1960–2026
        keepFields = ["COUNTRY", "UNIT"]
        for year in range(1960, currentYear+1):
            keepFields.append(str(year))


        for idx1, row in enumerate(csvReader):
            try:
                unitVal  = row.get("UNIT", "")
                unitVal  = unitVal.strip()
                country  = row.get("COUNTRY", "")

                # 

                # your debug print preserved
                print(f" {country:16}  {unitVal} ")

                if unitVal == targetUnit:


                    # normalize irregular country name
                    if country == "Czechia":
                        row["COUNTRY"] = "Czech Republic"
                        country        = "Czech Republic"


                    if country in euCountries:
                        filteredRow = {k: row[k] for k in keepFields if k in row}
                        filteredRows.append(filteredRow)

            except Exception as rowExc:
                print(f"Error processing row index {idx1}: {rowExc}")

except FileNotFoundError as fnfExc:
    print(f"Input file not found: {fnfExc}")
except Exception as readExc:
    print(f"Error reading input file: {readExc}")



if headerFields is None:
    print("No headers detected; nothing written.")
else:
    try:
        with outputPath.open(mode="w", encoding="utf-8", newline="") as outFile:
            csvWriter = csv.DictWriter(outFile, fieldnames=keepFields, delimiter=",")
            csvWriter.writeheader()

            for idx1, row in enumerate(filteredRows):
                try:
                    csvWriter.writerow(row)
                except Exception as writeRowExc:
                    print(f"Error writing row index {idx1}: {writeRowExc}")

        print(f"Wrote {len(filteredRows)} rows to {outputPath}")
    except Exception as writeExc:
        print(f"Error writing output file: {writeExc}")


