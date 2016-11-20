import Router from "./router"
import { teams } from "./teams"
import { login } from "./login"
import { employees } from "./employees"
import { standings } from "./standings"

var r = new Router();

r.addRoute("/teams", teams);
r.addRoute("/login", login);
r.addRoute("/employees", employees);
r.addRoute("/standings", standings);

$(document).ready(r.call());
