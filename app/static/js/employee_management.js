import getData from "./data"

export function employee_management() {
    getData("/list.json", createList);
}

function createList(data) {
    let entry;
    for (let i = 0; i < data.length; i++) {
        let role = data[i].role ? "manager" : "employee";
        entry = `<div class="panel panel-primary">
            <div class="panel-heading employee-list" id="${i}">
                <span class="emp-name">${data[i].name} ${data[i].surname}</span>
                <span class="emp-data">login: ${data[i].login}</span>
                <span class="emp-data">position: ${role}</span>
            </div>
            <div class="panel-body"
                <div id="employeeId${i}">
                <button type="button" class="btn-primary">Update data</button>
                <button type="button" class="btn-success">Promote</button>
                <button type="button" class="btn-danger">Remove</button>
                </div>
            </div>
            </div>`
            $(".list-group").append(entry);
    }
}

