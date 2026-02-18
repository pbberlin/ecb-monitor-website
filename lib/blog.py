from   datetime   import datetime, timedelta
import locale
import markdown
from   pathlib    import Path
from   flask import g, render_template_string



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



def renderMarkdown(markDownCnt):

  # --- render Jinja
  markDownCnt = render_template_string(
     markDownCnt
  )

  try:
    htmlContent = markdown.markdown(
      markDownCnt,
      extensions=["tables"],
    )
    return htmlContent

  except Exception as exc:
    return f"error markdown rendering: {exc}"



# parsing a markdown file - see doc string inside
def mdParts(blogType: str, lg: str, fn: str , paramAutofocus=False):

  """
    first three lines and markdown filename have special role.
    for list view
  """

  pth         = Path("content/blog") / blogType / lg / fn

  with open(pth, "r", encoding="utf-8") as f:

    # first line as head line - link-text
    h1 = f.readline().strip()
    h1 = h1.lstrip("<!--").rstrip("-->").strip()
    h1 = h1.lstrip("#").strip()


    h2 = ""
    if len(h1) > 0:
      h2 = f.readline().strip()

    designTpl = ""
    if len(h2) > 0:
      designTpl = f.readline().strip()

    restOfFile = f.read()

    autofoc = ""
    if paramAutofocus:
        # autofoc = "autofocus"
        autofoc = ""

    dateLine = dateFormat(pth.stem, lg)

    listEntry  = ""
    listEntry += " <li>"
    listEntry +=    f"<p class='date-line'>{dateLine}  </p> "
    itemPth = Path("blog") / blogType / lg / fn
    listEntry +=    f" <a class='blog-list-entry' href='/{itemPth.as_posix() }?lang={lg}' {autofoc} > {h1} </a>"
    if h2:
      # listEntry +=    f"<br> "
      listEntry +=    f"{h2} "
    listEntry += "</li>"


    return h1, h2, designTpl, restOfFile, dateLine, listEntry














def thumb(fn):
    baseDir = Path("/static/img")
    pth = baseDir / Path(fn)
    if fn.lower().endswith(".mp4"):
        return f'<video src="{pth}" width="200" controls></video>'
    # print(f"{fn:24} ->  {pth}")
    return f'<img src="{pth}" width="200">'

def licenceString(fnParam):
    fn = fnParam.lower()
    if "adobe" in fn:
        return "Licensed by our organisation from [Adobe Stock](https://stock.adobe.com)."
    if ("zew" in fn) or ("fhe" in fn):
        return "Produced by our organisation [ZEW](https://www.zew.de)."
    return "Source: [Wikimedia Commons](https://commons.wikimedia.org/wiki/Main_Page)."


def imageLicenses():

  imgs = [
      "symbols/imag0021_backspace.jpg",

      "homepage/logo_european_central_bank.png",
      "homepage/supply_and_demand_diagram-orig.png",
      "homepage/television_news_crew.jpg",
  
      "blog/electronica-biftu-cash-register--iceblue-yell.png",
      "blog/European_Central_Bank_Headquarters_(model_01)-sm-fg2.png",
      "blog/fhe--grey.jpg",
      "blog/fhe--iceblue.jpg",
      "blog/adobe-political-economy.jpg",
      "blog/adobe-stock-1878624005-sm.gif",
      "blog/adobe-stock-529399345-ecb.jpg",
    ]



  lines = []

  lines.append("### Image Credits (Licence Information)")
  lines.append("")
  lines.append("<br>This site uses [Apache Echarts](https://github.com/apache/echarts) <br>")
  lines.append("")
  lines.append("Credits for the images used on this website.")

  lines.append("")
  lines.append("| Thumbnail | Legal notice |")
  lines.append("|---------|--------------|")

  for idx1, fn in enumerate(imgs):
    try:
      thumbnailHtml = thumb(fn)
      legalText = licenceString( Path(fn).name )
      row = f"| {thumbnailHtml} | **{Path(fn).name}** <br> {legalText} |"
      lines.append(row)

    except Exception as exc:
      print("Error while processing:", fn)
      print(exc)
      raise

  markDownCnt = "\n".join(lines)



  htmlContent = markdown.markdown(
    markDownCnt,
    extensions=["tables"],
  )

  return htmlContent



