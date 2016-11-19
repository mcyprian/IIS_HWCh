import getData from "./data"

var standings_data

export function standings() {
	console.log("standings");
}

function but() {
	const button = document.getElementById("button-filter");
	button.addEventListener("click", forwardData, false);
	console.log("registered");
}

function forwardData() {
	console.log("getting data");
	getData("/list.json",filterData);
}

function filterData(data) {
	const filterString = $("#text-filter").val();
	if (filterString) {
		data = data.filter((value)=>{
			if(value.indexOf(filterString)!== -1)
				return value;
		});
		$("#result-div").append(data);
	}
}

function createStandingTable(data) {
	let standings_data = data
	console.log(`standings_DATA: ${standings_data}`)
	$("#table-wrap").html(finalTable())
}

function fillAdditionalOpt() {
	const option = $("#filter-select1").val()
	return `<th>${option}</th>`;
}

function fillTableData() {
	return ""
}

function finalTable() {
	let additional_option = fillAdditionalOpt();
	let table_data = fillTableData();
	let table_core = 
	`<table class="table">
		<thead>
			<tr>
				<th><span class="glyphicon glyphicon-sort-by-order"></span> Pos</th>
				<th>Name</th>
				<th> 
					<select>
						<option value="">SVK</option>
					</select>
				</th>
				<th>Position</th>
				${additional_option}
			</tr>
		</thead>
		<tbody>
			<tr>
				${table_data}
			</tr>
		</tbody>
	</table>`;
	return table_core;
}

// self executable
$(function() {
	$("#filter-select1").change(function() {
		if( $("#filter-select1").val() !== "ChooseFilter")
		{
			if (standings_data === undefined) {
				getData("/list.json", data => { // TODO repl URL
					createStandingTable(data) 
				});
				console.log("downloading data");
			}
			else {
				console.log("data are here dont have to donwload them");
				createStandingTable(standings_data);
			}
		}
	});
});
