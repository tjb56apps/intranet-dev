from flask import render_template, redirect, url_for, session
from app.addons.helloworld import bp
from app.manifest import get_addon, get_child_path, get_title_module
from app.auth.managementAuth import Users

@bp.route("/")
def helloworld():
    addon = get_addon(addondir="helloworld")
    if addon: # handle session ready or empty
        if addon[1]: # handle session True or False
            """
            **Here your code logic**
            Warning: coding rules that must be adhered to. it is prohibited to change the patented core system.
            """

            ses_info = {
                "sessions": ['session["loggedin"]', 'session["domain"]', 'session["username"]', 'session["department"]', 'session["position"]', 'session["leveling"]']
            }

            return render_template("addons/helloworld/templates/helloworld.html", 
                                   addon_nav=addon[0], # get json navigation
                                   path=get_child_path(), # handle highlight menu
                                   name=get_title_module(addon),
                                   ses_info=ses_info
                                   ) # get title module
    
    return redirect(url_for('main.index'))

@bp.route("/sub-menu-1")
def sub_menu_1():
    addon = get_addon(addondir="helloworld")
    if addon: # handle session ready or empty
        if addon[1]: # handle session True or False
            """
            **Here your code logic**
            Warning: coding rules that must be adhered to. it is prohibited to change the patented core system.
            """
            return render_template("addons/helloworld/templates/sub-menu-1.html", 
                                   addon_nav=addon[0], # get json navigation
                                   path=get_child_path(), # handle highlight menu
                                   name=get_title_module(addon)) # get title module
    
    return redirect(url_for('main.index'))

@bp.route("/sub-menu-2")
def sub_menu_2():
    addon = get_addon(addondir="helloworld")
    if addon: # handle session ready or empty
        if addon[1]: # handle session True or False
            """
            **Here your code logic**
            Warning: coding rules that must be adhered to. it is prohibited to change the patented core system.
            """
            return render_template("addons/helloworld/templates/sub-menu-2.html", 
                                   addon_nav=addon[0], # get json navigation
                                   path=get_child_path(), # handle highlight menu
                                   name=get_title_module(addon)) # get title module
    
    return redirect(url_for('main.index'))