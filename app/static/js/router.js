import { keys,each } from "underscore"

export default class Router{
	constructor(){
	 	this.routes = {};
	}

	addRoute(route,func){
		this.routes[route]=func;
	}
	
	call() {
		try{
			let path_key = this.findRoute();
			this.routes[path_key]();
		}
		catch (e){
			console.log(e);
		}
	}

	findRoute(){
		const key_list = keys(this.routes);
		let ret;
		for(var i=0;i<key_list.length;i++){
			const regx = new RegExp("^"+key_list[i]+"$");
			if(!!(regx.exec(document.location.pathname))) {
				ret = key_list[i];
				break;
			} 
		}
		if(!ret)
			throw "cannot find key based on url";
		return ret;
	}
}
