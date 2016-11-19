import getData from "./data"
import { keys } from "underscore"

export function teams(){
	getData("/list.json",createTeamList);
}

function createTeamList(data){
	let team;
	for(let i=0;i<data.length;i++) {
		let flagUrl = getFlag(data[i]);
		team = `<div class="panel panel-primary">
		<div class="panel-heading team-in-list" id="${i}">
				<img class="team-logo-heading" src="${flagUrl}">
				${data[i]}
		</div>
		<div class="panel-body"
			<div id="teamId${i}">
				<p>Team Data</p>
			</div>
		</div>
		</div>`;
		$(".list-group").append(team);
	}
	toggleTeamInfo();
}	

function toggleTeamInfo(){
	$(".team-in-list").click(function(){
		var id = $(this).attr("id");
		$("#teamId"+id).slideToggle("slow");
	});
}

function getFlag(country) {
	const flags = {
		Canada: "https://mcyprian.fedorapeople.org/flags/CAN",
		Slovakia: "https://mcyprian.fedorapeople.org/flags/SVK",
		Finland: "https://mcyprian.fedorapeople.org/flags/FIN",
		USA: "https://mcyprian.fedorapeople.org/flags/USA",
		Germany: "https://mcyprian.fedorapeople.org/flags/GER",
		Czech: "https://mcyprian.fedorapeople.org/flags/CZE",
		Russia: "https://mcyprian.fedorapeople.org/flags/RUS",
		Sweden: "https://mcyprian.fedorapeople.org/flags/SWE"
	};
	const key_flags = keys(flags);

	for(let i=0;i<key_flags.length;i++){
		if(country.indexOf(key_flags[i])!== -1)
			return flags[key_flags[i]];
	}
}
