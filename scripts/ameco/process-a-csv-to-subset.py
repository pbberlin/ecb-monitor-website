from pathlib import Path
import csv
from datetime import datetime



currentYear = datetime.now().year

euCountries = [
    # "Euro area (1-9 countries)",
    "Euro area (20 countries)",
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





def main(inputFile, targetFilename, targetCode, targetUnit):

    filteredRows = []
    headerFields = None

    # input and output paths
    inputPath  = Path(inputFile)
    outputPath = Path.cwd() / "static"  / "dl" /  f"ameco_{targetFilename}.csv"

    try:
        with inputPath.open(mode="r", encoding="latin-1", newline="") as inFile:
            csvReader = csv.DictReader(inFile, delimiter=",")
            headerFields = csvReader.fieldnames

            # keep only COUNTRY, UNIT, and years 1960–2026
            keepFields = ["COUNTRY", "UNIT"]
            # for year in range(1960, currentYear+2):
            for year in range(2000, currentYear+2):
                keepFields.append(str(year))


            for idx1, row in enumerate(csvReader):
                try:
                    codeRaw   = row.get("CODE", "")
                    codeRaw   = codeRaw.strip()

                    #  new since 2025-11 - code is now
                    #           ROM.1.0.99.327.UDGGLR
                    if "." in codeRaw:
                        parts = codeRaw.split(".")
                        codeVal = parts[-1]
                    else:
                        codeVal = codeRaw

                    unitVal   = row.get("UNIT", "")
                    unitVal   = unitVal.strip()

                    country  = row.get("COUNTRY", "")

                    if idx1 < 10 and ("Euro" not in country):
                        print(f"\t\t row{idx1:03} -  {codeVal:8}  {country:16}  {unitVal} ")


                    if unitVal == targetUnit  and  codeVal == targetCode:

                        if idx1 < 10 and ("Euro" not in country):
                            print(f"\t    unit found in {idx1:3} -  {country:16}  {unitVal} ")

                        # normalize irregular country name
                        if country == "Czechia":
                            row["COUNTRY"] = "Czech Republic"
                            country        = "Czech Republic"


                        if country in euCountries:
                            filteredRow = {k: row[k] for k in keepFields if k in row}
                            filteredRows.append(filteredRow)

                except Exception as rowExc:
                    print(f"error processing row index {idx1}: {rowExc}")

    except FileNotFoundError as fnfExc:
        print(f"input file not found: {fnfExc}")
    except Exception as readExc:
        print(f"error reading input file: {readExc}")



    if headerFields is None:
        print("No headers detected; nothing written.")
    else:
        try:
            with outputPath.open(mode="w", encoding="utf-8", newline="") as outFile:
                csvWriter = csv.DictWriter(outFile, fieldnames=keepFields, delimiter=";")
                csvWriter.writeheader()

                for idx1, row in enumerate(filteredRows):
                    try:
                        csvWriter.writerow(row)
                    except Exception as writeRowExc:
                        print(f"error writing row index {idx1}: {writeRowExc}")

            print(f"\twrote {len(filteredRows)} rows to {outputPath}")
        except Exception as writeExc:
            print(f"error writing output file: {writeExc}")



jobDirAmeco     = Path.cwd() / "scripts" / "ameco"


# filter settings
inpFile        = jobDirAmeco / "AMECO18.CSV"
outFileSuffix  = "debt_to_gdp"
code     = "UDGGL"
code     = "UDGG"
unit     = "(Percentage of GDP at current prices (excessive deficit procedure))"
main(inpFile, outFileSuffix, code, unit)


inpFile        = "AMECO16.CSV"
outFileSuffix  = jobDirAmeco / "net_lending"
code     = "UBLG"
unit     = "(Percentage of GDP at current prices (excessive deficit procedure))"
main(inpFile, outFileSuffix, code, unit)


inpFile        = jobDirAmeco / "AMECO16.CSV"
outFileSuffix  = "total_expenditure"
code     = "UUTG"
unit     = "(Percentage of GDP at current prices (excessive deficit procedure))"
main(inpFile, outFileSuffix, code, unit)


inpFile        = jobDirAmeco / "AMECO16.CSV"
outFileSuffix  = "interest_expenditure"
code     = "UYIG"
unit     = "(Percentage of GDP at current prices (excessive deficit procedure))"
main(inpFile, outFileSuffix, code, unit)


inpFile        = jobDirAmeco / "AMECO16.CSV"
outFileSuffix  = "interest_to_gdp"
code     = "UYIG"
unit     = "(Percentage of GDP at current prices (excessive deficit procedure))"
main(inpFile, outFileSuffix, code, unit)
