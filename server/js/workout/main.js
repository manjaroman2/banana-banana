var width;
var height;
var windowHeight;
var windowWidth;
var ytIframe;
var timerIframe;
var mute = false;
var spotifyIframe;
const aspectRatio = 16 / 9;
const inverseAspectRatio = 1 / aspectRatio;
const maxVideoHeightRatio = 1 / 2;

function onLoad() {
    // var yt = document.createElement("iframe");

    // yt.src = "https://www.youtube.com/watch?v=67c-Z2wOXhc"

    // document.body.insertAdjacentHTML(
    //     "afterbegin",
    //     `
    // "<iframe width="100%" height="" src="https://www.youtube.com/embed/67c-Z2wOXhc" title="60 Min. Ganzkörper Workout mit Kurzhanteln für Zuhause | Sascha Huber" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>"`
    // );
    updateWidthHeight();
    document.body.insertAdjacentHTML(
        "afterbegin",
        `
        <iframe id="yt-iframe" width="${width}px" height="${height}px" src="https://www.youtube.com/embed/67c-Z2wOXhc?si=9I7vCJgtEQKEe3EG&amp;start=127&amp;mute=1" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
        <iframe id="timer-iframe" src="https://martinkoban.com/interval-timer/?m1=00&amp;s1=40&amp;m2=00&amp;s2=20&d=60&amp;dt=rounds&amp;wu=5&amp;wut=seconds&amp;nm=0&amp;iframe=1&amp;p1n=Phase%201&amp;p2n=Phase%202&amp;volume=1" style="border:none;" title="Interval Timer by MartinKoban.com" scrolling="auto" allowtransparency="true"></iframe>
        `
    );
    //  width="${width}px" height="${windowHeight-height}px"
    ytIframe = document.getElementById("yt-iframe");
    timerIframe = document.getElementById("timer-iframe");

    timerIframe.style.top = "50px";
    timerIframe.style.right = "50px";
    timerIframe.width = "300vw";
    timerIframe.height = "600vh";
    timerIframe.style.opacity = "0.7";

    // timerIframe.addEventListener("load", function (ev) {
    //     var innerDoc = timerIframe.contentDocument || timerIframe.contentWindow.document;
    //     var a = innerDoc.querySelector("#cc-window > div.cc-compliance.cc-highlight > a.cc-btn.cc-allow.cc-btn-no-href")
    //     a.click();
    // })
}

function updateWidthHeight() {
    windowHeight = window.innerHeight;
    windowWidth = window.innerWidth;
    width = window.innerWidth;
    height = Math.floor(inverseAspectRatio * width);
    // if (height > windowHeight * maxVideoHeightRatio) {
    //     height = Math.floor(windowHeight * maxVideoHeightRatio);
    //     width = Math.floor(aspectRatio*height)
    // }
}

function onResize(ev) {
    updateWidthHeight();
    ytIframe.width = width;
    ytIframe.height = height;
    // timerIframe.width = width;
    // timerIframe.height = windowHeight-height;
}

function onKeydown(ev) {
    switch (ev.keyCode) {
        case 77:
            mute = !mute;
            console.log(mute);
            if (mute)
                timerIframe.contentWindow.postMessage(
                    '{"method":"setVolume", "value":0}',
                    "*"
                );
            else
                timerIframe.contentWindow.postMessage(
                    '{"method":"setVolume", "value":100}',
                    "*"
                );
            break;
    }
}

window.addEventListener("load", onLoad);
window.addEventListener("resize", onResize);
window.addEventListener("keydown", onKeydown);
