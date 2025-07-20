import json
import shutil
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
from jinja2 import Template
import webbrowser
import pandas as pd
import regex as re
import os

from cluster_to_graph import construct_graph_both_sides
from networkx.algorithms.community import greedy_modularity_communities
from config import get_config


def shorten_edges(edge_list):
    two_values_edge = [(a, b) for (a, b, _) in edge_list]
    pattern = re.compile(r"^\d{1,4}_[a-zA-Z]$")
    # remove Edges where one of the nodes is '' (Ignoring Clusters or Cluster edges that have no findspot)
    filtered_two_value_edge = [(c, d) for (c, d) in two_values_edge if c != '' and d != '']
    # only keep edges between a cluster and a place
    relevant_edges = [(e, f) for (e, f) in filtered_two_value_edge if not (pattern.match(e) and pattern.match(f))]
    return relevant_edges

def create_graph(edge_list, node_list, remove_low_degree_clusters, filter = []):
    network_graph = nx.Graph()
    edges = [("a","b"), ("b","c")]
    #print(edge_list)
    network_graph.add_edges_from(edge_list)


    if remove_low_degree_clusters == True:
        pattern = re.compile(r"^\d{1,4}_[a-zA-Z]$")
        removal = [
            node for node in network_graph.nodes()
            if network_graph.degree(node) == 1 and pattern.match(node)
        ]
        network_graph.remove_nodes_from(removal)

    attributes = {}

    for node in node_list:
        node_id = node[0]
        if node_id in network_graph:
            if node[1] == "Cluster":
                attributes[node_id] = {
                    "type" : node[1],
                    "cluster_id" : node_id,
                    "num_coins_in_cluster" : node[3],
                    "coins_in_cluster": node[4],
                    "node_type" : node[5],
                    "time_frame" : node[6]
                    }
            elif node[1] == "Findspot":
                attributes[node_id] = {
                    "type" : node[1],
                    "Findspot_name" : node_id,
                    "num_coins_at_findspot" : node[3],
                    "coins_at_findspot" : node[4],
                    "findspot_coordinates" : node[5],
                    "findspot_type" : node[6]
                    }
    nx.set_node_attributes(network_graph, attributes)

    if len(filter) > 0:
        for filter_variable in filter:
            removal_filter = [
                entry for entry, attributes in network_graph.nodes(data=True)
                if attributes.get("type") == "Cluster" and attributes.get("time_frame") == filter_variable
            ]
            print(removal_filter)
            network_graph.remove_nodes_from(removal_filter)

    nx.draw(network_graph, with_labels=True)
    plt.show()
    net = Network(height="800px", width="100%", notebook=False)
    net.from_nx(network_graph)

    

    with open("template.html", "r", encoding='utf8') as f:
        html_template = Template(f.read())
        net.template = html_template
    
    #net.show("network_graph.html")
    
    html_content = net.generate_html()

    with open(r"SNA_results/network_graph.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    


    webbrowser.open(r"SNA_results/network_graph.html")
    clusters = list(nx.connected_components(network_graph)) 
    #print(clusters)
    #graph_export = (nx.connected_components(network_graph))
    #print(graph_export)
    return network_graph

def network_Analysis(graph):

    
    degree_centrality = nx.degree_centrality(graph)
    #print(degree_centrality)

    
    closeness_centrality = nx.closeness_centrality(graph)
    #print(closeness_centrality)

    
    betweenness_centrality = nx.betweenness_centrality(graph)
    #print(betweenness_centrality)

    
    eigenvector_centrality = nx.eigenvector_centrality(graph)
    #print(eigenvector_centrality)

    pagerank = nx.pagerank(graph)
    #print(pagerank)

    av_neighbor_degree = nx.average_neighbor_degree(graph)

    #eccentricity = nx.eccentricity(graph)

    edge_betweeness_centrality = nx.edge_betweenness_centrality(graph)
    #print(edge_betweeness_centrality)

    edge_load_centrality = nx.edge_load_centrality(graph)

    num_edges = dict(graph.degree())

    sna_node_metrics = []
    sna_edge_metrics = []

    for node in graph.nodes():
        sna_node_metrics.append({

            "node" : node,
            "num_edges": num_edges.get(node, 0),
            "degree_centrality" : degree_centrality.get(node, 0),
            "closeness_centrality" : closeness_centrality.get(node, 0),
            "betweenness_centrality" : betweenness_centrality.get(node, 0),
            "eigenvector_centrality" : eigenvector_centrality.get(node, 0),
            "pagerank" : pagerank.get(node, 0),
            "av_neighbor_degree" : av_neighbor_degree.get(node, 0),
            #"eccentricity" : eccentricity.get(node, 0)

        })

    for a , b in graph.edges():
        key = tuple(sorted((a, b)))
        sna_edge_metrics.append({
            "From" : a,
            "To" :  b,
            "edge_betweeness_centrality" : edge_betweeness_centrality.get(key, 0),
            "edge_load_centrality" : edge_load_centrality.get(key, 0)
        })
    

    #print(sna_metrics)
    with open(r"SNA_results/node_sna_metrics.json", "w") as f:
        json.dump(sna_node_metrics, f, indent=2)

    with open(r"SNA_results/edge_sna_metrics.json", "w") as f_2:
        json.dump(sna_edge_metrics, f_2, indent=2)


def get_subgraphs(graph):

    directory = "subgraphs"

    if os.path.exists(directory):
        shutil.rmtree(directory)  # removes all contents
    os.makedirs(directory)
    
    communities = list(greedy_modularity_communities(graph))
    communities = [community for community in communities if len(community) > 1]
    community_data = []

    for counter, entry in enumerate(communities):
        subgraph = graph.subgraph(entry).copy()

        nodes = list(subgraph.nodes())
        edges = list(subgraph.edges())

        community_data.append({
            "id" : counter,
            "nodes" : nodes,
            "edges" : [list(edge) for edge in edges]
        })
        
        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(subgraph, seed=50)
        nx.draw(subgraph, pos, with_labels = True, node_size=300)
        plt.title(f"Community_{counter}")

        save_path = os.path.join(directory, f"Community_{counter}.png")
        plt.savefig(save_path)
        plt.close

    with open(r"subgraphs/community_data.json", "w") as f:
        json.dump(community_data, f, indent=2)


def export_graph(graph):
    data1 = nx.node_link_data(graph, edges="edges")
    json_graph = json.dumps(data1, indent=4)
    with open("networkx_export.json", "w") as f:
        f.write(json_graph)


if __name__ == "__main__":

    config = get_config()

    nodes, edges = construct_graph_both_sides("rsc/" + config["dataset-reverse"], "rsc/" + config["dataset-obverse"])

    #print(nodes)

    short_edges = shorten_edges(edges)

    NetworkX_Graph = create_graph(short_edges, nodes, True, ["A", "B"])

    network_Analysis(NetworkX_Graph)

    get_subgraphs(NetworkX_Graph)

    #print(NetworkX_Graph.nodes["2009_r"])
    #print(NetworkX_Graph.nodes["Manching"])

    print(NetworkX_Graph)
    data1 = nx.node_link_data(NetworkX_Graph, edges="edges")
    json_graph = json.dumps(data1, indent=4)
    with open("networkx_export.json", "w") as f:
        f.write(json_graph)
