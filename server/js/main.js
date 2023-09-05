import { DropdownMenu } from "/js/widgets.js";

var updateInterval = undefined;
var sortElem = undefined;
var sortEnum = ["best", "worst"];
var sortEnumLongest = Math.max(...sortEnum.map((el) => el.length));
var sortEnumIdx = 0;
var rightArrows = undefined;
var leftArrows = undefined;
var topbar = undefined;
var timeframeToRow = {};

var numberDropdown = new DropdownMenu("Number");
var timeframeDropdown = new DropdownMenu("Timeframe");

function round(x, ndigits = 2) {
    return Math.round(x * 10 ** ndigits) / 10 ** ndigits;
}
function clearArray(a) {
    // WHY IS THIS NOT IMPLEMENTED BY DEFAULT???
    while (a.length > 0) {
        a.pop();
    }
}

const fibs = (limit, a = 1, b = 1) =>
    a > limit
        ? [] // #1
        : [a, ...fibs(limit, b, a + b)];

var table = document.createElement("table");
table.id = "table";
var tbody = document.createElement("tbody");
table.append(tbody);

// function addHeadersToTable() {
//     let nameHeader = document.createElement("th");
//     let yearsHeader = document.createElement("th");
//     let isinHeader = document.createElement("th");
//     let linkHeader = document.createElement("th");
// }

function addRowToTable(fData, timeframe) {
    let name = fData["name"];
    let performance = round(fData["performance"][timeframe]["changeInPercent"]);
    let isin = fData["isin"];
    let link = "https://www.boerse-frankfurt.de/" + fData["slug"];
    let tr = document.createElement("tr");

    let nameTd = document.createElement("td");
    let performanceTd = document.createElement("td");
    let isinTd = document.createElement("td");
    let linkTd = document.createElement("td");
    linkTd.className = "link-td";

    nameTd.innerHTML = name;
    nameTd.style.width = "300px";
    performanceTd.innerHTML = performance;
    performanceTd.style.width = "50px";
    isinTd.innerHTML = isin;
    isinTd.style.width = "100px";
    isinTd.style.userSelect = "text";
    let linkA = document.createElement("a");
    linkA.href = link;
    linkA.innerHTML = fData["slug"];
    linkTd.appendChild(linkA);
    linkTd.style.width = "100px";

    tr.append(nameTd, performanceTd, isinTd, linkTd);
    tbody.append(tr);

    timeframeToRow[timeframe].push(tr);
}

function updateTableDisplayEntries() {
    let allRows = tbody.childNodes;
    if (numberDropdown.value === "All") numberDropdown.value = allRows.length;
    for (let i = 0; i < numberDropdown.value; i++) {
        const element = allRows[i];
        element.className = "visible";
    }
    for (let i = numberDropdown.value; i < allRows.length; i++) {
        const element = allRows[i];
        element.className = "hidden";
    }
}

function addFunctionalityToArrows() {
    function updateSort() {
        sortElem.innerHTML = sortEnum[sortEnumIdx];
        sortElem.style.transform = "scale(0.95)";
        let timer = setTimeout(() => {
            sortElem.style.transform = "scale(1.0)";
        }, 100);
    }
    rightArrows = Array.from(document.getElementsByClassName("arrow right"));
    rightArrows.forEach((element) => {
        element.onclick = () => {
            sortEnumIdx = (sortEnumIdx + 1) % sortEnum.length;
            updateSort();
            updateTableSort();
        };
    });
    leftArrows = Array.from(document.getElementsByClassName("arrow left"));
    leftArrows.forEach((element) => {
        element.onclick = () => {
            sortEnumIdx = (sortEnumIdx - 1 + sortEnum.length) % sortEnum.length;
            updateSort();
            updateTableSort();
        };
    });
}

function createTopbar() {
    topbar = document.createElement("div");
    topbar.className = "topbar";
    let sortDiv = document.createElement("div");
    sortDiv.className = "sortDiv";
    sortDiv.insertAdjacentHTML(
        "afterbegin",
        `
        <span><i class="arrow left"></i></span>
        <span id="sort">best</span>
        <span><i class="arrow right"></i></span>`
    );
    topbar.append(sortDiv);
    return topbar;
}

function updateTableDisplayTimeframe() {
    for (const [timeframe, rows] of Object.entries(timeframeToRow)) {
        if (timeframe == timeframeDropdown.value)
            rows.forEach((e) => (e.className = "visible"));
        else rows.forEach((e) => (e.className = "hidden"));
    }
}
function reverseChildren(parent) {
    for (var i = 1; i < parent.childNodes.length; i++) {
        parent.insertBefore(parent.childNodes[i], parent.firstChild);
    }
}

function updateTableSort() {
    reverseChildren(tbody);
}

function getApiData(callback, sort = "best", number = 10) {
    fetch(
        "/api/data?" +
            new URLSearchParams({
                s: sort,
                n: number,
            })
    )
        .then((response) => response.json())
        .then((data) => callback(data));
}

window.onload = () => {
    document.body.append(createTopbar());
    document.body.append(table);
    // Bodybuilding done here

    sortElem = document.getElementById("sort");
    sortElem.innerHTML = sortEnum[sortEnumIdx];
    sortElem.style.width = sortEnumLongest * 4 + "vw";
    // addFunctionalityToArrows();

    numberDropdown.createDOM(topbar);
    timeframeDropdown.createDOM(topbar);

    if (updateInterval != undefined) clearInterval(updateInterval);
    function intervalFunction() {
        getApiData((jsonResponse) => {
            if (jsonResponse.hasOwnProperty("error"))
                console.error(jsonResponse);
            else if (jsonResponse.length == 0) console.info("no data");
            else {
                // console.log(jsonResponse.length);
                // console.log(timeframeOptions);
                timeframeDropdown.options.forEach((timeframe) =>
                    jsonResponse.forEach((e) => addRowToTable(e, timeframe))
                );

                // Populate number dropdown
                let numberOptions = fibs(Math.floor(jsonResponse.length / 10))
                    .map((x) => 10 * x)
                    .slice(1); // I love this
                numberOptions.push("All");
                numberDropdown.setOptions(
                    numberOptions,
                    updateTableDisplayEntries
                );
                if (numberDropdown.value == undefined)
                    numberDropdown.value = jsonResponse.length;

                updateTableDisplayTimeframe();
                updateTableDisplayEntries();
            }
        });
    }

    function getApiInfo() {
        fetch("/api/info")
            .then((response) => response.json())
            .then((data) => {
                // Populate timeframe dropdown
                timeframeDropdown.setOptions(
                    data["frankfurt"]["timeframe"],
                    updateTableDisplayTimeframe
                );
                for (const timeframe of timeframeDropdown.options)
                    timeframeToRow[timeframe] = [];
            });
    }

    getApiInfo();

    intervalFunction();
    // updateInterval = setInterval(() => intervalFunction(), 5000);
};

window.addEventListener("keydown", function (ev) {
    switch (ev.keyCode) {
        case 39:
            rightArrows.forEach((element) => {
                element.click();
            });
            ev.preventDefault();
            break;
        case 37:
            leftArrows.forEach((element) => {
                element.click();
            });
            ev.preventDefault();
            break;
    }
});
