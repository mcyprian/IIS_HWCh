import Router from "./router"
import { teams } from "./teams"

var r = new Router();

r.addRoute("/teams",teams);

$(document).ready(r.call());
