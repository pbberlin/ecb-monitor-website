import json
import pickle
import pandas as pd
import math
from pathlib import Path

from pandas import Timestamp
from pandas import NaT # not a time
NaTType = type(pd.NaT)

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
        print(f"exc is {exc} " )





def formatValue(key, val):
    try:

        if key == "incumbent":
            if isinstance(val, float) and math.isnan(val):
                return ""            
            if val == 1.0:
                return True
            else:
                return False

        if key == "birth_year":
            if isinstance(val, float) and math.isnan(val):
                return ""
            return math.trunc(val)
        if key == "count_speeches":
            if isinstance(val, float) and math.isnan(val):
                return ""
            return math.trunc(val)
        if key == "euro_accession_year":
            if isinstance(val, float) and math.isnan(val):
                return ""
            return math.trunc(val)


        if val is None:
            return ""

        if isinstance(val, (int, float)):
            if isinstance(val, float) and math.isnan(val):
                return ""
            if isinstance(val, int):
                return f"{val}"
            if isinstance(val, float):
                return round(float(val),2)
                # return f"{val:.2f}"


        # default
        return val

    except Exception as e:
        print(f"Error in formatValue: {e}")
        return val



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






def sortByFunction(dataByName):

    try:

        keysInp = list(dataByName.values())

        def generateSortKey(memberRecord):

            sort1a    = memberRecord["organisation_euro"]
            sort1b    = memberRecord["role_euro"]

            fullName = memberRecord["name"]
            nameParts = fullName.split(" ")
            sort2 = nameParts[-1]

            sort3     = memberRecord["starting_date"]

            return (sort1a, sort1b, sort2, sort3)

        keysSorted = sorted(keysInp, key=generateSortKey)

        if False:
            print("--- Sorted Results ---")
            for idx1, member in enumerate(keysSorted):
                name = member["name"]
                date = member["starting_date"]
                role = member["role_euro"]                
                print(f"{idx1 + 1}. {date} | {role} | {name}")

        return keysSorted

    except Exception as exc:
        print(f"sortJson() exc {exc} " )




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

        
        # columns and the key column values
        cols = dta.columns.tolist()
        dbg = ", ".join(cols)
        print(f"cols: {dbg}")

        if keyColName not in cols:
            raise f"{keyColName} must be in cols {cols}"
        else:
            print(f"keyColName '{keyColName}' found cols")


        keyCol = dta[keyColName].tolist()
        for idx1, keyColVal in enumerate(keyCol):
            if idx1 > 3:
                break
            print(f"\tkey col '{keyColName}' val  - {keyColVal}")



        out = {}

        organisation_euro = defaultdict(int)
        role_euro         = defaultdict(int)

        # Iterate columns to create first level keys
        for idx1, colName in enumerate(cols):
            
            col = dta[colName].tolist()

            if idx1 < 1:
                print(f" first five row keys  {keyCol[:5]} ")

            # Iterate rows to create second level keys (cell values)
            for idx2, vl in enumerate(col):

                if vl is None:
                    pass
                elif type(vl) is float:
                    pass
                elif type(vl) is str:
                    pass
                elif type(vl) is NaTType:
                    vl = "NaT"
                    vl = "0"
                elif type(vl) is Timestamp:
                    if vl is NaT:
                        vl = "0"
                    else:
                        vl = vl.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    print(f" type of {vl} is OTHER:    {type(vl)}")


                # print(f" rowkey is {rowKey} ")
                rowKey = str(keyCol[idx2])

                # print(f" {rowKey:28}  {colName:24} {vl}")
                if not rowKey in out:
                    out[rowKey] = {}

                if "name_excel" in out[rowKey] and rowKey !=  out[rowKey]["name_excel"]:
                    print(f" {out[rowKey]['name_excel']} vs {rowKey}")

                if colName == "name_excel":
                    continue
                if colName == "source" and vl is  None:
                    continue


                out[rowKey][colName] = formatValue(colName, vl)

                if colName == "starting_date":
                    out[rowKey]["year_start"] = int(out[rowKey][colName][:4])
                if colName == "termination_date":
                    out[rowKey]["year_stop"] = int(out[rowKey][colName][:4])


                if colName == "organisation_euro":
                    organisation_euro[vl] += 1
                if colName == "role_euro":
                    role_euro[vl] += 1

        # sort - starting_date, organisation_euro, role_euro, name - last token


        print(f"organisation_euro {organisation_euro} ")
        print(f"role_euro         {role_euro} ")

        jsonString = json.dumps(out, indent=4)
        jsContent = f"const {varName}={jsonString}; \n\n"
        with outPthJs1.open("w", encoding="utf-8") as fileHandle:
            fileHandle.write(jsContent)
        print(f"converted \n\t{pthPickle} to \n\t{outPthJs1}")


        byFunction = sortByFunction(out)
        jsonString = json.dumps(byFunction, indent=4)
        jsContent  = f"councilByFunction={jsonString}; \n\n"
        with outPthJs2.open("w", encoding="utf-8") as fileHandle:
            fileHandle.write(jsContent)
        print(f"converted \n\t{pthPickle} to \n\t{outPthJs2}")





    except Exception as exc:
        print(f"exc is {exc} " )



scriptDir = Path(__file__).resolve().parent
appDir    = scriptDir.parent
print(f"\t script     {Path(__file__).resolve()}   start")



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




