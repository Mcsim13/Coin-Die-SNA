import { getRequest, postRequest } from "./utils.js"
import { fdGraph } from "./fdgraph.js"
import { initMap } from "./map.js"

let openInspector = async (id) => {
    $("#inspector-container").show();
    $("#inspector-heading").html(id);
    $("#inspector-comparison").html("");
    $("#inspector-comparison-heading").show();

    let clusterData = await getRequest("cluster", { clusterId: id });
    console.log(clusterData);
    $("#coin-section").html("");
    for (let fs in clusterData) {
        let sectionHtml = /*html*/`<h4 style="margin: 8px 0">${fs}</h4><div class="grid">`;
        for (let coin of clusterData[fs]) {
            sectionHtml += /*html*/`
                        <label class="sec flex coin-img-container">
                        <img class="coin-img" alt="${coin}" src="coinimg?id=${coin}&side=${id.split("_")[1]}">
                        <input type="checkbox" value="${coin}_${id.split("_")[1]}" name="compare-coins">${coin}
                        </label>
                    `;
        }
        sectionHtml += `</div>`;
        $("#coin-section").append(sectionHtml)
    }
}

let openInspectorFs = async (id) => {
    $("#inspector-container").show();
    $("#inspector-heading").html(id);
    $("#inspector-comparison").html("");
    $("#inspector-comparison-heading").hide();

    // TODO
    // let fsData = await getRequest("findspot", { fs: id });
    // console.log(fsData);
    $("#coin-section").html("");
    /* for (let fs in fsData) {
        let sectionHtml = `<h4 style="margin: 8px 0">${cluster}</h4><div class="grid">`;
        for (let coin of fsData[fs]) {
            sectionHtml += `
                        <label class="sec flex coin-img-container">
                        <img class="coin-img" alt="${coin}" src="coinimg?id=${coin}&side=${id.split("_")[1]}">
                        <input type="checkbox" value="${coin}_${id.split("_")[1]}" name="compare-coins">${coin}
                        </label>
                    `;
        }
        sectionHtml += `</div>`;
        $("#coin-section").append(sectionHtml)
    } */
}

let openAnalysisDataPage = async () => {
    $("#analysis-data-container").show();

    const analysisList = await getRequest("analysislist", {});
    console.log(analysisList);
    $("#analysis-list").html("");
    for (let analysis of analysisList) {
        $("#analysis-list").append(/*html*/`
            <div class="list-item">
                <div class="flex">
                    <label class="file-name">${analysis[0]}</label>
                    <div class="flex" style="gap: 8px">
                        <label class="sec">RI</label>
                        <label style="width: 30px">${Math.round(analysis[1] * 100) / 100}</label>
                        <label class="sec">ARI</label>
                        <label style="color: hsl(${((analysis[2]) * 128)}, 100%, 40%); width: 30px">${Math.round(analysis[2] * 100) / 100}</label>
                        <label class="sec">AMI</label>
                        <label style="color: hsl(${((analysis[4]) * 128)}, 100%, 40%); width: 30px">${Math.round(analysis[4] * 100) / 100}</label>
                        <label><input type="radio" name="dataset-obverse" value="${analysis[0]}" ${analysis[3] === "a" ? "checked" : ""}>Av</label>
                        <label><input type="radio" name="dataset-reverse" value="${analysis[0]}" ${analysis[3] === "r" ? "checked" : ""}>Rv</label>
                    </div>
                </div>
                <div class="coinsperdie-chart"></div>
            </div>
            `);
    }
}

let loadGraphs = async () => {
    const graph_data = await getRequest("graphdata", {});
    console.log(graph_data);

    const snaMetricsNode = await getRequest("snametricsnode", {})
    const snaMetricsEdge = await getRequest("snametricsedge", {})

    let chart = fdGraph(graph_data, snaMetricsNode, snaMetricsEdge);
    $("#graph-container").html(chart);

    initMap(graph_data, snaMetricsNode, snaMetricsEdge);
}

/**
 * Event Handler
 */
$(() => {
    $("button#appearance").on("click", () => {
        $("body").toggleClass("white");
        $("button#appearance > i").toggleClass("fa-moon fa-sun");
    })

    $("button.tab").on("click", async (e) => {
        $("button.tab").removeClass("active");
        $(e.currentTarget).addClass("active");

        $("#main-pages").children().hide();
        if (e.currentTarget.id === "analysis-data-btn") {
            openAnalysisDataPage();
        } else if (e.currentTarget.id === "map-graph-btn") {
            $("#map-container").show();
        } else {
            $("#graph-container").show();
        }
    })

    $("#analysis-list").on("click", ".list-item", (e) => {
        let name = $(e.currentTarget).find(".file-name")[0].innerHTML;
        if ($(e.currentTarget).find(".coinsperdie-chart").html() === "") {
            $(e.currentTarget).find(".coinsperdie-chart").html(`<img src="coinsperdiechart?file=${name}">`);
        } else {
            $(e.currentTarget).find(".coinsperdie-chart").html("")
        }
    })

    $("#analysis-list").on("change", "input", (e) => {
        let key = e.currentTarget.name;
        let value = e.currentTarget.value;
        postRequest("configset", JSON.stringify({ key: key, value: value }));
    })

    $("#start-sna").on("click", async (e) => {
        $("#sna-check").hide();
        $("#sna-spinner").show();
        let response = await postRequest("snapipeline", JSON.stringify({}));
        $("#sna-spinner").hide();
        $("#sna-check").show();
        loadGraphs();
    })

    $("#close-inspector").on("click", () => {
        $("#inspector-container").hide();
    })

    $("#coin-section").on("change", "input[type=checkbox]", (e) => {
        let numChecked = $("#coin-section input[type=checkbox]:checked").length;
        if (numChecked > 2) {
            e.currentTarget.checked = false;
            return;
        }
        if (numChecked != 2) return;

        let coinId1 = $("#coin-section input[type=checkbox]:checked")[0].value.split("_")[0];
        let coinId2 = $("#coin-section input[type=checkbox]:checked")[1].value.split("_")[0];
        let side = $("#coin-section input[type=checkbox]:checked")[0].value.split("_")[1];
        $("#inspector-comparison").html(/*html*/`
            <img src="coinmatching?coinid1=${coinId1}&coinid2=${coinId2}&side=${side}" class="matching-img">
            <br>
            <img src="coinmatching?coinid1=${coinId2}&coinid2=${coinId1}&side=${side}" class="matching-img">
        `);
    })
})

/**
 * Start Script
 */
$(async () => {
    loadGraphs();
})

export { openInspector, openInspectorFs }
