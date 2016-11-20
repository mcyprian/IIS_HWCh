export default function getData(URLpath,func){
	const url = document.URL;
	const full_path = url+URLpath;
	$.getJSON(full_path,func);
}

export function postData(url, data, success) {
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: url,
        data: JSON.stringify(data),
        success: success
    })
}
