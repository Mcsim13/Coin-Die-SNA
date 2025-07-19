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
function mapGraph(
    data, svg, map, snaMetricsNode, snaMetricsEdge
) {
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    const links = data.edges.map(d => ({ ...d }));
    const nodes = data.nodes.map(d => ({ ...d })).filter(d => d.type == "Cluster");
    const fsNodes = data.nodes.map(d => ({ ...d })).filter(d => d.type == "Findspot");

    fsNodes.forEach(node => {
        const layerPoint = map.latLngToLayerPoint(node.findspot_coordinates);
        node.fx = layerPoint.x;
        node.fy = layerPoint.y;

        for (let elem of snaMetricsNode) {
            if (elem.node === node.id) {
                node.betweenness_centrality = elem.betweenness_centrality;
            }
        }
    })

    nodes.forEach(node => {
        for (let elem of snaMetricsNode) {
            if (elem.node === node.id) {
                node.numEdges = elem.num_edges;
            }
        }
    })

    links.forEach(edge => {
        for (let elem of snaMetricsEdge) {
            if ((elem.From === edge.source && elem.To === edge.target) || (elem.From === edge.target && elem.To === edge.source)) {
                edge.betweenness_centrality = elem.edge_betweeness_centrality;

            }
        }
    })

    const simulation = d3.forceSimulation([...nodes, ...fsNodes])
        .force("link", d3.forceLink(links).id(d => d.id).distance(30))
        .force("charge", d3.forceManyBody().strength(-50))
        .force("collide", d3.forceCollide((d) => 10 + Math.sqrt(d.numEdges)))
        // .force("center", d3.forceCenter(width / 2, height / 2))
        .on("tick", ticked)
        .alphaMin(0.01);


    const g = svg.select("g");

    const link = g.append("g")
        .attr("stroke", "#444")
        .attr("stroke-opacity", 0.6)
        .selectAll()
        .data(links)
        .join("line")
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
        .attr("r", d => 3 + Math.sqrt(d.num_coins_in_cluster))
        .attr("fill", d => color(d.type + d.node_type));

    node.append("text")
        .attr("font-size", d => 6 + Math.sqrt(d.numEdges))
        .attr("x", 0)
        .attr("y", 12)
        .text(d => d.id);

    node.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    node.on("click", (e) => {
        let id = e.currentTarget.id;
        openInspector(id);

        link.attr("class", "");
        let connectedLinks = link.filter(d => d.source.id == id || d.target.id == id)
            .attr("class", "sel");
    })

    const fsNode = g.append("g")
        .selectAll("g")
        .data(fsNodes)
        .join("g")
        .attr("id", d => d.id)
        .attr("class", "node");

    fsNode.append("circle")
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .attr("r", d => 5 + Math.sqrt(d.betweenness_centrality * 200))
        .attr("fill", d => color(d.type + d.node_type));

    fsNode.append("text")
        .attr("font-size", d => 6 + Math.sqrt(d.numEdges))
        .attr("x", 0)
        .attr("y", 16)
        .text(d => d.id);

    fsNode.on("click", (e) => {
        let id = e.currentTarget.id;
        openInspectorFs(id);

        link.attr("class", "");
        let connectedLinks = link.filter(d => d.source.id == id || d.target.id == id)
           .attr("class", "sel");
        
        let connectedEdges = links.filter(d => d.source.id == id || d.target.id == id);
        
        for (let connection of connectedEdges) {
            let otherNode = connection.source.id != id ? connection.source.id : connection.target.id;
            let con2 = link.filter(d => d.source.id == otherNode || d.target.id == otherNode)
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

    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        if (d.fx === undefined && d.fy === undefined) {
            d.fx = d.x;
            d.fy = d.y;
        }
    }
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        if (!d.fixed) {
            d.fx = null;
            d.fy = null;
        }
    }

    function drawAndUpdate() {
        fsNode
            .attr("transform", (d) => {
                let layerPoint = map.latLngToLayerPoint(d.findspot_coordinates);
                /* d.x = layerPoint.x;
                d.y = layerPoint.y; */
                d.fx = layerPoint.x;
                d.fy = layerPoint.y;
                return `translate(${layerPoint.x},${layerPoint.y})`;
            })

        simulation.alpha(0.1).restart();
    }

    drawAndUpdate();
    map.on("moveend", drawAndUpdate);

    return svg.node();
}

export { mapGraph }
