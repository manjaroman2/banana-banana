var updateInterval = undefined;
var sortElem = undefined;
var sortEnum = ["best", "worst"];
var sortEnumLongest = Math.max(...sortEnum.map((el) => el.length));
var sortEnumIdx = 0;
var rightArrows = undefined;
var leftArrows = undefined;
var topbar = undefined;
var tableEntriesToDisplay = 0;
var tableTimeframeDisplay = "years1";
var tableData = [];

function round(x, ndigits = 2) {
    return Math.round(x * 10 ** ndigits) / 10 ** ndigits;
}

class DropdownMenu {
    constructor(name) {
        this.name = name;
    }

    createDOM(parent) {
        this.btnText = this.name + ": ";
        let div = document.createElement("div");
        div.className = "dropdown";
        this.btn = document.createElement("button");
        this.btn.className = "dropbtn";
        this.btn.innerHTML = this.btnText;
        this.divContent = document.createElement("div");
        this.divContent.className = "dropdown-content";

        div.append(this.divContent);
        div.append(this.btn);

        parent.appendChild(div);
    }

    resetContentDOM() {
        this.divContent.innerHTML = "";
    }

    addToDropdownContentDOM(text, onclick) {
        let span = document.createElement("span");
        span.innerHTML = text;
        span.onclick = () => {
            this.btn.innerHTML = this.btnText + text;
            onclick();
        };
        this.divContent.append(span);
    }
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

function getApi(callback, sort = "best", number = 10) {
    fetch(
        "/api?" +
            new URLSearchParams({
                s: sort,
                n: number,
            })
    )
        .then((response) => response.json())
        .then((data) => callback(data));
}

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

function addRowToTable(fData, timespan) {
    // console.log(fData);
    // console.log(timespan);
    let name = fData["name"];
    let performance = round(fData["performance"][timespan]["changeInPercent"]);
    let isin = fData["isin"];
    let link = 'https://www.boerse-frankfurt.de/etf/' + fData["slug"];
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
    linkA.innerHTML = link;
    linkTd.appendChild(linkA);
    linkTd.style.width = "100px";

    tr.append(nameTd, performanceTd, isinTd, linkTd);
    tbody.append(tr);
}

function updateTableDisplayEntries() {
    let allRows = tbody.childNodes;
    console.log(tableEntriesToDisplay);
    for (let i = 0; i < tableEntriesToDisplay; i++) {
        const element = allRows[i];
        element.className = "visible";
    }
    for (let i = tableEntriesToDisplay; i < allRows.length; i++) {
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

function updateTableDisplayTimeframe(jsonResponse) {
    tbody.innerHTML = "";
    jsonResponse.sort((a, b) => {
        cipA = a["performance"][tableTimeframeDisplay]["changeInPercent"];
        cipB = b["performance"][tableTimeframeDisplay]["changeInPercent"];
        return cipA - cipB;
    });
    jsonResponse.reverse();
    jsonResponse.forEach((e) =>
        addRowToTable(e, tableTimeframeDisplay)
    );
}
function reverseChildren(parent) {
    for (var i = 1; i < parent.childNodes.length; i++){
        parent.insertBefore(parent.childNodes[i], parent.firstChild);
    }
}

function updateTableSort() {
    reverseChildren(tbody);
}


window.onload = () => {
    document.body.append(createTopbar());
    document.body.append(table);
    // Bodybuilding done here

    sortElem = document.getElementById("sort");
    sortElem.innerHTML = sortEnum[sortEnumIdx];
    sortElem.style.width = sortEnumLongest * 4 + "vw";
    addFunctionalityToArrows();

    let numberDropdown = new DropdownMenu("Number");
    numberDropdown.createDOM(topbar);

    let timeframeDropdown = new DropdownMenu("Timeframe");
    timeframeDropdown.createDOM(topbar);

    if (updateInterval != undefined) clearInterval(updateInterval);
    function intervalFunction() {
        getApi((jsonResponse) => {
            if (jsonResponse.hasOwnProperty("error"))
                console.error(jsonResponse);
            else if (jsonResponse.length == 0) console.info("no data");
            else {
                console.log(jsonResponse.length);

                // Populate number dropdown
                numberDropdown.resetContentDOM();
                let numberOptions = fibs(
                    Math.floor(jsonResponse.length / 10)
                ).map((x) => 10 * x); // I love this
                console.log("number options: ", numberOptions);
                for (let i = 1; i < numberOptions.length; i++) {
                    const number = numberOptions[i];
                    if (jsonResponse.length > number)
                        numberDropdown.addToDropdownContentDOM(number, () => {
                            tableEntriesToDisplay = number;
                            updateTableDisplayEntries();
                        });
                    else break;
                }
                numberDropdown.addToDropdownContentDOM("All", () => {
                    tableEntriesToDisplay = jsonResponse.length;
                    updateTableDisplayEntries();
                });
                if (tableEntriesToDisplay == 0) tableEntriesToDisplay = jsonResponse.length;

                // Populate timeframe dropdown
                timeframeDropdown.resetContentDOM();
                let timeframeOptions = Object.keys(
                    jsonResponse[0]["performance"]
                );
                timeframeOptions.forEach((timeframe) => {
                    timeframeDropdown.addToDropdownContentDOM(
                        timeframe,
                        () => {
                            tableTimeframeDisplay = timeframe;
                            updateTableDisplayTimeframe(jsonResponse);
                        }
                    );
                });

                updateTableDisplayTimeframe(jsonResponse);
                updateTableDisplayEntries();
            }
        });
    }
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
