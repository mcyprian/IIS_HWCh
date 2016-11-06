import getData from "./data"
import { keys,values } from "underscore"

export function createTeamList(data){
	console.log("creating TEAM LIST");
	window.data = data;
	console.log(data);
	let team;
	for(let i=0;i<data.length;i++) {
		team = `<a href="#/" class="list-group-item team-in-list" id="${i}">${data[i]}</a><div id="teamId${i}"><p>Team Data</p></div>`;
		$(".list-group").append(team);
	}
	toggleTeamInfo();
}	

function toggleTeamInfo(){
	console.log("TOGGLE!!!!");
	$(".team-in-list").click(function(){
		var id = $(this).attr("id");
		console.log("clicked on " + id);
		$("#teamId"+id).slideToggle("slow");
	});
};

export function teams(){
	getData("/list.json",createTeamList);
}
