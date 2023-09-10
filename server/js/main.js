import { DropdownMenu, TableScroll, Topbar } from "./widgets.js";
import { Row, TableData } from "./data.js";
import { fibonacci } from "./utils.js";

var tableData = new TableData();
var numberDropdown = new DropdownMenu("Number");
var timeframeDropdown = new DropdownMenu("Timeframe");
var tableScroll = new TableScroll();
var topbar = new Topbar(
    {
        best: () => tableData[timeframeDropdown.value].sort((rowA, rowB) => rowA.performance - rowB.performance),
        worst: () => tableData[timeframeDropdown.value].sort((rowA, rowB) => rowA.performance - rowB.performance).reverse(),
    },
    updateTableDisplayTimeframe
);

var updateInterval = undefined;

const docTitle = "°º¤ø,¸¸,ø¤º°`°º¤ø,¸,ø¤°º¤ø,¸¸,ø¤º°`";
const docTitleFrames = [...Array(docTitle.length).keys()].map((i) => {
    return docTitle.slice(i, docTitle.length) + docTitle.slice(0, i);
});
var docTitleInterval = undefined;

async function getApiData(sort = "best", number = 10) {
    return fetch(
        "/api/data?" +
            new URLSearchParams({
                s: sort,
                n: number,
            })
    ).then((response) => response.json());
}

async function getApiInfo() {
    return fetch("/api/info").then((response) => response.json());
}

function updateTableDisplayTimeframe() {
    tableData.tbody.innerHTML = "";
    tableData[timeframeDropdown.value].forEach((row) => {
        tableData.tbody.append(row.tr);
        // row.sendDataToElementDOM();
    });

    updateTableDisplayEntries();
}

function updateTableDisplayEntries() {
    const allRows = tableData[timeframeDropdown.value];
    if (numberDropdown.value === "All") numberDropdown.value = allRows.length;
    for (let i = 0; i < numberDropdown.value; i++) allRows[i].tr.className = "visible";
    for (let i = numberDropdown.value; i < allRows.length; i++) allRows[i].tr.className = "hidden";
}

function intervalFunction() {
    startTitleAnimation();
    getApiData().then((jsonResponse) => {
        if (jsonResponse.hasOwnProperty("error")) console.error(jsonResponse);
        else if (jsonResponse.length == 0) console.info("no data");
        else {
            console.log(jsonResponse.length);
            timeframeDropdown.options.forEach((timeframe) =>
                jsonResponse.forEach((fData) => {
                    // console.log(fData)
                    tableData.addRow(new Row(fData, timeframe));
                    // console.log(tableData);
                })
            );
            // Populate number dropdown
            let numberOptions = fibonacci(Math.floor(jsonResponse.length / 10))
                .map((x) => 10 * x)
                .slice(1); // I love this
            numberOptions.push("All");
            numberDropdown.setOptions(numberOptions, updateTableDisplayEntries);
            if (numberDropdown.value == undefined) numberDropdown.value = jsonResponse.length;

            updateTableDisplayTimeframe();
        }
    });
    // .finally(endTitleAnimation);
}

function processApiInfo(infoData) {
    console.log(Object.keys(infoData));

    // Populate timeframe dropdown
    timeframeDropdown.setOptions(infoData["frankfurt"]["timeframe"], () => {
        updateTableDisplayTimeframe();
        updateTableDisplayEntries();
    });
    tableData.populateTimeframes(timeframeDropdown.options);
    tableScroll.outerDiv.append(tableData.table);
    topbar.updateIdx(0);
}


function startTitleAnimation() {
    console.log("start");
    var i = 0;
    function update() {
        document.title = docTitleFrames[i];
        // console.log(document.title);
    }
    update();
    docTitleInterval = setInterval(() => {
        i = (i + 1) % docTitle.length;
        update();
    }, 250);
}

function endTitleAnimation() {
    console.log("end");
    if (docTitleInterval != undefined) clearInterval(docTitleInterval);
}

window.addEventListener("keydown", function (ev) {
    switch (ev.keyCode) {
        case 39:
            topbar.arrowRight.click();
            ev.preventDefault();
            break;
        case 37:
            topbar.arrowLeft.click();
            ev.preventDefault();
            break;
    }
});

window.addEventListener("load", function (ev) {
    topbar.onLoad(document.body);
    tableScroll.onLoad(document.body);

    numberDropdown.createDOM(topbar.div);
    timeframeDropdown.createDOM(topbar.div);

    if (updateInterval != undefined) clearInterval(updateInterval);

    getApiInfo().then(processApiInfo).finally(intervalFunction);
    // updateInterval = setInterval(() => intervalFunction(), 5000);
});
