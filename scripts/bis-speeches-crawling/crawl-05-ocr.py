# pip install ocrmypdf
#       not tesseract from Uni Mannheim, its too old
# choco install tesseract
# choco install ghostscript

from pathlib import Path
import subprocess
from pypdf import PdfReader


def runOcrOnPdf(inputPdfPath: Path, outputPdfPath: Path) -> None:
    cmd = [
        "ocrmypdf",
        "--force-ocr",
        "--language",
        "eng",
        str(inputPdfPath),
        str(outputPdfPath),
    ]


    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ocrmypdf failed:")
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError(f"ocrmypdf failed with code {result.returncode}")


def extractTextFromPdf(pdfPath: Path) -> str:
    reader = PdfReader(str(pdfPath))
    allTextList = []
    for idx1, page in enumerate(reader.pages):
        pageText = page.extract_text()
        if pageText is None:
            print(f"Warning: page {idx1} returned None text")
            pageText = ""
        allTextList.append(pageText)
    return "\n\n".join(allTextList)


if __name__ == "__main__":
    originalPdf = Path("fabio-panetta-2024-07-09.pdf")
    ocredPdf = Path("fabio-panetta-2024-07-09_ocr.pdf")

    if not ocredPdf.exists():
        runOcrOnPdf(originalPdf, ocredPdf)

    extractedText = extractTextFromPdf(ocredPdf)
    # print(extractedText)
    out = originalPdf.with_name(  originalPdf.stem + ".txt")
    out.write_text(extractedText)
 