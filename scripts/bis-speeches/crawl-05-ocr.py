# pip install ocrmypdf
#       not tesseract from Uni Mannheim, its too old
# choco install tesseract
# choco install ghostscript

from pathlib import Path
import subprocess
from pypdf import PdfReader
import json


def runOcrOnPdf(inPth: Path, outPth: Path, jpegTranscoding=True) -> None:
    print(f"\t   starting OCR {inPth}")

    cmd = [
        "ocrmypdf",
        "--force-ocr",
        "--language",
        "eng",
        str(inPth),
        str(outPth),
    ]

    if not jpegTranscoding:
        cmd = [
            "ocrmypdf",
            "--optimize", "0",          # <- key change: disable JPEG transcoding        
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




def checkSlashRatio(filePath):
    maxBytes = 10 * 1024
    totalChars = 0
    slashCount = 0

    try:
        with filePath.open("r", encoding="utf-8", errors="replace") as f:
            textChunk = f.read(maxBytes)
            for idx1, ch in enumerate(textChunk):
                totalChars += 1
                if ch == "/":
                    slashCount += 1

        if totalChars == 0:
            print(f"no content for  {filePath}")
            return False

        ratio = slashCount / totalChars
        return ratio

    except Exception as exc:
        print(f"checkSlashRatio {exc}")
        return False





def oneFile(inp,out):

    ocrPdf    = inp.with_name(  inp.stem + "_ocr.pdf")
    if not ocrPdf.exists():
        try:
            runOcrOnPdf(inp, ocrPdf)
        except Exception as exc:
            try:
                print(f"\t      retry without jpeg transc")
                runOcrOnPdf(inp, ocrPdf, jpegTranscoding=False)
            except Exception as exc:            
                print(f"\t      {exc}")
                print(f"\t      skipping")

    extractedText = extractTextFromOcrPdf(ocrPdf)
    # print(extractedText)
    out.write_text(extractedText, encoding="utf-8")
    print(f"\t   written to {out}")
 


outDir = Path("./out")
dlDir = outDir / "dl"
dlDir.mkdir(parents=True, exist_ok=True)

jsonFilesList = sorted(outDir.glob("*.json"))



counterWithSlashes = 0
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

    if "pdf_url" not in jsonData:
        print(f"[{idx1}] Key 'pdf_url' not found in {jsonPath.name}")
        continue


    inpPdf = Path(".") / "out" / "dl" /  (jsonPath.stem +  ".pdf")
    inpTxt = Path(".") / "out" / (jsonPath.stem +  "_pdfcontent.txt")
    
    if inpPdf.exists():
        if not inpTxt.exists():
            print(f"{idx1:3} -     exists -  {inpPdf}")
            print(f"{idx1:3} - not exists -  {inpTxt}")
    else:
        print(f"{idx1:3} - not exists -  {inpPdf}")
        continue


    outOcr = Path(".") / "out" /  (inpPdf.stem + "_ocr.txt")
    if outOcr.exists():
        print(f"{idx1:3} -     exists -  {outOcr}")
        continue

    result = checkSlashRatio(inpTxt)
    if type(result) is bool and result == False:
        print("checkSlashRatio() failed")
        continue
    
    if result > 0.01:
        counterWithSlashes += 1
        print(f" \t{(result*100):5.1f}% slashes for {counterWithSlashes} {inpTxt.name}")

        oneFile(inpPdf, outOcr)
        # break