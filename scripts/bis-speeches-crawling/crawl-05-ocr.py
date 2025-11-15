# pip install ocrmypdf
#       not tesseract from Uni Mannheim, its too old
# choco install tesseract
# choco install ghostscript

from pathlib import Path
import subprocess
from pypdf import PdfReader


def runOcrOnPdf(inPth: Path, outPth: Path) -> None:
    print(f"\t starting OCR {inPth}")
    cmd = [
        "ocrmypdf",
        "--force-ocr",
        "--language",
        "eng",
        str(inPth),
        str(outPth),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("ocrmypdf failed:")
        print(res.stdout)
        print(res.stderr)
        raise RuntimeError(f"ocrmypdf failed with code {res.returncode}")


def extractTextFromOcrPdf(pdfPath: Path) -> str:
    reader = PdfReader(str(pdfPath))
    allTextList = []
    for idx1, page in enumerate(reader.pages):
        pageText = page.extract_text()
        if pageText is None:
            print(f"Warning: page {idx1} returned None text")
            pageText = ""
        allTextList.append(pageText)
    print(f"\t extracted {len(allTextList)} pages from {pdfPath}")
    return "\n\n".join(allTextList)


if __name__ == "__main__":

    inp = Path(".") / "out" / "dl" / "fabio-panetta-2024-07-09.pdf"
    ocredPdf    = inp.with_name(  inp.stem + "_ocr.pdf")
    if not ocredPdf.exists():
        runOcrOnPdf(inp, ocredPdf)

    extractedText = extractTextFromOcrPdf(ocredPdf)
    # print(extractedText)
    out = Path(".") / "out" /  (inp.stem + "_ocr.txt")
    out.write_text(extractedText)
    print(f"\t written to {out}")
 