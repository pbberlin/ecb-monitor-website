import os
import json
import random
import time
from   datetime   import datetime, timedelta
from   pathlib    import Path



import pandas as pd
import matplotlib
from   ipaddress import ip_address, ip_network


from   flask import Flask, request, Response, abort, current_app 
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
    "ezb-monitor.zew.de":              "de",
    "ecb-monitor.zew.de":              "en",
    "ezb-transparenz-monitor.zew.de":  "de",
    "ecb-transparency-monitor.zew.de": "en",
}

alternateHost = {
    "ezb-monitor.zew.de":               "ecb-monitor.zew.de",
    "ecb-monitor.zew.de":               "ezb-monitor.zew.de",
    "ezb-transparenz-monitor.zew.de":   "ecb-transparency-monitor.zew.de",
    "ecb-transparency-monitor.zew.de":  "ezb-transparenz-monitor.zew.de",
    "localhost":                        "localhost",
}

alternateLang = {
    "de": "en",
    "en": "de",
}



staticVersion = str(int(time.time()))
app.config["STATIC_VERSION"] = staticVersion


@app.before_request
def selectLanguage():
    hostHeader = request.headers.get("Host", "")
    hostParts  = hostHeader.split(":")
    hostName   = hostParts[0].lower()
    port       = ""
    if len(hostParts) > 1:
        port = ":" + hostParts[1]
    if request.is_secure:
        protocol = "https"
    else:
        protocol = "http"

    curLg      = LANGUAGE_BY_HOST.get(hostName, "de") 
    if hostName == "localhost":
        lg = request.args.get('lang')
        if (lg is None) or (lg == "") :
            curLg = "de"
        else:
            curLg = lg

    g.currentLanguage = curLg

    fPth = request.full_path
    fPth = fPth.replace(f"lang={curLg}", "")
    fPth += f"lang={alternateLang[curLg]}"
    g.switchLgUrl    = protocol + "://" + alternateHost[hostName] + port + fPth
    g.switchLgCode   = alternateLang[curLg]

    # print(f"cur lang by hostname is {curLg}")
    
    if False:
        # now available everyhwere
        currentLanguage = getattr(g, "currentLanguage", "de")


if False:
    from lib.trls    import getCurrentLanguageAndI18n

# dev mode => re-loading the translations python module with every request
import lib.trls as trlsModule
import importlib
def getI18nDyn():
    global trlsModule
    # taking it from current_app - not from app  - as above
    debugModeLive = current_app.debug or os.environ.get("FLASK_DEBUG") == "1"
    if debugModeLive:
        try:
            trlsModule = importlib.reload(trlsModule)
            print(f"\treloading lib.trls")
        except Exception as exc:
            print(f"Error reloading lib.trls: {exc}")
    return trlsModule.getCurrentLanguageAndI18n()



@app.context_processor
def injectLanguage():

    curI18n, curLg, switchLgCode, switchLgUrl  = getI18nDyn()

    # for idx, key in enumerate(curI18n):
    #     print(f"  {key:16} {curI18n[key][:44]}")
    #     if idx > 5:
    #         break


    # curLg      -> "en" / "de"
    # make available in all Jinja templates
    # used in index.html window.APP_LANGUAGE = "{{curLg}}";
    # i18n                 -> dict of key   -> translated string in current language
    # i18n                 -> staticVersion -> url param for static files
    return {
        "staticVersion": app.config["STATIC_VERSION"],
        "curLg"        : curLg,
        "switchLgCode" : switchLgCode,
        "switchLgUrl"  : switchLgUrl,

        "i18n": curI18n,
    }






wd = os.getcwd()
dirDl = Path(".") / "data" / "dl"





# allowed IPs or CIDR ranges
allowedIps = [
    "127.0.0.1",          # localhost
    "192.168.1.0/24",     # local network
    "193.196.11.188",     # ZEW internal
    "193.196.11.0/24",    # ZEW internal network (covers 193.196.11.1–193.196.11.255)
    "78.94.80.126",       # zew guest
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


@app.after_request
def addSecurityHeaders(resp):
    # resp.headers["Content-Security-Policy"] = (
    #     "default-src 'self'; "
    #     "script-src 'self' "
    #     "'sha256-MGIBbpKUJsi7zkhCI3XuEea7C34s7XragI7YFbdeBzM=';"
    # )
    return resp


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

    renderedCnt = render_template_string(
        cnt,
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

    renderedCnt = render_template_string(
        cnt,
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




@app.route('/some-file')
@app.route('/some-file.html')
def flow01():
    pth = Path("./content") / "flow-1.html"
    cnt = pth.read_text( encoding="utf-8"  )
    return render_template(
        "index.html",
        content = cnt,
    )




from lib.page1   import getAllPredictions
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

        return app.response_class(
            response=json.dumps(res), 
            status=200, 
            mimetype='application/json',
        )

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
