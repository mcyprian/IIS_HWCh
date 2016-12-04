import { postData } from "./data"

export function events() {
    let buttons; buttons = document.getElementsByClassName("remove");
    for (let j = 0; j < buttons.length; j++) {
        let evData = {id : buttons[j].id};
        buttons[j].addEventListener("click", function() {
            rmConfirm("/schedule/events/delete.json", evData, callback)
        }, false);
    }
}

function rmConfirm(url, data, callback) {
    if (confirm("Are you sure you want to remove event " + data.id + "?")) {
        postData(url, data, callback);
    }
}

var callback = function updatePanel(result) {
    if (result.status == "failure") {
        alert("Failed to remove event " + result.id + ".");
    } else {let panel = document.getElementById(result.id); panel.remove();}
}
