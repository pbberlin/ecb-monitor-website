import os
import json
import random
from   datetime   import datetime, timedelta
from   pathlib    import Path

import pandas as pd
import matplotlib




from   flask import Flask, request, render_template, send_from_directory, Response
app  = Flask(__name__)



from lib.page1   import getAllPredictions
from lib.util    import truncateUtf8
from lib.gingado import load_CB_speeches


wd = os.getcwd()
dirDl = Path(".") / "data" / "dl"


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

    # jinja template
    return render_template(
            "index.html",
            title   = "EZB Transparenzmonitor",
            content = cnt,
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
    return render_template(
        "index.html",
        title="EZB Transparenzmonitor",
        # cnt = "dummy",
        content=cnt,
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



@app.route('/ecb-speeches')
def fetch():


    fPth = dirDl / "speeches.pkl"
    reload  = False
    speeches = None

    if fPth.exists():
        fileDate = datetime.fromtimestamp(fPth.stat().st_mtime)
        if fileDate < datetime.now() - timedelta(hours=24):
            reload = True
    else:
        reload = True

    if reload:
        # https://bis-med-it.github.io/gingado/datasets.html
        speeches = load_CB_speeches(2020, cache=False)
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


    return render_template(
            "index.html",
            title   =  "EZB Transparenzmonitor",
            content = f"Reloaded {reload} <br>  {hd.to_html()}  <pre>  {hd} </pre>",
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
