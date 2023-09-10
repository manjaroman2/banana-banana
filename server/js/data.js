function round(x, ndigits = 2) {
    return Math.round(x * 10 ** ndigits) / 10 ** ndigits;
}

export class Row {
    constructor(fData, timeframe) {
        this.timeframe = timeframe;
        this.name = fData["name"];
        this.performance = round(
            fData["performance"][this.timeframe]["changeInPercent"]
        );
        this.isin = fData["isin"];
        this.link = "https://www.boerse-frankfurt.de/" + fData["slug"];
        this.slug = fData["slug"];

        this.createElementDOM();
        this.sendDataToElementDOM();
    }

    createElementDOM() {
        this.tr = document.createElement("tr");
        this.nameTd = document.createElement("td");
        this.performanceTd = document.createElement("td");
        this.isinTd = document.createElement("td");
        this.linkTd = document.createElement("td");
        this.linkTd.className = "link-td";

        this.isinTd.style.userSelect = "text";
        this.linkA = document.createElement("a");
        this.linkTd.appendChild(this.linkA);

        // this.nameTd.style.maxWidth = "25%";
        this.performanceTd.style.minWidth = "5vw";
        this.performanceTd.style.textAlign = "left";
        this.isinTd.style.minWidth = "10vw";
        // this.isinTd.style.maxWidth = "25%";
        // this.linkTd.style.maxWidth = "25%";

        this.tr.append(
            this.nameTd,
            this.performanceTd,
            this.isinTd,
            this.linkTd
        );
    }
    sendDataToElementDOM() {
        this.nameTd.innerHTML = this.name;
        this.performanceTd.innerHTML = "&nbsp;" + this.performance;
        this.isinTd.innerHTML = this.isin;
        this.linkA.href = this.link;
        this.linkA.innerHTML = this.slug;
    }
}

export class TableData {
    constructor() {
        this.table = document.createElement("table");
        this.table.id = "table";
        this.tbody = document.createElement("tbody");
        this.table.append(this.tbody);
    }

    populateTimeframes(timeframes) {
        timeframes.forEach((tf) => (this[tf] = []));
    }

    addRow(row) {
        this[row.timeframe].push(row);
    }

    setTimeframe(timeframe) {
        this.tbody.innerHTML = "";
        this[timeframe].forEach((row) => {
            this.tbody.append(row.tr);
            row.sendDataToElementDOM();
        });
    }
}
