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





def main(inputFile,targetFilename, targetCode, targetUnit):

    filteredRows = []
    headerFields = None

    # input and output paths
    inputPath  = Path(inputFile)
    outputPath = Path.cwd() / ".." /  ".." / "static"  / "dl" /  f"ameco_{targetFilename}.csv"

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

                    if idx1 < 10:
                        print(f" row{idx1:03} -  {codeVal:24}  {country:16}  {unitVal} ")


                    if unitVal == targetUnit  and  codeVal == targetCode:

                        print(f" unit found in {idx1:3} -  {country:16}  {unitVal} ")

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
                csvWriter = csv.DictWriter(outFile, fieldnames=keepFields, delimiter=";")
                csvWriter.writeheader()

                for idx1, row in enumerate(filteredRows):
                    try:
                        csvWriter.writerow(row)
                    except Exception as writeRowExc:
                        print(f"Error writing row index {idx1}: {writeRowExc}")

            print(f"Wrote {len(filteredRows)} rows to {outputPath}")
        except Exception as writeExc:
            print(f"Error writing output file: {writeExc}")




# filter settings
inpFile        = "AMECO18.CSV"
outFileSuffix  = "debt_to_gdp"
code     = "UDGGL"
code     = "UDGG"
unit     = "(Percentage of GDP at current prices (excessive deficit procedure))"
main(inpFile, outFileSuffix, code, unit)


outFileSuffix  = "net_lending"
inpFile        = "AMECO16.CSV"
code     = "UBLG"
unit     = "(Percentage of GDP at current prices (excessive deficit procedure))"
main(inpFile, outFileSuffix, code, unit)


outFileSuffix  = "total_expenditure"
inpFile        = "AMECO16.CSV"
code     = "UUTG"
unit     = "(Percentage of GDP at current prices (excessive deficit procedure))"
main(inpFile, outFileSuffix, code, unit)


outFileSuffix  = "interest_expenditure"
inpFile        = "AMECO16.CSV"
code     = "UYIG"
unit     = "(Percentage of GDP at current prices (excessive deficit procedure))"
main(inpFile, outFileSuffix, code, unit)


outFileSuffix  = "interest_to_gdp"
inpFile        = "AMECO16.CSV"
code     = "UYIG"
unit     = "(Percentage of GDP at current prices (excessive deficit procedure))"
main(inpFile, outFileSuffix, code, unit)
