import Router from "./router"
import { teams } from "./teams"
import { login  } from "./login"

var r = new Router();

r.addRoute("/teams",teams);
r.addRoute("/login",login);

$(document).ready(r.call());
