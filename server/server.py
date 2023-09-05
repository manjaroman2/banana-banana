from typing import Any
from flask import (
    Flask,
    send_from_directory,
    send_file,
    request,
    stream_with_context,
    Response,
)
import utils
import json
import threading
import atexit


def jsonify(d) -> Response:
    return Response(json.dumps(d, cls=utils.FrankfurtDataEncoder), mimetype="application/json")

def json_error(message: str) -> Response:
    return jsonify({"error": message})

POOL_TIME = 5

sorted_data = list()
app = Flask(__name__)
data_lock = threading.Lock()
timer = threading.Timer(0, lambda x: None, ())


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
def hello_world():
    return """<script src="https://code.jquery.com/jquery-3.7.1.min.js" integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=" crossorigin="anonymous"></script><script src="js/main.js"></script><link rel="stylesheet" href="css/main.css">"""


@app.route("/api", methods=["GET"])
def api():
    # sort = request.args.get("s")
    # number = request.args.get("n")

    # if not sort:
    #     sort = "best"
    # if not number:
    #     number = 10
    # try:
    #     number = int(number)
    # except ValueError:
    #     return json_error("Invalid number, please use an integer")
    
    # if sort == "best":
    #     _s = (-number, -1)
    # elif sort == "worst":
    #     _s = (0, number)
    # else:
    #     return json_error("Invalid sort type, please use 'best' or 'worst'")

    # print(sort, number)
    global sorted_data
    data = None 
    # with data_lock:
    #     data = sorted_data[_s[0]:_s[1]]    
    with data_lock:
        data = sorted_data
    return jsonify(data)


def main_thread():
    global sorted_data
    global timer 
    for item in utils.data_generator(n=-1):
        with data_lock:
            sorted_data.append(item)
    # for item in utils.analyze_data():
    #     with data_lock:
    #         sorted_data.insert(*item)


def start_main_thread():
    global timer
    timer = threading.Timer(POOL_TIME, main_thread, ())
    timer.start()
    
def interrupt():
    global timer
    timer.cancel()

if __name__ == "__main__":
    start_main_thread()
    atexit.register(interrupt)
    
    app.run("0.0.0.0", 5000)
