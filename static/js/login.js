var currentlySelected
function loginInit() {
    currentlySelected = document.getElementById("login_tab");
    currentlySelected.classList.add("tab_selected");
}
function updateContent() {
    var loginContent = document.getElementById("login_content");
    var registerContent = document.getElementById("register_content");
    if (currentlySelected.id === "login_tab") {
        registerContent.style.display = "none"
        loginContent.style.display = "";
    } else {
        loginContent.style.display = "none";
        registerContent.style.display = "";
    }
}
function selectTab(element) {
    currentlySelected.classList.remove("tab_selected");
    element.classList.add("tab_selected");
    currentlySelected = element;
    updateContent();
}

function loginCall() {

}
function registerCall() {

}