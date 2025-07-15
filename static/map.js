import { mapGraph } from "./mapgraph.js"

async function initMap(graphData, snaMetricsNode, snaMetricsEdge) {
    const map = new L.Map("map-container", { zoomControl: false, dragging: true, zoomSnap: 0.05, zoomAnimation: false, fadeAnimation: false }).setView([48.029, 10.180], 7);

    const tiles = new L.TileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    new L.Control.Scale({ maxWidth: 200, position: 'bottomleft', imperial: false }).addTo(map);
    new L.Control.Zoom({ position: 'bottomleft' }).addTo(map);

    let svgGraphLayer = new L.SVG();
    svgGraphLayer.addTo(map);

    let svg = d3.select("#map-container").select("svg");

    graphData.nodes = graphData.nodes.filter(d => d.id !== "");
    graphData.edges = graphData.edges.filter(d => d.source !== "" && d.target !== "");

    let svgGraph = mapGraph(graphData, svg, map, snaMetricsNode, snaMetricsEdge);
}

export { initMap }