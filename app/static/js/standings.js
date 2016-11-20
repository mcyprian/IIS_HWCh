import { sortBy } from "underscore"
import getData from "./data"

var STANDINGS_DATA
var POSITION_TOGGLE = false;

export function standings() {
	showTable();
	$("#filter-select1").change( () => {
		POSITION_TOGGLE = false;
		showTable()
	});
	$('#range input').change( () => {
		POSITION_TOGGLE = false;
		showTable()
	});
}

function showTable() {
	if( $("#filter-select1").val() !== "ChooseFilter")
	{
		if (STANDINGS_DATA === undefined) {
			getData("/data.json", data => {
				createStandingTable(data) 
			});
		}
		else {
			createStandingTable(STANDINGS_DATA);
		}
	}
}

function but() {
	const button = document.getElementById("button-filter");
	button.addEventListener("click", forwardData, false);
	console.log("registered");
}

function forwardData() {
	console.log("getting data");
	getData("/list.json", filterData);
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
	STANDINGS_DATA = data
	window.data = STANDINGS_DATA;
	const filterString = $("#filter-select1").val().toLowerCase()
	STANDINGS_DATA = sortBy(STANDINGS_DATA, 'name').reverse()
	STANDINGS_DATA = sortBy(STANDINGS_DATA, filterString).reverse()
	$("#table-wrap").html(finalTable())
	$("#pos-toggle").click( () => {
		POSITION_TOGGLE = !POSITION_TOGGLE;
		showTable()
	});
}

function fillAdditionalOpt() {
	const option = $("#filter-select1").val()
	return `<th>${option}</th>`;
}

function fillTableData(range) {
	let result = ""
	if (range=="ALL")
		range = STANDINGS_DATA.length
	if (range > STANDINGS_DATA.length)
		range = STANDINGS_DATA.length
	if(!POSITION_TOGGLE) {
		for(let i=0; i<range; i++) {
			result += wrapPlayerData(i+1, STANDINGS_DATA[i])
		}
	}
	else {
		for(let i=range-1; i>=0; i--) {
			result += wrapPlayerData(i+1, STANDINGS_DATA[i])
		}
	}
	return result
}

function wrapPlayerData(pos, player_data) {
	const filter_select =  $("#filter-select1").val().toLowerCase()
	return `<tr>
	<td>${pos}</td>
	<td>${player_data.name}</td>
	<td>${player_data.team}</td>
	<td>${player_data.position}</td>
	<td>${player_data[filter_select]}</td>
	<tr>`
}

function getRange() {
	let	range_value = $('input[name=range]:checked', '#range').val(); 
	return range_value;
}

function finalTable() {
	let additional_option = fillAdditionalOpt();
	let table_data = fillTableData(getRange());
	let position_icon = "glyphicon-sort-by-order";
	if(POSITION_TOGGLE)
		position_icon = "glyphicon-sort-by-order-alt";
	let table_core = 
	`<table class="table">
		<thead>
			<tr>
				<th><button id="pos-toggle"><span class="glyphicon ${position_icon}"></span> Pos</button></th>
				<th>Name</th>
				<th>Team</th>
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
