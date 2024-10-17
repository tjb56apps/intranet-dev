from flask import session, render_template, request, redirect, url_for
from app.addons.main import bp
from app.manifest import get_addons, get_addon, get_child_path, query_addons_from_db, get_addon_manifest, get_level, ldap_check # create_table, 
from app.addons.main.model.main import Nav
from app.auth.managementAuth import Users
# from app.extensions import db
from app.extensions.database import db
import json
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# index - v2
@bp.route("/v2")
def index_v2():
    if 'loggedin' in session:
        addons = query_addons_from_db()
        
        status= {
            "index": True,
            "users": False,
            "user_ad": False,
            "modules": False,
            "settings": False
        }

        print(addons)
        print(status)

        return render_template("addons/main/templates/v2/index.html", addons=addons, status=status, addon_nav=get_addon("main"))

    return redirect(url_for('main.login'))
# index - v2 - end

@bp.route('/')
def index():
    if 'loggedin' in session:

        # print(f'+++++> {get_level(session["username"])}')

        addons = query_addons_from_db()
        
        status= {
            "index": True,
            "users": False,
            "user_ad": False,
            "modules": False,
            "settings": False
        }

        # return 'Your loggedin as ' + session["username"] + ' <a href="/logout">Logout</a>'
        # return render_template("addons/main/templates/index.html", addons=addons, status=status, addon_nav=get_addon("main"))
        
        # return render_template("addons/main/templates/v2/index.html", addons=addons, status=status, addon_nav=get_addon("main"))
        return render_template("addons/main/templates/merge_template_v3/index.html", addons=addons, status=status, addon_nav=get_addon("main"), path="/dashboard", name="Home")
    
    return redirect(url_for('main.login'))

@bp.route("/users")
def users():
    if 'loggedin' in session:
        if get_level(session["username"]):
            # addons = get_addons()
            addons = query_addons_from_db()
            status= {
                "index": False,
                "users": True,
                "user_ad": False,
                "modules": False,
                "settings": False
            }

            # query-users
            all_users = db.query(Users).all()

            # return render_template("addons/main/templates/users.html", all_users=all_users, addons=addons, status=status, addon_nav=get_addon(get_child_path()))
            # return render_template("addons/main/templates/v2/users.html", all_users=all_users, addons=addons, status=status, addon_nav=get_addon(get_child_path()))
            return render_template("addons/main/templates/merge_template_v3/users.html", all_users=all_users, addons=addons, status=status, addon_nav=get_addon(get_child_path()), path=request.path, name="Users")
        else:
            return redirect(url_for("main.index"))
        
    return redirect(url_for("main.index"))

@bp.route("/login")
def login():

    # print(db.query(Users).filter_by(username="admin").where(Users.domain == "pt-bjp").first())

    # for row in db.query(Users).all():
    #     print(row)

    if 'loggedin' in session:
        return redirect(url_for("main.index"))
    else:
        # return render_template("addons/main/templates/login.html")
        # return render_template("addons/main/templates/v2/login.html")
        return render_template("addons/main/templates/merge_template_v3/login.html", path=request.path, name="Login")

@bp.route("/auth", methods=["GET", "POST"])
def auth():
    if 'loggedin' in session:
        return redirect(url_for("main.index"))
    else:
        if request.method == "POST":
            # print(request.form["domain"])
            # pwdd = generate_password_hash("sapi", "scrypt")
            # check_password_hash(pwdd, "sapi")
            
            # if Users.query.filter_by(username=request.form["username"]).first():
            if db.query(Users).filter_by(username=request.form["username"]).where(Users.domain == request.form["domain"]).first():
                # ldap control
                # if Users.query.filter_by(username=request.form["username"]).first().level == "administrator":
                if db.query(Users).filter_by(username=request.form["username"]).where(Users.domain == request.form["domain"]).first().level == "administrator":
                    print("TIDAK! MEMERLUKAN AKSES AD")
                    # check password from db
                    # if check_password_hash(Users.query.filter_by(username=request.form["username"]).first().password, request.form["password"]):
                    if check_password_hash(db.query(Users).filter_by(username=request.form["username"]).first().password, request.form["password"]):
                        print(True)

                        session["loggedin"] = True
                        session["domain"] = request.form["domain"]
                        # session["username"] = Users.query.filter_by(username=request.form["username"]).first().username
                        session["username"] = db.query(Users).filter_by(username=request.form["username"]).first().username
                        # update
                        session["leveling"] = db.query(Users).filter_by(username=request.form["username"]).first().leveling
                        session["department"] = db.query(Users).filter_by(username=request.form["username"]).first().department
                        session["position"] = db.query(Users).filter_by(username=request.form["username"]).first().position

                        return redirect(url_for("main.index"))
                    else:
                        print("Password failed.")
                        return redirect(url_for("main.login"))
                    # end check password from db
                # elif Users.query.filter_by(username=request.form["username"]).first().level == "user" and ldap_check(): # ldap control
                elif db.query(Users).filter_by(username=request.form["username"]).where(Users.domain == request.form["domain"]).first().level == "user" and ldap_check():
                    print("MEMERLUKAN AKSES AD")
                    from app.addons.powerad.connection import conn
                    
                    if conn.connect(request.form["username"], request.form["password"], request.form["domain"]):
                        session["loggedin"] = True
                        session["domain"] = request.form["domain"]
                        # session["username"] = Users.query.filter_by(username=request.form["username"]).first().username
                        session["username"] = db.query(Users).filter_by(username=request.form["username"]).first().username
                        # update
                        session["leveling"] = db.query(Users).filter_by(username=request.form["username"]).first().leveling
                        session["department"] = db.query(Users).filter_by(username=request.form["username"]).first().department
                        session["position"] = db.query(Users).filter_by(username=request.form["username"]).first().position

                        return redirect(url_for("main.index"))
                    else:
                        print("kembali ke index karena koneksi gagal")
                        return redirect(url_for("main.index"))
                else:
                    print("Fitur koneksi LDAP tidak aktif, akan dialaihkan ke login & pass dari database")
                # end ldap control
                    
                    # check password from db
                    # if check_password_hash(Users.query.filter_by(username=request.form["username"]).first().password, request.form["password"]):
                    if check_password_hash(db.query(Users).filter_by(username=request.form["username"]).first().password, request.form["password"]):
                        print(True)

                        session["loggedin"] = True
                        session["domain"] = request.form["domain"]
                        # session["username"] = Users.query.filter_by(username=request.form["username"]).first().username
                        session["username"] = db.query(Users).filter_by(username=request.form["username"]).first().username
                        # update
                        session["leveling"] = db.query(Users).filter_by(username=request.form["username"]).first().leveling
                        session["department"] = db.query(Users).filter_by(username=request.form["username"]).first().department
                        session["position"] = db.query(Users).filter_by(username=request.form["username"]).first().position
                        
                        return redirect(url_for("main.index"))
                    else:
                        print("Password failed.")
                        return redirect(url_for("main.login"))
                    # end check password from db
            else:
                print("User or Domain not found.")
                return redirect(url_for("main.login"))
            
        else:
            return redirect(url_for("main.login"))

@bp.route("/user-ad")
def user_ad():
    if 'loggedin' in session:
        if get_level(session["username"]):
            # addons = get_addons()
            addons = query_addons_from_db()
            status= {
                "index": False,
                "users": False,
                "user_ad": True,
                "modules": False,
                "settings": False
            }

            return render_template("addons/main/templates/user-ad.html", addons=addons, status=status, addon_nav=get_addon(get_child_path()))
        else:
            return redirect(url_for("main.index"))
        
    return redirect(url_for("main.index"))

@bp.route("/modules")
def modules():
    if 'loggedin' in session:
        if get_level(session["username"]):
            status= {
                "index": False,
                "users": False,
                "user_ad": False,
                "modules": True,
                "settings": False
            }

            # Queue from manifest
            addons = get_addons()
            # Query Nav from database
            nav_query = query_addons_from_db()

            # tester
            nav_dict = []
            for data in nav_query:
                root = {
                    "id": data.app_id,
                    "name": data.name,
                    "version": data.version,
                    "status": data.status,
                    "path": data.path,
                    "nav": data.nav
                }

                nav_dict.append(root)

            # check status submited
            for addon in addons:
                try:
                    # if Nav.query.filter_by(app_id=addon["id"]).first():
                    if db.query(Nav).filter_by(app_id=addon["id"]).first():
                        addon["export_status"] = True
                    else:
                        pass
                except:
                    pass
                
            # return render_template("addons/main/templates/modules.html", addons=nav_dict, addon_tables=addons,status=status, addon_nav=get_addon(get_child_path()), nav_query=nav_dict)
            # return render_template("addons/main/templates/v2/modules.html", addons=nav_dict, addon_tables=addons,status=status, addon_nav=get_addon(get_child_path()), nav_query=nav_dict)
            return render_template("addons/main/templates/merge_template_v3/modules.html", addons=nav_dict, addon_tables=addons,status=status, addon_nav=get_addon(get_child_path()), nav_query=nav_dict, path=request.path, name="Modules")
        else:
            return redirect(url_for("main.index"))
        
    return redirect(url_for("main.index"))

@bp.route("/settings")
def settings():
    if 'loggedin' in session:
        if get_level(session["username"]):
            # addons = get_addons()
            addons = query_addons_from_db()
            status= {
                "index": False,
                "users": False,
                "user_ad": False,
                "modules": False,
                "settings": True
            }

            # return render_template("addons/main/templates/settings.html", addons=addons, status=status, addon_nav=get_addon(get_child_path()))
            # return render_template("addons/main/templates/v2/settings.html", addons=addons, status=status, addon_nav=get_addon(get_child_path()))
            return render_template("addons/main/templates/merge_template_v3/settings.html", addons=addons, status=status, addon_nav=get_addon(get_child_path()), path=request.path, name="Settings")
        else:
            return redirect(url_for("main.index"))
        
    return redirect(url_for("main.index"))

@bp.route("/check-log")
def check_log():
    if 'loggedin' in session:
        if get_level(session["username"]):
            # addons = get_addons()
            addons = query_addons_from_db()
            status= {
                "index": False,
                "users": False,
                "user_ad": False,
                "modules": False,
                "settings": True
            }

            # return render_template("addons/main/templates/settings.html", addons=addons, status=status, addon_nav=get_addon(get_child_path()))
            # return render_template("addons/main/templates/v2/settings.html", addons=addons, status=status, addon_nav=get_addon(get_child_path()))
            return render_template("addons/main/templates/merge_template_v3/check-log.html", addons=addons, status=status, addon_nav=get_addon(get_child_path()), path=request.path, name="Check Log")
        else:
            return redirect(url_for("main.index"))
        
    return redirect(url_for("main.index"))

@bp.route("/export-app/<id>")
def export_app(id):
    if 'loggedin' in session:
        if get_level(session["username"]):
            # create_table()
            
            addons = get_addons()
            for addon in addons:
                if addon["id"] == id:
                    addon_ = get_addon_manifest(addon["path"])
                    
                    # query_id = Nav.query.filter_by(app_id=id).first()
                    query_id = db.query(Nav).filter_by(app_id=id).first()
                    if query_id:
                        # nav = Nav.query.filter_by(app_id=id)
                        nav = db.query(Nav).filter_by(app_id=id)
                        nav.update(
                            {
                                # Nav.app_id: addon_["id"],
                                # Nav.name: addon_["name"],
                                Nav.version: addon_["version"],
                                Nav.path: addon_["path"],
                                Nav.nav: json.dumps(addon_["nav"])
                            }
                        )

                        # db.session.commit()
                        db.commit()
                        
                    else:
                        nav = Nav(
                            app_id=addon_["id"],
                            name=addon_["name"],
                            version=addon_["version"],
                            status=1,
                            path=addon_["path"],
                            nav=json.dumps(addon_["nav"])
                        )

                        # db.session.add(nav)
                        # db.session.commit()
                        db.add(nav)
                        db.commit()

            return redirect(url_for('main.modules'))
        else:
            return redirect(url_for("main.index"))
        
    return redirect(url_for("main.login"))

@bp.route("/update-status/<id>/<status>")
def update_status(id, status):
    if 'loggedin' in session:
        if get_level(session["username"]):
            # nav = Nav.query.filter_by(app_id=id)
            nav = db.query(Nav).filter_by(app_id=id)
            nav.update(
                {
                    Nav.status: status
                }
            )

            # db.session.commit()
            db.commit()

            return redirect(url_for('main.modules'))
        return redirect(url_for("main.index"))

    return redirect(url_for("main.login"))

@bp.route("/user-edit")
def user_edit():
    if 'loggedin' in session:
        if get_level(session["username"]):
            if type(request.args.get("id", type=int)) == int:
                user = db.query(Users).filter_by(id=request.args.get("id")).first()
                # return render_template("addons/main/templates/user-edit.html", user=user, addon_nav=get_addon(get_child_path())) # addons=addons, status=status, addon_nav=get_addon(get_child_path())
                # return render_template("addons/main/templates/v2/user-edit.html", user=user, addon_nav=get_addon(get_child_path()))
                return render_template("addons/main/templates/merge_template_v3/users-edit.html", user=user, addon_nav=get_addon(get_child_path()))
            else:
                return redirect(url_for("main.users"))
        else:
            return redirect(url_for("main.index"))

    return redirect(url_for("main.index"))

@bp.route("/user-update", methods=["GET", "POST"])
def user_update():
    if 'loggedin' in session:
        if get_level(session["username"]):
            if request.method == "POST":
                pwd =  generate_password_hash(password=request.form["password"], method="scrypt")
                db.query(Users).where(Users.username == request.form["username"]).update(values={"apps_id": request.form["appsid"], "password": pwd, "leveling": request.form["addonlevel"]})
                db.commit()
                return redirect(url_for("main.user_edit"))

    return redirect(url_for("main.index"))

@bp.route("/user-delete")
def user_delete():
    if 'loggedin' in session:
        if get_level(session["username"]):
            id = request.args.get("id", type=int)
            if type(id) == int:
                # filter default user
                if db.query(Users).filter_by(id=id).first().username == "admin":
                    return redirect(url_for("main.users"))
                elif db.query(Users).filter_by(id=id).first().username == session["username"]:
                    return redirect(url_for("main.users"))
                else:
                    db.query(Users).filter_by(id=id).delete()
                    db.commit()
                    
                return redirect(url_for("main.users"))
            else:
                return {"type": "str"}
        else:
            return redirect(url_for("main.index"))
    else:
        return redirect(url_for("main.index"))

# POWER BI EMBEDDED
@bp.route("/pwbi-1")
def pwbi_1():
    if 'loggedin' in session:
        status= {
                "index": False,
                "users": False,
                "user_ad": False,
                "modules": False,
                "settings": False
            }
        
        addons = query_addons_from_db()
        return render_template("addons/main/templates/v2/pwbi-1.html", status=status, addons=addons, addon_nav=get_addon(get_child_path()))

    return redirect(url_for('main.login'))

@bp.route("/pwbi-2")
def pwbi_2():
    if 'loggedin' in session:
        status= {
                "index": False,
                "users": False,
                "user_ad": False,
                "modules": False,
                "settings": False
            }
        
        addons = query_addons_from_db()
        return render_template("addons/main/templates/v2/pwbi-2.html", status=status, addons=addons, addon_nav=get_addon(get_child_path()))

    return redirect(url_for('main.login'))

@bp.route("/pwbi-3")
def pwbi_3():
    if 'loggedin' in session:
        status= {
                "index": False,
                "users": False,
                "user_ad": False,
                "modules": False,
                "settings": False
            }
        
        addons = query_addons_from_db()
        return render_template("addons/main/templates/v2/pwbi-3.html", status=status, addons=addons, addon_nav=get_addon(get_child_path()))

    return redirect(url_for('main.login'))