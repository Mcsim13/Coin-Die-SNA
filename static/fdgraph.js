import { openInspector, openInspectorFs } from "./main.js";
/* ISC License

Copyright 2017–2023 Observable, Inc.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
*/
function fdGraph(
    data, snaMetricsNode, snaMetricsEdge, communities
) {
    const width = 1000;
    const height = 600;

    const color = d3.scaleOrdinal(["Findspot", "Clusterr", "Clustera"], ["#0ec253ff", "#1c4ee4ff", "#08b7dfff"]);
    const colorLinks = d3.scaleOrdinal(d3.quantize(d3.interpolateTurbo, communities.length + 1));

    const links = data.edges.map(d => ({ ...d }));
    const nodes = data.nodes.map(d => ({ ...d }));

    nodes.forEach(node => {
        for (let elem of snaMetricsNode) {
            if (elem.node === node.id) {
                node.numEdges = elem.num_edges;
                node.betweenness_centrality = elem.betweenness_centrality;
            }
        }
    })

    links.forEach(edge => {
        for (let elem of snaMetricsEdge) {
            if ((elem.From === edge.source && elem.To === edge.target) || (elem.From === edge.target && elem.To === edge.source)) {
                edge.betweenness_centrality = elem.edge_betweeness_centrality;
            }
        }

        for (let community of communities) {
            for (let elem of community.edges) {
                if ((elem[0] === edge.source && elem[1] === edge.target) || (elem[0] === edge.target && elem[1] === edge.source)) {
                    edge.community = community.id;
                    break;
                }
            }
        }
    })

    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(d => 10))
        .force("charge", d3.forceManyBody().strength(-100))
        .force("collide", d3.forceCollide((d) => 10/*d.numEdges*/))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .on("tick", ticked)
        .alphaMin(0.001);

    const svg = d3.create("svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", [0, 0, width, height])
        .attr("cursor", "grab");

    const g = svg.append("g");

    const link = g.append("g")
        .attr("stroke-opacity", 0.7)
        .selectAll()
        .data(links)
        .join("line")
        .attr("stroke", d => colorLinks(d.community) /* "#999" */)
        .attr("stroke-width", d => 1 + Math.sqrt(d.betweenness_centrality * 1000));

    const node = g.append("g")
        .selectAll("g")
        .data(nodes)
        .join("g")
        .attr("id", d => d.id)
        .attr("class", "node");

    node.append("circle")
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .attr("r", (d) => {
            if (d.type === "Findspot") {
                return 5 + Math.sqrt(d.betweenness_centrality * 1000);
            } else {
                return 3 + Math.sqrt(d.num_coins_in_cluster);
            }
        })
        .attr("fill", d => color(d.type + d.node_type));

    node.append("text")
        .attr("font-size", d => 6 + Math.sqrt(d.numEdges))
        .attr("font-weight", 500)
        .attr("fill", "var(--primary-text-color)")
        .attr("text-anchor", "middle")
        .attr("x", 0)
        .attr("y", 12)
        .text(d => d.id);

    node.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    node.on("click", (e) => {
        let id = e.currentTarget.id;
        let type = data.nodes.filter(d => d.id === id)[0].type;

        if (type === "Cluster") {
            openInspector(id);
        } else {
            openInspectorFs(id);
        }

        link.attr("class", "");
        let connectedLinks = link.filter(d => d.source.id == id || d.target.id == id)
            .attr("class", "sel");

        let connectedEdges = links.filter(d => d.source.id == id || d.target.id == id);

        for (let connection of connectedEdges) {
            let otherNode = connection.source.id != id ? connection.source : connection.target;
            if (otherNode.type == "Findspot") continue;
            let con2 = link.filter(d => d.source.id == otherNode.id || d.target.id == otherNode.id)
                .attr("class", "sel");
        }
    })

    function ticked() {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y)
            .attr("transform", d => `translate( ` + d.x + `,` + d.y + `)`);
    }

    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }
    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }
    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }

    svg.call(d3.zoom()
        //.extent([[0, 0], [width, height]])
        .scaleExtent([0.1, 5])
        .on("zoom", zoomed));

    function zoomed({ transform }) {
        g.attr("transform", transform)
    }

    return svg.node();
}

export { fdGraph }
