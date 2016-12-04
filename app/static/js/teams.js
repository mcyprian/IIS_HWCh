import getData from "./data"
import { keys } from "underscore"

export function teams() {
	getData("/list.json", createTeamList);
}

function createTeamList(data) {
	const teams = keys(data);
	let html_result;
	let flagUrl;
	let team_body =  "";
	for (let i = 0; i < teams.length; i++) {
		let country_name = teams[i];
		flagUrl = getCountryFlag(getCountryCode(country_name));
		team_body = createTeamBody(data[country_name], country_name);

		html_result = `<div class="panel panel-primary">
		<div class="panel-heading team-in-list" id="${i}">
				<img class="team-logo-heading" src="${flagUrl}">
				<b>${country_name}</b>
				<small> (Click for more)</small>
		</div>
		<div class="panel-body">
			<div id="teamId${i}">
				${team_body}
			</div>
		</div>
		</div>`;
		$(".list-group").append(html_result);
	}
	toggleTeamInfo();
}	

function createTeamBody(country_data, country_name) {
	const county_header = getCountryHeader(country_name);
	const mvp_player = createPersonDiv(country_data, "mvp");
	const coach = createPersonDiv(country_data, "coach");
	return `
	<div class="team-header-link">
		<h3>${county_header} National Hockey Team</h3>
		<a href="/teams/${country_name}" class="btn btn-info" role="button">Team Details</a>
	</div>
	<hr>
	<div class="row">
		${mvp_player}
		${coach}
	</div>`;
}

function createPersonDiv (country_data, position) {
	const mvp_or_coach = (position === "mvp" ? "The Most Valuable Player": "Coach");
	const name = (position === "mvp" ? country_data.mvp.full_name : country_data.coach.full_name);
	let link = "";
	let points = "";

	if (position === "mvp")
	{
		link = `<a href="players/${country_data.mvp.id}" class="btn btn-primary" role="button">View profile</a>`;
		points = `<p>Points:${country_data.mvp.points}</p>`;
	}
	return `
	<div class="col-md-6">
		<h3>${mvp_or_coach}</h3>
		<div class="thumbnail">
			<div class="caption">
				<div class="row">
					<div class="col-md-6 person-text">
						<h3>${name}</h3>
						${points}
						${link}
					</div>
					<div class="col-md-6 person-avatar">
						<img src="https://mcyprian.fedorapeople.org/avatar.png" class="avatar-img">
					</div>
				</div>
			</div>
		</div>
	</div>`;
}

function toggleTeamInfo() {
	$(".team-in-list").click(function() {
		var id = $(this).attr("id");
		$("#teamId" + id).slideToggle("slow");
	});
}

function getCountryHeader(country) {
	const flags = {
		Canada: "Canada",
		Slovakia: "Slovak Republic",
		Finland: "Republic of Finland",
		USA: "United States of America",
		Germany: "Federal Republic of Germany",
		Czech: "Czech Republic",
		Russia: "Russia Federation",
		Sweden: "Kingdom Of Sweden"
	};

	const key_flags = keys(flags);

	for (let i = 0; i < key_flags.length; i++) {
		if (country.indexOf(key_flags[i]) !== -1)
			return flags[key_flags[i]];
	}
}

function getCountryCode(country) {
	const flags = {
		Canada: "CAN",
		Slovakia: "SVK",
		Finland: "FIN",
		USA: "USA",
		Germany: "GER",
		Czech: "CZE",
		Russia: "RUS",
		Sweden: "SWE"
	};
	const key_flags = keys(flags);

	for(let i = 0; i < key_flags.length; i++) {
		if (country.indexOf(key_flags[i]) !== -1)
			return flags[key_flags[i]];
	}
}

function getCountryFlag(country_code) {
	return "https://mcyprian.fedorapeople.org/flags/" + country_code
}
