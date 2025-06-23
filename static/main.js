import { getRequest, postRequest } from "./utils.js"
import { fdGraph } from "./fdgraph.js"

let openInspector = async (id) => {
    $("#inspector-container").show();
    $("#inspector-heading").html(id);

    let clusterData = await getRequest("cluster", { clusterId: id });
    console.log(clusterData);
    $("#inspector-body").html("");
    for (let fs in clusterData) {
        let sectionHtml = /*html*/`<h4 style="margin: 8px 0">${fs}</h4><div class="grid">`;
        for (let coin of clusterData[fs]) {
            sectionHtml += /*html*/`
                        <div class="flex coin-img-container">
                        <img class="coin-img" alt="${coin}" src="coinimg?id=${coin}">
                        <label class="sec">${coin}</label>
                        </div>
                    `;
        }
        sectionHtml += `</div>`;
        $("#inspector-body").append(sectionHtml)
    }
}

$(() => {
    let appearance = "dark";
    $("button#appearance").on("click", () => {
        if (appearance === "dark") {
            $("body").addClass("white");
            $("button#appearance").html("Dark mode");
            appearance = "light";
        } else {
            $("body").removeClass("white");
            $("button#appearance").html("Light mode");
            appearance = "dark";
        }
    })

    $("button.tab").on("click", async (e) => {
        $("button.tab").removeClass("active");
        $(e.currentTarget).addClass("active");

        $("#main-pages").children().hide();
        if (e.currentTarget.id === "analysis-data-btn") {
            $("#analysis-data-container").show();

            const analysisList = await getRequest("analysislist", {});
            console.log(analysisList);
            $("#analysis-list").html("");
            for (let analysis of analysisList) {
                $("#analysis-list").append(/*html*/`
                            <div class="flex list-item">
                                <label>${analysis[0]}</label>
                                <div class="flex" style="gap: 8px">
                                    <label class="sec">RI</label>
                                    <label>${Math.round(analysis[1] * 100) / 100}</label>
                                    <label class="sec">ARI</label>
                                    <label>${Math.round(analysis[2] * 100) / 100}</label>
                                    <label><input type="radio" name="dataset-obverse" value="${analysis[0]}" ${analysis[3] === "a" ? "checked" : ""}>Av</label>
                                    <label><input type="radio" name="dataset-reverse" value="${analysis[0]}" ${analysis[3] === "r" ? "checked" : ""}>Rv</label>
                                </div>
                            </div>
                        `);
            }
        } else {
            $("#graph-container").show();
        }
    })

    $("#analysis-list").on("change", "input", (e) => {
        key = e.currentTarget.name;
        value = e.currentTarget.value;
        postRequest("configset", JSON.stringify({ key: key, value: value }));
    })

    $("#close-inspector").on("click", () => {
        $("#inspector-container").hide();
    })
})

$(async () => {
    const graph_data = await getRequest("graphdata", {});
    console.log(graph_data);

    let chart = fdGraph(graph_data);
    $("#graph-container").html(chart);
})

export { openInspector }
