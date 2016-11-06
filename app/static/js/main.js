import Router from "./router"
import { teams } from "./teams"

var r = new Router();
window.r =r

r.addRoute("/",function(){console.log("root")});
r.addRoute("/schedule",function(){console.log("schedule")});
r.addRoute("/teams",teams);
r.addRoute("/.*",function(){console.log("ALL OTHER")});

$(document).ready(r.call());
