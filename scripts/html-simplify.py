# pip install html5lib
from pathlib import Path
from bs4 import BeautifulSoup, Tag, NavigableString, Comment
from typing import List
import re
import html








def simplifyHtml( inpPth: Path) :


    outPth = inpPth.parent / (inpPth.stem + "_flat" + inpPth.suffix)

    # Read raw bytes, let BeautifulSoup guess encoding
    htmlBytes = inpPth.read_bytes()
    #  "html.parser" vs "html5lib"
    soup = BeautifulSoup(htmlBytes, "html5lib",    from_encoding=None)


    # 1) Drop all attributes except href
    for tag in soup.find_all(True):
        oldAttrs = dict(tag.attrs)
        newAttrs = {}

        if "href" in oldAttrs:
            newAttrs["href"] = oldAttrs["href"]

        tag.attrs = newAttrs


    # 2) Remove <head>, <footer>
    if soup.head:
        soup.head.decompose()
    if soup.footer:
        soup.footer.decompose()


    # 2b) Remove <script> and <noscript> tags inside <body>
    if soup.body:
        for tag in soup.body.find_all(["script", "noscript", "style"]):
            tag.decompose()


    # 2b-extra) Remove HTML comments
    # for textNode in soup.find_all(string=True):
    #     if isinstance(textNode, Comment):
    #         textNode.extract()


    # 2c) Unwrap common inline tags (keep their text)
    if soup.body:
        inlineTags = [
            "strong", "em", "b", "i", "u", "span", "small",
            "sup", "sub", "mark", "s", "del", "ins", "code", "kbd",
            "samp", "var", "abbr", "cite", "q", "time", "label"
        ]

        # inlineTags.append("a")
        for tag in list(soup.body.find_all(inlineTags)):
            tag.unwrap()



    # 3) Flatten: unwrap tags whose DIRECT children
    #    contain no non-whitespace text
    def hasDirectText(tag):
        for child in tag.contents:
            if isinstance(child, NavigableString):
                if str(child).strip() != "":
                    return True
        return False


    # dont flatten table tags
    def isExempt(tag):
        if tag.name == "table":
            return True
        if tag.name in ("thead", "tbody", "tfoot"):
            return True
        if tag.name == "tr" and tag.parent and tag.parent.name in ("table", "thead", "tbody", "tfoot"):
            return True
        if tag.name in ("td", "th") and tag.parent and tag.parent.name == "tr":
            return True

        # this leads to deeply nested <ul><li>  <ul><li> ...
        if True:
            if tag.name in ("ul", "ol"):
                return True

        return False



    changed = True
    while changed:
        changed = False
        # Iterate over a list copy since we may modify the tree
        for tag in list(soup.find_all(True)):
            if tag.name in ("html", "body"):
                continue
            if isExempt(tag):
                continue
            if not hasDirectText(tag):
                parent = tag.parent
                if parent is not None:
                    tag.unwrap()
                    changed = True





    if soup.html:
        soup.html.unwrap()
    if soup.body:
        soup.body.unwrap()


    # 3b) Normalize whitespace inside tags
    if False:
        pass
    for textNode in soup.find_all(string=True):
        if isinstance(textNode, NavigableString):
            # this does NOT remove double whitespace
            newText = " ".join(textNode.split())
            newText = re.sub(r"\s+", " ", newText, flags=re.UNICODE)
            textNode.replace_with(newText)





    # 4) Pretty-print
    prettyHtml = soup.prettify(formatter="html")
    outPth.write_text(prettyHtml, encoding="utf-8")
    # if writeFiles:

    # --- decode HTML entities ---
    prettyHtml = html.unescape(prettyHtml)

    # --- fix common double-encodings ---
    replacements = {
        "Ã¼": "ü",
        "Ã¤": "ä",
        "Ã¶": "ö",
        "ÃŸ": "ß",
        "Ã–": "Ö",
        "Ã„": "Ä",
        "Ãœ": "Ü",
        "â€“" : "—",
        "â€ž" : "'",
        "â€œ" : "'",
        "â€˜" : "'",
        "â€™" : "'",
    }



    for bad, good in replacements.items():
        prettyHtml = prettyHtml.replace(bad, good)





    outPth.write_text(prettyHtml, encoding="utf-8")

    print(f"\t\t  text size is {float(len(prettyHtml))/1024/1024:5.2f} MB")









inpPath = Path("./menu-tree.html")

simplifyHtml(inpPath)