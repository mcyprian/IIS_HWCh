import Router from "./router"
import { teams } from "./teams"
import { login } from "./login"
import { employees } from "./employees"
import { standings } from "./standings"
import { team_management } from "./team_management"

var r = new Router();

r.addRoute("/teams", teams);
r.addRoute("/login", login);
r.addRoute("/employees", employees);
r.addRoute("/standings", standings);
r.addRoute("/team_management/[^/]+", team_management);

$(document).ready(r.call());
