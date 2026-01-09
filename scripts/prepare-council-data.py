import json
import pickle
import pandas as pd
from pathlib import Path

from pandas import Timestamp
from pandas import NaT # not a time
NaTType = type(pd.NaT)

def convertPickleToJs(
    pthPickle, 
    outPthJs, 
    keyColName, 
    varName="ecbCouncil",
):

    try:

        with pthPickle.open("rb") as fileHandle:
            dta = pickle.load(fileHandle)

        # ensure is DataFrame
        if not isinstance(dta, pd.DataFrame):
            dta = pd.DataFrame(dta)

        out1 = {}
        
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



        out2 = {}

        # Iterate columns to create first level keys
        for idx1, colName in enumerate(cols):
            
            colDict = {}
            col = dta[colName].tolist()

            if idx1 < 6:
                print(f" row  {keyCol[:5]} ")

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
                elif type(vl) is Timestamp:
                    if vl is NaT:
                        vl = "NaT"
                    else:
                        vl = vl.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    print(f" type of {vl} is OTHER:    {type(vl)}")


                rowKey = str(keyCol[idx2])
                # print(f" rowkey is {rowKey} ")
                colDict[rowKey] = vl


                # print(f" {rowKey:28}  {colName:24} {vl}")
                if not rowKey in out2:
                    out2[rowKey] = {}
                out2[rowKey][colName] = vl


            out1[colName] = colDict


        # jsonString = json.dumps(out1, indent=4)
        jsonString = json.dumps(out2, indent=4)
        
        jsParts = [f"const {varName} = ", jsonString, ";"]
        jsContent = "".join(jsParts)

        with outPthJs.open("w", encoding="utf-8") as fileHandle:
            fileHandle.write(jsContent)

        print(f"converted {pthPickle} to {outPthJs}")

    except Exception as exc:
        print(f"exc is {exc} " )



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

    except Exception as exceptionObject:
        # Always print the exception
        print(exceptionObject)


scriptDir = Path(__file__).resolve().parent
appDir    = scriptDir.parent
print(f"\t script     {Path(__file__).resolve()}   start")


toHtml(   
    Path( appDir / "data" / "dl" / "ecb-council-data.pkl") ,
    Path( appDir / "data" / "dl" / "council.html") ,
)

convertPickleToJs(
    Path( appDir / "data"   / "dl" / "ecb-council-data.pkl") ,
    Path( appDir / "static" / "dl" / "ecb-council-data.js") ,
    "name",
)


