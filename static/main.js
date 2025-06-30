import { getRequest, postRequest } from "./utils.js"
import { fdGraph } from "./fdgraph.js"

let openInspector = async (id) => {
    $("#inspector-container").show();
    $("#inspector-heading").html(id);
    $("#inspector-comparison").html("");

    let clusterData = await getRequest("cluster", { clusterId: id });
    console.log(clusterData);
    $("#coin-section").html("");
    for (let fs in clusterData) {
        let sectionHtml = /*html*/`<h4 style="margin: 8px 0">${fs}</h4><div class="grid">`;
        for (let coin of clusterData[fs]) {
            sectionHtml += /*html*/`
                        <label class="sec flex coin-img-container">
                        <img class="coin-img" alt="${coin}" src="coinimg?id=${coin}">
                        <input type="checkbox" value="${coin}" name="compare-coins">${coin}
                        </label>
                    `;
        }
        sectionHtml += `</div>`;
        $("#coin-section").append(sectionHtml)
    }
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
                        <label style="color: hsl(${((analysis[2])*128)}, 100%, 40%); width: 30px">${Math.round(analysis[2] * 100) / 100}</label>
                        <label class="sec">AMI</label>
                        <label style="color: hsl(${((analysis[4])*128)}, 100%, 40%); width: 30px">${Math.round(analysis[4] * 100) / 100}</label>
                        <label><input type="radio" name="dataset-obverse" value="${analysis[0]}" ${analysis[3] === "a" ? "checked" : ""}>Av</label>
                        <label><input type="radio" name="dataset-reverse" value="${analysis[0]}" ${analysis[3] === "r" ? "checked" : ""}>Rv</label>
                    </div>
                </div>
                <div class="coinsperdie-chart"></div>
            </div>
            `);
    }
}

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

        let coinId1 = $("#coin-section input[type=checkbox]:checked")[0].value;
        let coinId2 = $("#coin-section input[type=checkbox]:checked")[1].value;
        $("#inspector-comparison").html(`
            <img src="coinmatching?coinid1=${coinId1}&coinid2=${coinId2}" class="matching-img">
            <img src="coinmatching?coinid1=${coinId2}&coinid2=${coinId1}" class="matching-img">
        `);
    })
})

$(async () => {
    const graph_data = await getRequest("graphdata", {});
    console.log(graph_data);

    let chart = fdGraph(graph_data);
    $("#graph-container").html(chart);
})

export { openInspector }
