from   datetime   import datetime, timedelta
import locale
import markdown
from   pathlib    import Path



def dateFormat( isoDate = "2026-01-26", lg="de" ):

    typedDte = datetime.strptime(isoDate, "%Y-%m-%d")

    if lg=="en":
        try:
            locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
            return typedDte.strftime("%d. %B %Y")
        except Exception as exc:
            return exc

    elif lg=="de" or True:
        try:
            locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
            return typedDte.strftime("%d. %B %Y")
        except Exception as exc:
            return exc


def renderMarkdown(pth):
  
  try:
    pathObj = Path(pth)
    with open(pathObj, "r", encoding="utf-8") as openFile:
      fileContent = openFile.read()      
    htmlContent = markdown.markdown(fileContent)    
    return htmlContent

  except Exception as exc:
    return f"Error reading or rendering file {pth}: {exc}"

