const lightdarkbutton = document.querySelectorAll('[id=lightdarkbutton]');
const lightdarktext = document.querySelectorAll('[id=lightdarktext]');

lightdarkbutton.forEach(function (elem) {
    elem.addEventListener('input', switchLightDark);
});

document.addEventListener("DOMContentLoaded", function () {
    initLightDark();
});

window.addEventListener('pageshow', (event) => {
    if (event.persisted) {
        console.log("window event thing");
        initLightDark();
    }
});

function initLightDark() {
    console.log("init mode:" + localStorage.getItem('isDarkmode'))
    if (localStorage.getItem('isDarkmode') == "dark") {
        toggleDark();
    } else {
        toggleLight();
    }
}

function switchLightDark(e) {
    if (!e.target.checked == "") {
        toggleDark();
    } else {
        toggleLight();
    }
}

function toggleLight() {
    lightdarkbutton.forEach(function (elem) {
        elem.checked = false;
    });
    // document.documentElement.setAttribute("class", "bg-afc-gold");
    document.body.style.backgroundColor = "#9C824A";
    lightdarktext.forEach(function (elem) {
        elem.classList.remove("text-afc-gold");
        elem.classList.add("text-afc-blue");
    });
    localStorage.setItem('isDarkmode', 'light');
    console.log(localStorage.getItem('isDarkmode'));
}

function toggleDark() {
    lightdarkbutton.forEach(function (elem) {
        elem.checked = true;
    });
    // document.documentElement.setAttribute("class", "bg-afc-blue");
    document.body.style.backgroundColor = "#063672";
    lightdarktext.forEach(function (elem) {
        elem.classList.remove("text-afc-blue");
        elem.classList.add("text-afc-gold");
    });
    localStorage.setItem('isDarkmode', 'dark');
    console.log(localStorage.getItem('isDarkmode'));
}
