from flask import (
    Flask,
    send_from_directory,
    send_file,
    request,
    stream_with_context,
    Response,
    redirect,
    jsonify
)
import utils

import threads as th 


def json_error(message: str) -> Response:
    return jsonify({"error": message})


app = Flask(__name__)
th.flask_app = app


@app.route("/js/<path:path>")
def send_javascript(path):
    return send_from_directory("js", path)


@app.route("/css/<path:path>")
def send_css(path):
    return send_from_directory("css", path)


@app.route("/favicon.ico")
def send_favicon():
    return send_file("favicon.ico")


@app.route("/")
def index():
    return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title></title>
        </head>
        <body>
            
        </body>
        <script src="js/data.js" type="module"></script>
        <script src="js/widgets.js" type="module"></script>
        <script src="js/utils.js" type="module"></script>
        <script src="js/main.js" type="module"></script>
        <link rel="stylesheet" href="css/main.css">
        </html>
    """


@app.route("/workout", methods=["GET"])
def workout():
    return """
        <script src="js/workout/main.js" type="module"></script>
        <link rel="stylesheet" href="css/workout/main.css">
    """


@app.route("/api/info", methods=["GET"])
def api_info():
    return jsonify(utils.get_info())


with app.app_context():
    th.create_threads(th.DataThread, th.ProxiesThread)
    

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=False)
