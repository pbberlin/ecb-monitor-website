#!/usr/bin/env python3
"""
Extract BIS Central Bankers' Speeches list-item URLs from the content area
for each input row that contains a BIS list URL like:
https://www.bis.org/cbspeeches/index.htm?authors=1106&m=256&cbspeeches_page_length=25

We do this with Playwright because parts of the list and filters are hydrated dynamically.

Important change for table-based lists:
The links live inside a <table class="documentList"> ... <div class="title"><a href="...">...</a></div>
We now target that table explicitly and collect only those anchors.

Usage:
pip install playwright beautifulsoup4
python -m playwright install

cls &&    python ./scripts/bis-speeches/crawl-02.py --input "./ecb-members-out.csv" --output "./ecb-members-links.csv" --headless false
cls &&    python ./scripts/bis-speeches/crawl-02.py --input "./ecb-members-out.csv" --output "./ecb-members-links.csv" [--headless true]

Notes:
- Input CSV must be semicolon-delimited and contain at least: name;url
- Output CSV is semicolon-delimited with columns: name;link_number;url
- The code focuses on the content area that shows "... items" and "Sort by ...", but extraction is now locked to the table.documentList structure.
"""

import argparse
import sys
import os
from   pathlib import Path
import csv
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


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
        print(f"\t",end="")
        for key in row:
            if row[key] is None:
                continue
            if row[key].strip() == "":
                continue
            if key == "url":
                continue
            print(f"{key}: {row[key]}", end=", ")
        print("")
        if idx>3:
            break

    return rows



def gotoAndWaitForContent(page, url: str):

    try:
        print(f"\t  loading {url}", end="... ")
        page.goto(url, wait_until="domcontentloaded", timeout=30*1000)
        page.wait_for_timeout(300)

        found = False

        try:
            locator = page.locator("text=/\\bSort\\s*by\\b/i")
            if locator.count() > 0:
                locator.first.wait_for(timeout=5*1000)
                found = True
        except Exception as exc:
            print(f"\nexc-wait-sortby  {exc}")

        if not found:
            try:
                locator2 = page.locator("text=/\\bitems\\b/i")
                if locator2.count() > 0:
                    locator2.first.wait_for(timeout=5*1000)
                    found = True
            except Exception as exc:
                print(f"\nexc-wait-items   {exc}")

        # Explicitly wait for the table that actually holds the links
        try:
            page.locator("table.documentList").first.wait_for(timeout=8*1000)
            found = True
        except Exception as exc:
            print(f"\nexc-wait-table   {exc}")

        if not found:
            try:
                page.locator("main, #content, div.content").first.wait_for(timeout=5*1000)
                found = True
            except Exception as exc:
                print(f"\nexc-wait-generic {exc}")

        print("done")
        return True
    except Exception as exc:
        print(f"exc-goto  {exc}")
        return False



def isLikelyListLink(href: str, text: str) -> bool:

    try:
        if href is None:
            return False

        h = href.strip()
        if len(h) == 0:
            return False

        if h.startswith("#"):
            return False

        if h.lower().startswith("javascript:"):
            return False

        # enforce BIS domain or relative links
        if h.startswith("/"):
            pass
        else:
            netloc = urlparse(h).netloc.lower()
            if "bis.org" not in netloc:
                return False

        t = (text or "").strip()
        if len(t) == 0:
            return False

        hl = h.lower()

        # For cbspeeches (BIS), detail pages often live under /review/ or /cbspeeches/
        if ("cbspeeches" in hl) or ("/review/" in hl) or ("/speeches/" in hl):
            return True

        return False
    except Exception as exc:
        print(f"exc-isLikelyListLink  {exc}")
        return False



def extractListUrlsFromRenderedHtml(html: str, baseUrl: str) -> list:

    urls = []

    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as exc:
        print(f"exc-BeautifulSoup  {exc}")
        return urls

    root = None

    # Prefer the explicit table with class documentList
    try:
        root = soup.select_one("table.documentList")
    except Exception as exc:
        print(f"exc-select-table  {exc}")
        root = None

    if root is None:
        try:
            sortByNode = soup.find(string=re.compile(r"\bSort\s*by\b", flags=re.I))
            if sortByNode is not None:
                node = sortByNode.parent
                root  = node
                parent = node.parent
                if parent is not None:
                    root = parent
        except Exception as exc:
            print(f"exc-find-sortby  {exc}")

    if root is None:
        try:
            for sel in ["main", "#content", "div.content", "div.container", "div#page-content", "div#main", "body"]:
                hit = soup.select_one(sel)
                if hit is not None:
                    root = hit
                    break
        except Exception as exc:
            print(f"exc-select-root  {exc}")
            root = soup

    anchors = []

    # Strict: only anchors inside the title cells of the list table
    try:
        titleLinks = root.select("tr.item td div.title a[href]")
        for a in titleLinks:
            anchors.append(a)
    except Exception as exc:
        print(f"exc-select-titlelinks  {exc}")

    # Fallback: any anchor inside the table (still filtered by isLikelyListLink)
    if len(anchors) == 0:
        try:
            for a in root.find_all("a"):
                anchors.append(a)
        except Exception as exc:
            print(f"exc-find_all-a  {exc}")
            return urls

    rawUrls = []
    for a in anchors:
        try:
            href = a.get("href", "")
            txt  = a.get_text(strip=True)
            if isLikelyListLink(href, txt):
                absUrl = urljoin(baseUrl, href)
                rawUrls.append(absUrl)
        except Exception as exc:
            print(f"exc-collect-a  {exc}")

    seen = set()
    deduped = []
    for u in rawUrls:
        if u not in seen:
            deduped.append(u)
            seen.add(u)

    return deduped



def writeOutputCsv(outputPath: Path, rowsOut: list):

    try:
        with outputPath.open("w", encoding="utf-8", newline="") as csvfile:
            fieldnames = ["name", "link_number", "url"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            for row in rowsOut:
                writer.writerow(row)
    except Exception as exc:
        print(f"exc-writeOutputCsv  {exc}")



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,  help="Path to the semicolon-delimited CSV with columns: name;url;...")
    parser.add_argument("--output", required=True, help="Path to write a CSV with columns: name;link_number;url")
    parser.add_argument("--headless", default="true", help="true|false")
    args = parser.parse_args()

    inpPth = Path(args.input).expanduser().resolve()
    outPth = Path(args.output).expanduser().resolve()

    headless = True
    if isinstance(args.headless, str):
        v = args.headless.strip().lower()
        if v in ["false", "0", "no", "f"]:
            headless = False

    rows = readInputCsv(inpPth)
    results = []

    with sync_playwright() as pw:

        try:
            browser = pw.chromium.launch(headless=headless)
        except Exception as exc:
            print(f"exc-launch  {exc}")
            sys.exit(1)

        try:
            context = browser.new_context()
            page    = context.new_page()
        except Exception as exc:
            print(f"exc-context  {exc}")
            browser.close()
            sys.exit(1)

        for idx, row in enumerate(rows):

            try:
                name = row.get("name", "").strip()
                url  = row.get("url",  "").strip()

                if len(url) < 10:
                    print(f"\t    {idx:2}  skipping - no url for  {name}")
                    continue

                ok = gotoAndWaitForContent(page, url)
                if not ok:
                    print(f"\t    {idx:2}  failed to load content  {name}")
                    continue

                try:
                    html = page.content()
                except Exception as exc:
                    print(f"\t    {idx:2}  exc-page.content  {exc}")
                    continue

                linkUrls = extractListUrlsFromRenderedHtml(html, url)

                if len(linkUrls) == 0:
                    print(f"\t    {idx:2}  no list links found    {name}")
                else:
                    print(f"\t    {idx:2}  found {len(linkUrls):3} links  {name}")

                ln = 0
                for u in linkUrls:
                    ln = ln + 1
                    results.append({
                        "name":         name,
                        "link_number":  ln,
                        "url":          u
                    })

            except Exception as exc:
                print(f"exc-main-loop  {exc}")

        try:
            context.close()
            browser.close()
        except Exception as exc:
            print(f"exc-close  {exc}")

    writeOutputCsv(outPth, results)



if __name__ == "__main__":
    scriptDir = Path(__file__).resolve().parent
    os.chdir(scriptDir)
    print(f"\t{Path(__file__)} start")
    main()
    print(f"\t{Path(__file__)} end")
