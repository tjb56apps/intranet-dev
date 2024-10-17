import os
import ast
from flask import url_for, request, session, redirect
# from app import create_app
# from app.extensions import db
from app.extensions.database import db
from app.addons.main.model.main import Nav
from app.auth.managementAuth import Users
import json

def get_addons():
    _mf_dict = []
    for addons_dir in os.listdir(os.path.join(os.getcwd(), "app", "addons")):
        try:
            mf = open(os.path.join(os.getcwd(), "app", "addons", addons_dir, "__manifest__.py"))
            mf_ = ast.literal_eval(mf.read())
            if mf_["name"] != "Main":
                # print(mf_["name"])
                _mf_dict.append(mf_)
        except:
            pass

    return _mf_dict

def query_addons_from_db():
    try:
        # return Nav.query.all()
        return db.query(Nav).all()
    except:
        return []
    
def get_addon(addondir=""):
    # print(f">> {addondir}")
    if addondir == "users":
        return {"name": "Users", "version": "1.0"}
    elif addondir == "user-edit":
        return {"name": "User Edit", "version": "1.0"}
    # elif addondir == "user-ad":
    #     return {"name": "User AD", "version": "1.0"}
    elif addondir == "modules":
        return {"name": "Modules", "version": "1.0"}
    elif addondir == "settings":
        return {"name": "Settings", "version": "1.0"}
    elif addondir == "check-log":
        return {"name": "Check log", "version": "1.0"}
    elif addondir == "pwbi-1":
        return {"name": "Hse Lagging Indicator", "version": "1.0"}
    elif addondir == "pwbi-2":
        return {"name": "Production & Consumption", "version": "1.0"}
    elif addondir == "pwbi-3":
        return {"name": "IT Team", "version": "1.0"}
    else:
 
        if "loggedin" in session:
            pass
        else:
            return []

        mf = open(os.path.join(os.getcwd(), "app", "addons", addondir, "__manifest__.py"))
        result = ast.literal_eval(mf.read())

        # from database
        # result__ = Nav.query.filter_by(app_id=result["id"]).first()
        result__ = db.query(Nav).filter_by(app_id=result["id"]).first()

        if result__:
            result_nav = {
                "id": result__.id,
                "name": result__.name,
                "version": result__.version,
                "status": result__.status,
                "path": result__.path,
                "nav": json.loads(result__.nav)
            }
        else:
            result_nav = []
        
        if result["id"]:
            try:
                # resmod = Nav.query.filter_by(app_id=result["id"]).first().status
                resmod = db.query(Nav).filter_by(app_id=result["id"]).first().status
            except:
                resmod = 0
        else:
            resmod = 0

        # get_apps_id = Users.query.filter_by(username=session["username"]).first()
        get_apps_id = db.query(Users).filter_by(username=session["username"]).first()
        level = get_apps_id.level
        user_app = 0
        for ap in get_apps_id.apps_id.split(","):
            if level == "administrator":
                user_app = 1
            elif level == "user":
                # control ldap
                # print("Control LDAP")
                # ldap = True
                # if ldap == True:
                # end control ldap
                if ap == result["id"]:
                    user_app = 1

        if 'loggedin' in session and resmod and user_app: # session management
            res = True
        else:
            res = False

        return result_nav, res
    
def get_addon_manifest(addondir=""):
    mf = open(os.path.join(os.getcwd(), "app", "addons", addondir, "__manifest__.py"))
    return ast.literal_eval(mf.read())
        
def get_child_path():
    return os.path.basename(url_for(request.endpoint))

# def create_table():
#     app = create_app()
#     with app.app_context():
#         db.create_all()

def get_level(username=""):
    
    level = db.query(Users).filter_by(username=username).where(Users.domain == session["domain"]).first().level
    # print(level)
    if level == "administrator":
        lv = True
    else:
        lv = False

    return lv

def ldap_check():
    # if Nav.query.filter_by(app_id="C003"):
    if db.query(Nav).filter_by(app_id="C003"):
        # return Nav.query.filter_by(app_id="C003").first().status
        return db.query(Nav).filter_by(app_id="C003").first().status
    else:
        return 0
    
def get_title_module(addon):
    # print(addon)
    # beta
    mcondi = request.path.split("/")
    # print(addon)
    if mcondi[1]:
        t1 = (addon[0]["name"])
        if mcondi[2]:
            for nd in addon[0]["nav"]:
                try:
                    for d in nd["child"]:
                        if d["path"] == mcondi[2]:
                            t2 = (d["name"])
                except:
                    pass
        try:
            return f"{t1} | {t2}"
        except:
            return f"{t1}"
    # end beta