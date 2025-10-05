import json
import random
from   pathlib    import Path


from   flask import Flask, request, render_template, send_from_directory, Response
app  = Flask(__name__)



from lib.page1 import getAllPredictions



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
    # cnt = "dummy"
    return render_template(
        "index.html",
        title="EZB Transparenzmonitor",
        content=cnt,
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
