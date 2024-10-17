from flask import flash, redirect, url_for
from ldap3 import Server, Connection, ALL, SUBTREE, ServerPool, SAFE_SYNC, ALL_ATTRIBUTES, MODIFY_REPLACE
import os
from app.extensions.database import db
from app.addons.powerad.model.powerad import Servers, DataServer
# from app.models.server import Servers, DataServer

# test
# def get_servers():
#     return db.query(DataServer).first()

# def get_groups(dc,ou):
#     # organizationalUnit
#     if ou:
#         ou = f"{ou},"
    
#     # AD connection pool
#     server_query = Servers.query.all()
#     serv_dict = []
#     for server in server_query:
#         serv = Server(server.domain, port=server.port)
#         # check connection
#         con_ = Connection(serv, client_strategy=SAFE_SYNC)
#         try:
#             if con_.bind():
#                 pass
#         except Exception as e:
#             flash(f"Check Connections: {e}", "danger")
#             return []

#         serv_dict.append(serv)

#     # get data password & username AD
#     server_data = DataServer.query.first()
#     # print([server_data.server])
#     server_pool = ServerPool([server_data.server], pool_strategy='ROUND_ROBIN', active=True, exhaust=True)
#     connection = Connection(server_pool, user=server_data.username, password=server_data.password, client_strategy=SAFE_SYNC)

#     if connection.bind():
#         status, results, response, _= connection.search(
#             search_base=f'{ou}{dc}',
#             search_filter='(objectClass=group)',
#             search_scope='SUBTREE',
#             attributes = ['cn', 'member']
#         )

#         # print(response)

#         try:
#             if status:
#                 groups = []
#                 for data in response:
#                     # print(data)
#                     try:
#                         groups.append(data["attributes"]["cn"])
#                     except:
#                         pass
            
#         except:
#             pass
        
#         try:
#             return groups
#         except Exception as e:
#             flash(f"Loaded Dropdown Groups: {e}", "danger")
#             return []

def get_users(g, dc, ou):
    # organizationalUnit
    if ou:
        ou = f"{ou},"
        
    # AD connection pool
    # server_query = Servers.query.all()
    server_query = db.query(Servers).all()
    serv_dict = []
    for server in server_query:
        serv = Server(server.domain, port=server.port)
        # check connection
        con_ = Connection(serv, client_strategy=SAFE_SYNC)
        try:
            if con_.bind():
                pass
        except Exception as e:
            # flash(f"Check Connections: {e}", "danger")
            return []

        serv_dict.append(serv)

    # return serv_dict

    # get data password & username AD
    # server_data = DataServer.query.first()
    server_data = db.query(DataServer).first()
    server_pool = ServerPool([server_data.server], pool_strategy='ROUND_ROBIN', active=True, exhaust=True)
    connection = Connection(server_pool, user="{}".format(server_data.username), password=server_data.password, client_strategy=SAFE_SYNC)

    if connection.bind():
        if "all" == g:
            status, results, response, _= connection.search(
                search_base=f'{dc}', # OU={os.environ.get("BASE_PLTU")}
                search_filter='(objectClass=user)',
                search_scope='SUBTREE',
                attributes = ['objectGUID', 'givenName', 'sn', 'displayName', 'sAMAccountName','department', 'title', 'userPrincipalName', 'st', 'distinguishedName']
            )

            if status:
                users_all_dict_ = []
                for user in response:
                    try:
                        if user["attributes"]["userPrincipalName"]:
                            # manipulation
                            result_last = user["attributes"]["displayName"]
                            if result_last:
                                last_ = result_last.split() 
                                if len(last_) == 2:
                                    last__ = (last_[1])
                                else:
                                    last__ = (last_[0])
                            else:
                                last__ = None

                            # print(last__)

                            root_users_ = {
                                "uid": user["attributes"]["objectGUID"],
                                "firstname": user["attributes"]["givenName"] if len([]) < len(user["attributes"]["givenName"]) else None,
                                # "lastname": user["attributes"]["sn"] if len([]) < len(user["attributes"]["sn"]) else None,
                                "lastname": user["attributes"]["displayName"] if len([]) < len(user["attributes"]["displayName"]) else None,
                                # "lastname": last__,
                                "username": user["attributes"]["sAMAccountName"],
                                "department": user["attributes"]["department"] if len([]) < len(user["attributes"]["department"]) else None,
                                "position": user["attributes"]["title"] if len([]) < len(user["attributes"]["title"]) else None,
                                "email_domain": user["attributes"]["userPrincipalName"],
                                "st": user["attributes"]["st"] if len([]) < len(user["attributes"]["st"]) else None,
                                "ds": user["attributes"]["distinguishedName"] if len([]) < len(user["attributes"]["distinguishedName"]) else None
                            }

                            users_all_dict_.append(root_users_)

                    except Exception as e:
                        pass

                return users_all_dict_
            
            else:
                flash("Users All Not Found", "danger")
                return []
            
        else:
            status_, results_, response_, _= connection.search(
                    search_base=f'CN={g},{ou}{dc}', # OU={os.environ.get("BASE_PLTU")}
                    search_filter='(objectClass=group)',
                    search_scope='SUBTREE',
                    attributes = ['member']
                )
            
            user_dict = []
            for member in response_:
                for user in member["attributes"]["member"]:
                    # print(user)
                    status__, results__, response__, _= connection.search(
                            search_base=user,
                            search_filter='(objectClass=user)',
                            search_scope='SUBTREE',
                            attributes = ['objectGUID', 'givenName', 'displayName', 'sAMAccountName','department', 'title', 'userPrincipalName', 'st', 'distinguishedName']
                        )
                
                    # print(response__)
                    # try:
                    if status__:
                        for user__ in response__:
                            if user__["attributes"]["userPrincipalName"]:
                                try:
                                    # manipulation
                                    result_last = user__["attributes"]["displayName"]
                                    if result_last:
                                        last_ = result_last.split() 
                                        if len(last_) == 2:
                                            last__ = (last_[1])
                                        else:
                                            last__ = (last_[0])
                                    else:
                                        last__ = None

                                    root_users__ = {
                                        "uid": user__["attributes"]["objectGUID"],
                                        "firstname": user__["attributes"]["givenName"] if len([]) < len(user__["attributes"]["givenName"]) else None,
                                        "lastname": user__["attributes"]["displayName"] if len([]) < len(user__["attributes"]["displayName"]) else None,
                                        # "lastname": last__,
                                        "username": user__["attributes"]["sAMAccountName"],
                                        "department": user__["attributes"]["department"] if len([]) < len(user__["attributes"]["department"]) else None,
                                        "position": user__["attributes"]["title"] if len([]) < len(user__["attributes"]["title"]) else None,
                                        "email_domain": user__["attributes"]["userPrincipalName"],
                                        "st": user__["attributes"]["st"] if len([]) < len(user__["attributes"]["st"]) else None,
                                        "ds": user__["attributes"]["distinguishedName"] if len([]) < len(user__["attributes"]["distinguishedName"]) else None
                                    }

                                    user_dict.append(root_users__)
                                except Exception as e:
                                    pass

                    # except Exception as e:
                    #     print(e)
                    #     return []

            try:
                return user_dict
            except Exception as e:
                flash(f"Not Found, Get Data by get Group Name{e}", "danger")
                return []

def get_user(name, dc):
    # parsing or REGEX 
    listname = name.split()

    try:
        give_name = listname[0]
        display_name = listname[1]
    except:
        display_name = listname[0]

    # return listname
    
    # print(give_name)
    # print(display_name)

    # AD connection pool
    # server_query = Servers.query.all()
    server_query = db.query(Servers).all()
    serv_dict = []
    for server in server_query:
        serv = Server(server.domain, port=server.port)
        # check connection
        con_ = Connection(serv, client_strategy=SAFE_SYNC)
        try:
            if con_.bind():
                pass
        except Exception as e:
            flash(f"Check Connections: {e}", "danger")
            return []

        serv_dict.append(serv)

    # get data password & username AD
    # server_data = DataServer.query.first()
    server_data = db.query(DataServer).first()
    server_pool = ServerPool([server_data.server], pool_strategy='ROUND_ROBIN', active=True, exhaust=True)
    connection = Connection(server_pool, user="{}".format(server_data.username), password=server_data.password, client_strategy=SAFE_SYNC)

    if connection.bind():
        status, result, response, _= connection.search(
                    search_base=f'{dc}',
                    search_filter=f'(|(givenName={give_name}*) (displayName={display_name}*) (sAMAccountName={give_name}*) (userPrincipalName={give_name}*) (mail={give_name}*) (department={give_name}*))',
                    attributes= ['objectGUID', 'givenName', 'displayName', 'sAMAccountName','department', 'title', 'userPrincipalName', 'st', 'distinguishedName']
                )

        if status:
            user_dict = []
            for user in response:
                try:
                    # manipulation
                    result_last = user["attributes"]["displayName"]
                    if result_last:
                        last_ = result_last.split() 
                        if len(last_) == 2:
                            last__ = (last_[1])
                        else:
                            last__ = (last_[0])
                    else:
                        last__ = None

                    root_users__ = {
                        "uid": user["attributes"]["objectGUID"],
                        "firstname": user["attributes"]["givenName"] if len([]) < len(user["attributes"]["givenName"]) else None,
                        "lastname": user["attributes"]["displayName"] if len([]) < len(user["attributes"]["displayName"]) else None,
                        # "lastname": last__,
                        "username": user["attributes"]["sAMAccountName"],
                        "department": user["attributes"]["department"] if len([]) < len(user["attributes"]["department"]) else None,
                        "position": user["attributes"]["title"] if len([]) < len(user["attributes"]["title"]) else None,
                        "email_domain": user["attributes"]["userPrincipalName"] if len([]) < len(user["attributes"]["userPrincipalName"]) else None,
                        "st": user["attributes"]["st"] if len([]) < len(user["attributes"]["st"]) else None,
                        "ds": user["attributes"]["distinguishedName"] if len([]) < len(user["attributes"]["distinguishedName"]) else None
                    }

                    user_dict.append(root_users__)
                except Exception as e:
                    pass

        return user_dict
    
# def get_user_by_guid(dc, guid):
#     # AD connection pool
#     server_query = Servers.query.all()
#     serv_dict = []
#     for server in server_query:
#         serv = Server(server.domain, port=server.port)
#         # check connection
#         con_ = Connection(serv, client_strategy=SAFE_SYNC)
#         try:
#             if con_.bind():
#                 pass
#         except Exception as e:
#             flash(f"Check Connections: {e}", "danger")
#             return []

#         serv_dict.append(serv)

#     # get data password & username AD
#     server_data = DataServer.query.first()
#     server_pool = ServerPool([server_data.server], pool_strategy='ROUND_ROBIN', active=True, exhaust=True)
#     connection = Connection(server_pool, user="{}".format(server_data.username), password=server_data.password, client_strategy=SAFE_SYNC)

#     if connection.bind():
#         status, result, response, _= connection.search(
#                     search_base=f'{dc}',
#                     search_filter=f'(objectGUID={guid})',
#                     attributes= ['objectGUID', 'givenName', 'displayName', 'sAMAccountName','department', 'title', 'userPrincipalName', 'st', 'distinguishedName']
#                 )

#         if status:
#             user_dict = []
#             for user in response:
#                 # print(user)
#                 try:
#                     # manipulation
#                     result_last = user["attributes"]["displayName"]
#                     if result_last:
#                         last_ = result_last.split() 
#                         if len(last_) == 2:
#                             last__ = (last_[1])
#                         else:
#                             last__ = (last_[0])
#                     else:
#                         last__ = None

#                     root_users__ = {
#                         "uid": user["attributes"]["objectGUID"],
#                         "firstname": user["attributes"]["givenName"] if len([]) < len(user["attributes"]["givenName"]) else None,
#                         "lastname": user["attributes"]["displayName"] if len([]) < len(user["attributes"]["displayName"]) else None,
#                         # "lastname": last__,
#                         "username": user["attributes"]["sAMAccountName"],
#                         "department": user["attributes"]["department"] if len([]) < len(user["attributes"]["department"]) else None,
#                         "position": user["attributes"]["title"] if len([]) < len(user["attributes"]["title"]) else None,
#                         "email_domain": user["attributes"]["userPrincipalName"] if len([]) < len(user["attributes"]["userPrincipalName"]) else None,
#                         "st": user["attributes"]["st"] if len([]) < len(user["attributes"]["st"]) else None,
#                         "ds": user["attributes"]["distinguishedName"] if len([]) < len(user["attributes"]["distinguishedName"]) else None
#                     }

#                     user_dict.append(root_users__)
#                 except Exception as e:
#                     pass

#         return user_dict
    
# def set_status_ad_user(username, password, oubase, server, type):
#     # AD connection pool
#     server_query = Servers.query.all()
#     serv_dict = []
#     for server in server_query:
#         serv = Server(server.domain, port=server.port)
#         # check connection
#         con_ = Connection(serv, client_strategy=SAFE_SYNC)
#         try:
#             if con_.bind():
#                 pass
#         except Exception as e:
#             flash(f"Check Connections: {e}", "danger")
#             return []

#         serv_dict.append(serv)

#     # get data password & username AD
#     server_data = DataServer.query.first()
#     server_pool = ServerPool([server_data.server], pool_strategy='ROUND_ROBIN', active=True, exhaust=True)
#     connection = Connection(server_pool, user="{}".format(server_data.username), password=server_data.password, client_strategy=SAFE_SYNC)
    
#     # server = Server(server, get_info=ALL)

#     # define the connection
#     # c = Connection(server, user=username, password=password)

#     if connection.bind():

#         # modify
#         if type:
#             connection.modify(f'{oubase}', {'st': [(MODIFY_REPLACE, [1])]})
#         else:
#             connection.modify(f'{oubase}', {'st': [(MODIFY_REPLACE, [])]})

#         print(connection.result)

#         # close the connection
#         connection.unbind()