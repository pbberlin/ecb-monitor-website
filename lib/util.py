import pandas as pd

import os
import sys
import traceback
from   pathlib      import Path


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



def stackTrace(exc=None, lastX=2, printDirectly=True):
    """
        stackTrace() not part of the stacktrace
        traceback ends, where the exception *occurs*
    """

    if exc is None:
        exc = sys.exc_info()[1]

    cwd = os.getcwd()
    cwd = str(Path.cwd())

    lastX += 1  # dont show current helper func
    lastX += 2

    l = []

    extractedTrace = traceback.extract_tb(exc.__traceback__)
    # extractedTrace = list(reversed(extractedTrace[-lastX:]))
    extractedTrace = list(extractedTrace[-lastX:])

    lastFrames = extractedTrace[-lastX:]
    for idx1, frame in enumerate(lastFrames):
        line = f"\t{idx1:2d}: {frame.filename}:{frame.lineno} in {frame.name}"
        line = line.replace( cwd , "...")
        l.append( line )

    l.append( "\t-------")
    l.extend( traceback.format_exception_only(type(exc), exc) )

    s = "\n".join(l)

    if printDirectly:
        print(s)

    return s
