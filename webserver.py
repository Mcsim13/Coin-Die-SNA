from flask import Flask, render_template, jsonify, request, send_file
import json
import glob
from check_gt import check_gt_file
from main import analysis_files, get_config, set_config
from cluster_to_graph import imagecluster_get_cluster, get_coin_findspots, map_clusters_to_findspots


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


@app.route("/analysislist")
def analysislist_api():
    analysis_list = []
    config = get_config()
    for path, name in analysis_files():
        side = "r" if ("reverse" in name) else "a"
        ri, ari = check_gt_file(path, side)
        selected = ""
        if config["dataset-reverse"] == name:
            selected = "r"
        if config["dataset-obverse"] == name:
            selected = "a"

        analysis_list.append((name, ri, ari, selected))

    json_data = jsonify(analysis_list)
    return json_data


@app.route("/config")
def config_api():
    return jsonify(get_config())


@app.route("/configset", methods=["POST"])
def config_set_api():
    data = json.loads(request.data)
    print(data)
    key = data.get("key")
    value = data.get("value")
    set_config(key, value)
    return jsonify({"response": "ok"})


@app.route("/cluster")
def cluster_api():
    cluster_id = request.args.get("clusterId", "")

    config = get_config()
    clusters = imagecluster_get_cluster("rsc/" + config["dataset-reverse"])
    coin_findspots = get_coin_findspots()
    clusters_at_findspot = map_clusters_to_findspots(clusters, coin_findspots)

    return jsonify(clusters_at_findspot[cluster_id])


@app.route("/coinimg")
def coinimg():
    coin_id = request.args.get("id", "")

    config = get_config()
    pattern = config["images-reverse"] + "/*_" + coin_id + "_*"
    paths = glob.glob(pattern, recursive=False)
    return send_file(paths[0], mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True)
