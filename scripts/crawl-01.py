#!/usr/bin/env python3
"""
Extract BIS Central Bankers' Speeches filter URLs for a list of authors.

pip install playwright pandas
python -m playwright install

Usage:
cls &&    python crawl-01.py --input "./ecb-members.csv" --output "./ecb-members-out.csv" [--headless true]
cls &&    python crawl-01.py --input "./ecb-members.csv" --output "./ecb-members-out.csv" --headless false


"""

import argparse
import sys
from   pathlib import Path
import csv


from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from playwright.sync_api import sync_playwright


urlMain = "https://www.bis.org/cbspeeches/index.htm"


def readInputCsv(inputPath: Path):

    lastError = None
    rows = []

    for enc in ["utf-8"]:
        try:
            with inputPath.open("r", encoding=enc, newline="") as csvfile:
                reader = csv.DictReader(csvfile, delimiter=";")
                for row in reader:
                    rows.append(row)
            break
        except Exception as e:
            lastError = e

    if not rows:
        print("Failed to read CSV. Last error: {}".format(lastError))
        sys.exit(1)

    print(f"found {len(rows)} rows")
    for idx, row in enumerate(rows):
        print(f"\t{row}")
        if idx>3:
            break

    return rows



def getResultUrlForAuthor(page, nm: str) -> str:

    try:
        # navigate fresh for each author to clear prior filters
        print(f"loading {urlMain}", end="... ")
        # page.goto( url, wait_until="networkidle", timeout=20*1000)
        # page.goto( url, wait_until="load", timeout=20*1000)
        page.goto( urlMain, wait_until="domcontentloaded", timeout=20*1000)
        print("done")
    except Exception as exc:
        print (f"exc1 -  {exc}")
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
        searchInput = page.locator("css=input.select2-search__field").first
        print(f"\t  found search input for {printExotic(nm)}")

        searchInput.fill(nm, timeout=10000)
        print(f"\t  filled {printExotic(nm)}")


        page.wait_for_timeout(1500)
        print(f"\t  populated {printExotic(nm)}")

        # Press Enter to choose the first match
        searchInput.press("Enter")
        print(f"\t  enter pressed {printExotic(nm)}")


    except Exception as exc:
        print(f"exc2 {exc}")
        return None

    # Wait for the URL to reflect the selection (authors=<id> present)
    # Sometimes the site updates content via pushState; we poll page.url.
    targetUrl = None
    try:
        for i in range(5):
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
                print("Apply button not found/usable: {}".format(exc))

    except Exception as exc:
        print(f"exc3 {exc}")
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
    for sp in exoticSpaces:
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

    outChars = []
    for ch in s:
        if ch in mapping:
            outChars.append(mapping[ch])
        else:
            outChars.append(ch)

    return "".join(outChars) 


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,     help="Path to the semicolon-delimited CSV")
    parser.add_argument("--output", required=True,    help="Path to write a CSV with columns: name;url;status;error")
    parser.add_argument("--headless", default="true", help="Run browser headless: true/false")
    args = parser.parse_args()

    inpPth   = Path(args.input).expanduser().resolve()
    outPth   = Path(args.output).expanduser().resolve()
    headless = str(args.headless).strip().lower() == "true"

    rows = readInputCsv(inpPth)
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page    = context.new_page()
        print(f"browser started - warming up... ", end=" ", flush=True)
        page.goto(urlMain, wait_until="domcontentloaded",     timeout=30*1000)
        page.wait_for_selector("input.select2-search__field", timeout=10*1000)
        print("ok", flush=True)

        for idx, row in enumerate(rows):
            try:
                name = row.get("name", "").strip()
                url  = row.get("url",  "").strip()

                if len(url) > 30:
                    print(f"\t  {idx:2}  skipping existing url  {name} - {url}")
                    results.append({"name": name, "url": url, "status": "ok", "error": ""})
                    continue

                url = getResultUrlForAuthor(page, name)

                # exotic spaces were *not* the reason - but page was not ready 

                # if url is None:
                #     for nm in spaceVariants(name):
                #         url = getResultUrlForAuthor(page, nm)
                #         if url is not None:
                #             break

                print(f"\t  {idx:2}  success for  {name} - {url}")


                results.append({"name": name, "url": url, "status": "ok", "error": ""})

            except Exception as exc:
                print(f" {exc}")
                results.append({"name": name, "url": "", "status": "error", "error": str(exc)})

        browser.close()

    with outPth.open("w", encoding="utf-8", newline="") as csvfile:
        fieldnames = ["name", "url", "status", "error"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for row in results:
            writer.writerow(row)

if __name__ == "__main__":
    main()
