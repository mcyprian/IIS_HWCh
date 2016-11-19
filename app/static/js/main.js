import Router from "./router"
import { teams } from "./teams"
import { login  } from "./login"
import { standings  } from "./standings"

var r = new Router();

r.addRoute("/teams",teams);
r.addRoute("/login",login);
r.addRoute("/standings",standings);

$(document).ready(r.call());
