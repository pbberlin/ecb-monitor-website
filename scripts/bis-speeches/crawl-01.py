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

from playwright.sync_api import sync_playwright

# importing from ../../lib/trls.py
parentDir = Path(__file__).resolve().parent.parent.parent
libPath = parentDir / "lib"
sys.path.insert(0, str(libPath))
from util import stackTrace



urlMain = "https://www.bis.org/cbspeeches/index.htm"


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
        # navigate fresh for each author to clear prior filters
        print(f"loading {urlMain}", end="... ")
        # page.goto( url, wait_until="networkidle", timeout=20*1000)
        # page.goto( url, wait_until="load", timeout=20*1000)
        page.goto( urlMain, wait_until="domcontentloaded", timeout=20*1000)
        print("done")
    except Exception as exc:
        stackTrace(exc)
        print(f"failed to load urlMain {urlMain}")
        return None


    """
        Try to open the "Author" (or "Autor") select widget.
        The BIS site uses a Select2 widget. We make several attempts to locate and interact with it.
        Strategy:
        1) Click the Author dropdown by label text "Author" or "Autor".
        2) Type the full name and press Enter to select the first match.
        3) Wait for the page to update its URL (navigation with query parameters) and then read page.url.

    <input class="select2-search__field" type="search"
    """


    try:

        selectTrigger = page.locator(".select2-selection").first
        selectTrigger.click(timeout=10000)
        print(f"\t  clicked select2 trigger for {nm}")
        page.wait_for_timeout(500)

        searchInput = page.locator("css=input.select2-search__field").first
        print(f"\t  found search input for {nm}")

        searchInput.fill(nm, timeout=10000)
        print(f"\t  filled        {printExotic(nm)}")


        page.wait_for_timeout(1500)
        print(f"\t  populated     {printExotic(nm)}")

        # Press Enter to choose the first match
        searchInput.press("Enter")
        print(f"\t  enter pressed {printExotic(nm)}")


    except Exception as exc:
        stackTrace(exc)
        print(f"failed to interact with select2 for {nm}")
        return None

    # Wait for the URL to reflect the selection (authors=<id> present)
    # Sometimes the site updates content via pushState; we poll page.url.
    targetUrl = None
    try:
        for idx1, i in enumerate(range(5)):
            print(f"\t  waiting for forward/reload {i:2}")
            page.wait_for_timeout(1250)

            current = page.url
            if "authors=" in current:
                targetUrl = current
                break

        if targetUrl is None:
            # As a fallback, look for a "Go" or "Apply" filter button and click it
            try:
                applyButton = page.get_by_role("button", name="Apply")
                if applyButton.is_visible():
                    applyButton.click()
                    page.wait_for_load_state("networkidle", timeout=20000)
                    if "authors=" in page.url:
                        targetUrl = page.url
            except Exception as exc:
                stackTrace(exc)
                print("Apply button not found/usable")

    except Exception as exc:
        stackTrace(exc)
        print("exception in apply button pressing")
        return None


    if targetUrl is None:
        print(f"\t  target url is None")
        return None


    parsed = urlparse(targetUrl)
    queryPairs = dict(parse_qsl(parsed.query, keep_blank_values=True))

    if "m" not in queryPairs:
        queryPairs["m"] = "256"
    if "cbspeeches_page_length" not in queryPairs:
        queryPairs["cbspeeches_page_length"] = "25"

    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        urlencode(queryPairs, doseq=True),
        parsed.fragment
    ))

    return normalized


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

        page.wait_for_selector("input.select2-search__field", timeout= timeOut2)
        print("\tok", flush=True)

        for idx1, row in enumerate(rows):
            try:
                nameNrm = row.get("name", "").strip()
                nameBis = row.get("name_bis", "").strip()

                if nameNrm.strip() == "":
                    print(f"name is empty")
                    print(f"row {row}")
                    sys.exit(-1)
                
                existingRow = prevs.get(nameNrm, {})
                url = existingRow.get("url", "").strip()

                searchName = nameNrm
                if nameBis != "" and nameBis != "NA":
                    searchName = nameBis

                if len(url) > 30:
                    print(f"\t  {idx1:2}  skipping existing url  {nameNrm} \n\t      {url}")
                    newRow = row.copy()
                    newRow["url"] = url
                    newRow["status"] = existingRow.get("status", "ok")
                    newRow["error"] = existingRow.get("error", "")
                    results.append(newRow)
                    continue

                url = getResultUrlForAuthor(page, searchName)

                # exotic spaces were *not* the reason - but page was not ready 

                # if url is None:
                #     for idx2, nm in enumerate(spaceVariants(searchName)):
                #         url = getResultUrlForAuthor(page, nm)
                #         if url is not None:
                #             break

                print(f"\t  {idx1:2}  success for  {nameNrm} - {url}")

                newRow = row.copy()
                newRow["url"] = url if url else ""
                newRow["status"] = "ok" if url else "error"
                newRow["error"] = "" if url else "URL not found"
                results.append(newRow)

            except Exception as exc:
                stackTrace(exc)
                print("main loop error")
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
