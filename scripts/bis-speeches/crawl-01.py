#!/usr/bin/env python3
"""
Extract BIS Central Bankers' Speeches filter URLs for a list of authors.

pip install playwright pandas
python -m playwright install

Usage:
cls &&    python ./scripts/bis-speeches/crawl-01.py --input "./ecb-members-input.csv" --output "./ecb-members-urls.csv" [--headless true]
cls &&    python ./scripts/bis-speeches/crawl-01.py --input "./ecb-members-input.csv" --output "./ecb-members-urls.csv"  --headless false


"""

import argparse
import sys
import os
from   pathlib import Path
import csv


from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# importing from ../../lib/trls.py
parentDir = Path(__file__).resolve().parent.parent.parent
libPath = parentDir / "lib"
sys.path.insert(0, str(libPath))
from util import stackTrace



urlMain = "https://www.bis.org/speeches/central-bank"


def inputCsv(pthInp: Path):


    rows = []

    try:

        """
        excel put a UTF-8 BOM marker at the start of the file     
          \ufeff  an invisible Unicode character 

          utf-8-sig  deals with this
        """

        with pthInp.open("r", encoding="utf-8-sig", newline="") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for idx2, row in enumerate(reader):
                rows.append(row)
    except Exception as exc:
        stackTrace(exc)
        print("Failed to read CSV")


    if not rows or len(rows) < 3:
        print(f"CSV-1 is empty.")
        sys.exit(-1)

    print(f"\tfound {len(rows)} rows in {pthInp}")


    for idx1, row in enumerate(rows):
        print(f"\t ",end="")
        for idx2, key in enumerate(row):
            if row[key] is None:
                continue
            if row[key].strip() == "":
                continue
            if key == "url":
                continue

            if key == "name":
                print(f"{key}: {row[key]:28}", end=", ")
            else:
                print(f"{key}: {row[key]}", end=", ")

        print("")
        if idx1>4:
            break


    return rows



def previousCsv(pthPrev: Path):

    byName = {}
    if not pthPrev.exists():
        print(f"did not find previous file: {pthPrev}")
        sys.exit(-1)
        return byName

    try:
        with pthPrev.open("r", encoding="utf-8-sig", newline="") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")

            print(f"\tlooking for previous records in  {pthPrev}")

            for idx2, row in enumerate(reader):
                # print( row )
                nm = row.get("name", "").strip()
                if nm != "":
                    if idx2<4:
                        print(f"\t name: {nm}")
                    byName[nm] = row

            print(f"\tfound   {len(byName)} recs")


        if len(byName) < 3:
            print(f"CSV-2 is empty.")
            sys.exit(-1)


    except Exception as exc:
        stackTrace(exc)
        print("failed to read previous CSV")
    

    return byName


def getResultUrlForAuthor(page, nm: str) -> str:

    try:
        page.goto(urlMain, wait_until="domcontentloaded", timeout=15000)
    except PlaywrightTimeoutError:
        print(f"\t      Timeout: failed to load urlMain {urlMain}")
        return None
    except Exception as exc:
        stackTrace(exc)
        print(f"\t      Error: failed to load urlMain {urlMain}")
        return None

    # Step 1: click the drop down symbol
    try:
        selectTrigger = page.locator(".select-pure__select").first
        selectTrigger.click(timeout=5000, force=True)
    except PlaywrightTimeoutError:
        print(f"\t      Timeout: Step 1 - clicking dropdown trigger")
        return None
    except Exception as exc:
        stackTrace(exc)
        print(f"\t      Error: Step 1 - clicking dropdown trigger")
        return None

    # HERE 16 Seconds timeout is CRITICAL
    # Step 2: wait for opened state
    try:
        page.wait_for_selector(".select-pure__select--opened", state="attached", timeout=16000)
    except PlaywrightTimeoutError:
        print(f"\t      Timeout: Step 2 - waiting for dropdown to open")
        return None
    except Exception as exc:
        stackTrace(exc)
        print(f"\t      Error: Step 2 - waiting for dropdown to open")
        return None

    # Step 3: input characters
    try:
        searchInput = page.locator("input.select-pure__autocomplete").first
        searchInput.fill(nm, timeout=5000)
        page.wait_for_timeout(1000)
    except PlaywrightTimeoutError:
        print(f"\t      Timeout: Step 3 - filling search input")
        return None
    except Exception as exc:
        stackTrace(exc)
        print(f"\t      Error: Step 3 - filling search input")
        return None

    # Step 4: wait for and click on the filtered option
    try:
        firstOption = page.locator(".select-pure__option:visible").first
        # if this times out, the author is likely not in the list
        firstOption.wait_for(state="visible", timeout=4000)
        firstOption.click(timeout=5000, force=True)
    except PlaywrightTimeoutError:
        print(f"\t      author not found in dropdown (or timeout filtering): {nm}")
        return None
    except Exception as exc:
        stackTrace(exc)
        print(f"\t      Error: Step 4 - clicking filtered option")
        return None

    # Step 5: wait for URL change via auto-submit
    targetUrl = None
    try:
        for idx1, i in enumerate(range(8)):
            page.wait_for_timeout(1000)
            current = page.url
            if "person%5B%5D=" in current or "person[]=" in current:
                targetUrl = current
                break
    except Exception as exc:
        stackTrace(exc)
        print(f"\t      exception while waiting for URL change")
        return None

    # Step 6: fallback to Apply button if auto-submit did not trigger navigation
    if targetUrl is None:
        try:
            applyButton = page.locator('input[value="Apply"]').first
            if applyButton.is_visible(timeout=2000):
                applyButton.click(timeout=5000)
                for idx1, i in enumerate(range(5)):
                    page.wait_for_timeout(1000)
                    current = page.url
                    if "person%5B%5D=" in current or "person[]=" in current:
                        targetUrl = current
                        break
            else:
                print(f"\t      Apply button not found and auto-submit failed")
                return None
        except PlaywrightTimeoutError:
            print(f"\t      Timeout: Step 6 - clicking Apply button")
            return None
        except Exception as exc:
            stackTrace(exc)
            print(f"\t      Error: Step 6 - clicking Apply button")
            return None

    if targetUrl is None:
        print(f"\t      target url did not change to expected format")
        return None

    return targetUrl


def spaceVariants(nm: str):
    exoticSpaces = [" ", "\u00A0", "\u202F"]
    exoticSpaces = [" "]

    variations = []
    for idx1, sp in enumerate(exoticSpaces):
        parts = nm.split(" ")
        if len(parts) >= 2:
            rebuilt = sp.join(parts)
            variations.append(rebuilt)
        else:
            variations.append(nm)

    return variations


def printExotic(s: str):
    # Map exotic spaces to readable symbols
    mapping = {
        "\u00A0": "␣(NBSP)",     # non-breaking space
        "\u202F": "␣(NNBSP)",    # narrow no-break space
        "\u2007": "␣(FIGURE)",   # figure space
        "\u2009": "␣(THIN)",     # thin space
        "\u200A": "␣(HAIR)",     # hair space
        "\u200B": "␣(ZWSP)",     # zero-width space
        "\u2060": "␣(WJ)",       # word joiner
        "\u3000": "␣(IDEOGRAPHIC)" # full-width space
    }

    return s.translate(str.maketrans(mapping))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  required=True,    help="Path to the semicolon-delimited CSV")
    parser.add_argument("--output", required=True,    help="Path to write a CSV with columns: name;url;status;error")
    parser.add_argument("--headless", default="true", help="Run browser headless: true/false")
    args = parser.parse_args()

    inpPth   = Path(args.input).expanduser().resolve()
    outPth   = Path(args.output).expanduser().resolve()
    headless = str( args.headless).strip().lower() == "true"

    rows  = inputCsv(inpPth)
    prevs = previousCsv(outPth)
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page    = context.new_page()

        timeOut1 = 180*1000
        print(f"browser opened - loading {urlMain} ...  {timeOut1/1000}s", end="\n", flush=True)
        page.goto(urlMain, wait_until="domcontentloaded",     timeout=timeOut1)
        print("\tok", flush=True)

        timeOut2 = 10*1000
        print(f"waiting for selector... {timeOut2/1000}s ", end="\n", flush=True)

        # waiting for the new select-pure component to be attached to the DOM
        page.wait_for_selector(".select-pure__select", state="attached", timeout= timeOut2)
        print("\tok", flush=True)

        for idx1, row in enumerate(rows):
            try:
                nameNrm = row.get("name", "").strip()
                nameBis = row.get("name_bis", "").strip()

                if nameNrm.strip() == "":
                    print(f"name is empty")
                    print(f"row {row}")
                    sys.exit(-1)
                
                print(f"\t{idx1:3} processing {nameNrm}")
                
                existingRow = prevs.get(nameNrm, {})
                url = existingRow.get("url", "").strip()

                searchName = nameNrm
                if nameBis != "" and nameBis != "NA":
                    searchName = nameBis

                if len(url) > 30:
                    print(f"\t      skipping existing url \n\t      {url}")
                    newRow = row.copy()
                    newRow["url"] = url
                    newRow["status"] = existingRow.get("status", "ok")
                    newRow["error"] = existingRow.get("error", "")
                    results.append(newRow)
                    continue

                url = getResultUrlForAuthor(page, searchName)

                if url:
                    print(f"\t      success -> {url}")
                else:
                    print(f"\t      failed")

                newRow = row.copy()
                newRow["url"] = url if url else ""
                newRow["status"] = "ok" if url else "error"
                newRow["error"] = "" if url else "URL not found"
                results.append(newRow)

            except Exception as exc:
                stackTrace(exc)
                print(f"\t      main loop error for {nameNrm}")
                newRow = row.copy()
                newRow["url"] = ""
                newRow["status"] = "error"
                newRow["error"] = str(exc)
                results.append(newRow)

        browser.close()


    with outPth.open("w", encoding="utf-8-sig", newline="") as csvfile:
        if len(results) > 0:
            fieldnames = list(results[0].keys())
        else:
            fieldnames = ["name", "url", "status", "error"]
            
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for idx1, row in enumerate(results):
            writer.writerow(row)


if __name__ == "__main__":
    scriptDir = Path(__file__).resolve().parent
    os.chdir(scriptDir)
    print(f"\t{Path(__file__)} start")
    main()
    print(f"\t{Path(__file__)} end")