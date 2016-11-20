import getData from "./data"
import { postData } from "./data"


export function employees() {
    initList();
}

var roles = ['employee', 'manager', 'administrator'];

function initList() {
    let buttons;
    let options = [{className: "btn-primary", action: "update" }, 
                   {className: "btn-success", action: "promote"},
                   {className: "btn-warning", action: "demote"},
                   {className: "btn-danger", action: "remove"}];
    for (let i = 0; i < options.length; i++) {
        buttons = document.getElementsByClassName(options[i].className);
        for (let j = 0; j < buttons.length; j++) {
            let empData = { login: buttons[j].id, action: options[i].action };
            buttons[j].addEventListener("click", 
                                        function() {
                                            postData("/employees/manage.json",
                                                     empData,
                                                     callback)
                                        },
                                        false);
        }
    }
}

var callback = function updatePanel(result) {
    let panel = document.getElementById(result.id);
    let head = panel.childNodes[1];
    let body = panel.childNodes[3];
    head.childNodes[1].innerHTML = result.name + ' ' + result.surname;
    head.childNodes[3].innerHTML = "login: " + result.login;
    head.childNodes[5].innerHTML = "position: " + roles[result.role];
    if (result.role  == 0) {
        body.childNodes[5].disabled = true;
        body.childNodes[5].className = "btn btn-warning disabled";
    } else if (result.role == 2) {
        body.childNodes[3].disabled = true;
        body.childNodes[3].className = "btn btn-success disabled";
    } else {
        body.childNodes[3].disabled = false;
        body.childNodes[3].className = "btn btn-success";
        body.childNodes[5].disabled = false;
        body.childNodes[5].className = "btn btn-warning";
    }
}
