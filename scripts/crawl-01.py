#!/usr/bin/env python3
"""
Extract BIS Central Bankers' Speeches filter URLs for a list of authors.

Usage:
  python bis_cbspeeches_urls.py --input "/path/to/file.csv" --output "/path/to/output.csv" [--headless true]

    pip install playwright pandas
    python -m playwright install
"""

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

from playwright.sync_api import sync_playwright

def readInputCsv(inputPath: Path) -> pd.DataFrame:
    encodingsToTry = ["utf-8-sig", "latin-1", "cp1252"]
    lastError = None
    df = None

    for enc in encodingsToTry:
        try:
            df = pd.read_csv(inputPath, sep=";", dtype=str, encoding=enc, engine="python")
            break
        except Exception as e:
            lastError = e

    if df is None:
        print("Failed to read CSV. Last error: {}".format(lastError))
        sys.exit(1)

    return df

def pickNameColumn(df: pd.DataFrame) -> str:
    candidateCols = []
    for col in df.columns:
        lowerCol = str(col).strip().lower()
        if lowerCol == "name":
            candidateCols.append(col)
        if lowerCol == "author":
            candidateCols.append(col)
        if lowerCol == "autor":
            candidateCols.append(col)
        if lowerCol == "speaker":
            candidateCols.append(col)

    if len(candidateCols) == 0:
        return df.columns[0]
    else:
        return candidateCols[0]

def getResultUrlForAuthor(page, authorName: str) -> str:
    # Navigate fresh for each author to clear prior filters
    page.goto("https://www.bis.org/cbspeeches/index.htm", wait_until="networkidle", timeout=60000)

    # Try to open the "Author" (or "Autor") select widget.
    # The BIS site uses a Select2 widget. We make several attempts to locate and interact with it.
    # Strategy:
    #  1) Click the Author dropdown by label text "Author" or "Autor".
    #  2) Type the full name and press Enter to select the first match.
    #  3) Wait for the page to update its URL (navigation with query parameters) and then read page.url.
    potentialLabels = ["Author", "Autor"]
    opened = False
    for labelText in potentialLabels:
        try:
            # Click the select2 container associated with the label
            labelLocator = page.locator("label", has_text=labelText).first
            container = labelLocator.locator("xpath=..").locator("css=span.select2").first
            container.click(timeout=5000)
            opened = True
            break
        except Exception as e:
            print("Could not open dropdown via label '{}': {}".format(labelText, e))

    if not opened:
        # Fallback: try any visible Select2 container on the page
        try:
            page.locator("css=span.select2").first.click(timeout=5000)
            opened = True
        except Exception as e:
            print("Could not open any select2 dropdown: {}".format(e))

    if not opened:
        raise RuntimeError("Failed to open Author selector")

    # Type the name into the Select2 search input and select the first option
    try:
        searchInput = page.locator("css=input.select2-search__field").first
        searchInput.fill(authorName, timeout=10000)
        # Give suggestions time to populate
        page.wait_for_timeout(500)
        # Press Enter to choose the first match
        searchInput.press("Enter")
    except Exception as e:
        raise RuntimeError("Failed to search/select author '{}': {}".format(authorName, e))

    # Wait for the URL to reflect the selection (authors=<id> present)
    # Sometimes the site updates content via pushState; we poll page.url.
    targetUrl = None
    try:
        for i in range(60):
            current = page.url
            if "authors=" in current:
                targetUrl = current
                break
            page.wait_for_timeout(250)
        if targetUrl is None:
            # As a fallback, look for a "Go" or "Apply" filter button and click it
            try:
                applyButton = page.get_by_role("button", name="Apply")
                if applyButton.is_visible():
                    applyButton.click()
                    page.wait_for_load_state("networkidle", timeout=20000)
                    if "authors=" in page.url:
                        targetUrl = page.url
            except Exception as e:
                print("Apply button not found/usable: {}".format(e))
    except Exception as e:
        raise RuntimeError("Error while waiting for filtered URL for '{}': {}".format(authorName, e))

    if targetUrl is None:
        raise RuntimeError("Timed out waiting for authors parameter in URL for '{}'".format(authorName))

    # Normalize to include m=256 and page length where missing
    # If m=256 or cbspeeches_page_length are absent, we add them without breaking the rest.
    from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to the semicolon-delimited CSV")
    parser.add_argument("--output", required=True, help="Path to write a CSV with columns: name;url;status;error")
    parser.add_argument("--headless", default="true", help="Run browser headless: true/false")
    args = parser.parse_args()

    inputPath = Path(args.input).expanduser().resolve()
    outputPath = Path(args.output).expanduser().resolve()
    headless = str(args.headless).strip().lower() == "true"

    df = readInputCsv(inputPath)
    nameCol = pickNameColumn(df)

    names = df[nameCol].fillna("").astype(str).str.strip()
    names = names[names != ""]

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        for idx, authorName in enumerate(names):
            try:
                url = getResultUrlForAuthor(page, authorName)
                results.append({"name": authorName, "url": url, "status": "ok", "error": ""})
                print("[{}/{}] {} -> {}".format(idx + 1, len(names), authorName, url))
            except Exception as e:
                err = str(e)
                print("[{}/{}] {} -> ERROR: {}".format(idx + 1, len(names), authorName, err))
                results.append({"name": authorName, "url": "", "status": "error", "error": err))

        browser.close()

    # Write output (semicolon-delimited as requested)
    outDf = pd.DataFrame(results, columns=["name", "url", "status", "error"])
    outDf.to_csv(outputPath, sep=";", index=False, encoding="utf-8")

if __name__ == "__main__":
    main()
