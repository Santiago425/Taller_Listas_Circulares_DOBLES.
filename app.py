from flask import Flask, jsonify, render_template, request

from transit import EmptyRouteError, RouteError, StopNotFoundError, build_sample_line

app = Flask(__name__)
line = build_sample_line()


def error_response(error):
    status = 404 if isinstance(error, (StopNotFoundError, EmptyRouteError)) else 400
    return jsonify({"error": str(error)}), status


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/route")
def get_route():
    return jsonify(line.snapshot())


@app.post("/api/stops")
def add_stop():
    payload = request.get_json(silent=True) or {}
    try:
        line.add_stop(
            payload.get("name"),
            payload.get("minutes"),
            payload.get("position", "end"),
            payload.get("reference"),
        )
    except RouteError as error:
        return error_response(error)
    return jsonify(line.snapshot()), 201


@app.get("/api/stops/<path:name>")
def find_stop(name):
    try:
        stop = line.find_stop(name)
    except RouteError as error:
        return error_response(error)
    return jsonify(stop.to_dict())


@app.delete("/api/stops/<path:name>")
def remove_stop(name):
    try:
        line.remove_stop(name)
    except RouteError as error:
        return error_response(error)
    return jsonify(line.snapshot())


@app.post("/api/bus/ahead")
def drive_ahead():
    try:
        line.drive_ahead()
    except RouteError as error:
        return error_response(error)
    return jsonify(line.snapshot())


@app.post("/api/bus/behind")
def drive_behind():
    try:
        line.drive_behind()
    except RouteError as error:
        return error_response(error)
    return jsonify(line.snapshot())


if __name__ == "__main__":
    app.run(debug=True)
