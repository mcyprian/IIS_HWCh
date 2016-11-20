import Router from "./router"
import { teams } from "./teams"
import { login } from "./login"
import { employee_management } from "./employee_management"

var r = new Router();

r.addRoute("/teams", teams);
r.addRoute("/login", login);
r.addRoute("/employee_management", employee_management);

$(document).ready(r.call());
