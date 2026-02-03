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

from ..lib.util import toHtml



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

        return vl

    except Exception as exc:
        tb = traceback.extract_tb(exc.__traceback__)[-1]
        print(f"\t formatValue() -{key}-  -{vl}-")
        print(f"\t {exc}")
        print(f"\t {tb.filename}:{tb.lineno} | {tb.line}")


        return vl



def testFormatValue():
    testData = [
        ("incumbent", 1.0),
        ("incumbent", 0.0),
    ]
    for idx1, testTuple in enumerate(testData):
        testKey   = testTuple[0]
        testValue = testTuple[1]
        result = formatValue(testKey, testValue)
        print(f"Key: {testKey:<12} | Value: {str(testValue):<15} -> Result: {result}")






def sortBy(members):
    keysInp = []
    for row in members:
        keysInp.append(row)

    return keysInp


def convertPickleToJs(
    pthPickle,
    outPthJs2,
    keyColName,
    varName="councilBy6Weeks",
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

            if "Jose Manuel Gonzalez-Paramo" in row["name"]:
                out[idx1]["name"] = "Jose M. Gonzalez-Paramo"


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
            if officeTitle:
                row["role_euro__from_to"]  = f"{officeTitle},  {row['from_to']} "
            else:
                pass
                # row["role_euro__from_to"]  = f"{row['from_to']} "



        # remove keys not needed
        for idx1, key in enumerate(out):
            out[idx1].pop("career_1",   None)
            out[idx1].pop("career_2",   None)


        #
        byFunction = sortBy(out)
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
    Path( appDir / "scripts" / "council" / "council-by-6weeks.pkl") ,
    Path( appDir / "scripts" / "council" / "council-by-6weeks.html") ,
)

convertPickleToJs(
    Path( appDir / "scripts" / "council" / "council-by-6weeks.pkl") ,
    Path( appDir / "static" / "dl"       / "council-by-6weeks.js") ,
    "name",
)

