import { postData } from "./data"

export function team_management() {
	$(".remove-button").click(removeMember);
}

function removeMember() {
	const member_div = $(this).parent().parent()
	let member_id = member_div.attr('id')
	const name = member_div.children('h4').text()
	member_id = member_id.substr(6) // memberID -> ID 
	if (confirm(`Are you sure you want to remove ${name} from team?`)) {
		postData(document.URL, {"rm": member_id}, (data)=>{member_div.remove()});
	}
}
