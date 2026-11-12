"""Microservice for search."""
from flask import Flask, request, jsonify, redirect
from search_engine import SearchEngine

# TODO: Refactor to use FastAPI for strict typing.

app = Flask(__name__)
search_engine = SearchEngine()


@app.route("/")
def redirect_to_test():
    return redirect("/test", code=302)


@app.route("/test", methods=["GET"])
def test():
    return "Container is running", 200


@app.route("/index", methods=["GET"])
def index():
    search_engine.index()
    return "Indexing done!", 200


@app.route("/ranking", methods=["GET"])
def retrieve():
    query = request.args.get("query", None)
    response = search_engine.retrieve(query)
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
