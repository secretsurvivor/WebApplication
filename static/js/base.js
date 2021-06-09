var active = false;
function login_frame_hide() {
    if (active) {
        $("#login_frame").hide()
        $("#login_document_background").hide();
        active = !active;
    }
}
function login_frame_show() {
    var loginFrame = $("#login_frame");
    var loginBackground = $("#login_document_background");
    if (active) {
        loginFrame.hide();
        loginBackground.hide();
    } else {
        loginFrame.show();
        loginBackground.show();
    }
    active = !active;
}

function update_current_user() {
    $.getJSON($SCRIPT_ROOT + "/dev/account", {}, function(data){
        if (data.account_id){
            $("#login_button").text("Account")
            $(".component_menu-button").show()
        } else {
            $("#login_button").text("Login")
            $(".component_menu-button").hide()
        }
    })
}

