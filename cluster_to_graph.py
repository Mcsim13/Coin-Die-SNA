import json
import csv
from findspot_geolocation import get_findspot_coordinate
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io


def get_findspots():
    """Returns { findspot: coin_count } dict"""
    findspots = dict()
    with open("bushel_series_DataChallenge_2025-numisdata4-2_TypenEinzeln.csv", "r") as numisdata_file:
        _ = next(numisdata_file)
        numisdata = csv.reader(numisdata_file, delimiter=";")
        for row in numisdata:
            findspots[row[13]] = findspots.get(row[13], 0) + 1

    return findspots


def get_coin_findspots():
    """Returns { coind_id: findspot } dict"""
    coin_findspots = {}
    with open("bushel_series_DataChallenge_2025-numisdata4-2_TypenEinzeln.csv", "r") as numisdata_file:
        _ = next(numisdata_file)
        numisdata = csv.reader(numisdata_file, delimiter=";")
        for row in numisdata:
            coin_findspots[row[0]] = row[13]

    return coin_findspots


def imagecluster_get_cluster(cluster_json):
    """Returns { cluster_id : [coin_id] } from { coin_id: cluster_id } input json"""
    with open(cluster_json, "r") as cluster_file:
        cluster_raw = json.load(cluster_file)

    clusters = {}
    for coin, cluster in cluster_raw.items():
        clusters.setdefault(cluster, []).append(coin.split("_")[0])

    return clusters


def map_clusters_to_findspots(clusters, coin_findspots):
    """
    Returns { cluster_id: { findspot: [coin_id] } }
    clusters: { cluster_id : [coin_id] }
    coin_findspots: { coind_id: findspot }
    """
    clusters_at_findspot = {}
    for cluster, coins in clusters.items():
        coins_at_fs = {}
        for coin in coins:
            fs = coin_findspots.get(coin, "")
            coins_at_fs.setdefault(fs, []).append(coin)

        clusters_at_findspot[cluster] = coins_at_fs

    return clusters_at_findspot


def connect_nodes_pairwise(node_list, name_prefix=""):
    edges = []
    for i in range(len(node_list)):
        for k in range(i + 1, len(node_list)):
            edges.append((name_prefix + "_" + node_list[i], name_prefix + "_" + node_list[k]))
    return edges


def construct_graph(cluster_file):
    """
    Nodes = Cluster, Findspots
    Edges = Coin of Cluster found at findspot
    """
    clusters = imagecluster_get_cluster(cluster_file)
    coin_findspots = get_coin_findspots()
    findspots = get_findspots()
    # print(clusters)
    # print(coin_findspots)
    # print(findspots)

    # Nodes
    clusters_at_findspot = map_clusters_to_findspots(clusters, coin_findspots)
    # print(clusters_at_findspot)
    print(len(clusters_at_findspot), "Clusters")

    # Write Nodes
    nodes = []
    for cluster, coins in clusters.items():
        node = [cluster, "Cluster", cluster, len(coins), coins]
        nodes.append(node)

    for findspot, num_coins in findspots.items():
        node = [findspot, "Findspot", findspot, num_coins, []]
        nodes.append(node)

    # Edges
    edges = []
    for cluster, coins_at_findspot in clusters_at_findspot.items():
        for findspot, coins in coins_at_findspot.items():
            edges.append((cluster, findspot, len(coins)))

    # print(edges)
    print(len(edges), "Edges")

    return nodes, edges


def networkX_graph():
    """
    OLD
    """
    G = nx.Graph()

    nodes, edges = construct_graph("rsc/die_studie_reverse_10_projhdbscan.json")

    node_names = [node[0] for node in nodes]
    edges_only = [edge[:2] for edge in edges]

    G.add_nodes_from(node_names)
    G.add_edges_from(edges_only)

    print(G)

    data1 = nx.node_link_data(G, edges="edges")
    # print(data1)
    json_graph = json.dumps(data1, indent=4)

    with open("networkx_export.json", "w") as f:
        f.write(json_graph)


def plot_coint_per_die(clusters):
    length_counts = {}

    for coins in clusters.values():
        length = len(coins)
        if length in length_counts:
            length_counts[length] += 1
        else:
            length_counts[length] = 1

    min_len = min(length_counts.keys())
    max_len = max(length_counts.keys())

    lengths = list(range(min_len, max_len + 1))
    counts = [length_counts.get(length, 0) for length in lengths]

    plt.figure(figsize=(8, 4))
    plt.bar(lengths, counts)
    plt.xlabel("Coins per die")
    plt.ylabel("Count")
    plt.xticks(lengths)
    plt.grid(axis="y", linestyle="-", alpha=0.7)
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format="svg")
    plt.close()
    buffer.seek(0)
    return buffer
    # plt.show()


def findspot_coordinates(findspots):
    fs_coordinates = dict()
    for fs, _ in findspots.items():
        coords = get_findspot_coordinate(fs)
        fs_coordinates[fs] = coords

    # print(fs_coordinates)
    json_coords = json.dumps(fs_coordinates, indent=4)

    with open("fs_coords.json", "w") as f:
        f.write(json_coords)


if __name__ == "__main__":
    # construct_graph("rsc/die_studie_reverse_7_projhdbscan.json", "imagecluster_reverse_nodes.csv", "imagecluster_reverse_edges.csv")

    # networkX_graph()

    # clusters = imagecluster_get_cluster("rsc/die_studie_reverse_10_projhdbscan.json")
    # plot_coint_per_die(clusters)

    findspots = get_findspots()
    findspot_coordinates(findspots)
