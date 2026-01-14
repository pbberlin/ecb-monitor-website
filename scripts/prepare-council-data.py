import json
import pickle
import pandas as pd
import math
from pathlib import Path
import traceback
import sys

from pandas import Timestamp
from pandas import NaT # not a time
NaTType = type(pd.NaT)

from numpy import float64

from collections import defaultdict

def toHtml(pthPickle, outPth):
    try:
        # Read the pickle file into a pandas DataFrame
        councilDataFrame = pd.read_pickle(pthPickle)

        # Transform the DataFrame into an HTML table string
        # Using built-in method to avoid manual loops as per instruction
        htmlTable = councilDataFrame.to_html()

        # print(htmlTable)
        with outPth.open("w", encoding="utf-8") as fileHandle:
            fileHandle.write(htmlTable)

    except Exception as exc:
        tb = traceback.extract_tb(exc.__traceback__)[-1]
        print(f"{exc} | {tb.filename}:{tb.lineno} | {tb.line}")





def formatValue(key, vl):
    try:

        if key == "starting_date" or key == "termination_date" :
            if vl is None:
                vl = "-"
            elif type(vl) is NaTType:
                vl = "0"
            elif type(vl) is Timestamp:
                if vl is NaT:
                    vl = "0"
                else:
                    vl = vl.strftime("%Y-%m-%d %H:%M:%S")


        if key == "incumbent":
            if isinstance(vl, float) and math.isnan(vl):
                return ""
            if vl == 1.0:
                return True
            else:
                return False

        if key == "birth_year":
            if isinstance(vl, float) and math.isnan(vl):
                return ""
            if type(vl) is str:
                return vl
            return int(math.trunc(vl))
        if key == "count_speeches":
            if isinstance(vl, float) and math.isnan(vl):
                return ""
            if type(vl) is str:
                return vl
            return int(math.trunc(vl))
        if key == "euro_accession_year":
            if isinstance(vl, float) and math.isnan(vl):
                return ""
            if type(vl) is str:
                return vl
            return int(math.trunc(vl))


        if vl is None:
            return ""

        if isinstance(vl, (int, float)):
            if isinstance(vl, float) and math.isnan(vl):
                return ""
            if isinstance(vl, int):
                return f"{vl}"
            if isinstance(vl, float):
                return round(float(vl),2)
                # return f"{val:.2f}"


        # default
        return vl

    except Exception as exc:
        # print(f"Error in formatValue: {e} \n\t  -{key}-  -{vl}-")
        tb = traceback.extract_tb(exc.__traceback__)[-1]
        print(f"\t formatValue() -{key}-  -{vl}-")
        print(f"\t {exc}")
        print(f"\t {tb.filename}:{tb.lineno} | {tb.line}")


        return vl



def testFormatValue():

    testData = [
        ("incumbent", 1.0),
        ("incumbent", 0.0),
        ("incumbent", float("nan")),
        ("birth_year", 1980.9),
        ("birth_year", float("nan")),
        ("some_float", 50000.1234),
        ("some_float", None),
        ("some_float", "Not a number"),
        ("some_int", 99)
    ]
    for idx1, testTuple in enumerate(testData):
        testKey   = testTuple[0]
        testValue = testTuple[1]
        result = formatValue(testKey, testValue)
        print(f"Key: {testKey:<12} | Value: {str(testValue):<15} -> Result: {result}")






def sortByFunction(members):

    # print(f" {type(members)}")

    try:
        # members is now a list of member records (dicts)

        keysInp = []
        for row in members:
            keysInp.append(row)


        roleOrderMap = {
            "president":       0,
            "vice-president":  1,
            "chief economist": 2,
            "executive board": 3,
            "board":           4,
            "governor":        5,   # non-ecb
            "executive board": 6,   # ecb
        }

        def generateSortKey(memberRecord):

            sort1a = memberRecord["organisation_euro"]  # ecb or country gov

            roleValue = memberRecord["role_euro"]        # president, vp, chief econ., board
            if roleValue not in roleOrderMap:
                raise ValueError(f"Unknown role_euro: {roleValue}")

            sort1b = roleOrderMap[roleValue]

            fullName = memberRecord["name"]
            nameParts = fullName.split(" ")
            sort2 = nameParts[-1]

            sort3 = memberRecord["starting_date"]

            # print(f" sorting by {sort1a}-{sort1b}-{sort2}-{sort3}")
            return (sort1a, sort1b, sort2, sort3)

        keysSorted = sorted(keysInp, key=generateSortKey)

        if True:
            print("\t\t--- Sorted Results ---")
            headTail = 5
            for idx1, member in enumerate(keysSorted):
                name = member["name"]
                date = member["starting_date"]
                role = member["role_euro"]
                if idx1 < headTail or idx1 > (len(keysSorted) - headTail):
                    print(f"\t\t{idx1 + 1:3}. {date} | {role:14} | {name}")

        return keysSorted

    except Exception as exc:
        tb = traceback.extract_tb(exc.__traceback__)[-1]
        print(f"{exc} | {tb.filename}:{tb.lineno} | {tb.line}")
        sys.exit(1)


def convertPickleToJs(
    pthPickle,
    outPthJs1,
    outPthJs2,
    keyColName,
    varName="councilByName",
):

    try:

        with pthPickle.open("rb") as fileHandle:
            dta = pickle.load(fileHandle)

        # ensure is DataFrame
        if not isinstance(dta, pd.DataFrame):
            dta = pd.DataFrame(dta)

        print(f"\t  found {len(dta)} records in data frame")

        # columns and the key column values
        cols = dta.columns.tolist()
        if keyColName not in cols:
            raise f"{keyColName} must be in cols {cols}"
        else:
            print(f"\t  keyColName '{keyColName}' and {len(cols)} cols total")
            # dbg = ", ".join(cols)
            # print(f"cols: {dbg}")



        if False:
            keyColA = dta[keyColName].tolist()
            print(f"\t  found {len(keyColA)} rows  by '{keyColName}'")
            for idx1, keyColVal in enumerate(keyColA):
                if idx1 > 2:
                    break
                print(f"\t     key col '{keyColName}' val  - {keyColVal}")


        out = []


        keyCol = dta[keyColName].tolist()
        for idx1, rawRowKey in enumerate(keyCol):

            loopName = dta.iloc[idx1][keyColName]
            if (idx1 < 3) or (idx1 >= (len(dta)-3)):
                print(f"\t     {idx1:3} key col '{keyColName}' val  - {loopName}")
    
            # iterate columns for row
            row = {}
            for idx2, colName in enumerate(cols):
                vl = dta.iloc[idx1][colName]
                vl = formatValue(colName, vl)
                row[colName] = vl
            out.append(row)


        print(f"\toutput-2 {len(out)} rows")


        if False:
            for idx1, row in enumerate(out):
                if (idx1 < 3) or (idx1 >= (len(out)-3)):
                    print("\t", end="")
                    for idx2, key in enumerate(row):
                        print(f" {key} {row[key]}", end=", ")
                    print("")


        organisation_euro = defaultdict(int)
        role_euro         = defaultdict(int)
        distinctNames     = defaultdict(int)


        for idx1, row in enumerate(out):
            if "name_excel" in row and row["name"] !=  row["name_excel"]:
                print(f" {row['name_excel']} vs {row['name']}")
            else:
                out[idx1].pop("name_excel",   None)


            if "starting_date" in row:
                out[idx1]["year_start"] = int(row["starting_date"][:4])
            if "termination_date" in row:
                out[idx1]["year_stop"]  = int(row["termination_date"][:4])


            if "organisation_euro" in row:
                organisation_euro[ row["organisation_euro"] ] += 1
            if "role_euro" in row:
                role_euro[ row["role_euro"] ] += 1
            if "name" in row:
                distinctNames[ row["name"] ]  += 1




        # print(f"\t  organisation_euro {', '.join(organisation_euro)} ")
        print("\t", end="")
        for key in organisation_euro:
            print(f"{key:<12}  {organisation_euro[key]}", end=", ")
        print("")
        print("\t", end="")
        # print(f"\t  role_euro         {', '.join(role_euro)} ")
        for key in role_euro:
            print(f"{key:<12}  {role_euro[key]}", end=", ")
        print("")
        print("\t", end="")
        cntr = 0
        for idx, key in enumerate(distinctNames):
            if distinctNames[key] > 1:
                print(f"{key:20} {distinctNames[key]}", end=", ")
                cntr += 1
            if cntr > 3:
                cntr = 0
                print("")
                print("\t", end="")
        print("")



        # combined keys for convenience
        for idx1, row in enumerate(out):
            row["from_to"] = f"{row['year_start']} - {row['year_stop']}"
            if row['year_stop'] == 0:
                row["from_to"] = f"since {row['year_start']}  "

            officeTitle = f"{row['role_euro']}"
            officeTitle = str(officeTitle).strip()
            # we do this using i18n later in Javascript:
            #    ...replace("executive board", "", -1)
            #    ...replace("chief economist", "", -1)
            #    ...replace("vice-president", "Vice-Pres.", -1)
            #    ...title()

            if officeTitle:
                row["role_euro__from_to"]  = f"{officeTitle},  {row['from_to']} "
            else:
                row["role_euro__from_to"]  = f"{row['from_to']} "


            row["born_raised"]  = f"*{row['birth_year']}, {row['country']}"


            row["education"]  = f"education: {row['field_of_study']}"

            row["career"] = "experience: "
            if row['career_1']:
                row["career"] += f"{row['career_1']}"
            if row['career_2']:
                row["career"] += f", {row['career_2']}"





        # remove keys not needed
        for idx1, key in enumerate(out):
            # out[idx1].pop("year_start", None)
            # out[idx1].pop("year_stop",  None)
            out[idx1].pop("career_1",   None)
            out[idx1].pop("career_2",   None)

            if ("source" in row)  and  row["source"]=="":
                out[idx1].pop("source",   None)

            if ("euro_accession_year" in row)  and  row["euro_accession_year"]=="":
                out[idx1].pop("euro_accession_year",   None)

            if ("name_excel" in row):
                if row["name_excel"]==row["name"]:
                    out[idx1].pop("name_excel",   None)



        if False:
            jsonString = json.dumps(out, indent=4)
            jsContent = f"const {varName}={jsonString}; \n\n"
            with outPthJs1.open("w", encoding="utf-8") as fileHandle:
                fileHandle.write(jsContent)
            print(f"converted \n\t{pthPickle} to \n\t{outPthJs1} - {len(out)} rows")



        #
        byFunction = sortByFunction(out)
        jsonString = json.dumps(byFunction, indent=4)
        jsContent  = f"councilByFunction={jsonString}; \n\n"
        with outPthJs2.open("w", encoding="utf-8") as fileHandle:
            fileHandle.write(jsContent)
        print(f"\tconverted \n\t  {pthPickle} to \n\t  {outPthJs2}")
        print(f"\toutput-3 {len(byFunction)} rows")





    except Exception as exc:
        tb = traceback.extract_tb(exc.__traceback__)[-1]
        print(f"{exc} | {tb.filename}:{tb.lineno} | {tb.line}")
        sys.exit(1)



scriptDir = Path(__file__).resolve().parent
appDir    = scriptDir.parent
print(f"\tscript     {Path(__file__).resolve()}   start")



# testFormatValue()


toHtml(
    Path( appDir / "data" / "dl" / "ecb-council-data.pkl") ,
    Path( appDir / "data" / "dl" / "council.html") ,
)

convertPickleToJs(
    Path( appDir / "data"   / "dl" / "ecb-council-data.pkl") ,
    Path( appDir / "static" / "dl" / "ecb-council-by-name.js") ,
    Path( appDir / "static" / "dl" / "ecb-council-by-function.js") ,
    "name",
)




