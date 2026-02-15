import os
import json
import random
import time
from   pathlib    import Path


import pandas as pd
import matplotlib
from   ipaddress import ip_address, ip_network


from   flask import Flask, request, Response, abort, current_app
from   flask import render_template, render_template_string, make_response,  send_from_directory
from   flask import g
app  = Flask(__name__)
# Flask automatically sets this when FLASK_ENV=development
# or when you run app.run(debug=True)
debugModeInit = app.debug or os.environ.get("FLASK_DEBUG") == "1"
if debugModeInit:
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
dirDl = Path(".") / "scripts" / "council"





# allowed IPs or CIDR ranges
allowedIps = [
    "127.0.0.1",          # localhost
    "192.168.1.0/24",     # local network
    "193.196.11.188",     # ZEW internal
    "193.196.11.0/24",    # ZEW internal network (covers 193.196.11.1–193.196.11.255)
    "78.94.80.126",       # zew guest
    "34.254.109.160",     # securityheaders.com
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

    # f"script-src 'self'{scriptHashPart}; "
    #  f"style-src 'self'{styleHashPart}; "

    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
    )


    if request.is_secure:
        resp.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )

    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

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


@app.route("/static/js/app-config.js")
def appConfigJs():

    debugModeLive = current_app.debug or os.environ.get("FLASK_DEBUG") == "1"
    curLg = getattr(g, "currentLanguage", "de")

    resp = make_response(
        render_template(
            "js/app-config.js",
            debug=debugModeLive,
            curLg=curLg,
        )
    )
    resp.headers["Content-Type"] = "application/javascript; charset=utf-8"
    return resp


@app.route('/pg/<htmlFile>')
def page(htmlFile):
    """ generic page  """

    if "/" in htmlFile or "\\" in htmlFile:
        # prevent requests like /pg/../password 
        abort(404)

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








from lib.blog import renderMarkdown, mdParts, imageLicenses


@app.route('/image-licences')
def handlerImageLicencse():
    outerCnt = render_template(
        "markdown-body.html",
        content=  imageLicenses() ,
    )
    return render_template(
        "index.html",
        content=outerCnt,
    )


@app.route('/md/<md>')
def markdownAny(lg=None, md=None):
    pth = Path("content/md") / g.currentLanguage / md
    # print(f"   pth {pth}")
    innerCnt = pth.read_text(encoding="utf-8")
    rendered = renderMarkdown(innerCnt)
    outerCnt = render_template(
        "markdown-body.html",
        content    = rendered,
    )
    return render_template(
        "index.html",
        content=outerCnt,
    )







@app.route('/blog/<blogType>')
@app.route('/blog/<blogType>/<md>')
@app.route('/blog/<blogType>/<lg>/<md>')
def handlerBlog(blogType=None, lg=None, md=None):

    if blogType is None:
        blogType = "policy"

    if lg is None:
        lg = g.currentLanguage

    h1 = ""
    h2 = ""
    da = ""

    # list view of entries
    if md is None:

        showBreadCrumb = False
        blogDir   = Path("content/blog") / blogType / lg
        mds = list(blogDir.glob("*.md"))  # markdown files
        mds.sort(reverse=True)

        listItems = []
        for idx1, pth in enumerate(mds):
            if idx1 >= 10:
                break
            try:
                _, _, _, _, _, outerCnt = mdParts(blogType, lg, Path(pth).name)
                listItems.append(outerCnt)
            except Exception as exc:
                return f"error processing {pth}: {exc}"
        innerCnt =  f"""<ul>
                             {''.join(listItems)} 
                        </ul>"""

    else:

        showBreadCrumb = True

        # newest => find most recent blog
        if md == "newest":
            blogDir = Path("content/blog")  / blogType / lg
            mds = list(blogDir.glob("*.md"))
            mds.sort(reverse=True)    
            pth = mds[0]

        else:
            pth = Path("content/blog") / lg / md


        print(f"   blog path  {pth}")


        h1, h2, designTpl, restOfFile, da, outerCnt = mdParts(blogType, lg, Path(pth).name)

        innerCnt = renderMarkdown(restOfFile)


        # third line can containe a custom template for graphic design
        if designTpl:
            tmp = Path(designTpl)
            if tmp.suffix == ".html":
                designTpl = tmp.with_suffix("")

            expTpl = Path("templates/blog") / (designTpl + ".html")
            if expTpl.exists():
                print(f"\texplicit blog template found {expTpl}")
                innerCnt = render_template(
                    "blog/" + expTpl.name,
                    content = innerCnt,
                )
            else:
                print(f"\texplicit blog template not found: -{expTpl}-")



    outerCnt = render_template(
        "blog-body.html",
        breadCrumb = showBreadCrumb,
        blogType   = blogType,
        h1  =  h1,
        h2  =  h2,
        dateLine   =  da,
        content    = innerCnt,
    )

    return render_template(
        "index.html",
        content=outerCnt,
    )






if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=True,
        port=5000,
        use_reloader=False,
    )
