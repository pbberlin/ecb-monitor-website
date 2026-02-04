#!/usr/bin/env python3

import json
import re
import subprocess
import sys
from pathlib import Path


DATA_DIR = Path.cwd() / "."
MIN_TOP_LEVEL_KEYS = 10
MIN_NESTED_KEYS    = 10


# zabbix_sender, port 10050
ZABBIX_SERVER = "monitor2.zew.de"
ZABBIX_HOST   = "ecb-monitor.zew.de"             # must match host in Zabbix
# for zabbix_sender - we need to create a zabbix trapper item
# http://monitor2.zew.de/zabbix/zabbix.php?action=item.list&filter_set=1&filter_hostids%5B%5D=10672&context=host
ZABBIX_KEY    = "crawling.status"                # create an item with this key (trapper or use sender-to-agent)


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
        print(f"[ERROR] Failed to read {jsPath}: {exc}", file=sys.stderr)
        return False

    try:
        jsonText = extractJsonFromJs(jsText)
    except Exception as exc:
        print(f"[ERROR] Failed to extract JSON from {jsPath}: {exc}", file=sys.stderr)
        return False

    try:
        jsDta = json.loads(jsonText)
    except Exception as exc:
        print(f"[ERROR] JSON parse error in {jsPath}: {exc}", file=sys.stderr)
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

        if isinstance(jsDta, dict):
            val1 = jsDta[key1]
        elif isinstance(jsDta, list):
            val1 = jsDta[0]

        if Path(jsPath).name == "council-by-6weeks.js":
            MIN_NESTED_KEYS = 3
        if Path(jsPath).name == "council-tempomat.js":
            MIN_NESTED_KEYS = 4


        keys2 = list(val1.keys())
        if len(keys2) < MIN_NESTED_KEYS:
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
    Use zabbix_sender to push a 0/1 into Zabbix.
    statusValue: 1 = OK, 0 = failure
    """
    commandList = [
        "zabbix_sender",
        "-vv", 
        "-z",
        ZABBIX_SERVER,
        "-s",
        ZABBIX_HOST,
        "-k",
        ZABBIX_KEY,
        "-o",
        str(statusValue),
    ]

    try:
        completedProcess = subprocess.run(
            commandList,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        print(f"[ERROR] Failed to run zabbix_sender: {exc}", file=sys.stderr)
        return False

    if completedProcess.returncode != 0:
        print(
            f"[ERROR] zabbix_sender exited with {completedProcess.returncode}, "
            f"stdout='{completedProcess.stdout.strip()}', "
            f"stderr='{completedProcess.stderr.strip()}'",
            file=sys.stderr,
        )
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
            print(f"sending success to zabbix failed.")
            print(f"{exc}")
        sys.exit(0)

    else:
        print("[ERROR] One or more JS files failed validation", file=sys.stderr)
        sendStatusOk = sendStatusToZabbix(0)
        if not sendStatusOk:
            sys.exit(2)
        sys.exit(1)


if __name__ == "__main__":
    main()
