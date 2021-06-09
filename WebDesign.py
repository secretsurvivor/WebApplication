import json
import os
from json import dumps, JSONEncoder

from flask import Flask, render_template, session, request, g, url_for, redirect, get_template_attribute, sessions, \
    flash, jsonify
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

import SQL_Database

app = Flask(__name__)

global db
with app.app_context():
    db = SQL_Database.SQLDatabase()
    if not db.table_exists("users"):
        db.execute("CREATE TABLE users (accountID INT AUTO_INCREMENT PRIMARY KEY, username TEXT, hashedPassword "
                   "TEXT, admin BOOL, dateCreated DATETIME)")

    if not db.table_exists("topics"):
        db.execute("CREATE TABLE topics (topicID INT AUTO_INCREMENT PRIMARY KEY, header TEXT, accountID "
                   "INT, dateSubmitted DATETIME)")

    if not db.table_exists("claims"):
        db.execute("CREATE TABLE claims (claimID INT AUTO_INCREMENT PRIMARY KEY, header TINYTEXT, content TEXT, "
                   "topicID INT, accountID INT, dateSubmitted DATETIME, relatedClaim INT, tag INT)")

    if not db.table_exists("replies"):
        db.execute("CREATE TABLE replies (replyID INT AUTO_INCREMENT PRIMARY KEY, content TEXT, "
                   "claimID INT, accountID INT, dateSubmitted DATETIME, parentReply INT, tag INT)")

app.secret_key = b'\x9d\x12\xa9C\xb1\x03\x91\x0bv\xe1dp-\x18\x19\\'


@app.errorhandler(404)
def page_not_found():
    return render_template("error.html"), 404

@app.route("/favicon.ico")
def favicon():
    return url_for("static", filename="resources/favicon.ico")


@app.route('/')
def base():
    return redirect("/home")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/claim/<claim_id>")
def show_claim_page(claim_id):
    claim = get_claim_info(claim_id)
    if claim:
        return render_template("claimPage.html", claim_id=claim_id, title=claim[1], related_claim=claim[6] if claim[6] else "")
    return page_not_found()

@app.route("/topic/<topic_id>")
def show_topic_page(topic_id):
    topic = get_topic_info(topic_id)
    print(topic)
    if topic:
        return render_template("topicPage.html", topic_id=topic[0], title=topic[1])
    return page_not_found()


@app.route("/login")
def login_frame():
    return render_template("login.html")

@app.route("/account")
def account_page():
    current_user = current_user_info()
    if current_user:
        return render_template("account.html", account_id=current_user[0])
    else:
        process = request.args.get("process")
        if process:
            username = escape(request.args.get("username")).striptags()
            password = escape(request.args.get("password")).striptags()
            if process == "login":
                user = db.select("""SELECT * FROM users WHERE username=%s""", (username,))
                if user:
                    user = user[0]
                    if check_password_hash(user[2], password):
                        session["account"] = [user[0], user[1], user[3], user[4]]
                        return render_template("account.html", account_id=user[0])
                    else:
                        flash("Password was incorrect")
                else:
                    flash("Username is unrecognised")
            elif process == "register":
                user = db.select("SELECT * FROM users WHERE username='%s'", username)
                if user is None:
                    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    h_password = generate_password_hash(password)
                    user_id = db.commit("INSERT INTO users (username, hashedPassword, admin, dateCreated) VALUES ("
                                        "%s, %s, %s, %s)", (username, h_password, False, date))
                    if user_id:
                        session["account"] = [user_id, username, 0, date]
                        return render_template("account.html", account_id=user_id)
                    else:
                        flash("An error occurred, please try again")
                else:
                    flash("Username is already in use")
            else:
                flash("Unknown login method type")
    return redirect("/login")

@app.route("/logout")
def logout():
    session.pop("account", None)
    return redirect("/login")


@app.route("/dev/account")
def account_response():
    user = current_user_info()
    if user is None:
        return jsonify()
    return jsonify(account_id=user[0], username=user[1], admin=user[2], date_created=user[3])

@app.route("/dev/build/<component_type>")
def build_response(component_type):
    get = request.args.get
    if component_type == "reply":
        if get("reply_id"):
            reply = get_reply_info(get("reply_id"))
            return M_reply(reply[1], get_account_name(reply[3]), format_sql_datetime(reply[4]), function_json("reply", reply[3], reply[0]), tag_classes_reply(reply[6], get("is_reply")))
        else:
            return M_reply(get("content"), get("username"), get("date"), get("info"), get("tag"), get("reply"))
    elif component_type == "reply_editor":
        return M_reply_editor(get("claim"), get("reply"), get("edit"))
    elif component_type == "claim":
        if get("claim_id"):
            claim = get_claim_info(get("claim_id"))
            print(claim[7], tag_classes_claim(claim[7]))
            return M_claim(claim[1], claim[2], get_account_name(claim[4]), format_sql_datetime(claim[5]), function_json("topic_claim", claim[4], claim[0]), tag_classes_claim(claim[7]), "", claim[0])
        else:
            return M_claim(get("title"), get("content"), get("username"), get("date"), get("info"), get("tag"), "", get("link"))
    elif component_type == "claim_editor":
        return M_claim_editor(get("topic"), get("reply"), get("edit"))
    elif component_type == "topic":
        if get("topic_id"):
            topic = get_topic_info(get("topic_id"))
            return M_topic(topic[1], format_sql_datetime(topic[3]), function_json("all_topic", topic[2], topic[0]), topic[0])
        else:
            return M_topic(get("title"), get("date"), get("info"), get("link"))
    elif component_type == "topic_editor":
        return M_topic_editor(get("edit"))
    return ""

@app.route("/dev/command/<component_type>")
def command_response(component_type):
    action = request.args.get("action")
    target = request.args.get("target")
    get = request.args.get
    user = current_user_info()
    if action == "edit":
        if component_type == "reply":
            component = db.select("""SELECT * FROM replies WHERE replyID=%s""", (target,))[0]
            if user[2] or (component[3] == user[0]):
                db.commit("UPDATE replies SET content=%s WHERE replyID=%s", (get("content"), target))
                return jsonify(success=True)
        elif component_type == "claim":
            component = db.select("""SELECT * FROM claims WHERE claimID=%s""", (target,))[0]
            if user[2] or (component[4] == user[0]):
                db.commit("UPDATE claims SET header=%s, content=%s WHERE claimID=%s", (get("header"), get("content"), target))
                return jsonify(success=True)
        elif component_type == "topic":
            component = db.select("""SELECT * FROM topics WHERE topicID=%s""", (target,))[0]
            if user[2] or (component[2] == user[0]):
                db.commit("UPDATE topics SET header=%s WHERE topicID=%s", (get("header"), target))
                return jsonify(success=True)
    elif action == "delete":
        if component_type == "reply":
            component = db.select("""SELECT * FROM replies WHERE replyID=%s""", (target,))[0]
            print(component[3], user[0])
            if user[2] or (component[3] == user[0]):
                db.commit("""DELETE FROM replies WHERE replyID=%s""", (target,))
                print("%s was deleted" % target)
                return jsonify(success=True)
        elif component_type == "claim":
            component = db.select("SELECT * FROM claims WHERE claimID=%s", (target,))[0]
            print(component[4], user[0])
            if user[2] or (component[4] == user[0]):
                db.commit("""DELETE FROM claims WHERE claimID=%s""", (target,))
                print("%s was deleted" % target)
                return jsonify(success=True)
        elif component_type == "topic":
            component = db.select("SELECT * FROM topics WHERE topicID=%s", (target,))[0]
            if user[2] or (component[2] == user[0]):
                db.commit("""DELETE FROM topics WHERE topicID=%s""", (target,))
                print("%s was deleted" % target)
                return jsonify(success=True)
    return jsonify(success=False)

@app.route("/dev/post/<component_type>")
def editor_post(component_type):
    get = request.args.get
    user = current_user_info()
    if user:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if component_type == "reply":
            claim = get("claim")
            if not claim:
                claim = db.select("SELECT claimID FROM replies WHERE replyID=%s", (get("reply"),))[0][0]
            c_id = db.commit("INSERT INTO replies (content, claimID, accountID, dateSubmitted, parentReply, tag) VALUES (%s, "
                      "%s, %s, %s, %s, %s)", (get("content"), claim, user[0], date, get("reply"), get("tag")))
            return jsonify(success=True, component_id=c_id)
        elif component_type == "claim":
            topic = get("topic")
            if not topic:
                topic = db.select("SELECT topicID FROM claims WHERE claimID=%s", (get("reply"),))[0][0]
            c_id = db.commit("INSERT INTO claims (header, content, topicID, accountID, dateSubmitted, relatedClaim, "
                      "tag) VALUES (%s, %s, %s, %s, %s, %s, %s)", (get("header"), get("content"), topic,
                                                                   user[0], date, get("reply"), get("tag")))
            return jsonify(success=True, component_id=c_id)
        elif component_type == "topic":
            c_id = db.commit("INSERT INTO topics (header, accountID, dateSubmitted) VALUES (%s, %s, %s)", (get("header"), user[0], date))
            return jsonify(success=True, component_id=c_id)
    return jsonify(success=False)


@app.context_processor
def flask_methods():
    return dict(
        url_for=dated_url_for,
        format_datetime=format_sql_datetime,
        posted_objects_num=posted_objects,
        get_account=get_account_info,
        get_claim=get_claim_info,
        get_reply=get_reply_info,
        get_topic=get_topic_info,
        select=db.select,
        current_user_info=current_user_info
    )

def current_user_info():  # [0: accountID, 1: username, 2: admin, 3: dateCreated]
    return session.get("account")


app.jinja_env.globals.update(current_user_info=current_user_info)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


def format_sql_datetime(date_time) -> str:
    return "%s/%s/%s %s:%s" % (date_time.year, date_time.month, date_time.day, date_time.hour, date_time.minute)


def posted_objects(account_id):
    topics = db.select("SELECT topicID FROM topics WHERE accountID='%s'", account_id) or []
    claims = db.select("SELECT claimID FROM claims WHERE accountID='%s'", account_id) or []
    replies = db.select("SELECT replyID FROM replies WHERE accountID='%s'", account_id) or []
    return [topics, claims, replies]


def get_account_info(account_id):
    user = db.select("""SELECT * FROM users WHERE accountID=%s""", (account_id,))
    if user:
        return user[0]
    return


def get_account_name(account_id):
    return get_account_info(account_id)[1]


def get_claim_info(claim_id):
    user = db.select("""SELECT * FROM claims WHERE claimID=%s""", (claim_id,))
    if user:
        return user[0]
    return


def get_reply_info(reply_id):
    user = db.select("""SELECT * FROM replies WHERE replyID=%s""", (reply_id,))
    if user:
        return user[0]
    return


def get_topic_info(topic_id):
    user = db.select("""SELECT * FROM topics WHERE topicID=%s""", (topic_id,))
    if user:
        return user[0]
    return


@app.context_processor
def macro_building_functions():
    return dict(
        build_all_topics=build_all_topics,
        build_topic_from_claim=build_topic_from_claim,
        build_related_claims=build_related_claims,
        build_claim=build_claim,
        build_replies=build_replies,
        build_topic=build_topic,
        build_claims_from_topic=build_claims_from_topic
    )


with app.app_context():
    M_reply = get_template_attribute("components/reply.html", "reply")
    # reply(content, username, dateTime, info, tag="", reply="")

    M_reply_editor = get_template_attribute("components/reply_editor.html", "reply_editor")
    # reply_editor(reply="")

    M_claim = get_template_attribute("components/claim.html", "claim")
    # claim(title, content, username, dateTime, info, tag="", reply="", link="")

    M_claim_editor = get_template_attribute("components/claim_editor.html", "claim_editor")
    # claim_editor(reply="")

    M_topic = get_template_attribute("components/topic.html", "topic")
    # topic(title, dateTime, info, link="")

    M_topic_editor = get_template_attribute("components/topic_editor.html", "topic_editor")
    # topic_editor()

tagClasses_reply = ["tag_clarification", "tag_supportingArgument", "tag_counterArgument", "tag_evidence", "tag_support",
                    "tag_rebuttal"]
tagClasses_claim = ["tag_opposed", "tag_equivalent"]


def tag_classes_reply(tag_id, reply):
    if tag_id is not None:
        if reply:
            return tagClasses_reply[tag_id + 3]
        else:
            return tagClasses_reply[tag_id]
    return ""

def tag_classes_claim(tag_id):
    if tag_id == 0:
        return "tag_opposed"
    elif tag_id == 1:
        return "tag_equivalent"
    return ""

def function_json(t, a, i):
    return "{'type':'%s', 'account_id':'%s', 'c_id':'%s'}" % (t, a, i)


def build_reply(reply_id, is_reply=False):
    reply = get_reply_info(reply_id)
    if reply:
        children = db.select("SELECT * FROM replies WHERE parentReply='%s'", (reply_id,))
        if children:
            replies = ""
            for child in children:
                replies += build_reply(child[0], True)
            return M_reply(reply[1], get_account_name(reply[3]), format_sql_datetime(reply[4]), function_json("reply", reply[3], reply[0]), tag_classes_reply(reply[6], is_reply), replies)
        else:
            return M_reply(reply[1], get_account_name(reply[3]), format_sql_datetime(reply[4]), function_json("reply", reply[3], reply[0]), tag_classes_reply(reply[6], is_reply))
    return ""


def build_topic_from_claim(claim_id):
    claim = get_claim_info(claim_id)
    if claim:
        topic = get_topic_info(claim[3])
        if topic:
            return M_topic(topic[1], topic[3], function_json("claim_topic", topic[2], topic[0]), topic[0])
    return ""

def build_related_claims(claim_id):
    claim = get_claim_info(claim_id)
    if claim:
        if claim[6]:
            out = build_related_claims(claim[6])
            out += M_claim(claim[1], claim[2], get_account_name(claim[4]), format_sql_datetime(claim[5]), function_json("related_claim", claim[4], claim[0]),
                           tag_classes_claim(claim[7]), "", claim[0])
            return out
        else:
            return M_claim(claim[1], claim[2], get_account_name(claim[4]), format_sql_datetime(claim[5]), function_json("related_claim", claim[4], claim[0]),
                           tag_classes_claim(claim[7]), "", claim[0])
    return ""

def build_claim(claim_id):
    claim = get_claim_info(claim_id)
    if claim:
        return M_claim(claim[1], claim[2], get_account_name(claim[4]), format_sql_datetime(claim[5]), function_json("claim", claim[4], claim[0]), tag_classes_claim(claim[7]))
    return ""

def build_replies(claim_id):
    replies = db.select("""SELECT * FROM replies WHERE claimID=%s and parentReply is null ORDER BY dateSubmitted DESC""", (claim_id,))
    if replies:
        out = ""
        for reply in replies:
            out += build_reply(reply[0])
        return out
    return ""

def build_topic(topic_id):
    topic = get_topic_info(topic_id)
    if topic:
        return M_topic(topic[1], format_sql_datetime(topic[3]), function_json("topic", topic[2], topic[0]))
    return ""

def build_all_topics():
    topics = db.select("SELECT * FROM topics ORDER BY dateSubmitted DESC")
    if topics:
        out = ""
        for topic in topics:
            out += M_topic(topic[1], format_sql_datetime(topic[3]), function_json("all_topic", topic[2], topic[0]), topic[0])
        return out
    return ""

def build_claims_from_topic(topic_id):
    claims = db.select("SELECT * FROM claims WHERE topicID='%s' ORDER BY dateSubmitted DESC ", (topic_id,))
    if claims:
        out = ""
        for claim in claims:
            out += M_claim(claim[1], claim[2], get_account_name(claim[4]), format_sql_datetime(claim[5]), function_json("topic_claim", claim[4], claim[0]), tag_classes_claim(claim[7]), "", claim[0])
        return out
    return ""


if __name__ == '__main__':
    app.run()
