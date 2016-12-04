export function match_profile() {
    $("#stats").hide();
    show();
}

function show() {
    let i = 0;
    $("button")
        .click(function() {
            $("#stats").slideToggle("slow");
            i = i + 1;
            rewrite(i);
        });
}

function rewrite(i) {

    if ((i % 2) == 1) {
        document.getElementById("show").innerHTML = "Hide events";
    } else {
        document.getElementById("show").innerHTML = "Show events";
    }
}
