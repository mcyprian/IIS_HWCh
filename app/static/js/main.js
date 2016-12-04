import Router from "./router"
import {teams} from "./teams"
import {login} from "./login"
import {employees} from "./employees"
import {events} from "./events"
import {standings} from "./standings"
import {team_management} from "./team_management"
import {match_profile} from "./match_profile"

var r = new Router();

r.addRoute("/teams", teams);
r.addRoute("/login", login);
r.addRoute("/employees", employees);
r.addRoute("/schedule/events/.", events);
r.addRoute("/standings", standings);
r.addRoute("/match_profile/.+", match_profile);
r.addRoute("/team_management/[^/]+", team_management);

$(document).ready(r.call());
