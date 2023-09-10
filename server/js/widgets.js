import { Timer, choose } from "./utils.js";

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
        this.options = options;
        const maxWidth = Math.max(...options.map((i) => new String(i)).map((el) => el.length));
        this.width = (this.btnText.length + maxWidth) * 15 + "px";
        this.div.style.width = this.width;
        this.btn.style.width = this.width;
        for (const e of this.divContent.childNodes) {
            e.style.width = width;
        }
        this.setValue(choose(options));

        this.resetContentDOM();
        this.options.forEach((opt) => this.addToDropdownContentDOM(opt, onClickCallback));
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

export class Topbar {
    constructor(rankEnumCallbacks, commonCallback) {
        this.commonCallback = commonCallback;
        this.rankEnumCallbacks = rankEnumCallbacks;
        this.rankEnum = Object.keys(rankEnumCallbacks);
        this.rankEnumLongest = Math.max(...this.rankEnum.map((el) => el.length));

        this.div = document.createElement("div");
        this.div.className = "topbar";
        let sortDiv = document.createElement("div");
        sortDiv.className = "sortDiv";

        this.arrowLeft = document.createElement("i");
        this.arrowLeft.className = "arrow left";
        this.arrowRight = document.createElement("i");
        this.arrowRight.className = "arrow right";
        this.arrowLeft.onclick = () => this.updateIdx((this.rankEnumIdx - 1 + this.rankEnum.length) % this.rankEnum.length);
        this.arrowRight.onclick = () => this.updateIdx((this.rankEnumIdx + 1) % this.rankEnum.length);

        this.rankSpan = document.createElement("span");
        this.rankSpan.className = "rank";
        this.rankSpan.style.width = this.rankEnumLongest * 4 + "vw";

        sortDiv.append(this.arrowLeft, this.rankSpan, this.arrowRight);

        this.div.append(sortDiv);
    }

    updateIdx(idx) {
        this.rankSpan.style.transform = "scale(0.95)";
        setTimeout(() => {
            this.rankSpan.style.transform = "scale(1.0)";
        }, 100);
        this.rankEnumIdx = idx;
        this.rankSpan.innerHTML = this.rankEnum[this.rankEnumIdx];
        this.rankEnumCallbacks[this.rankEnum[this.rankEnumIdx]]();

        this.commonCallback();
    }

    onLoad(parent) {
        parent.append(this.div);
    }
}

export class TableScroll {
    constructor() {
        this.outerDiv = document.createElement("div");
        this.outerDiv.className = "outer";
        this.scrollUp = document.createElement("div");
        this.scrollUp.className = "scrollUp";
        this.scrollDown = document.createElement("div");
        this.scrollDown.className = "scrollDown";

        console.log(this.outerDiv, this.scrollUp, this.scrollDown);
        this.outerDiv.append(this.scrollUp, this.scrollDown);
    }

    updateScrollHeight() {
        this.scrollHeight = this.scrollUp.getBoundingClientRect().height;
    }

    onLoad(parent) {
        parent.append(this.outerDiv);
        this.updateScrollHeight();

        new ResizeObserver(() => {
            const rect = this.outerDiv.getBoundingClientRect();
            const width = rect.width;
            const y = rect.y;
            const height = window.innerHeight - this.outerDiv.getBoundingClientRect().height;

            this.scrollUp.style.top = y + "px";
            this.scrollUp.style.width = width + "px";
            this.scrollDown.style.bottom = height + "px";
            this.scrollDown.style.width = width + "px";

            this.updateScrollHeight();
        }).observe(this.outerDiv);

        // function animation(scale, shift) {
        //     return (t) =>
        //         Math.exp(t / scale + shift) / (1 + Math.exp(t / scale + shift));
        // }

        function animation(a, b, c) {
            return (t) => (t + b) / (c + (t + b) / a);
        }

        const x = animation(1, 0, 10);
        const scrollUpAnimation = animation(-this.scrollHeight, -this.scrollHeight, 1);
        const scrollDownAnimation = animation(this.scrollHeight, 0, 1);

        const scrollUpTimer = new Timer(10);
        var scale = 100;
        this.scrollUp.addEventListener("mouseenter", (ev) => {
            scrollUpTimer.run((timer) => {
                const d = scale * x(timer.counter);
                this.outerDiv.scrollBy(0, d);
            });
        });
        this.scrollUp.addEventListener("mousemove", (ev) => {
            scale = scrollUpAnimation(ev.layerY);
        });

        this.scrollUp.addEventListener("mouseleave", () => {
            scrollUpTimer.stop();
        });
        const scrollDownTimer = new Timer(10);
        this.scrollDown.addEventListener("mouseenter", () => {
            scrollDownTimer.run((timer) => {
                const d = scale * x(timer.counter);
                this.outerDiv.scrollBy(0, d);
            });
        });
        this.scrollDown.addEventListener("mousemove", (ev) => {
            scale = scrollDownAnimation(ev.layerY);
        });
        this.scrollDown.addEventListener("mouseleave", () => scrollDownTimer.stop());
    }
}
