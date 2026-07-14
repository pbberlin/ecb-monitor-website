from pathlib import Path
import sys
import datetime
import httpx
import lxml.html
import re


pthScript   = Path(__file__).resolve()
projectRoot = pthScript.parent.parent
if str(projectRoot) not in sys.path:
    sys.path.insert(0, str(projectRoot))

from lib.util import stackTrace






def fetchHtml(url):
    # fetching URL with modern httpx client
    # setting timeout to prevent hanging scheduled jobs
    resp = httpx.get(url, timeout=15.0)
    resp.raise_for_status()
    return resp.text


def parseCalendarData(htmlContent):
    # parsing HTML string into lxml DOM object
    dom = lxml.html.fromstring(htmlContent)

    # using relative XPath targeting specific class
    # avoiding absolute paths to prevent breakage on layout changes
    xpathQry = "//div[contains(@class, 'definition-list')]//dl"
    dlElements = dom.xpath(xpathQry)

    if not dlElements:
        raise ValueError(f"No definition list found under xpath query path {xpathQry}")

    dlElement = dlElements[0]

    # extracting all dt and dd elements as siblings
    dtElements = dlElement.xpath("./dt")
    ddElements = dlElement.xpath("./dd")

    if len(dtElements) != len(ddElements):
        raise ValueError("Mismatch between dates (dt) and descriptions (dd) count")

    records = []
    for idx1, dtNode in enumerate(dtElements):
        if idx1 % 100 == 0:
            print(f"\t{idx1:3} of {len(dtElements)} calendar records processed")

        rawDate = dtNode.text_content().strip()
        rawDesc = ddElements[idx1].text_content().strip()

        # converting dd/mm/yyyy to dd.mm.yyyy
        formattedDate = rawDate.replace("/", ".")

        # sorting requires actual date objects
        # parsing date to ensure correct chronological sorting
        try:
            parsedDate = datetime.datetime.strptime(formattedDate, "%d.%m.%Y")
        except Exception as exc:
            stackTrace(exc)
            print(f"Failed parsing date {formattedDate}")
            continue

        tpl = (parsedDate, formattedDate, rawDesc)
        records.append(tpl)

    # sorting ascending by date object
    records.sort(key=lambda x: x[0])

    # limiting to 10 records
    limitedRecords = []
    for idx1, rec in enumerate(records):
        if idx1 >= 10:
            break
        limitedRecords.append(rec)

    return limitedRecords


def parseRatesData(htmlContent):
    dom = lxml.html.fromstring(htmlContent)

    xpathQry = "//div[contains(@class, 'table')]//table/tbody/tr"
    rowElements = dom.xpath(xpathQry)

    if not rowElements:
        raise ValueError(f"No table rows found under xpath query path {xpathQry}")

    records = []
    currentYear = ""

    for idx1, trNode in enumerate(rowElements):
        if idx1 % 100 == 0:
            print(f"\t{idx1:3} of {len(rowElements)} rate records processed")

        tdElements = trNode.xpath("./td")
        if len(tdElements) < 6:
            continue

        yearStr = tdElements[0].text_content().strip()

        # carrying forward the year if the current row's year cell is empty
        # this handles ECB's visual grouping where subsequent rows in the same year lack the year text
        if yearStr:
            currentYear = yearStr
        else:
            yearStr = currentYear

        dayMonthStr = tdElements[1].text_content().strip()

        depositRate = tdElements[2].text_content().strip()
        fixedRate = tdElements[3].text_content().strip()
        marginalRate = tdElements[5].text_content().strip()

        # extracting only day digits and month letters using regex
        # this strips out trailing footnotes (e.g., "18 Sep.5") and punctuation
        match = re.search(r'(\d+)\s+([a-zA-Z]+)', dayMonthStr)
        if not match:
            print(f"Failed extracting day and month from {dayMonthStr}")
            continue

        dayStr = match.group(1)
        monthStr = match.group(2)[:3]

        cleanDateStr = f"{yearStr} {dayStr} {monthStr}"

        try:
            parsedDate = datetime.datetime.strptime(cleanDateStr, "%Y %d %b")
        except Exception as exc:
            stackTrace(exc)
            print(f"Failed parsing date {cleanDateStr}")
            continue

        # reconstructing original display string for the markdown table
        displayDateStr = f"{yearStr} {dayMonthStr}"
        tpl = (parsedDate, displayDateStr, depositRate, fixedRate, marginalRate)
        records.append(tpl)

    # sorting descending by date object
    records.sort(key=lambda x: x[0], reverse=True)

    limitedRecords = []
    for idx1, rec in enumerate(records):
        if idx1 >= 10:
            break
        limitedRecords.append(rec)

    return limitedRecords


def buildCalendarMarkdown(records, sourceUrl, lastUpdated):
    lines = []
    lines.append("| Date | Meeting Title |")
    lines.append("|---|---|")

    for idx1, tpl in enumerate(records):
        _, dateStr, descStr = tpl
        # removing newlines from description to prevent markdown table breakage
        cleanDesc = descStr.replace("\n", " ").replace("\r", "")
        lines.append(f"| {dateStr} | {cleanDesc} |")

    lines.append("")
    lines.append(f"[To source]({sourceUrl})")
    lines.append("")
    lines.append(f"*Last updated: {lastUpdated}*")

    return "\n".join(lines)


def buildRatesMarkdown(records, sourceUrl, lastUpdated):
    lines = []
    lines.append("| Date (with effect from) | Deposit facility | Main refinancing operations (Fixed rate) | Marginal lending facility |")
    lines.append("|---|---|---|---|")

    for idx1, tpl in enumerate(records):
        _, dateStr, depRate, fixRate, margRate = tpl
        lines.append(f"| {dateStr} | {depRate} | {fixRate} | {margRate} |")

    lines.append("")
    lines.append(f"[To source]({sourceUrl})")
    lines.append("")
    lines.append(f"*Last updated: {lastUpdated}*")

    return "\n".join(lines)


def buildFallbackMarkdown(sourceUrl, lastUpdated):
    lines = []
    lines.append("Could not retrieve data, please use the link below.")
    lines.append("")
    lines.append(f"[To source]({sourceUrl})")
    lines.append("")
    lines.append(f"*Last updated: {lastUpdated}*")

    return "\n".join(lines)


def writeOutput(content, filename):
    # writing identical english content to both language directories
    # preserving english decimal separators and column names
    basePth = Path("./content/md")

    langs = ["en", "de"]
    for idx1, lg in enumerate(langs):
        pth = basePth / lg / filename
        pth.parent.mkdir(parents=True, exist_ok=True)
        # pth.write_text(content, encoding="utf-8")
        # print(f"Wrote {pth}")
        print(f"Skipping  {pth}")


def main():
    calendarUrl = "https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html"
    ratesUrl    = "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/key_ecb_interest_rates/html/index.en.html"

    now = datetime.datetime.now()
    lastUpdated = now.strftime("%Y-%m-%d %H:%M:%S")

    # processing calendar
    try:
        print("Fetching calendar data...")
        calHtml    = fetchHtml(calendarUrl)
        calRecords = parseCalendarData(calHtml)
        calMd      = buildCalendarMarkdown(calRecords, calendarUrl, lastUpdated)
        writeOutput(calMd, "calendar-ecb.md")
    except Exception as exc:
        stackTrace(exc)
        print("Failed processing calendar data")
        fallbackMd = buildFallbackMarkdown(calendarUrl, lastUpdated)
        writeOutput(fallbackMd, "calendar-ecb.md")

    # processing rates
    try:
        print("Fetching rates data...")
        ratesHtml    = fetchHtml(ratesUrl)
        ratesRecords = parseRatesData(ratesHtml)
        ratesMd      = buildRatesMarkdown(ratesRecords, ratesUrl, lastUpdated)
        writeOutput(ratesMd, "interest-rates.md")
    except Exception as exc:
        stackTrace(exc)
        print("Failed processing rates data")
        fallbackMd = buildFallbackMarkdown(ratesUrl, lastUpdated)
        writeOutput(fallbackMd, "interest-rates.md")


if __name__ == "__main__":
    try:
        pass
        main()

    except Exception as exc:
        stackTrace(exc)
        print("Critical failure in main execution block")
        sys.exit(-1)