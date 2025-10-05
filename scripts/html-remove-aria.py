# pip install html5lib
from pathlib import Path
from bs4 import BeautifulSoup, Tag, NavigableString, Comment
from typing import List, Optional
import re




def removeAria( 
        inpPth: Path,
        preserveAria:      bool = False,
        preserveIdAndRole: bool = True,
):


    outPth = inpPth.parent / (inpPth.stem + "_noaria" + inpPth.suffix)


    htmlBytes = inpPth.read_bytes()
    #  "html.parser" vs "html5lib"
    soup = BeautifulSoup(htmlBytes, "html5lib",    from_encoding=None)


    ariaAttrs = [
        "aria-haspopup",
        "aria-labelledby",
        "aria-controls",
        "aria-expanded",
        "aria-hidden",
        "aria-current",
        "aria-pressed",
        "aria-selected",
        "aria-describedby",
        "aria-live",
    ]


    # 1) Drop attributes with optional preservation for ARIA + id/role
    allTags = soup.find_all(True)
    for tag in allTags:
        
        oldAttrs = dict(tag.attrs)
        newAttrs = {}

        # 1) Keep every attribute except aria-*
        for key in oldAttrs.keys():
            keepAttr = True
            if key.startswith("aria-"):
                keepAttr = False

            if keepAttr:
                newAttrs[key] = oldAttrs[key]

        tag.attrs = newAttrs



    # 3b) Normalize whitespace inside tags
    if False:
        for textNode in soup.find_all(string=True):
            if isinstance(textNode, NavigableString):
                newText = " ".join(textNode.split())
                newText = re.sub(r"\s+", " ", newText, flags=re.UNICODE)
                textNode.replace_with(newText)



    # 4) Pretty-print
    # prettyHtml = soup.prettify(formatter="html")
    # outPth.write_text(prettyHtml, encoding="utf-8")
    # print(f"\t\t new  size is {float(len(prettyHtml))/1024/1024:5.2f} MB")



    outPth.write_bytes(soup.encode("utf-8", formatter="html"))















inpPath = Path("./index.html")

removeAria(inpPath)

