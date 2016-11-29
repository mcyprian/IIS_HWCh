import { postData } from "./data"


export function employees() {
    initList();
}

var roles = ['employee', 'manager', 'administrator'];

function initList() {
    let buttons;
    let options = ["update", "promote", "demote", "remove"];
    for (let i = 0; i < options.length; i++) {
        buttons = document.getElementsByClassName(options[i]);
        for (let j = 0; j < buttons.length; j++) {
            let empData = { login: buttons[j].id, action: options[i] };
            if (options[i] == "update") {
                buttons[j].addEventListener("click",
                                            function() {
                                                updateRedirect(buttons[j].id)
                                            },
                                            false);
            } else {
            buttons[j].addEventListener("click", 
                                        function() {
                                            rmConfirm("/employees/manage.json",
                                                      empData,
                                                      callback)
                                        },
                                        false);
            }
        }
    }
}

function updateRedirect(login) {
    window.location="/employees/update/" + login;
}

function rmConfirm(url, data, callback) {
    if (data.action == 'remove') {
        if (confirm("Are you sure you want to remove account of " + data.login + "?")) {
            postData(url, data, callback);
        }
    } else {
        postData(url, data, callback);
    }
}

var callback = function updatePanel(result) {
    let panel = document.getElementById(result.id);
    let head = panel.childNodes[1];
    let body = panel.childNodes[3];
    if (result.action == "promote" || result.action == "demote") {
        head.childNodes[1].innerHTML = result.name + ' ' + result.surname;
        head.childNodes[3].innerHTML = "login: " + result.login;
        head.childNodes[5].innerHTML = "position: " + roles[result.role];
        if (result.role  == 0) {
            body.childNodes[5].disabled = true;
            body.childNodes[5].className = "btn btn-warning demote disabled";
        } else if (result.role == 2) {
            body.childNodes[3].disabled = true;
            body.childNodes[3].className = "btn btn-success promote disabled";
        } else {
            body.childNodes[3].disabled = false;
            body.childNodes[3].className = "btn btn-success promote";
            body.childNodes[5].disabled = false;
            body.childNodes[5].className = "btn btn-warning demote";
        }
    } else if (result.action == "remove") {
        panel.remove();
    }
}
