#!/usr/bin/env python3
"""
Read a CSV with at least columns: name,url
Fetch each URL with httpx.
Extract specified elements using BeautifulSoup.
Write one JSON per input row to the "out" directory using tlsl(name).json as filename.

Usage:
cls &&    python ./scripts/bis-speeches/crawl-03.py --input ./ecb-members-links.csv [--download-all]
"""

import argparse
import csv
import json
import os
import sys
import time
import random
import re
from   pathlib import Path
from   typing  import Dict, Any, Optional
from   datetime import datetime
import httpx
from   bs4     import BeautifulSoup

# add parent directory of scripts/ (i.e., appdir/) to import path
sys.path.append(str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parents[2]))
from lib.slugify_wrapper import tlsl
from lib.util import stackTrace


# --- CSV I/O --------------------------------------------------------------------

def readInputCsv(inputPath: Path) -> list[dict]:
    rows = []
    lastError: Optional[Exception] = None

    # try to sniff delimiter
    for idx1, enc in enumerate(["utf-8", "utf-8-sig"]):
        try:
            with inputPath.open("r", encoding=enc, newline="") as f:
                sample = f.read(4096)
                f.seek(0)
                try:
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(sample, delimiters=";,")
                except Exception as exc:
                    stackTrace(exc)
                    print("exc-csv-sniff")
                    dialect = csv.excel
                    dialect.delimiter = ";"

                reader = csv.DictReader(f, dialect=dialect)
                for idx2, row in enumerate(reader):
                    rows.append(row)
            break
        except Exception as exc:
            stackTrace(exc)
            print("exc-csv-read")
            lastError = exc

    if len(rows) == 0:
        print(f"Failed to read CSV. Last error: {lastError}")
        sys.exit(-1)
    else: 
        print(f"{len(rows)} rows in csv {inputPath} loaded")


    for idx1, row in enumerate(rows):
        print( f"\t  {row['name']} - {row['url']}")
        if idx1 > 3:
            break


    return rows


def ensureOutDir(outDir: Path) -> None:
    try:
        outDir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        stackTrace(exc)
        print("exc-mkdir")
        sys.exit(-1)



# --- HTTP fetch -----------------------------------------------------------------

def fetchUrl(client: httpx.Client, url: str, maxRetries: int = 3, backoffSeconds: float = 1.5) -> Optional[str]:
    attempt = 0
    while True:
        try:
            attempt = attempt + 1
            resp = client.get(url, timeout=30.0, follow_redirects=True)
            
            htmlLower = resp.text.lower()
            isCf = False
            
            for idx1, marker in enumerate(["just a moment...", "attention required!", "cf-challenge-running", "cf-please-wait"]):
                if marker in htmlLower:
                    isCf = True
                    break
            
            if isCf:
                print(f"\t      FATAL: Cloudflare challenge detected for {url} (HTTP {resp.status_code}). IP blocked.")
                sys.exit(-1)

            if resp.status_code >= 200 and resp.status_code < 300:
                return resp.text
            else:
                print(f"HTTP {resp.status_code} for {url}")
        except Exception as exc:
            stackTrace(exc)
            print("exc-httpx-get")

        if attempt >= maxRetries:
            return None

        try:
            time.sleep(backoffSeconds * attempt)
        except Exception as exc:
            stackTrace(exc)
            print("exc-sleep")


# --- Extraction helpers ---------------------------------------------------------

def extractDateFromUrl(url: str) -> Optional[str]:
    # BIS URLs typically contain the date in YYYYMMDD format right after /speeches/
    # e.g., https://www.bis.org/speeches/20260630-united-diversity...
    try:
        match = re.search(r"/(\d{4})(\d{2})(\d{2})-", url)
        if match:
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    except Exception as exc:
        stackTrace(exc)
        print("exc-extractDateFromUrl")
    return None


def getText(node) -> Optional[str]:
    try:
        if node is None:
            return None
        text = node.get_text(separator=" ", strip=True)
        if isinstance(text, str):
            if len(text.strip()) == 0:
                return None
            return text
        return None
    except Exception as exc:
        stackTrace(exc)
        print("exc-getText")
        return None


def getInnerHtml(node) -> Optional[str]:
    try:
        if node is None:
            return None
        html = node.decode_contents()
        if isinstance(html, str):
            if len(html.strip()) == 0:
                return None
            return html
        return None
    except Exception as exc:
        stackTrace(exc)
        print("exc-getInnerHtml")
        return None


def extractFields(html: str, url: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "source_url": url,
        "headline": None,
        "description_html": None,
        "description_text": None,
        "date": None,
        "pdf_url": None,
        "content_html": None,
        "content_text": None,
    }

    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as exc:
        stackTrace(exc)
        print("exc-bs4-parse")
        return result

    # headline
    headlineNode = None
    try:
        for idx1, sel in enumerate(["h1.hero-publication__heading", "h1.hero__heading", "h1"]):
            for idx2, node in enumerate(soup.select(sel)):
                headlineNode = node
                break
            if headlineNode:
                break
    except Exception as exc:
        stackTrace(exc)
        print("exc-headline")

    headlineText = getText(headlineNode)
    result["headline"] = headlineText

    # description
    descriptionNode = None
    descriptionHtml = None
    descriptionText = None
    try:
        for idx1, sel in enumerate(["article .fs-4", ".fs-4", ".publication-body .fs-4"]):
            for idx2, node in enumerate(soup.select(sel)):
                descriptionNode = node
                break
            if descriptionNode:
                break
        
        descriptionHtml = getInnerHtml(descriptionNode)
        descriptionText = getText(descriptionNode)
        
        if not descriptionText:
            for idx1, sel in enumerate(["meta[name='description']", "meta[property='og:description']"]):
                for idx2, node in enumerate(soup.select(sel)):
                    descriptionText = node.get("content")
                    break
                if descriptionText:
                    break
    except Exception as exc:
        stackTrace(exc)
        print("exc-desc-node")

    result["description_html"] = descriptionHtml
    result["description_text"] = descriptionText

    # date
    dateText = None
    try:
        for idx1, sel in enumerate(["meta[name='citation_publication_date']", "meta[property='article:published_time']"]):
            for idx2, node in enumerate(soup.select(sel)):
                dateText = node.get("content")
                break
            if dateText:
                break

        if not dateText:
            for idx1, node in enumerate(soup.select(".publication-sidebar__heading")):
                if "Date" in (node.get_text() or ""):
                    sibling = node.find_next_sibling("div", class_="publication-sidebar__tags")
                    if sibling:
                        dateText = getText(sibling)
                    break
    except Exception as exc:
        stackTrace(exc)
        print("exc-date-meta")

    result["date"] = dateText

    # Parse date to YYYY-MM-DD
    try:
        if dateText:
            dateText = dateText.strip()
            if len(dateText) >= 10 and dateText[4] == "-" and dateText[7] == "-":
                result["date_parsed"] = dateText[:10]
            else:
                parsedDate = datetime.strptime(dateText, "%d %B %Y")
                result["date_parsed"] = parsedDate.strftime("%Y-%m-%d")
        else:
            result["date_parsed"] = ""
    except Exception as exc:
        stackTrace(exc)
        print("exc-date-parse")
        result["date_parsed"] = ""


    # pdf_url
    pdfAnchor = None
    try:
        for idx1, node in enumerate(soup.select("a[href$='.pdf']")):
            pdfAnchor = node
            break
    except Exception as exc:
        stackTrace(exc)
        print("exc-pdf-node")

    pdfUrl = None
    try:
        if pdfAnchor is not None:
            href = pdfAnchor.get("href")
            if isinstance(href, str):
                if href.startswith("http://") or href.startswith("https://"):
                    pdfUrl = href
                else:
                    try:
                        from urllib.parse import urljoin
                        pdfUrl = urljoin(url, href)
                    except Exception as exc:
                        stackTrace(exc)
                        print("exc-pdf-urljoin")
                        pdfUrl = href
    except Exception as exc:
        stackTrace(exc)
        print("exc-pdf-href")

    result["pdf_url"] = pdfUrl

    # content
    contentNode = None
    try:
        for idx1, sel in enumerate(["article div.text__component", "div.text__component", "article"]):
            for idx2, node in enumerate(soup.select(sel)):
                contentNode = node
                break
            if contentNode:
                break
    except Exception as exc:
        stackTrace(exc)
        print("exc-content-node")

    contentHtml = getInnerHtml(contentNode)
    contentText = getText(contentNode)
    result["content_html"] = contentHtml
    result["content_text"] = contentText

    return result



# --- main -----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  required=True, help="Path to CSV with at least: name,url")
    parser.add_argument("--download-all", action="store_true", help="Override skip if file exists")
    args = parser.parse_args()

    inpPth = Path(args.input).expanduser().resolve()
    outDir = Path("./out")
    dlAll  = args.download_all

    ensureOutDir(outDir)

    rows = readInputCsv(inpPth)
    if len(rows) == 0:
        print("No rows in input.")
        sys.exit(-1)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    with httpx.Client(http2=True, headers=headers) as client:

        for idx1, row in enumerate(rows):

            try:
                name = ""
                url  = ""

                name = (row.get("name") or "").strip()
                url  = (row.get("url")  or "").strip()

                if len(url) < 8:
                    print(f"\t  {idx1:4}  skip (no url)  {name}")
                    continue

                slug = tlsl(name)
                urlDate = extractDateFromUrl(url)
                expectedFilename = None
                outPth = None

                # If we can derive the date from the URL, check if file exists before fetching
                if urlDate:
                    expectedFilename = f"{slug}-{urlDate}.json"
                    outPth = outDir / expectedFilename
                    if outPth.exists() and not dlAll:
                        print(f"\t  {idx1:4}  skip (exists)  {expectedFilename}")
                        continue

                print(f"\t  {idx1:4}  fetching  {url}")

                html = fetchUrl(client, url)
                if html is None:
                    print(f"{idx1:4}  failed to fetch  {url}")
                    continue
                
                data = extractFields(html, url)

                # original row for traceability
                data["name"] = name
                data["name_orig"]   = row.get("name")
                data["url_orig"]    = row.get("url")
                
                # link number is changes for repeated fetches
                data.pop("link_number", None)

                contentDate = data.get("date_parsed", "")

                # Reconcile URL date and content date
                if urlDate:
                    data["date_parsed"] = urlDate
                    if contentDate and contentDate != urlDate:
                        data["date_parsed_content"] = contentDate
                else:
                    data["date_parsed"] = contentDate

                # If URL didn't have a date, we determine filename now
                if not expectedFilename:
                    dte = (data.get("date_parsed") or data.get("date") or row.get("link_number") or "").strip()
                    expectedFilename = f"{slug}-{dte}.json"
                    outPth = outDir / expectedFilename
                    
                    if outPth.exists() and not dlAll:
                        print(f"\t  {idx1:4}  skip (exists after fetch)  {expectedFilename}")
                        continue

                try:
                    with outPth.open("w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                        print(f"\t  {idx1:4}  wrote     {outPth}")
                except Exception as exc:
                    stackTrace(exc)
                    print("exc-json-dump")

                delay = random.uniform(0.3, 1.2)
                time.sleep(delay)

            except Exception as exc:
                stackTrace(exc)
                print("exc-main-loop")


if __name__ == "__main__":
    scriptDir = Path(__file__).resolve().parent
    os.chdir(scriptDir)
    print(f"\t{Path(__file__)} start")
    main()
    print(f"\t{Path(__file__)} end")