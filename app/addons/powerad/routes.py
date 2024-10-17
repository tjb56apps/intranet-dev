from app.addons.powerad import bp
from flask import render_template, jsonify, flash
from app.manifest import *
from app.addons.powerad.connection import active_directory
from app.extensions.database import db
from app.addons.powerad.model.powerad import DataServer, Servers

@bp.route("/")
def index():
    addon = get_addon(addondir="powerad")
    get_title_module(addon)
    if addon:
        if addon[1]:
            # return render_template("addons/powerad/templates/index.html", addon_nav=addon[0], path=get_child_path())
            # return render_template("addons/powerad/templates/v2/index.html", addon_nav=addon[0], path=get_child_path())
            return render_template("addons/powerad/templates/merge_template_v3/index.html", addon_nav=addon[0], path=get_child_path(), name=addon[0]["name"]) # name=addon[0]["name"]
    
    return redirect(url_for('main.index'))

@bp.route("/user-ad")
def user_ad():
    addon = get_addon(addondir="powerad")
    # print()
    if addon:
        if addon[1]:
            # default all
            dc = db.query(DataServer).filter_by(id=1).first()
            users_from_ad = active_directory.get_users("all", dc.dcserver, dc.oubase)
            # print(users_from_ad)

            # for user in users_from_ad:
            #     try:
            #         print("> ", user["lastname"].replace("–", "-").split("-")[0])
            #     except:
            #         print(user["lastname"])

            # return render_template("addons/powerad/templates/user-ad.html", users_from_ad=users_from_ad, addon_nav=addon[0], path=get_child_path())
            # return render_template("addons/powerad/templates/v2/user-ad.html", users_from_ad=users_from_ad, addon_nav=addon[0], path=get_child_path())
            return render_template("addons/powerad/templates/merge_template_v3/user-ad.html", users_from_ad=users_from_ad, addon_nav=addon[0], path=get_child_path(), name=get_title_module(addon)) # name=get_title_module(addon)
    return redirect(url_for('main.index'))

@bp.route("/export-user")
def export_user():
    addon = get_addon(addondir="powerad")
    if addon:
        if addon[1]:
            # get user AD
            dc = db.query(DataServer).filter_by(id=1).first()
            if request.args.get("username"):
                ad_user = active_directory.get_user(request.args.get("username"), dc.dcserver)
                if ad_user:
                    pass
                else:
                    print("AD not Connected !")
                    return redirect(url_for('main.index'))
            else:
                print("Please check route")
                return redirect(url_for('main.index'))

            # print(ad_user[0])
            # return render_template("addons/powerad/templates/export-user.html", ad_user=ad_user, addon_nav=addon[0])
            # return render_template("addons/powerad/templates/v2/export-user.html", ad_user=ad_user, addon_nav=addon[0])
            return render_template("addons/powerad/templates/merge_template_v3/export-user.html", ad_user=ad_user, addon_nav=addon[0])
    return redirect(url_for('main.index'))

@bp.route("/export-user-add", methods=["GET", "POST"])
def export_user_add():
    if request.method == "POST":
        addon = get_addon(addondir="powerad")
        if addon:
            if addon[1]:
                name = (request.form["name"])
                username = (request.form["username"])
                department = (request.form["department"])
                position = (request.form["position"])
                email = (request.form["email"])
                appsid = (request.form["appsid"])
                level = (request.form["level"])
                leveling = (request.form["addonlevel"])

                # extract domain
                email_domain = email.split("@")[1].split(".")[0]

                # check record exist
                if db.query(Users).filter_by(username=username).first():
                    if db.query(Users).filter_by(email=email).first():
                        flash("Account is al exist", "ready")
                        return redirect(url_for("powerad.user_ad"))
                    else:
                        if "administrator" == level:
                            level_ = "DB"
                        elif "user" == level:
                            level_ = "AD"

                        add_ = Users(name=name, department=department, position=position, email=email, username=username, password="", apps_id=appsid, level=level, type=level_, domain=email_domain, leveling=leveling)
                        db.add(add_)
                        db.commit()

                        return redirect(url_for("main.users"))    
                else:
                    if "administrator" == level:
                        level_ = "DB"
                    elif "user" == level:
                        level_ = "AD"

                    add_ = Users(name=name, department=department, position=position, email=email, username=username, password="", apps_id=appsid, level=level, type=level_, domain=email_domain, leveling=leveling)
                    db.add(add_)
                    db.commit()

                    return redirect(url_for("main.users"))
                
            return jsonify(message="error")
            
        return jsonify(message="error")
    
    return jsonify(message="error")

@bp.route("/settings")
def settings():
    addon = get_addon(addondir="powerad")
    # print(get_title_module(addon))
    if addon:
        if addon[1]:
            server_list = db.query(Servers).all()
            data_server = db.query(DataServer).first()

            # return render_template("addons/powerad/templates/settings.html", data_server=data_server, server_list=server_list, addon_nav=addon[0], path=get_child_path())
            # return render_template("addons/powerad/templates/v2/setting.html", data_server=data_server, server_list=server_list, addon_nav=addon[0], path=get_child_path())
            return render_template("addons/powerad/templates/merge_template_v3/setting.html", data_server=data_server, server_list=server_list, addon_nav=addon[0], path=get_child_path(), name=get_title_module(addon)) # name=get_title_module(addon)
    return redirect(url_for('main.index'))

@bp.route("/change-settings", methods=["GET", "POST"])
def change_settings():
    if request.method == "POST":
        addon = get_addon(addondir="powerad")
        if addon:
            if addon[1]:
                # print(request.form["username"])
                # print(request.form["password"])
                # print(request.form["server"])

                dc_serv = request.form["server"].split(".")
                dcserver = ""
                for serv in dc_serv:
                    dcserver += f"DC={serv},"
                
                # print(request.form["adsi"])

                # update
                data_server_update = db.query(DataServer)
                data_server_update.update({
                    DataServer.username: request.form["username"].strip(),
                    DataServer.password: request.form["password"].strip(),
                    DataServer.dcserver: dcserver[:-1].strip(),
                    DataServer.oubase: request.form["adsi"].strip(),
                    DataServer.server: request.form["server"].strip()
                })

                db.commit()

                return redirect(url_for("powerad.settings"))

    return redirect(url_for('main.index'))