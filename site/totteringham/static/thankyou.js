const lightdarkbutton = document.querySelectorAll('[id=lightdarkbutton]');

var audio = new Audio('static/wdwtot.mp3');

lightdarkbutton.forEach(function (elem) {
    elem.addEventListener('input', enableJWMode);
});

function enableJWMode(e) {
    // if (!e.target.checked == "") {
        if (audio.paused) {
            audio.play();
        }
        else {
            audio.pause();
        }
    // }
}

function play() {
    audio.play();
}

function pause() {
    audio.pause();
}