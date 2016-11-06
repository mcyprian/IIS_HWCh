export default function getData(URLpath,func){
	const url = document.URL;
	const full_path = url+URLpath;
	$.getJSON(full_path,func);
}
