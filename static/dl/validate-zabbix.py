#!/usr/bin/env python3

import json
import re
import subprocess
import sys
from pathlib import Path


DATA_DIR = Path.cwd() / "."
MIN_TOP_LEVEL_KEYS = 10
MIN_NESTED_KEYS    = 10

ZABBIX_SERVER = "http://monitor2.zew.de/zabbix/"      # adjust
ZABBIX_SERVER = "monitor2.zew.de"
# port is 10051 or 10050  
ZABBIX_HOST   = "ecb-monitor.zew.de"                  # must match host in Zabbix
ZABBIX_KEY    = "data.pipeline.status"                # create an item with this key (trapper or use sender-to-agent)

"""
    powershell
    Test-NetConnection -ComputerName monitor2.zew.de -Port 10050
    Test-NetConnection -ComputerName monitor2.zew.de -Port 10051


"""



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
        dataObject = json.loads(jsonText)
    except Exception as exc:
        print(f"[ERROR] JSON parse error in {jsPath}: {exc}", file=sys.stderr)
        return False

    if not isinstance(dataObject, dict):
        print(f"[ERROR] Top-level object in {jsPath} is not a dict", file=sys.stderr)
        return False

    topLevelKeys = list(dataObject.keys())
    if len(topLevelKeys) < MIN_TOP_LEVEL_KEYS:
        print(f"[ERROR] {jsPath} has only {len(topLevelKeys)} top-level keys", file=sys.stderr)
        return False

    for idx1, currentKey in enumerate(topLevelKeys):
        currentValue = dataObject[currentKey]

        if not isinstance(currentValue, dict):
            print(f"[ERROR] Value for key '{currentKey}' in {jsPath} is not a dict", file=sys.stderr)
            return False

        nestedKeys = list(currentValue.keys())
        if len(nestedKeys) < MIN_NESTED_KEYS:
            print(
                f"[ERROR] Value for key '{currentKey}' in {jsPath} "
                f"has only {len(nestedKeys)} nested keys",
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
        print(f"[INFO] Validating {jsPath}")
        isOk = validateJsFile(jsPath)
        if not isOk:
            allOk = False

    if allOk:
        print("[INFO] All JS files validated successfully")
        sendStatusOk = sendStatusToZabbix(1)
        if not sendStatusOk:
            sys.exit(2)
        sys.exit(0)
    else:
        print("[ERROR] One or more JS files failed validation", file=sys.stderr)
        sendStatusOk = sendStatusToZabbix(0)
        if not sendStatusOk:
            sys.exit(2)
        sys.exit(1)


if __name__ == "__main__":
    main()
