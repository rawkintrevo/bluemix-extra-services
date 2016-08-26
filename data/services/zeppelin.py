import json

from scp import SCPClient
from time import sleep

def startZeppelin(ssh, zeppelinDir = 'zeppelin-0.6.0-bin-all'):
    stdin, stdout, stderr = ssh.exec_command(zeppelinDir + "/bin/zeppelin-daemon.sh status")
    zeppelin_status = stdout.readlines()
    if "OK" in zeppelin_status:
        print "Zeppelin already running."
    if "FAILED" in zeppelin_status:
        stdin, stdout, stderr = ssh.exec_command(zeppelinDir + "/bin/zeppelin-daemon.sh start")
        zeppelin_status = stdout.readlines()
        if not "OK" in zeppelin_status:
            print "FYI: zeppelin didn't start up correctly."
            print zeppelin_status

def downloadTerpProps(ssh):
    scp = SCPClient(ssh.get_transport())
    scp.get('/home/guest/zeppelin-0.7.0-SNAPSHOT/conf/interpreter.json', "./data/resources/zeppelin/interpreter.json")

def uploadTerpProps(ssh):
    scp = SCPClient(ssh.get_transport())
    scp.put("./data/resources/zeppelin/interpreter.json", '/home/guest/zeppelin-0.7.0-SNAPSHOT/conf/interpreter.json')

def updateConfigs(ssh):
    print "todo need to update interpreter.json with new server address for hive"
    scp = SCPClient(ssh.get_transport())
    #todo change this to an update interpreter.json method
    #scp.put('./data/resources/zeppelin/interpreter.json', './zeppelin-0.7.0-SNAPSHOT/conf/interpreter.json')
    scp.put('./data/resources/zeppelin/zeppelin_env.sh', './zeppelin-0.7.0-SNAPSHOT/conf/zeppelin-env.sh')
    scp.put('./data/resources/zeppelin/zeppelin-site.xml', './zeppelin-0.7.0-SNAPSHOT/conf/zeppelin-site.xml')
    stdin, stdout, stderr = ssh.exec_command("chmod +x zeppelin-0.7.0-SNAPSHOT/conf/zeppelin-env.sh")
    #stdin, stdout, stderr = ssh.exec_command("zeppelin-0.7.0-SNAPSHOT/bin/zeppelin-daemon.sh restart")


def installZeppelin(ssh):
    # todo won't work until you get port forwarding
    print "downloading zeppelin"
    stdin, stdout, stderr = ssh.exec_command("wget -q https://github.com/rawkintrevo/incubator-zeppelin/releases/download/v0.7.0-NIGHTLY-2016.08.22/zeppelin-0.7.0-SNAPSHOT.tar.gz")
    print stdout.read()
    print "un tarring zeppelin"
    stdin, stdout, stderr = ssh.exec_command("tar xzf zeppelin-0.7.0-SNAPSHOT.tar.gz")
    print stdout.read()
    # print "chilling for a second while we untar"
    # sleep(5)  # give it a sec to unzip before pushing files
    updateConfigs(ssh)

def updateSparkWithStandardSettings():
    with open("./data/resources/zeppelin/interpreter.json") as f:
        interpreter_json = json.load(f)

    for k, v in interpreter_json['interpreterSettings'].iteritems():
        if v['name'] == 'spark':
            spark_id = k
            break

    interpreter_json['interpreterSettings'][spark_id]['properties']['master'] = "yarn-client"

    with open("./data/resources/zeppelin/interpreter.json", 'w') as f:
        json.dump(interpreter_json, f)
