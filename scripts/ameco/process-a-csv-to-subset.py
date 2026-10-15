from pathlib import Path
import csv
from datetime import datetime

parentDir = Path(__file__).resolve().parent.parent.parent
libPath = parentDir / "lib"
sys.path.insert(0, str(libPath))
from util import stackTrace



currentYear = datetime.now().year

euCodesToNames = {
    "EU27": "Euro area (27 countries)",
    "AUT": "Austria",
    "BEL": "Belgium",
    "BGR": "Bulgaria",
    "HRV": "Croatia",
    "CYP": "Cyprus",
    "CZE": "Czech Republic",
    "DNK": "Denmark",
    "EST": "Estonia",
    "FIN": "Finland",
    "FRA": "France",
    "DEU": "Germany",
    "GRC": "Greece",
    "HUN": "Hungary",
    "IRL": "Ireland",
    "ITA": "Italy",
    "LVA": "Latvia",
    "LTU": "Lithuania",
    "LUX": "Luxembourg",
    "MLT": "Malta",
    "NLD": "Netherlands",
    "POL": "Poland",
    "PRT": "Portugal",
    "ROM": "Romania",
    "SVK": "Slovakia",
    "SVN": "Slovenia",
    "ESP": "Spain",
    "SWE": "Sweden"
}





def main(inputFile, targetFilename, targetCode, targetUnit, targetUnitNot="impossibleNonEmptyDefault"):

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
            # for year in range(2000, currentYear+2):
            for year in range(1999, currentYear+2):
                keepFields.append(str(year))

            hitCounter = 0
            for idx1, row in enumerate(csvReader):
                try:
                    codeRaw   = row.get("CODE", "")
                    codeRaw   = codeRaw.strip()

                    # extracting country code and indicator code
                    if "." in codeRaw:
                        parts = codeRaw.split(".")
                        countryCode = parts[0]
                        codeVal     = parts[-1]
                    else:
                        countryCode = ""
                        codeVal     = codeRaw

                    unitVal   = row.get("UNIT", "")
                    unitVal   = unitVal.strip()

                    country  = row.get("COUNTRY", "")

                    # if idx1 < 10 and ("Euro" not in country):
                    #     print(f"\t  row{idx1:04} -  {codeVal:8}  {country:12}  {unitVal} ")


                    if codeVal == targetCode  and (unitVal == targetUnit or targetUnit=="*")  and  (targetUnitNot not in unitVal):

                        hitCounter +=1

                        # if idx1 < 11 and ("Euro" not in country):
                        dbgCountry = country.split(" ")[0]
                        unitValDbg = unitVal[0:36]
                        if hitCounter < 11 and ("Euro" not in country):
                            print(f"\t  row{idx1:04} {dbgCountry:12} code {codeVal:8}  unit {unitValDbg}    {row.get('2024', ''):8} {row.get('2025', ''):8} ")

                        # filtering by country code and overriding country name
                        if countryCode in euCodesToNames:
                            row["COUNTRY"] = euCodesToNames[countryCode]
                            filteredRow = {k: row[k] for k in keepFields if k in row}
                            filteredRows.append(filteredRow)


                except Exception as rowExc:
                    stackTrace(rowExc)
                    print(f"error processing row index {idx1}")

    except FileNotFoundError as fnfExc:
        stackTrace(fnfExc)
        print("input file not found")
    except Exception as readExc:
        stackTrace(readExc)
        print("error reading input file")



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
                        stackTrace(writeRowExc)
                        print(f"error writing row index {idx1}")

            print(f"\twrote {len(filteredRows)} rows to {outputPath}")
        except Exception as writeExc:
            stackTrace(writeExc)
            print("error writing output file")



jobDirAmeco     = Path.cwd() / "scripts" / "ameco"


# filter settings

# if False:
if True:
    inpFile        = jobDirAmeco / "AMECO18.CSV"
    outFileSuffix  = "debt_to_gdp"
    code     = "UDGG"
    unit     = "(Percentage of GDP at current prices (excessive deficit procedure))"
    main(inpFile, outFileSuffix, code, unit)


    inpFile        = jobDirAmeco / "AMECO16.CSV"
    outFileSuffix  = "net_lending"
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



    ##
    inpFile        = jobDirAmeco / "AMECO6.CSV"
    outFileSuffix  = "gdp_real"
    code     = "OVGD"
    unit     = "Mrd ECU/EUR, Standard aggregation"
    unit     = "Mrd ECU/EUR"
    unit     = "Mrd ECU/EUR, Weighted mean of t/t-1 national growth rates (weights: t-1 current prices in ECU/EUR)"
    unit     = "*"
    notUnit  = "current prices in PPS"
    main(inpFile, outFileSuffix, code, unit, notUnit)


    inpFile        = jobDirAmeco / "AMECO6.CSV"
    outFileSuffix  = "output_gap"
    code     = "AVGDGP"
    unit     = "(Percentage of potential gross domestic product at constant prices)"
    main(inpFile, outFileSuffix, code, unit)







inputPath  = Path.cwd() / "static" / "dl" / "ameco_gdp_real.csv"
outputPath = Path.cwd() / "static" / "dl" / "ameco_gdp_growth.csv"


try:
    with inputPath.open("r", newline="", encoding="utf-8") as infile:
        reader = list(csv.reader(infile,delimiter=";"))
except Exception as exc:
    stackTrace(exc)
    print("error reading ameco_gdp_real.csv")
    raise

print(f"\tconverting GDP to growth, computing" )


outHeader = reader[0]
outRows   = []

for idx1, row in enumerate(reader):

    if idx1 == 0:
        continue

    out = []

    if idx1 < 3 or idx1 > len(reader)-3:
        print(f"\t  row {idx1:2}  {row[0]}  {row[2]}  {row[3]}" )

    # print( row )

    for idx2, val in enumerate(row):
        if idx2 < 2:
            out.append(val)
        elif idx2 == 2:
            out.append("0")
        else:
            try:
                # (GDP(T)/(GDP(T-1)-1)*100
                vlT1 = float(val)
                vlT0 = float(row[idx2-1])
                pc0  = (vlT1 / vlT0) - 1

                #   rounding - i.e. Euro area
                #                1.019571     +1.020
                #                1.706894     +1.707
                pct  = round(100 * pc0, 4)
                out.append( str(pct).replace(".", ",")  )

                if idx1 < 3 or idx1 > len(reader)-3:
                    if idx2 == 3:
                        print("\t\t", end="")
                    if idx2 < 6:
                        # print(f" {vl:.2f} - {prev:.2f} - {pct:.3f}" , end=", ")
                        print(f"{pct:+.3f}" , end=", ")
                        # print(f"pp{100*pc0:+10.6f}" , end=", ")
                    if idx2 == 5:
                        print("")
            except Exception as exc:
                stackTrace(exc)
                print(f"error calculating growth for row {idx1} col {idx2}")

    outRows.append(out)

try:
    with outputPath.open("w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile, delimiter=";")
        writer.writerow(outHeader)
        writer.writerows(outRows)
except Exception as exc:
    stackTrace(exc)
    print("error writing ameco_gdp_growth.csv")
    raise