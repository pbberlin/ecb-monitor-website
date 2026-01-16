#!/usr/bin/env python3
"""
Read a CSV with at least columns: name,url
Fetch each URL with httpx.
Extract specified elements using BeautifulSoup.
Write one JSON per input row to the "out" directory using tlsl(name).json as filename.

Usage:
cls &&    python ./scripts/bis-speeches/crawl-03.py --input ./ecb-members-links.csv
"""

import argparse
import csv
import json
import os
import sys
import time
import random
from   pathlib import Path
from   typing  import Dict, Any, Optional
from   datetime import datetime
import httpx
from   bs4     import BeautifulSoup

# add parent directory of scripts/ (i.e., appdir/) to import path
sys.path.append(str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parents[2]))
from lib.slugify_wrapper import tlsl


# --- CSV I/O --------------------------------------------------------------------

def readInputCsv(inputPath: Path) -> list[dict]:
    rows = []
    lastError: Optional[Exception] = None

    # try to sniff delimiter
    for enc in ["utf-8", "utf-8-sig"]:
        try:
            with inputPath.open("r", encoding=enc, newline="") as f:
                sample = f.read(4096)
                f.seek(0)
                try:
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(sample, delimiters=";,")
                except Exception as exc:
                    print(exc)
                    dialect = csv.excel
                    dialect.delimiter = ";"

                reader = csv.DictReader(f, dialect=dialect)
                for row in reader:
                    rows.append(row)
            break
        except Exception as exc:
            lastError = exc

    if len(rows) == 0:
        print(f"Failed to read CSV. Last error: {lastError}")
        sys.exit(1)
    else: 
        print(f"{len(rows)} rows in csv {inputPath} loaded")


    for idx, row in enumerate(rows):
        print( f"\t  {row['name']} - {row['url']}")
        if idx > 3:
            break


    return rows


def ensureOutDir(outDir: Path) -> None:
    try:
        outDir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        print(exc)
        sys.exit(1)



# --- HTTP fetch -----------------------------------------------------------------

def fetchUrl(client: httpx.Client, url: str, maxRetries: int = 3, backoffSeconds: float = 1.5) -> Optional[str]:
    attempt = 0
    while True:
        try:
            attempt = attempt + 1
            resp = client.get(url, timeout=30.0, follow_redirects=True)
            if resp.status_code >= 200 and resp.status_code < 300:
                return resp.text
            else:
                print(f"HTTP {resp.status_code} for {url}")
        except Exception as exc:
            print(exc)

        if attempt >= maxRetries:
            return None

        try:
            time.sleep(backoffSeconds * attempt)
        except Exception as exc:
            print(exc)


# --- Extraction helpers ---------------------------------------------------------

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
        print(exc)
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
        print(exc)
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
        print(exc)
        return result

    # headline: //*[@id="center"]/h1
    headlineNode = None
    try:
        for node in soup.select("#center > h1"):
            headlineNode = node
            break
    except Exception as exc:
        print(exc)

    headlineText = getText(headlineNode)
    result["headline"] = headlineText

    # description: <div id="extratitle-div">...</div>
    descriptionNode = None
    try:
        for node in soup.select("#extratitle-div"):
            descriptionNode = node
            break
    except Exception as exc:
        print(exc)

    descriptionHtml = getInnerHtml(descriptionNode)
    descriptionText = getText(descriptionNode)
    result["description_html"] = descriptionHtml
    result["description_text"] = descriptionText

    # date: //*[@id="center"]/div[2]/div[2]/div[1]/div  class="date"
    dateNode = None
    try:
        for node in soup.select("#center .date"):
            dateNode = node
            break
    except Exception as exc:
        print(exc)

    dateText = getText(dateNode)
    result["date"] = dateText

    # 05 June 2025  - give me some standard formatted parsed date to result["date_parsed"] with yyyy-mm-dd
    try:
        parsedDate = datetime.strptime(dateText, "%d %B %Y")
        result["date_parsed"] = parsedDate.strftime("%Y-%m-%d")
    except Exception as exc:
        print(f"Date parse error: {exc}")
        result["date_parsed"] = ""


    # pdf_url: //*[@id="center"]/div[2]/div[2]/div[3]/a  class="pdftitle_link"
    pdfAnchor = None
    try:
        for node in soup.select("#center a.pdftitle_link[href]"):
            pdfAnchor = node
            break
    except Exception as exc:
        print(exc)

    pdfUrl = None
    try:
        if pdfAnchor is not None:
            href = pdfAnchor.get("href")
            if isinstance(href, str):
                if href.startswith("http://") or href.startswith("https://"):
                    pdfUrl = href
                else:
                    # resolve relative link
                    try:
                        from urllib.parse import urljoin
                        pdfUrl = urljoin(url, href)
                    except Exception as exc:
                        print(exc)
                        pdfUrl = href
    except Exception as exc:
        print(exc)

    result["pdf_url"] = pdfUrl

    # content: //*[@id="cmsContent"]
    contentNode = None
    try:
        for node in soup.select("#cmsContent"):
            contentNode = node
            break
    except Exception as exc:
        print(exc)

    contentHtml = getInnerHtml(contentNode)
    contentText = getText(contentNode)
    result["content_html"] = contentHtml
    result["content_text"] = contentText

    return result



# --- main -----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  required=True, help="Path to CSV with at least: name,url")
    args = parser.parse_args()

    inpPth = Path(args.input).expanduser().resolve()
    outDir = Path("./out")

    ensureOutDir(outDir)

    rows = readInputCsv(inpPth)
    if len(rows) == 0:
        print("No rows in input.")
        sys.exit(1)


    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ContentExtractor/1.0; +https://example.invalid)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    with httpx.Client(http2=True, headers=headers) as client:

        for idx, row in enumerate(rows):


            try:
                name = ""
                url  = ""

                name = (row.get("name") or "").strip()
                url  = (row.get("url") or "").strip()

                if len(url) < 8:
                    print(f"\t  {idx:4}  skip (no url)  {name}")
                    continue

                print(f"\t  {idx:4}  fetching  {url}")

                html = fetchUrl(client, url)
                if html is None:
                    print(f"{idx:4}  failed to fetch  {url}")
                    continue

                
                data = extractFields(html, url)

                # original row for traceability
                data["name"] = name
                data["name_orig"]   = row["name"]
                data["url_orig"]    = row["url"]
                
                # link number is changes for repeated fetches
                data.pop("link_number", None)


                slug = tlsl(name)
                dte  = (data["date_parsed"] or data["date"] or row["link_number"] or "").strip()
                filename = f"{slug}-{dte}.json"
                outPth   = outDir / filename

                try:
                    with outPth.open("w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                        print(f"\t  {idx:4}  wrote     {outPth}")
                except Exception as exc:
                    print(exc)


                delay = random.uniform(0.3, 1.2)
                time.sleep(delay)

            except Exception as exc:
                print(exc)


if __name__ == "__main__":
    scriptDir = Path(__file__).resolve().parent
    os.chdir(scriptDir)
    print(f"\t{Path(__file__)} start")
    main()
    print(f"\t{Path(__file__)} end")
