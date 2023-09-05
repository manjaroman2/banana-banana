function choose(choices) {
    var index = Math.floor(Math.random() * choices.length);
    return choices[index];
}

export class DropdownMenu {
    constructor(name) {
        this.name = name;
        this.value = undefined;
    }

    createDOM(parent) {
        this.btnText = this.name + ": ";
        this.div = document.createElement("div");
        this.div.className = "dropdown";
        this.btn = document.createElement("button");
        this.btn.className = "dropbtn";
        this.btn.innerHTML = this.btnText;
        this.divContent = document.createElement("div");
        this.divContent.className = "dropdown-content";

        this.div.append(this.divContent);
        this.div.append(this.btn);

        parent.appendChild(this.div);
    }

    setOptions(options, onClickCallback) {
        this.options = options 
        const maxWidth = Math.max(...(options.map((i) => new String(i)).map(el => el.length)));
        this.width = (this.btnText.length + maxWidth) * 15 + "px"; 
        this.div.style.width = this.width;
        this.btn.style.width = this.width;
        for (const e of this.divContent.childNodes) { 
            e.style.width = width;
        }
        this.setValue(choose(options));

        this.resetContentDOM();
        this.options.forEach((opt) =>
            this.addToDropdownContentDOM(
                opt,
                onClickCallback
            )
        );
    }

    resetContentDOM() {
        this.divContent.innerHTML = "";
    }

    setValue(value) {
        this.value = value;
        this.btn.innerHTML = this.btnText + value;
    }

    addToDropdownContentDOM(value, onClickCallback) {
        let span = document.createElement("span");
        span.innerHTML = value;
        span.style.width = this.width;
        span.onclick = () => {
            this.setValue(value);
            onClickCallback();
        };
        this.divContent.append(span);
    }
}

