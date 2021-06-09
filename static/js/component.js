function open_claim_branch(claimID) {
    window.open(`/claim/${claimID}#head`, "_self");
}
function open_topic_branch(topicID) {
    window.open(`/topic/${topicID}`, "_self");
}
function branch_back() {}

function html_list_element(name, onclick) {
    return `<div onclick="${onclick}">${name}</div>`
}
var _left, _top;
$(document).on("mousemove", function(event) {
    _left = event.pageX;
    _top = event.pageY;
})
var g_component = null;
var g_info = null;
var active = false;
function open_menu(component, info){
    $.getJSON($SCRIPT_ROOT + "/dev/account", {}, function(data) {
        let menu = $("#component_menu");
        let access = (data.account_id == info.account_id) || data.admin > 0;
        switch (info.type) {
            case "reply":
                menu.html(
                    html_list_element("Reply", `component_reply()`) +
                    (access ? html_list_element("Edit", `component_edit_reply()`) : "") +
                    (access ? html_list_element("Delete", `component_delete_reply()`) : "")
                );
                break;
            case "claim_topic":
                $(component).hide()
                return
            case "related_claim":
                $(component).hide()
                return
            case "claim":
                menu.html(
                    html_list_element("Reply", `component_claim_reply()`) +
                    (access ? html_list_element("Edit", `component_edit_claim()`) : "") +
                    (access ? html_list_element("Delete", `component_delete_claim()`) : "")
                );
                break;
            case "topic":
                menu.html(
                    html_list_element("Add Claim", `component_add_claim()`) +
                    (access ? html_list_element("Edit", `component_edit_topic()`) : "") +
                    (access ? html_list_element("Delete", `component_delete_topic()`) : "")
                );
                break;
            case "all_topic":
                if (!access) {
                    $(component).hide()
                    return
                }
                menu.html(
                    (access ? html_list_element("Edit", `component_edit_topic()`) : "") +
                    (access ? html_list_element("Delete", `component_delete_topic()`) : "")
                );
                break;
            case "topic_claim":
                menu.html(
                    html_list_element("Extend Claim", "component_claim_link()") +
                    (access ? html_list_element("Edit", `component_edit_claim()`) : "") +
                    (access ? html_list_element("Delete", `component_delete_claim()`) : "")
                );
                break;
            case "home_topic":
                menu.html(
                    html_list_element("Add Topic", `component_add_topic()`)
                )
                break;
            default:
                $(component).hide()
                return
        }
        menu.css("left", _left);
        menu.css("top", _top);
        menu.show();
        active = true;
        g_component = component;
        g_info = info;
        $("#component_menu_background").show();
    })
}
function component_hide_menu() {
    if (active) {
        $("#component_menu_background").hide();
        $("#component_menu").hide();
        active = false;
    }
}
function component_edit_reply() {
    $.get($SCRIPT_ROOT + "/dev/build/reply_editor", {
        reply: "",
        edit: "true"
    }, function(data) {
        $(g_component).parent().prev().children(".component_content").html(data)
    })
    component_hide_menu()
}
function component_edit_claim() {
    $.get($SCRIPT_ROOT + "/dev/build/claim_editor", {
        reply: "",
        edit: "true"
    }, function(data) {
        $(g_component).parent().prev().children(".component_content").html(data)
    })
    component_hide_menu()
}
function component_edit_topic() {
    $.get($SCRIPT_ROOT + "/dev/build/topic_editor", {
        edit: "true"
    }, function(data) {
        $(g_component).parent().prev().children(".component_title-topic").html(data)
    })
    component_hide_menu()
}
function submit_edit_reply(button) {
    let r_content = $(button).siblings("#editor_content").val()
    $.getJSON($SCRIPT_ROOT + "/dev/command/reply", {
        action: "edit",
        target: g_info.c_id,
        content: `${r_content}`
    }, function (data) {
        if (data.success) {
            $(g_component).parent().prev().children(".component_content").html(r_content)
        }
    })
}
function submit_edit_claim(button) {
    let c_header = $(button).siblings("#editor_header").val()
    let c_content = $(button).siblings("#editor_content").val()
    $.getJSON($SCRIPT_ROOT + "/dev/command/claim", {
        action: "edit",
        target: g_info.c_id,
        header: c_header,
        content: c_content
    }, function(data) {
        if (data.success) {
            $(g_component).parent().prev().prev().children(".component_title-claim").html(c_header)
            $(g_component).parent().prev().children(".component_content").html(c_content)
        }
    })
}
function submit_edit_topic(button) {
    let t_header = $(button).siblings("#editor_header").val()
    $.getJSON($SCRIPT_ROOT + "/dev/command/topic", {
        action: "edit",
        target: g_info.c_id,
        header: t_header
    }, function(data) {
        if (data.success) {
            $(g_component).parent().prev().children(".component_title-topic").html(t_header)
        }
    })
}
function component_delete(success) {
    if (success) {
        $(g_component).parent().parent().parent().remove()
    }
    component_hide_menu()
}
function component_delete_reply() {
    $.getJSON($SCRIPT_ROOT + "/dev/command/reply", {
        action: "delete",
        target: g_info.c_id
    }, function(data) {
        component_delete(data.success)
    })
}
function component_delete_claim() {
    $.getJSON($SCRIPT_ROOT + "/dev/command/claim", {
        action: "delete",
        target: g_info.c_id
    }, function(data) {
        component_delete(data.success)
    })
}
function component_delete_topic() {
    $.getJSON($SCRIPT_ROOT + "/dev/command/topic", {
        action: "delete",
        target: g_info.c_id
    }, function(data) {
        component_delete(data.success)
    })
}
function tag_class_to_id(clss) {
    switch (clss) {
        case "tag_clarification":
            return 0
        case "tag_supportingArgument":
            return 1
        case "tag_counterArgument":
            return 2
        case "tag_evidence":
            return 0
        case "tag_support":
            return 1
        case "tag_rebuttal":
            return 2
        case "tag_opposed":
            return 0
        case "tag_equivalent":
            return 1
        default:
            return ""
    }
}
function component_reply() {
    $.get($SCRIPT_ROOT + "/dev/build/reply_editor", {
        reply: g_info.c_id
    }, function(data) {
        $(g_component).parent().after(
            "<tr><td colspan='2'>" +
            data
            + "</td></tr>"
        )
    })
    component_hide_menu()
}
function post_reply_reply(button) {
    let r_content = $(button).siblings("#editor_content").val()
    let r_tag = $(button).siblings("#editor_tag").val()
    $.getJSON($SCRIPT_ROOT + "/dev/post/reply", {
        reply: g_info.c_id,
        content: r_content,
        tag: tag_class_to_id(r_tag)
    }, function (data) {
        if (data.success) {
            $.get($SCRIPT_ROOT + "/dev/build/reply", {
                reply_id: data.component_id,
                is_reply: "true"
            }, function(data) {
                $(g_component).parent().after(
                    "<tr><td colspan='2' class='component_reply-reply'>" +
                    data
                    + "</td></tr>"
                )
            })
        }
        $(button).parent().parent().parent().remove()
    })
}
function component_claim_reply() {
    $.get($SCRIPT_ROOT + "/dev/build/reply_editor", {
        claim: g_info.c_id
    }, function(data) {
        $(g_component).parent().after(
            "<tr><td colspan='2'>" +
            data
            + "</td></tr>"
        )
    })
    component_hide_menu()
}
function post_reply(button) {
    let r_content = $(button).siblings("#editor_content").val()
    let r_tag = $(button).siblings("#editor_tag").val()
    $.getJSON($SCRIPT_ROOT + "/dev/post/reply", {
        claim: g_info.c_id,
        content: r_content,
        tag: tag_class_to_id(r_tag)
    }, function (data) {
        if (data.success) {
            $.get($SCRIPT_ROOT + "/dev/build/reply", {
                reply_id: data.component_id
            }, function(data) {
                $("#replies").html(function (index, html) {
                    return data + html
                })
            })
        }
        $(button).parent().parent().parent().remove()
    })
}
function component_claim_link() {
    $.get($SCRIPT_ROOT + "/dev/build/claim_editor", {
        reply: g_info.c_id
    }, function(data) {
        $(g_component).parent().after(
            "<tr><td colspan='2'>" +
            data
            + "</td></tr>"
        )
    })
    component_hide_menu()
}
function post_claim_ex(button) {
    let c_header = $(button).siblings("#editor_header").val()
    let c_content = $(button).siblings("#editor_content").val()
    let c_tag = $(button).siblings("#editor_tag").val()
    $.getJSON($SCRIPT_ROOT + "/dev/post/claim", {
        header: c_header,
        content: c_content,
        reply: g_info.c_id,
        tag: tag_class_to_id(c_tag)
    }, function(data) {
        if (data.success) {
            $.get($SCRIPT_ROOT + "/dev/build/claim", {
                claim_id: data.component_id
            }, function(data) {
                $("#head-topic").after(data)
            })
        }
        $(button).parent().parent().parent().remove()
    })
}
function component_add_claim() {
    $.get($SCRIPT_ROOT + "/dev/build/claim_editor", {
        topic: g_info.c_id
    }, function(data) {
        $(g_component).parent().after(
            "<tr><td colspan='2'>" +
            data
            + "</td></tr>"
        )
    })
    component_hide_menu()
}
function post_claim(button) {
    let c_header = $(button).siblings("#editor_header").val()
    let c_content = $(button).siblings("#editor_content").val()
    let c_tag = $(button).siblings("#editor_tag").val()
    $.getJSON($SCRIPT_ROOT + "/dev/post/claim", {
        header: c_header,
        content: c_content,
        topic: g_info.c_id
    }, function(data) {
        if (data.success) {
            $.get($SCRIPT_ROOT + "/dev/build/claim", {
                claim_id: data.component_id
            }, function(data) {
                $("#head-topic").after(data)
            })
        }
        $(button).parent().parent().parent().remove()
    })
}
function component_add_topic() {
    $.get($SCRIPT_ROOT + "/dev/build/topic_editor", {}, function(data) {
        $(".base_home_topic-viewer").html(function (index, html) {
            return "<div class='component_base' id='new_topic'>" + data + "</div>" + html
        })
    })
    component_hide_menu()
}
function post_topic(button) {
    let t_header = $(button).siblings("#editor_header").val()
    $.getJSON($SCRIPT_ROOT + "/dev/post/topic", {
        header: t_header
    }, function (data) {
        if (data.success) {
            $.get($SCRIPT_ROOT + "/dev/build/topic", {
                topic_id: data.component_id
            }, function (data) {
                $(".base_home_topic-viewer").html(function (index, html) {
                    return data + html
                })
            })
        }
        $(".base_home_topic-viewer").children("#new_topic").remove()
    })
}