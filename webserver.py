from flask import Flask, render_template, jsonify, request, send_file, Response
import json
import glob
from check_gt import check_gt_file
from main import analysis_files, get_config, set_config
from cluster_to_graph import imagecluster_get_cluster, get_coin_findspots, map_clusters_to_findspots, plot_coint_per_die
from matching_plot import get_matches_plot


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
        ri, ari, ami = check_gt_file(path, side)
        selected = ""
        if config["dataset-reverse"] == name:
            selected = "r"
        if config["dataset-obverse"] == name:
            selected = "a"

        analysis_list.append((name, ri, ari, selected, ami))

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
    clusters_r = imagecluster_get_cluster("rsc/" + config["dataset-reverse"], "r")
    clusters_a = imagecluster_get_cluster("rsc/" + config["dataset-obverse"], "a")
    clusters = clusters_r | clusters_a
    coin_findspots = get_coin_findspots()
    clusters_at_findspot = map_clusters_to_findspots(clusters, coin_findspots)

    return jsonify(clusters_at_findspot[cluster_id])


@app.route("/coinimg")
def coinimg():
    coin_id = request.args.get("id", "")
    side = request.args.get("side", "r")

    config = get_config()
    folder = config["images-reverse"] if side == "r" else config["images-obverse"]
    pattern = folder + "/*_" + coin_id + "_*"
    paths = glob.glob(pattern, recursive=False)
    return send_file(paths[0], mimetype="image/png")


@app.route("/coinsperdiechart")
def coinsperimg_chart():
    analysis_file = request.args.get("file", "")
    side = "r" if ("reverse" in analysis_file) else "a"
    clusters = imagecluster_get_cluster("rsc/" + analysis_file, side)
    buffer = plot_coint_per_die(clusters)
    return send_file(buffer, mimetype="image/svg+xml")


@app.route("/coinmatching")
def coinmatching_img():
    coin_id1 = request.args.get("coinid1", "")
    coin_id2 = request.args.get("coinid2", "")
    side = request.args.get("side", "r")
    num_matches, img_matches = get_matches_plot(coin_id1, coin_id2, side)
    return send_file(img_matches, mimetype="image/jpeg")


# Temp
@app.route("/findspotcoords")
def findspotcoords():
    with open("fs_coords.json", "r") as f:
        data = json.load(f)
    coords_data = jsonify(data)
    return coords_data


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5001", debug=True)
