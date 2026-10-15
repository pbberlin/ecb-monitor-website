#!/usr/bin/env python3

import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

# resolving parent directory to import lib.util
parentDir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parentDir))
from lib.util import stackTrace

# resolving the data directory relative to the script's new location in ./scripts/
DATA_DIR = Path(__file__).resolve().parent.parent / "static" / "dl"
MIN_TOP_LEVEL_KEYS = 10
MIN_NESTED_KEYS    = 10


# zabbix api endpoint for https push
ZABBIX_SERVER    = "monitor2.zew.de"
ZABBIX_HOST      = "ecb-monitor.zew.de"             # must match host in Zabbix
# for history.push - we need to create a zabbix trapper item
# http://monitor2.zew.de/zabbix/zabbix.php?action=item.list&filter_set=1&filter_hostids%5B%5D=10672&context=host
ZABBIX_KEY       = "crawling.status"                # create an item with this key (trapper)
# generating api token in zabbix ui (users -> api tokens) to authorize history.push
ZABBIX_API_TOKEN = "ed7de1b8ff79efddfac725aeee04ffbf2562ee471694b0eba567279096620db7"


def extractJsonFromJs(jsText):
    """
    Assumes content like: var something = { ... };
    Returns the JSON string between '=' and the last ';'.
    """
    equalPos = jsText.find("=")
    if equalPos == -1:
        raise ValueError("No '=' found in JS content")

    jsonCandidate = jsText[equalPos + 1:].strip()

    if jsonCandidate.endswith(";"):
        jsonCandidate = jsonCandidate[:-1].strip()

    if not jsonCandidate:
        raise ValueError("No JSON content after '='")

    return jsonCandidate


def validateJsFile(jsPath):

    """
    Return True if valid enough, False otherwise.
    """

    try:
        jsText = jsPath.read_text(encoding="utf-8")
    except Exception as exc:
        stackTrace(exc)
        print(f"[ERROR] Failed to read {jsPath}", file=sys.stderr)
        return False

    try:
        jsonText = extractJsonFromJs(jsText)
    except Exception as exc:
        stackTrace(exc)
        print(f"[ERROR] Failed to extract JSON from {jsPath}", file=sys.stderr)
        return False

    try:
        jsDta = json.loads(jsonText)
    except Exception as exc:
        stackTrace(exc)
        print(f"[ERROR] JSON parse error in {jsPath}", file=sys.stderr)
        return False

    if not isinstance(jsDta, dict) and not isinstance(jsDta, list):
        print(f"[ERROR] Top-level object in {jsPath} is not a dict nor a list", file=sys.stderr)
        return False


    if isinstance(jsDta, dict):
        topLevelKeys = list(jsDta.keys())

    if isinstance(jsDta, list):
        topLevelKeys = jsDta
        # topLevelKeys = jsDta[0]


    if len(topLevelKeys) < MIN_TOP_LEVEL_KEYS:
        print(f"[ERROR] {jsPath} has only {len(topLevelKeys)} top-level keys", file=sys.stderr)
        return False


    for idx1, key1 in enumerate(topLevelKeys):

        if   isinstance(jsDta, dict):
            val1 = jsDta[key1]
        elif isinstance(jsDta, list):
            val1 = jsDta[0]

        minNestedLocal = MIN_NESTED_KEYS
        if Path(jsPath).name == "council-by-6weeks.js":
            minNestedLocal = 3
        if Path(jsPath).name == "council_barometer.js":
            minNestedLocal = 4
        if Path(jsPath).name == "eu-and-euro-countries.js":
            minNestedLocal = 4


        if type(val1) is list:
            val1 = val1[0]      # first element of list has dict
        else:
            keys2 = list(val1.keys())
            if len(keys2) < minNestedLocal:
                print(
                    f"[ERROR] Value for key '{key1}' in {jsPath} "
                    f"has only {len(keys2)} nested keys",
                    file=sys.stderr,
                )
                return False


    return True


def findJsFiles(dataDirPath):
    jsFileList = []

    for idx1, currentPath in enumerate(sorted(dataDirPath.glob("*.js"))):
        jsFileList.append(currentPath)

    return jsFileList


def sendStatusToZabbix(statusValue):
    """
    pushing 0/1 into zabbix via https json-rpc api (history.push).
    statusValue: 1 = OK, 0 = failure
    """

    # constructing api endpoint url based on provided zabbix server
    apiUrl = f"https://{ZABBIX_SERVER}/zabbix/api_jsonrpc.php"
    # apiUrl = f"http://{ZABBIX_SERVER}/zabbix/api_jsonrpc.php"

    # building json-rpc payload for history.push method
    # requiring zabbix 6.4+ and allowed ip in trapper item
    payloadDict = {
        "jsonrpc": "2.0",
        "method": "history.push",
        "params": [
            {
                "host": ZABBIX_HOST,
                "key": ZABBIX_KEY,
                "value": statusValue
            }
        ],
        "id": 1
    }

    try:
        payloadBytes = json.dumps(payloadDict).encode("utf-8")

        # preparing http request with correct content type for json-rpc
        # passing bearer token in authorization header to authenticate api call
        req = urllib.request.Request(
            apiUrl,
            data=payloadBytes,
            headers={
                "Content-Type": "application/json-rpc",
                "Authorization": f"Bearer {ZABBIX_API_TOKEN}"
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            respBytes = response.read()
            respDict  = json.loads(respBytes)

            # checking for api-level errors in response
            if "error" in respDict:
                print(f"[ERROR] zabbix api returned error: {respDict['error']}", file=sys.stderr)
                return False

    except Exception as exc:
        stackTrace(exc)
        print(f"[ERROR] failed pushing status to zabbix via https", file=sys.stderr)
        return False

    return True


def main():
    if not DATA_DIR.exists():
        print(f"[ERROR] Data dir does not exist: {DATA_DIR}", file=sys.stderr)
        sendStatusToZabbix(0)
        sys.exit(1)

    jsFileList = findJsFiles(DATA_DIR)

    if not jsFileList:
        print(f"[ERROR] No JS files found in {DATA_DIR}", file=sys.stderr)
        sendStatusToZabbix(0)
        sys.exit(1)

    allOk = True

    for idx1, jsPath in enumerate(jsFileList):
        print(f"\t  validating {jsPath}")

        isOk = validateJsFile(jsPath)
        if not isOk:
            allOk = False

    if allOk:
        print("\tall JS files validated successfully")
        try:
            sendStatusOk = sendStatusToZabbix(1)
            # if not sendStatusOk:
            #     sys.exit(2)
        except Exception as exc:
            stackTrace(exc)
            print(f"sending success to zabbix failed.")
        sys.exit(0)

    else:
        print("[ERROR] One or more JS files failed validation", file=sys.stderr)
        sendStatusOk = sendStatusToZabbix(0)
        if not sendStatusOk:
            sys.exit(2)
        sys.exit(1)


if __name__ == "__main__":
    main()