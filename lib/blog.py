from   datetime   import datetime, timedelta
import locale
import markdown
from   pathlib    import Path
from   flask import g






def dateFormat( isoDate = "2026-01-26", lg="de" ):

    typedDte = datetime.strptime(isoDate, "%Y-%m-%d")

    if lg=="en":
        try:
            locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
            return typedDte.strftime("%d. %B %Y")
        except Exception as exc:
            return str(exc)

    elif lg=="de" or True:
        try:
            locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
            return typedDte.strftime("%d. %B %Y")
        except Exception as exc:
            return str(exc)



def listEntry(pth: Path, idx: int):

  urlPth    = Path("blog") / g.currentLanguage / Path(pth).name

  with open(pth, "r", encoding="utf-8") as f:

    # first line as head line - link-text 
    h1 = f.readline().strip()
    h1 = h1.lstrip("<!--").rstrip("-->").strip()
    h1 = h1.lstrip("#").strip()


    h2 = ""
    if len(h1) > 0:
      h2 = f.readline().strip()

    tplName = ""
    if len(h2) > 0:
      tplName = f.readline().strip()
  

    restOfFile = f.read()

    autofoc = ""
    if idx == 0:
        # autofoc = "autofocus"
        autofoc = ""

    dateLine = dateFormat(pth.stem, g.currentLanguage)

    listEntry  = ""
    listEntry += " <li>"
    listEntry +=    f"<p class='date-line'>{dateLine}  </p> "
    listEntry +=    f"<b>  <a href='{urlPth.as_posix() }?lang=en' {autofoc} > {h1} </a> </b>"
    if h2:     
      listEntry +=    f"<br> "
      listEntry +=    f"{h2} "
    listEntry += "</li>"


    return h1, h2, tplName, restOfFile, dateLine, listEntry


def renderMarkdown(markDownCnt):
  try:
    htmlContent = markdown.markdown(markDownCnt)    
    return htmlContent

  except Exception as exc:
    return f"error markdown rendering: {exc}"

