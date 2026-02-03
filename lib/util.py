from pandas import Timestamp

import pandas as pd
import traceback

def truncateUtf8(text, limit=128):
    if not isinstance(text, str):
        return text
    encoded = text.encode('utf-8')
    if len(encoded) <= limit:
        return text
    truncated = encoded[:limit]
    # Ensure we don’t cut in the middle of a UTF-8 character
    while True:
        try:
            decoded = truncated.decode('utf-8')
            break
        except UnicodeDecodeError:
            truncated = truncated[:-1]
    return decoded + "..."


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

