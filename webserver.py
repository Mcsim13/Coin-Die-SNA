from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/graphdata")
def graphdata_api():
    with open("networkx_export.json", "r") as f:
        data = json.load(f)
    graph_data = jsonify(data)
    return graph_data


if __name__ == "__main__":
    app.run(debug=True)
