import getData from "./data"
import { keys,values } from "underscore"

export function teams(){
	getData("/list.json",createTeamList);
}

function createTeamList(data){
	let team;
	for(let i=0;i<data.length;i++) {
		team = `<div class="panel panel-primary">
		<div class="panel-heading team-in-list" id="${i}">
				<img class="team-logo-heading" src="http://emojipedia-us.s3.amazonaws.com/cache/8a/62/8a620e7379c29b55d5af4bdda77c6141.png">
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
