import os
import json
import random
from   datetime   import datetime, timedelta
from   pathlib    import Path

import pandas as pd
import matplotlib
from   ipaddress import ip_address, ip_network



from   flask import Flask, request, Response, abort 
from   flask import render_template, render_template_string, send_from_directory 
from   flask import g
app  = Flask(__name__)
# Flask automatically sets this when FLASK_ENV=development
# or when you run app.run(debug=True)
debugMode = app.debug or os.environ.get("FLASK_DEBUG") == "1"
if debugMode:
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}


LANGUAGE_BY_HOST = {
    "ecb-monitor.zew.de": "en",
    "ezb-monitor.zew.de": "de",
}


@app.before_request
def selectLanguage():
    hostHeader = request.headers.get("Host", "")
    hostName   = hostHeader.split(":")[0].lower()
    currLang   = LANGUAGE_BY_HOST.get(hostName, "de") 
    g.currentLanguage = currLang
    print(f"cur lang by hostname is {currLang}")
    
    if False:
        # now available everyhwere
        currentLanguage = getattr(g, "currentLanguage", "de")


from lib.trls    import AttrDict, trlsByLg, getCurrentLanguageAndI18n


@app.context_processor
def injectLanguage():

    curLg = getattr(g, "currentLanguage", "en")

    curI18n = {}
    if curLg in trlsByLg:
        curI18n = trlsByLg[curLg]

    curLg, curI18n = getCurrentLanguageAndI18n()

    # currentLanguage      -> "en" / "de"
    # make available in all Jinja templates
    # used in index.html window.APP_LANGUAGE = "{{ currentLanguage }}";
    # i18n                 -> dict of key -> translated string in current language
    return {
        "currentLanguage": curLg,
        "i18n": AttrDict(curI18n),
    }


from lib.page1   import getAllPredictions
from lib.util    import truncateUtf8
from lib.gingado import load_CB_speeches




wd = os.getcwd()
dirDl = Path(".") / "data" / "dl"





# allowed IPs or CIDR ranges
allowedIps = [
    "127.0.0.1",          # localhost
    "192.168.1.0/24",     # local network
    "193.196.11.188",     # ZEW internal
    "193.196.11.0/24",    # ZEW internal network (covers 193.196.11.1–193.196.11.255)
]

allowedNetworks = []
for ip in allowedIps:
    network = ip_network(ip, strict=False)
    allowedNetworks.append(network)


@app.before_request
def limitRemoteAddr():
    clientIp = request.remote_addr

    try:
        clientAddress = ip_address(clientIp)
        isAllowed = False

        for network in allowedNetworks:
            if clientAddress in network:
                isAllowed = True
                break

        if not isAllowed:
            print(f"Denied access for IP: {clientIp}")
            abort(403, description="Access denied")

    except Exception as exc:
        print(f"Error checking IP {clientIp}: {exc}")
        abort(403, description="Invalid IP address")



@app.route("/favicon.ico")
def favicon():
    staticPath = Path(app.static_folder)
    iconPath = staticPath / "favicon.ico"

    if iconPath.exists():
        return send_from_directory(
            staticPath.as_posix(),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon"
        )

    return Response(status=204)


@app.route('/')
def index():

    pth = Path("./content") / "main.html"

    cnt = pth.read_text( encoding="utf-8"  )

    # render content file with Jinja
    curLg, curI18n = getCurrentLanguageAndI18n()
    renderedCnt = render_template_string(
        cnt,
        currentLanguage=curLg,        
        i18n=AttrDict(curI18n),
    )

    return render_template(
            "index.html",
            content = renderedCnt,
    )



@app.route('/pg/<htmlFile>')
def page(htmlFile):
    """ generic page  """
    pth = Path("./content") / htmlFile
    if pth.suffix == "":
        pth = pth.with_suffix(".html")
    if not pth.exists():
        return f"Page '{htmlFile}' not found.", 404

    cnt = pth.read_text(encoding="utf-8")

    curLg, curI18n = getCurrentLanguageAndI18n()
    renderedCnt = render_template_string(
        cnt,
        currentLanguage=curLg,        
        i18n=AttrDict(curI18n),
    )

    return render_template(
        "index.html",
        content=renderedCnt,
    )


@app.route('/jans-remote-stuff')
def nameIsEgal():
    computed = f"2 * 55 is {2*55}"
    plt      = matplotlib.pyplot("todo: Eingabe vom HTML before")
    pthPlt =f"./tmp/plot-as-image-{computed}.png"
    plt.saveAs(pthPlt)
    return render_template(
        "index.html",
        title="EZB Transparenzmonitor",
        content = f"<img src='{pthPlt}' />",
    )



@app.route('/download-speeches')
def fetch():

    yr = 2025

    fPth = dirDl / f"speeches-{yr}.pkl"

    # print(f"file name {fPth}")

    reload   = False
    speeches = None

    if fPth.exists():
        fileDate = datetime.fromtimestamp(fPth.stat().st_mtime)
        if fileDate < datetime.now() - timedelta(hours=24):
            reload = True
    else:
        reload = True

    if reload:
        # https://bis-med-it.github.io/gingado/datasets.html
        speeches = load_CB_speeches(yr, cache=False)
        speeches.to_pickle(fPth)
    else:
        speeches = pd.read_pickle(fPth)



    hd      = speeches.head(n=4)

    for i in range(len(hd)):
        text = hd.at[i, "text"]
        text = truncateUtf8(text, 128)
        text = text.replace('\n', "<br>")
        hd.at[i, "text"]        = text

        desc = hd.at[i, "description"]
        hd.at[i, "description"] = truncateUtf8(desc, 128)


    # hd      = speeches.tail(n=4)


    cnt  = ""
    cnt += f"Reloaded {reload} <br>"
    cnt += hd.to_html()
    # cnt += f"<pre>  {hd} </pre>"
    cnt += f"<pre>  {fPth} </pre>"

    return render_template(
            "index.html",
            title   =  "EZB Transparenzmonitor",
            content = cnt,
        )



@app.route('/some-file')
@app.route('/some-file.html')
def flow01():
    pth = Path("./content") / "flow-1.html"
    cnt = pth.read_text( encoding="utf-8"  )
    return render_template(
            "index.html",
            title   = "EZB Transparenzmonitor",
            content = cnt,
        )




@app.route('/all-predictions', methods=['post','get'])
def allPredictionsH():
    try:

        #  arg.get does *not* contain POST values
        input_text = request.args.get('input_text')

        print(f"allPredictionsH 1 {input_text}")

        try:
            top_k = request.json['top_k']
        except Exception as error:
            print(str(error))

        res = getAllPredictions(input_text, random.randint(5,555))

        print(f"allPredictionsH 2 {input_text}")

        return app.response_class(response=json.dumps(res), status=200, mimetype='application/json')

    except Exception as error:
        err = str(error)
        print(err)
        return app.response_class(response=json.dumps(err), status=500, mimetype='application/json')




if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=True,
        port=5000,
        use_reloader=False,
    )
