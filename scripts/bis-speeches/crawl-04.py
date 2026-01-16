#!/usr/bin/env python3
"""
Usage:
cls &&    python ./scripts/bis-speeches/crawl-04.py
"""

from pathlib import Path
# pip install pypdf
from pypdf import PdfReader
from pathlib import Path
import os
import json
import httpx




def extractText(pthPdf: Path) -> str:
    '''
    pdf_file = Path("document.pdf")
    plain_text = extractText(pdf_file)
    '''

    reader = PdfReader(str(pthPdf))
    all_text = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text is None:
            print(f"Warning: page {idx} returned None text")
            text = ""
        all_text.append(text)
    return "\n\n".join(all_text)


def main():

    outDir = Path("./out")
    dlDir = outDir / "dl"
    dlDir.mkdir(parents=True, exist_ok=True)

    jsonFilesList = sorted(outDir.glob("*.json"))

    for idx1, jsonPath in enumerate(jsonFilesList):
        try:
            with jsonPath.open("r", encoding="utf-8") as f:
                jsonData = json.load(f)
        except Exception as exc:
            print(f"[{idx1}] JSON load failed for {jsonPath}: {exc}")
            continue

        if "pdf_url" not in jsonData:
            print(f"[{idx1}] Key 'pdf_url' not found in {jsonPath.name}")
            continue

        pdfUrl = jsonData["pdf_url"]
        baseName = jsonPath.stem
        localPdfPath = dlDir / f"{baseName}.pdf"

        if localPdfPath.exists():
            print(f"\t  [{idx1:4}] pdf already exists {localPdfPath}")
        else:
            try:
                with httpx.Client(follow_redirects=True, timeout=30.0) as client:
                    with client.stream("GET", pdfUrl) as resp:
                        try:
                            resp.raise_for_status()
                        except Exception as exc:
                            print(f"[{idx1}] HTTP error for {pdfUrl}: {exc}")
                            continue

                        with localPdfPath.open("wb") as outFile:
                            chunkSize = 1024 * 64
                            for idx2, chunk in enumerate(resp.iter_bytes(chunk_size=chunkSize)):
                                if chunk:
                                    outFile.write(chunk)
            except Exception as exc:
                print(f"[{idx1}] Download failed for {pdfUrl} -> {localPdfPath}: {exc}")
                continue

        try:
            textContent = extractText(localPdfPath)
        except Exception as exc:
            print(f"\t  [{idx1}] Text extraction failed for {localPdfPath}: {exc}")
            continue

        txtOutPath = outDir / f"{baseName}_pdfcontent.txt"
        try:
            with txtOutPath.open("w", encoding="utf-8", newline="") as f:
                f.write(textContent if textContent is not None else "")
                print(f"\t  [{idx1:4}] text extract success {pdfUrl} -> {localPdfPath}")
        except Exception as exc:
            print(f"[{idx1}] Write failed for {txtOutPath}: {exc}")



if __name__ == "__main__":
    scriptDir = Path(__file__).resolve().parent
    os.chdir(scriptDir)
    print(f"\t{Path(__file__)} start")
    main()
    print(f"\t{Path(__file__)} end")



