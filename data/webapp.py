from subprocess import call

import json

def deploy_app(port, new_app_name, server, username, password ):
    app_config = {
        "server": server,
        "username": username,
        "password": password,
        "remotePort": port
    }

    with open('webapp/config.json', 'w') as f:
        json.dump(app_config, f)

    fin = open("webapp/manifest.yml.template", 'rb')
    fout = open("webapp/manifest.yml", 'wb')
    manifest = fin.read().replace("webapp", new_app_name)
    fout.write(manifest)
    fin.close()
    fout.close()
    call(["cf", "push", new_app_name], cwd="webapp")
    print "webapp will be available soon at http://%s.mybluemix.net" % new_app_name

def clone_rawkintrevos_webapp_template():
    call(["rm", "-rf", "webapp"])
    call(["git", "clone", "https://github.com/rawkintrevo/bluemix-biginsights-simple-port-forward-python-app.git", "webapp"])
    call(["cp", "webapp/manifest.yml", "webapp/manifest.yml.template"])
