"""Flask backend. Serves the API and (for convenience) the ../frontend folder."""
import os
import random

from flask import Flask, jsonify, request, send_from_directory

from benchmark import run_benchmark
from search import MODES, linear_cost, record_steps

HERE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.join(HERE, "..", "frontend")

app = Flask(__name__, static_folder=FRONT, static_url_path="")


@app.after_request
def cors(resp):
    # so the frontend can also run from a different port while developing
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


def check(arr, target, mode):
    if mode not in MODES:
        return "mode must be any, first or last"
    if not isinstance(arr, list) or not 1 <= len(arr) <= 60:
        return "array needs 1 to 60 numbers"
    if not all(isinstance(x, int) and abs(x) <= 9999 for x in arr):
        return "array must hold whole numbers up to 9999"
    if arr != sorted(arr):
        return "array must be sorted"
    if isinstance(target, bool) or not isinstance(target, (int, float)):
        return "target must be a number"
    return None


@app.get("/")
def home():
    return send_from_directory(FRONT, "index.html")


@app.get("/api/random-list")
def random_list():
    size = max(1, min(request.args.get("size", 16, type=int), 60))
    top = round(size * 1.6) + 10  # small range on purpose, gives duplicates
    return jsonify(array=sorted(random.randint(1, top) for _ in range(size)))


@app.post("/api/search")
def search():
    body = request.get_json(silent=True) or {}
    arr, target, mode = body.get("array"), body.get("target"), body.get("mode", "any")
    problem = check(arr, target, mode)
    if problem:
        return jsonify(error=problem), 400
    return jsonify(steps=record_steps(arr, target, mode), linear=linear_cost(arr, target, mode))


@app.get("/api/benchmark")
def benchmark():
    return jsonify(run_benchmark())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
