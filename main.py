from config import get_config
from cluster_to_graph import construct_graph_both_sides
from NetworkX_SNA import shorten_edges, create_graph, network_Analysis, export_graph


def social_network_analysis_pipeline():
    config = get_config()

    # Graph Konstruktion
    nodes, edges = construct_graph_both_sides("rsc/" + config["dataset-reverse"], "rsc/" + config["dataset-obverse"])

    # Social Network Analysis
    short_edges = shorten_edges(edges)
    NetworkX_Graph = create_graph(short_edges, nodes, True)
    network_Analysis(NetworkX_Graph)

    # Export
    export_graph(NetworkX_Graph)


if __name__ == "__main__":
    social_network_analysis_pipeline()
