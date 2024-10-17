from ldap3 import Server, Connection, ALL, SUBTREE, ServerPool, SAFE_SYNC, ALL_ATTRIBUTES, MODIFY_REPLACE, ASYNC, get_config_parameter, set_config_parameter

def connect_old(username, password, domain):
    for server in ['pt-bjs.co.id', 'pt-bjp.co.id']:
        server_ = Server(server, connect_timeout=5)
        try:
            Connection(server_, auto_bind=True)
            print(f"Koneksi ditemukan as User: {username} Pass: {password}")

            server_pool = ServerPool(['pt-bjs.co.id', 'pt-bjp.co.id'], pool_strategy='ROUND_ROBIN', active=True, exhaust=True)
            connection = Connection(server_pool, user=f"{domain.strip()}\\{username}", password=password, client_strategy=ASYNC)
            print(">>>>>>>>>>>>>>>> process >>>>>>>>>>>>>>>>")
            if connection.bind():
                print(f">>>>> {connection.bind()}")
                return True
            else:
                print(f">>>>> {connection.bind()}")
                return False
        except:
            print("Koneksi tidak ditemukan")
            return False

def connect(username, password, domain):
    server = Server(f"{domain}.co.id", connect_timeout=5)
    conn = Connection(server, user=f"{domain.strip()}\\{username}", password=password, client_strategy=ASYNC)

    try:
        if conn.bind():
            return True
        else:
            return False
    except:
        print("AD not Connected !")
        return False