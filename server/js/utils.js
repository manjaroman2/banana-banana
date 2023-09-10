export const fibonacci = (limit, a = 1, b = 1) =>
    a > limit
        ? [] // #1
        : [a, ...fibonacci(limit, b, a + b)];

export function clearArray(a) {
    // WHY IS THIS NOT IMPLEMENTED BY DEFAULT???
    while (a.length > 0) {
        a.pop();
    }
}

export function choose(choices) {
    var index = Math.floor(Math.random() * choices.length);
    return choices[index];
}


export class Timer {
    constructor(timeout) {
        var self = this;
        this.interval = timeout ? timeout : 1000; // Default
        this.running = undefined;
        this.counter = 0;

        this.run = function (runnable) {
            this.running = setInterval(function () {
                self.counter = self.counter + 1;
                runnable(self);
            }, this.interval);
        };

        this.stop = function () {
            if (this.running != undefined) clearInterval(this.running);
            this.counter = 0;
        };
    }
}