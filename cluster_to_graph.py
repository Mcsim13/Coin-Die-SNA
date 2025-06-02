import json
import csv


def get_findspots():
    findspots = dict()
    with open("bushel_series_DataChallenge_2025-numisdata4-2_TypenEinzeln.csv", "r") as numisdata_file:
        _ = next(numisdata_file)
        numisdata = csv.reader(numisdata_file, delimiter=";")
        for row in numisdata:
            findspots[row[13]] = findspots.get(row[13], 0) + 1

    return findspots


def get_coin_findspots():
    coin_findspots = {}
    with open("bushel_series_DataChallenge_2025-numisdata4-2_TypenEinzeln.csv", "r") as numisdata_file:
        _ = next(numisdata_file)
        numisdata = csv.reader(numisdata_file, delimiter=";")
        for row in numisdata:
            coin_findspots[row[0]] = row[13]

    return coin_findspots


def imagecluster_get_cluster(cluster_json):
    with open(cluster_json, "r") as cluster_file:
        cluster_raw = json.load(cluster_file)

    clusters = {}
    for coin, cluster in cluster_raw.items():
        clusters.setdefault(cluster, []).append(coin.split("_")[0])

    return clusters


def map_clusters_to_findspots(clusters, coin_findspots):
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


"""
Nodes = Cluster at Findspot
Edges = Nodes with same cluster
"""
def imagecluster_to_gephi_graph_reduced(node_csv, edge_csv):
    clusters = imagecluster_get_cluster("cluster_result_rueckseite.json")
    coin_findspots = get_coin_findspots()

    # Nodes
    clusters_at_findspot = map_clusters_to_findspots(clusters, coin_findspots)

    print(len(clusters_at_findspot), "Clusters")

    # Write Nodes
    nodes = []
    with open(node_csv, "w", newline="") as node_file:
        writer = csv.writer(node_file)
        writer.writerow(["Id", "Cluster", "Findspot", "CoinCout", "Coins"])

        for cluster, coin_findspots in clusters_at_findspot.items():
            for fs, coins in coin_findspots.items():
                node = [cluster + "_" + fs, cluster, fs, len(coins), coins]
                nodes.append(node)
                writer.writerow(node)

    # Edges
    edges = []
    for cluster, coin_findspots in clusters_at_findspot.items():
        findspots = list(coin_findspots.keys())
        edges.extend(connect_nodes_pairwise(findspots, name_prefix=cluster))

    print(len(edges), "Edges")

    # Write Edges
    with open(edge_csv, "w", newline="") as edge_file:
        writer = csv.writer(edge_file)
        writer.writerow(["Source", "Target", "Type"])

        for edge in edges:
            writer.writerow([edge[0], edge[1], "Undirected"])

    return clusters_at_findspot, nodes, edges


"""
Edges = Same findspot
"""
def findspot_edges_gephi(findspot_nodes, findspot_edges_csv):
    # nodes_flat = [node[0] for node in findspot_nodes]
    edges = []
    for i in range(len(findspot_nodes)):
        for k in range(i+1, len(findspot_nodes)):
            if (findspot_nodes[i][2] == findspot_nodes[k][2]):
                edges.append((findspot_nodes[i][0], findspot_nodes[k][0]))

    print(len(edges), "Findspot Edges")

    # Write Edges
    with open(findspot_edges_csv, "w", newline="") as edge_file:
        writer = csv.writer(edge_file)
        writer.writerow(["Source", "Target", "Type", "Label"])

        for edge in edges:
            writer.writerow([edge[0], edge[1], "Undirected", "findspot"])


"""
Nodes = Coins
Edges = Same Cluster
"""
def imagecluster_to_gephi_graph(cluster_json, node_csv, edge_csv):
    with open(cluster_json, "r") as cluster_file:
        cluster_raw = json.load(cluster_file)

    # print(cluster_raw)

    # Nodes
    with open(node_csv, "w", newline="") as node_file:
        writer = csv.writer(node_file)

        writer.writerow(["Id", "Side"])

        for coin, cluster in cluster_raw.items():
            writer.writerow([coin.split("_")[0], coin.split("_")[1]])

    # Edges
    clusters = {}
    for coin, cluster in cluster_raw.items():
        clusters.setdefault(cluster, []).append(coin.split("_")[0])

    print(len(clusters), "Cluster")

    edges = []
    for coins in clusters.values():
        if len(coins) > 1:
            for i in range(len(coins)):
                for k in range(i + 1, len(coins)):
                    edges.append((coins[i], coins[k]))

    print(len(edges), "Edges")

    with open(edge_csv, "w", newline="") as edge_file:
        writer = csv.writer(edge_file)

        writer.writerow(["Source", "Target", "Type"])

        for edge in edges:
            writer.writerow([edge[0], edge[1], "Undirected"])


"""
Nodes = Cluster, Findspots
Edges = Coin of Cluster found at findspot 
"""
def imagecluster_to_gephi_graph_v3(node_csv, edge_csv):
    clusters = imagecluster_get_cluster("cluster_result_rueckseite.json")
    coin_findspots = get_coin_findspots()
    findspots = get_findspots()
    #print(clusters)
    #print(coin_findspots)
    print(findspots)

    # Nodes
    clusters_at_findspot = map_clusters_to_findspots(clusters, coin_findspots)
    # print(clusters_at_findspot)
    print(len(clusters_at_findspot), "Clusters")

    # Write Nodes
    nodes = []
    with open(node_csv, "w", newline="") as node_file:
        writer = csv.writer(node_file)
        writer.writerow(["Id", "Type", "Label", "CoinCout", "Coins"])

        for cluster, coins in clusters.items():
            node = [cluster, "Cluster", cluster, len(coins), coins]
            nodes.append(node)
            writer.writerow(node)

        for findspot, num_coins in findspots.items():
            node = [findspot, "Findspot", findspot, num_coins, []]
            nodes.append(node)
            writer.writerow(node)

    # Edges
    edges = []
    for cluster, coins_at_findspot in clusters_at_findspot.items():
        for findspot, coins in coins_at_findspot.items():
            edges.append((cluster, findspot, len(coins)))

    # print(edges)
    print(len(edges), "Edges")

    # Write Edges
    with open(edge_csv, "w", newline="") as edge_file:
        writer = csv.writer(edge_file)
        writer.writerow(["Source", "Target", "Type", "Weight"])

        for edge in edges:
            writer.writerow([edge[0], edge[1], "Undirected", edge[2]])


if __name__ == "__main__":
    # imagecluster_to_gephi_graph("cluster_result_rueckseite.json", "imagecluster_reverse_nodes.csv", "imagecluster_reverse_edges.csv")

    # clusters_at_findspot, nodes, edges = imagecluster_to_gephi_graph_reduced("imagecluster_reverse_nodes.csv", "imagecluster_reverse_edges.csv")
    # findspot_edges_gephi(nodes, "imagecluster_reverse_findspot_edges.csv")

    imagecluster_to_gephi_graph_v3("imagecluster_reverse_nodes.csv", "imagecluster_reverse_edges.csv")
