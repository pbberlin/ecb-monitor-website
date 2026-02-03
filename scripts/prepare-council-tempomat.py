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

from numpy import float64, int32

from collections import defaultdict


pthScript   = Path(__file__).resolve()
projectRoot = pthScript.parent.parent
if str(projectRoot) not in sys.path:
    sys.path.insert(0, str(projectRoot))

from lib.util import toHtml



def formatValue(key, vl):
    try:

        if key == "date" :
            if vl is None:
                vl = "-"
            elif type(vl) is NaTType:
                vl = "0"
            elif type(vl) is Timestamp:
                if vl is NaT:
                    vl = "0"
                else:
                    vl = vl.strftime("%Y-%m-%d %H:%M:%S")


        if vl is None:
            return ""

        if isinstance(vl, (int, int32, float)):
            if isinstance(vl, float) and math.isnan(vl):
                return ""
            if isinstance(vl, int):
                return f"{vl}"
            if isinstance(vl, int32):
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
    varName="councilTempomat",
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
            raise Exception(f"{keyColName} must be in cols {cols}")
        else:
            print(f"\t  keyColName '{keyColName}' and {len(cols)} cols total")
            # dbg = ", ".join(cols)
            # print(f"cols: {dbg}")



        if False:
        # if True:
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





        # remove keys not needed
        for idx1, key in enumerate(out):
            out[idx1].pop("career_1",   None)
            out[idx1].pop("career_2",   None)


        #
        # byFunction = sortBy(out)
        jsonString = json.dumps(out, indent=4)
        jsContent  = f"{varName}={jsonString}; \n\n"
        with outPthJs2.open("w", encoding="utf-8") as fileHandle:
            fileHandle.write(jsContent)
        print(f"\tconverted \n\t  {pthPickle} to \n\t  {outPthJs2}")
        print(f"\toutput-3 {len(out)} rows")





    except Exception as exc:
        tb = traceback.extract_tb(exc.__traceback__)[-1]
        print(f"{exc} | {tb.filename}:{tb.lineno} | {tb.line}")
        sys.exit(1)



scriptDir = Path(__file__).resolve().parent
appDir    = scriptDir.parent
print(f"\tscript     {Path(__file__).resolve()}   start")



# testFormatValue()


toHtml(
    Path( appDir / "scripts" / "council" / "tempomat.pkl") ,
    Path( appDir / "scripts" / "council" / "tempomat.html") ,
)

convertPickleToJs(
    Path( appDir / "scripts" / "council" / "tempomat.pkl") ,
    Path( appDir / "static" / "dl"       / "council-tempomat.js") ,
    "year",
)

