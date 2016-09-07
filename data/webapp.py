# /**
#  * Licensed to the Apache Software Foundation (ASF) under one
#  * or more contributor license agreements.  See the NOTICE file
#  * distributed with this work for additional information
#  * regarding copyright ownership.  The ASF licenses this file
#  * to you under the Apache License, Version 2.0 (the
#  * "License"); you may not use this file except in compliance
#  * with the License.  You may obtain a copy of the License at
#  *
#  *     http://www.apache.org/licenses/LICENSE-2.0
#  *
#  * Unless required by applicable law or agreed to in writing, software
#  * distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.
#  */

from subprocess import call

import json

def deploy_app(port, new_app_name, server, username, password, remoteBindAddr="127.0.0.1" ):
    app_config = {
        "server": server,
        "username": username,
        "password": password,
        "remotePort": port,
        "remoteBindAddr" : remoteBindAddr

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
